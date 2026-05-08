@echo off
title UNION PRINTING SYSTEM - Desktop Mode
echo ============================================
echo   UNION FOR DIGITAL PRINTING
echo   Desktop Application
echo ============================================
echo.

if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

echo Starting backend server...
start "Union Server" cmd /c "call venv\Scripts\activate.bat && cd backend && python manage.py runserver 127.0.0.1:8000 --noreload"

echo Waiting for server to start...
timeout /t 5 /nobreak >nul

echo Starting Desktop Application...
cd desktop
if not exist "node_modules" (
    echo Installing Electron...
    call npm install
)
call npm start
cd ..
pause
