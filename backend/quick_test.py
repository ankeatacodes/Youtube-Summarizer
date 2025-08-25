import requests
import json

def quick_test():
    print("Testing Health Endpoint...")
    try:
        response = requests.get('http://localhost:8002/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Server Status: {data['status']}")
            print(f"Message: {data['message']}")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    quick_test()
