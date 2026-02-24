import uuid
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .db import Base


class Team(Base):
    """Represents a team in the hackathon."""
    __tablename__ = "teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(String(32), unique=True, index=True, nullable=False)  # HACKCSM-001
    team_name = Column(String(255), nullable=False)
    college_name = Column(String(255), nullable=False)
    domain = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TeamMember(Base):
    """Represents an individual team member with per-member attendance tracking."""
    __tablename__ = "team_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(String(32), index=True, nullable=False)  # Links to Team.team_id
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    photo_path = Column(String(512), nullable=True)
    is_team_leader = Column(Boolean, default=False)
    access_key = Column(String(64), unique=True, nullable=False)  # Unique per member, used in QR
    attendance_status = Column(Boolean, default=False)
    checkin_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
