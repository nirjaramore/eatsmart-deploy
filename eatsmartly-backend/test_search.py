import psycopg2

# Connect directly to database
conn = psycopg2.connect(
    host='localhost',
    database='eatsmartly',
    user='eatsmartly',
    password='shreyas'
)
cur = conn.cursor()

# Check total products
cur.execute('SELECT COUNT(*) FROM food_products')
total = cur.fetchone()[0]
print(f'Total products in food_products: {total}')

# Check Amul products
cur.execute("SELECT COUNT(*) FROM food_products WHERE name ILIKE '%amul%' OR brand ILIKE '%amul%'")
amul_count = cur.fetchone()[0]
print(f'Amul products: {amul_count}')

# Show sample Amul products
if amul_count > 0:
    cur.execute("SELECT name, brand FROM food_products WHERE name ILIKE '%amul%' OR brand ILIKE '%amul%' LIMIT 5")
    print('\nSample Amul products:')
    for row in cur.fetchall():
        print(f'  - {row[0]} ({row[1]})')

cur.close()
conn.close()
