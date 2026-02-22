"""
Email sending and asset generation tasks.
No Celery or Redis dependency - all functions are synchronous/direct.
Uses separate email_service module for clean architecture.
"""

from .config import settings
from .utils import save_qr, create_id_pdf
from .pdf_generator import IDCardGenerator
from .email_service import EmailService
from .quotes import get_random_quote
import asyncio
import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)


def send_otp_email_sync(to_email: str, otp: str) -> bool:
    """
    Send OTP verification email synchronously via SMTP.
    Delegates to EmailService.
    
    Args:
        to_email: Recipient email address
        otp: One-time password (6 digits)
        
    Returns:
        True if email sent successfully, False otherwise
    """
    return EmailService.send_otp_email(to_email, otp)


def generate_assets_and_email(team_dict: dict) -> dict:
    """
    Generate QR code, professional ID cards PDF, and send confirmation email with attachment.
    This is a simple function (no Celery/working in main thread).
    
    Args:
        team_dict: Team object converted to dict with all registration details
        
    Returns:
        dict with status, qr path, pdf path, and email result
    """
    try:
        team_id = team_dict.get('team_id')
        logger.info(f"🔧 Generating assets for team {team_id}")
        
        # Generate QR code
        qr_path = save_qr(team_dict)
        logger.info(f"✓ QR code generated: {qr_path}")
        
        # Generate professional ID cards PDF using IDCardGenerator
        try:
            generator = IDCardGenerator(output_dir=settings.ASSETS_DIR)
            
            # Parse team_members from team_dict (stored as List[str] with format:
            # "name|email|phone|photo_path|TEAM_LEAD/MEMBER" or "name|email|phone|photo_path" for backward compatibility)
            team_members_raw = team_dict.get('team_members', [])
            team_members_list = []
            
            if isinstance(team_members_raw, list):
                for member_str in team_members_raw:
                    if isinstance(member_str, str):
                        # Parse pipe-separated format
                        parts = member_str.split('|')
                        if len(parts) >= 3:
                            member = {
                                'name': parts[0].strip(),
                                'email': parts[1].strip(),
                                'phone': parts[2].strip(),
                                'photo_path': None,
                                'is_team_leader': False
                            }
                            
                            # Handle photo_path (part 3, can be empty)
                            if len(parts) > 3 and parts[3].strip():
                                member['photo_path'] = parts[3].strip()
                            
                            # Handle TEAM_LEAD flag (part 4)
                            if len(parts) > 4:
                                role = parts[4].strip().upper()
                                member['is_team_leader'] = (role == 'TEAM_LEAD')
                            
                            team_members_list.append(member)
                    elif isinstance(member_str, dict):
                        # Already in dict format
                        team_members_list.append(member_str)
            
            if not team_members_list:
                logger.warning(f"⚠️ No valid team members found for {team_id}, using fallback")
                team_members_list = [{'name': 'Participant', 'email': '', 'phone': '', 'is_team_leader': False}]
            
            # Add unique participant IDs to each member for attendance check-in
            for idx, member in enumerate(team_members_list):
                if 'participant_id' not in member:
                    # Generate unique participant ID: TECH-{random}-{index}
                    import uuid
                    unique_code = str(uuid.uuid4())[:8].upper()
                    member['participant_id'] = f"TECH-{unique_code}-{idx:03d}"
                
                # Store team name and domain for PDF
                member['team_name'] = team_dict.get('team_name', 'Unknown Team')
                member['domain'] = team_dict.get('domain', 'General')
            
            # Prepare team_data for PDF generator
            team_data = {
                'team_id': team_id,
                'team_code': team_dict.get('team_code', 'UNKNOWN'),  # Add team code for QR data
                'team_name': team_dict.get('team_name', 'Unknown Team'),
                'leader_name': team_dict.get('leader_name', ''),
                'year': team_dict.get('year', ''),
                'domain': team_dict.get('domain', 'General'),
                'access_key': team_dict.get('access_key', '')
            }
            
            # Generate ID cards PDF
            pdf_path = generator.generate_participant_id_cards(
                team_data=team_data,
                team_members_list=team_members_list,
                output_filename=f'{team_id}_id_cards.pdf'
            )
            logger.info(f"✓ Professional ID cards PDF generated: {pdf_path}")
        except Exception as e:
            logger.exception(f"⚠️ ID card generation failed: {e}, using fallback")
            pdf_path = create_id_pdf(team_dict)
        
        # Generate individual QR code PNGs for each participant
        qr_png_paths = {}
        try:
            qr_png_paths = generator.generate_participant_qr_pngs(
                team_data=team_data,
                team_members_list=team_members_list
            )
            logger.info(f"✓ Participant QR codes PNG generated: {len(qr_png_paths)} files")
        except Exception as e:
            logger.warning(f"⚠️ QR PNG generation failed: {e}")
            qr_png_paths = {}
        
        logger.info(f"✓ Assets generated: QR={qr_path}, PDF={pdf_path}")
        
        # Update DB with asset paths
        try:
            async def _update_paths():
                from .db import AsyncSessionLocal
                from sqlalchemy import select
                from .models import Team
                
                async with AsyncSessionLocal() as session:
                    async with session.begin():
                        q = await session.execute(select(Team).where(Team.team_id == team_dict.get("team_id")))
                        obj = q.scalars().first()
                        if obj:
                            obj.qr_code_path = qr_path
                            obj.id_cards_pdf_path = pdf_path
                            await session.commit()
                            logger.info(f"✓ Asset paths saved to DB for team {team_dict.get('team_id')}")
                            return True
                        return False
            
            asyncio.run(_update_paths())
        except Exception as e:
            logger.warning(f"⚠️ Could not update DB with asset paths: {e}")
        
        # Send professional ID cards email
        try:
            email_result = EmailService.send_id_cards_email(
                to_email=team_dict.get("leader_email"),
                team_id=team_id,
                team_name=team_dict.get('team_name', 'Unknown Team'),
                leader_name=team_dict.get('leader_name', 'Participant'),
                id_cards_pdf_path=pdf_path,
                domain=team_dict.get('domain', 'General'),
                team_code=team_dict.get('team_code', None)  # Add team code
            )
            
            if email_result:
                logger.info(f"✓ ID cards email sent successfully to {team_dict.get('leader_email')}")
            else:
                logger.warning(f"⚠️ Failed to send ID cards email to {team_dict.get('leader_email')}")
        
        except Exception as e:
            logger.warning(f"⚠️ Exception while sending ID cards email: {e}")
        
        return {"qr": qr_path, "pdf": pdf_path, "status": "success"}
    
    except Exception as e:
        logger.exception(f"❌ Asset generation failed for team {team_dict.get('team_id')}: {e}")
        return {"status": "failed", "error": str(e)}
