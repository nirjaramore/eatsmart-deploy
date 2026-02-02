# EatSmartly Backend: Microsoft AutoGen Copilot Prompt (Local MVP)

**Copy-paste this entire prompt into GitHub Copilot Chat (Ctrl+I in VS Code)**

---

## 🤖 COPILOT PROMPT - COPY & PASTE

```
I'm building EatSmartly - an AI barcode food analyzer using Microsoft AutoGen for multi-agent coordination.

## PROJECT SPEC:
- Language: Python 3.10+
- Framework: FastAPI + Microsoft AutoGen
- Database: PostgreSQL (local via docker-compose)
- Cache: Redis (local via docker-compose)
- Cost: $0 (everything local, free APIs only)

## ARCHITECTURE (Microsoft AutoGen):
Agent 1 (DataCollectionAgent): Fetches food from USDA API + local DB + Redis cache
Agent 2 (WebScrapingAgent): Scrapes recipes & alternatives from AllRecipes, BBC Food
Agent 3 (PersonalizationAgent): Analyzes user health profile, filters recommendations
Agent 4 (OrchestratorAgent): Coordinates all agents, exposes REST API

## TASK: Generate MINIMAL production-ready backend scaffold:

### 1. PROJECT STRUCTURE:
```
eatsmartly-backend/
├── main.py                 # FastAPI entry + AutoGen orchestration
├── config.py              # Env vars (no hardcoding)
├── requirements.txt       # All dependencies
├── Dockerfile            # Single-stage for local dev
├── docker-compose.yml    # PostgreSQL + Redis
├── .env.example          # Template
├── .gitignore           # Python
└── agents/
    ├── data_collection.py    # Agent 1 with tools
    ├── web_scraping.py       # Agent 2 with tools
    ├── personalization.py    # Agent 3 with tools
    └── utils.py             # Shared helpers
```

### 2. DEPENDENCIES (requirements.txt):
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
pydantic==2.5.0
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
pyautogen==0.2.30
google-generativeai==0.3.0
pytest==7.4.3

### 3. FILES TO GENERATE:

**main.py:**
- FastAPI app initialization
- Single health check endpoint: GET /health → {status: healthy}
- Single analysis endpoint: POST /analyze-barcode → calls AutoGen orchestrator
- AutoGen ConversableAgent setup for each agent
- Error handling + basic logging

**config.py:**
- Load env vars: DATABASE_URL, REDIS_URL, GEMINI_API_KEY, etc.
- Pydantic BaseSettings for validation
- No secrets hardcoded

**agents/data_collection.py:**
- AutoGen AssistantAgent for data retrieval
- Tool: fetch_from_usda(barcode) → returns food data
- Tool: fetch_from_db(barcode) → queries PostgreSQL
- Tool: cache_get/cache_set (Redis)
- Fallback chain: cache → db → USDA API

**agents/web_scraping.py:**
- AutoGen AssistantAgent for web enrichment
- Tool: scrape_recipes(food_name) → returns recipe list
- Tool: find_alternatives(food_name, goal) → healthier options
- Error handling for blocked requests
- No persistent storage (just returns data)

**agents/personalization.py:**
- AutoGen AssistantAgent for health filtering
- Tool: load_user_profile(user_id) → returns {allergies, conditions, goals}
- Tool: evaluate_food_safety(food, profile) → {verdict, alerts}
- Tool: generate_suggestions(food, profile) → personalized advice

**agents/utils.py:**
- normalize_barcode(barcode) → UPC-A, EAN-13 validation
- parse_nutrition_response(json) → standardized schema
- log_analysis(user_id, barcode, verdict) → simple file logging

**docker-compose.yml:**
- PostgreSQL 15 service (local, $0 cost)
- Redis service (local, $0 cost)
- Volumes for data persistence
- Network for local container communication

**.env.example:**
DATABASE_URL=postgresql://eatsmartly:password@localhost:5432/eatsmartly
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=your_free_gemini_key
USDA_API_KEY=your_free_usda_key
DEBUG=true

**Dockerfile:**
- Python 3.11 slim base
- Single stage (no multi-stage for speed)
- Copy requirements, install, copy code
- CMD: uvicorn main:app --host 0.0.0.0 --reload

### 4. QUICK SETUP COMMANDS (comment in main.py):
```
# Setup:
# 1. docker-compose up -d
# 2. pip install -r requirements.txt
# 3. python -c "from sqlalchemy import create_engine; create_engine('DATABASE_URL').execute('CREATE TABLE IF NOT EXISTS foods...')"
# 4. uvicorn main:app --reload
# 5. curl http://localhost:8000/health
```

### 5. AUTOGEN AGENT PATTERN:
Each agent uses AutoGen ConversableAgent:
- system_prompt: Clear role definition
- tools: List of callable Python functions
- llm_config: Gemini API (free tier) OR local Ollama
- human_input_mode: "NEVER" (fully autonomous)

### 6. API ENDPOINT PATTERN:
POST /analyze-barcode
Input: {barcode: str, user_id: str}
Flow:
1. Call Agent 1 (fetch food)
2. Pass result to Agent 2 (enrich)
3. Pass to Agent 3 (personalize)
4. Return: {verdict: str, alerts: list, suggestions: list}

### REQUIREMENTS:
- Production-ready error handling
- No print statements (use logging)
- Type hints everywhere
- Docstrings on functions
- No credentials in code (use .env)
- All free APIs (USDA, Gemini free tier)
- Local-only (no AWS yet)

### CODE STYLE:
- PEP 8 compliant
- 88 char line length (Black)
- Type hints with typing module
- Async where it makes sense

OUTPUT: Generate complete working files ready to run locally with docker-compose + uvicorn.
```

---

## 📋 HOW TO USE THIS PROMPT

### Step 1: Open GitHub Copilot
```
VS Code → Copilot Chat (Ctrl+I)
```

### Step 2: Paste the Prompt
Paste the full prompt above (from "I'm building EatSmartly" to the end)

### Step 3: Generate Files
Copilot will generate:
- main.py
- config.py
- requirements.txt
- Dockerfile
- docker-compose.yml
- .env.example
- agents/data_collection.py
- agents/web_scraping.py
- agents/personalization.py
- agents/utils.py

### Step 4: Create Project Structure
```bash
mkdir eatsmartly-backend
cd eatsmartly-backend

# Create folders
mkdir agents

# Create .gitignore
echo "__pycache__/
*.pyc
.env
*.db
.DS_Store" > .gitignore

# Paste files from Copilot into respective locations
```

### Step 5: Run Locally
```bash
# Start containers
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn main:app --reload

# Test
curl http://localhost:8000/health
```

---

## 🎯 WHAT YOU'LL GET

✅ **main.py** - FastAPI with AutoGen orchestration
✅ **config.py** - Environment management (no secrets)
✅ **requirements.txt** - All free dependencies
✅ **docker-compose.yml** - Local PostgreSQL + Redis
✅ **agents/** - 3 AutoGen agents (data, scraping, personalization)
✅ **.env.example** - Configuration template
✅ **Dockerfile** - Container for deployment
✅ **Working health endpoint** - Proof it runs

**Total setup time: 30 minutes**

---

## 💰 COST BREAKDOWN (Local MVP)

| Component | Cost | Notes |
|-----------|------|-------|
| PostgreSQL (local) | $0 | Via docker-compose |
| Redis (local) | $0 | Via docker-compose |
| USDA API | $0 | 10K calls/day free |
| Gemini API | $0 | Free tier (60 req/min) |
| Ollama (local LLM) | $0 | Optional alternative |
| FastAPI | $0 | Open source |
| AutoGen | $0 | Microsoft open source |
| **Total/Month** | **$0** | Everything local |

---

## 🚀 NEXT STEPS AFTER GENERATION

### Week 1 (After Copilot generates scaffold):

1. **Test Local Setup** (30 min)
   ```bash
   docker-compose up
   pip install -r requirements.txt
   uvicorn main:app --reload
   curl http://localhost:8000/health
   ```

2. **Populate Test Data** (1 hour)
   ```python
   # Manual USDA API call to fetch 10 foods
   # Save to PostgreSQL
   python -c "
   import requests
   from sqlalchemy import create_engine, text
   
   # Fetch from USDA FDC API (free, no auth needed)
   r = requests.get('https://fdc.nal.usda.gov/api/v1/foods/search?query=apple&pageSize=10')
   foods = r.json()['foods']
   
   # Save to DB
   engine = create_engine('postgresql://eatsmartly:password@localhost/eatsmartly')
   # Insert logic here
   "
   ```

3. **Test Agent 1 (Data Collection)** (1-2 hours)
   ```bash
   # Mock barcode scan test
   curl -X POST http://localhost:8000/analyze-barcode \
     -H "Content-Type: application/json" \
     -d '{"barcode": "5051379102719", "user_id": "test_user"}'
   
   # Expected: {barcode, food_name, nutrition_data}
   ```

4. **Wire Agent 2 (Web Scraping)** (2-3 hours)
   - Add AllRecipes scraping
   - Test with 5 foods
   - Verify recipe extraction

5. **Wire Agent 3 (Personalization)** (2-3 hours)
   - Create test user profile
   - Test allergen filtering
   - Verify verdict logic

6. **Test Full Pipeline** (1 hour)
   - End-to-end barcode → verdict
   - Verify all agents collaborate

**Total Week 1: ~12 hours of actual coding**

---

## 🔧 TROUBLESHOOTING

### Docker issues:
```bash
# If docker-compose fails:
docker-compose down -v
docker-compose up --build
```

### PostgreSQL connection error:
```bash
# Check connection in .env
DATABASE_URL=postgresql://eatsmartly:password@localhost:5432/eatsmartly

# Verify service running:
docker-compose ps
```

### AutoGen import error:
```bash
# Ensure version matches
pip install pyautogen==0.2.30
```

### USDA API timeout:
```bash
# Add retry logic in agents/utils.py
# Or use Nutritionix as fallback
```

---

## 📊 MVP SUCCESS CRITERIA

After running Copilot prompt + Week 1 implementation:

- [ ] Backend starts: `uvicorn main:app --reload` ✓
- [ ] Health endpoint: `GET /health` returns status
- [ ] Database: PostgreSQL running with tables
- [ ] Agent 1: Fetches food from DB successfully
- [ ] Agent 2: Returns recipes for a test food
- [ ] Agent 3: Personalizes for a test user
- [ ] Full pipeline: Barcode → Verdict in <2 seconds
- [ ] No hardcoded secrets in code
- [ ] Error handling for all edge cases
- [ ] Logging instead of prints

---

## 🎯 AUTOPILOT CHECKLIST

After Copilot generates code, verify:

```
✅ No syntax errors: python -m py_compile agents/*.py
✅ Type checking: python -m mypy main.py (optional)
✅ Lint: python -m flake8 main.py
✅ Docker builds: docker-compose build
✅ Services start: docker-compose up
✅ API responds: curl http://localhost:8000/health
✅ No .env committed: .gitignore includes .env
✅ Requirements complete: pip install -r requirements.txt works
```

---

## 💡 PRO TIPS

1. **Use Ollama for free local LLM** (instead of Gemini if offline):
   ```bash
   # Download Ollama: ollama.ai
   # Run: ollama run llama2
   # In config: LLM_LOCAL=true
   ```

2. **Cache aggressively** (Redis):
   - Cache food data for 24 hours
   - Cache recipes for 48 hours
   - Saves API calls = lower costs

3. **Batch operations**:
   - POST /batch-analyze for multiple barcodes
   - Reduces overhead

4. **Monitor locally**:
   - Simple file-based logging (no third-party)
   - Check `logs/eatsmartly.log`

5. **Database backup**:
   - Regular `pg_dump` to backup food data
   - Keep version controlled

---

## 📝 FIRST COMMIT AFTER GENERATION

```bash
git init
git add .
git commit -m "feat: AutoGen-based EatSmartly backend scaffold

- 4-agent architecture with Microsoft AutoGen
- FastAPI for REST API
- Local PostgreSQL + Redis (docker-compose)
- Free APIs only (USDA, Gemini free tier)
- Zero AWS dependencies (local MVP)
- All configuration via .env"

git remote add origin https://github.com/yourusername/eatsmartly-backend.git
git push -u origin main
```

---

**You're ready. Paste the prompt into Copilot now and watch it generate your backend! 🚀**

Total time to working MVP: 30 min (Copilot) + 12 hours (Week 1) = ~2 days

