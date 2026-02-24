"""
Reset the database for testing.
This script deletes all data from the teams table.
WARNING: This will delete all registered teams and attendance records!
"""

import asyncio
import os
from sqlalchemy import text
from app.db import engine

async def reset_database():
    """Drop all tables and recreate empty structure."""
    async with engine.begin() as conn:
        # Drop all tables (teams and team_members)
        await conn.execute(text("DROP TABLE IF EXISTS team_members CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS teams CASCADE"))
        print("✓ Dropped teams and team_members tables")
        
        # Recreate schema by importing models
        from app.models import Base
        await conn.run_sync(Base.metadata.create_all)
        print("✓ Recreated empty database schema")
        
        # Verify
        result = await conn.execute(text("SELECT COUNT(*) FROM teams"))
        count = result.scalar()
        print(f"✓ Teams table has {count} records (should be 0)")
        result2 = await conn.execute(text("SELECT COUNT(*) FROM team_members"))
        count2 = result2.scalar()
        print(f"✓ Team_members table has {count2} records (should be 0)")

async def verify_connection():
    """Test database connection."""
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        if result.scalar() == 1:
            print("✓ Database connection successful")
            return True
    return False

async def main():
    """Main function."""
    print("=" * 60)
    print("DATABASE RESET - FOR TESTING ONLY")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will delete ALL teams and attendance data!")
    print()
    
    # Verify connection first
    if not await verify_connection():
        print("❌ Cannot connect to database. Check DATABASE_URL in .env")
        return
    
    # Confirm before proceeding
    response = input("Type 'yes' to proceed with database reset: ").strip().lower()
    if response != 'yes':
        print("✓ Cancelled. Database not modified.")
        return
    
    print()
    print("Resetting database...")
    try:
        await reset_database()
        print()
        print("=" * 60)
        print("✅ DATABASE RESET COMPLETE")
        print("=" * 60)
        print()
        print("You can now register new teams with the same email addresses.")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main())
