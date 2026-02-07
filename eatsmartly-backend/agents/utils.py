"""
Utility functions for EatSmartly agents.
Handles barcode normalization, data parsing, and logging.
"""
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up logger with consistent formatting.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def normalize_barcode(barcode: str) -> Optional[str]:
    """
    Normalize and validate barcode (UPC-A, EAN-13, EAN-8).
    
    Args:
        barcode: Raw barcode string
        
    Returns:
        Normalized barcode or None if invalid
    """
    if not barcode:
        return None
    
    # Remove any non-digit characters
    clean_barcode = re.sub(r'\D', '', barcode)
    
    # Valid lengths: UPC-A (12), EAN-13 (13), EAN-8 (8)
    valid_lengths = [8, 12, 13]
    
    if len(clean_barcode) not in valid_lengths:
        return None
    
    # Pad UPC-A to EAN-13 format
    if len(clean_barcode) == 12:
        clean_barcode = '0' + clean_barcode
    
    return clean_barcode


def validate_upc_checksum(barcode: str) -> bool:
    """
    Validate UPC/EAN checksum digit.
    
    Args:
        barcode: Normalized barcode
        
    Returns:
        True if checksum is valid
    """
    if not barcode or len(barcode) not in [8, 13]:
        return False
    
    digits = [int(d) for d in barcode]
    check_digit = digits[-1]
    
    # Calculate checksum
    odd_sum = sum(digits[-2::-2])
    even_sum = sum(digits[-3::-2])
    
    if len(barcode) == 13:
        calculated = (10 - ((odd_sum + even_sum * 3) % 10)) % 10
    else:  # EAN-8
        calculated = (10 - ((odd_sum * 3 + even_sum) % 10)) % 10
    
    return check_digit == calculated


def parse_nutrition(api_response: Dict[str, Any], source: str = "usda") -> Dict[str, Any]:
    """
    Parse nutrition data from various API sources into standardized format.
    
    Args:
        api_response: Raw API response
        source: Data source (usda, nutritionix, etc.)
        
    Returns:
        Standardized nutrition dictionary
    """
    nutrition = {
        "name": None,
        "brand": None,
        "serving_size": None,
        "serving_unit": None,
        "calories": None,
        "protein_g": None,
        "carbs_g": None,
        "fat_g": None,
        "saturated_fat_g": None,
        "sodium_mg": None,
        "sugar_g": None,
        "fiber_g": None,
        "allergens": [],
        "ingredients": None,
        "source": source,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    if source == "usda":
        nutrition.update(_parse_usda_nutrition(api_response))
    elif source == "nutritionix":
        nutrition.update(_parse_nutritionix_nutrition(api_response))
    
    return nutrition


def _parse_usda_nutrition(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse USDA FoodData Central response."""
    result = {}
    
    if not data:
        return result
    
    result["name"] = data.get("description", "").strip()
    result["brand"] = data.get("brandOwner", "").strip()
    
    # Parse serving size
    serving_size = data.get("servingSize")
    serving_unit = data.get("servingSizeUnit", "g")
    result["serving_size"] = serving_size
    result["serving_unit"] = serving_unit
    
    # Parse nutrients
    nutrients = data.get("foodNutrients", [])
    nutrient_map = {
        "Energy": "calories",
        "Protein": "protein_g",
        "Carbohydrate, by difference": "carbs_g",
        "Total lipid (fat)": "fat_g",
        "Fatty acids, total saturated": "saturated_fat_g",
        "Sodium, Na": "sodium_mg",
        "Sugars, total including NLEA": "sugar_g",
        "Fiber, total dietary": "fiber_g"
    }
    
    for nutrient in nutrients:
        nutrient_name = nutrient.get("nutrientName", "")
        nutrient_value = nutrient.get("value")
        
        for usda_name, field_name in nutrient_map.items():
            if usda_name in nutrient_name and nutrient_value is not None:
                result[field_name] = float(nutrient_value)
                break
    
    # Parse ingredients
    result["ingredients"] = data.get("ingredients", "").strip()
    
    return result


def _parse_nutritionix_nutrition(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Nutritionix API response."""
    result = {}
    
    if not data or "foods" not in data or not data["foods"]:
        return result
    
    food = data["foods"][0]
    
    result["name"] = food.get("food_name", "").strip()
    result["brand"] = food.get("brand_name", "").strip()
    result["serving_size"] = food.get("serving_qty")
    result["serving_unit"] = food.get("serving_unit", "g")
    result["calories"] = food.get("nf_calories")
    result["protein_g"] = food.get("nf_protein")
    result["carbs_g"] = food.get("nf_total_carbohydrate")
    result["fat_g"] = food.get("nf_total_fat")
    result["saturated_fat_g"] = food.get("nf_saturated_fat")
    result["sodium_mg"] = food.get("nf_sodium")
    result["sugar_g"] = food.get("nf_sugars")
    result["fiber_g"] = food.get("nf_dietary_fiber")
    
    return result


def extract_allergens(ingredients: str) -> List[str]:
    """
    Extract common allergens from ingredient list.
    
    Args:
        ingredients: Ingredient string
        
    Returns:
        List of detected allergens
    """
    if not ingredients:
        return []
    
    ingredients_lower = ingredients.lower()
    allergens = []
    
    allergen_keywords = {
        "milk": ["milk", "dairy", "lactose", "whey", "casein", "butter", "cream", "cheese"],
        "eggs": ["egg", "albumin", "lysozyme", "mayonnaise"],
        "peanuts": ["peanut", "groundnut"],
        "tree_nuts": ["almond", "cashew", "walnut", "pecan", "pistachio", "hazelnut", "macadamia"],
        "soy": ["soy", "soya", "tofu", "edamame", "tempeh"],
        "wheat": ["wheat", "flour", "gluten", "semolina", "durum"],
        "fish": ["fish", "anchovy", "bass", "catfish", "cod", "flounder", "halibut", "salmon", "tuna"],
        "shellfish": ["shrimp", "crab", "lobster", "clam", "oyster", "mussel", "scallop"]
    }
    
    for allergen, keywords in allergen_keywords.items():
        if any(keyword in ingredients_lower for keyword in keywords):
            allergens.append(allergen)
    
    return list(set(allergens))


def calculate_health_score(nutrition: Dict[str, Any], product_name: str = "", brand: str = "") -> float:
    """
    Calculate health score (0-100) based on evidence-based nutritional guidelines.
    Uses the Nutrient Profiling Model similar to traffic light labeling systems.
    
    Scoring Logic (per 100g):
    - Start at 100 (perfect score)
    - Deduct points for unhealthy components (sugar, sodium, saturated fat, calories)
    - Add back points for healthy components (protein, fiber)
    - Severe penalties for ultra-processed foods like instant noodles
    - Final score determines verdict: >70=safe, 40-70=caution, <40=avoid
    
    Args:
        nutrition: Standardized nutrition dictionary
        product_name: Product name for detecting ultra-processed foods
        brand: Brand name for detecting ultra-processed foods
        
    Returns:
        Health score (0-100)
    """
    score = 100.0  # Start with perfect score
    
    # Detect instant noodles and similar ultra-processed foods
    product_lower = product_name.lower() if product_name else ""
    brand_lower = brand.lower() if brand else ""
    
    instant_noodle_indicators = [
        "maggi", "noodles", "instant noodles", "ramen", "2 minute", "top ramen",
        "yippee", "wai wai", "sunfeast yippee", "knorr instant", "nissin", "indomie",
        "instant pasta", "cup noodles"
    ]
    
    is_instant_noodles = any(
        indicator in product_lower or indicator in brand_lower 
        for indicator in instant_noodle_indicators
    )
    
    # Extract nutritional values (assume per 100g serving)
    calories = nutrition.get("calories", 0) or 0
    protein = nutrition.get("protein_g", 0) or 0
    fiber = nutrition.get("fiber_g", 0) or 0
    sugar = nutrition.get("sugar_g", 0) or 0
    sodium = nutrition.get("sodium_mg", 0) or 0
    saturated_fat = nutrition.get("saturated_fat_g", 0) or 0
    total_fat = nutrition.get("fat_g", 0) or 0
    
    # === NEGATIVE POINTS (Unhealthy Components) ===
    
    # 1. SUGAR PENALTY (Max -35 points)
    # WHO recommends <10% daily calories from sugar (~50g/day)
    # Per 100g: <5g=low, 5-10g=medium, 10-15g=high, >15g=very high
    if sugar > 25:
        score -= 35  # Extremely high sugar (candy, soda)
    elif sugar > 20:
        score -= 32  # Very high sugar
    elif sugar > 15:
        score -= 28  # High sugar
    elif sugar > 10:
        score -= 20  # Moderate-high sugar (soft drinks per 100ml!)
    elif sugar > 5:
        score -= 10  # Some sugar
    elif sugar > 2:
        score -= 5   # Low sugar
    
    # 2. SODIUM PENALTY (Max -25 points)
    # WHO recommends <2000mg/day
    # Per 100g: <120mg=low, 120-600mg=medium, >600mg=high
    if sodium > 1000:
        score -= 25  # Very high sodium
    elif sodium > 600:
        score -= 20  # High sodium
    elif sodium > 400:
        score -= 12  # Moderate sodium
    elif sodium > 120:
        score -= 6   # Some sodium
    
    # 3. SATURATED FAT PENALTY (Max -20 points)
    # WHO recommends <10% daily calories (~20g/day for 2000 cal diet)
    # Per 100g: <1.5g=low, 1.5-5g=medium, >5g=high
    if saturated_fat > 10:
        score -= 20  # Very high saturated fat
    elif saturated_fat > 5:
        score -= 15  # High saturated fat
    elif saturated_fat > 3:
        score -= 8   # Moderate saturated fat
    elif saturated_fat > 1.5:
        score -= 4   # Some saturated fat
    
    # 4. TOTAL FAT PENALTY (Max -10 points)
    # High fat foods are calorie-dense
    if total_fat > 40:
        score -= 10  # Very high fat (like butter, oil)
    elif total_fat > 20:
        score -= 5   # High fat
    elif total_fat > 10:
        score -= 2   # Moderate fat
    
    # 5. CALORIE PENALTY (Max -15 points)
    # Energy density matters for weight management
    # Per 100g: <100=low, 100-300=medium, >300=high
    if calories > 500:
        score -= 15  # Very calorie-dense
    elif calories > 400:
        score -= 12  # High calories
    elif calories > 300:
        score -= 8   # Moderately high
    elif calories > 200:
        score -= 4   # Moderate calories
    
    # === POSITIVE POINTS (Healthy Components) ===
    
    # 1. PROTEIN BONUS (Max +15 points)
    # Higher protein is beneficial for satiety and muscle health
    # Per 100g: >20g=excellent, 10-20g=good, 5-10g=moderate
    if protein > 20:
        score += 15  # Excellent protein (lean meats, legumes)
    elif protein > 15:
        score += 12  # Very good protein
    elif protein > 10:
        score += 8   # Good protein
    elif protein > 5:
        score += 4   # Moderate protein
    elif protein > 2:
        score += 2   # Some protein
    
    # 2. FIBER BONUS (Max +15 points)
    # Fiber aids digestion and satiety
    # Per 100g: >6g=high, 3-6g=good, <3g=low
    if fiber > 10:
        score += 15  # Excellent fiber (whole grains, legumes)
    elif fiber > 6:
        score += 12  # High fiber
    elif fiber > 4:
        score += 8   # Good fiber
    elif fiber > 2:
        score += 4   # Moderate fiber
    elif fiber > 1:
        score += 2   # Some fiber
    
    # === SPECIAL CASES ===
    
    # Bonus for nutrient-dense, low-calorie foods (vegetables, fruits with natural sugars)
    # Only apply if it's actually nutritious (has fiber or protein)
    # Exclude if high added sugar (fruits have fiber, soda doesn't)
    if calories < 100 and (fiber >= 2 or protein >= 2) and sugar < 12:
        score += 5  # Nutrient-dense bonus
    
    # === CRITICAL PENALTIES FOR ULTRA-PROCESSED FOODS ===
    
    # INSTANT NOODLES - Extremely harsh penalty (-70 points minimum)
    # Maggi, Top Ramen, etc. are ultra-processed with harmful additives
    if is_instant_noodles:
        score -= 70  # Massive penalty for instant noodles
        logger.info(f"🚨 INSTANT NOODLES DETECTED: {product_name or brand} - Applying -70 penalty")
        # Additional penalties for typical instant noodle characteristics
        if sodium > 800:
            score -= 10  # Extra penalty for excessive sodium
        if fiber < 2:
            score -= 5   # Extra penalty for no fiber
    
    # CRITICAL: Harsh penalty for sugary beverages
    # Soft drinks have: >8g sugar, <1g protein, <0.5g fiber, <1g fat
    # This catches: Coca-Cola, Pepsi, Sprite, energy drinks, sweetened juices
    is_sugary_drink = (sugar > 8 and protein < 1 and fiber < 0.5 and total_fat < 1)
    
    if is_sugary_drink:
        score -= 40  # Major penalty for sugary beverages (soda, sweetened drinks)
        logger.debug(f"Sugary beverage detected: sugar={sugar}g, protein={protein}g, fiber={fiber}g")
    
    # Ultra-processed foods (high calories + high sugar/sodium + low fiber/protein)
    if calories > 350 and sugar > 10 and sodium > 400 and fiber < 2 and protein < 5:
        score -= 10  # Ultra-processed penalty
    
    # Ensure score stays within 0-100 range
    final_score = max(0, min(100, score))
    
    return round(final_score, 1)


def format_serving_size(size: Optional[float], unit: Optional[str]) -> str:
    """
    Format serving size for display.
    
    Args:
        size: Serving size value
        unit: Serving unit
        
    Returns:
        Formatted string
    """
    if size is None:
        return "Unknown"
    
    unit = unit or "g"
    return f"{size:.1f} {unit}"


# Initialize default logger
logger = setup_logger(__name__)
