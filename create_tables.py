import asyncio
from app.db import engine
from app.models import Base

async def create_tables():
    print("Connected to:", engine.url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Tables created successfully!")

asyncio.run(create_tables())