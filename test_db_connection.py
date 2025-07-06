#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_db_connection():
    try:
        from app.db.session import session_manager
        from app.core.config import settings
        
        print("Testing database connection...")
        print(f"Database URL: {settings.DATABASE_URL}")
        
        # Initialize the session manager
        session_manager.init(settings.DATABASE_URL)
        
        # Test getting a session
        async for session in session_manager.get_db():
            print("✓ Database connection successful!")
            await session.close()
            break
            
        await session_manager.close()
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_db_connection())
    if not success:
        sys.exit(1)
