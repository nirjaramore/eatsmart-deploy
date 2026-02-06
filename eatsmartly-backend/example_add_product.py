"""
Example: How to add products with nutrition data using add_products_supabase.py

This demonstrates the consolidated approach for adding products with nutrition facts.
"""
from add_products_supabase import add_product_with_nutrition

# Example 1: Add Organic Quinoa Flour with full nutrition data
if __name__ == '__main__':
    product = {
        'product_name': 'Organic Quinoa Flour',
        'brand': 'Organic Tattva',
        'category': 'Flour & Grains',
        'manufacturer': 'MEHROTRA CONSUMER PRODUCTS PVT. LTD.',
        'region': 'Greater Noida, Uttar Pradesh',
        'weight': '500gm',
        'fssai_license': '10019130069',
        'image_url': 'https://organictattva.com/cdn/shop/files/quinoapowder.jpg'
    }
    
    nutrition = {
        'serving_size': '100g',
        'servings_per_container': 5,
        'calories': 387,
        'total_fat': 3.22,
        'saturated_fat': 0.73,
        'trans_fat': 0.005,
        'cholesterol': 0.10,
        'sodium': 4.26,
        'total_carbohydrates': 84.58,
        'dietary_fiber': 5.15,
        'total_sugars': 0.65,
        'added_sugars': 0.00,
        'protein': 2.47,
        'confidence': 'manual'
    }
    
    # Add product with nutrition
    result = add_product_with_nutrition(product, nutrition)
    
    if result:
        print(f"\n✅ Successfully added product!")
        print(f"   Product ID: {result['product']['id']}")
        if result['nutrition']:
            print(f"   Nutrition ID: {result['nutrition']['id']}")
