import requests

# Test with popular products that are definitely in Open Food Facts
test_barcodes = {
    "737628064502": "Nutella",
    "0012000181078": "Coca-Cola 12oz Can",
    "3017620422003": "Nutella (France)",
    "5449000000996": "Coca-Cola 330ml",
    "8076809513838": "Ferrero Rocher",
}

print("Testing Open Food Facts with well-known products:\n")

for barcode, expected_name in test_barcodes.items():
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if data.get("status") == 1:
        product = data.get("product", {})
        nutrients = product.get("nutriments", {})
        
        print(f"✅ {expected_name}")
        print(f"   Barcode: {barcode}")
        print(f"   Name: {product.get('product_name', 'N/A')}")
        print(f"   Brand: {product.get('brands', 'N/A')}")
        print(f"   Calories: {nutrients.get('energy-kcal_100g', 'N/A')} kcal/100g")
        print(f"   Protein: {nutrients.get('proteins_100g', 'N/A')} g")
        print(f"   Categories: {product.get('categories', 'N/A')[:50]}")
        print()
    else:
        print(f"❌ {expected_name} (barcode: {barcode}) - Not found\n")

print("\n" + "="*60)
print("Now testing with your backend API:")
print("="*60 + "\n")

# Test with backend
import time

for barcode, expected_name in list(test_barcodes.items())[:2]:
    print(f"Testing {expected_name} (barcode: {barcode})...")
    start = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze-barcode",
            json={
                "barcode": barcode,
                "user_id": "test",
                "detailed": True
            },
            timeout=60
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS ({elapsed:.2f}s)")
            print(f"   Product: {data.get('food_name')}")
            print(f"   Brand: {data.get('brand')}")
            print(f"   Verdict: {data.get('verdict')}")
            print(f"   Health Score: {data.get('health_score')}")
            print(f"   Source: Backend found it!")
        else:
            print(f"❌ FAILED ({elapsed:.2f}s)")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()
