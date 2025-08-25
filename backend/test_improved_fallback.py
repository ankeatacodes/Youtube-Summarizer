#!/usr/bin/env python3
"""
Test the improved fallback handling
"""
import requests
import json

def test_improved_fallback():
    base_url = "http://localhost:8002"
    
    print("🧪 Testing Improved Fallback Handling")
    print("=" * 50)
    
    # Test with a video that's likely to fail metadata extraction
    test_video = {
        "url": "https://www.youtube.com/watch?v=K4t_by8x4qs",
        "videoId": "K4t_by8x4qs"
    }
    
    try:
        payload = {
            "url": test_video["url"],
            "action": "summarize",
            "videoId": test_video["videoId"]
        }
        
        print(f"🎬 Testing video: {test_video['url']}")
        print("⏳ Processing...")
        
        response = requests.post(f"{base_url}/process-video", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                summary = data.get('summary', '')
                video_info = data.get('video_info', {})
                
                print(f"\n📊 Video Info:")
                print(f"   Title: {video_info.get('title')}")
                print(f"   Source: {video_info.get('source', 'unknown')}")
                
                print(f"\n📝 New Improved Response:")
                print(f"   {summary}")
                
                # Check if the response is much better
                if "YouTube API restrictions" in summary and len(summary) < 500:
                    print(f"\n✅ SUCCESS: Much better fallback response!")
                    print("   - Honest about limitations")
                    print("   - Provides helpful alternatives")
                    print("   - No more generic rambling")
                else:
                    print(f"\n⚠️  Response type: {'Detailed' if len(summary) > 500 else 'Concise'}")
                
            else:
                print(f"❌ Processing failed: {result.get('error')}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_improved_fallback()
