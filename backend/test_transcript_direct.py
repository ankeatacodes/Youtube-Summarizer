#!/usr/bin/env python3
"""
Simple test for the improved YouTube transcript extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions directly
from gemini_server import get_video_transcript, extract_video_id

def test_transcript_extraction():
    """Test the new transcript extraction directly"""
    print("🧪 Testing youtube-transcript-api directly...")
    
    # Test with a well-known video
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"🎥 Testing URL: {test_url}")
    
    # Extract video ID
    video_id = extract_video_id(test_url)
    print(f"📹 Video ID: {video_id}")
    
    if not video_id:
        print("❌ Failed to extract video ID")
        return False
    
    # Test transcript extraction
    print("📄 Attempting transcript extraction...")
    transcript = get_video_transcript(test_url)
    
    if transcript:
        print(f"✅ SUCCESS! Extracted {len(transcript)} characters")
        print(f"📝 First 200 characters: {transcript[:200]}...")
        return True
    else:
        print("❌ Failed to extract transcript")
        return False

if __name__ == "__main__":
    test_transcript_extraction()
