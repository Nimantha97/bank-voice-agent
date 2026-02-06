#!/usr/bin/env python3
"""Test all API endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("Testing API endpoints...")
    print(f"Base URL: {BASE_URL}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"[OK] Health endpoint: {response.status_code} - {response.json()}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Server not running on port 8000")
        return
    except Exception as e:
        print(f"[ERROR] Health endpoint: {e}")
        return
    
    # Test OpenAPI docs
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get('paths', {})
            print(f"[OK] OpenAPI spec: {len(paths)} endpoints found")
            
            # List all endpoints
            banking_endpoints = []
            chat_endpoints = []
            other_endpoints = []
            
            for path, methods in paths.items():
                for method in methods.keys():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE']:
                        endpoint = f"{method.upper()} {path}"
                        if '/banking/' in path:
                            banking_endpoints.append(endpoint)
                        elif '/chat/' in path:
                            chat_endpoints.append(endpoint)
                        else:
                            other_endpoints.append(endpoint)
            
            print(f"\nBanking endpoints ({len(banking_endpoints)}):")
            for endpoint in banking_endpoints:
                print(f"  {endpoint}")
            
            print(f"\nChat endpoints ({len(chat_endpoints)}):")
            for endpoint in chat_endpoints:
                print(f"  {endpoint}")
            
            print(f"\nOther endpoints ({len(other_endpoints)}):")
            for endpoint in other_endpoints:
                print(f"  {endpoint}")
                
        else:
            print(f"[ERROR] OpenAPI spec: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] OpenAPI spec: {e}")
    
    # Test banking verify endpoint
    try:
        test_data = {"customer_id": "CUST001", "pin": "1234"}
        response = requests.post(f"{BASE_URL}/api/banking/verify", json=test_data, timeout=5)
        print(f"\n[OK] Banking verify endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"\n[ERROR] Banking verify endpoint: {e}")

if __name__ == "__main__":
    test_endpoints()