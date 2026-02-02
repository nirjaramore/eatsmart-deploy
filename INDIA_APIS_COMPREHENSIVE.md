# 🇮🇳 INDIA-SPECIFIC FOOD DATA SOURCES

## ✅ FREE & OFFICIAL SOURCES

### 1. **Open Food Facts India** ⭐⭐⭐ (BEST - Already Integrated)
```
API: https://in.openfoodfacts.org/api/v0/product/{barcode}.json
Coverage: 50,000+ Indian products
Cost: FREE
Auth: None needed
```

**How to use:**
```python
# Modify current Open Food Facts to prefer India data
url = f"https://in.openfoodfacts.org/api/v0/product/{barcode}.json"
# Falls back to world database if not in India subset
```

### 2. **FSSAI FoSCoS Portal** ⭐⭐⭐ (OFFICIAL INDIA)
```
Website: https://foscos.fssai.gov.in/
Coverage: ALL licensed food businesses in India
Cost: FREE
Auth: Registration required
Type: Web scraping / Manual lookup
```

**Data Available:**
- Food product approvals
- Manufacturer details
- License numbers
- Compliance status

### 3. **BigBasket API** ⭐⭐ (E-commerce Data)
```
Type: Unofficial / Web scraping
Coverage: 40,000+ products sold in India
Cost: FREE (scraping)
```

**Scraping approach:**
```python
def search_bigbasket(product_name):
    url = f"https://www.bigbasket.com/ps/?q={product_name}"
    # Parse product nutrition from listings
```

### 4. **JioMart API** ⭐ (E-commerce Data)
```
Website: https://www.jiomart.com/
Coverage: 50,000+ Indian products
Type: Web scraping
```

### 5. **India Brand Equity Foundation (IBEF)** ⭐
```
Website: https://www.ibef.org/
Type: Market research data
Coverage: Top Indian brands
```

---

## 🔧 READY-TO-USE APIS

### 6. **Edamam Food Database API** ⭐⭐⭐
```
API: https://api.edamam.com/api/food-database/v2
Coverage: International + some Indian foods
Cost: FREE tier (100 calls/month), Paid plans available
Auth: API key required
```

**Sign up:** https://developer.edamam.com/

**Example:**
```python
import requests

API_KEY = "your_key"
APP_ID = "your_id"

url = f"https://api.edamam.com/api/food-database/v2/parser"
params = {
    "app_id": APP_ID,
    "app_key": API_KEY,
    "ingr": "rice",
    "nutrition-type": "cooking"
}

response = requests.get(url, params=params)
```

### 7. **Spoonacular API** ⭐⭐
```
API: https://api.spoonacular.com/
Coverage: 380,000+ foods (some Indian)
Cost: FREE tier (150 calls/day)
Auth: API key required
```

**Sign up:** https://spoonacular.com/food-api

### 8. **FatSecret Platform API** ⭐⭐
```
API: https://platform.fatsecret.com/api/
Coverage: Large food database
Cost: FREE for non-commercial
Auth: OAuth required
```

---

## 🇮🇳 INDIAN E-COMMERCE DATA (Web Scraping)

### 9. **Amazon India**
```python
def get_amazon_india_product(barcode):
    search_url = f"https://www.amazon.in/s?k={barcode}"
    # Parse nutrition from product page
```

### 10. **Flipkart**
```python
def get_flipkart_product(barcode):
    search_url = f"https://www.flipkart.com/search?q={barcode}"
    # Parse nutrition info
```

### 11. **Blinkit (formerly Grofers)**
```python
def get_blinkit_product(barcode):
    search_url = f"https://blinkit.com/search?q={barcode}"
    # Parse nutrition
```

---

## 📊 RECOMMENDED IMPLEMENTATION STRATEGY

### **Tier 1: Official & Free (Implement First)**
1. Open Food Facts India (Already done ✓)
2. USDA FoodData Central (Already done ✓)
3. Edamam API (Add this - good coverage)

### **Tier 2: E-commerce Scraping (Week 2)**
1. BigBasket scraping
2. Amazon India scraping
3. JioMart scraping

### **Tier 3: Premium APIs (Optional)**
1. Spoonacular (150 free calls/day)
2. Nutritionix (if you upgrade)
3. FatSecret

---

## 🚀 QUICK WINS - ADD THESE NOW:

### **1. Edamam API Integration**
```python
# Add to .env
EDAMAM_APP_ID=your_app_id
EDAMAM_API_KEY=your_api_key

# Add to multi_source_agent.py
async def _fetch_edamam(self, query):
    url = "https://api.edamam.com/api/food-database/v2/parser"
    params = {
        "app_id": os.getenv("EDAMAM_APP_ID"),
        "app_key": os.getenv("EDAMAM_API_KEY"),
        "ingr": query,
        "nutrition-type": "cooking"
    }
    response = await loop.run_in_executor(
        None,
        lambda: requests.get(url, params=params, timeout=10)
    )
    # Parse response
```

### **2. Open Food Facts India Preference**
```python
# Modify existing Open Food Facts to prefer India
async def _fetch_open_food_facts(self, barcode):
    # Try India-specific first
    india_url = f"https://in.openfoodfacts.org/api/v0/product/{barcode}.json"
    world_url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    
    # Try India first, fallback to world
    for url in [india_url, world_url]:
        response = await loop.run_in_executor(...)
        if data.get("status") == 1:
            return result
```

### **3. BigBasket Web Scraping**
```python
async def _fetch_bigbasket(self, product_name):
    url = f"https://www.bigbasket.com/ps/?q={product_name}"
    response = await loop.run_in_executor(
        None,
        lambda: requests.get(url, headers=self.headers, timeout=10)
    )
    soup = BeautifulSoup(response.content, 'html.parser')
    # Extract nutrition from product cards
```

---

## 📝 FREE API CREDENTIALS TO GET:

1. **Edamam:** https://developer.edamam.com/
   - Free tier: 100 calls/month
   - Good for Indian foods lookup

2. **Spoonacular:** https://spoonacular.com/food-api
   - Free tier: 150 calls/day
   - Recipe alternatives

3. **FatSecret:** https://platform.fatsecret.com/api/
   - Free for non-commercial
   - Large food database

---

## 🎯 PRIORITY ORDER FOR INDIA:

```
1. ✅ Open Food Facts India (Already working)
2. ✅ USDA (Already working)
3. 🆕 Edamam (Add today - 5 mins)
4. 🆕 Open Food Facts India-specific endpoint (Modify existing)
5. 🆕 BigBasket scraping (Week 2)
6. 🆕 Amazon India scraping (Week 2)
```

---

## 📊 EXPECTED COVERAGE AFTER ADDING THESE:

| Source | Indian Products | International | Status |
|--------|----------------|---------------|---------|
| Open Food Facts India | 50,000+ | N/A | ✅ Working |
| USDA | Limited | 1M+ | ✅ Working |
| Edamam | 10,000+ | 800K+ | 🆕 Add today |
| BigBasket Scraping | 40,000+ | N/A | 🆕 Week 2 |
| Amazon India | 100,000+ | N/A | 🆕 Week 2 |

**Total Coverage: 200,000+ Indian products** after full implementation!

---

## ⚡ IMPLEMENT TODAY (30 minutes):

```bash
# 1. Sign up for Edamam
# Visit: https://developer.edamam.com/

# 2. Add to .env
EDAMAM_APP_ID=your_app_id
EDAMAM_API_KEY=your_api_key

# 3. Modify multi_source_agent.py (I'll do this for you)

# 4. Test with Indian food
python -c "import asyncio; from agents.multi_source_agent import MultiSourceDataAgent; agent = MultiSourceDataAgent(); asyncio.run(agent.fetch_from_all_sources('dal'))"
```

This will give you **4 active data sources** with strong India coverage!
