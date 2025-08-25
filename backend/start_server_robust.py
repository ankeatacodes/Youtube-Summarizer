#!/usr/bin/env python3
"""
Robust Server Starter - Starts the server in a way that isolates it from terminal interference
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def start_server_robust():
    """Start the server in a robust way"""
    print("🚀 Starting YouTube Video Summarizer Server (Robust Mode)")
    print("=" * 60)
    
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()
    server_script = script_dir / "gemini_server.py"
    
    if not server_script.exists():
        print(f"❌ Error: gemini_server.py not found at {server_script}")
        return False
    
    print(f"📁 Working directory: {script_dir}")
    print(f"🐍 Server script: {server_script}")
    
    try:
        # Start the server in a new process with proper isolation
        if os.name == 'nt':  # Windows
            # Use CREATE_NEW_PROCESS_GROUP to isolate the process
            process = subprocess.Popen(
                [sys.executable, str(server_script)],
                cwd=str(script_dir),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:  # Unix-like systems
            process = subprocess.Popen(
                [sys.executable, str(server_script)],
                cwd=str(script_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid
            )
        
        print(f"🔄 Server starting with PID: {process.pid}")
        print("⏳ Waiting for server to initialize...")
        
        # Wait for server to start (max 30 seconds)
        for i in range(30):
            try:
                response = requests.get('http://localhost:8002/health', timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Server is RUNNING!")
                    print(f"   Status: {data.get('status')}")
                    print(f"   URL: http://localhost:8002")
                    print(f"   Docs: http://localhost:8002/docs")
                    print(f"   PID: {process.pid}")
                    print("\n🎉 Server started successfully!")
                    print("   The server is now running independently.")
                    print("   You can safely run other commands in this terminal.")
                    return True
            except:
                pass
            
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("❌ Server failed to start within 30 seconds")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def check_if_already_running():
    """Check if server is already running"""
    try:
        response = requests.get('http://localhost:8002/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("ℹ️  Server is already running!")
            print(f"   Status: {data.get('status')}")
            print(f"   URL: http://localhost:8002")
            print(f"   Docs: http://localhost:8002/docs")
            return True
    except:
        pass
    return False

if __name__ == "__main__":
    print("🤖 YouTube Video Summarizer - Robust Server Starter")
    print()
    
    # Check if already running
    if check_if_already_running():
        print("✅ No action needed - server is already running!")
    else:
        print("🔄 Server not detected, starting new instance...")
        success = start_server_robust()
        
        if success:
            print("\n📋 Quick Commands:")
            print("   Test server: python test_server_health.py")
            print("   View docs:   http://localhost:8002/docs")
        else:
            print("\n🚨 Failed to start server!")
            print("   Try running manually: python gemini_server.py")
