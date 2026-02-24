# Hackathon Registration Backend

FastAPI backend for 6-Hour Hackathon Registration (CSE AI & ML) — minimal production-ready scaffold.

Run (local):

1. Copy `.env.example` to `.env` and edit values.
2. Install dependencies: `pip install -r requirements.txt`
3. Start services (docker-compose recommended):

```bash
docker-compose up --build
```

API endpoints are under `/api`.

---

## Troubleshooting

### "Email already registered" but database looks empty

The system checks the `team_members` table for existing leader emails while
registration is in progress. If you inspect the `teams` table in pgAdmin you
may see no rows while `team_members` still contains entries (especially
if records were manually deleted or an earlier migration went wrong). When
a leader row exists without a matching team record the backend now automatically
cleans up the orphan and allows the user to re‑register.

To manually inspect or delete orphaned entries:

```python
from app.db import AsyncSessionLocal
from app.models import TeamMember, Team
from sqlalchemy import delete, select

async with AsyncSessionLocal() as db:
    # find members with missing team
    q = await db.execute(
        select(TeamMember).outerjoin(Team, Team.team_id == TeamMember.team_id)
        .where(Team.team_id == None)
    )
    orphans = q.scalars().all()
    print(orphans)

    # remove all orphaned rows
    await db.execute(delete(TeamMember).where(TeamMember.team_id.notin_(select(Team.team_id))))
    await db.commit()
```

Alternatively run the `reset_db.py` script to drop and recreate all tables for a
clean slate.
