"""
Debug test for title extraction
"""

import sys
import os
import logging
import re
import html
import json

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_title_extraction():
    """Debug the title extraction step by step"""
    import requests
    
    video_id = "bUAYvKCFpTg"
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print("🔍 Debug Title Extraction")
    print("=" * 30)
    
    response = requests.get(url, headers=headers, timeout=20)
    content = response.text
    
    print(f"Content length: {len(content)}")
    
    # Extract title step by step
    title = None
    
    # Method 1: Page title patterns
    title_patterns = [
        r'<title>([^<]+)</title>',
        r'<title[^>]*>([^<]+)</title>',
        r'"title":"([^"]+)"',
        r'property="og:title" content="([^"]+)"'
    ]
    
    for i, pattern in enumerate(title_patterns, 1):
        title_match = re.search(pattern, content, re.IGNORECASE)
        if title_match:
            raw_title = title_match.group(1)
            processed_title = raw_title.replace(' - YouTube', '').strip()
            print(f"Pattern {i}: Raw='{raw_title}' -> Processed='{processed_title}'")
            
            if processed_title and processed_title != 'YouTube' and not processed_title.startswith('YouTube'):
                title = html.unescape(processed_title)
                print(f"✅ Final title: '{title}'")
                break
            else:
                print(f"❌ Title rejected: '{processed_title}'")
        else:
            print(f"Pattern {i}: No match")
    
    if not title:
        print("❌ No title extracted from any pattern")
    
    # Test the full info structure
    info = {
        'video_id': video_id,
        'source': 'web_scraping',
        'title': title or f"YouTube Video (ID: {video_id})",
        'description': "Test description",
        'author': "Test author",
        'length': 'Unknown',
        'views': 'Unknown', 
        'publish_date': 'Unknown'
    }
    
    print(f"\\nFinal info structure:")
    print(f"Title: {info['title']}")
    print(f"Title starts with 'YouTube Video (ID:': {info['title'].startswith('YouTube Video (ID:')}")
    
    # Test the condition that decides success/failure
    meaningful_title = info.get('title') and not info['title'].startswith("YouTube Video (ID:")
    print(f"\\nMeaningful title check: {meaningful_title}")

if __name__ == "__main__":
    debug_title_extraction()
