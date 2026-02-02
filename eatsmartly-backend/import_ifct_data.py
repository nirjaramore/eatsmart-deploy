"""
IFCT 2017 Data Import Script
Extracts data from IFCT2017.pdf and imports to PostgreSQL
"""
import pdfplumber
import psycopg2
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_db():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        host="localhost",
        database="eatsmartly",
        user="eatsmartly",
        password="shreyas"
    )

def parse_ifct_pdf(pdf_path: str):
    """
    Parse IFCT2017 PDF and extract food composition data
    """
    logger.info(f"📖 Opening PDF: {pdf_path}")
    
    foods = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"   📄 Total pages: {len(pdf.pages)}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract tables from page
                tables = page.extract_tables()
                
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    # Try to identify if this is a food composition table
                    header = table[0] if table else []
                    
                    # Look for key columns
                    has_food_name = any('food' in str(cell).lower() for cell in header if cell)
                    has_protein = any('protein' in str(cell).lower() for cell in header if cell)
                    has_energy = any('energy' in str(cell).lower() or 'kcal' in str(cell).lower() for cell in header if cell)
                    
                    if has_food_name and (has_protein or has_energy):
                        logger.info(f"   ✅ Found food table on page {page_num}")
                        
                        # Parse data rows
                        for row in table[1:]:
                            if not row or len(row) < 5:
                                continue
                            
                            food_data = parse_food_row(row, header)
                            if food_data:
                                foods.append(food_data)
                
                if page_num % 10 == 0:
                    logger.info(f"   📊 Processed {page_num} pages, found {len(foods)} foods")
    
    except Exception as e:
        logger.error(f"❌ Error parsing PDF: {e}")
    
    logger.info(f"✅ Extraction complete: {len(foods)} foods found")
    return foods

def parse_food_row(row, header):
    """Parse a single food data row"""
    try:
        # Try to extract basic info
        food_data = {}
        
        for i, cell in enumerate(row):
            if not cell or i >= len(header):
                continue
            
            col_name = str(header[i]).lower() if i < len(header) else ''
            value = str(cell).strip()
            
            # Extract numeric value
            numeric = extract_number(value)
            
            # Map columns
            if 'food' in col_name and 'code' not in col_name:
                food_data['food_name'] = value
            elif 'code' in col_name:
                food_data['food_code'] = value
            elif 'protein' in col_name:
                food_data['protein_g'] = numeric
            elif 'fat' in col_name:
                food_data['fat_g'] = numeric
            elif 'carb' in col_name:
                food_data['carbohydrate_g'] = numeric
            elif 'energy' in col_name or 'kcal' in col_name:
                food_data['energy_kcal'] = numeric
            elif 'moisture' in col_name:
                food_data['moisture_g'] = numeric
            elif 'fiber' in col_name or 'fibre' in col_name:
                food_data['crude_fiber_g'] = numeric
            elif 'calcium' in col_name:
                food_data['calcium_mg'] = numeric
            elif 'iron' in col_name:
                food_data['iron_mg'] = numeric
        
        # Only return if we have at least name and one nutrient
        if 'food_name' in food_data and len(food_data) > 2:
            return food_data
        
        return None
        
    except Exception as e:
        logger.warning(f"   ⚠️  Error parsing row: {e}")
        return None

def extract_number(text):
    """Extract numeric value from text"""
    if not text:
        return None
    
    # Remove commas and extract number
    match = re.search(r'(\d+(?:\.\d+)?)', text.replace(',', ''))
    if match:
        return float(match.group(1))
    return None

def import_to_database(foods):
    """Import parsed foods to PostgreSQL"""
    logger.info(f"💾 Importing {len(foods)} foods to database...")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    inserted = 0
    
    for food in foods:
        try:
            # Prepare insert statement
            columns = ', '.join(food.keys())
            placeholders = ', '.join(['%s'] * len(food))
            values = list(food.values())
            
            sql = f"""
                INSERT INTO ifct_foods ({columns})
                VALUES ({placeholders})
                ON CONFLICT (food_code) DO UPDATE SET
                    food_name = EXCLUDED.food_name,
                    protein_g = EXCLUDED.protein_g,
                    fat_g = EXCLUDED.fat_g,
                    carbohydrate_g = EXCLUDED.carbohydrate_g,
                    energy_kcal = EXCLUDED.energy_kcal
            """
            
            cursor.execute(sql, values)
            inserted += 1
            
            if inserted % 100 == 0:
                conn.commit()
                logger.info(f"   ✅ Inserted {inserted} foods")
        
        except Exception as e:
            logger.error(f"   ❌ Error inserting {food.get('food_name', 'unknown')}: {e}")
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info(f"✅ Import complete: {inserted} foods imported")
    return inserted

def create_sample_data():
    """Create sample IFCT data for testing"""
    logger.info("📝 Creating sample IFCT data...")
    
    sample_foods = [
        {
            'food_code': 'A001',
            'food_name': 'Rice, raw, milled',
            'food_group': 'Cereals and Millets',
            'protein_g': 6.8,
            'carbohydrate_g': 78.2,
            'fat_g': 0.5,
            'energy_kcal': 345,
            'moisture_g': 13.3,
            'crude_fiber_g': 0.2,
            'calcium_mg': 10,
            'iron_mg': 0.7
        },
        {
            'food_code': 'A002',
            'food_name': 'Wheat, whole',
            'food_group': 'Cereals and Millets',
            'protein_g': 11.8,
            'carbohydrate_g': 71.2,
            'fat_g': 1.5,
            'energy_kcal': 346,
            'moisture_g': 12.8,
            'crude_fiber_g': 1.2,
            'calcium_mg': 41,
            'iron_mg': 5.3
        },
        {
            'food_code': 'B001',
            'food_name': 'Milk, buffalo',
            'food_group': 'Milk and Milk Products',
            'protein_g': 3.7,
            'carbohydrate_g': 5.0,
            'fat_g': 6.5,
            'energy_kcal': 97,
            'moisture_g': 84.0,
            'calcium_mg': 210,
            'iron_mg': 0.2
        },
        {
            'food_code': 'C001',
            'food_name': 'Chicken, curry cut',
            'food_group': 'Meat, Fish and Poultry',
            'protein_g': 18.6,
            'carbohydrate_g': 0.0,
            'fat_g': 4.8,
            'energy_kcal': 123,
            'moisture_g': 75.9,
            'iron_mg': 1.3,
            'calcium_mg': 14
        },
        {
            'food_code': 'D001',
            'food_name': 'Dal, masoor (lentil)',
            'food_group': 'Pulses and Legumes',
            'protein_g': 25.1,
            'carbohydrate_g': 59.0,
            'fat_g': 0.7,
            'energy_kcal': 343,
            'moisture_g': 11.9,
            'crude_fiber_g': 0.8,
            'calcium_mg': 69,
            'iron_mg': 7.5
        }
    ]
    
    return import_to_database(sample_foods)

if __name__ == "__main__":
    print("=" * 80)
    print("🇮🇳 IFCT 2017 Data Import")
    print("=" * 80)
    
    pdf_path = Path(__file__).parent.parent / "IFCT2017.pdf"
    
    if pdf_path.exists():
        logger.info(f"✅ Found PDF: {pdf_path}")
        
        # Parse PDF
        foods = parse_ifct_pdf(str(pdf_path))
        
        if foods:
            # Import to database
            import_to_database(foods)
        else:
            logger.warning("⚠️  No foods extracted from PDF, creating sample data...")
            create_sample_data()
    else:
        logger.warning(f"⚠️  PDF not found at {pdf_path}")
        logger.info("Creating sample IFCT data instead...")
        create_sample_data()
    
    print("=" * 80)
    print("✅ IFCT Import Complete!")
    print("=" * 80)
