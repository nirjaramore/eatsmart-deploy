"""
Test the new health scoring system with various products
"""
from agents.utils import calculate_health_score
from agents.personalization import PersonalizationAgent

# Test different food profiles
test_foods = [
    {
        "name": "Amul Butter",
        "nutrition": {
            "calories": 724,
            "protein_g": 1,
            "carbs_g": 0,
            "fat_g": 80,
            "saturated_fat_g": 48,
            "sodium_mg": 500,
            "sugar_g": 0,
            "fiber_g": 0
        }
    },
    {
        "name": "Apple (Fresh)",
        "nutrition": {
            "calories": 52,
            "protein_g": 0.3,
            "carbs_g": 14,
            "fat_g": 0.2,
            "saturated_fat_g": 0,
            "sodium_mg": 1,
            "sugar_g": 10,
            "fiber_g": 2.4
        }
    },
    {
        "name": "Coca Cola",
        "nutrition": {
            "calories": 42,
            "protein_g": 0,
            "carbs_g": 10.6,
            "fat_g": 0,
            "saturated_fat_g": 0,
            "sodium_mg": 11,
            "sugar_g": 10.6,
            "fiber_g": 0
        }
    },
    {
        "name": "Chicken Breast (Grilled)",
        "nutrition": {
            "calories": 165,
            "protein_g": 31,
            "carbs_g": 0,
            "fat_g": 3.6,
            "saturated_fat_g": 1,
            "sodium_mg": 74,
            "sugar_g": 0,
            "fiber_g": 0
        }
    },
    {
        "name": "Maggi Noodles",
        "nutrition": {
            "calories": 400,
            "protein_g": 9,
            "carbs_g": 62,
            "fat_g": 12,
            "saturated_fat_g": 6,
            "sodium_mg": 1200,
            "sugar_g": 3,
            "fiber_g": 2
        }
    },
    {
        "name": "Parle-G Biscuits",
        "nutrition": {
            "calories": 455,
            "protein_g": 6.7,
            "carbs_g": 75.6,
            "fat_g": 13.3,
            "saturated_fat_g": 6.7,
            "sodium_mg": 267,
            "sugar_g": 26.7,
            "fiber_g": 1.3
        }
    },
    {
        "name": "Oats (Plain)",
        "nutrition": {
            "calories": 389,
            "protein_g": 16.9,
            "carbs_g": 66.3,
            "fat_g": 6.9,
            "saturated_fat_g": 1.2,
            "sodium_mg": 2,
            "sugar_g": 1,
            "fiber_g": 10.6
        }
    }
]

print("="*80)
print("HEALTH SCORE ANALYSIS")
print("="*80)
print("\nScoring System:")
print("  70-100: SAFE (Green) - Healthy choice")
print("  43-69:  CAUTION (Yellow) - Okay in moderation")
print("  0-42:   AVOID (Red) - Unhealthy choice")
print("\n" + "="*80)

agent = PersonalizationAgent()
default_profile = agent._get_default_profile("test_user")

for food in test_foods:
    name = food["name"]
    nutrition = food["nutrition"]
    
    # Calculate health score
    score = calculate_health_score(nutrition)
    
    # Get full evaluation
    evaluation = agent.evaluate_food_safety(nutrition, default_profile)
    
    # Determine color
    if score >= 70:
        color = "🟢 SAFE"
    elif score >= 43:
        color = "🟡 CAUTION"
    else:
        color = "🔴 AVOID"
    
    print(f"\n{name}")
    print(f"  Score: {score:.1f}/100 - {color}")
    print(f"  Verdict: {evaluation['verdict'].upper()}")
    
    # Show nutrition breakdown
    print(f"  Nutrition (per 100g):")
    print(f"    Calories: {nutrition['calories']} kcal")
    print(f"    Protein: {nutrition['protein_g']}g | Fiber: {nutrition['fiber_g']}g")
    print(f"    Sugar: {nutrition['sugar_g']}g | Sodium: {nutrition['sodium_mg']}mg")
    print(f"    Saturated Fat: {nutrition['saturated_fat_g']}g")
    
    if evaluation['warnings']:
        print(f"  Warnings:")
        for warning in evaluation['warnings']:
            print(f"    {warning}")

print("\n" + "="*80)
