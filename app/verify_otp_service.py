"""
Enhanced OTP Verification and Team Creation API Endpoint.
Implements complete error handling, rate limiting, and security best practices.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import logging
import json
import asyncio
from typing import Optional, Dict

from app.schemas import OTPIn, TeamOut
from app.db import get_db
from app.models import Team
from app.config import settings
from app.utils import (
    generate_unique_team_code,
    generate_participant_id,
    generate_access_key,
    generate_otp
)
from app.otp_manager import (
    verify_otp as verify_otp_from_manager,
    delete_otp,
    get_otp,
    get_registration_data,
    delete_registration_data,
    store_otp
)
from app.email_service import EmailService
from app.idcard_service import IDCardService

logger = logging.getLogger(__name__)

# Rate limiting: store attempt counts
_otp_attempts: Dict[str, tuple] = {}  # {email: (attempts, reset_time)}
MAX_OTP_ATTEMPTS = 3
OTP_ATTEMPT_WINDOW_MINUTES = 15


def check_otp_rate_limit(email: str) -> bool:
    """
    Check if email has exceeded OTP verification attempts.
    
    Args:
        email: Email address to check
        
    Returns:
        True if can attempt, False if rate limited
    """
    current_time = datetime.utcnow()
    
    if email not in _otp_attempts:
        _otp_attempts[email] = (0, current_time)
        return True
    
    attempts, reset_time = _otp_attempts[email]
    
    # Check if attempt window has passed
    if current_time > reset_time:
        _otp_attempts[email] = (0, current_time)
        return True
    
    # Check if exceeded max attempts
    if attempts >= MAX_OTP_ATTEMPTS:
        remaining_time = (reset_time - current_time).total_seconds()
        logger.warning(
            f"⚠️  Rate limit exceeded for {email}. "
            f"Attempts: {attempts}, Reset in: {remaining_time:.0f}s"
        )
        return False
    
    return True


def increment_otp_attempts(email: str):
    """Increment OTP attempt counter."""
    current_time = datetime.utcnow()
    reset_time = current_time + timedelta(minutes=OTP_ATTEMPT_WINDOW_MINUTES)
    
    if email in _otp_attempts:
        attempts, _ = _otp_attempts[email]
        _otp_attempts[email] = (attempts + 1, reset_time)
    else:
        _otp_attempts[email] = (1, reset_time)


async def generate_id_cards_async(
    team_id: str,
    team_code: str,
    team_members_list: list,
    team_data: dict
) -> Optional[str]:
    """
    Asynchronously generate ID cards PDF.
    
    Args:
        team_id: Team ID
        team_code: Team code
        team_members_list: List of team members
        team_data: Team information
        
    Returns:
        Path to generated PDF or None on error
    """
    try:
        logger.info(f"📱 Starting async ID card generation for team {team_id}")
        
        service = IDCardService(output_dir=settings.ASSETS_DIR)
        pdf_path = service.generate_pdf(
            team_data=team_data,
            team_members=team_members_list,
            output_filename=f"{team_id}_id_cards.pdf"
        )
        
        logger.info(f"✅ ID cards PDF generated: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"❌ Failed to generate ID cards: {e}")
        return None


async def send_email_async(
    to_email: str,
    team_id: str,
    team_name: str,
    leader_name: str,
    pdf_path: str,
    domain: str,
    team_code: str
) -> bool:
    """
    Asynchronously send ID cards email.
    
    Args:
        to_email: Recipient email
        team_id: Team ID
        team_name: Team name
        leader_name: Leader name
        pdf_path: Path to PDF
        domain: Domain/track
        team_code: Team code
        
    Returns:
        True if sent successfully
    """
    try:
        logger.info(f"📧 Sending ID cards email to {to_email}")
        
        email_sent = EmailService.send_id_cards_email(
            to_email=to_email,
            team_id=team_id,
            team_name=team_name,
            leader_name=leader_name,
            id_cards_pdf_path=pdf_path,
            domain=domain,
            team_code=team_code
        )
        
        if email_sent:
            logger.info(f"✅ Email sent successfully to {to_email}")
        else:
            logger.error(f"❌ Email sending returned False for {to_email}")
        
        return email_sent
        
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        return False


def generate_team_id_sequential(seq: int) -> str:
    """Generate sequential Team ID: TX2025-001, TX2025-002, etc."""
    return f"TX2025-{seq:03d}"


async def verify_otp_endpoint(
    payload: OTPIn,
    db: AsyncSession = Depends(get_db)
) -> TeamOut:
    """
    Verify OTP and create team record with complete error handling.
    
    STEP 2: After user receives OTP email, they verify OTP code here.
    
    On success:
    1. Validates OTP (must match, must not be expired)
    2. Prevents duplicate verification attempts
    3. Creates Team record with unique team_code
    4. Generates professional ID cards PDF
    5. Sends email with PDF attachment
    6. Clears temporary data
    
    Args:
        payload: Contains leader_email and otp
        db: AsyncSession
        
    Returns:
        TeamOut: Created team information
        
    Raises:
        HTTPException 400: Invalid/expired OTP
        HTTPException 410: OTP expired
        HTTPException 429: Too many attempts (rate limited)
        HTTPException 409: Email already verified
        HTTPException 500: Server error (ID card generation, email sending)
    """
    
    logger.info(f"🔐 OTP verification attempt for: {payload.leader_email}")
    
    try:
        # ============================================================
        # STEP 1: Rate Limiting Check
        # ============================================================
        if not check_otp_rate_limit(payload.leader_email):
            remaining_window = OTP_ATTEMPT_WINDOW_MINUTES
            logger.warning(f"⚠️  Rate limit exceeded for {payload.leader_email}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed OTP attempts. Try again in {remaining_window} minutes.",
                headers={"Retry-After": str(remaining_window * 60)}
            )
        
        # ============================================================
        # STEP 2: Validate OTP Exists and Not Expired
        # ============================================================
        otp_record = get_otp(payload.leader_email)
        if not otp_record:
            increment_otp_attempts(payload.leader_email)
            logger.warning(f"❌ OTP not found or expired for {payload.leader_email}")
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="OTP has expired. Please request a new OTP."
            )
        
        # ============================================================
        # STEP 3: Verify OTP Code Matches
        # ============================================================
        if not verify_otp_from_manager(payload.leader_email, payload.otp):
            increment_otp_attempts(payload.leader_email)
            attempts_left = MAX_OTP_ATTEMPTS - _otp_attempts[payload.leader_email][0]
            logger.warning(f"❌ Invalid OTP for {payload.leader_email} (attempts left: {attempts_left})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid OTP. {attempts_left} attempts remaining."
            )
        
        # ============================================================
        # STEP 4: Check Email Not Already Registered
        # ============================================================
        existing_team = await db.execute(
            select(Team).where(Team.leader_email == payload.leader_email)
        )
        if existing_team.scalars().first():
            logger.warning(f"❌ Email {payload.leader_email} already registered")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email is already registered with a team. "
                       "Use a different email to register a new team."
            )
        
        # ============================================================
        # STEP 5: Get Registration Data
        # ============================================================
        reg_data = get_registration_data(payload.leader_email)
        if not reg_data:
            logger.warning(f"❌ Registration data expired for {payload.leader_email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration data has expired. "
                       "Please submit the registration form again and request a new OTP."
            )
        
        # ============================================================
        # STEP 6: Generate Team IDs and Codes
        # ============================================================
        count_result = await db.execute(select(func.count(Team.id)))
        seq = (count_result.scalar() or 0) + 1
        team_id = generate_team_id_sequential(seq)
        team_code = generate_unique_team_code()
        access_key = generate_access_key(32)
        
        logger.info(f"Generated IDs - Team ID: {team_id}, Team Code: {team_code}")
        
        # ============================================================
        # STEP 7: Parse Team Members
        # ============================================================
        team_members_raw = reg_data.get("team_members", [])
        team_members_list = []
        
        if isinstance(team_members_raw, list):
            for idx, member_data in enumerate(team_members_raw):
                try:
                    if isinstance(member_data, dict):
                        # Already parsed as dict
                        member = member_data.copy()
                    elif isinstance(member_data, str):
                        # Parse pipe-separated format
                        parts = member_data.split('|')
                        if len(parts) < 3:
                            logger.warning(f"Skipping invalid member format: {member_data}")
                            continue
                        
                        member = {
                            'name': parts[0].strip(),
                            'email': parts[1].strip(),
                            'phone': parts[2].strip(),
                            'photo_path': None,
                            'is_team_leader': idx == 0
                        }
                        
                        if len(parts) > 3 and parts[3].strip():
                            member['photo_path'] = parts[3].strip()
                        
                        if len(parts) > 4:
                            role = parts[4].strip().upper()
                            member['is_team_leader'] = (role == 'TEAM_LEAD')
                    else:
                        logger.warning(f"Skipping unknown member format: {type(member_data)}")
                        continue
                    
                    # Generate participant ID
                    participant_id = generate_participant_id(team_code, idx)
                    member['participant_id'] = participant_id
                    
                    team_members_list.append(member)
                    logger.debug(f"✓ Parsed member {idx}: {member.get('name')} ({participant_id})")
                    
                except Exception as e:
                    logger.error(f"❌ Error parsing member {idx}: {e}")
                    continue
        
        if not team_members_list:
            logger.error(f"❌ No valid team members found")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid team members found. Please submit the form again."
            )
        
        logger.info(f"✓ Parsed {len(team_members_list)} team members")
        
        # ============================================================
        # STEP 8: Create Team Record
        # ============================================================
        team = Team(
            team_id=team_id,
            team_code=team_code,
            team_name=reg_data.get("team_name"),
            leader_name=reg_data.get("leader_name"),
            leader_email=reg_data.get("leader_email"),
            leader_phone=reg_data.get("leader_phone"),
            college_name=reg_data.get("college_name"),
            year=reg_data.get("year"),
            domain=reg_data.get("domain"),
            team_members=team_members_list,
            access_key=access_key,
        )
        
        try:
            db.add(team)
            await db.commit()
            await db.refresh(team)
            logger.info(f"✅ Team record created: {team_id}")
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"❌ Database integrity error: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Team creation failed due to duplicate data. Please try again."
            )
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Database error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create team record. Please try again."
            )
        
        # ============================================================
        # STEP 9: Generate ID Cards (with error handling)
        # ============================================================
        team_data = {
            'team_id': team_id,
            'team_code': team_code,
            'team_name': reg_data.get("team_name"),
            'leader_name': reg_data.get("leader_name"),
            'leader_email': reg_data.get("leader_email"),
            'college_name': reg_data.get("college_name"),
            'year': reg_data.get("year"),
            'domain': reg_data.get("domain"),
        }
        
        pdf_path = await generate_id_cards_async(
            team_id=team_id,
            team_code=team_code,
            team_members_list=team_members_list,
            team_data=team_data
        )
        
        if not pdf_path:
            logger.error(f"❌ ID card generation failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate ID cards. Please contact support."
            )
        
        # ============================================================
        # STEP 10: Send Email with PDF Attachment
        # ============================================================
        email_sent = await send_email_async(
            to_email=reg_data.get("leader_email"),
            team_id=team_id,
            team_name=reg_data.get("team_name"),
            leader_name=reg_data.get("leader_name"),
            pdf_path=pdf_path,
            domain=reg_data.get("domain", "General"),
            team_code=team_code
        )
        
        if not email_sent:
            logger.error(f"❌ Email sending failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ID cards generated but email delivery failed. Please check SMTP settings."
            )
        
        # ============================================================
        # STEP 11: Clean Up Temporary Data
        # ============================================================
        delete_otp(payload.leader_email)
        delete_registration_data(payload.leader_email)
        if payload.leader_email in _otp_attempts:
            del _otp_attempts[payload.leader_email]
        
        logger.info(f"✅ OTP verification complete for {payload.leader_email}")
        logger.info(f"✅ Team {team_id} successfully created and registered")
        
        # ============================================================
        # STEP 12: Return Success Response
        # ============================================================
        return TeamOut(
            id=str(team.id),
            team_id=team.team_id,
            team_code=team.team_code,
            team_name=team.team_name,
            leader_name=team.leader_name,
            leader_email=team.leader_email,
            college_name=team.college_name,
            year=team.year,
            domain=team.domain,
            attendance_status=team.attendance_status,
            checkin_time=team.checkin_time,
            created_at=team.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Unexpected error in OTP verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again or contact support."
        )
