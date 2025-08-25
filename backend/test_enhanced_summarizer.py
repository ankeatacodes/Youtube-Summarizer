#!/usr/bin/env python3
"""
Test script for the improved YouTube Video Summarizer with transcript extraction
"""

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8002"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed with error: {e}")

def test_gemini():
    """Test the Gemini AI integration"""
    print("\n🧠 Testing Gemini AI integration...")
    try:
        response = requests.post(f"{BASE_URL}/test-gemini")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Gemini AI test passed!")
                print(f"   AI Response: {result.get('summary', '')[:100]}...")
            else:
                print(f"❌ Gemini AI test failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Gemini AI test failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Gemini AI test failed with error: {e}")

def test_video_summarization(video_url, video_id):
    """Test video summarization with transcript extraction"""
    print(f"\n📹 Testing video summarization for: {video_id}")
    print(f"   URL: {video_url}")
    
    try:
        payload = {
            "url": video_url,
            "action": "summarize",
            "videoId": video_id
        }
        
        print("   🔄 Processing video (this may take a while)...")
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/process-video", json=payload)
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Video summarization completed in {processing_time:.2f} seconds!")
                
                data = result.get('data', {})
                video_info = data.get('video_info', {})
                summary = data.get('summary', '')
                
                print(f"\n📊 Video Information:")
                print(f"   Title: {video_info.get('title', 'Unknown')}")
                print(f"   Author: {video_info.get('author', 'Unknown')}")
                print(f"   Duration: {video_info.get('duration', 'Unknown')}")
                print(f"   Views: {video_info.get('views', 'Unknown')}")
                
                print(f"\n📝 AI Summary:")
                print(f"   {summary[:500]}...")
                
                return True
            else:
                print(f"❌ Video summarization failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Video summarization failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Video summarization failed with error: {e}")
        return False

def test_video_transcription(video_url, video_id):
    """Test video transcription"""
    print(f"\n📝 Testing video transcription for: {video_id}")
    
    try:
        payload = {
            "url": video_url,
            "action": "transcribe",
            "videoId": video_id
        }
        
        print("   🔄 Processing video transcript...")
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/process-video", json=payload)
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Video transcription completed in {processing_time:.2f} seconds!")
                
                data = result.get('data', {})
                transcription = data.get('transcription', '')
                
                print(f"\n📄 Transcription Preview:")
                print(f"   {transcription[:300]}...")
                
                return True
            else:
                print(f"❌ Video transcription failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Video transcription failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Video transcription failed with error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 YouTube Video Summarizer - Enhanced Test Suite")
    print("=" * 60)
    
    # Test basic functionality
    test_health()
    test_gemini()
    
    # Test video processing with different types of videos
    test_videos = [
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "id": "dQw4w9WgXcQ",
            "description": "Short music video (should have captions)"
        },
        {
            "url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
            "id": "9bZkp7q19f0", 
            "description": "PSY - Gangnam Style (popular video with captions)"
        }
    ]
    
    success_count = 0
    total_tests = len(test_videos) * 2  # summarize + transcribe for each video
    
    for video in test_videos:
        print(f"\n🎬 Testing with: {video['description']}")
        print("-" * 50)
        
        # Test summarization
        if test_video_summarization(video['url'], video['id']):
            success_count += 1
        
        # Test transcription
        if test_video_transcription(video['url'], video['id']):
            success_count += 1
        
        # Small delay between tests
        time.sleep(2)
    
    print(f"\n🏁 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Your YouTube summarizer is working perfectly!")
    elif success_count > 0:
        print("⚠️ Some tests passed. Check the failures above for issues.")
    else:
        print("❌ All tests failed. Check your server configuration and API key.")

if __name__ == "__main__":
    main()
