"""
Add or update products in Supabase with nutrition data.
Supports both bulk product imports and individual products with detailed nutrition facts.

Usage:
  - Ensure SUPABASE_URL and SUPABASE_ANON_KEY are set in your environment or .env
  - python add_products_supabase.py
  
To add a product with nutrition:
  - Use add_product_with_nutrition(product_data, nutrition_data) function
"""
import os
import sys
import requests
import logging
from urllib.parse import quote  # ✅ Changed from quote_plus to quote
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import brand scrapers
try:
    from scrapers.brand_scrapers import scrape_all_brands
except ImportError:
    # If import fails, we'll just use the hardcoded products list
    scrape_all_brands = None
    logging.warning("Could not import brand_scrapers. Will use hardcoded products only.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    logger.error("SUPABASE_URL and SUPABASE_ANON_KEY must be set in the environment.")
    raise SystemExit(1)

# Use the anon/public key for client-like requests as requested
HEADERS = {
    'apikey': SUPABASE_ANON_KEY,
    'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# Supabase storage info for images
SUPABASE_PUBLIC_BUCKET = "eatsmart"
SUPABASE_PROJECT_URL = SUPABASE_URL.rstrip('/')

def build_supabase_image_url(filename: str) -> str:
    """
    Returns a properly URL-encoded public Supabase storage URL for the image.
    """
    safe_filename = quote(filename, safe="/")
    return f"{SUPABASE_PROJECT_URL}/storage/v1/object/public/{SUPABASE_PUBLIC_BUCKET}/{safe_filename}"

# Try 'products' table first (as suggested by Supabase error), fallback to 'food_products'
API_BASE = SUPABASE_URL.rstrip('/') + '/rest/v1/products'
API_BASE_NUTRITION = SUPABASE_URL.rstrip('/') + '/rest/v1/nutrition_facts'

# Products to add/update (you can extend this list)
PRODUCTS = [
    {
        'name': 'Disano Whole Wheat Pasta',
        'brand': 'Disano',
        'category': 'Pasta',
        'source': 'manual',
        'official_website': 'https://disanofoods.com/',
        'product_page_url': 'https://disanofoods.com/',
        'is_indian_product': True,
        'image_filename': 'disano_pasta_front.webp'
    },
    {
        'name': 'Barilla Whole Wheat Pasta',
        'brand': 'Barilla',
        'category': 'Pasta',
        'source': 'manual',
        'official_website': 'https://www.barilla.com/',
        'product_page_url': 'https://www.barilla.com/',
        'is_indian_product': False,
        'image_filename': 'barilla_pasta_front.webp'
    },
    # ... add rest of your products, include 'image_filename' key
]


def supabase_insert(product):
    """
    Insert a product into Supabase, generating a proper image URL.
    """
    minimal_product = {
        'name': product['name'],
        'brand': product['brand'],
    }

    if product.get('category'):
        minimal_product['category'] = product['category']
    if product.get('source'):
        minimal_product['source'] = product['source']
    if product.get('official_website'):
        minimal_product['url'] = product.get('official_website')  # Use 'url' not 'official_website'

    # ✅ Build image_url using helper if image_filename exists
    if product.get('image_filename'):
        minimal_product['image_url'] = build_supabase_image_url(product['image_filename'])

    r = requests.post(API_BASE, headers=HEADERS, json=minimal_product)
    if r.status_code not in (200, 201):
        logger.error(f"Insert failed: {r.status_code} {r.text}")
        return None
    return r.json()[0] if r.json() else None


def supabase_update(product_id, product):
    url = f"{API_BASE}?id=eq.{product_id}"
    r = requests.patch(url, headers=HEADERS, json=product)
    if r.status_code not in (200, 204):
        logger.error(f"Update failed: {r.status_code} {r.text}")
        return None
    # fetch updated
    r2 = requests.get(f"{API_BASE}?id=eq.{product_id}&select=*")
    if r2.status_code == 200:
        return r2.json()[0]
    return None


def supabase_get_by_url(url):
    # Try to filter by url field (not product_page_url)
    filter_url = quote(f"url=eq.{url}")
    q = f"{API_BASE}?{filter_url}&select=id,url"
    r = requests.get(q, headers=HEADERS)
    if r.status_code != 200:
        logger.debug(f"GET query failed: {r.status_code} {r.text}")
        return None
    data = r.json()
    return data[0] if data else None


def main():
    print("\n" + "="*60)
    print("BRAND PRODUCT SCRAPER & DATABASE IMPORTER")
    print("="*60)

    scraped_products = []
    if scrape_all_brands:
        print("\n🔍 Scraping products from brand websites...")
        try:
            products_by_brand = scrape_all_brands(max_per_brand=30)
            for brand, products in products_by_brand.items():
                for product in products:
                    scraped_products.append({
                        'name': product['name'],
                        'brand': product['brand'],
                        'category': product.get('category', 'Food'),
                        'source': product['source'],
                        'official_website': product.get('official_website'),
                        'product_page_url': product.get('product_url'),
                        'is_indian_product': product.get('is_indian_product', False),
                        'image_filename': product.get('image_filename')
                    })
            logger.info(f"\n✅ Scraped {len(scraped_products)} products from brand websites")
        except Exception as e:
            logger.error(f"❌ Error during scraping: {e}")
            logger.info("Falling back to hardcoded products list")
    else:
        logger.info("⚠️  Brand scrapers not available, using hardcoded products only")

    all_products = scraped_products + PRODUCTS if scraped_products else PRODUCTS

    print(f"\n📦 Processing {len(all_products)} total products...")
    print("="*60 + "\n")

    stats = {'added': 0, 'updated': 0, 'failed': 0}

    for i, p in enumerate(all_products, 1):
        logger.info(f"[{i}/{len(all_products)}] Processing: {p['brand']} - {p['name'][:50]}...")

        try:
            existing = supabase_get_by_url(p['product_page_url'])
            if existing:
                pid = existing['id']
                logger.info(f"  ↻ Found existing product id={pid}, updating...")
                updated = supabase_update(pid, p)
                if updated:
                    logger.info(f"  ✅ Updated successfully")
                    stats['updated'] += 1
                else:
                    logger.error(f"  ❌ Update failed")
                    stats['failed'] += 1
            else:
                inserted = supabase_insert(p)
                if inserted:
                    logger.info(f"  ✅ Inserted new product (ID: {inserted.get('id')})")
                    stats['added'] += 1
                else:
                    logger.error(f"  ❌ Insert failed")
                    stats['failed'] += 1
        except Exception as e:
            logger.error(f"  ❌ Error processing product: {e}")
            stats['failed'] += 1

    print("\n" + "="*60)
    print("IMPORT SUMMARY")
    print("="*60)
    print(f"Total processed:      {len(all_products)}")
    print(f"New products added:   {stats['added']}")
    print(f"Existing updated:     {stats['updated']}")
    print(f"Failed:               {stats['failed']}")
    print(f"Success rate:         {((stats['added'] + stats['updated']) / len(all_products) * 100):.1f}%")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
