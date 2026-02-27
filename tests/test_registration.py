import pytest
from app.schemas import RegisterIn, TeamMemberCreate
from pydantic import ValidationError


def test_registerin_accepts_member_objects():
    # valid payload with leader plus one member
    payload = {
        "team_name": "TeamX",
        "leader_name": "Alice",
        "leader_email": "alice@example.com",
        "leader_phone": "1234567890",
        "college_name": "Example U",
        "year": "II",
        "domain": "AI",
        "team_members": [
            {"name": "Alice", "email": "alice@example.com", "phone": "1234567890", "is_team_leader": True},
            {"name": "Bob", "email": "bob@example.com", "phone": "0987654321", "is_team_leader": False},
        ],
        "terms_accepted": True,
    }
    reg = RegisterIn(**payload)
    assert len(reg.team_members) == 2
    assert any(m.is_team_leader for m in reg.team_members)


def test_registerin_autoflags_first_member_leader():
    payload = {
        "team_name": "TeamY",
        "leader_name": "Alice",
        "leader_email": "alice@example.com",
        "leader_phone": "1234567890",
        "college_name": "Example U",
        "year": "II",
        "domain": "AI",
        "team_members": [
            {"name": "Bob", "email": "bob@example.com", "phone": "0987654321", "is_team_leader": False},
            {"name": "Charlie", "email": "charlie@example.com", "phone": "2222222222", "is_team_leader": False},
        ],
        "terms_accepted": True,
    }
    reg = RegisterIn(**payload)
    assert reg.team_members[0].is_team_leader
    assert reg.team_members[1].is_team_leader is False


def test_registerin_rejects_too_many_members():
    payload = {
        "team_name": "TeamX",
        "leader_name": "Alice",
        "leader_email": "alice@example.com",
        "leader_phone": "1234567890",
        "college_name": "Example U",
        "year": "II",
        "domain": "AI",
        "team_members": [
            {"name": "A", "email": "a@example.com", "phone": "1111111111", "is_team_leader": True},
            {"name": "B", "email": "b@example.com", "phone": "2222222222", "is_team_leader": False},
            {"name": "C", "email": "c@example.com", "phone": "3333333333", "is_team_leader": False},
            {"name": "D", "email": "d@example.com", "phone": "4444444444", "is_team_leader": False},
        ],
        "terms_accepted": True,
    }
    with pytest.raises(ValidationError):
        RegisterIn(**payload)
