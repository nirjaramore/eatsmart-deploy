"""
Test script to verify food_images table data
Run this to check if your food_images table is properly configured
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    exit(1)

print("=" * 80)
print("🔍 Testing food_images Table")
print("=" * 80)

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if table exists
        check_table = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'food_images'
            );
        """)
        
        result = conn.execute(check_table)
        exists = result.scalar()
        
        if not exists:
            print("❌ ERROR: food_images table does not exist!")
            print("\nCreate it with this SQL:")
            print("""
CREATE TABLE public.food_images (
    id BIGSERIAL PRIMARY KEY,
    barcode VARCHAR(13),
    image_url TEXT NOT NULL,
    storage_path TEXT,
    image_type VARCHAR(50) DEFAULT 'product',
    alt_text VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
            """)
            exit(1)
        
        print("✅ food_images table exists\n")
        
        # Get table structure
        print("📋 Table Structure:")
        columns_query = text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'food_images'
            ORDER BY ordinal_position;
        """)
        
        cols = conn.execute(columns_query).fetchall()
        for col in cols:
            print(f"   {col[0]}: {col[1]} (nullable: {col[2]})")
        
        # Count total rows
        count_query = text("SELECT COUNT(*) FROM food_images")
        total = conn.execute(count_query).scalar()
        print(f"\n📊 Total rows: {total}")
        
        if total == 0:
            print("\n⚠️  WARNING: No data in food_images table!")
            print("Add some data with SQL like:")
            print("""
INSERT INTO food_images (barcode, image_url, image_type, alt_text)
VALUES 
    ('8901030895784', 
     'https://your-project.supabase.co/storage/v1/object/public/eatsmart/image1.jpg',
     'product', 
     'Product Name');
            """)
        else:
            # Show sample data
            print(f"\n🔍 Sample Data (first 5 rows):")
            sample_query = text("""
                SELECT id, barcode, 
                       SUBSTRING(image_url, 1, 60) as image_url_preview,
                       image_type, alt_text
                FROM food_images 
                ORDER BY uploaded_at DESC 
                LIMIT 5
            """)
            
            samples = conn.execute(sample_query).fetchall()
            for row in samples:
                print(f"\n   ID: {row[0]}")
                print(f"   Barcode: {row[1] or 'None'}")
                print(f"   Image URL: {row[2]}...")
                print(f"   Type: {row[3] or 'None'}")
                print(f"   Alt Text: {row[4] or 'None'}")
            
            # Check for NULL image URLs
            null_query = text("SELECT COUNT(*) FROM food_images WHERE image_url IS NULL")
            null_count = conn.execute(null_query).scalar()
            
            if null_count > 0:
                print(f"\n⚠️  WARNING: {null_count} rows have NULL image_url")
            
            # Check image URL format
            http_query = text("SELECT COUNT(*) FROM food_images WHERE image_url LIKE 'http%'")
            http_count = conn.execute(http_query).scalar()
            
            print(f"\n✅ {http_count} rows have valid HTTP/HTTPS URLs")
            
            if http_count < total:
                print(f"⚠️  {total - http_count} rows have non-HTTP URLs (might be relative paths)")
        
        print("\n" + "=" * 80)
        print("✅ Database check complete!")
        print("=" * 80)
        print("\n📝 Next steps:")
        print("1. Restart your backend: cd eatsmartly-backend && python main.py")
        print("2. Visit: http://localhost:3001/product")
        print("3. Check browser console for any errors")
        print("4. Backend should be at: http://localhost:3000/food-images")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
