import requests
import json

# Check what product 123456789 actually is
barcode = "123456789"
url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

response = requests.get(url)
data = response.json()

if data.get("status") == 1:
    product = data.get("product", {})
    
    print(f"✅ FOUND IN OPEN FOOD FACTS!")
    print(f"Barcode: {barcode}")
    print(f"Name: {product.get('product_name')}")
    print(f"Brand: {product.get('brands')}")
    print(f"Categories: {product.get('categories')}")
    print(f"Countries: {product.get('countries')}")
    
    # Full nutrition
    nutrients = product.get("nutriments", {})
    print(f"\nNutrition (per 100g):")
    print(f"  Calories: {nutrients.get('energy-kcal_100g')} kcal")
    print(f"  Protein: {nutrients.get('proteins_100g')} g")
    print(f"  Carbs: {nutrients.get('carbohydrates_100g')} g")
    print(f"  Fat: {nutrients.get('fat_100g')} g")
    print(f"  Sugar: {nutrients.get('sugars_100g')} g")
    print(f"  Sodium: {nutrients.get('sodium_100g')} mg")
    print(f"  Fiber: {nutrients.get('fiber_100g')} g")
    
    print(f"\nIngredients: {product.get('ingredients_text', 'N/A')}")
    print(f"Allergens: {product.get('allergens', 'N/A')}")
    
    # Full JSON for debugging
    print("\n" + "="*50)
    print("FULL PRODUCT DATA:")
    print(json.dumps(product, indent=2)[:1000] + "...")
else:
    print("Not found")
