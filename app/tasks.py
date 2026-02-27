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
    """Legacy asset generation – now a no-op.

    Photo uploads, ID cards and QR generation have been deprecated and the
    related routes removed.  This helper remains only to avoid import errors
    but it immediately returns an empty response.
    """
    logger.warning("generate_assets_and_email called but asset generation is disabled")
    return {"status": "disabled"}
