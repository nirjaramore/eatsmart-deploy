"""
Import OpenFoodFacts Indian Products to Database
Fetches Indian FMCG products and imports to PostgreSQL
"""
import sys
import psycopg2
import logging
from typing import List, Dict

# Add parent directory to path
sys.path.append('.')

from agents.openfoodfacts_indian_fetcher import OpenFoodFactsIndiaFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="eatsmartly",
            user="eatsmartly",
            password="shreyas"
        )
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.info("Make sure you've run setup_database.py first!")
        sys.exit(1)

def import_products_to_db(products: List[Dict]):
    """
    Import normalized products to food_products table
    """
    logger.info(f"💾 Importing {len(products)} products to database...")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    inserted = 0
    updated = 0
    skipped = 0
    
    for product in products:
        try:
            # Prepare data
            allergens_str = ','.join(product.get('allergens', [])) if product.get('allergens') else None
            
            # Insert or update
            sql = """
                INSERT INTO food_products (
                    barcode, name, brand, category, source,
                    calories, protein_g, carbs_g, fat_g, saturated_fat_g, trans_fat_g,
                    fiber_g, sugar_g, sodium_mg, cholesterol_mg,
                    calcium_mg, iron_mg, vitamin_a_mcg, vitamin_c_mg,
                    ingredients, allergens,
                    serving_size, serving_unit,
                    is_indian_product,
                    product_page_url
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s, %s,
                    %s,
                    %s
                )
                ON CONFLICT (barcode) DO UPDATE SET
                    name = EXCLUDED.name,
                    brand = EXCLUDED.brand,
                    category = EXCLUDED.category,
                    calories = COALESCE(EXCLUDED.calories, food_products.calories),
                    protein_g = COALESCE(EXCLUDED.protein_g, food_products.protein_g),
                    carbs_g = COALESCE(EXCLUDED.carbs_g, food_products.carbs_g),
                    fat_g = COALESCE(EXCLUDED.fat_g, food_products.fat_g),
                    updated_at = CURRENT_TIMESTAMP
            """
            
            values = (
                product.get('barcode'),
                product.get('name'),
                product.get('brand'),
                product.get('category'),
                product.get('source'),
                # Nutrition
                product.get('calories'),
                product.get('protein_g'),
                product.get('carbs_g'),
                product.get('fat_g'),
                product.get('saturated_fat_g'),
                product.get('trans_fat_g'),
                product.get('fiber_g'),
                product.get('sugar_g'),
                product.get('sodium_mg'),
                product.get('cholesterol_mg'),
                # Additional nutrients
                product.get('calcium_mg'),
                product.get('iron_mg'),
                product.get('vitamin_a_mcg'),
                product.get('vitamin_c_mg'),
                # Other fields
                product.get('ingredients'),
                allergens_str,
                product.get('serving_size'),
                product.get('serving_unit'),
                product.get('is_indian_product', True),
                product.get('product_page_url'),
            )
            
            cursor.execute(sql, values)
            
            if cursor.rowcount == 1:
                inserted += 1
            else:
                updated += 1
            
            if (inserted + updated) % 100 == 0:
                conn.commit()
                logger.info(f"   ✅ Processed {inserted + updated} products (Inserted: {inserted}, Updated: {updated})")
        
        except Exception as e:
            logger.warning(f"   ⚠️  Error importing {product.get('name', 'unknown')}: {e}")
            skipped += 1
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info(f"✅ Import complete!")
    logger.info(f"   📊 Inserted: {inserted}")
    logger.info(f"   📊 Updated: {updated}")
    logger.info(f"   📊 Skipped: {skipped}")
    
    return inserted, updated, skipped

def verify_import():
    """Verify the import was successful"""
    logger.info("🔍 Verifying import...")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Count products
    cursor.execute("SELECT COUNT(*) FROM food_products WHERE is_indian_product = TRUE")
    count = cursor.fetchone()[0]
    logger.info(f"   ✅ Indian products in database: {count}")
    
    # Top brands
    cursor.execute("""
        SELECT brand, COUNT(*) as count 
        FROM food_products 
        WHERE is_indian_product = TRUE AND brand IS NOT NULL
        GROUP BY brand 
        ORDER BY count DESC 
        LIMIT 10
    """)
    
    logger.info("\n📊 Top 10 Indian Brands:")
    for brand, count in cursor.fetchall():
        logger.info(f"   • {brand}: {count} products")
    
    # Top categories
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM food_products 
        WHERE is_indian_product = TRUE
        GROUP BY category 
        ORDER BY count DESC 
        LIMIT 10
    """)
    
    logger.info("\n📊 Top 10 Categories:")
    for category, count in cursor.fetchall():
        logger.info(f"   • {category}: {count} products")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("=" * 80)
    print("🇮🇳 Import OpenFoodFacts Indian Products to Database")
    print("=" * 80)
    
    # Ask how many products to fetch
    try:
        limit = int(input("\nHow many products to fetch? (default 1000): ").strip() or "1000")
    except ValueError:
        limit = 1000
    
    print(f"\n📊 Fetching {limit} products from OpenFoodFacts India...")
    
    # Fetch and normalize products
    fetcher = OpenFoodFactsIndiaFetcher()
    products = fetcher.fetch_and_normalize_indian_products(limit=limit)
    
    if not products:
        logger.error("❌ No products fetched!")
        sys.exit(1)
    
    # Show statistics
    stats = fetcher.get_product_statistics(products)
    print("\n" + "=" * 80)
    print("📊 STATISTICS")
    print("=" * 80)
    print(f"Total Products: {stats['total_products']}")
    print(f"With Nutrition: {stats['with_nutrition']}")
    print(f"Unique Brands: {stats['unique_brands']}")
    
    # Confirm import
    print("\n" + "=" * 80)
    confirm = input("Import to database? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Import cancelled")
        sys.exit(0)
    
    # Import to database
    inserted, updated, skipped = import_products_to_db(products)
    
    # Verify
    print("\n" + "=" * 80)
    verify_import()
    print("=" * 80)
    
    print("\n✅ Import complete!")
    print("\n📝 Next steps:")
    print("1. Restart backend: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("2. Test search: Search for 'Amul', 'Parle', 'Britannia', etc.")
    print("3. Scan barcodes of Indian products")
