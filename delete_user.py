#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def delete_user_by_email(email: str):
    """
    Simple utility to delete a user by email address
    """
    try:
        from app.db.session import session_manager
        from app.core.config import settings
        from app.db.repositories import user_repo
        
        print(f"🗑️  Deleting user: {email}")
        
        # Initialize the database session manager
        session_manager.init(settings.DATABASE_URL)
        
        async for session in session_manager.get_db():
            existing_user = await user_repo.get_by_email(session, email)
            if existing_user:
                print(f"Found user: ID={existing_user.id}, Username={existing_user.username}")
                
                # Delete the user
                await session.delete(existing_user)
                await session.commit()
                print(f" User '{email}' deleted successfully!")
                
            else:
                print(f" User '{email}' not found in database")
            
            await session.close()
            break
        
        await session_manager.close()
        return True
        
    except Exception as e:
        print(f" Failed to delete user '{email}': {e}")
        import traceback
        traceback.print_exc()
        try:
            await session_manager.close()
        except:
            pass
        return False

async def list_all_users():
    """
    List all users in the database
    """
    try:
        from app.db.session import session_manager
        from app.core.config import settings
        from sqlalchemy import select
        from app.models.db_models import User
        
        print(" Listing all users in database:")
        
        # Initialize the database session manager
        session_manager.init(settings.DATABASE_URL)
        
        async for session in session_manager.get_db():
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            if users:
                print(f"Found {len(users)} users:")
                for user in users:
                    print(f"  - ID: {user.id}, Email: {user.email}, Username: {user.username}")
            else:
                print("No users found in database")
            
            await session.close()
            break
        
        await session_manager.close()
        return True
        
    except Exception as e:
        print(f" Failed to list users: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python delete_user.py <email>           # Delete specific user")
        print("  python delete_user.py --list            # List all users")
        print("  python delete_user.py --help            # Show this help")
        print("")
        print("Examples:")
        print("  python delete_user.py tompsonphilip446@gmail.com")
        print("  python delete_user.py test2@example.com")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "--list":
        success = asyncio.run(list_all_users())
    elif command == "--help":
        print("Delete User Utility")
        print("==================")
        print("This utility helps you delete users from your self-checkout system database.")
        print("")
        print("Commands:")
        print("  <email>     Delete user with specified email")
        print("  --list      List all users in database")
        print("  --help      Show this help message")
        sys.exit(0)
    else:
        # Treat as email to delete
        email = command
        success = asyncio.run(delete_user_by_email(email))
    
    if not success:
        sys.exit(1)
