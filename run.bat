@echo off
title UNION PRINTING SYSTEM
echo ============================================
echo   UNION FOR DIGITAL PRINTING
echo   Management System
echo ============================================
echo.

if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Starting server...
echo.
echo Access the system at:
echo   Local:    http://localhost:8000
echo   Network:  http://%COMPUTERNAME%:8000
echo.
echo Press Ctrl+C to stop the server.
echo.

cd backend
python manage.py runserver 0.0.0.0:8000
cd ..
pause
