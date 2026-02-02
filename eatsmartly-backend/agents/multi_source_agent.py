"""
Multi-Source Data Agent using AutoGen.
Queries multiple APIs (Open Food Facts, USDA, Nutritionix) and cross-verifies data.
"""
import os
import json
import asyncio
from typing import Dict, Any, Optional, List
import requests
from datetime import datetime

from config import settings
from agents.utils import setup_logger

logger = setup_logger(__name__, settings.LOG_LEVEL)


class MultiSourceDataAgent:
    """
    Agent that queries multiple food databases and cross-verifies data.
    Uses consensus approach to determine most accurate nutrition info.
    """
    
    def __init__(self):
        """Initialize multi-source data agent."""
        self.usda_api_key = settings.USDA_API_KEY
        self.nutritionix_app_id = os.getenv("NUTRITIONIX_APP_ID")
        self.nutritionix_app_key = os.getenv("NUTRITIONIX_APP_KEY")
        self.edamam_app_id = os.getenv("EDAMAM_APP_ID")
        self.edamam_app_key = os.getenv("EDAMAM_APP_KEY")
        
        logger.info("MultiSourceDataAgent initialized")
        logger.info(f"USDA API: {'Configured ✅' if self.usda_api_key else 'Missing ❌'}")
        logger.info(f"Nutritionix API: {'Configured ✅' if self.nutritionix_app_id else 'Missing ❌'}")
        logger.info(f"Edamam API: {'Configured ✅' if self.edamam_app_id else 'Missing ❌'}")
    
    async def fetch_from_all_sources(self, barcode: str) -> Dict[str, Any]:
        """
        Fetch data from all available sources concurrently.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Dictionary with data from all sources and consensus
        """
        logger.info("="*80)
        logger.info(f"🔍 STARTING BARCODE SEARCH: {barcode}")
        logger.info(f"📊 Will query 4 data sources concurrently...")
        logger.info("="*80)
        
        # Fetch from all sources concurrently (4 sources now)
        results = await asyncio.gather(
            self._fetch_open_food_facts(barcode),
            self._fetch_usda(barcode),
            self._fetch_nutritionix(barcode),
            self._fetch_edamam(barcode),
            return_exceptions=True
        )
        
        sources_data = {
            "open_food_facts": results[0] if not isinstance(results[0], Exception) else None,
            "usda": results[1] if not isinstance(results[1], Exception) else None,
            "nutritionix": results[2] if not isinstance(results[2], Exception) else None,
            "edamam": results[3] if not isinstance(results[3], Exception) else None,
        }
        
        # Log detailed results from each source
        logger.info("\n" + "="*80)
        logger.info("📋 DATA SOURCE RESULTS:")
        logger.info("="*80)
        
        for source_name, data in sources_data.items():
            if data:
                logger.info(f"✅ {source_name.upper()}: FOUND - {data.get('name', 'Unknown')}")
                logger.info(f"   Brand: {data.get('brand', 'N/A')}")
                logger.info(f"   Calories: {data.get('calories', 'N/A')} kcal")
                logger.info(f"   Confidence: {data.get('confidence', 'N/A')}")
            elif isinstance(results[list(sources_data.keys()).index(source_name)], Exception):
                error = results[list(sources_data.keys()).index(source_name)]
                logger.warning(f"❌ {source_name.upper()}: FAILED - {str(error)[:100]}")
            else:
                logger.warning(f"❌ {source_name.upper()}: NOT FOUND")
        logger.info("="*80 + "\n")
        
        # Calculate consensus
        consensus_data = self._calculate_consensus(sources_data)
        
        return {
            "sources": sources_data,
            "consensus": consensus_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _fetch_open_food_facts(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Fetch from Open Food Facts (FREE, no auth needed). Try India endpoint first for better local coverage."""
        try:
            logger.info(f"🇮🇳 Querying Open Food Facts (India first, then Global)...")
            # Try India endpoint first for better coverage of Indian products
            india_url = f"https://in.openfoodfacts.org/api/v0/product/{barcode}.json"
            global_url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            logger.debug(f"   India URL: {india_url}")
            logger.debug(f"   Global URL: {global_url}")
            
            loop = asyncio.get_event_loop()
            
            # Try India endpoint first
            try:
                response = await loop.run_in_executor(
                    None, 
                    lambda: requests.get(india_url, timeout=10)
                )
                
                data = response.json()
                
                if data.get("status") == 1:
                    product = data.get("product", {})
                    product_name = product.get("product_name") or product.get("product_name_en")
                    logger.info(f"✅ SUCCESS: Open Food Facts INDIA - {product_name}")
                    logger.info(f"   Categories: {product.get('categories', 'N/A')}")
                    logger.info(f"   Brands: {product.get('brands', 'N/A')}")
                    return self._parse_open_food_facts_product(barcode, product)
                else:
                    logger.info(f"⚠️  Product not in India database, trying global...")
            except Exception as e:
                logger.warning(f"⚠️  India endpoint error: {str(e)[:100]}")
            
            # Fallback to global endpoint
            logger.info(f"🌍 Trying Open Food Facts GLOBAL database...")
            response = await loop.run_in_executor(
                None, 
                lambda: requests.get(global_url, timeout=10)
            )
            
            data = response.json()
            
            if data.get("status") != 1:
                logger.warning(f"❌ Open Food Facts: Product {barcode} NOT FOUND in any database")
                return None
            
            product = data.get("product", {})
            product_name = product.get("product_name") or product.get("product_name_en")
            logger.info(f"✅ SUCCESS: Open Food Facts GLOBAL - {product_name}")
            logger.info(f"   Countries: {product.get('countries', 'N/A')}")
            return self._parse_open_food_facts_product(barcode, product)
            
        except Exception as e:
            logger.error(f"Error fetching from Open Food Facts: {e}")
            return None
    
    def _parse_open_food_facts_product(self, barcode: str, product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Open Food Facts product data."""
        product_name = product.get("product_name") or product.get("product_name_en")
        
        if not product_name:
            logger.warning(f"Open Food Facts: Product {barcode} missing name")
            return None
        
        nutrients = product.get("nutriments", {})
        
        result = {
            "source": "Open Food Facts",
            "barcode": barcode,
            "name": product_name,
            "brand": product.get("brands"),
            "calories": nutrients.get("energy-kcal_100g"),
            "protein_g": nutrients.get("proteins_100g"),
            "carbs_g": nutrients.get("carbohydrates_100g"),
            "fat_g": nutrients.get("fat_100g"),
            "saturated_fat_g": nutrients.get("saturated-fat_100g"),
            "sodium_mg": (nutrients.get("sodium_100g") or 0) * 1000,
            "sugar_g": nutrients.get("sugars_100g"),
            "fiber_g": nutrients.get("fiber_100g"),
            "ingredients": product.get("ingredients_text"),
            "allergens": product.get("allergens_tags", []),
            "confidence": 0.85,  # Community-maintained
            "last_updated": product.get("last_modified_t")
        }
        
        logger.info(f"Open Food Facts: Found {product_name}")
        return result
    
    async def _fetch_usda(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Fetch from USDA FoodData Central (Official US database)."""
        try:
            logger.info(f"🇺🇸 Querying USDA FoodData Central...")
            if not self.usda_api_key:
                logger.warning("❌ USDA API key not configured - skipping")
                return None
            
            url = "https://api.nal.usda.gov/fdc/v1/foods/search"
            params = {
                "query": barcode,
                "api_key": self.usda_api_key,
                "dataType": ["Branded"],
                "pageSize": 1
            }
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=10)
            )
            
            data = response.json()
            foods = data.get("foods", [])
            
            if not foods:
                logger.info(f"USDA: Product {barcode} not found")
                return None
            
            food = foods[0]
            
            # Extract nutrition from foodNutrients
            nutrients = {}
            for nutrient in food.get("foodNutrients", []):
                name = nutrient.get("nutrientName", "").lower()
                value = nutrient.get("value")
                
                if "energy" in name or "calorie" in name:
                    nutrients["calories"] = value
                elif "protein" in name:
                    nutrients["protein_g"] = value
                elif "carbohydrate" in name:
                    nutrients["carbs_g"] = value
                elif "total lipid" in name or "fat" in name:
                    nutrients["fat_g"] = value
                elif "fatty acids, total saturated" in name:
                    nutrients["saturated_fat_g"] = value
                elif "sodium" in name:
                    nutrients["sodium_mg"] = value
                elif "sugars" in name:
                    nutrients["sugar_g"] = value
                elif "fiber" in name:
                    nutrients["fiber_g"] = value
            
            result = {
                "source": "USDA",
                "barcode": barcode,
                "name": food.get("description"),
                "brand": food.get("brandOwner"),
                **nutrients,
                "ingredients": food.get("ingredients"),
                "confidence": 0.95,  # Official government database
                "last_updated": food.get("publishedDate")
            }
            
            logger.info(f"USDA: Found {food.get('description')}")
            return result
            
        except Exception as e:
            logger.error(f"USDA error: {e}")
            return None
    
    async def _fetch_nutritionix(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Fetch from Nutritionix (Comprehensive food database)."""
        try:
            if not self.nutritionix_app_id or not self.nutritionix_app_key:
                logger.warning("Nutritionix API credentials not configured")
                return None
            
            url = f"https://trackapi.nutritionix.com/v2/search/item?upc={barcode}"
            headers = {
                "x-app-id": self.nutritionix_app_id,
                "x-app-key": self.nutritionix_app_key,
                "Content-Type": "application/json"
            }
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, headers=headers, timeout=10)
            )
            
            data = response.json()
            foods = data.get("foods", [])
            
            if not foods:
                logger.info(f"Nutritionix: Product {barcode} not found")
                return None
            
            food = foods[0]
            
            result = {
                "source": "Nutritionix",
                "barcode": barcode,
                "name": food.get("food_name"),
                "brand": food.get("brand_name"),
                "calories": food.get("nf_calories"),
                "protein_g": food.get("nf_protein"),
                "carbs_g": food.get("nf_total_carbohydrate"),
                "fat_g": food.get("nf_total_fat"),
                "saturated_fat_g": food.get("nf_saturated_fat"),
                "sodium_mg": food.get("nf_sodium"),
                "sugar_g": food.get("nf_sugars"),
                "fiber_g": food.get("nf_dietary_fiber"),
                "ingredients": food.get("nf_ingredient_statement"),
                "allergens": food.get("allergens", []),
                "confidence": 0.90,  # Commercial database
                "last_updated": food.get("updated_at")
            }
            
            logger.info(f"Nutritionix: Found {food.get('food_name')}")
            return result
            
        except Exception as e:
            logger.error(f"Nutritionix error: {e}")
            return None
    
    async def _fetch_edamam(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Fetch from Edamam Food Database (Good for Indian & International products)."""
        try:
            logger.info(f"🌏 Querying Edamam Food Database (Indian + International)...")
            if not self.edamam_app_id or not self.edamam_app_key:
                logger.warning("❌ Edamam API credentials not configured - skipping")
                return None
            
            # Edamam doesn't support direct barcode search
            # Try UPC search through their parser API
            url = "https://api.edamam.com/api/food-database/v2/parser"
            
            params = {
                "app_id": self.edamam_app_id,
                "app_key": self.edamam_app_key,
                "upc": barcode,
                "nutrition-type": "cooking"
            }
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=10)
            )
            
            if response.status_code != 200:
                logger.info(f"Edamam: Product {barcode} not found (status {response.status_code})")
                return None
            
            data = response.json()
            hints = data.get("hints", [])
            
            if not hints:
                logger.info(f"Edamam: No results for barcode {barcode}")
                return None
            
            # Use first result
            food = hints[0].get("food", {})
            nutrients = food.get("nutrients", {})
            
            result = {
                "source": "Edamam",
                "barcode": barcode,
                "name": food.get("label"),
                "brand": food.get("brand"),
                "calories": nutrients.get("ENERC_KCAL"),
                "protein_g": nutrients.get("PROCNT"),
                "carbs_g": nutrients.get("CHOCDF"),
                "fat_g": nutrients.get("FAT"),
                "saturated_fat_g": nutrients.get("FASAT"),
                "sodium_mg": nutrients.get("NA"),
                "sugar_g": nutrients.get("SUGAR"),
                "fiber_g": nutrients.get("FIBTG"),
                "ingredients": None,  # Not available in Edamam
                "allergens": [],
                "confidence": 0.88,  # Commercial, good for Indian products
                "last_updated": None
            }
            
            logger.info(f"✅ Edamam: Found {food.get('label')}")
            return result
            
        except Exception as e:
            logger.error(f"Edamam error: {e}")
            return None
    
    def _calculate_consensus(self, sources_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate consensus nutrition data from multiple sources.
        Uses weighted average based on source confidence.
        """
        logger.info("Calculating consensus from all sources")
        
        # Filter out None values
        valid_sources = {k: v for k, v in sources_data.items() if v is not None}
        
        if not valid_sources:
            logger.warning("No valid data from any source")
            return None
        
        # If only one source, use it directly
        if len(valid_sources) == 1:
            source_name, data = list(valid_sources.items())[0]
            logger.info(f"Only one source available: {source_name}")
            return {**data, "consensus_method": "single_source"}
        
        # Calculate weighted consensus
        consensus = {
            "name": None,
            "brand": None,
            "calories": 0,
            "protein_g": 0,
            "carbs_g": 0,
            "fat_g": 0,
            "saturated_fat_g": 0,
            "sodium_mg": 0,
            "sugar_g": 0,
            "fiber_g": 0,
            "ingredients": None,
            "allergens": [],
            "sources_used": list(valid_sources.keys()),
            "consensus_method": "weighted_average"
        }
        
        # Use most recent name and brand
        for source_data in valid_sources.values():
            if source_data.get("name") and not consensus["name"]:
                consensus["name"] = source_data["name"]
            if source_data.get("brand") and not consensus["brand"]:
                consensus["brand"] = source_data["brand"]
            if source_data.get("ingredients") and not consensus["ingredients"]:
                consensus["ingredients"] = source_data["ingredients"]
        
        # Calculate weighted average for nutrition
        total_weight = 0
        nutrient_keys = ["calories", "protein_g", "carbs_g", "fat_g", 
                        "saturated_fat_g", "sodium_mg", "sugar_g", "fiber_g"]
        
        for source_data in valid_sources.values():
            confidence = source_data.get("confidence", 0.5)
            total_weight += confidence
            
            for key in nutrient_keys:
                value = source_data.get(key)
                if value is not None:
                    consensus[key] += value * confidence
        
        # Normalize by total weight
        if total_weight > 0:
            for key in nutrient_keys:
                consensus[key] = round(consensus[key] / total_weight, 2)
        
        # Merge allergens from all sources
        all_allergens = set()
        for source_data in valid_sources.values():
            allergens = source_data.get("allergens", [])
            if isinstance(allergens, list):
                all_allergens.update(allergens)
        consensus["allergens"] = list(all_allergens)
        
        # Add data variance (for quality assessment)
        consensus["data_variance"] = self._calculate_variance(valid_sources, nutrient_keys)
        
        logger.info(f"Consensus calculated from {len(valid_sources)} sources")
        logger.info(f"Data variance: {consensus['data_variance']:.1f}%")
        
        return consensus
    
    def _calculate_variance(self, sources: Dict[str, Any], keys: List[str]) -> float:
        """Calculate average variance across nutrient values."""
        if len(sources) < 2:
            return 0.0
        
        variances = []
        
        for key in keys:
            values = [s.get(key) for s in sources.values() if s.get(key) is not None]
            
            if len(values) >= 2:
                mean = sum(values) / len(values)
                if mean > 0:
                    variance = sum((v - mean) ** 2 for v in values) / len(values)
                    variance_pct = (variance ** 0.5 / mean) * 100
                    variances.append(variance_pct)
        
        return sum(variances) / len(variances) if variances else 0.0
    
    def get_best_source_data(self, multi_source_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the best data (consensus if available, otherwise highest confidence source).
        """
        consensus = multi_source_result.get("consensus")
        
        if consensus and consensus.get("name"):
            logger.info("Using consensus data")
            return consensus
        
        # Fall back to highest confidence source
        sources = multi_source_result.get("sources", {})
        valid_sources = [(k, v) for k, v in sources.items() if v is not None]
        
        if not valid_sources:
            return None
        
        # Sort by confidence
        best_source = max(valid_sources, key=lambda x: x[1].get("confidence", 0))
        logger.info(f"Using {best_source[0]} as primary source")
        
        return best_source[1]
