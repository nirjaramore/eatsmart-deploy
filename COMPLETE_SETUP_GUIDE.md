# 🚀 EatSmartly - Complete Setup Guide

## What You Have Now

### ✅ Backend (Python FastAPI)
- **Location**: `c:\Users\anany\projects\eatsmart\eatsmartly-backend\`
- 4-agent system (Data Collection, Web Scraping, Personalization, Orchestrator)
- PostgreSQL database configured
- Redis caching ready
- USDA API integrated
- Gemini AI ready

### ✅ Flutter App
- **Location**: `c:\Users\anany\projects\eatsmart\eatsmartly_app\`
- Beautiful UI with your custom colors
- Barcode scanner with live camera
- Results screen with health analysis
- API integration ready

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Start the Backend

```powershell
# Terminal 1 - Start backend
cd c:\Users\anany\projects\eatsmart\eatsmartly-backend
python main.py
```

You should see:
```
INFO:     EatSmartly Backend Starting...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test it:**
```powershell
# In another terminal
curl http://localhost:8000/health
```

Should return: `{"status":"healthy",...}`

### Step 2: Setup Flutter App

```powershell
# Terminal 2 - Setup Flutter
cd c:\Users\anany\projects\eatsmart\eatsmartly_app
.\setup.ps1
```

This will:
- Check Flutter installation
- Install dependencies
- Check for connected devices

### Step 3: Configure API Endpoint

**Open:** `c:\Users\anany\projects\eatsmart\eatsmartly_app\lib\services\api_service.dart`

**Find this line:**
```dart
static const String baseUrl = 'http://localhost:8000';
```

**Change it based on your device:**

**Option A - Testing on Android Emulator:**
```dart
static const String baseUrl = 'http://10.0.2.2:8000';
```

**Option B - Testing on Physical Device:**
1. Get your PC's IP: Run `ipconfig` in PowerShell
2. Look for "IPv4 Address" (e.g., `192.168.1.100`)
3. Update to:
```dart
static const String baseUrl = 'http://192.168.1.100:8000';
```

### Step 4: Run the App

```powershell
flutter run
```

**OR** press **F5** in VS Code!

---

## 📱 Using the App

### First Launch
1. App opens to **Home Screen** (beautiful gradient with your colors)
2. Tap **"Start Scanning"** button
3. Grant camera permission when asked

### Scanning a Barcode
1. Point camera at any product barcode
2. Keep it steady within the frame (pink corners)
3. App automatically detects and analyzes
4. Loading screen appears: "Analyzing food..."

### Viewing Results
1. See food name, brand, barcode
2. **Health Score** (0-100) with color coding:
   - Green (Safe) = 70-100
   - Orange (Caution) = 40-69
   - Red (Avoid) = 0-39
3. View alerts, warnings, suggestions
4. See healthier alternatives
5. Check detailed nutrition facts
6. Tap **"Scan Another"** to continue

---

## 🧪 Testing Without Real Products

### Test Barcodes

Since you might not have products handy, here are real barcodes to test:

| Product | Barcode | Expected Result |
|---------|---------|-----------------|
| Coca-Cola Classic | `012000814204` | High sugar warning |
| Cheerios | `016000275287` | Generally safe |
| Snickers Bar | `040000000891` | High sugar/fat |
| Doritos | `028400056229` | High sodium |

### How to Test

**Option 1: Print a Barcode**
1. Go to https://barcode.tec-it.com/en/EAN13
2. Enter: `012000814204`
3. Generate and print
4. Scan with your app

**Option 2: Display on Another Device**
1. Generate barcode online
2. Display on laptop/tablet screen
3. Scan with phone

**Option 3: Manual Entry (Add Later)**
Currently app only scans. You can add a manual entry feature.

---

## 🎨 Your Custom Color Scheme

The app uses your exact colors:

```dart
// Primary Colors
Champagne: #F5E6D1  // Light background, soft and neutral
Light Red: #FFC8CB  // Soft pink accent, gentle highlights
Rose Gold: #B46C72  // Primary brand color, buttons
Puce Red:  #6E2E34  // Dark accent, text, strong elements
Rackley:   #5E7B9B  // Info/neutral, secondary actions
```

**Where They're Used:**
- **Background gradients**: Champagne → Light Red
- **Primary buttons**: Rose Gold
- **App bar**: Rose Gold
- **Text headings**: Puce Red
- **Feature cards**: White with Rose Gold accents
- **Scanner overlay**: Light Red corners
- **Verdict cards**: Color-coded (Safe/Caution/Avoid)

---

## 🔧 Troubleshooting

### Backend Issues

**"Database connection failed"**
```powershell
# Check if PostgreSQL is running
docker-compose ps

# Restart if needed
docker-compose down
docker-compose up -d
```

**"Food not found for barcode"**
- USDA API might not have that product
- Try a different barcode (test with Coca-Cola: `012000814204`)
- Check USDA API key in `.env`

### Flutter App Issues

**"Connection refused"**
```
Check:
1. Backend is running (http://localhost:8000/health)
2. Correct IP address in api_service.dart
3. For emulator: Use 10.0.2.2:8000
4. For physical device: Use your PC's IP
5. Firewall isn't blocking port 8000
```

**"Camera permission denied"**
```
1. Open phone Settings
2. Apps → EatSmartly
3. Permissions → Camera → Allow
4. Restart app
```

**"No barcode detected"**
```
- Ensure good lighting
- Hold phone steady
- Position barcode in frame
- Try different angle
- Use clear, printed barcode
```

**Build errors:**
```powershell
flutter clean
flutter pub get
flutter run
```

---

## 📊 Expected Flow

### Happy Path
```
1. User opens app → Home screen (2 seconds)
2. Taps "Start Scanning" → Camera opens
3. Points at barcode → Detection (instant)
4. Processing → API call (2-3 seconds)
5. Results shown → Full analysis displayed
6. User reviews → Reads suggestions
7. Taps "Scan Another" → Back to camera
```

### Sample API Response
When you scan Coca-Cola (`012000814204`):
```json
{
  "verdict": "caution",
  "health_score": 25.5,
  "food_name": "Coca-Cola Classic",
  "brand": "The Coca-Cola Company",
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
    }
  ]
}
```

---

## 🚀 Next Steps

### Immediate (Week 1)
- [ ] Test with 10+ different barcodes
- [ ] Take screenshots for documentation
- [ ] Add user profile screen
- [ ] Implement scan history

### Short-term (Week 2-3)
- [ ] Add manual barcode entry
- [ ] Implement search by food name
- [ ] Add favorites feature
- [ ] Create onboarding tutorial
- [ ] Add dark mode

### Long-term (Month 2+)
- [ ] User authentication (Firebase)
- [ ] Cloud deployment (AWS/GCP)
- [ ] iOS version
- [ ] Social sharing
- [ ] Meal planning
- [ ] Grocery list

---

## 📚 File Structure

### Backend
```
eatsmartly-backend/
├── main.py              # FastAPI app
├── config.py            # Configuration
├── agents/
│   ├── data_collection.py
│   ├── web_scraping.py
│   └── personalization.py
└── .env                 # Your API keys ✓
```

### Flutter App
```
eatsmartly_app/
├── lib/
│   ├── main.dart        # App entry point
│   ├── theme.dart       # Your custom colors
│   ├── models/
│   │   └── food_analysis.dart
│   ├── services/
│   │   └── api_service.dart
│   └── screens/
│       ├── home_screen.dart
│       ├── scanner_screen.dart
│       └── result_screen.dart
└── pubspec.yaml         # Dependencies
```

---

## 💡 Tips

1. **Always start backend first** before running app
2. **Test health endpoint** before scanning: `curl localhost:8000/health`
3. **Use good lighting** for barcode scanning
4. **Print barcodes** from online generators for testing
5. **Check logs** in both backend terminal and Flutter console

---

## 🎉 Success Checklist

You're ready when:
- [ ] Backend running at http://localhost:8000
- [ ] Health check returns `{"status":"healthy"}`
- [ ] Flutter app builds without errors
- [ ] Camera permission granted
- [ ] Can scan a barcode successfully
- [ ] Results screen shows correctly
- [ ] Can scan multiple products
- [ ] Colors match your design

---

## 📞 Quick Reference

**Start Backend:**
```powershell
cd c:\Users\anany\projects\eatsmart\eatsmartly-backend
python main.py
```

**Run Flutter App:**
```powershell
cd c:\Users\anany\projects\eatsmart\eatsmartly_app
flutter run
```

**Test Backend:**
```powershell
curl http://localhost:8000/health
```

**Your Database:**
```
Host: localhost
Port: 5432
Database: eatsmartly
User: postgres
```

---

**🎨 Your beautiful, color-coordinated food analyzer is ready! Start scanning! 🚀**
