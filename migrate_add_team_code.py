#!/usr/bin/env python
"""
Migration script to add team_code to existing teams.
Run this if you have existing teams without the new team_code field.

Usage:
    python migrate_add_team_code.py
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db import AsyncSessionLocal, engine, Base
from app.models import Team
from app.utils import generate_unique_team_code
from sqlalchemy import select, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_add_team_code():
    """Add team_code to existing teams that don't have one."""
    
    logger.info("🚀 Starting migration: Add team_code to existing teams")
    
    try:
        # First ensure the team_code column exists
        async with engine.begin() as conn:
            try:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ Database schema updated if needed")
            except Exception as e:
                logger.warning(f"⚠️ Schema update info: {e}")
        
        # Connect to database and migrate
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Get all teams without team_code
                result = await session.execute(
                    select(Team).where(Team.team_code == None)
                )
                teams = result.scalars().all()
                
                if not teams:
                    logger.info("✅ No teams to migrate - all have team_code!")
                    return
                
                logger.info(f"📋 Found {len(teams)} teams without team_code")
                
                updated_count = 0
                for idx, team in enumerate(teams, 1):
                    try:
                        team.team_code = generate_unique_team_code()
                        updated_count += 1
                        logger.info(
                            f"  [{idx}/{len(teams)}] ✅ {team.team_id} → Code: {team.team_code}"
                        )
                    except Exception as e:
                        logger.error(f"  [{idx}/{len(teams)}] ❌ Error for {team.team_id}: {e}")
                
                # Commit changes
                try:
                    await session.commit()
                    logger.info(f"\n✅ Migration complete!")
                    logger.info(f"   • Updated: {updated_count} teams")
                    logger.info(f"   • Total teams: {len(teams)}")
                except Exception as e:
                    logger.error(f"❌ Failed to commit changes: {e}")
                    await session.rollback()
                    raise
    
    except Exception as e:
        logger.exception(f"❌ Migration failed: {e}")
        sys.exit(1)


async def verify_migration():
    """Verify that all teams have team_code."""
    
    logger.info("\n🔍 Verifying migration...")
    
    async with AsyncSessionLocal() as session:
        # Check teams with team_code
        result_with = await session.execute(
            select(Team).where(Team.team_code != None)
        )
        teams_with_code = result_with.scalars().all()
        
        # Check teams without team_code
        result_without = await session.execute(
            select(Team).where(Team.team_code == None)
        )
        teams_without_code = result_without.scalars().all()
        
        total = len(teams_with_code) + len(teams_without_code)
        
        logger.info(f"\n📊 Migration Results:")
        logger.info(f"   • Teams with team_code: {len(teams_with_code)}")
        logger.info(f"   • Teams without team_code: {len(teams_without_code)}")
        logger.info(f"   • Total teams: {total}")
        
        if teams_without_code:
            logger.warning(f"\n⚠️ Warning: {len(teams_without_code)} teams still without team_code:")
            for team in teams_without_code[:10]:  # Show first 10
                logger.warning(f"   - {team.team_id}: {team.team_name}")
            if len(teams_without_code) > 10:
                logger.warning(f"   ... and {len(teams_without_code) - 10} more")
        else:
            logger.info("\n✅ All teams have been assigned team_code!")


async def main():
    """Run migration."""
    try:
        await migrate_add_team_code()
        await verify_migration()
        logger.info("\n✅ Migration script completed successfully!")
    except KeyboardInterrupt:
        logger.info("\n⏹️ Migration cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
