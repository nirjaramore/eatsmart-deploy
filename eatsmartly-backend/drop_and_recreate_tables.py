"""
Drop all existing tables and recreate them
"""
import psycopg2
import os
from pathlib import Path

DATABASE_URL = "postgresql://eatsmartly:shreyas@localhost:5432/eatsmartly"

print("=" * 80)
print("🗑️  Dropping and recreating database tables")
print("=" * 80)

try:
    # Connect
    print("\nConnecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Drop all tables
    print("Dropping existing tables...")
    tables_to_drop = [
        'scan_history',
        'product_alternatives',
        'product_search_cache',
        'user_profiles',
        'food_products',
        'ifct_foods'
    ]
    
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            print(f"  Dropped {table}")
        except Exception as e:
            print(f"  Skipped {table}: {e}")
    
    # Drop functions if they exist
    try:
        cursor.execute("DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE")
        print("  Dropped function update_updated_at_column")
    except:
        pass
    
    # Read and execute SQL file
    sql_file = Path(__file__).parent / "database_setup.sql"
    print(f"\nReading {sql_file}...")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print("Creating tables...")
    cursor.execute(sql_content)
    
    print("✅ Tables created successfully!")
    
    # Verify tables
    print("\n🔍 Verifying tables...")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print(f"\n📋 Created {len(tables)} tables:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   ✅ {table[0]} (rows: {count})")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ Database setup complete!")
    print("=" * 80)
    print("\n📝 Next steps:")
    print("1. Run: python import_ifct_data.py")
    print("2. Run: python import_indian_products.py")
    print("3. Start the backend server")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
