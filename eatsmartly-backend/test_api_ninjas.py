"""
Test API Ninjas nutrition extraction endpoints.
"""
import requests
import json

BASE_URL = "http://192.168.1.4:8000"

def test_analyze_text():
    """Test natural language nutrition extraction."""
    print("\n" + "="*80)
    print("TEST 1: NATURAL LANGUAGE NUTRITION EXTRACTION")
    print("="*80)
    
    queries = [
        "1 cup cooked rice",
        "2 eggs and toast",
        "1lb brisket and fries",
        "grilled chicken breast with mashed potatoes",
        "amul butter sandwich"
    ]
    
    for query in queries:
        print(f"\n📝 Query: {query}")
        print("-" * 80)
        
        response = requests.post(
            f"{BASE_URL}/analyze-text",
            json={"query": query, "user_id": "test_user"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['item_count']} items")
            
            for idx, item in enumerate(data['items'], 1):
                print(f"\n   Item {idx}: {item['name']}")
                print(f"   Serving: {item['serving_size']}")
                print(f"   Calories: {item['nutrition']['calories']}")
                print(f"   Protein: {item['nutrition']['protein_g']}g")
                print(f"   Carbs: {item['nutrition']['carbs_g']}g")
                print(f"   Fat: {item['nutrition']['fat_g']}g")
                print(f"   Health Score: {item['health_score']}/100")
                print(f"   Verdict: {item['verdict'].upper()}")
            
            print(f"\n   📊 TOTAL NUTRITION:")
            total = data['total_nutrition']
            print(f"   Calories: {total['calories']}")
            print(f"   Protein: {total['protein_g']}g")
            print(f"   Carbs: {total['carbs_g']}g")
            print(f"   Fat: {total['fat_g']}g")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.json())


def test_analyze_item():
    """Test single item nutrition with quantity."""
    print("\n" + "="*80)
    print("TEST 2: SINGLE ITEM WITH QUANTITY")
    print("="*80)
    
    items = [
        {"food_item": "rice", "quantity": "1 cup"},
        {"food_item": "butter", "quantity": "2 tbsp"},
        {"food_item": "chicken breast", "quantity": "200g"},
        {"food_item": "milk", "quantity": "1 glass"},
        {"food_item": "banana", "quantity": "1 piece"}
    ]
    
    for item in items:
        print(f"\n🍽️ Item: {item['quantity']} {item['food_item']}")
        print("-" * 80)
        
        response = requests.post(
            f"{BASE_URL}/analyze-item",
            json={
                "food_item": item['food_item'],
                "quantity": item['quantity'],
                "user_id": "test_user"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis complete")
            print(f"   Serving: {data['serving_size']}")
            
            nutrition = data['nutrition']
            print(f"   Calories: {nutrition['calories']}")
            print(f"   Protein: {nutrition['protein_g']}g")
            print(f"   Carbs: {nutrition['carbs_g']}g")
            print(f"   Fat: {nutrition['fat_g']}g")
            print(f"   Sugar: {nutrition['sugar_g']}g")
            print(f"   Fiber: {nutrition['fiber_g']}g")
            print(f"   Sodium: {nutrition['sodium_mg']}mg")
            
            print(f"\n   Health Score: {data['health_score']}/100")
            print(f"   Verdict: {data['verdict'].upper()}")
            print(f"   Risk Level: {data['risk_level'].upper()}")
            
            if data['alerts']:
                print(f"   🚨 Alerts: {', '.join(data['alerts'])}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.json())


def test_recipe_analysis():
    """Test recipe nutrition extraction."""
    print("\n" + "="*80)
    print("TEST 3: RECIPE NUTRITION ANALYSIS")
    print("="*80)
    
    recipe = """
    2 cups flour
    3 eggs
    1 cup milk
    2 tbsp butter
    1 tsp sugar
    """
    
    print(f"\n📝 Recipe:\n{recipe}")
    print("-" * 80)
    
    response = requests.post(
        f"{BASE_URL}/analyze-text",
        json={"query": recipe, "user_id": "test_user"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Recipe contains {data['item_count']} ingredients")
        
        print(f"\n📊 INGREDIENT BREAKDOWN:")
        for idx, item in enumerate(data['items'], 1):
            print(f"\n   {idx}. {item['name']}")
            print(f"      Serving: {item['serving_size']}")
            print(f"      Calories: {item['nutrition']['calories']}")
            print(f"      Health Score: {item['health_score']}/100")
        
        print(f"\n📊 TOTAL RECIPE NUTRITION:")
        total = data['total_nutrition']
        print(f"   Total Calories: {total['calories']}")
        print(f"   Total Protein: {total['protein_g']}g")
        print(f"   Total Carbs: {total['carbs_g']}g")
        print(f"   Total Fat: {total['fat_g']}g")
        print(f"   Total Sugar: {total['sugar_g']}g")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())


if __name__ == "__main__":
    print("\n🧪 TESTING API NINJAS NUTRITION EXTRACTION")
    print("="*80)
    print("This tests natural language processing for nutrition data")
    print("="*80)
    
    test_analyze_text()
    test_analyze_item()
    test_recipe_analysis()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETE")
    print("="*80)
    print("\nAPI Ninjas Integration Benefits:")
    print("  ✓ Natural language understanding (no need for exact food names)")
    print("  ✓ Automatic portion scaling (handles cups, tbsp, lbs, etc.)")
    print("  ✓ Multi-item extraction (recipes, meals, menus)")
    print("  ✓ Comprehensive nutrition data (10+ nutrients)")
    print("  ✓ Works alongside barcode scanning for complete coverage")
    print("="*80 + "\n")
