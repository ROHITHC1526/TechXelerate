#!/usr/bin/env python3
"""
Apply database schema fix without requiring psql client
"""
import sys
import asyncio
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

async def main():
    print("=" * 70)
    print("DATABASE SCHEMA FIX")
    print("=" * 70)
    print()
    
    try:
        # Import after path is set
        from app.db import AsyncSessionLocal, engine
        from sqlalchemy import text
        
        print("✅ Connecting to database...")
        
        async with AsyncSessionLocal() as session:
            try:
                # Test connection
                result = await session.execute(text("SELECT version();"))
                version = result.fetchone()
                print(f"✅ Connected to PostgreSQL: {version[0][:50]}...")
                print()
                
                # Step 1: Make old columns nullable
                print("Step 1: Making old columns nullable...")
                nullable_commands = [
                    "ALTER TABLE teams ALTER COLUMN IF EXISTS leader_name DROP NOT NULL;",
                    "ALTER TABLE teams ALTER COLUMN IF EXISTS leader_email DROP NOT NULL;",
                    "ALTER TABLE teams ALTER COLUMN IF EXISTS leader_phone DROP NOT NULL;",
                    "ALTER TABLE teams ALTER COLUMN IF EXISTS year DROP NOT NULL;",
                ]
                
                for cmd in nullable_commands:
                    try:
                        await session.execute(text(cmd))
                        print(f"  ✅ {cmd[:50]}...")
                    except Exception as e:
                        print(f"  ⚠️  {cmd[:50]}... (might already be done)")
                
                await session.commit()
                print()
                
                # Step 2: Drop old columns
                print("Step 2: Dropping old conflicting columns...")
                drop_commands = [
                    "ALTER TABLE teams DROP COLUMN IF EXISTS leader_name CASCADE;",
                    "ALTER TABLE teams DROP COLUMN IF EXISTS leader_email CASCADE;",
                    "ALTER TABLE teams DROP COLUMN IF EXISTS leader_phone CASCADE;",
                    "ALTER TABLE teams DROP COLUMN IF EXISTS year CASCADE;",
                    "ALTER TABLE teams DROP COLUMN IF EXISTS team_members CASCADE;",
                    "ALTER TABLE teams DROP COLUMN IF EXISTS access_key CASCADE;",
                    "ALTER TABLE teams DROP COLUMN IF EXISTS qr_code_path CASCADE;",
                    "ALTER TABLE teams DROP COLUMN IF EXISTS id_cards_pdf_path CASCADE;",
                    "ALTER TABLE teams DROP COLUMN IF EXISTS attendance_status CASCADE;",
                    "ALTER TABLE teams DROP COLUMN IF EXISTS checkin_time CASCADE;",
                    "ALTER TABLE teams DROP COLUMN IF EXISTS checkout_time CASCADE;",
                ]
                
                for cmd in drop_commands:
                    try:
                        await session.execute(text(cmd))
                        print(f"  ✅ {cmd[:50]}...")
                    except Exception as e:
                        print(f"  ⚠️  {cmd[:50]}...")
                
                await session.commit()
                print()
                
                # Step 3: Create team_members table if not exists
                print("Step 3: Creating team_members table...")
                create_team_members = """
                CREATE TABLE IF NOT EXISTS team_members (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    team_id VARCHAR(32) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    phone VARCHAR(50) NOT NULL,
                    photo_path VARCHAR(512),
                    is_team_leader BOOLEAN DEFAULT FALSE,
                    access_key VARCHAR(64) UNIQUE NOT NULL,
                    attendance_status BOOLEAN DEFAULT FALSE,
                    checkin_time TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    CONSTRAINT fk_team_id FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE
                );
                """
                
                await session.execute(text(create_team_members))
                await session.commit()
                print("  ✅ team_members table created")
                print()
                
                # Step 4: Create indexes
                print("Step 4: Creating indexes...")
                index_commands = [
                    "CREATE INDEX IF NOT EXISTS idx_team_members_team_id ON team_members(team_id);",
                    "CREATE INDEX IF NOT EXISTS idx_team_members_email ON team_members(email);",
                    "CREATE INDEX IF NOT EXISTS idx_team_members_attendance ON team_members(attendance_status);",
                    "CREATE INDEX IF NOT EXISTS idx_team_members_access_key ON team_members(access_key);",
                    "CREATE INDEX IF NOT EXISTS idx_teams_team_id ON teams(team_id);",
                ]
                
                for cmd in index_commands:
                    try:
                        await session.execute(text(cmd))
                        print(f"  ✅ {cmd[:50]}...")
                    except Exception as e:
                        print(f"  ⚠️  {cmd[:50]}...")
                
                await session.commit()
                print()
                
                # Step 5: Verify final schema
                print("Step 5: Verifying final schema...")
                verify_teams = """
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'teams' 
                ORDER BY ordinal_position;
                """
                
                result = await session.execute(text(verify_teams))
                teams_schema = result.fetchall()
                print("  Teams table columns:")
                for row in teams_schema:
                    nullable_text = "NULLABLE" if row[2] else "NOT NULL"
                    print(f"    - {row[0]:30} {row[1]:20} {nullable_text}")
                
                print()
                
                verify_members = """
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'team_members' 
                ORDER BY ordinal_position;
                """
                
                result = await session.execute(text(verify_members))
                members_schema = result.fetchall()
                
                if members_schema:
                    print("  ✅ team_members table exists with columns:")
                    for row in members_schema:
                        print(f"    - {row[0]}")
                else:
                    print("  ❌ team_members table not found!")
                
                print()
                print("=" * 70)
                print("✅ DATABASE FIX COMPLETE!")
                print("=" * 70)
                print()
                print("Next steps:")
                print("  1. Restart backend: docker-compose down && docker-compose up -d")
                print("  2. Test API: curl http://localhost:8000/api/stats")
                print()
                
            except Exception as e:
                print(f"❌ Error during fix: {e}")
                import traceback
                traceback.print_exc()
                await session.rollback()
                return False
    
    except Exception as e:
        print(f"❌ Connection error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
