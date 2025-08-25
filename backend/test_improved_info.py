"""
Quick test for improved video info extraction
"""

import sys
import os
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from professional_transcript_extractor import transcript_extractor

def test_improved_extraction():
    """Test the improved video info extraction"""
    test_url = "https://www.youtube.com/watch?v=bUAYvKCFpTg"
    
    print("🧪 Testing Improved Video Info Extraction")
    print("=" * 50)
    print(f"URL: {test_url}")
    
    try:
        video_info = transcript_extractor.get_video_info_robust(test_url)
        
        print("\n📊 Results:")
        print(f"Title: {video_info.get('title', 'N/A')}")
        print(f"Author: {video_info.get('author', 'N/A')}")
        print(f"Description: {video_info.get('description', 'N/A')[:100]}...")
        print(f"Source: {video_info.get('source', 'N/A')}")
        print(f"Video ID: {video_info.get('video_id', 'N/A')}")
        
        if video_info.get('title') and not video_info['title'].startswith("YouTube Video (ID:"):
            print("\n✅ Successfully extracted meaningful video info!")
        else:
            print("\n⚠️ Only basic fallback info available")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_improved_extraction()
