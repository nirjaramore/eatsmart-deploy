"""
Brand-specific product scrapers for Disano Foods, Organic Tattva, and Barilla
These scrapers extract product information from brand websites.
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }


def scrape_disano_products(max_products: int = 50) -> List[Dict]:
    """
    Scrape products from Disano Foods website
    
    Args:
        max_products: Maximum number of products to scrape
        
    Returns:
        List of product dictionaries
    """
    try:
        logger.info("🔍 Scraping Disano Foods website...")
        products = []
        
        # Disano product pages - they have collections
        base_url = "https://disanofoods.com"
        
        # Try collections/all or shop pages
        urls_to_try = [
            f"{base_url}/collections/all",
            f"{base_url}/collections/pasta",
            f"{base_url}/collections/honey",
            f"{base_url}/collections/peanut-butter",
        ]
        
        for url in urls_to_try:
            try:
                logger.info(f"Trying URL: {url}")
                time.sleep(2)  # Rate limiting
                
                response = requests.get(url, headers=get_headers(), timeout=15)
                if response.status_code != 200:
                    logger.warning(f"Disano returned status {response.status_code} for {url}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find product cards (common Shopify selectors)
                product_cards = soup.find_all(['div', 'li'], class_=re.compile(r'product.*item|grid.*item|card'))
                
                logger.info(f"Found {len(product_cards)} potential product cards")
                
                for card in product_cards[:max_products]:
                    try:
                        # Extract product name
                        title_elem = card.find(['h2', 'h3', 'a'], class_=re.compile(r'product.*title|card.*title'))
                        if not title_elem:
                            title_elem = card.find('a', href=re.compile(r'/products/'))
                        
                        title = title_elem.get_text(strip=True) if title_elem else None
                        if not title or len(title) < 3:
                            continue
                        
                        # Extract product URL
                        link_elem = card.find('a', href=re.compile(r'/products/'))
                        product_url = None
                        if link_elem:
                            href = link_elem.get('href', '')
                            product_url = href if href.startswith('http') else f"{base_url}{href}"
                        
                        # Extract price
                        price_elem = card.find(['span', 'div'], class_=re.compile(r'price'))
                        price = None
                        if price_elem:
                            price_text = price_elem.get_text(strip=True).replace('₹', '').replace('Rs.', '').replace(',', '').strip()
                            match = re.search(r'(\d+(?:\.\d+)?)', price_text)
                            if match:
                                try:
                                    price = float(match.group(1))
                                except ValueError:
                                    pass
                        
                        # Extract image
                        img_elem = card.find('img')
                        image_url = None
                        if img_elem:
                            image_url = img_elem.get('src') or img_elem.get('data-src')
                            if image_url and not image_url.startswith('http'):
                                image_url = f"https:{image_url}" if image_url.startswith('//') else f"{base_url}{image_url}"
                        
                        product = {
                            'source': 'disano_scrape',
                            'brand': 'Disano',
                            'name': title,
                            'product_url': product_url,
                            'official_website': base_url,
                            'price': price,
                            'image_url': image_url,
                            'category': 'Health Foods',
                            'is_indian_product': True
                        }
                        
                        products.append(product)
                        logger.info(f"✅ Found: {title[:50]}...")
                        
                    except Exception as e:
                        logger.error(f"Error parsing Disano product card: {e}")
                        continue
                
                if len(products) >= max_products:
                    break
                    
            except Exception as e:
                logger.error(f"Error scraping Disano URL {url}: {e}")
                continue
        
        logger.info(f"✅ Scraped {len(products)} products from Disano")
        return products[:max_products]
        
    except Exception as e:
        logger.error(f"Error scraping Disano: {e}")
        return []


def scrape_organic_tattva_products(max_products: int = 50) -> List[Dict]:
    """
    Scrape products from Organic Tattva website
    
    Args:
        max_products: Maximum number of products to scrape
        
    Returns:
        List of product dictionaries
    """
    try:
        logger.info("🔍 Scraping Organic Tattva website...")
        products = []
        
        base_url = "https://organictattva.com"
        
        # Try different collection URLs
        urls_to_try = [
            f"{base_url}/collections/all",
            f"{base_url}/collections/organic-pasta",
            f"{base_url}/collections/organic-grains",
            f"{base_url}/collections/organic-pulses",
        ]
        
        for url in urls_to_try:
            try:
                logger.info(f"Trying URL: {url}")
                time.sleep(2)  # Rate limiting
                
                response = requests.get(url, headers=get_headers(), timeout=15)
                if response.status_code != 200:
                    logger.warning(f"Organic Tattva returned status {response.status_code} for {url}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find product cards
                product_cards = soup.find_all(['div', 'li'], class_=re.compile(r'product.*item|grid.*item|card'))
                
                logger.info(f"Found {len(product_cards)} potential product cards")
                
                for card in product_cards[:max_products]:
                    try:
                        # Extract product name
                        title_elem = card.find(['h2', 'h3', 'a'], class_=re.compile(r'product.*title|card.*title'))
                        if not title_elem:
                            title_elem = card.find('a', href=re.compile(r'/products/'))
                        
                        title = title_elem.get_text(strip=True) if title_elem else None
                        if not title or len(title) < 3:
                            continue
                        
                        # Extract product URL
                        link_elem = card.find('a', href=re.compile(r'/products/'))
                        product_url = None
                        if link_elem:
                            href = link_elem.get('href', '')
                            product_url = href if href.startswith('http') else f"{base_url}{href}"
                        
                        # Extract price
                        price_elem = card.find(['span', 'div'], class_=re.compile(r'price'))
                        price = None
                        if price_elem:
                            price_text = price_elem.get_text(strip=True).replace('₹', '').replace('Rs.', '').replace(',', '').strip()
                            match = re.search(r'(\d+(?:\.\d+)?)', price_text)
                            if match:
                                try:
                                    price = float(match.group(1))
                                except ValueError:
                                    pass
                        
                        # Extract image
                        img_elem = card.find('img')
                        image_url = None
                        if img_elem:
                            image_url = img_elem.get('src') or img_elem.get('data-src')
                            if image_url and not image_url.startswith('http'):
                                image_url = f"https:{image_url}" if image_url.startswith('//') else f"{base_url}{image_url}"
                        
                        product = {
                            'source': 'organic_tattva_scrape',
                            'brand': 'Organic Tattva',
                            'name': title,
                            'product_url': product_url,
                            'official_website': base_url,
                            'price': price,
                            'image_url': image_url,
                            'category': 'Organic Foods',
                            'is_indian_product': True
                        }
                        
                        products.append(product)
                        logger.info(f"✅ Found: {title[:50]}...")
                        
                    except Exception as e:
                        logger.error(f"Error parsing Organic Tattva product card: {e}")
                        continue
                
                if len(products) >= max_products:
                    break
                    
            except Exception as e:
                logger.error(f"Error scraping Organic Tattva URL {url}: {e}")
                continue
        
        logger.info(f"✅ Scraped {len(products)} products from Organic Tattva")
        return products[:max_products]
        
    except Exception as e:
        logger.error(f"Error scraping Organic Tattva: {e}")
        return []


def scrape_barilla_products(max_products: int = 50) -> List[Dict]:
    """
    Scrape products from Barilla website
    
    Args:
        max_products: Maximum number of products to scrape
        
    Returns:
        List of product dictionaries
    """
    try:
        logger.info("🔍 Scraping Barilla website...")
        products = []
        
        base_url = "https://www.barilla.com"
        
        # Barilla US site products
        urls_to_try = [
            f"{base_url}/en-us/products/pasta",
            f"{base_url}/en-us/products/sauces",
        ]
        
        for url in urls_to_try:
            try:
                logger.info(f"Trying URL: {url}")
                time.sleep(2)  # Rate limiting
                
                response = requests.get(url, headers=get_headers(), timeout=15)
                if response.status_code != 200:
                    logger.warning(f"Barilla returned status {response.status_code} for {url}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find product cards
                product_cards = soup.find_all(['div', 'article', 'li'], class_=re.compile(r'product.*card|item'))
                
                logger.info(f"Found {len(product_cards)} potential product cards")
                
                for card in product_cards[:max_products]:
                    try:
                        # Extract product name
                        title_elem = card.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'product.*title|card.*title|name'))
                        if not title_elem:
                            title_elem = card.find('a')
                        
                        title = title_elem.get_text(strip=True) if title_elem else None
                        if not title or len(title) < 3:
                            continue
                        
                        # Extract product URL
                        link_elem = card.find('a', href=True)
                        product_url = None
                        if link_elem:
                            href = link_elem.get('href', '')
                            product_url = href if href.startswith('http') else f"{base_url}{href}"
                        
                        # Extract image
                        img_elem = card.find('img')
                        image_url = None
                        if img_elem:
                            image_url = img_elem.get('src') or img_elem.get('data-src')
                            if image_url and not image_url.startswith('http'):
                                image_url = f"https:{image_url}" if image_url.startswith('//') else f"{base_url}{image_url}"
                        
                        product = {
                            'source': 'barilla_scrape',
                            'brand': 'Barilla',
                            'name': title,
                            'product_url': product_url,
                            'official_website': base_url,
                            'image_url': image_url,
                            'category': 'Pasta',
                            'is_indian_product': False
                        }
                        
                        products.append(product)
                        logger.info(f"✅ Found: {title[:50]}...")
                        
                    except Exception as e:
                        logger.error(f"Error parsing Barilla product card: {e}")
                        continue
                
                if len(products) >= max_products:
                    break
                    
            except Exception as e:
                logger.error(f"Error scraping Barilla URL {url}: {e}")
                continue
        
        logger.info(f"✅ Scraped {len(products)} products from Barilla")
        return products[:max_products]
        
    except Exception as e:
        logger.error(f"Error scraping Barilla: {e}")
        return []


def scrape_all_brands(max_per_brand: int = 50) -> Dict[str, List[Dict]]:
    """
    Scrape products from all three brands
    
    Args:
        max_per_brand: Maximum products to scrape per brand
        
    Returns:
        Dictionary with brand names as keys and product lists as values
    """
    results = {
        'Disano': [],
        'Organic Tattva': [],
        'Barilla': []
    }
    
    logger.info("🚀 Starting to scrape all brands...")
    
    # Scrape each brand
    results['Disano'] = scrape_disano_products(max_per_brand)
    results['Organic Tattva'] = scrape_organic_tattva_products(max_per_brand)
    results['Barilla'] = scrape_barilla_products(max_per_brand)
    
    total = sum(len(products) for products in results.values())
    logger.info(f"\n✅ SCRAPING COMPLETE!")
    logger.info(f"Total products scraped: {total}")
    for brand, products in results.items():
        logger.info(f"  - {brand}: {len(products)} products")
    
    return results


if __name__ == "__main__":
    # Test scraping
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("Testing Brand Scrapers")
    print("="*60 + "\n")
    
    results = scrape_all_brands(max_per_brand=10)
    
    # Print summary
    print("\n" + "="*60)
    print("SCRAPING RESULTS")
    print("="*60)
    
    for brand, products in results.items():
        print(f"\n{brand}: {len(products)} products")
        for i, product in enumerate(products[:3], 1):
            print(f"  {i}. {product['name']}")
            print(f"     URL: {product.get('product_url', 'N/A')}")
