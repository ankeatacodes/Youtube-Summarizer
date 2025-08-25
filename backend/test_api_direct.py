#!/usr/bin/env python3
"""
Test with a specific video known to have captions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from youtube_transcript_api import YouTubeTranscriptApi

def test_youtube_transcript_api_directly():
    """Test the youtube-transcript-api directly to see if it's working"""
    print("🧪 Testing youtube-transcript-api directly...")
    
    # Test with a video that should have captions
    video_id = "9bZkp7q19f0"  # PSY - Gangnam Style (very likely to have captions)
    print(f"📹 Testing video ID: {video_id}")
    
    try:
        # Try to get English transcript
        print("📄 Attempting to get English transcript...")
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        
        if transcript_list:
            # Combine all transcript entries into one text
            transcript_text = ' '.join([entry['text'] for entry in transcript_list])
            print(f"✅ SUCCESS! Got {len(transcript_text)} characters")
            print(f"📝 First few entries:")
            for i, entry in enumerate(transcript_list[:3]):
                print(f"   {entry['start']:.1f}s: {entry['text']}")
            return True
            
    except Exception as e:
        print(f"❌ Failed to get English transcript: {e}")
        
        # Try to list available transcripts
        try:
            print("📋 Listing available transcripts...")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            print("Available transcripts:")
            for transcript in transcript_list:
                print(f"   - {transcript.language} ({transcript.language_code})")
                
                # Try to get the first available transcript
                try:
                    data = transcript.fetch()
                    if data:
                        transcript_text = ' '.join([entry['text'] for entry in data])
                        print(f"✅ SUCCESS with {transcript.language}! Got {len(transcript_text)} characters")
                        print(f"📝 Sample: {transcript_text[:100]}...")
                        return True
                except Exception as fetch_error:
                    print(f"   ❌ Failed to fetch {transcript.language}: {fetch_error}")
                    
        except Exception as list_error:
            print(f"❌ Failed to list transcripts: {list_error}")
    
    return False

if __name__ == "__main__":
    success = test_youtube_transcript_api_directly()
    if success:
        print("\n🎉 youtube-transcript-api is working!")
    else:
        print("\n🚨 youtube-transcript-api is not working properly")
