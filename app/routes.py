from fastapi import APIRouter, Depends, HTTPException, status, Request, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .schemas import RegisterIn, OTPIn, TeamOut, AdminLogin, DownloadIDIn, CheckinIn, AttendanceQRIn
from .db import get_db, AsyncSessionLocal
from .models import Team
from .config import settings
from .auth import create_access_token, get_password_hash, verify_password, get_current_admin
from .utils import generate_otp, generate_access_key, generate_team_id, generate_unique_team_code, generate_participant_id, create_attendance_qr_data
from .tasks import send_otp_email_sync, generate_assets_and_email
from .otp_manager import store_otp, get_otp, verify_otp as verify_otp_from_manager, delete_otp, store_registration_data, get_registration_data, delete_registration_data
from .email_service import EmailService
from .verify_otp_service import verify_otp_endpoint as enhanced_verify_otp
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

# Ensure uploads directory exists
UPLOADS_DIR = os.path.join(os.getcwd(), "uploads")
Path(UPLOADS_DIR).mkdir(parents=True, exist_ok=True)


async def save_upload_file(upload_file: UploadFile, team_id: str = None) -> str:
    """
    Save uploaded file to uploads directory.
    
    Args:
        upload_file: The file uploaded by user
        team_id: Optional team ID for organizing files
        
    Returns:
        Path to saved file
        
    Raises:
        HTTPException: If file type is invalid or save fails
    """
    # Validate file type
    allowed_types = {'image/jpeg', 'image/png', 'image/jpg'}
    if upload_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"❌ Invalid file type. Only JPEG and PNG images are allowed. Got: {upload_file.content_type}"
        )
    
    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    file_content = await upload_file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="❌ File too large. Maximum size is 5MB"
        )
    
    # Generate safe filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_ext = ".jpg" if upload_file.content_type in {'image/jpeg', 'image/jpg'} else ".png"
    filename = f"{team_id or 'temp'}_{timestamp}{file_ext}"
    
    filepath = os.path.join(UPLOADS_DIR, filename)
    
    try:
        # Write file
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"✓ File saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"❌ Failed to save file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


def generate_team_id_sequential(seq: int) -> str:
    """Generate sequential Team ID format: HACK-001, HACK-002, etc."""
    return f"HACK-{seq:03d}"


@router.post("/register-multipart", status_code=202)
async def register_multipart(
    team_name: str = Form(...),
    leader_name: str = Form(...),
    leader_email: str = Form(...),
    leader_phone: str = Form(...),
    college_name: str = Form(...),
    year: str = Form(...),
    domain: str = Form(...),
    team_members_json: str = Form(...),
    photos: list[UploadFile] = File(default=[]),
    leader_photo: UploadFile | None = File(default=None),
    request: Request = None
):
    """
    Register team with photo uploads - STEP 1: Send OTP
    Accepts multipart/form-data with file uploads.
    Returns OTP sent message, requiring verification before team is created.
    
    team_members_json: JSON string of [{name, email, phone}, ...]
    photos: List of photo files for team members (optional)
    leader_photo: Photo file for team leader (optional)
    """
    try:
        # Parse team members from JSON
        team_members = json.loads(team_members_json)
        if not isinstance(team_members, list):
            raise ValueError("team_members must be a list")
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid team_members JSON: {str(e)}")
    
    # Save team leader photo (first member is leader)
    leader_photo_path = None
    if leader_photo:
        try:
            leader_photo_path = await save_upload_file(leader_photo, team_id="leader")
            logger.info(f"✓ Photo saved for team leader: {leader_photo_path}")
        except HTTPException as he:
            logger.warning(f"⚠️ Could not save photo for team leader: {he.detail}")
    
    # Save photos and build team members with photo paths
    team_members_with_photos = []
    for idx, member in enumerate(team_members):
        member_dict = {
            'name': member.get('name', ''),
            'email': member.get('email', ''),
            'phone': member.get('phone', ''),
            'is_team_leader': False
        }
        
        # Try to save photo if provided
        if idx < len(photos) and photos[idx]:
            try:
                photo_path = await save_upload_file(photos[idx], team_id=f"member_{idx}")
                member_dict['photo_path'] = photo_path
                logger.info(f"✓ Photo saved for member {idx}: {photo_path}")
            except HTTPException as he:
                logger.warning(f"⚠️ Could not save photo for member {idx}: {he.detail}")
        
        team_members_with_photos.append(member_dict)
    
    # Add team leader as first team member
    leader_member = {
        'name': leader_name,
        'email': leader_email,
        'phone': leader_phone,
        'is_team_leader': True
    }
    if leader_photo_path:
        leader_member['photo_path'] = leader_photo_path
    
    all_members = [leader_member] + team_members_with_photos
    
    # Convert team members to pipe-separated format
    team_members_formatted = []
    for idx, member in enumerate(all_members):
        parts = [member['name'], member['email'], member['phone']]
        if member.get('photo_path'):
            parts.append(member['photo_path'])
        parts.append('TEAM_LEAD' if member.get('is_team_leader') else 'MEMBER')
        team_members_formatted.append('|'.join(parts))
    
    # Prepare registration data
    registration_data = {
        'team_name': team_name,
        'leader_name': leader_name,
        'leader_email': leader_email,
        'leader_phone': leader_phone,
        'college_name': college_name,
        'year': year,
        'domain': domain,
        'team_members': team_members_formatted,
    }
    
    # Generate OTP
    otp = generate_otp()
    
    # Store OTP (5 minutes)
    store_otp(leader_email, otp, expiry_seconds=300)
    
    # Store registration data (5 minutes)
    store_registration_data(leader_email, registration_data, expiry_seconds=300)
    
    # Send OTP email
    otp_sent = False
    try:
        logger.info(f"📧 Sending OTP email to {leader_email}")
        otp_sent = send_otp_email_sync(leader_email, otp)
        if otp_sent:
            logger.info(f"✅ OTP email sent to {leader_email}")
        else:
            logger.warning(f"⚠️ Failed to send OTP email to {leader_email}")
    except Exception as e:
        logger.exception(f"⚠️ Exception sending OTP: {e}")
    
    if otp_sent:
        return {
            "status": "success",
            "message": f"✅ OTP sent successfully to {leader_email}. Check your inbox (including spam folder) for the 6-digit code. OTP expires in 5 minutes.",
            "step": "otp_verification"
        }
    else:
        # Fallback for development
        logger.warning("⚠️ Email sending failed - returning OTP for testing")
        return {
            "status": "warning",
            "message": "⚠️ Email sending failed. Check SMTP settings in .env file.",
            "otp": otp,
            "step": "otp_verification",
            "note": "To fix: Configure SMTP_HOST, SMTP_USER, SMTP_PASS in .env file"
        }


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

async def export_teams(domain: str = None, year: str = None, attendance: str = None, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    """Export teams as CSV. Filters: domain, year, attendance (true/false). Admin-only."""
    from io import StringIO
    import csv

    q = select(Team)
    if domain:
        q = q.where(Team.domain == domain)
    if year:
        q = q.where(Team.year == year)
    if attendance is not None:
        if attendance.lower() in ('true', '1'):
            q = q.where(Team.attendance_status == True)
        elif attendance.lower() in ('false', '0'):
            q = q.where(Team.attendance_status == False)

    res = await db.execute(q)
    rows = res.scalars().all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["team_id","team_name","leader_name","leader_email","leader_phone","college_name","year","domain","team_members","access_key","qr_code_path","id_cards_pdf_path","attendance_status","checkin_time","created_at"])
    for t in rows:
        writer.writerow([
            t.team_id, t.team_name, t.leader_name, t.leader_email, t.leader_phone, t.college_name,
            t.year, t.domain, json.dumps(t.team_members), t.access_key, t.qr_code_path, t.id_cards_pdf_path,
            str(bool(t.attendance_status)), t.checkin_time.isoformat() if t.checkin_time else '', t.created_at.isoformat() if t.created_at else ''
        ])

    from fastapi.responses import StreamingResponse
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type='text/csv', headers={"Content-Disposition": "attachment; filename=teams_export.csv"})


@router.get('/admin/teams')
async def list_teams(page: int = 1, page_size: int = 50, search: str = None, domain: str = None, year: str = None, attendance: str = None, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    q = select(Team)
    if search:
        q = q.where(Team.team_id.ilike(f"%{search}%"))
    if domain:
        q = q.where(Team.domain == domain)
    if year:
        q = q.where(Team.year == year)
    if attendance is not None:
        if attendance.lower() in ('true','1'):
            q = q.where(Team.attendance_status == True)
        elif attendance.lower() in ('false','0'):
            q = q.where(Team.attendance_status == False)

    total_q = await db.execute(select(func.count(Team.id)))
    total = total_q.scalar() or 0
    q = q.offset((page-1)*page_size).limit(page_size)
    res = await db.execute(q)
    rows = res.scalars().all()
    out = []
    for t in rows:
        out.append({
            'team_id': t.team_id,
            'team_name': t.team_name,
            'leader_name': t.leader_name,
            'leader_email': t.leader_email,
            'domain': t.domain,
            'year': t.year,
            'attendance_status': bool(t.attendance_status),
            'checkin_time': t.checkin_time.isoformat() if t.checkin_time else None,
        })
    return { 'total': total, 'page': page, 'page_size': page_size, 'items': out }


@router.get("/stats")
async def stats(db: AsyncSession = Depends(get_db)):
    total_teams_q = await db.execute(select(func.count(Team.id)))
    total_teams = total_teams_q.scalar() or 0
    total_participants_q = await db.execute(select(func.sum(func.json_array_length(Team.team_members))))
    total_participants = total_participants_q.scalar() or 0
    domain_q = await db.execute(select(Team.domain, func.count(Team.id)).group_by(Team.domain))
    domain_dist = {row[0]: row[1] for row in domain_q.all()}
    return {"total_teams": total_teams, "total_participants": total_participants, "domain_distribution": domain_dist}


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
async def checkin(payload: CheckinIn, db: AsyncSession = Depends(get_db)):
    """Check-in team using scanned QR code + typed unique access key."""
    try:
        # Parse QR data (contains team_id and access_key)
        import json
        qr_data = json.loads(payload.qr_data)
        team_id = qr_data.get("team_id")
        qr_access_key = qr_data.get("access_key")
        
        if not team_id or not qr_access_key:
            raise HTTPException(status_code=400, detail="Invalid QR code data")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid QR code format")
    
    # Find team by QR data
    q = await db.execute(select(Team).where(Team.team_id == team_id, Team.access_key == qr_access_key))
    team = q.scalars().first()
    if not team:
        raise HTTPException(status_code=404, detail="❌ Team not found")
    
    # Verify typed access key matches
    if team.access_key != payload.access_key:
        raise HTTPException(status_code=400, detail="❌ Invalid access key")
    
    # Already checked in?
    if team.attendance_status:
        raise HTTPException(status_code=400, detail="⚠️ Team already checked in")
    
    # Mark attendance
    team.checkin_time = datetime.utcnow()
    team.attendance_status = True
    await db.commit()
    
    return {"message": f"✅ {team.team_name} checked in successfully", "team_id": team_id}


@router.post("/attendance/scan")
async def scan_attendance_qr(payload: AttendanceQRIn, db: AsyncSession = Depends(get_db)):
    """
    Scan attendance QR code from ID card to mark participant as present.
    Expects JSON with team_code, participant_id, participant_name, is_team_leader.
    
    Updates team attendance status in database when scanned.
    """
    try:
        import json
        
        qr_data_str = payload.qr_data.strip()
        logger.info(f"🔍 Scanning QR code: {qr_data_str[:50]}...")
        
        # Parse QR code data (JSON format)
        try:
            qr_data = json.loads(qr_data_str)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in QR code: {qr_data_str}")
            raise HTTPException(status_code=400, detail="❌ Invalid QR code format")
        
        team_code = qr_data.get("team_code")
        participant_id = qr_data.get("participant_id")
        participant_name = qr_data.get("participant_name", "Unknown")
        is_team_leader = qr_data.get("is_team_leader", False)
        
        if not team_code or not participant_id:
            raise HTTPException(status_code=400, detail="❌ Invalid QR code: missing team_code or participant_id")
        
        logger.info(f"📱 QR Scanned - Team Code: {team_code}, Participant: {participant_name} ({participant_id})")
        
        # Find team by team_code
        team_q = await db.execute(select(Team).where(Team.team_code == team_code))
        team = team_q.scalars().first()
        
        if not team:
            logger.warning(f"⚠️ Team not found for code: {team_code}")
            raise HTTPException(status_code=404, detail=f"❌ Team code {team_code} not found")
        
        logger.info(f"✅ Found team: {team.team_name} ({team.team_id})")
        
        # Update team attendance status
        team.attendance_status = True
        if not team.checkin_time:
            team.checkin_time = datetime.utcnow()
            logger.info(f"🕐 Set check-in time: {team.checkin_time}")
        
        await db.commit()
        
        role = "Team Lead" if is_team_leader else "Team Member"
        
        logger.info(f"✅ Attendance marked: {participant_name} ({role}) | Team: {team.team_name}")
        
        # Return success response with team details
        return {
            "message": f"✅ Welcome {participant_name}!",
            "status": "success",
            "team_id": team.team_id,
            "team_code": team_code,
            "team_name": team.team_name,
            "leader_name": team.leader_name,
            "domain": team.domain or "Not Specified",
            "year": team.year or "Not Specified",
            "participant_name": participant_name,
            "participant_id": participant_id,
            "role": role,
            "attendance_status": "checked_in",
            "checkin_time": team.checkin_time.isoformat() if team.checkin_time else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error scanning QR code: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"❌ Invalid QR code: {str(e)}")


@router.get("/team/by-code/{team_code}")
async def get_team_by_code(team_code: str, db: AsyncSession = Depends(get_db)):
    """
    Get team information by unique team code.
    Useful for verifying registration and team details.
    """
    try:
        team_q = await db.execute(select(Team).where(Team.team_code == team_code))
        team = team_q.scalars().first()
        
        if not team:
            raise HTTPException(status_code=404, detail=f"❌ Team code {team_code} not found")
        
        logger.info(f"✅ Retrieved team info for code: {team_code}")
        
        return {
            "team_id": team.team_id,
            "team_code": team.team_code,
            "team_name": team.team_name,
            "leader_name": team.leader_name,
            "leader_email": team.leader_email,
            "leader_phone": team.leader_phone,
            "college_name": team.college_name,
            "year": team.year,
            "domain": team.domain,
            "attendance_status": team.attendance_status,
            "checkin_time": team.checkin_time.isoformat() if team.checkin_time else None,
            "created_at": team.created_at.isoformat() if team.created_at else None,
            "team_members_count": len(team.team_members) if isinstance(team.team_members, list) else (len(json.loads(team.team_members) if isinstance(team.team_members, str) else []) if team.team_members else 0)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching team by code: {str(e)}")
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
