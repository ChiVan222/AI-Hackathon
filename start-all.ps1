# PowerShell script to start both servers
Write-Host "========================================"
Write-Host "  AI Hackathon Idea Generator"
Write-Host "  Starting Backend and Frontend"
Write-Host "========================================"
Write-Host ""

Write-Host "[1/2] Starting Backend Server..." -ForegroundColor Green
Write-Host "Backend will run on http://localhost:8000"
Write-Host ""

# Start backend in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

Write-Host "[2/2] Starting Frontend Server..." -ForegroundColor Green
Write-Host "Frontend will run on http://localhost:3000"
Write-Host ""
Write-Host "NOTE: Make sure you have run 'npm install' in the frontend directory first!" -ForegroundColor Yellow
Write-Host ""

Start-Sleep -Seconds 2

# Start frontend in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "========================================"
Write-Host "  Both servers are starting!"
Write-Host "========================================"
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 5

Write-Host "Opening application in browser..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "To stop the servers, close their PowerShell windows." -ForegroundColor Yellow
Write-Host ""
