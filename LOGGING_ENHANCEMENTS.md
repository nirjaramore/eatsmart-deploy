# Enhanced Logging & Debugging Guide

## 🔍 What Was Added

### Backend Logging Enhancements

#### 1. **Multi-Source Agent Detailed Logging** (`agents/multi_source_agent.py`)
- **Start of search**: Shows barcode being searched with 80-char separator
- **Source-by-source results**: Each API reports its status:
  - ✅ **FOUND**: Shows product name, brand, calories, confidence
  - ❌ **FAILED**: Shows error message (truncated to 100 chars)
  - ❌ **NOT FOUND**: Product not in that database
- **India vs Global tracking**: Open Food Facts tries India endpoint first, logs which one succeeds
- **Emoji-enhanced logs** for easy scanning:
  - 🔍 Search starting
  - 📊 Data source results
  - 🇮🇳 India database query
  - 🌍 Global database query
  - 🇺🇸 USDA query
  - 🏪 Nutritionix query
  - 🌏 Edamam query
  - ✅ Success
  - ❌ Failure

#### 2. **Main API Endpoint Logging** (`main.py`)
- **Request details**: Barcode, user ID, detailed flag
- **Step-by-step progress**:
  - 🚀 STEP 1/4: Initiating orchestrator
  - 🤖 STEP 2/4: Running multi-agent analysis
  - ✅ STEP 3/4: Processing results
  - ✅ STEP 4/4: Response prepared
- **Final summary**:
  - 📊 Data sources used (e.g., "2/4")
  - 🎯 Data confidence level
  - 🔴 Verdict (SAFE/CAUTION/AVOID)
  - 💯 Health score
- **Error logging**:
  - 🚨 Critical error section with 100-char separators
  - 🐞 Error type and message
  - 📊 Barcode that failed
  - Full stack trace

#### 3. **AutoGen Orchestrator Logging** (`agents/autogen_orchestrator.py`)
- **Multi-step workflow tracking**:
  - 📡 STEP 1: Fetching from multiple sources
  - 🌐 STEP 1.5: Trying brand website
  - 🍳 STEP 2: Scraping recipes
  - 👤 STEP 3: Personalized analysis
- **Product found confirmation**: Shows product name immediately
- **Sources checked list**: If not found, shows all 5 sources checked
- **Recipe/tips count**: Shows how many found

#### 4. **Brand Website Scraper** (NEW: `agents/brand_website_scraper.py`)
- **Barcode analysis**: Identifies likely country/brand from barcode prefix
  - `890-894`: Indian products
  - `76`: Swiss (Nestle)
  - `30`: US/Canada
  - `50`: UK
  - `40-43`: German
- **Brand detection**: Extracts brand from product name
  - Maps to official websites
  - Supports: Amul, Britannia, Nestle, ITC, Parle, Haldiram, etc.
- **Website mapping**: Ready for scraping (implementation placeholder)

### Frontend Progress Tracking (`lib/screens/scanner_screen.dart`)

#### 1. **5-Step Progress Indicator**
Shows exactly what's happening:
1. **Scanning barcode**: {barcode number}
2. **Searching Open Food Facts India...**
3. **Checking global food databases...**
4. **Cross-verifying nutrition data...**
5. **Analysis complete!**

#### 2. **Visual Progress**
- Circular progress bar fills from 0% to 100%
- Shows "Step X of 5"
- Displays current action
- Timer reminder: "This may take up to 60 seconds"

#### 3. **Mounted State Safety**
- All `setState()` calls protected with `mounted` checks
- Prevents "setState after dispose" errors
- Safe navigation and error handling

## 📊 How to Read the Logs

### Example: Successful Barcode Scan

```
====================================================================================================
🔍 BARCODE ANALYSIS REQUEST
📊 Barcode: 3017620422003
👤 User ID: test_user
📝 Detailed: True
====================================================================================================
🚀 STEP 1/4: Initiating AutoGen Multi-Agent Orchestrator...
🤖 STEP 2/4: Running multi-agent analysis (this may take 30-60 seconds)...

================================================================================
🔍 STARTING BARCODE SEARCH: 3017620422003
📊 Will query 4 data sources concurrently...
================================================================================

🇮🇳 Querying Open Food Facts (India first, then Global)...
🇺🇸 Querying USDA FoodData Central...
🏪 Querying Nutritionix (Branded Products)...
🌏 Querying Edamam Food Database (Indian + International)...

✅ SUCCESS: Open Food Facts GLOBAL - Nutella
   Countries: France, United States
❌ USDA: NOT FOUND
❌ Nutritionix: API credentials not configured - skipping
❌ Edamam: API credentials not configured - skipping

================================================================================
📋 DATA SOURCE RESULTS:
================================================================================
✅ OPEN_FOOD_FACTS: FOUND - Nutella
   Brand: Ferrero
   Calories: 539 kcal
   Confidence: 0.85
❌ USDA: NOT FOUND
❌ NUTRITIONIX: NOT FOUND
❌ EDAMAM: NOT FOUND
================================================================================

✅ STEP 3/4: Analysis complete, processing results...
📊 Data sources used: 1/4
🎯 Data confidence: High
🔴 Verdict: CAUTION
💯 Health Score: 45/100
✅ STEP 4/4: Response prepared and sent to client
====================================================================================================
```

### Example: Product Not Found

```
🔍 STARTING BARCODE SEARCH: 1234567890123
📊 Will query 4 data sources concurrently...

❌ Open Food Facts: Product 1234567890123 NOT FOUND in any database
❌ USDA: NOT FOUND
❌ Nutritionix: API credentials not configured
❌ Edamam: API credentials not configured

❌ No product data found for barcode: 1234567890123
   Checked: Open Food Facts (India + Global), USDA, Nutritionix, Edamam

🚨 ANALYSIS FAILED: Product not found in any database
====================================================================================================
```

### Example: Error During Processing

```
====================================================================================================
🚨 CRITICAL ERROR IN BARCODE ANALYSIS
🐞 Error Type: TimeoutError
📝 Error Message: Request timeout after 60 seconds
📊 Barcode: 3017620422003
====================================================================================================
[Full stack trace here]
```

## 🎯 What to Look For

### Successful Scan Indicators
- ✅ At least one data source returns FOUND
- Product name appears in logs
- Health score calculated
- Verdict assigned (SAFE/CAUTION/AVOID)
- All 4 steps complete

### Failure Indicators
- ❌ All sources return NOT FOUND
- "Product not found in any database" message
- API credentials missing warnings
- Timeout errors
- Network connection errors

### Performance Metrics
- **Sources found**: Shows how many of 4 APIs returned data
- **Data confidence**: Based on source reliability
- **Processing time**: Should be under 60 seconds

## 🔧 Troubleshooting

### If No Product Found
1. **Check barcode format**: Should be 8-13 digits
2. **Try multiple sources**: Sign up for Edamam/Nutritionix
3. **Check logs** for which specific source might have it
4. **Brand hint**: Logs show country/brand from barcode prefix

### If Slow Response
1. **Check logs** to see which source is slow
2. **Network issues**: Look for timeout messages
3. **API rate limits**: Check for 429 errors

### If App Shows Error
1. **Backend logs**: Check terminal running `uvicorn`
2. **Frontend logs**: Check Flutter console
3. **Network**: Ensure backend is on `http://10.0.2.2:8000` (emulator)
4. **API status**: Check `/health` endpoint

## 📱 Frontend Progress Messages

Users see:
1. "Scanning barcode: 3017620422003"
2. "Searching Open Food Facts India..."
3. "Checking global food databases..."
4. "Cross-verifying nutrition data..."
5. "Analysis complete!"

## 🎨 Log Color Coding (Terminal)

- 🔍 Blue: Search/Query operations
- ✅ Green: Success
- ❌ Red: Failure/Error
- ⚠️ Yellow: Warning
- 📊 Cyan: Data/Metrics
- 🎯 Magenta: Final results

## 📝 New Features

### Brand Website Detection
- Automatically identifies brand from barcode prefix
- Maps known brands to official websites
- Ready for web scraping (placeholder for now)
- Logs which brand website would be checked

### IFCT2017 Integration (Future)
The Indian Food Composition Tables (IFCT2017) PDF you attached can be integrated:
- Extract nutrition data for Indian foods
- Add as 5th data source
- Match by food name/description
- Especially useful for traditional Indian foods

---

**Now when you scan a barcode, you'll see exactly:**
1. ✅ Which APIs are being queried
2. ✅ Which ones found the product
3. ✅ What data each returned
4. ✅ How the final analysis was calculated
5. ✅ Any errors or timeouts

**Check your backend terminal while scanning to see all these detailed logs! 🚀**
