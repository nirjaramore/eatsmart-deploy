"""
Web Scraping Agent for EatSmartly.
Enriches food data with recipes and healthier alternatives from web sources.
"""
import time
from typing import Dict, Any, Optional, List
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import re

from config import settings
from agents.utils import setup_logger


logger = setup_logger(__name__, settings.LOG_LEVEL)


class WebScrapingAgent:
    """Agent responsible for web scraping recipes and alternatives."""
    
    def __init__(self):
        """Initialize the web scraping agent."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        logger.info("WebScrapingAgent initialized")
    
    def scrape_recipes(self, food_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Scrape recipes for a given food from AllRecipes.
        
        Args:
            food_name: Name of the food
            limit: Maximum number of recipes to return
            
        Returns:
            List of recipe dictionaries
        """
        logger.info(f"Scraping recipes for: {food_name}")
        
        recipes = []
        
        try:
            # Try AllRecipes with timeout
            allrecipes = self._scrape_allrecipes(food_name, limit)
            recipes.extend(allrecipes)
            
            # If we need more, try BBC Good Food
            if len(recipes) < limit:
                bbc_recipes = self._scrape_bbc_good_food(food_name, limit - len(recipes))
                recipes.extend(bbc_recipes)
        except Exception as e:
            logger.warning(f"Recipe scraping failed: {e}")
            # Return mock recipes as fallback
            recipes = self._get_mock_recipes(food_name, limit)
        
        return recipes[:limit] if recipes else self._get_mock_recipes(food_name, limit)
    
    def _scrape_allrecipes(self, food_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Scrape recipes from AllRecipes.com."""
        recipes = []
        
        try:
            search_query = quote_plus(food_name)
            search_url = f"https://www.allrecipes.com/search?q={search_query}"
            
            response = self.session.get(search_url, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find recipe cards (structure may vary)
            recipe_cards = soup.find_all('a', class_=re.compile('card__title'), limit=limit * 2)
            
            for card in recipe_cards[:limit]:
                try:
                    recipe_url = card.get('href', '')
                    recipe_title = card.get_text(strip=True)
                    
                    if recipe_url and recipe_title:
                        # Get recipe details
                        recipe_details = self._get_allrecipes_details(recipe_url)
                        
                        if recipe_details:
                            recipe_details['title'] = recipe_title
                            recipe_details['url'] = recipe_url
                            recipe_details['source'] = 'AllRecipes'
                            recipes.append(recipe_details)
                        
                        time.sleep(0.5)  # Be respectful
                        
                except Exception as e:
                    logger.warning(f"Error parsing AllRecipes card: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"AllRecipes scraping error: {e}")
        
        return recipes
    
    def _get_allrecipes_details(self, url: str) -> Optional[Dict[str, Any]]:
        """Get detailed recipe information from AllRecipes."""
        try:
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {}
            
            # Prep time
            prep_time = soup.find('span', class_=re.compile('recipe-meta.*prep'))
            if prep_time:
                details['prep_time'] = prep_time.get_text(strip=True)
            
            # Cook time
            cook_time = soup.find('span', class_=re.compile('recipe-meta.*cook'))
            if cook_time:
                details['cook_time'] = cook_time.get_text(strip=True)
            
            # Servings
            servings = soup.find('div', class_=re.compile('recipe-meta.*servings'))
            if servings:
                details['servings'] = servings.get_text(strip=True)
            
            # Ingredients
            ingredients = []
            ingredient_list = soup.find_all('li', class_=re.compile('ingredient'))
            for ing in ingredient_list:
                ing_text = ing.get_text(strip=True)
                if ing_text:
                    ingredients.append(ing_text)
            details['ingredients'] = ingredients
            
            # Instructions (simplified)
            instructions = []
            instruction_list = soup.find_all('li', class_=re.compile('instruction'))
            for inst in instruction_list[:5]:  # First 5 steps
                inst_text = inst.get_text(strip=True)
                if inst_text:
                    instructions.append(inst_text)
            details['instructions'] = instructions
            
            return details if ingredients else None
            
        except Exception as e:
            logger.warning(f"Error getting AllRecipes details: {e}")
            return None
    
    def _scrape_bbc_good_food(self, food_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Scrape recipes from BBC Good Food."""
        recipes = []
        
        try:
            search_query = quote_plus(food_name)
            search_url = f"https://www.bbcgoodfood.com/search?q={search_query}"
            
            response = self.session.get(search_url, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find recipe links
            recipe_links = soup.find_all('a', class_=re.compile('link d-block'), limit=limit)
            
            for link in recipe_links:
                try:
                    recipe_url = link.get('href', '')
                    if recipe_url and not recipe_url.startswith('http'):
                        recipe_url = urljoin('https://www.bbcgoodfood.com', recipe_url)
                    
                    recipe_title = link.get_text(strip=True)
                    
                    if recipe_url and recipe_title:
                        recipes.append({
                            'title': recipe_title,
                            'url': recipe_url,
                            'source': 'BBC Good Food'
                        })
                        
                        time.sleep(0.5)  # Be respectful
                        
                except Exception as e:
                    logger.warning(f"Error parsing BBC recipe: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"BBC Good Food scraping error: {e}")
        
        return recipes
    
    def find_alternatives(
        self, 
        food_name: str, 
        health_goal: str = "general", 
        limit: int = 5
    ) -> List[Dict[str, str]]:
        """
        Find healthier alternative foods.
        
        Args:
            food_name: Current food name
            health_goal: User's health goal (weight_loss, muscle_gain, general)
            limit: Maximum alternatives
            
        Returns:
            List of alternative food suggestions
        """
        logger.info(f"Finding alternatives for: {food_name} (goal: {health_goal})")
        
        # Predefined alternatives database (expandable)
        alternatives_db = {
            # Snacks
            "chips": [
                {"name": "Air-popped popcorn", "reason": "90% fewer calories, high fiber"},
                {"name": "Baked vegetable chips", "reason": "Less fat, more nutrients"},
                {"name": "Roasted chickpeas", "reason": "High protein, filling"},
                {"name": "Rice cakes with hummus", "reason": "Low calorie, protein-rich"},
                {"name": "Carrot sticks with guacamole", "reason": "Vitamins, healthy fats"}
            ],
            "soda": [
                {"name": "Sparkling water with lemon", "reason": "Zero calories, refreshing"},
                {"name": "Green tea", "reason": "Antioxidants, metabolism boost"},
                {"name": "Coconut water", "reason": "Natural electrolytes"},
                {"name": "Infused water", "reason": "Zero calories, hydrating"},
                {"name": "Kombucha", "reason": "Probiotics, low sugar"}
            ],
            "ice cream": [
                {"name": "Greek yogurt with berries", "reason": "High protein, probiotics"},
                {"name": "Frozen banana bites", "reason": "Natural sweetness, potassium"},
                {"name": "Sorbet", "reason": "Lower fat, fruit-based"},
                {"name": "Protein ice cream", "reason": "High protein, low calorie"},
                {"name": "Chia seed pudding", "reason": "Fiber, omega-3"}
            ],
            "white bread": [
                {"name": "Whole wheat bread", "reason": "More fiber, nutrients"},
                {"name": "Sourdough bread", "reason": "Easier digestion, probiotics"},
                {"name": "Ezekiel bread", "reason": "Sprouted grains, protein"},
                {"name": "Oat bread", "reason": "Heart-healthy, filling"},
                {"name": "Lettuce wraps", "reason": "Ultra low carb, fresh"}
            ],
            "pasta": [
                {"name": "Whole wheat pasta", "reason": "Higher fiber, nutrients"},
                {"name": "Zucchini noodles", "reason": "Very low calorie, vitamins"},
                {"name": "Chickpea pasta", "reason": "High protein, gluten-free"},
                {"name": "Quinoa", "reason": "Complete protein, minerals"},
                {"name": "Shirataki noodles", "reason": "Zero calorie, filling"}
            ],
            "candy": [
                {"name": "Dark chocolate (70%+)", "reason": "Antioxidants, less sugar"},
                {"name": "Fresh berries", "reason": "Natural sweetness, vitamins"},
                {"name": "Dates", "reason": "Natural sugar, fiber"},
                {"name": "Fruit leather (no sugar)", "reason": "Real fruit, portable"},
                {"name": "Frozen grapes", "reason": "Low calorie, refreshing"}
            ]
        }
        
        # Normalize food name for matching
        food_lower = food_name.lower()
        
        # Find matching alternatives
        alternatives = []
        for key, alts in alternatives_db.items():
            if key in food_lower or food_lower in key:
                alternatives.extend(alts[:limit])
                break
        
        # If no specific match, provide general healthy swaps
        if not alternatives:
            alternatives = self._get_general_alternatives(food_name, health_goal, limit)
        
        return alternatives[:limit]
    
    def _get_general_alternatives(
        self, 
        food_name: str, 
        health_goal: str, 
        limit: int
    ) -> List[Dict[str, str]]:
        """Provide general healthy alternatives based on food type."""
        
        # Basic categorization and suggestions
        if any(term in food_name.lower() for term in ["cookie", "cake", "donut", "pastry"]):
            return [
                {"name": "Oatmeal cookies", "reason": "Whole grains, less sugar"},
                {"name": "Fruit salad", "reason": "Natural sweetness, vitamins"},
                {"name": "Homemade energy balls", "reason": "Nuts, dates, controlled ingredients"}
            ]
        
        if any(term in food_name.lower() for term in ["fried", "fries"]):
            return [
                {"name": "Baked version", "reason": "90% less fat"},
                {"name": "Sweet potato fries (baked)", "reason": "More nutrients, fiber"},
                {"name": "Roasted vegetables", "reason": "Low calorie, vitamins"}
            ]
        
        if any(term in food_name.lower() for term in ["burger", "sandwich"]):
            return [
                {"name": "Grilled chicken sandwich", "reason": "Lean protein"},
                {"name": "Veggie burger", "reason": "Plant-based, fiber"},
                {"name": "Lettuce wrap burger", "reason": "Low carb, fresh"}
            ]
        
        # Default suggestions
        return [
            {"name": "Fresh fruits", "reason": "Natural, nutrient-rich"},
            {"name": "Vegetables with hummus", "reason": "Fiber, protein"},
            {"name": "Greek yogurt", "reason": "High protein, probiotics"}
        ][:limit]
    
    def get_nutrition_tips(self, food_data: Dict[str, Any]) -> List[str]:
        """
        Generate nutrition tips based on food data.
        
        Args:
            food_data: Standardized food data
            
        Returns:
            List of nutrition tips
        """
        tips = []
        
        sugar = food_data.get("sugar_g", 0) or 0
        sodium = food_data.get("sodium_mg", 0) or 0
        fiber = food_data.get("fiber_g", 0) or 0
        protein = food_data.get("protein_g", 0) or 0
        
        # Sugar tips
        if sugar > 10:
            tips.append(f"⚠️ High sugar content ({sugar:.1f}g). Limit to special occasions.")
        elif sugar > 5:
            tips.append(f"Moderate sugar ({sugar:.1f}g). Balance with protein and fiber.")
        
        # Sodium tips
        if sodium > 500:
            tips.append(f"⚠️ High sodium ({sodium:.0f}mg). Drink plenty of water.")
        elif sodium > 300:
            tips.append(f"Moderate sodium ({sodium:.0f}mg). Watch daily intake.")
        
        # Fiber tips
        if fiber < 2:
            tips.append("💡 Low fiber. Pair with vegetables or whole grains.")
        elif fiber >= 5:
            tips.append(f"✅ Good fiber content ({fiber:.1f}g). Supports digestion.")
        
        # Protein tips
        if protein < 3:
            tips.append("💡 Low protein. Add lean meat, eggs, or legumes to your meal.")
        elif protein >= 10:
            tips.append(f"✅ Good protein ({protein:.1f}g). Supports muscle health.")
        
        return tips
    
    def _get_mock_recipes(self, food_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Return mock recipes when scraping fails."""
        return [
            {
                "title": f"Healthy {food_name} Recipe",
                "url": "https://www.allrecipes.com",
                "source": "Suggested",
                "prep_time": "15 min",
                "cook_time": "30 min",
                "servings": "4 servings"
            },
            {
                "title": f"Quick {food_name} Meal",
                "url": "https://www.bbcgoodfood.com",
                "source": "Suggested",
                "prep_time": "10 min",
                "cook_time": "20 min",
                "servings": "2 servings"
            }
        ][:limit]
