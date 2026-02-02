"""
Database setup script for EatSmartly
Run this to create tables and import IFCT data
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from pathlib import Path

def create_database():
    """Create the database if it doesn't exist"""
    print("📊 Creating database...")
    
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host="localhost",
            database="eatsmartly",
            user="postgres",
            password="shreyas"  # Your postgres password from .env
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='eatsmartly'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE eatsmartly")
            print("✅ Database 'eatsmartly' created")
        else:
            print("ℹ️  Database 'eatsmartly' already exists")
        
        # Create user
        cursor.execute("SELECT 1 FROM pg_user WHERE usename='eatsmartly'")
        user_exists = cursor.fetchone()
        
        if not user_exists:
            cursor.execute("CREATE USER eatsmartly WITH PASSWORD 'shreyas'")
            print("✅ User 'eatsmartly' created")
        else:
            print("ℹ️  User 'eatsmartly' already exists")
            cursor.execute("ALTER USER eatsmartly WITH PASSWORD 'shreyas'")
            print("✅ Password updated for user 'eatsmartly'")
        
        # Always grant privileges
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE eatsmartly TO eatsmartly")
        cursor.execute("ALTER DATABASE eatsmartly OWNER TO eatsmartly")
        print("✅ Privileges granted to eatsmartly")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("\n📝 Run these commands manually in psql:")
        print("   CREATE DATABASE eatsmartly;")
        print("   CREATE USER eatsmartly WITH PASSWORD 'password';")
        print("   GRANT ALL PRIVILEGES ON DATABASE eatsmartly TO eatsmartly;")

def run_sql_file(filepath):
    """Execute SQL file"""
    print(f"📄 Running {filepath}...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="eatsmartly",
            user="eatsmartly",
            password="password"
        )
        cursor = conn.cursor()
        
        # Read and execute SQL file
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()
            cursor.execute(sql)
            conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"✅ {filepath} executed successfully")
        
    except Exception as e:
        print(f"❌ Error executing {filepath}: {e}")
        raise

def verify_tables():
    """Verify tables were created"""
    print("\n🔍 Verifying tables...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="eatsmartly",
            user="eatsmartly",
            password="password"
        )
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        
        print("\n📋 Created tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {table[0]} (rows: {count})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 EatSmartly Database Setup")
    print("=" * 80)
    
    # Step 1: Create database
    create_database()
    
    # Step 2: Run SQL file
    sql_file = Path(__file__).parent / "database_setup.sql"
    if sql_file.exists():
        run_sql_file(sql_file)
    else:
        print(f"❌ SQL file not found: {sql_file}")
    
    # Step 3: Verify
    verify_tables()
    
    print("\n" + "=" * 80)
    print("✅ Database setup complete!")
    print("=" * 80)
    print("\n📝 Next steps:")
    print("1. Your .env is already configured: DATABASE_URL=postgresql://eatsmartly:shreyas@localhost:5432/eatsmartly")
    print("2. Run: python import_ifct_data.py (to import IFCT2017 PDF data)")
    print("3. Run: python import_indian_products.py (to import Indian products)")
    print("4. Restart the backend server")
