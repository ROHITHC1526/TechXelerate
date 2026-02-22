from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
import re


class RegisterIn(BaseModel):
    """Schema for team registration."""
    team_name: str = Field(..., min_length=3, max_length=100, description="Team name (3-100 chars)")
    leader_name: str = Field(..., min_length=2, max_length=100, description="Leader full name (2-100 chars)")
    leader_email: EmailStr = Field(..., description="Leader email address")
    leader_phone: str = Field(..., min_length=10, max_length=20, description="Leader phone number (10-20 digits)")
    college_name: str = Field(..., min_length=2, max_length=100, description="College/Institution name (2-100 chars)")
    year: str = Field(..., min_length=1, max_length=50, description="Academic year (e.g., 3rd Year)")
    domain: str = Field(..., min_length=1, max_length=50, description="Hackathon domain/track")
    team_members: List[str] = Field(..., min_length=1, max_length=50, description="List of team members (1-50 members)")
    terms_accepted: bool = Field(default=False, description="Terms and conditions acceptance")
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    @field_validator('team_name', 'leader_name', mode='before')
    @classmethod
    def validate_names(cls, v):
        if not isinstance(v, str):
            raise ValueError('Must be a string')
        if not re.match(r'^[a-zA-Z0-9\s\-\.]+$', v):
            raise ValueError('Name contains invalid characters')
        return v.strip()
    
    @field_validator('leader_phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        if not isinstance(v, str):
            raise ValueError('Phone must be a string')
        phone_digits = re.sub(r'\D', '', v)
        if len(phone_digits) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        return v.strip()
    
    @field_validator('terms_accepted')
    @classmethod
    def validate_terms(cls, v):
        if not v:
            raise ValueError('You must accept terms and conditions')
        return v


class OTPIn(BaseModel):
    """Schema for OTP verification."""
    leader_email: EmailStr = Field(..., description="Email address to verify")
    otp: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$', description="6-digit OTP code")
    
    model_config = ConfigDict(str_strip_whitespace=True)


class TeamOut(BaseModel):
    """Schema for team response."""
    id: Optional[str] = None
    team_id: str = Field(..., description="Unique sequential team ID (e.g., TX2025-001)")
    team_code: Optional[str] = Field(None, description="Unique team code for QR (e.g., TEAM-K9X2V5)")
    team_name: Optional[str] = None
    leader_name: Optional[str] = None
    leader_email: Optional[str] = None
    college_name: Optional[str] = None
    year: Optional[str] = None
    domain: Optional[str] = None
    attendance_status: Optional[bool] = None
    checkin_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)



class AdminLogin(BaseModel):
    """Schema for admin login."""
    username: str = Field(..., min_length=3, max_length=50, description="Admin username")
    password: str = Field(..., min_length=6, max_length=100, description="Admin password")
    
    model_config = ConfigDict(str_strip_whitespace=True)


class DownloadIDIn(BaseModel):
    """Schema for ID card download request."""
    team_id: str = Field(..., min_length=5, max_length=50, description="Team ID")
    access_key: str = Field(..., min_length=10, max_length=100, description="Team access key")
    
    model_config = ConfigDict(str_strip_whitespace=True)


class CheckinIn(BaseModel):
    """Schema for QR code check-in at event."""
    qr_data: str = Field(..., description="Scanned QR code data (team_id + access_key)")
    access_key: str = Field(..., description="Typed unique access key from ID card")
    
    model_config = ConfigDict(str_strip_whitespace=True)


class AttendanceQRIn(BaseModel):
    """Schema for scanning attendance QR codes from ID cards."""
    qr_data: str = Field(..., description="Scanned attendance QR code JSON data")
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    @field_validator('qr_data', mode='before')
    @classmethod
    def validate_qr_data(cls, v):
        if not isinstance(v, str):
            raise ValueError('QR data must be a string')
        # Try to parse as JSON to ensure it's valid
        import json
        try:
            json.loads(v)
        except json.JSONDecodeError:
            raise ValueError('QR data must be valid JSON')
        return v


class TestEmailIn(BaseModel):
    """Schema for testing email configuration."""
    email: EmailStr = Field(..., description="Email address to send test email to")
    
    model_config = ConfigDict(str_strip_whitespace=True)
