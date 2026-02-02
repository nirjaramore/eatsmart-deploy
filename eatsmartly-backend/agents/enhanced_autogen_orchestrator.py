"""
Enhanced AutoGen Multi-Agent Orchestrator
Uses AutoGen for intelligent coordination of:
- Multi-source data collection
- Data normalization and validation
- Web scraping
- Personalized analysis
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedAutoGenOrchestrator:
    """
    Enhanced orchestrator using AutoGen patterns for multi-agent coordination
    """
    
    def __init__(self):
        # Import agents
        from agents.multi_source_agent import MultiSourceFoodAgent
        from agents.web_scraping import WebScrapingAgent
        from agents.personalization import PersonalizationAgent
        from agents.brand_website_scraper_enhanced import BrandWebsiteScraper
        from agents.openfoodfacts_indian_fetcher import OpenFoodFactsIndiaFetcher
        
        # Initialize specialized agents
        self.data_agent = MultiSourceFoodAgent()
        self.scraping_agent = WebScrapingAgent()
        self.personalization_agent = PersonalizationAgent()
        self.brand_scraper = BrandWebsiteScraper()
        self.india_fetcher = OpenFoodFactsIndiaFetcher()
        
        logger.info("✅ Enhanced AutoGen Orchestrator initialized with 5 specialized agents")
    
    async def analyze_product_with_autogen(
        self,
        barcode: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Orchestrate multi-agent analysis using AutoGen patterns
        
        Agents collaborate in sequence:
        1. Data Collection Agent - Fetch from multiple sources
        2. India Data Agent - Check OpenFoodFacts India database
        3. Brand Scraper Agent - Scrape official website
        4. Web Scraping Agent - Get recipes and alternatives
        5. Personalization Agent - Apply user profile
        """
        logger.info("=" * 100)
        logger.info(f"🤖 AUTOGEN MULTI-AGENT ORCHESTRATION")
        logger.info(f"📊 Barcode: {barcode}")
        logger.info(f"👤 User: {user_id}")
        logger.info("=" * 100)
        
        try:
            # STEP 1: Multi-source data collection
            logger.info("📡 STEP 1: Fetching from multiple data sources...")
            product_data = await self._collect_from_all_sources(barcode)
            
            if not product_data or not product_data.get("product_name"):
                logger.warning("❌ No product data found in any source")
                return {"error": f"Product {barcode} not found in any database"}
            
            logger.info(f"✅ Product found: {product_data.get('product_name')}")
            logger.info(f"   Brand: {product_data.get('brand', 'Unknown')}")
            logger.info(f"   Calories: {product_data.get('nutrition', {}).get('calories', 'N/A')}")
            
            # STEP 1.5: Try to enhance with brand website data
            logger.info("🌐 STEP 1.5: Attempting to fetch from brand website...")
            brand_data = self.brand_scraper.scrape_nutrition_from_website(
                product_data.get("product_name", ""),
                barcode
            )
            
            if brand_data:
                logger.info("   ✅ Enhanced with brand website data")
                # Merge brand data (only fill missing values)
                nutrition = product_data.get("nutrition", {})
                for key, value in brand_data.items():
                    if value and not nutrition.get(key):
                        nutrition[key] = value
                product_data["nutrition"] = nutrition
            
            # STEP 2: Scrape recipes and alternatives
            logger.info("🍳 STEP 2: Scraping recipes and nutrition tips...")
            recipes = []
            nutrition_tips = []
            
            try:
                food_name = product_data.get("product_name", "")
                recipes_data = self.scraping_agent.scrape_recipes(food_name, max_recipes=3)
                recipes = recipes_data.get("recipes", [])
                logger.info(f"   ✅ Found {len(recipes)} recipes")
            except Exception as e:
                logger.warning(f"   ⚠️  Recipe scraping failed: {e}")
            
            try:
                tips_data = self.scraping_agent.scrape_nutrition_tips(food_name)
                nutrition_tips = tips_data.get("tips", [])
                logger.info(f"   ✅ Found {len(nutrition_tips)} nutrition tips")
            except Exception as e:
                logger.warning(f"   ⚠️  Nutrition tips scraping failed: {e}")
            
            # STEP 3: Apply personalization
            logger.info("👤 STEP 3: Applying personalized health analysis...")
            user_profile = self.personalization_agent.get_user_profile(user_id)
            
            # Evaluate food safety
            evaluation = self.personalization_agent.evaluate_food_safety(
                product_data,
                user_profile
            )
            
            logger.info(f"   🎯 Verdict: {evaluation['verdict'].upper()}")
            logger.info(f"   💯 Health Score: {evaluation['health_score']}/100")
            logger.info(f"   ⚠️  Alerts: {len(evaluation.get('alerts', []))}")
            logger.info(f"   💡 Suggestions: {len(evaluation.get('suggestions', []))}")
            
            # Build comprehensive response
            response = {
                "barcode": barcode,
                "product_name": product_data.get("product_name"),
                "brand": product_data.get("brand"),
                "category": product_data.get("category"),
                
                # Nutrition data (consensus from multiple sources)
                "nutrition": product_data.get("nutrition", {}),
                "ingredients": product_data.get("ingredients"),
                "allergens": product_data.get("allergens", []),
                
                # Personalized evaluation
                "verdict": evaluation["verdict"],
                "risk_level": evaluation["risk_level"],
                "health_score": evaluation["health_score"],
                "alerts": evaluation.get("alerts", []),
                "warnings": evaluation.get("warnings", []),
                "suggestions": evaluation.get("suggestions", []),
                
                # Enriched content
                "alternatives": evaluation.get("alternatives", []),
                "recipes": recipes,
                "nutrition_tips": nutrition_tips,
                
                # Metadata
                "data_quality": product_data.get("data_quality", {}),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "sources_used": product_data.get("data_quality", {}).get("sources_found", 0),
            }
            
            logger.info("=" * 100)
            logger.info("✅ AUTOGEN ORCHESTRATION COMPLETE")
            logger.info("=" * 100)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ AutoGen orchestration failed: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def _collect_from_all_sources(self, barcode: str) -> Dict[str, Any]:
        """
        Collect data from all available sources using Multi-Source Agent
        """
        # Use the multi-source agent which already implements:
        # - Open Food Facts (India + Global)
        # - USDA FoodData Central
        # - Nutritionix
        # - Edamam
        # - Consensus calculation
        
        product_data = self.data_agent.fetch_from_all_sources(barcode)
        
        if not product_data:
            return {}
        
        return product_data
    
    def enhance_with_indian_data(self, barcode: str) -> Optional[Dict]:
        """
        Check if product exists in our Indian products database
        and enhance with that data
        """
        try:
            # This would query a local database of Indian products
            # fetched using OpenFoodFactsIndiaFetcher
            # For now, it's a placeholder
            return None
        except Exception as e:
            logger.warning(f"   ⚠️  Indian data enhancement failed: {e}")
            return None
    
    async def search_products(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        source: str = "all"
    ) -> List[Dict]:
        """
        Search for products across multiple sources
        
        Args:
            query: Search query (product name)
            user_id: User identifier
            limit: Maximum results
            source: 'all', 'india', 'usda', 'openfoodfacts'
        """
        logger.info(f"🔍 Searching for: {query} (limit: {limit}, source: {source})")
        
        results = []
        
        try:
            if source in ['all', 'india']:
                # Search OpenFoodFacts India
                india_results = await self._search_openfoodfacts_india(query, limit // 2)
                results.extend(india_results)
            
            if source in ['all', 'usda']:
                # Search USDA
                usda_results = self._search_usda(query, limit // 2)
                results.extend(usda_results)
            
            if source in ['all', 'openfoodfacts']:
                # Search OpenFoodFacts Global
                off_results = await self._search_openfoodfacts_global(query, limit // 2)
                results.extend(off_results)
            
            # Remove duplicates based on barcode
            seen_barcodes = set()
            unique_results = []
            for result in results:
                barcode = result.get('barcode')
                if barcode and barcode not in seen_barcodes:
                    seen_barcodes.add(barcode)
                    unique_results.append(result)
                elif not barcode:
                    unique_results.append(result)
            
            logger.info(f"✅ Found {len(unique_results)} results")
            return unique_results[:limit]
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []
    
    async def _search_openfoodfacts_india(self, query: str, limit: int) -> List[Dict]:
        """Search OpenFoodFacts India database"""
        try:
            import requests
            
            url = f"https://in.openfoodfacts.org/cgi/search.pl"
            params = {
                'search_terms': query,
                'json': 1,
                'page_size': limit,
                'fields': 'code,product_name,brands,nutriments,categories_tags'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            products = data.get('products', [])
            
            # Normalize to our format
            results = []
            for product in products:
                normalized = self.india_fetcher.normalize_product(product)
                if normalized:
                    results.append(normalized)
            
            return results
            
        except Exception as e:
            logger.warning(f"   ⚠️  India search failed: {e}")
            return []
    
    def _search_usda(self, query: str, limit: int) -> List[Dict]:
        """Search USDA FoodData Central"""
        try:
            from agents.data_collection import DataCollectionAgent
            
            data_agent = DataCollectionAgent()
            results = data_agent.search_food_by_name(query, limit)
            
            return results
            
        except Exception as e:
            logger.warning(f"   ⚠️  USDA search failed: {e}")
            return []
    
    async def _search_openfoodfacts_global(self, query: str, limit: int) -> List[Dict]:
        """Search OpenFoodFacts Global database"""
        try:
            import requests
            
            url = f"https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                'search_terms': query,
                'json': 1,
                'page_size': limit,
                'fields': 'code,product_name,brands,nutriments,categories_tags'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            products = data.get('products', [])
            
            # Normalize to our format
            results = []
            for product in products:
                normalized = self.india_fetcher.normalize_product(product)
                if normalized:
                    results.append(normalized)
            
            return results
            
        except Exception as e:
            logger.warning(f"   ⚠️  Global search failed: {e}")
            return []
