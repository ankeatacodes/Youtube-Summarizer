import requests
import json

# Simple test script
def simple_test():
    base_url = "http://localhost:8002"
    
    # Test health
    print("Testing health...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health: {response.json()}")
    except Exception as e:
        print(f"Health error: {e}")
    
    # Test Gemini
    print("\nTesting Gemini...")
    try:
        response = requests.post(f"{base_url}/test-gemini")
        result = response.json()
        print(f"Gemini: {result.get('success')} - {result.get('message')}")
        if result.get('summary'):
            print(f"Sample: {result.get('summary')[:100]}...")
    except Exception as e:
        print(f"Gemini error: {e}")
    
    # Test video processing
    print("\nTesting video summarization...")
    try:
        payload = {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "action": "summarize", 
            "videoId": "dQw4w9WgXcQ"
        }
        response = requests.post(f"{base_url}/process-video", json=payload)
        result = response.json()
        print(f"Video processing: {result.get('success')}")
        if result.get('success'):
            data = result.get('data', {})
            summary = data.get('summary', '')
            video_info = data.get('video_info', {})
            print(f"Title: {video_info.get('title')}")
            print(f"Summary: {summary[:200]}...")
    except Exception as e:
        print(f"Video processing error: {e}")

if __name__ == "__main__":
    simple_test()
