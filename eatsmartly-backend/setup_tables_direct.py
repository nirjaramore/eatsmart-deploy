"""
Setup database tables directly from SQL file using DATABASE_URL
"""
import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('DATABASE_URL_SUPABASE')

if not DATABASE_URL:
    print("\nERROR: No DATABASE_URL or DATABASE_URL_SUPABASE found in environment.\nPlease set DATABASE_URL or DATABASE_URL_SUPABASE in your .env file and retry.")
    raise SystemExit(1)

print("=" * 80)
print("🚀 EatSmartly Database Tables Setup")
print("=" * 80)
print(f"Using DATABASE_URL: {DATABASE_URL}")

try:
    # Connect using DATABASE_URL
    print("\nConnecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Read SQL file
    sql_file = Path(__file__).parent / "database_setup.sql"
    print(f"Reading {sql_file}...")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Execute SQL
    print("Creating tables...")
    cursor.execute(sql_content)
    conn.commit()
    
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
    print(f"\n📋 Found {len(tables)} tables:")
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
    print("1. Run: python import_ifct_data.py (to import IFCT2017 data)")
    print("2. Run: python import_indian_products.py (to import Indian products)")
    print("3. Start the backend server")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
