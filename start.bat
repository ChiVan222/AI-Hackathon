@echo off
echo ========================================
echo   AI Hackathon Idea Generator
echo   Starting Backend and Frontend...
echo ========================================
echo.

REM Start FastAPI backend in a new window
echo [1/2] Starting FastAPI Backend on port 8000...
call venv\Scripts\activate
pip install -r requirements.txt
start "FastAPI Backend" cmd /k "cd /d %~dp0 && python -m uvicorn app.main:app --reload --port 8000"

REM Wait a moment for backend to initialize
timeout /t 3 /nobreak >nul

REM Start Next.js frontend in a new window
echo [2/2] Starting Next.js Frontend on port 3000...
start "Next.js Frontend" cmd /k "cd /d %~dp0my-project && npm run dev"

echo.
echo ========================================
echo   Both servers are starting!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo ========================================
echo.
echo Press any key to exit this window...
pause >nul
