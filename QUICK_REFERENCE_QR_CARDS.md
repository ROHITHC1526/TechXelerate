# Quick Reference: Attendance QR & Glossy ID Cards

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
| `pdf_generator.py` | Vibrant AI theme, glossy effects, team lead badge, attendance QR |
| `routes.py` | Team leader photo upload, `/api/attendance/scan` endpoint |
| `tasks.py` | Parse "name\|email\|phone\|photo\|ROLE" format |
| `schemas.py` | New `AttendanceQRIn` schema |

### Frontend (`frontend/app/registration/`)

| File | Key Changes |
|------|------------|
| `page.tsx` | Team leader photo upload, member limit (max 3), delete button |

## 🎨 Color Palette (RGB)

```python
# Gradients
gradient_start = (0, 50, 180)        # Electric Blue
gradient_end = (150, 20, 100)        # Deep Magenta

# Accents
cyan_neon = (0, 255, 200)            # Bright Cyan
magenta_neon = (255, 100, 200)       # Pink

# Special
team_lead_badge = (255, 150, 0)      # Gold
text_orange = (255, 180, 0)          # Names
text_cyan = (0, 200, 255)            # Info
```

## 🔐 QR Code Data Format

```json
{
  "team_id": "HACK-2026-001",
  "participant": "John Doe",
  "index": 0,
  "is_team_leader": true,
  "attendance": false,
  "timestamp": "2026-02-21T10:30:00"
}
```

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

### Scan Attendance QR
```bash
POST /api/attendance/scan
Content-Type: application/json

{
  "qr_data": "{\"team_id\": \"HACK-001\", \"participant\": \"John\", ...}"
}

Response:
{
  "message": "✅ Attendance confirmed for John (Team Lead)",
  "team_id": "HACK-001",
  "checkin_time": "2026-02-21T10:30:00"
}
```

## 🗄️ Database Fields

```python
Team.team_members       # JSON: pipe-separated with role
Team.attendance_status  # Boolean: True when QR scanned
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
# Simulate QR scan
import json, requests

qr_data = {
    "team_id": "HACK-001",
    "participant": "John Doe",
    "index": 0,
    "is_team_leader": True,
    "attendance": False,
    "timestamp": "2026-02-21T10:30:00"
}

response = requests.post(
    "http://localhost:8000/api/attendance/scan",
    json={"qr_data": json.dumps(qr_data)}
)
print(response.json())
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Photo not showing | Check 5MB limit, try JPEG format |
| QR code too small on card | It's 70×70px, visible when printed |
| Team member limit error | Remove members until 3 total |
| Attendance not updating | Verify QR JSON format with double quotes |
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
- [ ] Test registration form with team leader photo
- [ ] Verify ID cards generate with glossy design
- [ ] Check QR codes embed attendance data
- [ ] Test `/api/attendance/scan` endpoint
- [ ] Verify pgAdmin shows attendance_status updates
- [ ] Test file upload validation (size, type)
- [ ] Test team member limit enforcement
- [ ] Generate sample PDF and verify colors
- [ ] Email sending configured (SMTP)

---

**Version:** 1.0  
**Date:** Feb 21, 2026  
**Status:** ✅ Production Ready
