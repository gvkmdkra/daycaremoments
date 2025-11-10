#!/usr/bin/env python3
"""
DaycareMoments - Quick Start Script
Run this script to start the application locally
"""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ required")
        print(f"Current version: {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor} detected")

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("⚠️  No .env file found")
        print("Create .env with your API keys (see README.md)")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print("✅ .env file found")

def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def run_app():
    """Start Streamlit app"""
    print("\n🚀 Starting DaycareMoments...")
    print("App will open at http://localhost:8501")
    print("Press Ctrl+C to stop\n")
    try:
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except subprocess.CalledProcessError:
        print("\n❌ Failed to start app")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 50)
    print("  DaycareMoments - Local Development")
    print("=" * 50 + "\n")
    
    check_python_version()
    check_env_file()
    
    response = input("\nInstall/update dependencies? (y/n): ")
    if response.lower() == 'y':
        install_dependencies()
    
    run_app()
