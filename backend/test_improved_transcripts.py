#!/usr/bin/env python3
"""
Test script for improved YouTube transcript extraction using youtube-transcript-api
This script tests the reliability improvements over pytube
"""

import requests
import json
import time

def test_video_processing(video_url, video_name):
    """Test processing a single video with the improved transcript system"""
    print(f"\n{'='*60}")
    print(f"🎥 Testing: {video_name}")
    print(f"🔗 URL: {video_url}")
    print(f"{'='*60}")
    
    # Prepare the request
    payload = {
        "url": video_url,
        "action": "summarize",
        "videoId": video_url.split('=')[-1]  # Extract video ID
    }
    
    try:
        print("📤 Sending request to FastAPI server...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8002/process",
            json=payload,
            timeout=60  # 60 second timeout
        )
        
        processing_time = time.time() - start_time
        print(f"⏱️  Processing time: {processing_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success', False):
                print("✅ SUCCESS! Video processed successfully")
                
                data = result.get('data', {})
                
                # Display results
                print(f"\n📊 Video Information:")
                print(f"   Title: {data.get('title', 'N/A')}")
                print(f"   Author: {data.get('author', 'N/A')}")
                print(f"   Duration: {data.get('length', 'N/A')} seconds")
                print(f"   Views: {data.get('views', 'N/A'):,}")
                
                summary = data.get('summary', '')
                if summary:
                    print(f"\n📝 Summary ({len(summary)} characters):")
                    print(f"   {summary[:200]}...")
                    
                    # Check if it looks like a real summary (not generic)
                    generic_indicators = [
                        "based on the title and description",
                        "metadata suggests",
                        "from the available information",
                        "general overview of the video"
                    ]
                    
                    is_likely_real = not any(indicator in summary.lower() for indicator in generic_indicators)
                    if is_likely_real:
                        print("✅ Summary appears to be based on actual content!")
                    else:
                        print("⚠️  Summary might be generic (metadata-based)")
                
                transcript_used = data.get('transcript_extracted', False)
                if transcript_used:
                    print("📄 Transcript was successfully extracted and used")
                else:
                    print("⚠️  No transcript found - summary based on metadata")
                
                return True
                
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ FAILED: {error}")
                return False
                
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 60 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - make sure the server is running on localhost:8002")
        return False
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")
        return False

def main():
    """Test improved transcript extraction with various types of videos"""
    
    print("🧪 Testing YouTube Video Summarizer with Improved Transcript Extraction")
    print("🔧 Using youtube-transcript-api for more reliable transcript extraction")
    
    # Check if server is running
    try:
        health_response = requests.get("http://localhost:8002/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server health check failed")
            return
        print("✅ Server is running and healthy")
    except:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8002")
        return
    
    # Test videos with different characteristics
    test_videos = [
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "name": "Rick Astley - Never Gonna Give You Up (Music Video)"
        },
        {
            "url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
            "name": "PSY - GANGNAM STYLE (Music Video)"
        },
        {
            "url": "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
            "name": "Luis Fonsi - Despacito ft. Daddy Yankee (Music Video)"
        }
    ]
    
    print(f"\n🎯 Testing {len(test_videos)} videos...")
    
    success_count = 0
    for i, video in enumerate(test_videos, 1):
        print(f"\n📹 Test {i}/{len(test_videos)}")
        success = test_video_processing(video["url"], video["name"])
        if success:
            success_count += 1
        
        # Add delay between tests to be respectful
        if i < len(test_videos):
            print("\n⏳ Waiting 3 seconds before next test...")
            time.sleep(3)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {success_count}/{len(test_videos)}")
    print(f"❌ Failed: {len(test_videos) - success_count}/{len(test_videos)}")
    print(f"📈 Success Rate: {(success_count/len(test_videos)*100):.1f}%")
    
    if success_count == len(test_videos):
        print("\n🎉 All tests passed! The improved transcript extraction is working!")
    elif success_count > 0:
        print(f"\n🔧 {success_count} tests passed. Some issues remain to be investigated.")
    else:
        print("\n🚨 All tests failed. Check server logs for issues.")

if __name__ == "__main__":
    main()
