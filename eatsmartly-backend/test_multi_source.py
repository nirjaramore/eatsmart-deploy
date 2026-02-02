"""
Test Multi-Source Data Collection with AutoGen
Tests all 3 APIs: Open Food Facts, USDA, Nutritionix
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.multi_source_agent import MultiSourceDataAgent


async def test_multi_source():
    """Test multi-source data collection."""
    
    print("="*80)
    print("TESTING MULTI-SOURCE DATA COLLECTION")
    print("="*80)
    print()
    
    agent = MultiSourceDataAgent()
    
    # Test with a well-known product (Nutella)
    test_barcode = "3017620422003"
    
    print(f"Testing with barcode: {test_barcode} (Nutella)")
    print()
    print("Querying all sources...")
    print("-" * 80)
    
    result = await agent.fetch_from_all_sources(test_barcode)
    
    # Display results from each source
    sources = result.get("sources", {})
    
    print("\n📊 DATA FROM EACH SOURCE:\n")
    
    for source_name, source_data in sources.items():
        print(f"🔍 {source_name.upper().replace('_', ' ')}:")
        
        if source_data:
            print(f"   ✅ Found!")
            print(f"   Name: {source_data.get('name')}")
            print(f"   Brand: {source_data.get('brand')}")
            print(f"   Calories: {source_data.get('calories')} kcal/100g")
            print(f"   Protein: {source_data.get('protein_g')} g")
            print(f"   Carbs: {source_data.get('carbs_g')} g")
            print(f"   Fat: {source_data.get('fat_g')} g")
            print(f"   Confidence: {source_data.get('confidence', 0)*100:.0f}%")
        else:
            print(f"   ❌ Not found")
        
        print()
    
    # Display consensus
    consensus = result.get("consensus")
    
    if consensus:
        print("\n" + "="*80)
        print("✨ CONSENSUS DATA (Combined from all sources):")
        print("="*80)
        print(f"\nProduct: {consensus.get('name')}")
        print(f"Brand: {consensus.get('brand')}")
        print(f"\nNutrition (per 100g):")
        print(f"  Calories: {consensus.get('calories')} kcal")
        print(f"  Protein: {consensus.get('protein_g')} g")
        print(f"  Carbs: {consensus.get('carbs_g')} g")
        print(f"  Fat: {consensus.get('fat_g')} g")
        print(f"  Sugar: {consensus.get('sugar_g')} g")
        print(f"  Sodium: {consensus.get('sodium_mg')} mg")
        
        print(f"\nData Quality:")
        print(f"  Sources used: {', '.join(consensus.get('sources_used', []))}")
        print(f"  Data variance: {consensus.get('data_variance', 0):.1f}%")
        print(f"  Method: {consensus.get('consensus_method')}")
        
        if consensus.get('data_variance', 0) < 5:
            print(f"  Quality: 🟢 Excellent (all sources agree)")
        elif consensus.get('data_variance', 0) < 15:
            print(f"  Quality: 🟡 Good (minor variations)")
        else:
            print(f"  Quality: 🔴 Fair (significant variations)")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    
    # Test with another product
    print("\n\n")
    print("="*80)
    print("TESTING WITH COCA-COLA")
    print("="*80)
    print()
    
    coca_cola_barcode = "5449000000996"
    result2 = await agent.fetch_from_all_sources(coca_cola_barcode)
    
    sources2 = result2.get("sources", {})
    found_count = len([s for s in sources2.values() if s is not None])
    
    print(f"Barcode: {coca_cola_barcode}")
    print(f"Sources found: {found_count}/3")
    
    for source_name, source_data in sources2.items():
        if source_data:
            print(f"  ✅ {source_name}: {source_data.get('name')}")
        else:
            print(f"  ❌ {source_name}: Not found")
    
    consensus2 = result2.get("consensus")
    if consensus2:
        print(f"\nConsensus Product: {consensus2.get('name')}")
        print(f"Calories: {consensus2.get('calories')} kcal/100g")
        print(f"Data variance: {consensus2.get('data_variance', 0):.1f}%")


if __name__ == "__main__":
    print("\n🚀 Starting Multi-Source API Test\n")
    print("This will query:")
    print("  1. Open Food Facts (FREE)")
    print("  2. USDA FoodData Central (requires API key)")
    print("  3. Nutritionix (requires API key)")
    print()
    
    asyncio.run(test_multi_source())
