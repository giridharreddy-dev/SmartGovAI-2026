@echo off
REM SmartGov Health - Quick Start Script (Windows)
REM Run this to set up the entire application

echo.
echo ╔════════════════════════════════════════════╗
echo ║     SmartGov Health - Setup Script        ║
echo ║   For Rural Andhra Pradesh Health Schemes  ║
echo ╚════════════════════════════════════════════╝
echo.

REM Step 1: Create virtual environment
echo 📍 Creating virtual environment...
python -m venv myenv
call myenv\Scripts\activate.bat

REM Step 2: Install dependencies
echo 📍 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Step 3: Generate audio files
echo 📍 Generating Telugu audio files...
echo    (This may take 2-5 minutes...)
python generate_audio.py

REM Step 4: Success message
echo.
echo ╔════════════════════════════════════════════╗
echo ║         🎉 Setup Complete! 🎉             ║
echo ╠════════════════════════════════════════════╣
echo ║  Your app is ready!                        ║
echo ║                                            ║
echo ║  To start the app, run:                    ║
echo ║  start_app.bat                             ║
echo ║                                            ║
echo ║  Then open: http://localhost:5000          ║
echo ║                                            ║
echo ║  To access app later, just run:            ║
echo ║  start_app.bat                             ║
echo ╚════════════════════════════════════════════╝
echo.

pause

REM Ask to start app
set /p start="Do you want to start the app now? (y/n): "
if /i "%start%"=="y" (
    python app.py
)
