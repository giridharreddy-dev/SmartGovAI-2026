#!/bin/bash
# SmartGov Health - Quick Start Script (Linux/macOS)
# Run this to set up the entire application

set -e

echo "╔════════════════════════════════════════════╗"
echo "║     SmartGov Health - Setup Script        ║"
echo "║   For Rural Andhra Pradesh Health Schemes  ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Step 1: Create virtual environment
echo "📍 Creating virtual environment..."
python3 -m venv myenv
source myenv/bin/activate

# Step 2: Install dependencies
echo "📍 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 3: Generate audio files
echo "📍 Generating Telugu audio files..."
echo "   (This may take 2-5 minutes...)"
python generate_audio.py

# Step 4: Success message
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║         🎉 Setup Complete! 🎉             ║"
echo "╠════════════════════════════════════════════╣"
echo "║  Your app is ready!                        ║"
echo "║                                            ║"
echo "║  To start the app:                         ║"
echo "║  $ source myenv/bin/activate               ║"
echo "║  $ python app.py                           ║"
echo "║                                            ║"
echo "║  Then open: http://localhost:5000          ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Optional: Ask to start app
read -p "Do you want to start the app now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python app.py
fi
