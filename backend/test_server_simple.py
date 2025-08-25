"""
Simple test to verify the server is running and responsive
"""

import requests
import time

def test_server():
    print("🧪 Testing Professional YouTube Summarizer Server")
    print("=" * 50)
    
    # Test health endpoint
    try:
        print("🔍 Testing health endpoint...")
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health endpoint error: {str(e)}")
        return
    
    # Test summarize endpoint with a simple request
    try:
        print("\n🔍 Testing summarize endpoint...")
        test_data = {"url": "https://www.youtube.com/watch?v=bUAYvKCFpTg"}
        
        print("🔄 Sending request (this may take a moment)...")
        response = requests.post(
            "http://localhost:8002/summarize", 
            json=test_data, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Summarize endpoint working!")
            print(f"📝 Title: {result.get('title', 'No title')}")
            print(f"👤 Author: {result.get('author', 'No author')}")
            print(f"🎯 Source: {result.get('source', 'No source')}")
            print(f"📊 Status: {result.get('status', 'No status')}")
            if result.get('summary'):
                print(f"📋 Summary: {result['summary'][:100]}...")
        else:
            print(f"❌ Summarize endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Summarize endpoint error: {str(e)}")

if __name__ == "__main__":
    test_server()
