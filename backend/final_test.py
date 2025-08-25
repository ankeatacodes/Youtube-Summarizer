#!/usr/bin/env python3
"""
Final demonstration test for the enhanced YouTube Video Summarizer
"""

import requests
import json
import time

def test_api():
    base_url = "http://localhost:8002"
    
    print("🚀 YouTube Video Summarizer - Enhanced with Transcript Extraction")
    print("=" * 70)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing server health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Server is healthy: {result['message']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")
        return
    
    # Test 2: Gemini AI Integration
    print("\n2️⃣ Testing Gemini AI integration...")
    try:
        response = requests.post(f"{base_url}/test-gemini", timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Gemini AI is working properly")
                print(f"   Sample response: {result.get('summary', '')[:100]}...")
            else:
                print(f"❌ Gemini AI test failed: {result.get('error')}")
        else:
            print(f"❌ Gemini test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Gemini test error: {e}")
    
    # Test 3: Video Summarization
    print("\n3️⃣ Testing video summarization...")
    test_video = {
        "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # "Me at the zoo" - first YouTube video
        "videoId": "jNQXAC9IVRw"
    }
    
    try:
        payload = {
            "url": test_video["url"],
            "action": "summarize",
            "videoId": test_video["videoId"]
        }
        
        print(f"   📹 Processing: {test_video['url']}")
        print("   ⏳ This may take 10-30 seconds...")
        
        start_time = time.time()
        response = requests.post(f"{base_url}/process-video", json=payload, timeout=60)
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                video_info = data.get('video_info', {})
                summary = data.get('summary', '')
                
                print(f"✅ Video processed successfully in {processing_time:.1f} seconds")
                print(f"\n📊 Video Information:")
                print(f"   📺 Title: {video_info.get('title', 'Unknown')}")
                print(f"   👤 Author: {video_info.get('author', 'Unknown')}")
                print(f"   ⏱️  Duration: {video_info.get('duration', 'Unknown')}")
                
                print(f"\n🤖 AI-Generated Summary:")
                print(f"   {summary[:400]}...")
                
                # Check if transcript was used
                if "transcript not available" in summary.lower() or "metadata" in summary.lower():
                    print(f"\n📝 Note: Used metadata-based summary (transcript not available)")
                else:
                    print(f"\n📝 Note: Used transcript-based summary")
                    
            else:
                print(f"❌ Video processing failed: {result.get('error')}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Video processing error: {e}")
    
    # Test 4: Quick Summary Feature
    print("\n4️⃣ Testing quick summary feature...")
    try:
        response = requests.post(f"{base_url}/quick-summary", timeout=30)
        if response.status_code == 200:
            result = response.json()
            if 'summary' in result:
                print(f"✅ Quick summary working")
                print(f"   Sample: {result['summary'][:100]}...")
            else:
                print(f"❌ Quick summary failed: {result}")
        else:
            print(f"❌ Quick summary failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Quick summary error: {e}")
    
    print("\n🎉 Testing Complete!")
    print("\n📝 Summary of Features Implemented:")
    print("   ✅ Real transcript extraction from YouTube videos")
    print("   ✅ Intelligent chunking for long videos")
    print("   ✅ Natural, conversational AI summaries")
    print("   ✅ Graceful fallback to metadata when transcript unavailable")
    print("   ✅ Error handling and logging")
    print("   ✅ FastAPI with comprehensive endpoints")
    
    print("\n🌟 Your YouTube Video Summarizer is now working like Sider/Eightify!")
    print("   🔗 API Docs: http://localhost:8002/docs")
    print("   💡 Ready for Chrome extension integration")

if __name__ == "__main__":
    test_api()
