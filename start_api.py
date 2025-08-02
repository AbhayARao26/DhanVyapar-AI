#!/usr/bin/env python3
"""
Startup script for DhanVyapar AI API Server
Handles environment setup and server startup
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking environment...")
    
    # Check GROQ API key
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("⚠️  GROQ_API_KEY not found in environment variables")
        print("   Some AI agents may not work properly")
        print("   Set it with: export GROQ_API_KEY='your_api_key'")
    else:
        print("✅ GROQ_API_KEY found")
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "api_server.py").exists():
        print("❌ api_server.py not found in current directory")
        print("   Make sure you're in the project root directory")
        return False
    
    print("✅ Environment check completed")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_server():
    """Start the API server"""
    print("\n🚀 Starting API server...")
    print("   Server will be available at: http://localhost:8000")
    print("   API Documentation: http://localhost:8000/docs")
    print("   Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the server
        subprocess.run([sys.executable, "api_server.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

def main():
    """Main startup function"""
    print("🎯 DhanVyapar AI API Server Startup")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please fix the issues above.")
        return
    
    # Install dependencies if needed
    install_choice = input("\n📦 Install/update dependencies? (y/n): ").lower().strip()
    if install_choice in ['y', 'yes']:
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please install manually.")
            return
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 