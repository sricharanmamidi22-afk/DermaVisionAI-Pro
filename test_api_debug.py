#!/usr/bin/env python3
"""
Test script for improvement suggestions API
"""
import requests
import json

def test_api():
    """Test the improvement suggestions API endpoint"""
    try:
        print("Testing improvement suggestions API...")

        # Test with different scan IDs
        test_ids = ['1', 'DV-123', 'mock-456']

        for scan_id in test_ids:
            url = f'http://127.0.0.1:5000/api/improvement-suggestions/{scan_id}'
            print(f"\nTesting URL: {url}")

            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Response Status: {data.get('status', 'Unknown')}")
                    if 'suggestions' in data:
                        suggestions = data['suggestions']
                        print(f"Current Score: {suggestions.get('current_score', 'N/A')}")
                        print(f"Active Protocols: {len(suggestions.get('suggestions', []))}")
                        print("✅ API working correctly!")
                    else:
                        print("❌ No suggestions in response")
                        print(f"Response: {data}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"Raw response (first 200 chars): {response.text[:200]}...")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")

    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_api()