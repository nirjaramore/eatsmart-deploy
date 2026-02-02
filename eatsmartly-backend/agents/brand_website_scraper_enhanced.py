"""
Enhanced Brand Website Scraper with actual implementation
Scrapes nutrition data from official brand websites
"""
import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import Dict, Optional, List
import time

logger = logging.getLogger(__name__)

class BrandWebsiteScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Brand detection patterns
        self.barcode_prefixes = {
            '890': 'India', '891': 'India', '892': 'India', '893': 'India', '894': 'India',
            '76': 'Switzerland (Nestle)', '30': 'USA', '50': 'UK',
            '40': 'Germany', '41': 'Germany', '42': 'Germany', '43': 'Germany'
        }
        
        # Indian brand keywords and their URLs
        self.brand_search_urls = {
            'amul': 'https://www.amul.com',
            'britannia': 'https://www.britannia.co.in',
            'parle': 'https://www.parleproducts.com',
            'nestle': 'https://www.nestle.in',
            'maggi': 'https://www.maggi.in',
            'kitkat': 'https://www.kitkat.in',
            'haldiram': 'https://www.haldirams.com',
            'itc': 'https://www.itcportal.com',
            'sunfeast': 'https://www.sunfeast.in',
            'aashirvaad': 'https://www.aashirvaad.com'
        }
    
    def scrape_nutrition_from_website(self, product_name: str, barcode: str) -> Optional[Dict]:
        """
        Main method to scrape nutrition data from brand website
        """
        logger.info(f"🌐 STEP 1.5: Attempting website scrape for {product_name} ({barcode})")
        
        # Identify brand
        brand = self._extract_brand_from_name(product_name)
        if not brand:
            brand_prefix = self._identify_brand_from_barcode(barcode)
            logger.info(f"   📍 Barcode prefix suggests: {brand_prefix}")
        else:
            logger.info(f"   🏷️  Detected brand: {brand}")
        
        if not brand:
            logger.info("   ❌ Could not identify brand for website scraping")
            return None
        
        # Get brand website
        brand_lower = brand.lower()
        website_url = self.brand_search_urls.get(brand_lower)
        
        if not website_url:
            logger.info(f"   ⚠️  No scraping template for brand: {brand}")
            return None
        
        # Try to scrape
        try:
            nutrition_data = self._scrape_brand_site(website_url, product_name, barcode, brand_lower)
            
            if nutrition_data:
                logger.info(f"   ✅ Successfully scraped from {website_url}")
                logger.info(f"   📊 Found: {nutrition_data.get('calories', 'N/A')} kcal")
                return nutrition_data
            else:
                logger.info(f"   ❌ No nutrition data found on {website_url}")
                return None
                
        except Exception as e:
            logger.error(f"   ❌ Error scraping {website_url}: {str(e)}")
            return None
    
    def _scrape_brand_site(self, base_url: str, product_name: str, barcode: str, brand: str) -> Optional[Dict]:
        """
        Scrape specific brand website
        """
        try:
            # Try product search page
            search_url = f"{base_url}/products"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"   ⚠️  Website returned status {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Brand-specific scraping logic
            if brand == 'amul':
                return self._scrape_amul(soup, product_name)
            elif brand == 'britannia':
                return self._scrape_britannia(soup, product_name)
            elif brand == 'nestle':
                return self._scrape_nestle(soup, product_name)
            elif brand == 'parle':
                return self._scrape_parle(soup, product_name)
            else:
                return self._generic_scrape(soup, product_name)
                
        except requests.exceptions.Timeout:
            logger.warning(f"   ⏱️  Timeout scraping {base_url}")
            return None
        except Exception as e:
            logger.error(f"   ❌ Scraping error: {str(e)}")
            return None
    
    def _scrape_amul(self, soup: BeautifulSoup, product_name: str) -> Optional[Dict]:
        """Scrape Amul website"""
        # Look for nutrition table
        nutrition_data = {}
        
        # Find nutrition facts table
        tables = soup.find_all('table', class_=re.compile('nutrition|facts', re.I))
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    # Extract numeric value
                    numeric_value = self._extract_number(value)
                    
                    if 'energy' in label or 'calorie' in label:
                        nutrition_data['calories'] = numeric_value
                    elif 'protein' in label:
                        nutrition_data['protein_g'] = numeric_value
                    elif 'carbohydrate' in label or 'carbs' in label:
                        nutrition_data['carbs_g'] = numeric_value
                    elif 'fat' in label and 'saturated' not in label:
                        nutrition_data['fat_g'] = numeric_value
                    elif 'sugar' in label:
                        nutrition_data['sugar_g'] = numeric_value
                    elif 'fiber' in label or 'fibre' in label:
                        nutrition_data['fiber_g'] = numeric_value
        
        return nutrition_data if nutrition_data else None
    
    def _scrape_britannia(self, soup: BeautifulSoup, product_name: str) -> Optional[Dict]:
        """Scrape Britannia website"""
        return self._generic_scrape(soup, product_name)
    
    def _scrape_nestle(self, soup: BeautifulSoup, product_name: str) -> Optional[Dict]:
        """Scrape Nestle India website"""
        return self._generic_scrape(soup, product_name)
    
    def _scrape_parle(self, soup: BeautifulSoup, product_name: str) -> Optional[Dict]:
        """Scrape Parle website"""
        return self._generic_scrape(soup, product_name)
    
    def _generic_scrape(self, soup: BeautifulSoup, product_name: str) -> Optional[Dict]:
        """
        Generic scraping method for any food website
        Looks for common patterns in nutrition tables
        """
        nutrition_data = {}
        
        # Find all tables
        tables = soup.find_all('table')
        
        # Look for nutrition-related divs
        nutrition_divs = soup.find_all(['div', 'section'], class_=re.compile('nutrition|facts|ingredients', re.I))
        
        # Search in tables
        for table in tables:
            text = table.get_text().lower()
            if 'nutrition' in text or 'energy' in text or 'calorie' in text:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        numeric_value = self._extract_number(value)
                        
                        if numeric_value:
                            if 'energy' in label or 'calorie' in label or 'kcal' in label:
                                nutrition_data['calories'] = numeric_value
                            elif 'protein' in label:
                                nutrition_data['protein_g'] = numeric_value
                            elif 'carbohydrate' in label:
                                nutrition_data['carbs_g'] = numeric_value
                            elif 'fat' in label and 'saturated' not in label:
                                nutrition_data['fat_g'] = numeric_value
                            elif 'sugar' in label:
                                nutrition_data['sugar_g'] = numeric_value
                            elif 'fiber' in label or 'fibre' in label:
                                nutrition_data['fiber_g'] = numeric_value
                            elif 'sodium' in label or 'salt' in label:
                                nutrition_data['sodium_mg'] = numeric_value
        
        # Search in divs
        for div in nutrition_divs:
            text = div.get_text()
            
            # Look for patterns like "Energy: 500 kcal"
            patterns = {
                r'energy[:\s]+(\d+(?:\.\d+)?)\s*k?cal': 'calories',
                r'protein[:\s]+(\d+(?:\.\d+)?)\s*g': 'protein_g',
                r'carbohydrate[:\s]+(\d+(?:\.\d+)?)\s*g': 'carbs_g',
                r'total\s+fat[:\s]+(\d+(?:\.\d+)?)\s*g': 'fat_g',
                r'sugar[:\s]+(\d+(?:\.\d+)?)\s*g': 'sugar_g',
                r'fib[re]+[:\s]+(\d+(?:\.\d+)?)\s*g': 'fiber_g',
                r'sodium[:\s]+(\d+(?:\.\d+)?)\s*mg': 'sodium_mg',
            }
            
            for pattern, key in patterns.items():
                match = re.search(pattern, text, re.I)
                if match:
                    nutrition_data[key] = float(match.group(1))
        
        return nutrition_data if nutrition_data else None
    
    def _extract_number(self, text: str) -> Optional[float]:
        """Extract first number from text"""
        match = re.search(r'(\d+(?:\.\d+)?)', text)
        if match:
            return float(match.group(1))
        return None
    
    def _extract_brand_from_name(self, product_name: str) -> Optional[str]:
        """Extract brand name from product name"""
        product_lower = product_name.lower()
        
        brand_keywords = [
            'amul', 'britannia', 'parle', 'nestle', 'maggi', 
            'kitkat', 'haldiram', 'haldirams', 'itc', 'sunfeast', 
            'aashirvaad', 'yippee', 'top ramen', 'bingo', 'lays',
            'kurkure', 'horlicks', 'bournvita', 'dairy milk',
            'oreo', 'cadbury', 'knorr'
        ]
        
        for brand in brand_keywords:
            if brand in product_lower:
                logger.info(f"   🎯 Found brand keyword: {brand}")
                return brand
        
        return None
    
    def _identify_brand_from_barcode(self, barcode: str) -> Optional[str]:
        """Identify country/brand from barcode prefix"""
        if not barcode:
            return None
        
        for prefix, country in self.barcode_prefixes.items():
            if barcode.startswith(prefix):
                return country
        
        return None
