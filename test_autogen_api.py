import requests
import json

print("\n" + "="*60)
print("TESTING AUTOGEN MULTI-SOURCE ANALYSIS")
print("="*60 + "\n")

try:
    response = requests.post(
        'http://localhost:3000/analyze-barcode',
        json={
            'barcode': '3017620422003',
            'user_id': 'test',
            'detailed': True
        },
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ MULTI-SOURCE ANALYSIS COMPLETE\n")
        print(f"Product: {data.get('food_name')}")
        print(f"Brand: {data.get('brand')}")
        
        nutrition = data.get('detailed_nutrition', {})
        print(f"Calories: {nutrition.get('calories')} kcal")
        print(f"Protein: {nutrition.get('protein_g')} g")
        print(f"Carbs: {nutrition.get('carbs_g')} g")
        print(f"Fat: {nutrition.get('fat_g')} g")
        
        print(f"\nData Quality:")
        print(f"  Sources found: {nutrition.get('data_sources')}/3")
        print(f"  Confidence: {nutrition.get('data_confidence')}")
        print(f"  Variance: {nutrition.get('data_variance')}%")
        
        print(f"\nHealth Assessment:")
        print(f"  Verdict: {data.get('verdict')}")
        print(f"  Health Score: {data.get('health_score')}/100")
        print(f"  Warnings: {len(data.get('warnings', []))}")
        
        print(f"\nRecipes found: {len(data.get('recipes', []))}")
        print(f"Alternatives: {len(data.get('alternatives', []))}")
        
        print("\n" + "="*60)
        print("✅ SUCCESS! AutoGen multi-source system is working!")
        print("="*60)
        
    else:
        print(f"❌ Error: HTTP {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
