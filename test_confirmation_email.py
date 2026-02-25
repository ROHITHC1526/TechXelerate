import pytest

from app.email_service import EmailService
from app.config import settings


def test_send_registration_confirmation_formats(monkeypatch):
    """Ensure the confirmation email helper accepts expanded parameters and attempts to send."""
    # configure dummy SMTP settings so _get_smtp_config passes
    settings.SMTP_HOST = "localhost"
    settings.SMTP_USER = "tester@example.com"
    settings.SMTP_PASS = "password"
    settings.SMTP_PORT = "1025"  # arbitrary

    # create a dummy SMTP object to avoid network operations
    class DummySMTP:
        def __init__(self, host, port, timeout=None):
            self.host = host
            self.port = port

        def starttls(self):
            pass

        def login(self, user, pwd):
            assert user == settings.SMTP_USER
            assert pwd == settings.SMTP_PASS

        def send_message(self, msg):
            # basic sanity checks on message contents
            assert settings.SMTP_USER in msg["From"]
            assert "TechXelarate" in msg["Subject"]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr("app.email_service.smtplib.SMTP", DummySMTP)

    result = EmailService.send_registration_confirmation(
        to_email="leader@team.com",
        leader_name="Leader Name",
        team_name="Super Team",
        team_id="TX2025-007",
        college_name="My College",
        domain="AI/ML",
        year="3rd Year",
        team_members=[
            {"name": "Leader Name", "email": "leader@team.com", "phone": "1111111111", "is_team_leader": True},
            {"name": "Member One", "email": "m1@team.com", "phone": "2222222222", "is_team_leader": False},
        ],
    )
    assert result is True
