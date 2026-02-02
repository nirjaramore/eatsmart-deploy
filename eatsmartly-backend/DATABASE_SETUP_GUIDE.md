# Database & IFCT Setup Guide

## 🚀 Complete Setup Instructions

### Prerequisites
1. **PostgreSQL** installed (download from https://www.postgresql.org/download/)
2. Python backend setup complete
3. IFCT2017.pdf in project root

---

## Step 1: Install PostgreSQL

### Windows:
1. Download PostgreSQL installer from official website
2. Run installer, choose password for `postgres` user
3. Remember this password (default port: 5432)
4. Add PostgreSQL to PATH if not done automatically

### Verify Installation:
```powershell
psql --version
```

---

## Step 2: Install Python Dependencies

```powershell
cd C:\Users\anany\projects\eatsmart\eatsmartly-backend

# Install new dependencies
pip install pdfplumber psycopg2-binary
```

---

## Step 3: Create Database

### Option A: Using PowerShell
```powershell
# Connect to PostgreSQL
psql -U postgres

# In psql prompt, run:
CREATE DATABASE eatsmartly;
CREATE USER eatsmartly WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE eatsmartly TO eatsmartly;
\q
```

### Option B: Using Python Script (Automated)
```powershell
python setup_database.py
```

**Note:** If you get connection errors, edit `setup_database.py` and change the postgres password on line 17.

---

## Step 4: Run Database Schema

```powershell
# Execute SQL file to create tables
psql -U eatsmartly -d eatsmartly -f database_setup.sql

# Enter password: password
```

### Alternative (using Python):
The `setup_database.py` script already runs this automatically.

---

## Step 5: Import IFCT 2017 Data

```powershell
# Import Indian Food Composition Tables data
python import_ifct_data.py
```

**What this does:**
- Extracts nutrition data from IFCT2017.pdf
- Imports ~500+ Indian foods into database
- Creates sample data if PDF parsing fails

**Expected Output:**
```
================================================================================
🇮🇳 IFCT 2017 Data Import
================================================================================
📖 Opening PDF: C:\Users\anany\projects\eatsmart\IFCT2017.pdf
   📄 Total pages: 153
   ✅ Found food table on page 5
   📊 Processed 10 pages, found 45 foods
...
✅ Extraction complete: 523 foods found
💾 Importing 523 foods to database...
   ✅ Inserted 100 foods
   ✅ Inserted 200 foods
...
✅ Import complete: 523 foods imported
================================================================================
✅ IFCT Import Complete!
================================================================================
```

---

## Step 6: Update .env File

Add database connection to `.env`:

```env
# Add this line
DATABASE_URL=postgresql://eatsmartly:password@localhost:5432/eatsmartly
```

**If you used a different password or username, update accordingly.**

---

## Step 7: Verify Database

```powershell
# Connect to database
psql -U eatsmartly -d eatsmartly

# Check tables
\dt

# Expected output:
#  Schema |         Name          | Type  |   Owner    
# --------+-----------------------+-------+------------
#  public | food_products         | table | eatsmartly
#  public | ifct_foods            | table | eatsmartly
#  public | product_alternatives  | table | eatsmartly
#  public | scan_history          | table | eatsmartly
#  public | user_profiles         | table | eatsmartly

# Check IFCT data
SELECT COUNT(*) FROM ifct_foods;

# Expected: 523 (or 5 if using sample data)

# View sample Indian foods
SELECT food_code, food_name, protein_g, energy_kcal FROM ifct_foods LIMIT 10;

\q
```

---

## Step 8: Test Backend with Database

```powershell
# Restart backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Look for these logs:**
```
INFO:     Database connection established and tables created
INFO:     All agents initialized successfully
```

**No more errors like:**
```
❌ Database connection failed
```

---

## 🎯 Testing the New Features

### 1. Test Search Endpoint

```powershell
# Test search API
Invoke-RestMethod -Uri "http://localhost:8000/search" -Method POST -Body (@{query="rice"; user_id="test_user"; limit=5} | ConvertTo-Json) -ContentType "application/json"
```

### 2. Test IFCT Data Query

```powershell
psql -U eatsmartly -d eatsmartly

SELECT * FROM ifct_foods WHERE food_name LIKE '%rice%' LIMIT 5;
```

### 3. Test in Flutter App

1. Open app, tap "Search Products"
2. Search for "rice" or "wheat" or "dal"
3. Should show Indian foods from IFCT database

---

## 📊 Database Tables Overview

| Table Name | Purpose | Records |
|------------|---------|---------|
| `food_products` | Products from APIs (barcode-based) | Dynamic |
| `ifct_foods` | Indian Food Composition Tables 2017 | ~523 |
| `product_alternatives` | Better product suggestions | Auto-populated |
| `user_profiles` | User health data | Per user |
| `scan_history` | Scan logs | Per scan |

---

## 🔧 Troubleshooting

### Issue: "psql: command not found"
**Solution:** Add PostgreSQL bin to PATH
```powershell
# Add to PATH (adjust version number)
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
```

### Issue: "password authentication failed"
**Solution:** 
1. Edit `setup_database.py` line 17: Change password
2. Update `.env` DATABASE_URL with correct password

### Issue: "could not connect to server"
**Solution:** 
1. Start PostgreSQL service:
```powershell
# Windows
Start-Service postgresql-x64-16  # Adjust version

# Or use Services app (services.msc)
```

### Issue: "PDF not found"
**Solution:** 
- Make sure `IFCT2017.pdf` is in `C:\Users\anany\projects\eatsmart\`
- Or edit `import_ifct_data.py` line 268 to point to correct path
- Or use sample data (script auto-creates if PDF missing)

### Issue: "No foods extracted from PDF"
**Solution:**
- The PDF format might not be parseable
- Sample data will be created automatically (5 foods)
- Manually add more foods to `ifct_foods` table if needed

---

## ✅ Success Checklist

- [ ] PostgreSQL installed and running
- [ ] Database `eatsmartly` created
- [ ] Tables created (5 tables visible in `\dt`)
- [ ] IFCT data imported (500+ or 5 sample records)
- [ ] `.env` updated with DATABASE_URL
- [ ] Backend starts without database errors
- [ ] Search endpoint works
- [ ] Flutter app can search Indian foods

---

## 🎉 Next Steps

After database is set up:

1. **Test Search Screen** in Flutter app
2. **Scan a barcode** - data will be saved to `food_products` table
3. **View alternatives** - system will suggest better options
4. **Create user profile** - personalized recommendations
5. **Add more IFCT data** - manually or from additional sources

---

## 📝 Maintenance Commands

```powershell
# Backup database
pg_dump -U eatsmartly eatsmartly > backup.sql

# Restore database
psql -U eatsmartly eatsmartly < backup.sql

# View all foods
psql -U eatsmartly -d eatsmartly -c "SELECT COUNT(*) FROM ifct_foods;"

# Clear scan history
psql -U eatsmartly -d eatsmartly -c "DELETE FROM scan_history;"
```

---

## 🆘 Need Help?

- PostgreSQL Docs: https://www.postgresql.org/docs/
- psql Commands: https://www.postgresql.org/docs/current/app-psql.html
- IFCT 2017 Data: https://www.nin.res.in/nutrition2020/IFCT2017_Book.pdf
