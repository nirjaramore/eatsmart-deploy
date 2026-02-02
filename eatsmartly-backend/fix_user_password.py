"""
Fix the eatsmartly user password
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

print("Connecting as postgres superuser...")
try:
    # Connect as postgres
    conn = psycopg2.connect(
        host="localhost",
        database="eatsmartly",
        user="postgres",
        password="shreyas"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Reset password
    print("Resetting eatsmartly password...")
    cursor.execute("ALTER USER eatsmartly WITH PASSWORD 'shreyas';")
    
    # Grant all privileges
    print("Granting privileges...")
    cursor.execute("GRANT ALL PRIVILEGES ON DATABASE eatsmartly TO eatsmartly;")
    cursor.execute("ALTER DATABASE eatsmartly OWNER TO eatsmartly;")
    
    # Grant schema privileges
    cursor.execute("GRANT ALL ON SCHEMA public TO eatsmartly;")
    cursor.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO eatsmartly;")
    cursor.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO eatsmartly;")
    
    print("✅ Password and privileges updated successfully!")
    
    cursor.close()
    conn.close()
    
    # Test connection as eatsmartly
    print("\nTesting connection as eatsmartly...")
    test_conn = psycopg2.connect(
        host="localhost",
        database="eatsmartly",
        user="eatsmartly",
        password="shreyas"
    )
    print("✅ Connection successful!")
    test_conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
