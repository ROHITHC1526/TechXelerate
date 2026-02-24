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
from app.utils import generate_next_team_id, generate_access_key, save_qr
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
# GENERATE QR FOR EACH MEMBER
# ============================================================

async def generate_member_qr_codes(
    team_id: str,
    members: List[Dict],
    out_dir: str = "assets"
) -> List[Dict]:

    try:
        qr_codes = []

        for member in members:

            payload = {
                "team_id": team_id,
                "member_id": member["member_id"],
                "access_key": member["access_key"]
            }

            qr_path = save_qr(
                payload,
                out_dir=out_dir,
                filename_prefix=f"{team_id}_{member['member_id']}"
            )

            qr_codes.append({
                "member_id": member["member_id"],
                "member_name": member["name"],
                "qr_path": qr_path
            })

            logger.info(f"✅ QR generated for {member['name']}")

        return qr_codes

    except Exception as e:
        logger.exception(f"❌ QR generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error generating QR codes"
        )   