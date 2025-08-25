"""
Final API test to verify the complete professional system works
"""

import requests
import json

def test_professional_api():
    """Test the professional API with our fixed metadata extraction"""
    
    url = "http://localhost:8002/summarize"
    test_video = "https://www.youtube.com/watch?v=bUAYvKCFpTg"
    
    print("🧪 Testing Professional YouTube Summarizer API")
    print("=" * 50)
    print(f"📺 Video: {test_video}")
    print("🔄 Sending request...")
    
    try:
        response = requests.post(
            url,
            json={"url": test_video},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS! API Response:")
            print(f"📋 Summary: {result.get('summary', 'No summary')[:200]}...")
            print(f"📝 Title: {result.get('title', 'No title')}")
            print(f"👤 Author: {result.get('author', 'No author')}")
            print(f"🎯 Source: {result.get('source', 'No source')}")
            print(f"⏱️  Length: {result.get('length', 'No length')}")
            print(f"📊 Status: {result.get('status', 'No status')}")
            
            if "meaningful title extracted" in str(result):
                print("\n🎉 METADATA EXTRACTION WORKING!")
            else:
                print(f"\n🔍 Full response: {json.dumps(result, indent=2)}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - make sure it's running on localhost:8002")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_professional_api()
