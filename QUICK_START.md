# 🚀 Quick Start Guide - Run This First!

## ⚡ One-Command Setup

```powershell
cd C:\Users\anany\projects\eatsmart\eatsmartly-backend
.\setup_complete_database.ps1
```

**This will automatically:**
- ✅ Install Python dependencies
- ✅ Create PostgreSQL database
- ✅ Create all tables (5 tables)
- ✅ Import IFCT 2017 data (500+ Indian foods)
- ✅ Update .env file
- ✅ Verify everything works

---

## 📋 Prerequisites

Before running the setup script:

1. **PostgreSQL must be installed**
   - Download: https://www.postgresql.org/download/
   - Remember the `postgres` user password

2. **Python backend environment ready**
   - Already set up in previous steps

3. **IFCT2017.pdf in project root** (optional)
   - If missing, sample data will be created

---

## 🎯 After Setup - Start Backend

```powershell
cd C:\Users\anany\projects\eatsmart\eatsmartly-backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Look for this in logs:**
```
✅ Database connection established and tables created
✅ All agents initialized successfully
```

---

## 📱 Test in Flutter App

### 1. Test Search Feature:
```
1. Open app on physical device
2. Tap "Search Products" button
3. Type "rice" or "dal" or "wheat"
4. Should see Indian foods from IFCT database
5. Tap any product to analyze
```

### 2. Test Barcode Scanning:
```
1. Tap "Start Scanning"
2. Scan a barcode (try Nutella: 3017620422003)
3. View beautiful result screen
4. Product data saved to database automatically
```

### 3. Test Alternatives (Code Update Needed):
Add this button to `result_screen.dart` to test alternatives:

```dart
// In result_screen.dart, add after recipes section:
ElevatedButton.icon(
  onPressed: () {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AlternativesScreen(
          barcode: widget.analysis.barcode,
          productName: widget.analysis.foodName ?? 'Unknown',
          userId: 'test_user',
        ),
      ),
    );
  },
  icon: Icon(Icons.swap_horiz),
  label: Text('View Better Alternatives'),
  style: ElevatedButton.styleFrom(
    backgroundColor: AppColors.success,
    padding: EdgeInsets.symmetric(vertical: 16),
  ),
)
```

---

## 🔍 Verify Database Setup

```powershell
# Connect to database
psql -U eatsmartly -d eatsmartly

# Check tables exist
\dt

# Expected output:
# food_products | ifct_foods | product_alternatives | scan_history | user_profiles

# Check IFCT data
SELECT COUNT(*) FROM ifct_foods;

# Should return: 523 (or 5 for sample data)

# View sample Indian foods
SELECT food_code, food_name, protein_g, energy_kcal 
FROM ifct_foods 
LIMIT 10;

# Exit
\q
```

---

## 🧪 Test API Endpoints

### Test Search:
```powershell
Invoke-RestMethod -Uri "http://192.168.1.4:8000/search" `
  -Method POST `
  -Body (@{query="rice"; user_id="test_user"; limit=5} | ConvertTo-Json) `
  -ContentType "application/json"
```

### Test Health:
```powershell
Invoke-RestMethod -Uri "http://192.168.1.4:8000/health" -Method GET
```

---

## 🆘 Troubleshooting

### Setup script fails?
**Manual steps:**
```powershell
# 1. Create database manually
psql -U postgres
CREATE DATABASE eatsmartly;
CREATE USER eatsmartly WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE eatsmartly TO eatsmartly;
\q

# 2. Run Python scripts
python setup_database.py
python import_ifct_data.py

# 3. Add to .env
DATABASE_URL=postgresql://eatsmartly:password@localhost:5432/eatsmartly
```

### Backend won't start?
Check:
1. PostgreSQL service running? (services.msc)
2. Correct password in .env?
3. Port 8000 not in use? (change to 8001)

### No search results?
1. Check IFCT data imported: `SELECT COUNT(*) FROM ifct_foods;`
2. Re-run: `python import_ifct_data.py`
3. Sample data should work (5 foods minimum)

---

## 📚 Full Documentation

For detailed information, see:
- `DATABASE_SETUP_GUIDE.md` - Complete setup instructions
- `IMPLEMENTATION_SUMMARY.md` - All features and testing
- `database_setup.sql` - Database schema

---

## ✅ Success Checklist

After running setup:
- [ ] `setup_complete_database.ps1` completed successfully
- [ ] Backend starts without errors
- [ ] Database has 5 tables
- [ ] IFCT data imported (500+ or 5 foods)
- [ ] Search endpoint works
- [ ] Flutter app connects to backend
- [ ] Can search for Indian foods
- [ ] Can scan barcodes

---

## 🎉 You're Ready!

**Everything is set up. Now you can:**

1. **Search** for any Indian food by name
2. **Scan** barcodes and get instant analysis
3. **View** beautiful nutrition displays
4. **Get** healthier alternatives suggestions
5. **Track** your scans in database
6. **Personalize** with user profiles

**Enjoy your AI-powered food analyzer!** 🍽️✨

---

**Quick Command Reference:**

| Action | Command |
|--------|---------|
| Setup database | `.\setup_complete_database.ps1` |
| Start backend | `python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000` |
| Check database | `psql -U eatsmartly -d eatsmartly` |
| Run Flutter app | `flutter run` |
| Test search API | `Invoke-RestMethod -Uri "http://192.168.1.4:8000/search" -Method POST -Body (@{query="rice"; user_id="test"} | ConvertTo-Json) -ContentType "application/json"` |

---

Created: November 30, 2025  
Status: Ready to Use ✅
