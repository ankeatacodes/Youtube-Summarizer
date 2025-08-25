#!/usr/bin/env python3
"""
Test with videos that are more likely to have transcripts available
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gemini_server import get_video_transcript, extract_video_id

def test_video(url, name):
    """Test transcript extraction for a specific video"""
    print(f"\n{'='*50}")
    print(f"🎥 Testing: {name}")
    print(f"🔗 URL: {url}")
    print(f"{'='*50}")
    
    # Extract video ID
    video_id = extract_video_id(url)
    print(f"📹 Video ID: {video_id}")
    
    if not video_id:
        print("❌ Failed to extract video ID")
        return False
    
    # Test transcript extraction
    print("📄 Attempting transcript extraction...")
    transcript = get_video_transcript(url)
    
    if transcript:
        print(f"✅ SUCCESS! Extracted {len(transcript)} characters")
        print(f"📝 Preview: {transcript[:150]}...")
        return True
    else:
        print("❌ Failed to extract transcript")
        return False

def main():
    """Test with different types of videos"""
    
    # Test videos that are more likely to have captions
    test_videos = [
        {
            "url": "https://www.youtube.com/watch?v=fJ9rUzIMcZQ",
            "name": "Tutorial/Educational Video (more likely to have captions)"
        },
        {
            "url": "https://www.youtube.com/watch?v=LXb3EKWsInQ",
            "name": "Another test video"
        },
        {
            "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "name": "Me at the zoo (first YouTube video)"
        }
    ]
    
    print("🧪 Testing youtube-transcript-api with different videos...")
    
    success_count = 0
    for video in test_videos:
        success = test_video(video["url"], video["name"])
        if success:
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"📊 RESULTS: {success_count}/{len(test_videos)} videos successful")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
