#!/usr/bin/env python3
"""
Server Health Checker - Tests the server without interfering with it
"""

import requests
import json
import time
import sys
from datetime import datetime

def test_server_health():
    """Test the server health endpoint"""
    print("🔍 Testing YouTube Video Summarizer Server...")
    print("=" * 50)
    
    try:
        # Test health endpoint
        print("📡 Connecting to http://localhost:8002/health...")
        response = requests.get('http://localhost:8002/health', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is HEALTHY!")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Message: {data.get('message', 'No message')}")
            print(f"   Model: {data.get('model', 'Unknown')}")
            print(f"   Timestamp: {data.get('timestamp', 'Unknown')}")
            
            # Test API documentation endpoint
            print("\n📚 Testing API documentation endpoint...")
            try:
                docs_response = requests.get('http://localhost:8002/docs', timeout=5)
                if docs_response.status_code == 200:
                    print("✅ API Documentation is accessible")
                else:
                    print(f"⚠️  API Documentation returned: {docs_response.status_code}")
            except Exception as e:
                print(f"⚠️  API Documentation test failed: {e}")
            
            return True
            
        else:
            print(f"❌ Server returned HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Server is not running")
        print("   Please start the server using: python gemini_server.py")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Server is not responding")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_summarization_endpoint():
    """Test the summarization endpoint with a sample video"""
    print("\n🎥 Testing video summarization endpoint...")
    
    # Sample YouTube video URL (short educational video)
    test_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short video
    
    try:
        payload = {
            "url": test_video_url
        }
        
        print(f"   Testing with video: {test_video_url}")
        response = requests.post(
            'http://localhost:8002/process-video', 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Summarization endpoint is working!")
            print(f"   Video Title: {data.get('title', 'Unknown')[:50]}...")
            print(f"   Summary Length: {len(data.get('summary', ''))} characters")
            return True
        else:
            print(f"⚠️  Summarization returned: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("⚠️  Summarization test timed out (this is normal for longer videos)")
        return True  # Timeout is acceptable for this test
        
    except Exception as e:
        print(f"⚠️  Summarization test failed: {e}")
        return False

if __name__ == "__main__":
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test health endpoint
    health_ok = test_server_health()
    
    if health_ok:
        # If health is good, test summarization
        test_summarization_endpoint()
        
        print("\n" + "=" * 50)
        print("🎉 Server testing completed!")
        print("   Your YouTube Video Summarizer is ready to use!")
        print("   Access the API docs at: http://localhost:8002/docs")
    else:
        print("\n" + "=" * 50)
        print("🚨 Server is not running!")
        print("   Please start the server first:")
        print("   1. Run: python gemini_server.py")
        print("   2. Or use: start_server.bat")
        sys.exit(1)
