#!/usr/bin/env python3
"""
Bible in a Year - Application Launcher
Run both backend and frontend servers
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        print("✓ Backend dependencies installed")
    except ImportError:
        print("✗ Backend dependencies missing. Run: pip install -r requirements.txt")
        return False

    # Check if frontend is built
    frontend_dist = Path("static")
    if not frontend_dist.exists():
        print("✗ Frontend not built. Run: cd frontend && npm run build")
        return False

    print("✓ Frontend built")
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    return subprocess.Popen([
        sys.executable, "-m", "backend.main"
    ])

def open_browser():
    """Open the application in the default browser"""
    time.sleep(2)  # Wait for server to start
    webbrowser.open("http://localhost:8000")
    print("🌐 Opened http://localhost:8000 in your browser")

def main():
    print("📖 Bible in a Year with AI Spiritual Companions")
    print("=" * 50)

    if not check_requirements():
        sys.exit(1)

    # Start backend
    backend_process = start_backend()

    try:
        print("⏳ Waiting for server to start...")
        time.sleep(3)

        # Check if backend is running
        import requests
        try:
            response = requests.get("http://localhost:8000/api/app/info", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully")
                open_browser()
            else:
                print("⚠️  Backend server may not be responding correctly")
        except requests.exceptions.RequestException:
            print("⚠️  Could not verify backend server status")

        print("\n" + "=" * 50)
        print("🎉 Application is running!")
        print("📱 Frontend: http://localhost:8000")
        print("🔧 API Docs: http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop")
        print("=" * 50)

        # Keep running
        backend_process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ Application stopped")

if __name__ == "__main__":
    main()