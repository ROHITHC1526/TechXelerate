# Quick Reference: Manual Team Check‑in & ID Cards

## 🚀 Quick Start

```bash
# 1. Run validation
python validate_attendance_qr.py

# 2. Start backend
cd app && python -m uvicorn main:app --reload

# 3. Start frontend (in new terminal)
cd frontend && npm run dev

# 4. Visit registration page
open http://localhost:3000/registration
```

## 📋 Key Changes Summary

### Backend (`app/`)

| File | Key Changes |
|------|------------|
| `idcard_service.py` | Futuristic gradient design, no QR codes, "Verified Participant" text |
| `routes.py` | Added manual `/api/attendance/checkin` endpoint; cleaned QR logic |
| `tasks.py` | Deprecated QR asset generation, stores only PDF path |
| `schemas.py` | `TeamCheckinIn` schema for check-in input |

### Frontend (`frontend/app/checkin/`)

| File | Key Changes |
|------|------------|
| `page.tsx` | Replaced camera/QR UI with team ID input form |

## 🎨 Color Palette (RGB)

```python
# Gradient background: purple to cyan
gradient_start = (128, 0, 128)       # Purple
gradient_end = (0, 255, 255)          # Cyan

# Accents
neon_green = (0, 255, 136)
neon_cyan = (0, 232, 255)
neon_magenta = (200, 0, 255)
neon_orange = (255, 170, 0)
```

<!-- QR codes are no longer used. Manual check-in only. -->

## 📝 Team Member String Format

**New Format (with role):**
```
name|email|phone|photo_path|ROLE
John Doe|john@email.com|9876543210|uploads/leader.jpg|TEAM_LEAD
Jane Smith|jane@email.com|9876543211|uploads/member.jpg|MEMBER
```

**Backward Compatible:**
```
name|email|phone|photo_path
Bob Wilson|bob@email.com|9876543212|uploads/photo.jpg
```

## 🔗 API Endpoints

### Registration with Photos
```bash
POST /api/register-multipart
Content-Type: multipart/form-data

team_name: "Tech Innovators"
leader_name: "John Doe"
leader_email: "john@example.com"
leader_phone: "9876543210"
college_name: "LBRCE"
year: "III"
domain: "Explainable AI"
team_members_json: "[{...}]"
leader_photo: <File>
photos: [<File>, <File>]
```

### Manual Attendance Check-in
```bash
POST /api/attendance/checkin
Content-Type: application/json

{
  "team_id": "HACKCSM-001"
}

Response (success):
{
  "status": "success",
  "team_id": "HACKCSM-001",
  "attendance": true
}

If already checked in HTTP 400 with detail "Already checked in".

If invalid ID HTTP 404 with detail "Invalid Team ID".
```

## 🗄️ Database Fields

```python
Team.team_members       # JSON: pipe-separated with role
Team.attendance_status  # Boolean: True when team checked in (manual entry)
Team.checkin_time       # DateTime: When attendance marked
```

## 📸 Photo Specifications

| Aspect | Requirement |
|--------|------------|
| Format | JPEG, PNG |
| Size | < 5 MB |
| Dimensions | Any (auto-resized) |
| Location | `/uploads/` directory |
| Usage | Team leader + members |

## ✨ Glossy Design Features

- **Gradient:** 600×380px with vibrant colors
- **Shine:** Top 15% white gradient fade
- **Glow:** Multi-layer borders (magenta → cyan → magenta)
- **Badge:** Team lead indicator (orange, 25px)
- **Accents:** AI circuit patterns, tech elements
- **Typography:** Orange names, cyan info, lime IDs
- **Footer:** Motivational quote + tech branding

## 🎯 Validation Rules

- Team leader: MANDATORY
- Photos: OPTIONAL
- Team members: 2-3 (min 2, max 3 total)
- File size: < 5 MB each
- File type: JPEG/PNG only
- Email: Must be valid format

## 🧪 Testing

```python
# Simulate manual check-in
import requests

response = requests.post(
    "http://localhost:8000/api/attendance/checkin",
    json={"team_id": "HACKCSM-001"}
)
print(response.status_code, response.json())
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Photo not showing | Check 5MB limit, try JPEG format |
| Team member limit error | Remove members until 3 total |
| Attendance not updating | Ensure correct team ID and that it hasn't been used |
| pgAdmin shows old data | Refresh browser, check database commit |

## 📚 Documentation Files

- `ATTENDANCE_QR_AND_GLOSSY_CARDS.md` - Full implementation guide
- `QUICK_START.md` - Getting started
- `PROFESSIONAL_ID_CARDS_COMPLETE.md` - Previous implementation

## 🛠️ Development Utils

```python
# In app/utils.py
def save_upload_file(file, team_id) -> str
    # Returns: uploads/TEAM_ID_filename_timestamp.ext

def generate_otp() -> str
    # Returns: 6-digit OTP

def generate_team_id() -> str
    # Returns: HACK-YYYY-XXXX format
```

## 🔍 Key Classes

```python
# PDF Generation
IDCardGenerator(output_dir)
    .generate_participant_id_cards(team_data, team_members_list, filename)

# Email Service
EmailService.send_otp_email(email, otp)
EmailService.send_id_cards_email(email, team_id, pdf_path, ...)

# File Handling
save_upload_file(file: UploadFile, team_id: str) -> str
```

## 📊 Example Database Entry

```json
{
  "team_id": "HACK-2026-001",
  "team_name": "AI Warriors",
  "leader_name": "John Doe",
  "leader_email": "john@example.com",
  "college_name": "LBRCE",
  "year": "III",
  "domain": "Explainable AI",
  "team_members": [
    "John Doe|john@example.com|9876543210|uploads/leader.jpg|TEAM_LEAD",
    "Jane Smith|jane@example.com|9876543211|uploads/member1.jpg|MEMBER",
    "Bob Wilson|bob@example.com|9876543212||MEMBER"
  ],
  "access_key": "ABC123XYZ789",
  "attendance_status": true,
  "checkin_time": "2026-02-21T10:35:00Z"
}
```

## ✅ Pre-Launch Checklist

- [ ] Run `python validate_attendance_qr.py` (all ✅)
- [ ] Verify basic attendance workflow using team ID input
- [ ] Test registration form with team leader photo
- [ ] Verify ID cards generate with glossy design
- [ ] Ensure manual check-in works: POST `/api/attendance/checkin`
- [ ] Verify pgAdmin shows attendance_status updates
- [ ] Test file upload validation (size, type)
- [ ] Test team member limit enforcement
- [ ] Generate sample PDF and verify colors
- [ ] Email sending configured (SMTP)

---

**Version:** 1.0  
**Date:** Feb 21, 2026  
**Status:** ✅ Production Ready
