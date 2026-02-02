"""
Test to verify barcode scanning and search return the same data.
"""
import requests
import json

BASE_URL = "http://192.168.1.4:8000"

def test_search():
    """Test search functionality."""
    print("\n" + "="*80)
    print("TESTING SEARCH FUNCTIONALITY")
    print("="*80)
    
    response = requests.post(
        f"{BASE_URL}/search",
        json={"query": "amul", "user_id": "test_user", "limit": 3}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    data = response.json()
    print(f"\nSearch Results for 'amul':")
    print(f"Count: {data.get('count', 0)}")
    
    results = data.get('results', [])
    for idx, product in enumerate(results, 1):
        print(f"\n{idx}. {product.get('name')} ({product.get('brand')})")
        print(f"   Barcode: {product.get('barcode')}")
        print(f"   Calories: {product.get('calories')}")
        print(f"   Protein: {product.get('protein_g')}g")
        print(f"   Sugar: {product.get('sugar_g')}g")
        
    return results

def test_barcode(barcode):
    """Test barcode analysis."""
    print("\n" + "="*80)
    print(f"TESTING BARCODE ANALYSIS: {barcode}")
    print("="*80)
    
    response = requests.post(
        f"{BASE_URL}/analyze-barcode",
        json={
            "barcode": barcode,
            "user_id": "test_user",
            "detailed": True
        }
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nProduct: {data.get('food_name')} ({data.get('brand')})")
        print(f"Health Score: {data.get('health_score')}/100")
        print(f"Verdict: {data.get('verdict').upper()}")
        
        if data.get('detailed_nutrition'):
            nutrition = data['detailed_nutrition']
            print(f"\nNutrition:")
            print(f"   Calories: {nutrition.get('calories')}")
            print(f"   Protein: {nutrition.get('protein_g')}g")
            print(f"   Carbs: {nutrition.get('carbs_g')}g")
            print(f"   Fat: {nutrition.get('fat_g')}g")
            print(f"   Sugar: {nutrition.get('sugar_g')}g")
            print(f"   Sodium: {nutrition.get('sodium_mg')}mg")
            
        return data
    else:
        print(f"ERROR: {response.json()}")
        return None

if __name__ == "__main__":
    print("\n🧪 TESTING BARCODE VS SEARCH DATA CONSISTENCY")
    print("="*80)
    
    # First, search for products
    search_results = test_search()
    
    # Then test barcode analysis on the same products
    if search_results:
        for product in search_results[:2]:  # Test first 2 products
            barcode = product.get('barcode')
            if barcode:
                barcode_data = test_barcode(barcode)
                
                # Compare data
                print("\n" + "-"*80)
                print("DATA COMPARISON:")
                print("-"*80)
                print(f"Search - Calories: {product.get('calories')}")
                if barcode_data and barcode_data.get('detailed_nutrition'):
                    print(f"Barcode - Calories: {barcode_data['detailed_nutrition'].get('calories')}")
                    if product.get('calories') == barcode_data['detailed_nutrition'].get('calories'):
                        print("✅ MATCH: Data is consistent!")
                    else:
                        print("❌ MISMATCH: Data differs between search and barcode!")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
