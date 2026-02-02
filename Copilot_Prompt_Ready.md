# 🤖 GITHUB COPILOT: COPY-PASTE DIRECTLY

**Ctrl+I in VS Code → Paste below → Generate**

---

```
I'm building EatSmartly - AI barcode food analyzer using Microsoft AutoGen.

PROJECT: Python FastAPI + AutoGen (4 agents) + Local PostgreSQL/Redis. $0 cost.

GENERATE 11 FILES (production-ready, concise, no pseudo-code):

=== FILE 1: main.py ===
- FastAPI app initialization
- GET /health → {status: "healthy"}
- POST /analyze-barcode {barcode: str, user_id: str} → calls AutoGen orchestrator
- Setup 3 AutoGen ConversableAgents (data_agent, scrape_agent, personalize_agent)
- Orchestrator agent that chains all 3 and returns {verdict, alerts, suggestions}
- Basic logging (not prints), error handling

=== FILE 2: config.py ===
- Pydantic BaseSettings from .env
- DATABASE_URL, REDIS_URL, GEMINI_API_KEY, USDA_API_KEY
- Type hints, validation

=== FILE 3: agents/data_collection.py ===
- AutoGen AssistantAgent named "DataCollectionAgent"
- System prompt: "Fetch food data from USDA, cache, or local DB. Return normalized nutrition."
- Tools:
  1. fetch_usda_food(barcode) → calls https://fdc.nal.usda.gov/api/v1/foods/search
  2. get_redis_cache(barcode) → Redis lookup
  3. save_redis_cache(barcode, data) → Redis store (24h TTL)
- Tool implementations: Python functions, not stubs

=== FILE 4: agents/web_scraping.py ===
- AutoGen AssistantAgent named "WebScrapingAgent"
- System prompt: "Enrich food with recipes and healthier alternatives via web scraping."
- Tools:
  1. scrape_recipes(food_name) → beautifulsoup4, AllRecipes/BBC Food
  2. find_alternatives(food_name, health_goal) → returns list of better options
- Use try/except for blocked requests, no prints

=== FILE 5: agents/personalization.py ===
- AutoGen AssistantAgent named "PersonalizationAgent"
- System prompt: "Filter food based on user allergies, health conditions, goals."
- Tools:
  1. evaluate_food_safety(food_dict, user_allergies, user_conditions) → {safe: bool, alerts: list}
  2. generate_verdict(evaluation_result) → returns "Safe" OR "Caution" OR "Risky"
  3. create_suggestions(food, user_profile) → list of personalized actions
- Return structured data, not free text

=== FILE 6: agents/utils.py ===
- normalize_barcode(barcode: str) → validates UPC-A/EAN-13, returns standardized format
- parse_nutrition(api_response) → returns {name, calories, protein, carbs, fat, sodium, sugar, allergens}
- Logger setup (logging module, not print)

=== FILE 7: requirements.txt ===
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

=== FILE 8: docker-compose.yml ===
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: eatsmartly
      POSTGRES_PASSWORD: password
      POSTGRES_DB: eatsmartly
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:

=== FILE 9: .env.example ===
DATABASE_URL=postgresql://eatsmartly:password@localhost:5432/eatsmartly
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=your_free_gemini_api_key
USDA_API_KEY=your_free_usda_key
DEBUG=true

=== FILE 10: Dockerfile ===
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

=== FILE 11: .gitignore ===
__pycache__/
*.pyc
.env
*.db
.DS_Store
.venv/
*.log

REQUIREMENTS:
- Type hints on all functions (typing module)
- Docstrings on all functions
- No secrets in code (use .env only)
- Error handling required (try/except)
- Logging instead of print()
- PEP 8 compliant
- Black formatted (88 char lines)
- No pseudo-code (actual working code)

OUTPUT: 11 complete, working files ready for:
docker-compose up -d
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## ✅ AFTER COPILOT GENERATES

```bash
# 1. Create project structure
mkdir eatsmartly-backend && cd eatsmartly-backend
mkdir agents
git init

# 2. Create .gitignore immediately (before pasting files)
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.env
*.db
.DS_Store
.venv/
*.log
EOF

# 3. Paste each file from Copilot output into correct location

# 4. Copy .env
cp .env.example .env

# 5. Start local environment
docker-compose up -d

# 6. Install Python deps
pip install -r requirements.txt

# 7. Run backend
uvicorn main:app --reload

# 8. Test in new terminal
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# 9. First commit
git add .
git commit -m "feat: EatSmartly AutoGen backend MVP

- 4-agent system (Data Collection, Web Scraping, Personalization, Orchestrator)
- FastAPI REST API
- Microsoft AutoGen for agent coordination  
- Local PostgreSQL + Redis
- Free APIs (USDA, Gemini)"

git remote add origin https://github.com/yourusername/eatsmartly-backend
git push -u origin main
```

---

## 🎯 WEEK 1 AFTER SCAFFOLD

**Day 1-2:** Local setup + import 10 test foods from USDA API
**Day 3-4:** Test Agent 1 (fetch food by barcode)
**Day 5-6:** Test Agent 2 (scrape recipes) + Agent 3 (personalize)
**Day 7:** Polish + first commit

**Total: ~15 hours coding**

---

## 💰 COST

**Local MVP: $0/month** ✓

---

**Paste the full prompt above into GitHub Copilot now! 🚀**

