"""
Test script for Gemini API integration
"""

import requests
import json
import time

def test_gemini_api():
    """Test the Gemini API integration"""
    
    # Test data
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    test_request = {
        "url": test_url,
        "action": "summarize",
        "videoId": "dQw4w9WgXcQ"
    }
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        health_response = requests.get("http://localhost:8002/health", timeout=10)
        print(f"Health Status: {health_response.status_code}")
        print(f"Health Response: {health_response.json()}")
        
        # Test Gemini integration
        print("\nTesting Gemini API integration...")
        gemini_response = requests.post("http://localhost:8002/test-gemini", timeout=30)
        print(f"Gemini Test Status: {gemini_response.status_code}")
        print(f"Gemini Test Response: {gemini_response.json()}")
        
        # Test video processing
        print("\nTesting video processing...")
        process_response = requests.post(
            "http://localhost:8002/process-video", 
            json=test_request,
            timeout=60
        )
        print(f"Process Status: {process_response.status_code}")
        result = process_response.json()
        
        if result.get("success"):
            print("✅ Video processing successful!")
            if "summary" in result.get("data", {}):
                print(f"Summary: {result['data']['summary'][:200]}...")
            if "video_info" in result.get("data", {}):
                print(f"Video Info: {result['data']['video_info']}")
        else:
            print(f"❌ Video processing failed: {result.get('error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on port 8002.")
    except requests.exceptions.Timeout:
        print("❌ Request timed out.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_gemini_api()
