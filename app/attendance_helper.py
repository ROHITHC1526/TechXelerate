# Member-level attendance marking from QR scans

from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException
from datetime import datetime
import logging
from uuid import UUID as PythonUUID

from app.models import TeamMember

logger = logging.getLogger(__name__)


async def mark_attendance_from_qr(
    team_id: str,
    member_id: str,
    access_key: str,
    db: AsyncSession
) -> Dict:
    """
    Mark individual member as present based on QR scan.
    
    Args:
        team_id: Team ID from QR
        member_id: Member UUID from QR
        access_key: Member's access key from QR
        db: Database session
        
    Returns:
        Success response with member details
        
    Raises:
        HTTPException: If QR is invalid or member already checked in
    """
    try:
        # Query: SELECT * FROM team_members
        # WHERE id = member_id AND team_id = team_id AND access_key = access_key
        
        query = select(TeamMember).where(
            and_(
                TeamMember.id == PythonUUID(member_id),
                TeamMember.team_id == team_id,
                TeamMember.access_key == access_key
            )
        )
        
        result = await db.execute(query)
        member = result.scalars().first()
        
        # If not found → 404 Invalid QR
        if not member:
            logger.warning(f"❌ Invalid QR: member_id={member_id}, team_id={team_id}")
            raise HTTPException(
                status_code=404,
                detail="❌ Invalid QR code or member not found"
            )
        
        # If already present → return "Already marked"
        if member.attendance_status:
            logger.info(f"⚠️  Member {member.name} already marked present")
            return {
                "status": "already_present",
                "message": f"✅ {member.name} already marked present",
                "team_id": team_id,
                "member_name": member.name,
                "attendance_status": True,
                "checkin_time": member.checkin_time.isoformat() if member.checkin_time else None
            }
        
        # Else: mark as present
        member.attendance_status = True
        member.checkin_time = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"✅ {member.name} attendance marked at {member.checkin_time}")
        
        return {
            "status": "success",
            "message": f"✅ Attendance marked for {member.name}",
            "team_id": team_id,
            "member_name": member.name,
            "attendance_status": True,
            "checkin_time": member.checkin_time.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error marking attendance: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error marking attendance: {str(e)}"
        )
