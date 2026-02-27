from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
import re


# ===== NEW TEAM MEMBER SCHEMAS =====

class TeamMemberCreate(BaseModel):
    """Schema for creating a team member."""
    name: str = Field(..., min_length=2, max_length=100, description="Member name")
    email: EmailStr = Field(..., description="Member email")
    phone: str = Field(..., min_length=10, max_length=20, description="Member phone (10-20 digits)")
    is_team_leader: bool = Field(default=False, description="Is this member a team leader")
    
    model_config = ConfigDict(str_strip_whitespace=True)


class TeamMemberOut(BaseModel):
    """Schema for team member response."""
    member_id: str = Field(..., description="Member UUID")
    name: str
    email: str
    phone: str
    is_team_leader: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RegisterIn(BaseModel):
    """Schema for team registration."""
    team_name: str = Field(..., min_length=3, max_length=100, description="Team name (3-100 chars)")
    leader_name: str = Field(..., min_length=2, max_length=100, description="Leader full name (2-100 chars)")
    leader_email: EmailStr = Field(..., description="Leader email address")
    leader_phone: str = Field(..., min_length=10, max_length=20, description="Leader phone number (10-20 digits)")
    college_name: str = Field(..., min_length=2, max_length=100, description="College/Institution name (2-100 chars)")
    year: str = Field(..., min_length=1, max_length=50, description="Academic year (e.g., 3rd Year)")
    domain: str = Field(..., min_length=1, max_length=50, description="Hackathon domain/track")
    team_members: List[TeamMemberCreate] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="List of team members (up to 3 including leader)"
    )
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

    @field_validator('team_members')
    @classmethod
    def validate_members(cls, v):
        # ensure one and only one leader flag or infer from first member
        if not any(member.is_team_leader for member in v):
            # automatically mark first member as leader if none provided
            v[0].is_team_leader = True
        # enforce max 3 already by Field but double-check
        if len(v) > 3:
            raise ValueError('Maximum 3 team members allowed (including leader)')
        return v


class OTPIn(BaseModel):
    """Schema for OTP verification."""
    leader_email: EmailStr = Field(..., description="Email address to verify")
    otp: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$', description="6-digit OTP code")
    
    model_config = ConfigDict(str_strip_whitespace=True)


class TeamOut(BaseModel):
    """Schema for team response."""
    id: Optional[str] = None
    team_id: str = Field(..., description="Unique sequential team ID (e.g., HACKCSM-001)")
    team_name: Optional[str] = None
    leader_name: Optional[str] = None
    leader_email: Optional[str] = None
    college_name: Optional[str] = None
    year: Optional[str] = None
    domain: Optional[str] = None
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


# deprecated: QR based checkin removed



# manual attendance check-in schema removed (feature disabled)


class TestEmailIn(BaseModel):
    """Schema for testing email configuration."""
    email: EmailStr = Field(..., description="Email address to send test email to")
    
    model_config = ConfigDict(str_strip_whitespace=True)

# ===== NEW TEAM MEMBER SCHEMAS =====

class TeamMemberCreate(BaseModel):
    """Schema for creating a team member."""
    name: str = Field(..., min_length=2, max_length=100, description="Member name")
    email: EmailStr = Field(..., description="Member email")
    phone: str = Field(..., min_length=10, max_length=20, description="Member phone (10-20 digits)")
    is_team_leader: bool = Field(default=False, description="Is this member a team leader")
    
    model_config = ConfigDict(str_strip_whitespace=True)


class TeamMemberOut(BaseModel):
    """Schema for team member response."""
    member_id: str = Field(..., description="Member UUID")
    name: str
    email: str
    phone: str
    is_team_leader: bool
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TeamWithMembersOut(BaseModel):
    """Schema for team with all members."""
    team_id: str
    team_name: str
    college_name: str
    domain: str
    total_members: int
    members: List[TeamMemberOut]
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Attendance-related responses removed (feature disabled)
