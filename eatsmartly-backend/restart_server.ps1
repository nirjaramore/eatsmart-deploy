# Restart Backend Server (to load latest code changes)

Write-Host "Stopping existing backend servers..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -eq 'python' -and $_.MainWindowTitle -match 'uvicorn'} | Stop-Process -Force -ErrorAction SilentlyContinue

# Wait a moment
Start-Sleep -Seconds 2

Write-Host "Starting backend server with updated code..." -ForegroundColor Green
cd C:\Users\anany\projects\eatsmart\eatsmartly-backend

# Start server in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\anany\projects\eatsmart\eatsmartly-backend; python main.py" -WindowStyle Normal

Write-Host "`nBackend server starting..." -ForegroundColor Cyan
Write-Host "Waiting 5 seconds for server to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Test if server is up
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "`n✅ Backend server is running!" -ForegroundColor Green
    Write-Host "Health check:" -ForegroundColor White
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
} catch {
    Write-Host "`n❌ Backend server failed to start" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`nServer is ready to accept requests with Open Food Facts integration!" -ForegroundColor Green
