"""
Quick test of just the video info extraction to verify it works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from professional_transcript_extractor import get_video_info

def test_video_info_only():
    """Test just the video info extraction"""
    
    video_url = "https://www.youtube.com/watch?v=bUAYvKCFpTg"
    
    print("🧪 Testing Video Info Extraction Only")
    print("=" * 40)
    print(f"📺 URL: {video_url}")
    print("🔄 Extracting info...")
    
    try:
        info = get_video_info(video_url)
        
        print("\n✅ EXTRACTION SUCCESS!")
        print(f"📝 Title: {info.get('title')}")
        print(f"👤 Author: {info.get('author')}")
        print(f"📋 Description: {info.get('description', '')[:100]}...")
        print(f"🎯 Source: {info.get('source')}")
        print(f"🆔 Video ID: {info.get('video_id')}")
        
        # Check if we got meaningful data
        title = info.get('title', '')
        if title and not title.startswith('YouTube Video (ID:'):
            print("\n🎉 SUCCESS: Meaningful title extracted!")
            print("✅ Video metadata extraction is working properly!")
        else:
            print("\n⚠️  Still getting fallback title")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_video_info_only()
