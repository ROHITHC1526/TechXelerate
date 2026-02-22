"""
OTP Service Module
Handles OTP generation, storage, verification, and rate limiting.
Implements full life cycle of OTP from generation to verification to cleanup.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from .utils import generate_otp
from .otp_manager import (
    store_otp as store_otp_to_manager,
    verify_otp as verify_otp_from_manager,
    delete_otp as delete_otp_from_manager,
    get_otp as get_otp_from_manager,
)

logger = logging.getLogger(__name__)

# Rate limiting: Track OTP generation attempts
# Format: {email: {"count": int, "reset_time": datetime}}
_otp_generation_attempts: Dict[str, Dict] = {}

# Configuration
OTP_GENERATION_MAX_ATTEMPTS = 3  # Max 3 OTP generations per window
OTP_GENERATION_WINDOW_MINUTES = 1  # Reset window (1 minute)
OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 300  # 5 minutes


class OTPRateLimitError(Exception):
    """Raised when OTP generation rate limit is exceeded."""
    pass


class OTPNotFoundError(Exception):
    """Raised when OTP is not found or expired."""
    pass


class OTPVerificationError(Exception):
    """Raised when OTP verification fails."""
    pass


def _check_otp_generation_rate_limit(email: str) -> bool:
    """
    Check if email has exceeded OTP generation rate limit.
    
    Args:
        email: Email address to check
        
    Returns:
        True if within limit, False if exceeded
        
    Raises:
        OTPRateLimitError: If rate limit exceeded
    """
    now = datetime.utcnow()
    
    if email not in _otp_generation_attempts:
        _otp_generation_attempts[email] = {
            "count": 0,
            "reset_time": now + timedelta(minutes=OTP_GENERATION_WINDOW_MINUTES)
        }
        return True
    
    attempt_data = _otp_generation_attempts[email]
    reset_time = attempt_data.get("reset_time")
    
    # Check if window has expired
    if now >= reset_time:
        # Reset the counter
        _otp_generation_attempts[email] = {
            "count": 0,
            "reset_time": now + timedelta(minutes=OTP_GENERATION_WINDOW_MINUTES)
        }
        return True
    
    # Check if within limit
    if attempt_data["count"] >= OTP_GENERATION_MAX_ATTEMPTS:
        time_remaining = (reset_time - now).total_seconds()
        logger.warning(
            f"⚠️ OTP generation rate limit exceeded for {email}. "
            f"Retry after {int(time_remaining)} seconds."
        )
        raise OTPRateLimitError(
            f"Too many OTP generation attempts. Please try again in {int(time_remaining)} seconds."
        )
    
    return True


def _increment_otp_generation_attempts(email: str) -> None:
    """Increment OTP generation attempt counter for email."""
    if email in _otp_generation_attempts:
        _otp_generation_attempts[email]["count"] += 1
    else:
        _otp_generation_attempts[email] = {
            "count": 1,
            "reset_time": datetime.utcnow() + timedelta(minutes=OTP_GENERATION_WINDOW_MINUTES)
        }


def generate_otp_with_rate_limit(email: str) -> Tuple[str, str]:
    """
    Generate OTP with rate limiting.
    
    Args:
        email: Email address to generate OTP for
        
    Returns:
        Tuple of (otp_code, message)
        
    Raises:
        OTPRateLimitError: If rate limit exceeded
    """
    # Check rate limit
    _check_otp_generation_rate_limit(email)
    
    # Generate OTP
    otp_code = generate_otp()
    
    # Store OTP in manager
    store_otp_to_manager(email, otp_code, expiry_seconds=OTP_EXPIRY_SECONDS)
    
    # Increment attempt counter
    _increment_otp_generation_attempts(email)
    
    logger.info(f"✅ OTP generated and sent to {email}")
    
    message = f"OTP sent to your email ({email}). Valid for 5 minutes."
    return otp_code, message


def verify_otp_with_proper_codes(email: str, otp_code: str) -> Tuple[bool, str]:
    """
    Verify OTP with proper error codes and messages.
    
    Args:
        email: Email address to verify
        otp_code: OTP code to verify
        
    Returns:
        Tuple of (is_valid, message_or_status_code)
        Possible returns:
        - (True, "valid"): OTP is valid
        - (False, "invalid"): OTP code doesn't match
        - (False, "expired"): OTP has expired (410 Gone)
        - (False, "not_found"): OTP was never generated (410 Gone)
    """
    # Check if OTP exists and get it
    stored_otp = get_otp_from_manager(email)
    
    if stored_otp is None:
        logger.warning(f"⚠️ No OTP found for {email} (not generated or already used)")
        return False, "expired"  # Treat as expired for security
    
    # Verify OTP matches
    if not verify_otp_from_manager(email, otp_code):
        logger.warning(f"⚠️ Invalid OTP attempt for {email}")
        return False, "invalid"
    
    # OTP is valid
    logger.info(f"✅ OTP verified successfully for {email}")
    return True, "valid"


def delete_otp(email: str) -> None:
    """
    Delete OTP after successful verification.
    
    Args:
        email: Email address to delete OTP for
    """
    delete_otp_from_manager(email)
    logger.debug(f"🗑️ OTP deleted for {email}")


def cleanup_old_attempt_records(max_age_hours: int = 24) -> int:
    """
    Clean up old OTP attempt records to prevent memory bloat.
    
    Args:
        max_age_hours: Delete records older than this many hours
        
    Returns:
        Number of records deleted
    """
    now = datetime.utcnow()
    deleted_count = 0
    emails_to_delete = []
    
    for email, data in _otp_generation_attempts.items():
        if "created_at" in data:
            created_at = data["created_at"]
            if now - created_at > timedelta(hours=max_age_hours):
                emails_to_delete.append(email)
                deleted_count += 1
    
    for email in emails_to_delete:
        del _otp_generation_attempts[email]
    
    if deleted_count > 0:
        logger.info(f"🧹 Cleaned up {deleted_count} old OTP attempt records")
    
    return deleted_count


def get_otp_stats() -> Dict:
    """
    Get statistics about current OTP attempts (for monitoring/debugging).
    
    Returns:
        Dictionary with stats
    """
    now = datetime.utcnow()
    active_attempts = 0
    
    for email, data in _otp_generation_attempts.items():
        reset_time = data.get("reset_time")
        if reset_time and now < reset_time:
            active_attempts += 1
    
    return {
        "total_emails_with_attempts": len(_otp_generation_attempts),
        "active_attempt_windows": active_attempts,
        "rate_limit_per_window": OTP_GENERATION_MAX_ATTEMPTS,
        "window_duration_minutes": OTP_GENERATION_WINDOW_MINUTES,
        "otp_expiry_seconds": OTP_EXPIRY_SECONDS,
    }


# Error messages for different scenarios
OTP_ERROR_MESSAGES = {
    "expired": {
        "status_code": 410,
        "message": "❌ OTP has expired. Please request a new one.",
        "recovery": "Go back to Step 1 and request a new OTP."
    },
    "invalid": {
        "status_code": 400,
        "message": "❌ Invalid OTP code. Please check and try again.",
        "recovery": "Verify the 6-digit code from your email."
    },
    "not_found": {
        "status_code": 410,
        "message": "❌ OTP not found. Please request a new one.",
        "recovery": "Go back to Step 1 and request a new OTP."
    },
    "rate_limited": {
        "status_code": 429,
        "message": "❌ Too many attempts. Please wait before trying again.",
        "recovery": "Wait a few minutes and try again."
    },
}


def get_error_response(error_key: str) -> Dict:
    """
    Get standardized error response.
    
    Args:
        error_key: Key from OTP_ERROR_MESSAGES
        
    Returns:
        Dictionary with status_code and message
    """
    return OTP_ERROR_MESSAGES.get(error_key, {
        "status_code": 500,
        "message": "❌ An error occurred. Please try again.",
        "recovery": "Refresh the page and try again."
    })
