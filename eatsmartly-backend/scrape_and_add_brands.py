"""
Scrape brands and add products to Supabase database
This script scrapes products from Disano, Organic Tattva, and Barilla websites
and adds them to the food_products table in Supabase.

Usage:
    python scrape_and_add_brands.py
    
Environment variables required:
    - SUPABASE_URL
    - SUPABASE_ANON_KEY (or SUPABASE_SERVICE_ROLE_KEY)
"""
import os
import sys
import requests
import logging
from typing import List, Dict
from scrapers.brand_scrapers import scrape_all_brands

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_SERVICE_ROLE_KEY) must be set")
    sys.exit(1)

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

API_BASE = SUPABASE_URL.rstrip('/') + '/rest/v1/food_products'


def product_exists(product_url: str) -> bool:
    """
    Check if a product with this URL already exists in database
    
    Args:
        product_url: Product page URL
        
    Returns:
        True if product exists, False otherwise
    """
    try:
        if not product_url:
            return False
            
        # Query Supabase for existing product
        response = requests.get(
            API_BASE,
            headers=HEADERS,
            params={'product_page_url': f'eq.{product_url}', 'select': 'id'}
        )
        
        if response.status_code == 200:
            data = response.json()
            return len(data) > 0
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking if product exists: {e}")
        return False


def add_product_to_supabase(product: Dict) -> bool:
    """
    Add a single product to Supabase
    
    Args:
        product: Product dictionary with scraped data
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if product already exists
        if product.get('product_url') and product_exists(product['product_url']):
            logger.info(f"⏭️  Product already exists: {product['name'][:50]}...")
            return False
        
        # Prepare product data for database
        db_product = {
            'name': product['name'],
            'brand': product['brand'],
            'category': product.get('category'),
            'source': product['source'],
            'official_website': product.get('official_website'),
            'product_page_url': product.get('product_url'),
            'is_indian_product': product.get('is_indian_product', False),
        }
        
        # Add optional fields if available
        if product.get('price'):
            db_product['metadata'] = {'price': product['price']}
        
        # Insert into Supabase
        response = requests.post(
            API_BASE,
            headers=HEADERS,
            json=db_product
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            if result and len(result) > 0:
                product_id = result[0].get('id')
                logger.info(f"✅ Added product (ID: {product_id}): {product['name'][:50]}...")
                return True
            else:
                logger.warning(f"⚠️  No data returned for: {product['name'][:50]}...")
                return False
        else:
            logger.error(f"❌ Failed to add product: {response.status_code} - {response.text[:200]}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error adding product to Supabase: {e}")
        return False


def add_all_products(products_by_brand: Dict[str, List[Dict]]) -> Dict:
    """
    Add all scraped products to Supabase
    
    Args:
        products_by_brand: Dictionary with brand names as keys and product lists as values
        
    Returns:
        Dictionary with statistics
    """
    stats = {
        'total_scraped': 0,
        'added': 0,
        'skipped': 0,
        'failed': 0
    }
    
    for brand, products in products_by_brand.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {brand} products ({len(products)} total)")
        logger.info(f"{'='*60}")
        
        stats['total_scraped'] += len(products)
        
        for product in products:
            result = add_product_to_supabase(product)
            
            if result:
                stats['added'] += 1
            elif product_exists(product.get('product_url', '')):
                stats['skipped'] += 1
            else:
                stats['failed'] += 1
    
    return stats


def main():
    """Main function to scrape and add products"""
    
    print("\n" + "="*60)
    print("BRAND SCRAPER & DATABASE IMPORTER")
    print("="*60)
    print("\nScraping products from:")
    print("  - Disano Foods (https://disanofoods.com/)")
    print("  - Organic Tattva (https://organictattva.com/)")
    print("  - Barilla (https://www.barilla.com/)")
    print("\n" + "="*60 + "\n")
    
    # Step 1: Scrape all brands
    logger.info("🔍 Starting web scraping...")
    products_by_brand = scrape_all_brands(max_per_brand=50)
    
    total_scraped = sum(len(products) for products in products_by_brand.values())
    
    if total_scraped == 0:
        logger.warning("⚠️  No products were scraped. Check your internet connection or website availability.")
        return
    
    logger.info(f"\n✅ Scraping complete! Found {total_scraped} products total")
    
    # Step 2: Add products to database
    logger.info("\n📦 Adding products to Supabase database...")
    stats = add_all_products(products_by_brand)
    
    # Step 3: Print summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print(f"\nProducts scraped:     {stats['total_scraped']}")
    print(f"Successfully added:   {stats['added']}")
    print(f"Skipped (existing):   {stats['skipped']}")
    print(f"Failed:               {stats['failed']}")
    print(f"\nSuccess rate:         {(stats['added'] / stats['total_scraped'] * 100):.1f}%")
    print("\n" + "="*60 + "\n")
    
    if stats['failed'] > 0:
        logger.warning(f"⚠️  {stats['failed']} products failed to import. Check logs above for details.")
    
    logger.info("✅ Import process complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)
