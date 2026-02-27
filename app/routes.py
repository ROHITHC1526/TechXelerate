from fastapi import APIRouter, Depends, HTTPException, status, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .schemas import RegisterIn, OTPIn, TeamOut, AdminLogin, DownloadIDIn
from .db import get_db, AsyncSessionLocal
from .models import Team, TeamMember
from .config import settings
from .auth import create_access_token, get_password_hash, verify_password, get_current_admin
from .utils import generate_otp, generate_access_key, generate_team_id, generate_next_team_id
from .tasks import send_otp_email_sync
from .otp_manager import store_otp, get_otp, verify_otp as verify_otp_from_manager, delete_otp, store_registration_data, get_registration_data, delete_registration_data
from .email_service import EmailService
from .verify_otp_service import verify_otp_endpoint as enhanced_verify_otp
# QR scanning and check‑in removed; related module deleted

from datetime import datetime
import json
import logging
import os
import shutil
import asyncio
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# photo upload support removed – feature deprecated



def generate_team_id_sequential(seq: int) -> str:
    """Generate sequential Team ID format: HACK-001, HACK-002, etc."""
    return f"HACK-{seq:03d}"


# multipart registration endpoint removed – photos are no longer supported.
# Clients should use the simple /register route instead.
# Any request to this URL will now return 410 Gone.
@router.post("/register-multipart", status_code=status.HTTP_410_GONE)
async def register_multipart_removed():
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Photo upload registration has been removed. Use /register with JSON payload.")


@router.post("/register", status_code=202)
async def register(payload: RegisterIn, request: Request):
    """Register team and send OTP email directly (no Celery/Redis)."""
    ip = request.client.host
    
    # Generate and store OTP in memory
    otp = generate_otp()
    store_otp(payload.leader_email, otp, expiry_seconds=300)
    
    # Store registration data temporarily for OTP verification
    store_registration_data(payload.leader_email, payload.dict(), expiry_seconds=300)
    
    # Send OTP email directly (synchronous)
    otp_sent = False
    try:
        otp_sent = send_otp_email_sync(payload.leader_email, otp)
        if otp_sent:
            logger.info("✓ OTP sent directly to %s", payload.leader_email)
        else:
            logger.warning("✗ Failed to send OTP to %s", payload.leader_email)
    except Exception as e:
        logger.exception("✗ Exception sending OTP to %s: %s", payload.leader_email, str(e))
    
    if otp_sent:
        return {
            "status": "success",
            "message": f"✅ OTP sent successfully to {payload.leader_email}. Check your inbox (including spam folder). OTP expires in 5 minutes."
        }
    else:
        # In development, return OTP for testing
        logger.warning("⚠️ OTP email failed to send. SMTP might not be configured. Returning OTP for development testing.")
        return {
            "status": "warning",
            "message": "⚠️ OTP email sending failed. Check SMTP settings in .env file.",
            "otp": otp,  # Only in development
            "note": "To fix: Configure SMTP_HOST, SMTP_USER, SMTP_PASS in .env file"
        }




@router.post("/verify-otp", response_model=TeamOut)
async def verify_otp_endpoint(payload: OTPIn, db: AsyncSession = Depends(get_db)):
    """
    STEP 2: Verify OTP and create team record.
    Uses enhanced verify_otp_service with:
    - Rate limiting (3 attempts per 15 minutes)
    - Proper HTTP status codes (429, 410, 400, 409, 500)
    - Async PDF generation and email sending
    - Complete error handling and cleanup
    """
    return await enhanced_verify_otp(payload, db)


@router.get('/admin/export')

async def export_teams(domain: str = None, year: str = None, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    """Export teams as CSV. Filters: domain, year. Admin-only."""
    from io import StringIO
    import csv

    q = select(Team)
    if domain:
        q = q.where(Team.domain == domain)

    res = await db.execute(q)
    teams = res.scalars().all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["team_id", "team_name", "college_name", "domain", "total_members", "created_at"])
    
    for team in teams:
        members_q = await db.execute(
            select(TeamMember).where(TeamMember.team_id == team.team_id)
        )
        members = members_q.scalars().all()
        
        writer.writerow([
            team.team_id, 
            team.team_name, 
            team.college_name,
            team.domain, 
            len(members),
            team.created_at.isoformat() if team.created_at else ''
        ])

    from fastapi.responses import StreamingResponse
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type='text/csv', headers={"Content-Disposition": "attachment; filename=teams_export.csv"})


@router.get('/admin/teams')
async def list_teams(page: int = 1, page_size: int = 50, search: str = None, domain: str = None, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    """
    List teams (attendance tracking removed).
    
    Args:
        page: Page number (1-indexed)
        page_size: Results per page
        search: Search by team_id or team_name
        domain: Filter by domain
        db: Database session
        _admin: Authenticated admin user
    """
    q = select(Team)
    if search:
        q = q.where(Team.team_id.ilike(f"%{search}%"))
    if domain:
        q = q.where(Team.domain == domain)

    total_q = await db.execute(select(func.count(Team.id)))
    total = total_q.scalar() or 0
    q = q.offset((page-1)*page_size).limit(page_size)
    res = await db.execute(q)
    teams = res.scalars().all()
    
    out = []
    for team in teams:
        # Get member stats for this team
        members_q = await db.execute(
            select(TeamMember).where(TeamMember.team_id == team.team_id)
        )
        members = members_q.scalars().all()
        
        # Get team leader info
        leader = None
        for m in members:
            if m.is_team_leader:
                leader = m
                break
        
        out.append({
            'team_id': team.team_id,
            'team_name': team.team_name,
            'leader_name': leader.name if leader else 'N/A',
            'leader_email': leader.email if leader else 'N/A',
            'domain': team.domain,
            'total_members': len(members),
        })

    return { 'total': total, 'page': page, 'page_size': page_size, 'items': out }


@router.get("/stats")
async def stats(db: AsyncSession = Depends(get_db)):
    """Get hackathon statistics."""
    total_teams_q = await db.execute(select(func.count(Team.id)))
    total_teams = total_teams_q.scalar() or 0
    
    total_members_q = await db.execute(select(func.count(TeamMember.id)))
    total_members = total_members_q.scalar() or 0
    
    # attendance metrics removed
    domain_q = await db.execute(select(Team.domain, func.count(Team.id)).group_by(Team.domain))
    domain_dist = {row[0]: row[1] for row in domain_q.all()}
    
    return {
        "total_teams": total_teams,
        "total_members": total_members,
        "domain_distribution": domain_dist
    }


@router.post("/download-id")
async def download_id(payload: DownloadIDIn, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(Team).where(Team.team_id == payload.team_id, Team.access_key == payload.access_key))
    team = q.scalars().first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if not team.id_cards_pdf_path:
        raise HTTPException(status_code=404, detail="ID card not yet generated")
    return {"id_cards_pdf_path": team.id_cards_pdf_path}


@router.get("/download-id")
async def download_id_get(team_id: str, access_key: str, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(Team).where(Team.team_id == team_id, Team.access_key == access_key))
    team = q.scalars().first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found or invalid access key")
    if not team.id_cards_pdf_path or not team.qr_code_path:
        raise HTTPException(status_code=404, detail="Assets not yet generated")
    from fastapi.responses import FileResponse
    # Return the file response for the id card PDF
    return FileResponse(team.id_cards_pdf_path, media_type='application/pdf', filename=f"{team.team_id}_id.pdf")


@router.post("/checkin")
async def checkin(db: AsyncSession = Depends(get_db)):
    """Endpoint retained for compatibility but check-in is disabled."""
    raise HTTPException(status_code=410, detail="Check-in feature is disabled")


@router.post("/attendance/scan")
async def scan_attendance_qr(db: AsyncSession = Depends(get_db)):
    """
    **Check-in disabled**

    This endpoint no longer performs any scanning or attendance updates.
    All attempts receive a 410 response.
    """
    raise HTTPException(status_code=410, detail="Check-in feature is disabled")



@router.post("/attendance/scan-file")
async def scan_attendance_file(db: AsyncSession = Depends(get_db)):
    """
    **Check-in disabled**

    Attendance image scanning is not available. Requests will be rejected.
    """
    raise HTTPException(status_code=410, detail="Check-in feature is disabled")


@router.post("/attendance/scan-member")
async def scan_member_attendance(db: AsyncSession = Depends(get_db)):
    """
    **Member check-in disabled**

    This endpoint is disabled; attendance logic removed.
    """
    raise HTTPException(status_code=410, detail="Member check-in disabled")


@router.post("/attendance/scan-member-file")
async def scan_member_attendance_file(db: AsyncSession = Depends(get_db)):
    """
    **Member check-in disabled**

    File-based member scan is no longer supported.
    """
    raise HTTPException(status_code=410, detail="Member check-in disabled")


@router.get("/team/{team_id}")
async def get_team_by_id(team_id: str, db: AsyncSession = Depends(get_db)):
    """Get basic team information by `team_id`.

    Attendance fields were removed; this returns only static registration data.
    """
    try:
        team_q = await db.execute(select(Team).where(Team.team_id == team_id))
        team = team_q.scalars().first()
        
        if not team:
            raise HTTPException(status_code=404, detail=f"❌ Team {team_id} not found")
        
        logger.info(f"✅ Retrieved team info for id: {team_id}")
        
        return {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "leader_name": team.leader_name,
            "leader_email": team.leader_email,
            "leader_phone": team.leader_phone,
            "college_name": team.college_name,
            "year": team.year,
            "domain": team.domain,
            "created_at": team.created_at.isoformat() if team.created_at else None,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching team by id: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@router.post("/admin/login")
async def admin_login(payload: AdminLogin):
    if payload.username != settings.ADMIN_USERNAME or payload.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": "admin"})
    return {"access_token": token}


@router.post("/test-email")
async def test_email(payload: dict):
    """Test email sending directly via SMTP."""
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="email required")
    try:
        success = EmailService.send_otp_email(email, "000000")
        if success:
            return {"message": f"✅ Test email sent to {email}"}
        else:
            raise HTTPException(status_code=500, detail="❌ Failed to send email. Check SMTP configuration.")
    except Exception as e:
        logger.exception("Failed to send test email to %s", email)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/team/{team_id}/members")
async def get_team_members_attendance(team_id: str, db: AsyncSession = Depends(get_db)):
    """This endpoint is disabled; individual attendance tracking removed."""
    raise HTTPException(status_code=410, detail="Member attendance endpoint disabled")


@router.websocket('/ws/stats')
async def ws_stats(websocket: WebSocket):
    """WebSocket stats endpoint (simplified without Redis)."""
    await websocket.accept()
    try:
        # Simple implementation: send pong to keep connection alive
        import asyncio
        while True:
            await asyncio.sleep(30)
            try:
                await websocket.send_text('pong')
            except:
                break
    except WebSocketDisconnect:
        await pubsub.unsubscribe('stats')
        return
