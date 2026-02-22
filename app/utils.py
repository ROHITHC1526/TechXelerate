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


def generate_access_key(n: int = 10) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(n))


def generate_team_id(seq: int) -> str:
    return f"HACK2026-{seq:03d}"


def generate_checkin_code(n: int = 8) -> str:
    """Generate a unique check-in code for attendance verification."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(n))


def generate_unique_team_code() -> str:
    """
    Generate a unique team code for QR scanning and attendance tracking.
    Format: TEAM-{6 uppercase alphanumeric chars}
    Example: TEAM-K9X2V5
    """
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(6))
    return f"TEAM-{code}"


def generate_participant_id(team_code: str, member_index: int) -> str:
    """
    Generate unique participant ID for each team member.
    Format: TEAM-K9X2V5-000 (team code + member index)
    """
    return f"{team_code}-{member_index:03d}"


def create_attendance_qr_data(team_code: str, participant_id: str, participant_name: str, is_team_leader: bool = False) -> str:
    """
    Create QR code data containing attendance information.
    Format: JSON string with team_code, participant_id, participant_name, is_team_leader, timestamp
    """
    qr_payload = {
        "team_code": team_code,
        "participant_id": participant_id,
        "participant_name": participant_name,
        "is_team_leader": is_team_leader,
        "timestamp": datetime.utcnow().isoformat()
    }
    return json.dumps(qr_payload, separators=(',', ':'))


def save_qr(payload: dict, out_dir: str = "assets") -> str:
    """Generate a QR containing a JSON payload (team_id + access_key) and save to assets.

    Payload should be a dict with at least `team_id` and `access_key`.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    # ensure only relevant keys
    data = {"team_id": payload.get("team_id"), "access_key": payload.get("access_key")}
    import json
    qr_text = json.dumps(data, separators=(',', ':'))
    img = qrcode.make(qr_text)
    safe_name = data.get("team_id", "team")
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
