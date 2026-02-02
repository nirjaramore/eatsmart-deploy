# EatSmartly Backend Setup Script
# Run this script to set up the backend environment

Write-Host "🚀 EatSmartly Backend Setup" -ForegroundColor Green
Write-Host "=" * 50

# Check Python version
Write-Host "`n📌 Checking Python version..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(1[0-9]|[0-9]{2})") {
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python 3.10+ required. Found: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Check Docker
Write-Host "`n📌 Checking Docker..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
Write-Host "`n📌 Checking Docker Compose..." -ForegroundColor Cyan
try {
    $composeVersion = docker-compose --version 2>&1
    Write-Host "✅ $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose not found." -ForegroundColor Red
    exit 1
}

# Create .env file if not exists
Write-Host "`n📌 Setting up environment file..." -ForegroundColor Cyan
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "✅ Created .env from .env.example" -ForegroundColor Green
    Write-Host "⚠️  Please edit .env and add your API keys!" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env already exists" -ForegroundColor Green
}

# Create virtual environment
Write-Host "`n📌 Creating virtual environment..." -ForegroundColor Cyan
if (-not (Test-Path venv)) {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host "`n📌 Installing Python dependencies..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Start Docker services
Write-Host "`n📌 Starting PostgreSQL and Redis..." -ForegroundColor Cyan
docker-compose up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if services are running
$postgresStatus = docker-compose ps | Select-String "postgres.*Up"
$redisStatus = docker-compose ps | Select-String "redis.*Up"

if ($postgresStatus -and $redisStatus) {
    Write-Host "✅ PostgreSQL and Redis are running" -ForegroundColor Green
} else {
    Write-Host "⚠️  Services may not be fully ready. Check with: docker-compose ps" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" + ("=" * 50)
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "=" * 50

Write-Host "`nNext steps:"
Write-Host "1. Edit .env and add your USDA API key (get it from: https://fdc.nal.usda.gov/api-key-signup.html)" -ForegroundColor Cyan
Write-Host "2. Run the backend:" -ForegroundColor Cyan
Write-Host "   python main.py" -ForegroundColor White
Write-Host "   OR" -ForegroundColor White
Write-Host "   uvicorn main:app --reload" -ForegroundColor White
Write-Host "3. Test the API:" -ForegroundColor Cyan
Write-Host "   curl http://localhost:8000/health" -ForegroundColor White
Write-Host "4. View API docs: http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "`n📚 Documentation: See README.md for full details" -ForegroundColor Yellow
Write-Host "`n✨ Happy coding!" -ForegroundColor Green
