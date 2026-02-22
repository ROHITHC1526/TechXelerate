"""
Simple in-memory OTP storage manager.
No Redis dependency - uses Python dictionary with expiry timestamps.
"""

import time
from typing import Dict, Optional
import json

# In-memory storage: {key: (value, expiry_time)}
_otp_store: Dict[str, tuple] = {}
_registration_store: Dict[str, tuple] = {}


def store_otp(email: str, otp: str, expiry_seconds: int = 300) -> None:
    """Store OTP with expiry time (default 5 minutes)."""
    key = f"otp:{email}"
    expiry_time = time.time() + expiry_seconds
    _otp_store[key] = (otp, expiry_time)


def verify_otp(email: str, otp: str) -> bool:
    """Verify OTP matches and hasn't expired."""
    key = f"otp:{email}"
    if key not in _otp_store:
        return False
    
    stored_otp, expiry_time = _otp_store[key]
    
    # Check if expired
    if time.time() > expiry_time:
        del _otp_store[key]
        return False
    
    # Check if matches
    return stored_otp == otp


def get_otp(email: str) -> Optional[str]:
    """Get stored OTP if valid and not expired."""
    key = f"otp:{email}"
    if key not in _otp_store:
        return None
    
    otp, expiry_time = _otp_store[key]
    
    if time.time() > expiry_time:
        del _otp_store[key]
        return None
    
    return otp


def delete_otp(email: str) -> None:
    """Delete OTP after verification."""
    key = f"otp:{email}"
    _otp_store.pop(key, None)


def store_registration_data(email: str, data: dict, expiry_seconds: int = 300) -> None:
    """Store registration data temporarily while awaiting OTP verification."""
    key = f"reg:{email}"
    expiry_time = time.time() + expiry_seconds
    _registration_store[key] = (data, expiry_time)


def get_registration_data(email: str) -> Optional[dict]:
    """Get stored registration data if not expired."""
    key = f"reg:{email}"
    if key not in _registration_store:
        return None
    
    data, expiry_time = _registration_store[key]
    
    if time.time() > expiry_time:
        del _registration_store[key]
        return None
    
    return data


def delete_registration_data(email: str) -> None:
    """Delete registration data after team is created."""
    key = f"reg:{email}"
    _registration_store.pop(key, None)


def cleanup_expired() -> None:
    """Remove all expired entries (call periodically or on demand)."""
    current_time = time.time()
    
    # Clean OTP store
    expired_keys = [k for k, (_, exp_time) in _otp_store.items() if current_time > exp_time]
    for key in expired_keys:
        del _otp_store[key]
    
    # Clean registration store
    expired_keys = [k for k, (_, exp_time) in _registration_store.items() if current_time > exp_time]
    for key in expired_keys:
        del _registration_store[key]
