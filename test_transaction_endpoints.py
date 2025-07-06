#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_transaction_endpoints():
    """Test transaction endpoints using FastAPI TestClient"""
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        print("Testing transaction endpoints...")
        
        # Create test client
        client = TestClient(app)
        
        # Test getting transactions list - this requires X-User-ID header
        print("1. Testing GET /api/v1/transactions/ (this should fail without proper headers)")
        response = client.get("/api/v1/transactions/")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("    Transaction endpoint properly requires user ID (expected 400)")
        elif response.status_code == 200:
            transactions = response.json()
            print(f"    Transaction endpoint works - found {len(transactions)} transactions")
        else:
            print(f"     Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Test with X-User-ID header
        print("\n2. Testing GET /api/v1/transactions/ with X-User-ID header")
        headers = {"X-User-ID": "1"}  # Use a test user ID
        response_with_header = client.get("/api/v1/transactions/", headers=headers)
        print(f"   Status Code: {response_with_header.status_code}")
        
        if response_with_header.status_code == 200:
            transactions = response_with_header.json()
            print(f"    Transaction endpoint works with headers - found {len(transactions)} transactions")
        else:
            print(f"    Transaction endpoint failed: {response_with_header.text}")
            return False
        
        print("\n Transaction endpoint AttributeError is fixed!")
        return True
        
    except Exception as e:
        print(f" Transaction endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_transaction_endpoints()
    if not success:
        sys.exit(1)
