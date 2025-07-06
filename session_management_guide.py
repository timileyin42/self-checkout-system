#!/usr/bin/env python3

import asyncio
import sys
import os
import uuid
import json

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_session_management():
    """Test session management and show how to use session IDs"""
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        print("=== Session ID Management Demo ===")
        
        # Create test client
        client = TestClient(app)
        
        # 1. Generate a session ID (this would normally be done by the frontend)
        session_id = str(uuid.uuid4())
        print(f"1. Generated Session ID: {session_id}")
        print("   (In a real app, this would be stored in browser localStorage)")
        
        # 2. Test endpoints that require session ID
        print(f"\n2. Testing endpoints with X-Session-ID header")
        
        # Test an endpoint that requires session ID (let's check cart endpoints)
        headers = {
            "X-Session-ID": session_id,
            "Content-Type": "application/json"
        }
        
        # Let's check what endpoints actually require session ID
        print("\n3. Looking for endpoints that use session ID...")
        
        # Test if there are any cart endpoints
        endpoints_to_test = [
            "/api/v1/cart/",
            "/api/v1/cart/items",
            "/api/v1/products/"  # This one shouldn't require session ID
        ]
        
        for endpoint in endpoints_to_test:
            print(f"\n   Testing {endpoint}")
            try:
                # Test without session ID first
                response_no_session = client.get(endpoint)
                print(f"     Without session ID: {response_no_session.status_code}")
                
                # Test with session ID
                response_with_session = client.get(endpoint, headers=headers)
                print(f"     With session ID: {response_with_session.status_code}")
                
                if response_with_session.status_code == 200:
                    print(f"      {endpoint} works with session ID")
                elif response_no_session.status_code == 200:
                    print(f"      {endpoint} works without session ID (doesn't require it)")
                else:
                    print(f"       {endpoint} status: {response_with_session.status_code}")
                    
            except Exception as e:
                print(f"      Error testing {endpoint}: {e}")
        
        # 4. Show how to manage session in a real application
        print(f"\n4. Session Management Best Practices:")
        print(f"   Frontend JavaScript example:")
        print(f"""
   // Generate or get existing session ID
   let sessionId = localStorage.getItem('sessionId');
   if (!sessionId) {{
       sessionId = '{session_id}';
       localStorage.setItem('sessionId', sessionId);
   }}
   
   // Use in API calls
   fetch('/api/v1/cart/', {{
       headers: {{
           'X-Session-ID': sessionId,
           'Content-Type': 'application/json'
       }}
   }})
   """)
        
        print(f"\n5. Session ID Lifecycle:")
        print(f"   - Guest visits site → Generate session ID")
        print(f"   - User adds items to cart → Use session ID")
        print(f"   - User logs in → Merge session cart with user cart")
        print(f"   - User logs out → Keep session ID for guest cart")
        
        return True
        
    except Exception as e:
        print(f" Session management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_session_api_examples():
    """Show practical API usage examples with session IDs"""
    
    session_id = str(uuid.uuid4())
    user_id = 123  # Example user ID from login
    
    print("\n=== API Usage Examples ===")
    
    print("\n1. Guest User (before login):")
    print(f"   Session ID: {session_id}")
    print(f"   Headers: {{'X-Session-ID': '{session_id}'}}")
    
    print(f"""
   curl -X GET http://localhost:8000/api/v1/cart/ \\
        -H 'X-Session-ID: {session_id}'
   """)
    
    print(f"\n2. Logged-in User:")
    print(f"   User ID: {user_id}")
    print(f"   Session ID: {session_id} (optional, for cart merging)")
    print(f"   Headers: {{'X-User-ID': '{user_id}', 'X-Session-ID': '{session_id}', 'Authorization': 'Bearer TOKEN'}}")
    
    print(f"""
   curl -X GET http://localhost:8000/api/v1/transactions/ \\
        -H 'Authorization: Bearer YOUR_TOKEN' \\
        -H 'X-User-ID: {user_id}'
   """)
    
    print(f"\n3. Cart Merge (when user logs in):")
    print(f"""
   curl -X POST http://localhost:8000/api/v1/auth/merge-cart \\
        -H 'Authorization: Bearer YOUR_TOKEN' \\
        -H 'X-User-ID: {user_id}' \\
        -H 'X-Session-ID: {session_id}'
   """)

async def test_auth_with_session_flow():
    """Test a complete authentication flow with session management"""
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        print("\n=== Complete Auth + Session Flow ===")
        
        client = TestClient(app)
        session_id = str(uuid.uuid4())
        
        print(f"1. Guest session ID: {session_id}")
        
        # Step 1: Login to get user info
        print("\n2. Logging in...")
        login_data = {
            "username": "tompsonphilip446@gmail.com",
            "password": "@Maverick42"
        }
        
        login_response = client.post("/api/v1/auth/token", data=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data["access_token"]
            print("    Login successful!")
            
            # Step 2: Get user info
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = client.get("/api/v1/auth/me", headers=headers)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                user_id = user_data["id"]
                print(f"    User ID: {user_id}")
                
                # Step 3: Show headers for different scenarios
                print(f"\n3. Headers for API calls:")
                
                print(f"\n   For transactions (requires auth + user ID):")
                transaction_headers = {
                    "Authorization": f"Bearer {access_token}",
                    "X-User-ID": str(user_id)
                }
                print(f"   {json.dumps(transaction_headers, indent=6)}")
                
                print(f"\n   For cart merge (auth + user ID + session ID):")
                merge_headers = {
                    "Authorization": f"Bearer {access_token}",
                    "X-User-ID": str(user_id),
                    "X-Session-ID": session_id
                }
                print(f"   {json.dumps(merge_headers, indent=6)}")
                
                # Step 4: Test a transaction endpoint
                print(f"\n4. Testing transaction endpoint...")
                trans_response = client.get("/api/v1/transactions/", headers=transaction_headers)
                print(f"   Status: {trans_response.status_code}")
                
                if trans_response.status_code == 200:
                    transactions = trans_response.json()
                    print(f"    Found {len(transactions)} transactions")
                
                return True
            else:
                print(f"    Failed to get user info: {user_response.status_code}")
        else:
            print(f"    Login failed: {login_response.status_code}")
            
        return False
        
    except Exception as e:
        print(f" Auth flow test failed: {e}")
        return False

if __name__ == "__main__":
    print("Session ID Management Guide")
    print("=" * 50)
    
    # Test session management
    success1 = test_session_management()
    
    # Show API examples
    show_session_api_examples()
    
    # Test complete flow
    success2 = asyncio.run(test_auth_with_session_flow())
    
    if success1 and success2:
        print("\n Session management guide completed successfully!")
        print("\n Key Takeaways:")
        print("   - Session ID: Use UUID for guest users")
        print("   - Store in browser localStorage/sessionStorage")
        print("   - X-User-ID: From login response")
        print("   - X-Session-ID: For cart/session management")
        print("   - Both can be used together for cart merging")
    else:
        print("\n Some tests failed!")
        sys.exit(1)
