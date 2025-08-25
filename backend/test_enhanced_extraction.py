"""
Test script for the enhanced transcript extraction system
Tests various scenarios and fallback methods
"""

import sys
import os
import logging
import time
import asyncio

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from improved_transcript_extractor import transcript_extractor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_video_info_extraction():
    """Test video info extraction with different URLs"""
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - very popular video
        "https://www.youtube.com/watch?v=bUAYvKCFpTg",  # Previous test video
        "https://youtu.be/dQw4w9WgXcQ",  # Short URL format
        "https://www.youtube.com/embed/dQw4w9WgXcQ",  # Embed format
    ]
    
    print("🔍 Testing Video Info Extraction")
    print("=" * 50)
    
    for url in test_urls:
        try:
            print(f"\\n📹 Testing URL: {url}")
            video_id = transcript_extractor.extract_video_id(url)
            print(f"   Video ID: {video_id}")
            
            if video_id:
                video_info = transcript_extractor.get_video_info_robust(url)
                print(f"   Title: {video_info.get('title', 'N/A')}")
                print(f"   Author: {video_info.get('author', 'N/A')}")
                print(f"   Duration: {video_info.get('length', 'N/A')}")
                print(f"   Source: {video_info.get('source', 'N/A')}")
                print(f"   Description: {video_info.get('description', 'N/A')[:100]}...")
            else:
                print("   ❌ Could not extract video ID")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Be nice to YouTube

def test_transcript_extraction():
    """Test transcript extraction with different methods"""
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - likely has captions
        "https://www.youtube.com/watch?v=bUAYvKCFpTg",  # Previous test video
        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # TED Talk - usually has captions
    ]
    
    print("\\n\\n📝 Testing Transcript Extraction")
    print("=" * 50)
    
    for url in test_urls:
        try:
            print(f"\\n🎬 Testing transcript for: {url}")
            video_id = transcript_extractor.extract_video_id(url)
            print(f"   Video ID: {video_id}")
            
            if video_id:
                transcript = transcript_extractor.get_transcript_robust(url)
                
                if transcript:
                    print(f"   ✅ Transcript extracted: {len(transcript)} characters")
                    print(f"   Preview: {transcript[:200]}...")
                else:
                    print("   ❌ No transcript available")
            else:
                print("   ❌ Could not extract video ID")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)  # Be extra nice to YouTube for transcript requests

def test_specific_methods():
    """Test specific extraction methods"""
    print("\\n\\n🔧 Testing Specific Methods")
    print("=" * 50)
    
    test_video_id = "dQw4w9WgXcQ"  # Rick Roll
    
    print(f"\\n🎯 Testing with video ID: {test_video_id}")
    
    # Test transcript API method
    print("\\n1. Testing YouTube Transcript API:")
    try:
        transcript = transcript_extractor._try_transcript_api(test_video_id)
        if transcript:
            print(f"   ✅ Success: {len(transcript)} characters")
            print(f"   Preview: {transcript[:150]}...")
        else:
            print("   ❌ Failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test video info extraction
    print("\\n2. Testing Video Info Extraction:")
    try:
        url = f"https://www.youtube.com/watch?v={test_video_id}"
        video_info = transcript_extractor.get_video_info_robust(url)
        print(f"   ✅ Success")
        print(f"   Title: {video_info.get('title', 'N/A')}")
        print(f"   Author: {video_info.get('author', 'N/A')}")
        print(f"   Source: {video_info.get('source', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Run all tests"""
    print("🚀 Enhanced Transcript Extraction Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Video Info Extraction
        test_video_info_extraction()
        
        # Test 2: Transcript Extraction
        test_transcript_extraction()
        
        # Test 3: Specific Methods
        test_specific_methods()
        
        print("\\n\\n✅ Test suite completed!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\\n\\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\\n\\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    main()
