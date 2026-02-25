"""
Team Creation & QR Service
Creates Team and TeamMember records with unique QR per member.
"""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging
import uuid
from typing import List, Dict, Optional

from app.models import Team, TeamMember
from app.utils import generate_next_team_id, generate_access_key
from app.otp_manager import get_registration_data, delete_registration_data

logger = logging.getLogger(__name__)


# ============================================================
# CREATE TEAM + MEMBERS
# ============================================================

async def create_team_and_members(
    leader_email: str,
    db: AsyncSession,
    registration_data: Optional[Dict] = None
) -> Dict:

    try:
        # Fetch registration data
        if not registration_data:
            registration_data = get_registration_data(leader_email)

        if not registration_data:
            raise HTTPException(
                status_code=400,
                detail="No registration data found"
            )

        logger.info(f"📝 Creating team for {leader_email}")

        # Generate team ID
        team_id = await generate_next_team_id(db)
        logger.info(f"✅ Generated team_id: {team_id}")

        # Create team
        team = Team(
            team_id=team_id,
            team_name=registration_data.get("team_name"),
            college_name=registration_data.get("college_name"),
            domain=registration_data.get("domain"),
        )

        db.add(team)
        await db.flush()

        # Get members list
        team_members = registration_data.get("team_members", [])

        if not isinstance(team_members, list) or not team_members:
            raise HTTPException(
                status_code=400,
                detail="No team members provided"
            )

        created_members = []

        for idx, member_data in enumerate(team_members):

            if not isinstance(member_data, dict):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid member data format"
                )

            access_key = generate_access_key(64)

            member = TeamMember(
                id=uuid.uuid4(),
                team_id=team_id,
                name=member_data.get("name"),
                email=member_data.get("email"),
                phone=member_data.get("phone"),
                photo_path=member_data.get("photo_path"),
                is_team_leader=(idx == 0),
                access_key=access_key,
                attendance_status=False,
                checkin_time=None
            )

            db.add(member)

            created_members.append({
                "member_id": str(member.id),
                "name": member.name,
                "email": member.email,
                "is_team_leader": member.is_team_leader,
                "access_key": access_key
            })

            logger.info(f"✅ Member created: {member.name}")

        await db.commit()

        logger.info(f"✅ Team {team_id} created successfully")

        delete_registration_data(leader_email)

        return {
            "team_id": team_id,
            "member_count": len(created_members),
            "members": created_members
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception(f"❌ Team creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error creating team"
        )


# ============================================================
# GENERATE QR FOR EACH MEMBER (LEGACY)
# This function is no longer used by the manual check-in workflow.
# It remains only to satisfy existing clients that still call it.
# ============================================================

async def generate_member_qr_codes(
    team_id: str,
    members: List[Dict],
    out_dir: str = "assets"
) -> List[Dict]:
    """Legacy stub: return an empty list and log a warning.

    The original implementation generated PNG files using the
    :func:`utils.save_qr` helper.  That behavior is not needed for the
    current attendance system so the stub simply avoids filesystem
    operations and does not import the QR library.
    """
    logger.warning("generate_member_qr_codes called but QR generation is deprecated; returning empty list")
    return []
   