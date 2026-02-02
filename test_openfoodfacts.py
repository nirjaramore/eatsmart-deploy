import requests
import json

# Test Open Food Facts with real Indian barcodes
test_barcodes = [
    "8901030778261",  # Maggi
    "8901063311886",  # Britannia
    "8901396316046",  # Parle-G
    "5000112638144",  # Coca-Cola
]

print("Testing Open Food Facts API with Indian barcodes:\n")

for barcode in test_barcodes:
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("status") == 1:
            product = data.get("product", {})
            print(f"✅ Barcode: {barcode}")
            print(f"   Name: {product.get('product_name', 'N/A')}")
            print(f"   Brand: {product.get('brands', 'N/A')}")
            print(f"   Categories: {product.get('categories', 'N/A')}")
            
            # Nutrition
            nutrients = product.get("nutriments", {})
            print(f"   Calories: {nutrients.get('energy-kcal_100g', 'N/A')} kcal/100g")
            print(f"   Protein: {nutrients.get('proteins_100g', 'N/A')} g")
            print(f"   Carbs: {nutrients.get('carbohydrates_100g', 'N/A')} g")
            print(f"   Fat: {nutrients.get('fat_100g', 'N/A')} g")
            print()
        else:
            print(f"❌ Barcode: {barcode} - Not found in database\n")
    
    except Exception as e:
        print(f"❌ Error for {barcode}: {e}\n")

print("\nTesting with your barcode (123456789):")
response = requests.get("https://world.openfoodfacts.org/api/v0/product/123456789.json")
data = response.json()
print(f"Status: {data.get('status')}")
print(f"Found: {'Yes' if data.get('status') == 1 else 'No (invalid barcode)'}")
