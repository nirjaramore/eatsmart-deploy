# EatSmartly System Architecture

## High-Level Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        FLUTTER MOBILE APP                         │
│                     (User Interface Layer)                        │
└────────────────────┬─────────────────────────────────────────────┘
                     │ HTTP REST API
                     │
┌────────────────────▼─────────────────────────────────────────────┐
│                    FASTAPI BACKEND SERVER                         │
│                      (Port 8000)                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              AGENT 4: ORCHESTRATOR                          │ │
│  │  Endpoints: /analyze-barcode, /search, /user/profile       │ │
│  └───┬─────────────────────────────────────────────────────────┘ │
│      │                                                             │
│  ┌───▼───────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │   AGENT 1     │  │   AGENT 2    │  │     AGENT 3         │   │
│  │ DataCollection│  │ WebScraping  │  │ Personalization     │   │
│  └───┬───────────┘  └──┬───────────┘  └─────┬───────────────┘   │
└──────┼─────────────────┼───────────────────┼───────────────────┘
       │                 │                   │
       │                 │                   │
┌──────▼────┐   ┌────────▼──────┐   ┌───────▼─────────┐
│  REDIS    │   │  WEB SCRAPING │   │  POSTGRESQL     │
│  Cache    │   │  - AllRecipes │   │  User Profiles  │
│  (Port    │   │  - BBC Food   │   │  (Port 5432)    │
│   6379)   │   └───────────────┘   └─────────────────┘
└──────┬────┘
       │
┌──────▼──────────┐
│  POSTGRESQL     │
│  Foods Database │
│  (Port 5432)    │
└─────────────────┘
       │
       │
┌──────▼──────────┐
│  USDA FDC API   │
│  500K+ Foods    │
│  (External)     │
└─────────────────┘
```

## Data Flow Diagram

### Barcode Analysis Request

```
STEP 1: User Scans Barcode in Flutter App
    ↓
STEP 2: Flutter sends POST to /analyze-barcode
    {
      "barcode": "012000814204",
      "user_id": "user123"
    }
    ↓
STEP 3: AGENT 4 (Orchestrator) receives request
    ↓
┌─────────────────────────────────────────────────┐
│ STEP 4: AGENT 1 (Data Collection)               │
│  ├─ Check Redis cache for barcode               │
│  │  └─ HIT? Return cached data ✓                │
│  │  └─ MISS? Continue...                        │
│  ├─ Query PostgreSQL for barcode                │
│  │  └─ FOUND? Cache + Return ✓                  │
│  │  └─ NOT FOUND? Continue...                   │
│  └─ Fetch from USDA API                         │
│     └─ Save to DB + Cache + Return ✓            │
└─────────────────────────────────────────────────┘
    ↓
    Food Data: {name, brand, calories, nutrients...}
    ↓
┌─────────────────────────────────────────────────┐
│ STEP 5: AGENT 2 (Web Scraping)                  │
│  ├─ Scrape recipes from AllRecipes              │
│  │  └─ Returns: 3 recipes with links            │
│  ├─ Find healthier alternatives                 │
│  │  └─ Returns: 5 better options                │
│  └─ Generate nutrition tips                     │
│     └─ Returns: Actionable advice               │
└─────────────────────────────────────────────────┘
    ↓
    Enrichment Data: {recipes[], alternatives[], tips[]}
    ↓
┌─────────────────────────────────────────────────┐
│ STEP 6: AGENT 3 (Personalization)               │
│  ├─ Load user profile from PostgreSQL           │
│  │  └─ {allergies, health_goal, conditions}     │
│  ├─ Check allergens in food                     │
│  │  └─ Match? Add ALERT ⚠️                      │
│  ├─ Check health conditions                     │
│  │  └─ Diabetes + High Sugar? WARN ⚠️           │
│  ├─ Check dietary restrictions                  │
│  │  └─ Vegan + Contains Milk? AVOID ❌          │
│  ├─ Calculate health score (0-100)              │
│  └─ Determine verdict: SAFE/CAUTION/AVOID       │
└─────────────────────────────────────────────────┘
    ↓
    Personalized Result: {verdict, score, alerts, suggestions}
    ↓
STEP 7: AGENT 4 combines all data into JSON
    ↓
STEP 8: Return response to Flutter app
    {
      "verdict": "caution",
      "health_score": 65.5,
      "alerts": ["High sugar"],
      "alternatives": [...],
      "recipes": [...]
    }
    ↓
STEP 9: Flutter displays beautiful UI
```

## Database Schema

### Foods Table
```sql
┌─────────────────────────────────────────────────┐
│                  FOODS TABLE                     │
├──────────────┬──────────────────────────────────┤
│ barcode      │ VARCHAR(13) PRIMARY KEY          │
│ name         │ VARCHAR(500)                     │
│ brand        │ VARCHAR(200)                     │
│ serving_size │ FLOAT                            │
│ serving_unit │ VARCHAR(20)                      │
│ calories     │ FLOAT                            │
│ protein_g    │ FLOAT                            │
│ carbs_g      │ FLOAT                            │
│ fat_g        │ FLOAT                            │
│ sodium_mg    │ FLOAT                            │
│ sugar_g      │ FLOAT                            │
│ fiber_g      │ FLOAT                            │
│ allergens    │ VARCHAR(500)                     │
│ ingredients  │ TEXT                             │
│ source       │ VARCHAR(50)                      │
│ created_at   │ TIMESTAMP                        │
│ updated_at   │ TIMESTAMP                        │
└──────────────┴──────────────────────────────────┘
```

### User Profiles Table
```sql
┌──────────────────────────────────────────────────┐
│              USER_PROFILES TABLE                 │
├───────────────────┬──────────────────────────────┤
│ user_id           │ VARCHAR(255) PRIMARY KEY     │
│ age               │ INTEGER                      │
│ gender            │ VARCHAR(20)                  │
│ height_cm         │ FLOAT                        │
│ weight_kg         │ FLOAT                        │
│ activity_level    │ VARCHAR(50)                  │
│ health_goal       │ VARCHAR(100)                 │
│ allergies         │ VARCHAR(500) (comma-sep)     │
│ health_conditions │ VARCHAR(500) (comma-sep)     │
│ dietary_restrictions│ VARCHAR(500) (comma-sep)   │
│ daily_calorie_target│ INTEGER                    │
│ daily_protein_target_g│ FLOAT                    │
│ created_at        │ TIMESTAMP                    │
│ updated_at        │ TIMESTAMP                    │
└───────────────────┴──────────────────────────────┘
```

## Agent Responsibilities

```
┌─────────────────────────────────────────────────────────┐
│  AGENT 1: DATA COLLECTION                               │
├─────────────────────────────────────────────────────────┤
│  INPUT:  Barcode string                                 │
│  OUTPUT: Standardized nutrition data                    │
│                                                          │
│  TOOLS:                                                  │
│  • fetch_from_usda(barcode) → USDA API call            │
│  • get_redis_cache(barcode) → Redis lookup             │
│  • save_redis_cache(barcode, data) → Redis store       │
│  • get_from_database(barcode) → PostgreSQL query       │
│  • save_to_database(barcode, data) → PostgreSQL save   │
│                                                          │
│  FALLBACK CHAIN:                                         │
│  Redis Cache → PostgreSQL → USDA API → Error           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  AGENT 2: WEB SCRAPING                                  │
├─────────────────────────────────────────────────────────┤
│  INPUT:  Food name                                      │
│  OUTPUT: Recipes, alternatives, nutrition tips          │
│                                                          │
│  TOOLS:                                                  │
│  • scrape_recipes(food_name) → Recipe list             │
│  • find_alternatives(food_name, goal) → Better options │
│  • get_nutrition_tips(food_data) → Actionable advice   │
│                                                          │
│  SOURCES:                                                │
│  • AllRecipes.com (4M+ recipes)                         │
│  • BBC Good Food (trusted recipes)                      │
│  • Internal alternatives database (50+ swaps)           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  AGENT 3: PERSONALIZATION                               │
├─────────────────────────────────────────────────────────┤
│  INPUT:  Food data + User profile                       │
│  OUTPUT: Safety verdict + Personalized suggestions      │
│                                                          │
│  TOOLS:                                                  │
│  • get_user_profile(user_id) → User data               │
│  • evaluate_food_safety(food, profile) → Verdict       │
│  • generate_suggestions(food, profile) → Tips          │
│                                                          │
│  CHECKS:                                                 │
│  • Allergen matching (8 major allergens)                │
│  • Health condition filtering                           │
│  • Dietary restriction validation                       │
│  • Health goal alignment                                │
│  • Health score calculation (0-100)                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  AGENT 4: ORCHESTRATOR (FastAPI)                        │
├─────────────────────────────────────────────────────────┤
│  INPUT:  HTTP requests from Flutter                     │
│  OUTPUT: Unified JSON responses                         │
│                                                          │
│  ENDPOINTS:                                              │
│  • POST /analyze-barcode → Full analysis                │
│  • POST /search → Food search                           │
│  • GET /user/{id}/profile → Get profile                 │
│  • POST /user/{id}/profile → Update profile             │
│  • POST /batch-analysis → Multiple barcodes             │
│  • GET /health → System health check                    │
│                                                          │
│  ORCHESTRATION:                                          │
│  Calls Agent 1 → Agent 2 → Agent 3 → Combine results   │
└─────────────────────────────────────────────────────────┘
```

## Deployment Architecture (Future)

```
┌──────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                  │
└──────────────────────────────────────────────────────────┘

              ┌──────────────┐
              │  CloudFlare  │  (CDN, DDoS Protection)
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │   AWS ALB    │  (Load Balancer)
              └──────┬───────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼───┐  ┌────▼───┐  ┌────▼───┐
   │FastAPI │  │FastAPI │  │FastAPI │  (Auto-scaling)
   │Instance│  │Instance│  │Instance│
   └────┬───┘  └────┬───┘  └────┬───┘
        └────────────┼────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
   ┌────▼─────┐            ┌─────▼────┐
   │ AWS RDS  │            │ElastiCache│  (Managed Services)
   │PostgreSQL│            │   Redis   │
   └──────────┘            └───────────┘
```

---

**System designed for scalability, reliability, and cost-efficiency! 🚀**
