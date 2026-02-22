"""
Migration script to update database schema.
Drops and recreates the teams table with the new schema.
"""
import asyncio
from app.db import engine
from app.models import Base
from sqlalchemy import text

async def migrate_db():
    async with engine.begin() as conn:
        # Drop existing tables
        print("🔄 Dropping existing tables...")
        try:
            await conn.execute(text("DROP TABLE IF EXISTS teams CASCADE"))
            print("✅ Dropped teams table")
        except Exception as e:
            print(f"⚠️ Could not drop teams table: {e}")
        
        # Create new tables with updated schema
        print("🔄 Creating new tables with updated schema...")
        try:
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables created successfully!")
            print("\n📋 Final Schema:")
            print("  ✓ Removed 'semester' field")
            print("  ✓ Using 'access_key' as unique identifier for check-in verification")
            print("  ✓ attendance_status defaults to False (True after check-in)")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            raise

print("Running database schema migration...")
asyncio.run(migrate_db())
print("\n✅ Migration completed!")
