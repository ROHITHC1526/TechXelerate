"""
Database Migration Script for TechXelarate Hackathon System.
Ensures schema is properly synced and all required columns exist.

Usage:
    python migrate_db.py
"""

import asyncio
import logging
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import Team
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_database():
    """
    Perform database migrations to ensure schema is up-to-date.
    
    Steps:
    1. Drop and recreate all tables (DEVELOPMENT ONLY)
    2. Or: Alter table to add missing columns (PRODUCTION)
    """
    
    # Create async engine - convert driver to asyncpg if needed
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql+psycopg2://"):
        db_url = db_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(db_url, echo=False)
    
    try:
        logger.info("=" * 60)
        logger.info("Starting Database Migration")
        logger.info("=" * 60)
        
        # Create all tables (safe - will not drop existing)
        async with engine.begin() as conn:
            # Ensure schema is created
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Base schema created/verified")
            
            # Check if leader_email has unique constraint
            result = await conn.execute(
                text("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE table_name='teams' AND constraint_type='UNIQUE' 
                        AND constraint_name LIKE '%leader_email%'
                    )
                """)
            )
            email_unique_exists = result.scalar()
            
            if not email_unique_exists:
                logger.info("📝 Adding unique constraint to leader_email...")
                try:
                    await conn.execute(text("""
                        ALTER TABLE teams 
                        ADD CONSTRAINT uq_teams_leader_email UNIQUE (leader_email);
                    """))
                    logger.info("✅ Unique constraint added to leader_email")
                except Exception as e:
                    logger.warning(f"⚠️  Unique constraint: {e}")
            else:
                logger.info("✅ Unique constraint on leader_email already exists")
            
            # (Removed legacy team_code index checks; project uses team_id)
            
            # Check and create index on leader_email
            result = await conn.execute(
                text("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_indexes 
                        WHERE tablename='teams' AND indexname='ix_teams_leader_email'
                    )
                """)
            )
            email_index_exists = result.scalar()
            
            if not email_index_exists:
                logger.info("📝 Adding index on leader_email...")
                try:
                    await conn.execute(text("""
                        CREATE INDEX ix_teams_leader_email ON teams(leader_email);
                    """))
                    logger.info("✅ Index created on leader_email")
                except Exception as e:
                    logger.warning(f"⚠️  leader_email index: {e}")
            else:
                logger.info("✅ Index on leader_email already exists")
            
            # Check and create index on team_id
            result = await conn.execute(
                text("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_indexes 
                        WHERE tablename='teams' AND indexname='ix_teams_team_id'
                    )
                """)
            )
            team_id_index_exists = result.scalar()
            
            if not team_id_index_exists:
                logger.info("📝 Adding index on team_id...")
                try:
                    await conn.execute(text("""
                        CREATE INDEX ix_teams_team_id ON teams(team_id);
                    """))
                    logger.info("✅ Index created on team_id")
                except Exception as e:
                    logger.warning(f"⚠️  team_id index: {e}")
            else:
                logger.info("✅ Index on team_id already exists")
            
            await conn.commit()
        
        logger.info("=" * 60)
        logger.info("✅ Database migration completed successfully!")
        logger.info("=" * 60)
        
        # Display table info
        async with engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = 'teams'
                    ORDER BY ordinal_position;
                """)
            )
            
            logger.info("\n📋 Teams Table Schema:")
            logger.info("-" * 80)
            for column_name, data_type, is_nullable, column_default in result:
                nullable_str = "NULL" if is_nullable == "YES" else "NOT NULL"
                default_str = f"Default: {column_default}" if column_default else ""
                logger.info(f"  {column_name:<20} {data_type:<15} {nullable_str:<10} {default_str}")
            logger.info("-" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database migration failed: {e}")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(migrate_database())
    exit(0 if success else 1)
