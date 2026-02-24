import random
import string
import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pathlib import Path
from .config import settings
import os
import json
from datetime import datetime


def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"


def generate_access_key(n: int = 64) -> str:
    """Generate a secure random access key (default 64 chars)."""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(n))


def generate_team_id(seq: int) -> str:
    """
    Format team id as HACKCSM-XXX where XXX is a zero-padded 3-digit sequence.
    """
    return f"HACKCSM-{seq:03d}"


def generate_checkin_code(n: int = 8) -> str:
    """Generate a unique check-in code for attendance verification."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(n))




async def generate_next_team_id(async_session) -> str:
    """
    Generate the next sequential team id using the teams table count.
    This must be called after OTP verification and before creating the Team record.
    Returns a string like HACKCSM-001
    """
    # Import here to avoid circular imports
    from sqlalchemy import select, func
    from .models import Team

    q = await async_session.execute(select(func.count()).select_from(Team))
    (count,) = q.one()
    next_seq = int(count) + 1
    return generate_team_id(next_seq)


def save_qr(payload: dict, out_dir: str = "assets", filename_prefix: str = None) -> str:
    """Generate a QR containing a JSON payload and save to assets.

    Payload should be a dict with: team_id, member_id, access_key
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    # Use exact values from DB
    data = {
        "team_id": payload.get("team_id"),
        "member_id": payload.get("member_id"),
        "access_key": payload.get("access_key")
    }
    qr_text = json.dumps(data, separators=(',', ':'))
    img = qrcode.make(qr_text)
    
    # Use member_id if provided, otherwise team_id
    safe_name = filename_prefix or payload.get("member_id") or payload.get("team_id", "qr")
    path = os.path.join(out_dir, f"{safe_name}_qr.png")
    img.save(path)
    return path


def create_id_pdf(team: dict, out_dir: str = "assets") -> str:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    path = os.path.join(out_dir, f"{team['team_id']}_id.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(30 * mm, 270 * mm, "CSE (AI & ML) – LBRCE")
    c.setFont("Helvetica", 12)
    c.drawString(30 * mm, 255 * mm, f"Team: {team['team_name']}")
    c.drawString(30 * mm, 245 * mm, f"Team ID: {team['team_id']}")
    c.drawString(30 * mm, 235 * mm, f"Leader: {team['leader_name']} ({team['leader_email']})")
    c.drawString(30 * mm, 225 * mm, f"Domain: {team['domain']}")
    c.drawString(30 * mm, 215 * mm, f"College: {team['college_name']}")
    c.showPage()
    c.save()
    return path
