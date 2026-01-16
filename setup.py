#!/usr/bin/env python3
"""
Bible in a Year - Development Setup Script
Installs all dependencies and sets up the development environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stderr)
        return False

def main():
    print("📖 Bible in a Year - Development Setup")
    print("=" * 50)

    project_root = Path(__file__).parent
    os.chdir(project_root)

    success_count = 0
    total_steps = 4

    # 1. Install Python dependencies
    if run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        success_count += 1
    else:
        print("💡 Tip: You may need to upgrade pip: pip install --upgrade pip")
        print("💡 Or create a virtual environment: python -m venv venv && venv\\Scripts\\activate (Windows)")

    # 2. Check Node.js and npm
    if run_command("node --version", "Checking Node.js installation"):
        if run_command("npm --version", "Checking npm installation"):
            success_count += 1
        else:
            print("❌ npm not found. Please install Node.js from https://nodejs.org")
    else:
        print("❌ Node.js not found. Please install from https://nodejs.org")

    # 3. Install frontend dependencies
    if run_command("cd frontend && npm install", "Installing frontend dependencies"):
        success_count += 1
    else:
        print("💡 Make sure you're in the correct directory and npm is installed")

    # 4. Build frontend
    if run_command("cd frontend && npm run build", "Building frontend"):
        success_count += 1
    else:
        print("💡 Try running: cd frontend && npm run build")

    print("\n" + "=" * 50)
    print(f"Setup completed: {success_count}/{total_steps} steps successful")

    if success_count == total_steps:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Place Saint Augustine's writings in: data/augustine/")
        print("2. Install Ollama: https://ollama.ai")
        print("3. Run: ollama pull llama2:7b")
        print("4. Start the app: python run.py")
        print("\n📖 Happy reading!")
    else:
        print("⚠️  Some steps failed. Please check the errors above and try again.")
        print("You can also run individual steps manually.")

    print("=" * 50)

if __name__ == "__main__":
    main()