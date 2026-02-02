# 🚀 EatSmartly Quick Start Guide

Get your EatSmartly backend running in 5 minutes!

## Prerequisites Checklist
- [ ] Windows 10/11
- [ ] Python 3.10+ installed
- [ ] Docker Desktop installed and running
- [ ] PowerShell

## Step-by-Step Setup

### 1. Navigate to Project Directory
```powershell
cd c:\Users\anany\projects\eatsmart\eatsmartly-backend
```

### 2. Run Automated Setup
```powershell
.\setup.ps1
```

This script will:
- Check Python & Docker versions
- Create `.env` file from template
- Set up Python virtual environment
- Install all dependencies
- Start PostgreSQL and Redis containers

### 3. Get Your FREE USDA API Key

1. Visit: https://fdc.nal.usda.gov/api-key-signup.html
2. Fill out the form (takes 1 minute)
3. Check your email for the API key
4. Open `.env` and replace `your_free_usda_fdc_key_here` with your key

```env
USDA_API_KEY=YOUR_ACTUAL_API_KEY_HERE
```

### 4. Start the Backend
```powershell
# Activate virtual environment (if not already activated)
.\venv\Scripts\Activate.ps1

# Start the server
python main.py
```

You should see:
```
INFO:     EatSmartly Backend Starting...
INFO:     Database: localhost:5432/eatsmartly
INFO:     Redis: redis://localhost:6379/0
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5. Test the API

Open a new PowerShell window and test:

```powershell
# Health check
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","timestamp":"...","services":{"database":"connected","redis":"connected","agents":"active"}}
```

### 6. View API Documentation
Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## First API Call - Analyze a Barcode

### Example Barcode: Coca-Cola (012000814204)

```powershell
curl -X POST http://localhost:8000/analyze-barcode `
  -H "Content-Type: application/json" `
  -d '{\"barcode\": \"012000814204\", \"user_id\": \"test_user\", \"detailed\": true}'
```

### What You'll Get Back:
```json
{
  "barcode": "012000814204",
  "food_name": "Coca-Cola Classic",
  "brand": "The Coca-Cola Company",
  "verdict": "caution",
  "risk_level": "medium",
  "health_score": 25.5,
  "alerts": [],
  "warnings": [
    "⚠️ High sugar (39.0g) - Limit to special occasions"
  ],
  "suggestions": [
    "🍬 High sugar - limit to occasional treat",
    "⚖️ Portion control: 140 cal per serving"
  ],
  "alternatives": [
    {
      "name": "Sparkling water with lemon",
      "reason": "Zero calories, refreshing"
    },
    {
      "name": "Green tea",
      "reason": "Antioxidants, metabolism boost"
    }
  ]
}
```

## Next Steps

### 1. Create a User Profile
```powershell
curl -X POST http://localhost:8000/user/test_user/profile `
  -H "Content-Type: application/json" `
  -d '{
    \"age\": 30,
    \"gender\": \"male\",
    \"height_cm\": 175,
    \"weight_kg\": 70,
    \"health_goal\": \"weight_loss\",
    \"allergies\": [\"peanuts\"],
    \"health_conditions\": [\"diabetes\"],
    \"dietary_restrictions\": []
  }'
```

### 2. Search for Foods
```powershell
curl -X POST http://localhost:8000/search `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"apple\", \"user_id\": \"test_user\", \"limit\": 5}'
```

### 3. Try More Barcodes

Common product barcodes to test:
- **Snickers**: `040000000891`
- **Cheerios**: `016000275287`
- **Doritos**: `028400056229`
- **Coca-Cola**: `012000814204`

## Integration with Flutter

See `FLUTTER_INTEGRATION.md` for complete Flutter setup.

Quick Flutter test:
```dart
final api = EatSmartlyAPI();
final result = await api.analyzeBarcode('012000814204', 'test_user');
print('Verdict: ${result.verdict}');
```

## Troubleshooting

### "Database connection failed"
```powershell
# Check if PostgreSQL is running
docker-compose ps

# Restart services
docker-compose down
docker-compose up -d
```

### "Redis connection failed"
```powershell
# Test Redis
docker exec -it eatsmartly_redis redis-cli ping
# Should return: PONG
```

### "USDA API timeout"
- Check your API key in `.env`
- Verify you haven't exceeded daily limit (10,000 calls)
- Check internet connection

### "Module not found"
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Can't access from Flutter Android emulator
Change API base URL to `http://10.0.2.2:8000` (Android emulator localhost)

## Monitoring

### Check Docker Logs
```powershell
docker-compose logs -f db
docker-compose logs -f redis
```

### Check Application Logs
Logs are printed to console. Look for:
- `INFO` - Normal operations
- `WARNING` - Potential issues
- `ERROR` - Problems that need attention

## Production Checklist

Before deploying to production:
- [ ] Change `DEBUG=false` in `.env`
- [ ] Set strong database password
- [ ] Enable authentication (JWT)
- [ ] Set up proper CORS origins
- [ ] Use environment-specific `.env` files
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure SSL/TLS
- [ ] Set up CI/CD pipeline

## Support

- **Documentation**: See `README.md`
- **Flutter Guide**: See `FLUTTER_INTEGRATION.md`
- **Architecture**: See `EatSmartly_4Agent_Market_Research_Architecture.md`

## Success Checklist

You're ready when:
- [ ] `curl http://localhost:8000/health` returns `{"status":"healthy"}`
- [ ] You can analyze a barcode successfully
- [ ] You can search for foods
- [ ] User profile CRUD works
- [ ] Docker containers are running (`docker-compose ps`)

**Happy coding! 🎉**

---

**Total setup time: ~10 minutes** (including API key signup)
