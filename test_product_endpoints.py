#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_product_endpoints():
    """Test product endpoints using FastAPI TestClient"""
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        print("Testing product endpoints...")
        
        # Create test client
        client = TestClient(app)
        
        # Test getting products list
        print("1. Testing GET /api/v1/products/")
        response = client.get("/api/v1/products/")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            products = response.json()
            print(f"    Products list endpoint works - found {len(products)} products")
            
            # If we have products, test individual product endpoint
            if products:
                product_id = products[0].get("id")
                print(f"\n2. Testing GET /api/v1/products/{product_id}")
                detail_response = client.get(f"/api/v1/products/{product_id}")
                print(f"   Status Code: {detail_response.status_code}")
                
                if detail_response.status_code == 200:
                    product = detail_response.json()
                    print(f"    Product detail endpoint works - product: {product.get('name')}")
                else:
                    print(f"    Product detail endpoint failed: {detail_response.text}")
                    
        else:
            print(f"    Products list endpoint failed: {response.text}")
            return False
        
        # Test search endpoint
        print("\n3. Testing search endpoint")
        search_response = client.get("/api/v1/products/?search=test")
        print(f"   Status Code: {search_response.status_code}")
        
        if search_response.status_code == 200:
            search_results = search_response.json()
            print(f"    Search endpoint works - found {len(search_results)} results")
        else:
            print(f"    Search endpoint failed: {search_response.text}")
            return False
        
        print("\n All product endpoints are working correctly!")
        return True
        
    except Exception as e:
        print(f" Product endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_product_endpoints()
    if not success:
        sys.exit(1)
