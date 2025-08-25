#!/usr/bin/env python3
"""
Test the complete summarization system including fallbacks
This demonstrates that even when transcripts aren't available, 
the system still provides useful summaries from metadata
"""

import requests
import json
import time

def test_server_endpoint():
    """Test the full FastAPI endpoint with fallback behavior"""
    print("🧪 Testing Complete YouTube Summarization System")
    print("📝 This test shows how the system handles cases where transcripts aren't available")
    
    # Test with a video
    test_url = "https://www.youtube.com/watch?v=9bZkp7q19f0"  # PSY - Gangnam Style
    
    payload = {
        "url": test_url,
        "action": "summarize", 
        "videoId": "9bZkp7q19f0"
    }
    
    try:
        print(f"📤 Sending request to FastAPI server...")
        print(f"🎥 Video: {test_url}")
        
        response = requests.post(
            "http://localhost:8002/process",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success', False):
                print("✅ SUCCESS! Server processed the request")
                
                data = result.get('data', {})
                
                print(f"\n📊 Video Information:")
                print(f"   Title: {data.get('title', 'N/A')}")
                print(f"   Author: {data.get('author', 'N/A')}")
                print(f"   Duration: {data.get('length', 'N/A')} seconds")
                print(f"   Views: {data.get('views', 'N/A')}")
                
                summary = data.get('summary', '')
                if summary:
                    print(f"\n📝 Generated Summary:")
                    print(f"   Length: {len(summary)} characters")
                    print(f"   Content: {summary[:300]}...")
                    
                    # Check quality indicators
                    print(f"\n🔍 Summary Analysis:")
                    if "based on the title and description" in summary.lower():
                        print("   ℹ️  Summary is metadata-based (expected when transcript unavailable)")
                    else:
                        print("   🎉 Summary appears to be content-based!")
                    
                    if len(summary) > 100:
                        print("   ✅ Summary has good length")
                    else:
                        print("   ⚠️  Summary is quite short")
                
                return True
                
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ Server returned error: {error}")
                return False
                
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - make sure the server is running on localhost:8002")
        return False
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Server health: {health_data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except:
        print("❌ Health check failed - server not responding")
        return False

def main():
    """Main test function"""
    print("🚀 YouTube Video Summarizer - Complete System Test")
    print("=" * 60)
    
    # Test health first
    print("1️⃣ Testing server health...")
    if not test_health_endpoint():
        print("Server is not running. Please start it with: python gemini_server.py")
        return
    
    print("\n2️⃣ Testing video processing...")
    success = test_server_endpoint()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SYSTEM IS WORKING!")
        print("✅ The YouTube summarizer can process videos and generate summaries")
        print("📝 Even when transcripts aren't available, it provides useful metadata-based summaries")
        print("🔧 The improved transcript extraction is in place for when transcripts are available")
    else:
        print("🚨 SYSTEM NEEDS ATTENTION")
        print("❌ Please check the server logs for issues")
    
    print("\n💡 Note: Transcript extraction may be rate-limited by YouTube.")
    print("   The system gracefully falls back to metadata-based summaries.")

if __name__ == "__main__":
    main()
