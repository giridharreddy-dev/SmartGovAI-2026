@echo off
REM SmartGov Health - Start App (Windows)
REM Run this to start the app

echo.
echo ╔════════════════════════════════════════════╗
echo ║   SmartGov Health - Starting App...       ║
echo ╚════════════════════════════════════════════╝
echo.

REM Activate virtual environment
call myenv\Scripts\activate.bat

REM Start the Flask app
echo 📱 Starting Flask app...
echo.
echo 🌐 Open your browser at: http://localhost:5000
echo.
echo 💡 Press Ctrl+C to stop the server
echo.

python app.py
