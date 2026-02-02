# EatSmartly Backend - Multi-Agent Food Analyzer

AI-powered barcode food analyzer using Microsoft AutoGen multi-agent architecture. Provides personalized nutrition analysis, allergen warnings, and healthier alternatives.

## 🏗️ Architecture

**4-Agent System:**
- **Agent 1 (DataCollectionAgent)**: Fetches food data from USDA API, PostgreSQL, and Redis cache
- **Agent 2 (WebScrapingAgent)**: Enriches data with recipes and alternatives from AllRecipes, BBC Food
- **Agent 3 (PersonalizationAgent)**: Filters recommendations based on user health profile
- **Agent 4 (Orchestrator)**: Coordinates all agents via FastAPI REST API

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- USDA API Key (free): https://fdc.nal.usda.gov/api-key-signup.html

### Setup

1. **Clone and navigate:**
```powershell
cd c:\Users\anany\projects\eatsmart\eatsmartly-backend
```

2. **Create environment file:**
```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your USDA API key.

3. **Start PostgreSQL and Redis:**
```powershell
docker-compose up -d
```

4. **Install Python dependencies:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

5. **Run the backend:**
```powershell
python main.py
```

Or with uvicorn:
```powershell
uvicorn main:app --reload
```

6. **Test the API:**
```powershell
# Health check
curl http://localhost:8000/health

# Analyze barcode (example)
curl -X POST http://localhost:8000/analyze-barcode `
  -H "Content-Type: application/json" `
  -d '{\"barcode\": \"012000161155\", \"user_id\": \"test_user\"}'
```

## 📡 API Endpoints

### Core Endpoints

**GET /** - API information
**GET /health** - Health check

**POST /analyze-barcode**
```json
{
  "barcode": "012000161155",
  "user_id": "test_user",
  "detailed": true
}
```

**POST /search**
```json
{
  "query": "apple",
  "user_id": "test_user",
  "limit": 5
}
```

**GET /user/{user_id}/profile** - Get user profile
**POST /user/{user_id}/profile** - Update user profile

**POST /batch-analysis** - Analyze multiple barcodes

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🗄️ Database Schema

### Foods Table
```sql
CREATE TABLE foods (
    barcode VARCHAR(13) PRIMARY KEY,
    name VARCHAR(500),
    brand VARCHAR(200),
    serving_size FLOAT,
    serving_unit VARCHAR(20),
    calories FLOAT,
    protein_g FLOAT,
    carbs_g FLOAT,
    fat_g FLOAT,
    saturated_fat_g FLOAT,
    sodium_mg FLOAT,
    sugar_g FLOAT,
    fiber_g FLOAT,
    allergens VARCHAR(500),
    ingredients TEXT,
    source VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### User Profiles Table
```sql
CREATE TABLE user_profiles (
    user_id VARCHAR(255) PRIMARY KEY,
    age INTEGER,
    gender VARCHAR(20),
    height_cm FLOAT,
    weight_kg FLOAT,
    activity_level VARCHAR(50),
    health_goal VARCHAR(100),
    allergies VARCHAR(500),
    health_conditions VARCHAR(500),
    dietary_restrictions VARCHAR(500),
    daily_calorie_target INTEGER,
    daily_protein_target_g FLOAT,
    daily_carbs_target_g FLOAT,
    daily_fat_target_g FLOAT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## 🧪 Testing

```powershell
# Run tests
pytest

# With coverage
pytest --cov=agents --cov=main
```

## 🔧 Configuration

All configuration via `.env` file:

```env
DATABASE_URL=postgresql://eatsmartly:password@localhost:5432/eatsmartly
REDIS_URL=redis://localhost:6379/0
USDA_API_KEY=your_api_key_here
DEBUG=true
LOG_LEVEL=INFO
```

## 📊 Agent Details

### DataCollectionAgent
- **Fallback chain**: Redis → PostgreSQL → USDA API
- **Caching**: 24-hour TTL in Redis
- **Database**: Automatic upsert to PostgreSQL
- **Validation**: UPC-A, EAN-13, EAN-8 checksum

### WebScrapingAgent
- **Recipe sources**: AllRecipes, BBC Good Food
- **Alternatives database**: 50+ healthier swaps
- **Nutrition tips**: Automated based on nutrition data
- **Rate limiting**: Respectful scraping with delays

### PersonalizationAgent
- **Allergen detection**: 8 major allergens tracked
- **Health conditions**: Diabetes, hypertension, heart disease support
- **Dietary restrictions**: Vegetarian, vegan, gluten-free
- **Health goals**: Weight loss, muscle gain, heart health
- **Safety verdicts**: Safe, Caution, Avoid

## 🌐 Flutter Integration

### Example API Call from Flutter
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<Map<String, dynamic>> analyzeBarcode(String barcode, String userId) async {
  final response = await http.post(
    Uri.parse('http://localhost:8000/analyze-barcode'),
    headers: {'Content-Type': 'application/json'},
    body: json.encode({
      'barcode': barcode,
      'user_id': userId,
      'detailed': true
    }),
  );
  
  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('Failed to analyze barcode');
  }
}
```

## 💰 Cost (Local MVP)

| Component | Cost/Month |
|-----------|-----------|
| PostgreSQL (local) | $0 |
| Redis (local) | $0 |
| USDA API | $0 (10K calls/day) |
| Gemini API (optional) | $0 (free tier) |
| **Total** | **$0** |

## 📁 Project Structure

```
eatsmartly-backend/
├── agents/
│   ├── __init__.py
│   ├── data_collection.py    # Agent 1: Data fetching
│   ├── web_scraping.py        # Agent 2: Web enrichment
│   ├── personalization.py     # Agent 3: User filtering
│   └── utils.py               # Shared utilities
├── main.py                    # FastAPI app + orchestrator
├── config.py                  # Environment configuration
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # PostgreSQL + Redis
├── Dockerfile                 # Container image
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🐛 Troubleshooting

### Database connection error
```powershell
# Check if PostgreSQL is running
docker-compose ps

# Restart services
docker-compose down
docker-compose up -d
```

### Redis connection error
```powershell
# Test Redis connection
docker exec -it eatsmartly_redis redis-cli ping
```

### USDA API timeout
- Check API key in `.env`
- Verify daily limit (10,000 calls)
- Check internet connection

### Import errors
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📝 TODO for Production

- [ ] Add authentication (JWT)
- [ ] Rate limiting per user
- [ ] Async agent execution
- [ ] Cached recipe storage
- [ ] User activity logging
- [ ] Performance monitoring
- [ ] Deploy to AWS/GCP
- [ ] CI/CD pipeline
- [ ] Integration tests
- [ ] Load testing

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run tests: `pytest`
4. Submit pull request

## 📄 License

MIT License

## 🔗 Resources

- USDA FoodData Central: https://fdc.nal.usda.gov/
- FastAPI Docs: https://fastapi.tiangolo.com/
- Microsoft AutoGen: https://github.com/microsoft/autogen

---

**Built with ❤️ for healthier food choices**
