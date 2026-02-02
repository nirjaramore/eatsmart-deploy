"""
Data Collection Agent for EatSmartly.
Fetches food data from USDA API, PostgreSQL, and Redis cache.
"""
import json
import asyncio
from typing import Dict, Any, Optional, List
import requests
import redis
from sqlalchemy import create_engine, text, Table, Column, String, Float, DateTime, MetaData
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from config import settings
from agents.utils import (
    setup_logger,
    normalize_barcode,
    parse_nutrition,
    extract_allergens,
    validate_upc_checksum
)


logger = setup_logger(__name__, settings.LOG_LEVEL)


class DataCollectionAgent:
    """Agent responsible for collecting food data from multiple sources."""
    
    def __init__(self):
        """Initialize the data collection agent."""
        self.usda_api_key = settings.USDA_API_KEY
        self.usda_base_url = settings.USDA_BASE_URL
        self.rapidapi_key = settings.RAPIDAPI_KEY
        self.rapidapi_nutritional_host = settings.RAPIDAPI_NUTRITIONAL_HOST
        self.rapidapi_dietagram_host = settings.RAPIDAPI_DIETAGRAM_HOST
        self.api_ninjas_key = settings.API_NINJAS_KEY
        self.api_ninjas_base_url = settings.API_NINJAS_BASE_URL
        self.redis_client = self._init_redis()
        self.db_engine = self._init_database()
        self.Session = sessionmaker(bind=self.db_engine) if self.db_engine else None
        
        logger.info("DataCollectionAgent initialized")
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection."""
        try:
            client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5
            )
            client.ping()
            logger.info("Redis connection established")
            return client
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without cache.")
            return None
    
    def _init_database(self):
        """Initialize PostgreSQL connection and create tables."""
        try:
            engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Create tables if they don't exist
            metadata = MetaData()
            
            foods_table = Table(
                'foods', metadata,
                Column('barcode', String(13), primary_key=True),
                Column('name', String(500)),
                Column('brand', String(200)),
                Column('serving_size', Float),
                Column('serving_unit', String(20)),
                Column('calories', Float),
                Column('protein_g', Float),
                Column('carbs_g', Float),
                Column('fat_g', Float),
                Column('saturated_fat_g', Float),
                Column('sodium_mg', Float),
                Column('sugar_g', Float),
                Column('fiber_g', Float),
                Column('allergens', String(500)),
                Column('ingredients', String(5000)),
                Column('source', String(50)),
                Column('created_at', DateTime, default=datetime.utcnow),
                Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            )
            
            metadata.create_all(engine)
            logger.info("Database connection established and tables created")
            return engine
        except Exception as e:
            logger.warning(f"Database connection failed: {e}. Running without database.")
            return None
    
    def fetch_food_data(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Fetch food data using fallback chain: Redis → DB → USDA API.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Standardized food data dictionary or None
        """
        normalized_barcode = normalize_barcode(barcode)
        
        if not normalized_barcode:
            logger.warning(f"Invalid barcode format: {barcode}")
            return None
        
        if not validate_upc_checksum(normalized_barcode):
            logger.warning(f"Invalid barcode checksum: {normalized_barcode}")
        
        logger.info(f"Fetching food data for barcode: {normalized_barcode}")
        
        # Try cache first
        cached_data = self._get_from_cache(normalized_barcode)
        if cached_data:
            logger.info(f"Cache hit for barcode: {normalized_barcode}")
            return cached_data
        
        # Try database
        db_data = self._get_from_database(normalized_barcode)
        if db_data:
            logger.info(f"Database hit for barcode: {normalized_barcode}")
            self._save_to_cache(normalized_barcode, db_data)
            return db_data
        
        # Try RapidAPI DietaGram (barcode lookup)
        rapidapi_data = self._fetch_from_rapidapi_barcode(normalized_barcode)
        if rapidapi_data:
            logger.info(f"RapidAPI DietaGram hit for barcode: {normalized_barcode}")
            self._save_to_database(normalized_barcode, rapidapi_data)
            self._save_to_cache(normalized_barcode, rapidapi_data)
            return rapidapi_data
        
        # Try Open Food Facts (Free, no API key needed)
        off_data = self._fetch_from_open_food_facts(normalized_barcode)
        if off_data:
            logger.info(f"Open Food Facts hit for barcode: {normalized_barcode}")
            self._save_to_database(normalized_barcode, off_data)
            self._save_to_cache(normalized_barcode, off_data)
            return off_data
        
        # Try USDA API (if API key available)
        usda_data = self._fetch_from_usda(normalized_barcode)
        if usda_data:
            logger.info(f"USDA API hit for barcode: {normalized_barcode}")
            self._save_to_database(normalized_barcode, usda_data)
            self._save_to_cache(normalized_barcode, usda_data)
            return usda_data
        
        logger.warning(f"No data found for barcode: {normalized_barcode}")
        return None
    
    def _get_from_cache(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Retrieve food data from Redis cache."""
        if not self.redis_client:
            return None
            
        try:
            cache_key = f"food:{barcode}"
            cached_json = self.redis_client.get(cache_key)
            
            if cached_json:
                return json.loads(cached_json)
            return None
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None
    
    def _save_to_cache(self, barcode: str, data: Dict[str, Any]) -> None:
        """Save food data to Redis cache with TTL."""
        if not self.redis_client:
            return
            
        try:
            cache_key = f"food:{barcode}"
            self.redis_client.setex(
                cache_key,
                settings.REDIS_CACHE_TTL,
                json.dumps(data)
            )
            logger.debug(f"Cached data for barcode: {barcode}")
        except Exception as e:
            logger.error(f"Cache write error: {e}")
    
    def _get_from_database(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Retrieve food data from PostgreSQL food_products table."""
        if not self.db_engine:
            return None
            
        try:
            with self.db_engine.connect() as conn:
                # Query food_products table (Indian products)
                result = conn.execute(
                    text("""
                        SELECT id, barcode, name, brand, serving_size, serving_unit,
                               calories, protein_g, carbs_g, fat_g, saturated_fat_g,
                               sodium_mg, sugar_g, fiber_g, allergens, ingredients, source
                        FROM food_products 
                        WHERE barcode = :barcode
                    """),
                    {"barcode": barcode}
                ).fetchone()
                
                if result:
                    return {
                        "id": result[0],
                        "barcode": result[1],
                        "name": result[2],
                        "brand": result[3],
                        "serving_size": result[4],
                        "serving_unit": result[5],
                        "calories": result[6],
                        "protein_g": result[7],
                        "carbs_g": result[8],
                        "fat_g": result[9],
                        "saturated_fat_g": result[10],
                        "sodium_mg": result[11],
                        "sugar_g": result[12],
                        "fiber_g": result[13],
                        "allergens": result[14] or [],
                        "ingredients": result[15],
                        "source": result[16]
                    }
                return None
        except Exception as e:
            logger.error(f"Database read error: {e}")
            return None
    
    def _save_to_database(self, barcode: str, data: Dict[str, Any]) -> None:
        """Save food data to PostgreSQL."""
        if not self.db_engine:
            return
            
        try:
            with self.Session() as session:
                allergens_str = ",".join(data.get("allergens", []))
                
                session.execute(
                    text("""
                        INSERT INTO foods 
                        (barcode, name, brand, serving_size, serving_unit, calories, 
                         protein_g, carbs_g, fat_g, saturated_fat_g, sodium_mg, 
                         sugar_g, fiber_g, allergens, ingredients, source, updated_at)
                        VALUES 
                        (:barcode, :name, :brand, :serving_size, :serving_unit, :calories,
                         :protein_g, :carbs_g, :fat_g, :saturated_fat_g, :sodium_mg,
                         :sugar_g, :fiber_g, :allergens, :ingredients, :source, :updated_at)
                        ON CONFLICT (barcode) DO UPDATE SET
                            name = EXCLUDED.name,
                            brand = EXCLUDED.brand,
                            serving_size = EXCLUDED.serving_size,
                            serving_unit = EXCLUDED.serving_unit,
                            calories = EXCLUDED.calories,
                            protein_g = EXCLUDED.protein_g,
                            carbs_g = EXCLUDED.carbs_g,
                            fat_g = EXCLUDED.fat_g,
                            saturated_fat_g = EXCLUDED.saturated_fat_g,
                            sodium_mg = EXCLUDED.sodium_mg,
                            sugar_g = EXCLUDED.sugar_g,
                            fiber_g = EXCLUDED.fiber_g,
                            allergens = EXCLUDED.allergens,
                            ingredients = EXCLUDED.ingredients,
                            source = EXCLUDED.source,
                            updated_at = EXCLUDED.updated_at
                    """),
                    {
                        "barcode": barcode,
                        "name": data.get("name"),
                        "brand": data.get("brand"),
                        "serving_size": data.get("serving_size"),
                        "serving_unit": data.get("serving_unit"),
                        "calories": data.get("calories"),
                        "protein_g": data.get("protein_g"),
                        "carbs_g": data.get("carbs_g"),
                        "fat_g": data.get("fat_g"),
                        "saturated_fat_g": data.get("saturated_fat_g"),
                        "sodium_mg": data.get("sodium_mg"),
                        "sugar_g": data.get("sugar_g"),
                        "fiber_g": data.get("fiber_g"),
                        "allergens": allergens_str,
                        "ingredients": data.get("ingredients"),
                        "source": data.get("source", "usda"),
                        "updated_at": datetime.utcnow()
                    }
                )
                session.commit()
                logger.debug(f"Saved to database: {barcode}")
        except Exception as e:
            logger.error(f"Database write error: {e}")
    
    def _fetch_from_open_food_facts(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Fetch food data from Open Food Facts (FREE - No API key needed).
        Works great for international and Indian products.
        """
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if product was found
            if data.get("status") != 1:
                logger.info(f"Product not found in Open Food Facts: {barcode}")
                return None
            
            product = data.get("product", {})
            
            # Extract product info
            product_name = product.get("product_name") or product.get("product_name_en")
            brand = product.get("brands")
            
            # Skip if no basic info
            if not product_name:
                logger.warning(f"Open Food Facts has barcode {barcode} but missing product name")
                return None
            
            # Extract nutrition
            nutrients = product.get("nutriments", {})
            
            # Build standardized nutrition data
            nutrition_data = {
                "barcode": barcode,
                "name": product_name,
                "brand": brand or "Unknown",
                "serving_size": product.get("serving_size") or 100,
                "serving_unit": "g",
                "calories": nutrients.get("energy-kcal_100g") or nutrients.get("energy-kcal"),
                "protein_g": nutrients.get("proteins_100g") or nutrients.get("proteins"),
                "carbs_g": nutrients.get("carbohydrates_100g") or nutrients.get("carbohydrates"),
                "fat_g": nutrients.get("fat_100g") or nutrients.get("fat"),
                "saturated_fat_g": nutrients.get("saturated-fat_100g") or nutrients.get("saturated-fat"),
                "sodium_mg": (nutrients.get("sodium_100g") or nutrients.get("sodium") or 0) * 1000,  # Convert g to mg
                "sugar_g": nutrients.get("sugars_100g") or nutrients.get("sugars"),
                "fiber_g": nutrients.get("fiber_100g") or nutrients.get("fiber"),
                "ingredients": product.get("ingredients_text") or product.get("ingredients_text_en") or "",
                "allergens": product.get("allergens_tags", []),
                "source": "Open Food Facts"
            }
            
            # Convert None values to 0 for numeric fields
            for key in ["calories", "protein_g", "carbs_g", "fat_g", "saturated_fat_g", "sodium_mg", "sugar_g", "fiber_g"]:
                if nutrition_data[key] is None:
                    nutrition_data[key] = 0
            
            logger.info(f"Open Food Facts: Found {product_name} by {brand}")
            return nutrition_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Open Food Facts API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Open Food Facts parsing error: {e}")
            return None
    
    def _search_open_food_facts(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search Open Food Facts database for products by name.
        This has 400k+ products including many Indian brands.
        """
        try:
            search_url = "https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                "search_terms": query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": limit,
                "sort_by": "popularity"  # Sort by popularity for better results
            }
            
            response = requests.get(search_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            products = data.get("products", [])
            if not products:
                logger.info(f"Open Food Facts search: No results for '{query}'")
                return []
            
            results = []
            for product in products[:limit]:
                # Extract basic product info
                product_name = product.get("product_name") or product.get("product_name_en")
                brand = product.get("brands")
                barcode = product.get("code")
                
                if not product_name:
                    continue
                
                # Extract nutrition data
                nutrients = product.get("nutriments", {})
                
                # Build standardized result
                result = {
                    "id": None,  # Open Food Facts doesn't have IDs like our DB
                    "barcode": barcode,
                    "name": product_name,
                    "brand": brand or "Unknown",
                    "serving_size": product.get("serving_size") or 100,
                    "serving_unit": "g",
                    "calories": nutrients.get("energy-kcal_100g") or nutrients.get("energy-kcal"),
                    "protein_g": nutrients.get("proteins_100g") or nutrients.get("proteins"),
                    "carbs_g": nutrients.get("carbohydrates_100g") or nutrients.get("carbohydrates"),
                    "fat_g": nutrients.get("fat_100g") or nutrients.get("fat"),
                    "saturated_fat_g": nutrients.get("saturated-fat_100g") or nutrients.get("saturated-fat"),
                    "sodium_mg": (nutrients.get("sodium_100g") or nutrients.get("sodium") or 0) * 1000,  # Convert g to mg
                    "sugar_g": nutrients.get("sugars_100g") or nutrients.get("sugars"),
                    "fiber_g": nutrients.get("fiber_100g") or nutrients.get("fiber"),
                    "allergens": product.get("allergens_tags", []),
                    "ingredients": product.get("ingredients_text") or product.get("ingredients_text_en") or "",
                    "source": "Open Food Facts"
                }
                
                # Convert None values to 0 for numeric fields
                for key in ["calories", "protein_g", "carbs_g", "fat_g", "saturated_fat_g", "sodium_mg", "sugar_g", "fiber_g"]:
                    if result[key] is None:
                        result[key] = 0
                
                results.append(result)
            
            logger.info(f"Open Food Facts search: Found {len(results)} results for '{query}'")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Open Food Facts search API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Open Food Facts search parsing error: {e}")
            return []
    
    def _fetch_from_rapidapi_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Fetch nutrition data from RapidAPI DietaGram by barcode."""
        if not self.rapidapi_key:
            return None
            
        try:
            url = f"https://{self.rapidapi_dietagram_host}/apiFood.php"
            querystring = {"icode": barcode}
            
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": self.rapidapi_dietagram_host
            }
            
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if product found
            if not data or "dishes" not in data or not data["dishes"]:
                logger.info(f"RapidAPI DietaGram: No data for barcode {barcode}")
                return None
            
            dish = data["dishes"][0]
            
            # Parse nutrition data
            nutrition_data = {
                "barcode": barcode,
                "name": dish.get("name", "Unknown"),
                "brand": dish.get("brand") or dish.get("manufacturer"),
                "serving_size": dish.get("serving_qty") or 100,
                "serving_unit": dish.get("serving_unit") or "g",
                "calories": dish.get("caloric"),
                "protein_g": dish.get("protein"),
                "carbs_g": dish.get("carbs"),
                "fat_g": dish.get("fat"),
                "saturated_fat_g": dish.get("saturated_fat"),
                "trans_fat_g": dish.get("trans_fat"),
                "sodium_mg": dish.get("sodium"),
                "sugar_g": dish.get("sugar"),
                "fiber_g": dish.get("fiber"),
                "cholesterol_mg": dish.get("cholesterol"),
                "ingredients": "",
                "allergens": [],
                "source": "RapidAPI_DietaGram"
            }
            
            logger.info(f"RapidAPI DietaGram: Found {nutrition_data.get('name')}")
            return nutrition_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"RapidAPI DietaGram API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"RapidAPI DietaGram parsing error: {e}")
            return None
    
    def _fetch_from_rapidapi_nutrition(self, food_name: str) -> Optional[Dict[str, Any]]:
        """Fetch nutrition data from RapidAPI AI Nutritional Facts by product name."""
        if not self.rapidapi_key:
            return None
            
        try:
            url = f"https://{self.rapidapi_nutritional_host}/api/nutrition"
            
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": self.rapidapi_nutritional_host
            }
            
            payload = {"query": food_name}
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse nutrition data
            if not data or "servings" not in data:
                logger.info(f"RapidAPI AI Nutritional: No data for {food_name}")
                return None
            
            nutrition_info = data.get("nutrition", {})
            
            nutrition_data = {
                "name": food_name,
                "brand": None,
                "serving_size": data.get("servings", 1),
                "serving_unit": data.get("serving_unit") or "serving",
                "calories": nutrition_info.get("calories_in_kcal"),
                "protein_g": nutrition_info.get("total_fat_in_g"),
                "carbs_g": nutrition_info.get("carbs_in_g"),
                "fat_g": nutrition_info.get("total_fat_in_g"),
                "saturated_fat_g": nutrition_info.get("saturated_fat_in_g"),
                "trans_fat_in_g": nutrition_info.get("trans_fat_in_g"),
                "sodium_mg": nutrition_info.get("sodium_in_mg"),
                "sugar_g": nutrition_info.get("sugar_in_g"),
                "fiber_g": nutrition_info.get("fiber_in_g"),
                "cholesterol_mg": nutrition_info.get("cholesterol_in_mg"),
                "ingredients": "",
                "allergens": [],
                "source": "RapidAPI_AI_Nutritional"
            }
            
            logger.info(f"RapidAPI AI Nutritional: Found data for {food_name}")
            return nutrition_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"RapidAPI AI Nutritional API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"RapidAPI AI Nutritional parsing error: {e}")
            return None
    
    def _fetch_from_usda(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Fetch food data from USDA FoodData Central API."""
        try:
            # Try barcode search first
            search_url = f"{self.usda_base_url}/foods/search"
            params = {
                "query": barcode,
                "api_key": self.usda_api_key,
                "dataType": ["Branded"],
                "pageSize": 1
            }
            
            response = requests.get(
                search_url,
                params=params,
                timeout=settings.API_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            foods = data.get("foods", [])
            
            if not foods:
                logger.warning(f"No USDA data for barcode: {barcode}")
                return None
            
            food_data = foods[0]
            
            # Parse and standardize
            nutrition = parse_nutrition(food_data, source="usda")
            nutrition["barcode"] = barcode
            
            # Extract allergens from ingredients
            if nutrition.get("ingredients"):
                nutrition["allergens"] = extract_allergens(nutrition["ingredients"])
            
            return nutrition
            
        except requests.exceptions.RequestException as e:
            logger.error(f"USDA API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"USDA API parsing error: {e}")
            return None
    
    def search_food_by_name(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for foods by name in database first, then USDA if needed.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of food data dictionaries
        """
        try:
            # First, search local database (includes Indian products)
            logger.info(f"Searching database for: {query}")
            
            if self.db_engine:
                try:
                    with self.db_engine.connect() as conn:
                        # Use ILIKE for case-insensitive search in PostgreSQL
                        # Try food_products table first (Indian products), then nutrition_data
                        search_query = text("""
                            SELECT id, barcode, name, brand, serving_size, serving_unit,
                                   calories, protein_g, carbs_g, fat_g, saturated_fat_g,
                                   sodium_mg, sugar_g, fiber_g, allergens, ingredients, source
                            FROM food_products
                            WHERE name ILIKE :search_pattern
                               OR brand ILIKE :search_pattern
                            ORDER BY 
                                CASE 
                                    WHEN name ILIKE :exact_match THEN 1
                                    WHEN name ILIKE :starts_with THEN 2
                                    ELSE 3
                                END,
                                name
                            LIMIT :limit
                        """)
                        
                        result = conn.execute(search_query, {
                            "search_pattern": f"%{query}%",
                            "exact_match": query,
                            "starts_with": f"{query}%",
                            "limit": limit
                        })
                        
                        results = []
                        for row in result:
                            results.append({
                                "id": row[0],
                                "barcode": row[1],
                                "name": row[2],
                                "brand": row[3],
                                "serving_size": row[4],
                                "serving_unit": row[5],
                                "calories": row[6],
                                "protein_g": row[7],
                                "carbs_g": row[8],
                                "fat_g": row[9],
                                "saturated_fat_g": row[10],
                                "sodium_mg": row[11],
                                "sugar_g": row[12],
                                "fiber_g": row[13],
                                "allergens": row[14] or [],
                                "ingredients": row[15],
                                "source": row[16]
                            })
                        
                        if results:
                            logger.info(f"Found {len(results)} products in database")
                            return results
                        else:
                            logger.info(f"No results in database, trying Open Food Facts")
                            
                except Exception as db_error:
                    logger.error(f"Database search error: {db_error}")
            
            # Try Open Food Facts search first (has 400k+ products including Indian)
            off_results = self._search_open_food_facts(query, limit)
            if off_results:
                logger.info(f"Found {len(off_results)} products in Open Food Facts")
                return off_results
            
            # Fall back to USDA if no Open Food Facts results
            logger.info(f"No results in Open Food Facts, trying USDA")
            search_url = f"{self.usda_base_url}/foods/search"
            params = {
                "query": query,
                "api_key": self.usda_api_key,
                "pageSize": limit
            }
            
            response = requests.get(
                search_url,
                params=params,
                timeout=settings.API_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            foods = data.get("foods", [])
            
            results = []
            for food in foods:
                nutrition = parse_nutrition(food, source="usda")
                results.append(nutrition)
            
            return results
            
        except Exception as e:
            logger.error(f"Food search error: {e}")
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by database ID from food_products table.
        
        Args:
            product_id: Product ID from database
            
        Returns:
            Product data dictionary or None
        """
        if not self.db_engine:
            logger.warning("Database not available")
            return None
            
        try:
            with self.db_engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT id, barcode, name, brand, serving_size, serving_unit,
                               calories, protein_g, carbs_g, fat_g, saturated_fat_g,
                               sodium_mg, sugar_g, fiber_g, allergens, ingredients, source
                        FROM food_products
                        WHERE id = :product_id
                    """),
                    {"product_id": product_id}
                ).fetchone()
                
                if result:
                    return {
                        "id": result[0],
                        "barcode": result[1],
                        "name": result[2],
                        "brand": result[3],
                        "serving_size": result[4],
                        "serving_unit": result[5],
                        "calories": result[6],
                        "protein_g": result[7],
                        "carbs_g": result[8],
                        "fat_g": result[9],
                        "saturated_fat_g": result[10],
                        "sodium_mg": result[11],
                        "sugar_g": result[12],
                        "fiber_g": result[13],
                        "allergens": result[14] or [],
                        "ingredients": result[15],
                        "source": result[16]
                    }
                
                logger.info(f"Product {product_id} not found in database")
                return None
                
        except Exception as e:
            logger.error(f"Error getting product by ID: {e}")
            return None
    
    def fetch_from_api_ninjas_text(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetch nutrition data from API Ninjas using natural language text.
        
        This API is excellent for:
        - Extracting nutrition from recipes, menus, food blogs
        - Handling custom portions (e.g., "1 cup rice", "2 tbsp butter")
        - Processing multiple food items in one query (e.g., "1lb brisket and fries")
        
        Args:
            query: Natural language text describing food (e.g., "1 cup cooked rice")
            
        Returns:
            List of nutrition data dictionaries
        """
        if not self.api_ninjas_key:
            logger.warning("API Ninjas key not configured")
            return []
            
        try:
            url = f"{self.api_ninjas_base_url}/nutrition"
            headers = {
                "X-Api-Key": self.api_ninjas_key
            }
            params = {
                "query": query
            }
            
            logger.info(f"Fetching nutrition from API Ninjas for: {query}")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.info(f"API Ninjas: No data for '{query}'")
                return []
            
            # Convert API Ninjas format to our standard format
            results = []
            for item in data:
                nutrition_data = {
                    "name": item.get("name"),
                    "brand": None,
                    "serving_size": item.get("serving_size_g"),
                    "serving_unit": "g",
                    "calories": item.get("calories"),
                    "protein_g": item.get("protein_g"),
                    "carbs_g": item.get("carbohydrates_total_g"),
                    "fat_g": item.get("fat_total_g"),
                    "saturated_fat_g": item.get("fat_saturated_g"),
                    "sodium_mg": item.get("sodium_mg"),
                    "sugar_g": item.get("sugar_g"),
                    "fiber_g": item.get("fiber_g"),
                    "potassium_mg": item.get("potassium_mg"),
                    "cholesterol_mg": item.get("cholesterol_mg"),
                    "ingredients": "",
                    "allergens": [],
                    "source": "API_Ninjas"
                }
                results.append(nutrition_data)
            
            logger.info(f"API Ninjas: Found {len(results)} items for '{query}'")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API Ninjas request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"API Ninjas error: {e}")
            return []
    
    def fetch_from_api_ninjas_item(self, food_item: str, quantity: str) -> Optional[Dict[str, Any]]:
        """
        Fetch nutrition for a single food item with specific quantity from API Ninjas.
        
        Supports various units: "1 cup", "2 lbs", "100g", "2 tbsp", etc.
        
        Args:
            food_item: Single food item name (e.g., "rice", "butter")
            quantity: Quantity with unit (e.g., "1 cup", "2 tbsp")
            
        Returns:
            Nutrition data dictionary or None
        """
        if not self.api_ninjas_key:
            logger.warning("API Ninjas key not configured")
            return None
            
        try:
            url = f"{self.api_ninjas_base_url}/nutritionitem"
            headers = {
                "X-Api-Key": self.api_ninjas_key
            }
            params = {
                "query": food_item,
                "quantity": quantity
            }
            
            logger.info(f"Fetching nutrition from API Ninjas for: {quantity} {food_item}")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.info(f"API Ninjas: No data for '{quantity} {food_item}'")
                return None
            
            # Convert API Ninjas format to our standard format
            nutrition_data = {
                "name": data.get("name", food_item),
                "brand": None,
                "serving_size": data.get("serving_size_g"),
                "serving_unit": "g",
                "calories": data.get("calories"),
                "protein_g": data.get("protein_g"),
                "carbs_g": data.get("carbohydrates_total_g"),
                "fat_g": data.get("fat_total_g"),
                "saturated_fat_g": data.get("fat_saturated_g"),
                "sodium_mg": data.get("sodium_mg"),
                "sugar_g": data.get("sugar_g"),
                "fiber_g": data.get("fiber_g"),
                "potassium_mg": data.get("potassium_mg"),
                "cholesterol_mg": data.get("cholesterol_mg"),
                "ingredients": "",
                "allergens": [],
                "source": "API_Ninjas"
            }
            
            logger.info(f"API Ninjas: Found data for '{quantity} {food_item}'")
            return nutrition_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API Ninjas request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"API Ninjas error: {e}")
            return None
