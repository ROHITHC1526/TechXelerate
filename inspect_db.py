#!/usr/bin/env python3
from app.db import AsyncSessionLocal
from app.models import TeamMember, Team
from sqlalchemy import select
import asyncio

async def show():
    async with AsyncSessionLocal() as db:
        res= await db.execute(select(TeamMember))
        members=res.scalars().all()
        print('members',len(members))
        for m in members:
            print(m.team_id, m.email, m.is_team_leader)
        res2= await db.execute(select(Team))
        teams=res2.scalars().all()
        print('teams',len(teams))
        for t in teams:
            print(t.team_id, t.team_name)

if __name__ == '__main__':
    asyncio.run(show())
