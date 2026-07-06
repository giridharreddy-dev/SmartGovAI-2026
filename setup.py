#!/usr/bin/env python3
"""
SmartGov Health - Quick Setup Script
Run this once to set up the entire application with all MP3 audio files.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command with error handling."""
    print(f"\n📍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed: {result.stderr}")
            return False
        print(f"✅ {description} - Complete!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    print("""
╔════════════════════════════════════════════╗
║     SmartGov Health - Setup Wizard         ║
║   For Rural Andhra Pradesh Health Schemes  ║
╚════════════════════════════════════════════╝
    """)
    
    # Step 1: Virtual Environment
    if not (base_dir / "myenv" / "Scripts" / "python.exe").exists() and \
       not (base_dir / "myenv" / "bin" / "python").exists():
        if not run_command("python -m venv myenv", "Creating virtual environment"):
            sys.exit(1)
    
    # Step 2: Install requirements
    python_cmd = str(base_dir / "myenv" / "Scripts" / "python.exe") if os.name == 'nt' \
                 else f"source {base_dir}/myenv/bin/activate && python"
    
    if not run_command(f"{python_cmd} -m pip install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Step 3: Generate audio files
    print("\n📍 Generating Telugu audio files for all schemes...")
    print("   This may take 2-5 minutes depending on internet speed...")
    
    if not run_command(f"{python_cmd} generate_audio.py", "Audio generation"):
        print("⚠️  Audio generation failed, but app can still run with browser TTS")
    
    # Step 4: Start the app
    print("""
╔════════════════════════════════════════════╗
║         🎉 Setup Complete! 🎉             ║
╠════════════════════════════════════════════╣
║  Your app is ready to start!               ║
║                                            ║
║  Next steps:                               ║
║  1. Run: python app.py                     ║
║  2. Open: http://localhost:5000            ║
║  3. Install as PWA for offline use         ║
║                                            ║
║  🔊 Telugu audio is pre-cached             ║
║  📱 Works on mobile, tablet, desktop       ║
║  ✅ Offline-first design                   ║
╚════════════════════════════════════════════╝
    """)
    
    start_app = input("Do you want to start the app now? (y/n): ").lower()
    if start_app == 'y':
        if os.name == 'nt':
            os.system(f"{python_cmd} app.py")
        else:
            os.system(f"source myenv/bin/activate && python app.py")

if __name__ == "__main__":
    main()
