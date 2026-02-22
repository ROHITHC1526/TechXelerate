import uuid
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .db import Base


class Team(Base):
    __tablename__ = "teams"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(String(32), unique=True, index=True, nullable=False)
    team_code = Column(String(32), unique=True, index=True, nullable=False)  # Unique team code for QR scanning
    team_name = Column(String(255), nullable=False)
    leader_name = Column(String(255), nullable=False)
    leader_email = Column(String(255), unique=True, nullable=False)
    leader_phone = Column(String(50), nullable=False)
    college_name = Column(String(255), nullable=False)
    year = Column(String(10), nullable=False)
    domain = Column(String(100), nullable=False)
    team_members = Column(JSON, nullable=False)  # Stores: [{name, email, phone, photo_path, participant_id}, ...]
    access_key = Column(String(32), unique=True, nullable=False)
    qr_code_path = Column(String(512), nullable=True)
    id_cards_pdf_path = Column(String(512), nullable=True)
    checkin_time = Column(DateTime(timezone=True), nullable=True)
    checkout_time = Column(DateTime(timezone=True), nullable=True)
    attendance_status = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
