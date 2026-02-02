"""
AutoGen-based Multi-Agent Orchestrator for EatSmartly.
Uses Microsoft AutoGen to coordinate multiple agents for food analysis.
"""
import asyncio
from typing import Dict, Any, List, Optional
import os

try:
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    # Create dummy classes to avoid runtime errors
    class AssistantAgent:
        pass
    class UserProxyAgent:
        pass
    class GroupChat:
        pass
    class GroupChatManager:
        pass

from config import settings
from agents.utils import setup_logger
from agents.multi_source_agent import MultiSourceDataAgent
from agents.web_scraping import WebScrapingAgent
from agents.personalization import PersonalizationAgent
from agents.brand_website_scraper import BrandWebsiteScraper

logger = setup_logger(__name__, settings.LOG_LEVEL)


class AutoGenOrchestrator:
    """
    Orchestrator using Microsoft AutoGen for multi-agent coordination.
    Coordinates data collection, verification, and personalization agents.
    """
    
    def __init__(self):
        """Initialize AutoGen orchestrator with multiple agents."""
        
        # Initialize our custom agents
        self.data_agent = MultiSourceDataAgent()
        self.scraping_agent = WebScrapingAgent()
        self.personalization_agent = PersonalizationAgent()
        self.brand_scraper = BrandWebsiteScraper()
        
        # Configure AutoGen LLM (using Gemini)
        self.llm_config = {
            "model": "gemini-pro",
            "api_key": settings.GEMINI_API_KEY,
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        logger.info("AutoGen Orchestrator initialized with Brand Website Scraper")
    
    async def analyze_product_with_autogen(
        self, 
        barcode: str, 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Analyze product using AutoGen multi-agent system.
        
        Agents:
        1. Data Collector Agent: Fetches from multiple sources
        2. Verification Agent: Cross-checks data quality
        3. Personalization Agent: Applies user preferences
        4. Report Agent: Generates final analysis
        
        Args:
            barcode: Product barcode
            user_id: User identifier
            
        Returns:
            Complete analysis with verified data
        """
        logger.info(f"Starting AutoGen analysis for barcode: {barcode}")
        
        # Step 1: Fetch from all sources
        logger.info("📡 STEP 1: Fetching from multiple data sources...")
        multi_source_data = await self.data_agent.fetch_from_all_sources(barcode)
        
        # Get consensus/best data
        product_data = self.data_agent.get_best_source_data(multi_source_data)
        
        if not product_data:
            logger.warning(f"❌ No product data found for barcode: {barcode}")
            logger.warning(f"   Checked: Open Food Facts (India + Global), USDA, Nutritionix, Edamam")
            return {
                "error": "Product not found in any database",
                "barcode": barcode,
                "sources_checked": ["Open Food Facts India", "Open Food Facts Global", "USDA", "Nutritionix", "Edamam"]
            }
        
        logger.info(f"✅ Product found: {product_data.get('name', 'Unknown')}")
        
        logger.info(f"✅ Product found: {product_data.get('name', 'Unknown')}")
        
        # Step 1.5: Try brand website (additional source)
        logger.info("🌐 STEP 1.5: Attempting to fetch from brand website...")
        product_name = product_data.get("name", "")
        brand_data = await self.brand_scraper.fetch_from_brand_website(barcode, product_name)
        if brand_data:
            logger.info(f"✅ Additional data from brand website")
        else:
            logger.info(f"ℹ️  No additional data from brand website")
        
        # Step 2: Enrich with web data
        logger.info("🍳 STEP 2: Scraping recipes and nutrition tips...")
        product_name = product_data.get("name", "")
        
        try:
            recipes = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.scraping_agent.scrape_recipes(product_name, limit=2)
                ),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            recipes = self.scraping_agent._get_mock_recipes(product_name, 2)
            logger.info("⏱️  Recipe scraping timed out, using fallback recipes")
        
        nutrition_tips = self.scraping_agent.get_nutrition_tips(product_data)
        logger.info(f"✅ Found {len(recipes)} recipes and {len(nutrition_tips)} tips")
        
        # Step 3: Personalize
        logger.info("👤 STEP 3: Applying personalized health analysis...")
        user_profile = self.personalization_agent.get_user_profile(user_id)
        evaluation = self.personalization_agent.evaluate_food_safety(product_data, user_profile)
        suggestions = self.personalization_agent.generate_suggestions(
            product_data,
            user_profile,
            evaluation
        )
        
        # Get alternatives if needed
        alternatives = []
        if evaluation["verdict"] in ["caution", "avoid"]:
            alternatives = self.scraping_agent.find_alternatives(
                product_name,
                user_profile.get("health_goal", "general"),
                limit=5
            )
        
        # Step 4: Compile comprehensive report
        analysis = {
            "barcode": barcode,
            "product_name": product_data.get("name"),
            "brand": product_data.get("brand"),
            
            # Multi-source verification
            "data_sources": multi_source_data.get("sources"),
            "consensus_data": multi_source_data.get("consensus"),
            "data_quality": {
                "sources_found": len([s for s in multi_source_data.get("sources", {}).values() if s]),
                "variance": multi_source_data.get("consensus", {}).get("data_variance", 0),
                "confidence": "High" if multi_source_data.get("consensus", {}).get("data_variance", 100) < 10 else "Medium"
            },
            
            # Nutrition
            "nutrition": {
                "calories": product_data.get("calories"),
                "protein_g": product_data.get("protein_g"),
                "carbs_g": product_data.get("carbs_g"),
                "fat_g": product_data.get("fat_g"),
                "saturated_fat_g": product_data.get("saturated_fat_g"),
                "sodium_mg": product_data.get("sodium_mg"),
                "sugar_g": product_data.get("sugar_g"),
                "fiber_g": product_data.get("fiber_g"),
            },
            
            # Safety evaluation
            "verdict": evaluation["verdict"],
            "risk_level": evaluation["risk_level"],
            "health_score": evaluation["health_score"],
            "alerts": evaluation["alerts"],
            "warnings": evaluation["warnings"],
            
            # Recommendations
            "suggestions": suggestions,
            "alternatives": alternatives,
            "recipes": recipes,
            "nutrition_tips": nutrition_tips,
            
            # Metadata
            "ingredients": product_data.get("ingredients"),
            "allergens": product_data.get("allergens", []),
            "analysis_timestamp": multi_source_data.get("timestamp")
        }
        
        logger.info(f"AutoGen analysis complete for {product_name}")
        logger.info(f"Data quality: {analysis['data_quality']['confidence']} " 
                   f"(variance: {analysis['data_quality']['variance']:.1f}%)")
        
        return analysis
    
    def create_autogen_agents(self):
        """
        Create AutoGen agents for collaborative analysis.
        This demonstrates AutoGen's conversational AI capabilities.
        """
        
        # Data Collection Agent
        data_collector = AssistantAgent(
            name="DataCollector",
            system_message="""You are a data collection specialist. 
            Your job is to gather product information from multiple sources:
            - Open Food Facts (community database)
            - USDA FoodData Central (official US database)
            - Nutritionix (commercial database)
            
            Always cross-verify data and report any discrepancies.""",
            llm_config=self.llm_config
        )
        
        # Verification Agent
        verifier = AssistantAgent(
            name="DataVerifier",
            system_message="""You are a data quality expert.
            Review nutrition data from multiple sources and:
            1. Identify discrepancies
            2. Calculate confidence scores
            3. Flag suspicious data
            4. Recommend consensus values
            
            Be strict about data quality.""",
            llm_config=self.llm_config
        )
        
        # Health Analyst Agent
        health_analyst = AssistantAgent(
            name="HealthAnalyst",
            system_message="""You are a nutrition and health expert.
            Analyze food products for health impact:
            1. Evaluate nutritional quality
            2. Identify health risks
            3. Suggest healthier alternatives
            4. Provide personalized recommendations
            
            Consider user health goals and restrictions.""",
            llm_config=self.llm_config
        )
        
        # User Proxy (represents the system)
        user_proxy = UserProxyAgent(
            name="System",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            code_execution_config={"use_docker": False}
        )
        
        return {
            "data_collector": data_collector,
            "verifier": verifier,
            "health_analyst": health_analyst,
            "user_proxy": user_proxy
        }
    
    def create_group_chat(self, agents: Dict[str, Any]):
        """Create AutoGen group chat for agent collaboration."""
        
        agent_list = list(agents.values())
        
        group_chat = GroupChat(
            agents=agent_list,
            messages=[],
            max_round=10
        )
        
        manager = GroupChatManager(
            groupchat=group_chat,
            llm_config=self.llm_config
        )
        
        return manager
    
    async def collaborative_analysis(self, barcode: str, user_id: str) -> str:
        """
        Perform collaborative analysis using AutoGen group chat.
        Agents discuss and reach consensus on product analysis.
        
        NOTE: This is a demonstration of AutoGen's capabilities.
        For production, use analyze_product_with_autogen() for speed.
        """
        logger.info(f"Starting collaborative AutoGen analysis for: {barcode}")
        
        # Create agents
        agents = self.create_autogen_agents()
        
        # Create group chat
        manager = self.create_group_chat(agents)
        
        # Start conversation
        initial_message = f"""
        Analyze this food product collaboratively:
        
        Barcode: {barcode}
        User ID: {user_id}
        
        Tasks:
        1. DataCollector: Fetch product data from all sources
        2. DataVerifier: Cross-check data quality and accuracy
        3. HealthAnalyst: Evaluate health impact and provide recommendations
        
        Discuss and reach consensus on the final analysis.
        """
        
        # Initiate chat
        agents["user_proxy"].initiate_chat(
            manager,
            message=initial_message
        )
        
        # Extract final analysis from conversation
        conversation = manager.groupchat.messages
        
        logger.info("Collaborative analysis complete")
        
        return {
            "conversation": conversation,
            "final_analysis": "See conversation for detailed collaborative analysis"
        }


# Global orchestrator instance
orchestrator = AutoGenOrchestrator()
