"""
Test Open Food Facts search functionality
"""
import requests
import json

def test_openfoodfacts_search(query):
    """Test Open Food Facts search API directly."""
    print(f"\n🔍 Testing Open Food Facts search for: '{query}'")
    print("="*60)
    
    search_url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 5,
        "sort_by": "popularity"
    }
    
    try:
        response = requests.get(search_url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        products = data.get("products", [])
        
        print(f"Found {len(products)} products")
        
        for i, product in enumerate(products[:3], 1):
            name = product.get("product_name") or product.get("product_name_en", "Unknown")
            brand = product.get("brands", "Unknown")
            barcode = product.get("code", "No barcode")
            
            print(f"\n{i}. {name}")
            print(f"   Brand: {brand}")
            print(f"   Barcode: {barcode}")
            
            # Check nutrition data
            nutrients = product.get("nutriments", {})
            calories = nutrients.get("energy-kcal_100g") or nutrients.get("energy-kcal")
            if calories:
                print(f"   Calories: {calories} kcal/100g")
        
        return len(products) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_backend_search(query):
    """Test our backend search endpoint."""
    print(f"\n🔍 Testing backend search for: '{query}'")
    print("="*60)
    
    try:
        response = requests.post(
            "http://192.168.1.4:8000/search",
            json={"query": query, "user_id": "test_user", "limit": 3}
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            print(f"Status: {response.status_code}")
            print(f"Found {len(results)} results")
            
            for i, product in enumerate(results, 1):
                print(f"\n{i}. {product.get('name')} ({product.get('brand')})")
                print(f"   Source: {product.get('source')}")
                print(f"   Calories: {product.get('calories')}")
                print(f"   Protein: {product.get('protein_g')}g")
                print(f"   Sugar: {product.get('sugar_g')}g")
            
            return len(results) > 0
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.json())
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_queries = [
        "dr oetkers mayonaise",
        "dr oetker mayonnaise",
        "mayonnaise",
        "amul butter",
        "coca cola"
    ]
    
    print("🧪 TESTING OPEN FOOD FACTS INTEGRATION")
    print("="*80)
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"QUERY: {query.upper()}")
        print('='*80)
        
        # Test direct API
        direct_found = test_openfoodfacts_search(query)
        
        # Test backend
        backend_found = test_backend_search(query)
        
        if direct_found and backend_found:
            print("✅ SUCCESS: Both direct API and backend found results")
        elif direct_found and not backend_found:
            print("⚠️  WARNING: Direct API found results but backend didn't")
        elif not direct_found and backend_found:
            print("ℹ️  INFO: Backend found results but direct API didn't")
        else:
            print("❌ FAILURE: Neither found results")
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print('='*80)