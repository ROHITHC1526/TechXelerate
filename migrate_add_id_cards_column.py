import asyncio
from sqlalchemy import text
from app.db import engine

async def migrate():
    """Add id_cards_pdf_path column to teams table if it doesn't exist"""
    async with engine.begin() as conn:
        try:
            # Check if column exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'teams' AND column_name = 'id_cards_pdf_path'
                )
            """))
            column_exists = result.scalar()
            
            if not column_exists:
                print("Adding id_cards_pdf_path column to teams table...")
                await conn.execute(text("""
                    ALTER TABLE teams ADD COLUMN id_cards_pdf_path VARCHAR(512)
                """))
                print("✅ Column added successfully!")
            else:
                print("✅ Column already exists!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(migrate())
