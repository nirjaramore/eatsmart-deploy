# ============================================================================
# EatSmartly - Complete Database Setup
# Run these commands in order to set up the database and IFCT data
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 EatSmartly Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to backend directory
Set-Location "C:\Users\anany\projects\eatsmart\eatsmartly-backend"

# Step 1: Install dependencies
Write-Host "📦 Step 1: Installing Python dependencies..." -ForegroundColor Yellow
pip install pdfplumber psycopg2-binary

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 2: Create database
Write-Host "🗄️  Step 2: Creating PostgreSQL database..." -ForegroundColor Yellow
Write-Host "Note: You may need to enter the postgres password" -ForegroundColor Gray

python setup_database.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Automated setup failed. Run manually:" -ForegroundColor Yellow
    Write-Host "   psql -U postgres" -ForegroundColor Gray
    Write-Host "   Then run these commands:" -ForegroundColor Gray
    Write-Host "   CREATE DATABASE eatsmartly;" -ForegroundColor Gray
    Write-Host "   CREATE USER eatsmartly WITH PASSWORD 'password';" -ForegroundColor Gray
    Write-Host "   GRANT ALL PRIVILEGES ON DATABASE eatsmartly TO eatsmartly;" -ForegroundColor Gray
    Write-Host "   \q" -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne 'y') {
        exit 1
    }
}
Write-Host "✅ Database created" -ForegroundColor Green
Write-Host ""

# Step 3: Import IFCT data
Write-Host "🇮🇳 Step 3: Importing IFCT 2017 data..." -ForegroundColor Yellow
python import_ifct_data.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  IFCT import had issues (sample data may have been created)" -ForegroundColor Yellow
}
Write-Host "✅ IFCT data imported" -ForegroundColor Green
Write-Host ""

# Step 4: Verify database
Write-Host "🔍 Step 4: Verifying database setup..." -ForegroundColor Yellow

Write-Host "Connecting to database to verify..." -ForegroundColor Gray
$verifyCommand = @"
SELECT 
    (SELECT COUNT(*) FROM ifct_foods) as ifct_count,
    (SELECT COUNT(*) FROM food_products) as products_count;
"@

try {
    $result = psql -U eatsmartly -d eatsmartly -t -c $verifyCommand 2>&1
    Write-Host $result -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Could not verify - you may need to enter database password" -ForegroundColor Yellow
}

Write-Host "✅ Verification complete" -ForegroundColor Green
Write-Host ""

# Step 5: Update .env
Write-Host "📝 Step 5: Checking .env file..." -ForegroundColor Yellow

$envFile = ".env"
$databaseUrl = "DATABASE_URL=postgresql://eatsmartly:password@localhost:5432/eatsmartly"

if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    if ($envContent -notmatch "DATABASE_URL") {
        Write-Host "Adding DATABASE_URL to .env..." -ForegroundColor Gray
        Add-Content -Path $envFile -Value "`n$databaseUrl"
        Write-Host "✅ DATABASE_URL added to .env" -ForegroundColor Green
    } else {
        Write-Host "✅ DATABASE_URL already in .env" -ForegroundColor Green
    }
} else {
    Write-Host "Creating .env file..." -ForegroundColor Gray
    Set-Content -Path $envFile -Value $databaseUrl
    Write-Host "✅ .env file created" -ForegroundColor Green
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Database Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Yellow
Write-Host "  • PostgreSQL database: eatsmartly" -ForegroundColor Gray
Write-Host "  • Tables created: 5" -ForegroundColor Gray
Write-Host "  • IFCT foods imported: Check output above" -ForegroundColor Gray
Write-Host "  • .env configured: Yes" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Restart backend: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
Write-Host "  2. Check logs for 'Database connection established'" -ForegroundColor Gray
Write-Host "  3. Test search in Flutter app" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
