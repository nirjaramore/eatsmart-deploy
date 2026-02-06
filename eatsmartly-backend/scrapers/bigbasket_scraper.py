"""
BigBasket Product Scraper
BigBasket is India's largest online grocery store with excellent nutrition data
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def get_headers():
    """Get randomized headers for requests"""
    import random
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-IN,en;q=0.9,hi;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.bigbasket.com/'
    }

def search_bigbasket(product_name: str, max_results: int = 5) -> List[Dict]:
    """
    Search BigBasket for products
    BigBasket has a search API we can use!
    
    Args:
        product_name: Name of product to search for
        max_results: Maximum number of results to return (default 5)
        
    Returns:
        List of product dictionaries
    """
    try:
        logger.info(f"🔍 Searching BigBasket for: {product_name}")
        
        # BigBasket search endpoint
        search_url = "https://www.bigbasket.com/product/search/"
        
        params = {
            'q': product_name,
            'page': 1
        }
        
        response = requests.get(
            search_url,
            params=params,
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code != 200:
            logger.warning(f"BigBasket returned status code: {response.status_code}")
            return []
        
        # Parse HTML response
        soup = BeautifulSoup(response.content, 'lxml')
        products = []
        
        # Find product cards (BigBasket uses specific classes)
        product_cards = soup.find_all('div', class_=re.compile(r'product-card|SKUDeck'))
        logger.info(f"Found {len(product_cards)} product cards on BigBasket")
        
        for card in product_cards[:max_results]:
            try:
                # Extract product name
                title_elem = card.find('a', class_=re.compile(r'product.*title|text-decoration'))
                if not title_elem:
                    title_elem = card.find('h3')
                title = title_elem.get_text(strip=True) if title_elem else None
                
                if not title:
                    continue
                
                # Extract brand
                brand_elem = card.find('span', class_=re.compile(r'brand'))
                brand = brand_elem.get_text(strip=True) if brand_elem else None
                
                # Extract price
                price_elem = card.find('span', class_=re.compile(r'discounted.*price|Pricing.*sale'))
                price = None
                if price_elem:
                    price_text = price_elem.get_text(strip=True).replace('₹', '').replace(',', '').strip()
                    try:
                        price = float(price_text)
                    except ValueError:
                        pass
                
                # Extract rating
                rating_elem = card.find('div', class_=re.compile(r'rating'))
                rating = None
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    match = re.search(r'(\d+\.?\d*)', rating_text)
                    if match:
                        try:
                            rating = float(match.group(1))
                        except ValueError:
                            pass
                
                # Extract image
                img_elem = card.find('img')
                image_url = None
                if img_elem:
                    image_url = img_elem.get('src') or img_elem.get('data-src')
                
                # Extract product URL
                link_elem = card.find('a', href=True)
                product_url = None
                if link_elem:
                    href = link_elem['href']
                    if href.startswith('http'):
                        product_url = href
                    else:
                        product_url = f"https://www.bigbasket.com{href}"
                
                # Extract weight/size
                weight_elem = card.find('span', class_=re.compile(r'weight|size|pack'))
                weight = weight_elem.get_text(strip=True) if weight_elem else None
                
                products.append({
                    'source': 'BigBasket',
                    'product_name': title,
                    'brand': brand,
                    'price': price,
                    'rating': rating,
                    'image_url': image_url,
                    'product_url': product_url,
                    'weight': weight,
                    'confidence': 0.85  # BigBasket has good quality data
                })
                
                logger.info(f"✅ Found: {title[:50]}... (₹{price if price else 'N/A'})")
                
            except Exception as e:
                logger.error(f"Error parsing BigBasket product card: {e}")
                continue
        
        logger.info(f"✅ Returning {len(products)} products from BigBasket")
        return products
        
    except requests.exceptions.Timeout:
        logger.error("BigBasket request timed out")
        return []
    except Exception as e:
        logger.error(f"Error searching BigBasket: {e}")
        return []

def get_bigbasket_product_details(product_url: str) -> Optional[Dict]:
    """
    Get detailed product information from BigBasket product page
    BigBasket has EXCELLENT nutrition information!
    
    Args:
        product_url: Full URL to BigBasket product page
        
    Returns:
        Dictionary with detailed product info including nutrition
    """
    try:
        logger.info(f"📦 Getting BigBasket product details from: {product_url}")
        
        # Add rate limiting
        time.sleep(1)
        
        response = requests.get(
            product_url,
            headers=get_headers(),
            timeout=15
        )
        
        if response.status_code != 200:
            logger.warning(f"BigBasket returned status code: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract product name
        title_elem = soup.find('h1', class_=re.compile(r'product.*title|Description'))
        if not title_elem:
            title_elem = soup.find('h1')
        product_name = title_elem.get_text(strip=True) if title_elem else None
        
        # Extract brand
        brand_elem = soup.find('a', class_=re.compile(r'brand|uiv2'))
        if not brand_elem:
            brand_elem = soup.find('span', class_=re.compile(r'brand'))
        brand = brand_elem.get_text(strip=True) if brand_elem else None
        
        # Extract image
        img_elem = soup.find('img', class_=re.compile(r'product.*image'))
        if not img_elem:
            img_elem = soup.find('img', alt=re.compile(product_name or ''))
        image_url = None
        if img_elem:
            image_url = img_elem.get('src') or img_elem.get('data-src')
        
        # Extract price
        price_elem = soup.find('span', class_=re.compile(r'sale.*price|Pricing'))
        price = None
        if price_elem:
            price_text = price_elem.get_text(strip=True).replace('₹', '').replace(',', '').strip()
            try:
                price = float(price_text)
            except ValueError:
                pass
        
        # Extract rating
        rating_elem = soup.find('div', class_=re.compile(r'rating|stars'))
        rating = None
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            match = re.search(r'(\d+\.?\d*)', rating_text)
            if match:
                try:
                    rating = float(match.group(1))
                except ValueError:
                    pass
        
        # Extract description
        desc_elem = soup.find('div', class_=re.compile(r'description|ProductDescription'))
        description = None
        if desc_elem:
            desc_p = desc_elem.find('p')
            if desc_p:
                description = desc_p.get_text(strip=True)
            else:
                description = desc_elem.get_text(strip=True)
        
        # Extract features
        features = []
        feature_list = soup.find('ul', class_=re.compile(r'feature|key'))
        if feature_list:
            feature_items = feature_list.find_all('li')
            for item in feature_items:
                feature_text = item.get_text(strip=True)
                if feature_text and len(feature_text) > 10:
                    features.append(feature_text)
        
        # Extract nutrition (BigBasket is EXCELLENT for this!)
        nutrition = extract_nutrition_from_bigbasket(soup)
        
        product_details = {
            'source': 'BigBasket',
            'product_name': product_name,
            'brand': brand,
            'image_url': image_url,
            'price': price,
            'rating': rating,
            'description': description,
            'features': features,
            'nutrition': nutrition,
            'product_url': product_url
        }
        
        logger.info(f"✅ Extracted details for: {product_name}")
        if nutrition:
            logger.info(f"✅ Found nutrition info: {list(nutrition.keys())}")
        
        return product_details
        
    except requests.exceptions.Timeout:
        logger.error("BigBasket product page request timed out")
        return None
    except Exception as e:
        logger.error(f"Error getting BigBasket product details: {e}")
        return None

def extract_nutrition_from_bigbasket(soup: BeautifulSoup) -> Optional[Dict]:
    """
    Extract nutrition information from BigBasket product page
    BigBasket has well-structured nutrition tables!
    
    Args:
        soup: BeautifulSoup object of product page
        
    Returns:
        Dictionary with nutrition values or None
    """
    nutrition = {}
    
    try:
        # Look for nutrition section (BigBasket has dedicated sections)
        nutrition_sections = [
            soup.find('div', class_=re.compile(r'nutrition|Nutritional')),
            soup.find('section', class_=re.compile(r'nutrition')),
            soup.find('div', id=re.compile(r'nutrition', re.IGNORECASE))
        ]
        
        for section in nutrition_sections:
            if not section:
                continue
            
            # Look for nutrition table
            table = section.find('table')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value_text = cells[1].get_text(strip=True)
                        
                        # Extract numeric value
                        match = re.search(r'(\d+\.?\d*)', value_text)
                        if match:
                            try:
                                value = float(match.group(1))
                                
                                # Map to standard nutrition keys
                                if 'energy' in key or 'calor' in key:
                                    nutrition['calories'] = value
                                elif 'protein' in key:
                                    nutrition['protein'] = value
                                elif 'fat' in key and 'saturated' not in key:
                                    nutrition['totalFat'] = value
                                elif 'saturated' in key:
                                    nutrition['saturatedFat'] = value
                                elif 'carbohydrate' in key or 'carbs' in key:
                                    nutrition['carbs'] = value
                                elif 'sugar' in key:
                                    nutrition['sugars'] = value
                                elif 'fiber' in key or 'fibre' in key:
                                    nutrition['fiber'] = value
                                elif 'sodium' in key or 'salt' in key:
                                    nutrition['sodium'] = value
                                    
                            except ValueError:
                                continue
            
            # If found nutrition, break
            if nutrition:
                break
        
        # If no table found, look for text-based nutrition info
        if not nutrition:
            all_text = soup.get_text().lower()
            if 'nutrition' in all_text or 'energy' in all_text:
                # Try regex patterns for common nutrition formats
                patterns = {
                    'calories': r'energy[:\s]+(\d+\.?\d*)\s*(?:kcal|cal)',
                    'protein': r'protein[:\s]+(\d+\.?\d*)\s*g',
                    'totalFat': r'(?:total\s+)?fat[:\s]+(\d+\.?\d*)\s*g',
                    'carbs': r'carbohydrate[:\s]+(\d+\.?\d*)\s*g',
                    'sugars': r'sugar[:\s]+(\d+\.?\d*)\s*g',
                    'fiber': r'fib(?:er|re)[:\s]+(\d+\.?\d*)\s*g',
                    'sodium': r'sodium[:\s]+(\d+\.?\d*)\s*(?:mg|g)'
                }
                
                for key, pattern in patterns.items():
                    match = re.search(pattern, all_text, re.IGNORECASE)
                    if match:
                        try:
                            nutrition[key] = float(match.group(1))
                        except ValueError:
                            continue
        
        return nutrition if nutrition else None
        
    except Exception as e:
        logger.error(f"Error extracting nutrition from BigBasket: {e}")
        return None
