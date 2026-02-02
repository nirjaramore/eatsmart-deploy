"""
EatSmartly Backend - FastAPI Application with Multi-Agent System.
Main entry point for the barcode food analyzer API.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from config import settings
from agents.data_collection import DataCollectionAgent
from agents.web_scraping import WebScrapingAgent
from agents.personalization import PersonalizationAgent
# from agents.autogen_orchestrator import AutoGenOrchestrator  # Temporarily disabled
from agents.utils import setup_logger


# Setup logging
logger = setup_logger(__name__, settings.LOG_LEVEL)

# Initialize FastAPI app
app = FastAPI(
    title="EatSmartly API",
    description="AI-powered barcode food analyzer with multi-agent system",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS middleware for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
data_agent = DataCollectionAgent()
scraping_agent = WebScrapingAgent()
personalization_agent = PersonalizationAgent()
# autogen_orchestrator = AutoGenOrchestrator()  # Temporarily disabled

logger.info("Agents initialized (AutoGen orchestrator disabled for testing)")



# ==================== Request/Response Models ====================

class BarcodeAnalysisRequest(BaseModel):
    """Request model for barcode analysis."""
    barcode: Optional[str] = Field(None, description="Product barcode")
    product_id: Optional[int] = Field(None, description="Product ID from database")
    product_name: Optional[str] = Field(None, description="Product name")
    user_id: str = Field(..., description="User identifier")
    detailed: bool = Field(default=False, description="Include detailed nutrition breakdown")


class ProductAnalysisRequest(BaseModel):
    """Request model for product analysis by name/ID."""
    product_id: Optional[int] = Field(None, description="Product ID from database")
    product_name: Optional[str] = Field(None, description="Product name")
    user_id: str = Field(..., description="User identifier")
    detailed: bool = Field(default=False, description="Include detailed nutrition breakdown")


class FoodAnalysisResponse(BaseModel):
    """Response model for food analysis."""
    barcode: str
    food_name: Optional[str]
    brand: Optional[str]
    verdict: str  # safe, caution, avoid
    risk_level: str  # low, medium, high
    health_score: float
    alerts: List[str]
    warnings: List[str]
    suggestions: List[str]
    alternatives: List[Dict[str, str]]
    recipes: List[Dict[str, Any]]
    nutrition_tips: List[str]
    detailed_nutrition: Optional[Dict[str, Any]] = None
    timestamp: str


class UserProfileRequest(BaseModel):
    """Request model for user profile."""
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    health_goal: Optional[str] = None
    allergies: Optional[List[str]] = []
    health_conditions: Optional[List[str]] = []
    dietary_restrictions: Optional[List[str]] = []


class SearchRequest(BaseModel):
    """Request model for food search."""
    query: str = Field(..., description="Food name to search")
    user_id: str = Field(..., description="User identifier")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum results")


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "EatSmartly API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze-barcode",
            "search": "/search",
            "profile": "/user/{user_id}/profile"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        if data_agent.db_engine:
            data_agent.db_engine.connect()
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        # Check Redis connection
        if data_agent.redis_client:
            data_agent.redis_client.ping()
            redis_status = "connected"
        else:
            redis_status = "disconnected"
        
        # Determine overall health
        all_healthy = db_status == "connected" and redis_status == "connected"
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": db_status,
                "redis": redis_status,
                "agents": "active"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.post("/analyze-barcode", response_model=FoodAnalysisResponse)
async def analyze_barcode(request: BarcodeAnalysisRequest):
    """
    Analyze a barcode using AutoGen multi-agent system.
    
    Features:
    1. Multi-source data collection (Open Food Facts, USDA, Nutritionix)
    2. Cross-verification and consensus calculation
    3. Web scraping for recipes and alternatives
    4. Personalized recommendations based on user profile
    
    The AutoGen orchestrator coordinates all agents for accurate analysis.
    """
    try:
        logger.info("\n" + "="*100)
        logger.info(f"🔍 BARCODE ANALYSIS REQUEST")
        logger.info(f"📊 Barcode: {request.barcode}")
        logger.info(f"👤 User ID: {request.user_id}")
        logger.info(f"📝 Detailed: {request.detailed}")
        logger.info("="*100)
        
        logger.info("🚀 STEP 1/4: Initiating AutoGen Multi-Agent Orchestrator...")
        
        logger.info("🚀 STEP 1/4: Initiating AutoGen Multi-Agent Orchestrator...")
        
        # === USE SIMPLE ANALYSIS (AutoGen disabled) ===
        logger.info("🤖 STEP 2/4: Running simple analysis...")
        # Get basic product data from database
        product_data = data_agent.fetch_food_data(request.barcode)
        
        if not product_data:
            logger.error(f"❌ ANALYSIS FAILED: Product {request.barcode} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with barcode {request.barcode} not found"
            )
        
        # Simple evaluation
        user_profile = personalization_agent.get_user_profile(request.user_id)
        evaluation = personalization_agent.evaluate_food_safety(product_data, user_profile)
        
        analysis = {
            "product_name": product_data.get("name"),
            "brand": product_data.get("brand"),
            "nutrition": {
                "calories": product_data.get("calories"),
                "protein_g": product_data.get("protein_g"),
                "carbs_g": product_data.get("carbs_g"),
                "fat_g": product_data.get("fat_g"),
                "sugar_g": product_data.get("sugar_g"),
                "fiber_g": product_data.get("fiber_g"),
                "sodium_mg": product_data.get("sodium_mg")
            },
            "ingredients": product_data.get("ingredients"),
            "allergens": product_data.get("allergens"),
            "verdict": evaluation.get("verdict", "caution"),
            "risk_level": evaluation.get("risk_level", "medium"),
            "health_score": evaluation.get("health_score", 50),
            "alerts": evaluation.get("alerts", []),
            "warnings": evaluation.get("warnings", []),
            "suggestions": evaluation.get("suggestions", []),
            "alternatives": [],
            "recipes": [],
            "nutrition_tips": ["Check nutrition labels regularly"],
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "data_quality": {
                "sources_found": 1,
                "confidence": "Database",
                "variance": 0
            }
        }
        
        logger.info("✅ STEP 3/4: Analysis complete, processing results...")
        
        logger.info("✅ STEP 3/4: Analysis complete, processing results...")
        
        # Check if product was found
        if "error" in analysis:
            logger.error(f"❌ ANALYSIS FAILED: {analysis['error']}")
            logger.error(f"🚨 Product {request.barcode} not found in any data source")
            logger.info("="*100 + "\n")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=analysis["error"]
            )
        
        # Build detailed nutrition if requested
        detailed_nutrition = None
        if request.detailed:
            nutrition = analysis.get("nutrition", {})
            detailed_nutrition = {
                "serving_size": 100,  # Consensus data is per 100g
                "serving_unit": "g",
                "calories": nutrition.get("calories"),
                "protein_g": nutrition.get("protein_g"),
                "carbs_g": nutrition.get("carbs_g"),
                "fat_g": nutrition.get("fat_g"),
                "saturated_fat_g": nutrition.get("saturated_fat_g"),
                "sodium_mg": nutrition.get("sodium_mg"),
                "sugar_g": nutrition.get("sugar_g"),
                "fiber_g": nutrition.get("fiber_g"),
                "ingredients": analysis.get("ingredients"),
                "allergens": analysis.get("allergens"),
                "data_sources": analysis.get("data_quality", {}).get("sources_found", 0),
                "data_confidence": analysis.get("data_quality", {}).get("confidence", "Unknown"),
                "data_variance": analysis.get("data_quality", {}).get("variance", 0)
            }
        
        # Build response
        response = FoodAnalysisResponse(
            barcode=request.barcode,
            food_name=analysis.get("product_name"),
            brand=analysis.get("brand"),
            verdict=analysis.get("verdict"),
            risk_level=analysis.get("risk_level"),
            health_score=analysis.get("health_score"),
            alerts=analysis.get("alerts", []),
            warnings=analysis.get("warnings", []),
            suggestions=analysis.get("suggestions", []),
            alternatives=analysis.get("alternatives", []),
            recipes=analysis.get("recipes", []),
            nutrition_tips=analysis.get("nutrition_tips", []),
            detailed_nutrition=detailed_nutrition,
            timestamp=analysis.get("analysis_timestamp")
        )
        
        logger.info(f"Analysis complete for barcode: {request.barcode}")
        logger.info(f"📊 Data sources used: {analysis.get('data_quality', {}).get('sources_found', 0)}/4")
        logger.info(f"🎯 Data confidence: {analysis.get('data_quality', {}).get('confidence', 'Unknown')}")
        logger.info(f"🔴 Verdict: {analysis.get('verdict', 'Unknown').upper()}")
        logger.info(f"💯 Health Score: {analysis.get('health_score', 0)}/100")
        logger.info("✅ STEP 4/4: Response prepared and sent to client")
        logger.info("="*100 + "\n")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("="*100)
        logger.error("🚨 CRITICAL ERROR IN BARCODE ANALYSIS")
        logger.error(f"🐞 Error Type: {type(e).__name__}")
        logger.error(f"📝 Error Message: {str(e)}")
        logger.error(f"📊 Barcode: {request.barcode}")
        logger.error("="*100, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/analyze-product", response_model=FoodAnalysisResponse)
async def analyze_product(request: BarcodeAnalysisRequest):
    """
    Analyze a product by barcode, name, or ID.
    
    This endpoint allows analysis of products using barcode, product name, or database ID.
    """
    try:
        logger.info("\n" + "="*100)
        logger.info(f"🔍 PRODUCT ANALYSIS REQUEST")
        logger.info(f"📊 Barcode: {request.barcode}")
        logger.info(f"📊 Product ID: {request.product_id}")
        logger.info(f"📝 Product Name: {request.product_name}")
        logger.info(f"👤 User ID: {request.user_id}")
        logger.info(f"📝 Detailed: {request.detailed}")
        logger.info("="*100)
        
        # Get product data based on what's provided
        product_data = None
        
        if request.barcode:
            logger.info("   Using barcode for analysis")
            product_data = data_agent.fetch_food_data(request.barcode)
        elif request.product_id:
            logger.info("   Using product ID for analysis")
            product_data = data_agent.get_product_by_id(request.product_id)
        elif request.product_name:
            logger.info("   Using product name for analysis")
            # Search for the product and get the first match
            search_results = data_agent.search_food_by_name(request.product_name, 1)
            if search_results:
                product_data = search_results[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product '{request.product_name}' not found"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide barcode, product_id, or product_name"
            )
        
        if not product_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        logger.info("🚀 STEP 1/3: Product found, running analysis...")
        
        # Analyze the product
        if request.barcode:
            # Use simple barcode analysis
            analysis = await _analyze_barcode_simple(request.barcode, request.user_id)
        else:
            # Create analysis from database data
            analysis = await _analyze_product_from_data(product_data, request.user_id)
        
        logger.info("✅ STEP 2/3: Analysis complete, processing results...")
        
        # Check if analysis was successful
        if "error" in analysis:
            logger.error(f"❌ ANALYSIS FAILED: {analysis['error']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=analysis["error"]
            )
        
        # Build detailed nutrition if requested
        detailed_nutrition = None
        if request.detailed:
            nutrition = analysis.get("nutrition", {})
            detailed_nutrition = {
                "serving_size": 100,
                "serving_unit": "g",
                "calories": nutrition.get("calories"),
                "protein_g": nutrition.get("protein_g"),
                "carbs_g": nutrition.get("carbs_g"),
                "fat_g": nutrition.get("fat_g"),
                "saturated_fat_g": nutrition.get("saturated_fat_g"),
                "sodium_mg": nutrition.get("sodium_mg"),
                "sugar_g": nutrition.get("sugar_g"),
                "fiber_g": nutrition.get("fiber_g"),
                "ingredients": analysis.get("ingredients"),
                "allergens": analysis.get("allergens"),
                "data_sources": 1,  # Database only
                "data_confidence": "Database",
                "data_variance": 0
            }
        
        # Build response
        response = FoodAnalysisResponse(
            barcode=request.barcode or f"no-barcode-{product_data.get('id', 'unknown')}",
            food_name=analysis.get("product_name"),
            brand=analysis.get("brand"),
            verdict=analysis.get("verdict"),
            risk_level=analysis.get("risk_level"),
            health_score=analysis.get("health_score"),
            alerts=analysis.get("alerts", []),
            warnings=analysis.get("warnings", []),
            suggestions=analysis.get("suggestions", []),
            alternatives=analysis.get("alternatives", []),
            recipes=analysis.get("recipes", []),
            nutrition_tips=analysis.get("nutrition_tips", []),
            detailed_nutrition=detailed_nutrition,
            timestamp=analysis.get("analysis_timestamp")
        )
        
        logger.info(f"Product analysis complete for: {product_data.get('name', 'Unknown')}")
        logger.info(f"🔴 Verdict: {analysis.get('verdict', 'Unknown').upper()}")
        logger.info(f"💯 Health Score: {analysis.get('health_score', 0)}/100")
        logger.info("✅ STEP 3/3: Response prepared and sent to client")
        logger.info("="*100 + "\n")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("="*100)
        logger.error("🚨 CRITICAL ERROR IN PRODUCT ANALYSIS")
        logger.error(f"🐞 Error Type: {type(e).__name__}")
        logger.error(f"📝 Error Message: {str(e)}")
        logger.error(f"📊 Barcode: {request.barcode}")
        logger.error(f"📊 Product ID: {request.product_id}")
        logger.error(f"📝 Product Name: {request.product_name}")
        logger.error("="*100, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


async def _analyze_product_from_data(product_data: dict, user_id: str) -> dict:
    """Analyze product using database data when barcode analysis isn't available."""
    try:
        # Get user profile for personalization
        user_profile = personalization_agent.get_user_profile(user_id)
        
        # Extract nutrition data
        nutrition = {
            "calories": product_data.get("calories"),
            "protein_g": product_data.get("protein_g"),
            "carbs_g": product_data.get("carbs_g"),
            "fat_g": product_data.get("fat_g"),
            "saturated_fat_g": product_data.get("saturated_fat_g"),
            "sugar_g": product_data.get("sugar_g"),
            "fiber_g": product_data.get("fiber_g"),
            "sodium_mg": product_data.get("sodium_mg")
        }
        
        # Evaluate food safety
        evaluation = personalization_agent.evaluate_food_safety({
            "name": product_data.get("name"),
            "nutrition": nutrition,
            "ingredients": product_data.get("ingredients"),
            "allergens": product_data.get("allergens")
        }, user_profile)
        
        # Find alternatives
        alternatives = []
        if product_data.get("name"):
            search_term = product_data["name"].split()[0]  # First word
            similar_products = data_agent.search_food_by_name(search_term, 5)
            
            for alt_product in similar_products:
                if alt_product.get("id") != product_data.get("id"):
                    alt_score = 0
                    improvements = []
                    
                    # Compare sugar content
                    if alt_product.get("sugar_g", 999) < product_data.get("sugar_g", 999):
                        alt_score += 25
                        improvements.append("Lower sugar")
                    
                    # Compare protein
                    if alt_product.get("protein_g", 0) > product_data.get("protein_g", 0):
                        alt_score += 20
                        improvements.append("Higher protein")
                    
                    # Compare fiber
                    if alt_product.get("fiber_g", 0) > product_data.get("fiber_g", 0):
                        alt_score += 15
                        improvements.append("Higher fiber")
                    
                    if alt_score > 0:
                        alternatives.append({
                            "name": alt_product.get("name"),
                            "brand": alt_product.get("brand"),
                            "reason": "better_nutrition",
                            "score_improvement": alt_score,
                            "description": ", ".join(improvements)
                        })
        
        return {
            "product_name": product_data.get("name"),
            "brand": product_data.get("brand"),
            "nutrition": nutrition,
            "ingredients": product_data.get("ingredients"),
            "allergens": product_data.get("allergens"),
            "verdict": evaluation.get("verdict", "caution"),
            "risk_level": evaluation.get("risk_level", "medium"),
            "health_score": evaluation.get("health_score", 50),
            "alerts": evaluation.get("alerts", []),
            "warnings": evaluation.get("warnings", []),
            "suggestions": evaluation.get("suggestions", []),
            "alternatives": alternatives,
            "recipes": [],
            "nutrition_tips": [
                "Check nutrition labels regularly",
                "Compare similar products for better choices",
                "Consider your daily nutritional goals"
            ],
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "data_quality": {
                "sources_found": 1,
                "confidence": "Database",
                "variance": 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing product from data: {e}")
        return {
            "error": f"Failed to analyze product: {str(e)}"
        }


async def _analyze_barcode_simple(barcode: str, user_id: str) -> dict:
    """Simple barcode analysis without AutoGen."""
    try:
        # Get product data from database
        product_data = data_agent.fetch_food_data(barcode)
        
        if not product_data:
            return {"error": f"Product with barcode {barcode} not found"}
        
        # Get user profile for personalization
        user_profile = personalization_agent.get_user_profile(user_id)
        
        # Extract nutrition data
        nutrition = {
            "calories": product_data.get("calories"),
            "protein_g": product_data.get("protein_g"),
            "carbs_g": product_data.get("carbs_g"),
            "fat_g": product_data.get("fat_g"),
            "saturated_fat_g": product_data.get("saturated_fat_g"),
            "sugar_g": product_data.get("sugar_g"),
            "fiber_g": product_data.get("fiber_g"),
            "sodium_mg": product_data.get("sodium_mg")
        }
        
        # Evaluate food safety
        evaluation = personalization_agent.evaluate_food_safety({
            "name": product_data.get("name"),
            "nutrition": nutrition,
            "ingredients": product_data.get("ingredients"),
            "allergens": product_data.get("allergens")
        }, user_profile)
        
        return {
            "product_name": product_data.get("name"),
            "brand": product_data.get("brand"),
            "nutrition": nutrition,
            "ingredients": product_data.get("ingredients"),
            "allergens": product_data.get("allergens"),
            "verdict": evaluation.get("verdict", "caution"),
            "risk_level": evaluation.get("risk_level", "medium"),
            "health_score": evaluation.get("health_score", 50),
            "alerts": evaluation.get("alerts", []),
            "warnings": evaluation.get("warnings", []),
            "suggestions": evaluation.get("suggestions", []),
            "alternatives": [],
            "recipes": [],
            "nutrition_tips": ["Check nutrition labels regularly"],
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "data_quality": {
                "sources_found": 1,
                "confidence": "Database",
                "variance": 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error in simple barcode analysis: {e}")
        return {
            "error": f"Failed to analyze barcode: {str(e)}"
        }


@app.post("/search")
async def search_food(request: SearchRequest):
    """Search for food by name."""
    try:
        logger.info(f"🔍 Searching for: {request.query}")
        
        results = data_agent.search_food_by_name(request.query, request.limit)
        
        logger.info(f"✅ Found {len(results)} results for '{request.query}'")
        
        return {
            "query": request.query,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


class AlternativesRequest(BaseModel):
    """Request model for alternatives."""
    barcode: Optional[str] = Field(None, description="Product barcode")
    product_id: Optional[int] = Field(None, description="Product ID from database")
    product_name: Optional[str] = Field(None, description="Product name")
    user_id: str = Field(..., description="User identifier")
    criteria: str = Field(default="all", description="Criteria: 'protein', 'sugar', 'fat', 'fiber', 'all'")


@app.post("/alternatives")
async def get_alternatives(request: AlternativesRequest):
    """
    Get healthier alternatives for a product.
    
    Args:
        request: AlternativesRequest with barcode, product_id, product_name, user_id, and criteria
    """
    try:
        logger.info(f"🔄 Finding alternatives for barcode: {request.barcode}, product_id: {request.product_id}, product_name: {request.product_name}")
        logger.info(f"   Criteria: {request.criteria}")
        
        # Get product data based on what's provided
        product_data = None
        
        if request.barcode:
            logger.info("   Using barcode for alternatives")
            product_data = data_agent.fetch_food_data(request.barcode)
        elif request.product_id:
            logger.info("   Using product ID for alternatives")
            product_data = data_agent.get_product_by_id(request.product_id)
        elif request.product_name:
            logger.info("   Using product name for alternatives")
            # Search for the product and get the first match
            search_results = data_agent.search_food_by_name(request.product_name, 1)
            if search_results:
                product_data = search_results[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product '{request.product_name}' not found"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide barcode, product_id, or product_name"
            )
        
        if not product_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        product_name = product_data.get("name", "")
        nutrition = {
            "calories": product_data.get("calories"),
            "protein_g": product_data.get("protein_g"),
            "carbs_g": product_data.get("carbs_g"),
            "fat_g": product_data.get("fat_g"),
            "sugar_g": product_data.get("sugar_g"),
            "fiber_g": product_data.get("fiber_g"),
            "saturated_fat_g": product_data.get("saturated_fat_g")
        }
        
        # Search for similar products
        search_query = product_name.split()[0]  # First word of product name
        similar_products = data_agent.search_food_by_name(search_query, 10)
        
        # Filter and rank alternatives
        alternatives = []
        
        for product in similar_products:
            # Skip the same product
            if (request.barcode and product.get("barcode") == request.barcode) or \
               (request.product_id and product.get("id") == request.product_id) or \
               (request.product_name and product.get("name") == request.product_name):
                continue
            
            score = 0
            improvements = []
            
            # Compare nutrition
            if request.criteria in ["protein", "all"]:
                if product.get("protein_g", 0) > nutrition.get("protein_g", 0):
                    score += 20
                    diff = product.get("protein_g", 0) - nutrition.get("protein_g", 0)
                    improvements.append(f"+{diff:.1f}g protein")
            
            if request.criteria in ["sugar", "all"]:
                if product.get("sugar_g", 999) < nutrition.get("sugar_g", 999):
                    score += 25
                    diff = nutrition.get("sugar_g", 0) - product.get("sugar_g", 0)
                    improvements.append(f"-{diff:.1f}g sugar")
            
            if request.criteria in ["fat", "all"]:
                if product.get("saturated_fat_g", 999) < nutrition.get("saturated_fat_g", 999):
                    score += 20
                    improvements.append("Lower saturated fat")
            
            if request.criteria in ["fiber", "all"]:
                if product.get("fiber_g", 0) > nutrition.get("fiber_g", 0):
                    score += 15
                    diff = product.get("fiber_g", 0) - nutrition.get("fiber_g", 0)
                    improvements.append(f"+{diff:.1f}g fiber")
            
            # Lower calories is generally better
            if product.get("calories", 999) < nutrition.get("calories", 999):
                score += 20
                diff = nutrition.get("calories", 0) - product.get("calories", 0)
                improvements.append(f"-{int(diff)} calories")
            
            if score > 0:
                alternatives.append({
                    "name": product.get("name"),
                    "brand": product.get("brand"),
                    "barcode": product.get("barcode"),
                    "score": score,
                    "improvements": improvements,
                    "nutrition": {
                        "calories": product.get("calories"),
                        "protein_g": product.get("protein_g"),
                        "carbs_g": product.get("carbs_g"),
                        "fat_g": product.get("fat_g"),
                        "sugar_g": product.get("sugar_g"),
                        "fiber_g": product.get("fiber_g")
                    }
                })
        
        # Sort by score
        alternatives.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"✅ Found {len(alternatives)} better alternatives")
        
        return {
            "original_product": product_name,
            "criteria": request.criteria,
            "count": len(alternatives),
            "alternatives": alternatives[:5]  # Top 5
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Alternatives error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find alternatives: {str(e)}"
        )


@app.get("/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Get user health profile."""
    try:
        profile = personalization_agent.get_user_profile(user_id)
        
        return {
            "user_id": user_id,
            "profile": profile
        }
        
    except Exception as e:
        logger.error(f"Error retrieving profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve profile: {str(e)}"
        )


@app.post("/user/{user_id}/profile")
async def update_user_profile(user_id: str, profile: UserProfileRequest):
    """Update user health profile."""
    try:
        profile_data = {
            "age": profile.age,
            "gender": profile.gender,
            "height_cm": profile.height_cm,
            "weight_kg": profile.weight_kg,
            "activity_level": profile.activity_level,
            "health_goal": profile.health_goal,
            "allergies": profile.allergies,
            "health_conditions": profile.health_conditions,
            "dietary_restrictions": profile.dietary_restrictions,
            # Calculate targets (simplified)
            "daily_calorie_target": 2000,  # Default, should calculate based on profile
            "daily_protein_target_g": 50,
            "daily_carbs_target_g": 250,
            "daily_fat_target_g": 65
        }
        
        success = personalization_agent.save_user_profile(user_id, profile_data)
        
        if success:
            return {
                "message": "Profile updated successfully",
                "user_id": user_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@app.post("/batch-analysis")
async def batch_analysis(barcodes: List[str], user_id: str):
    """Analyze multiple barcodes in batch."""
    try:
        logger.info(f"Batch analysis for {len(barcodes)} barcodes")
        
        results = []
        for barcode in barcodes[:10]:  # Limit to 10 per batch
            try:
                food_data = data_agent.fetch_food_data(barcode)
                if food_data:
                    user_profile = personalization_agent.get_user_profile(user_id)
                    evaluation = personalization_agent.evaluate_food_safety(food_data, user_profile)
                    
                    results.append({
                        "barcode": barcode,
                        "food_name": food_data.get("name"),
                        "verdict": evaluation["verdict"],
                        "health_score": evaluation["health_score"]
                    })
            except Exception as e:
                logger.warning(f"Error processing barcode {barcode}: {e}")
                continue
        
        return {
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}"
        )


class NutritionTextRequest(BaseModel):
    """Request model for text-based nutrition extraction."""
    query: str = Field(..., description="Natural language food description (e.g., '1 cup rice', '2 eggs and toast')")
    user_id: str = Field(..., description="User identifier")


@app.post("/analyze-text")
async def analyze_nutrition_text(request: NutritionTextRequest):
    """
    Extract nutrition information from natural language text using API Ninjas.
    
    This endpoint uses AI to extract nutrition from:
    - Recipes (e.g., "2 cups flour, 3 eggs, 1 tbsp butter")
    - Menu items (e.g., "grilled chicken sandwich with fries")
    - Food descriptions (e.g., "1lb brisket and mashed potatoes")
    
    Automatically handles custom portions and multiple items.
    """
    try:
        logger.info(f"📝 Analyzing nutrition text: {request.query}")
        
        # Use API Ninjas to extract nutrition from text
        nutrition_items = data_agent.fetch_from_api_ninjas_text(request.query)
        
        if not nutrition_items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not extract nutrition information from: {request.query}"
            )
        
        # Analyze each item
        user_profile = personalization_agent.get_user_profile(request.user_id)
        analyzed_items = []
        
        for item in nutrition_items:
            # Calculate health score
            evaluation = personalization_agent.evaluate_food_safety(item, user_profile)
            
            analyzed_items.append({
                "name": item.get("name"),
                "serving_size": f"{item.get('serving_size', 100)}{item.get('serving_unit', 'g')}",
                "nutrition": {
                    "calories": item.get("calories"),
                    "protein_g": item.get("protein_g"),
                    "carbs_g": item.get("carbs_g"),
                    "fat_g": item.get("fat_g"),
                    "saturated_fat_g": item.get("saturated_fat_g"),
                    "sugar_g": item.get("sugar_g"),
                    "fiber_g": item.get("fiber_g"),
                    "sodium_mg": item.get("sodium_mg"),
                    "potassium_mg": item.get("potassium_mg"),
                    "cholesterol_mg": item.get("cholesterol_mg")
                },
                "health_score": evaluation.get("health_score"),
                "verdict": evaluation.get("verdict"),
                "alerts": evaluation.get("alerts", []),
                "warnings": evaluation.get("warnings", [])
            })
        
        # Calculate total nutrition
        total_nutrition = {
            "calories": sum(item.get("calories", 0) for item in nutrition_items),
            "protein_g": sum(item.get("protein_g", 0) for item in nutrition_items),
            "carbs_g": sum(item.get("carbs_g", 0) for item in nutrition_items),
            "fat_g": sum(item.get("fat_g", 0) for item in nutrition_items),
            "sugar_g": sum(item.get("sugar_g", 0) for item in nutrition_items),
            "fiber_g": sum(item.get("fiber_g", 0) for item in nutrition_items),
            "sodium_mg": sum(item.get("sodium_mg", 0) for item in nutrition_items)
        }
        
        logger.info(f"✅ Extracted nutrition for {len(analyzed_items)} items")
        
        return {
            "query": request.query,
            "item_count": len(analyzed_items),
            "items": analyzed_items,
            "total_nutrition": total_nutrition,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze text: {str(e)}"
        )


class NutritionItemRequest(BaseModel):
    """Request model for single food item nutrition."""
    food_item: str = Field(..., description="Food item name (e.g., 'rice', 'chicken')")
    quantity: str = Field(..., description="Quantity with unit (e.g., '1 cup', '100g', '2 tbsp')")
    user_id: str = Field(..., description="User identifier")


@app.post("/analyze-item")
async def analyze_nutrition_item(request: NutritionItemRequest):
    """
    Get nutrition for a single food item with specific quantity.
    
    Supports various units:
    - Volume: cup, tbsp, tsp, ml, l
    - Weight: g, kg, oz, lb
    - Count: piece, slice, serving
    """
    try:
        logger.info(f"🍽️ Analyzing: {request.quantity} {request.food_item}")
        
        # Use API Ninjas to get nutrition for specific item and quantity
        nutrition_data = data_agent.fetch_from_api_ninjas_item(request.food_item, request.quantity)
        
        if not nutrition_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find nutrition for: {request.quantity} {request.food_item}"
            )
        
        # Analyze health
        user_profile = personalization_agent.get_user_profile(request.user_id)
        evaluation = personalization_agent.evaluate_food_safety(nutrition_data, user_profile)
        
        logger.info(f"✅ Nutrition found for {request.quantity} {request.food_item}")
        
        return {
            "food_item": request.food_item,
            "quantity": request.quantity,
            "serving_size": f"{nutrition_data.get('serving_size', 100)}g",
            "nutrition": {
                "calories": nutrition_data.get("calories"),
                "protein_g": nutrition_data.get("protein_g"),
                "carbs_g": nutrition_data.get("carbs_g"),
                "fat_g": nutrition_data.get("fat_g"),
                "saturated_fat_g": nutrition_data.get("saturated_fat_g"),
                "sugar_g": nutrition_data.get("sugar_g"),
                "fiber_g": nutrition_data.get("fiber_g"),
                "sodium_mg": nutrition_data.get("sodium_mg"),
                "potassium_mg": nutrition_data.get("potassium_mg"),
                "cholesterol_mg": nutrition_data.get("cholesterol_mg")
            },
            "health_score": evaluation.get("health_score"),
            "verdict": evaluation.get("verdict"),
            "risk_level": evaluation.get("risk_level"),
            "alerts": evaluation.get("alerts", []),
            "warnings": evaluation.get("warnings", []),
            "suggestions": evaluation.get("suggestions", []),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Item analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze item: {str(e)}"
        )


# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("=" * 50)
    logger.info("EatSmartly Backend Starting...")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    logger.info(f"Redis: {settings.REDIS_URL}")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("EatSmartly Backend Shutting Down...")


# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
