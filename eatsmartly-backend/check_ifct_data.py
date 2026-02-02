"""
Check IFCT data in database
"""
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="eatsmartly",
    user="eatsmartly",
    password="shreyas"
)
cursor = conn.cursor()

cursor.execute('SELECT food_code, food_name, food_group, protein_g, carbohydrate_g, fat_g, energy_kcal FROM ifct_foods LIMIT 10')
rows = cursor.fetchall()

print('IFCT Foods in database:')
print('=' * 80)
for row in rows:
    print(f"Code: {row[0]}, Name: {row[1]}, Group: {row[2]}")
    print(f"  Protein: {row[3]}g, Carbs: {row[4]}g, Fat: {row[5]}g, Energy: {row[6]} kcal")
    print()

cursor.close()
conn.close()