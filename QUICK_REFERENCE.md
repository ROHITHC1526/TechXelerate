# 🚀 QUICK START & DEBUG REFERENCE

## ⚡ 30-Second Setup

1. **Add to .env**:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-16-char-app-password
DATABASE_URL=postgresql://user:pass@localhost:5432/hackathon
JWT_SECRET=your-secret-key
```

2. **Get Gmail App Password**:
- Go: https://myaccount.google.com/apppasswords
- Select: Mail + Windows (or your device)
- Copy 16-char password → `SMTP_PASS` in .env

3. **Start Server**:
```bash
python -m uvicorn app.main:app --reload
```

4. **Test Flow**:
```bash
python test_complete_flow.py
```

---

## 🧪 Quick Test Commands

### Test 1: Send OTP Email
```bash
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "team_name": "Test Team",
    "leader_name": "John Doe",
    "leader_email": "your-email@gmail.com",
    "leader_phone": "+919876543210",
    "college_name": "LBRCE",
    "year": "3rd Year",
    "domain": "AI",
    "team_members": [{"name":"Alice","email":"alice@example.com","phone":"+919876543211"}]
  }'
```
**Expected**: `"status": "success", "otp": "123456"`

### Test 2: Verify OTP & Get ID Cards
```bash
curl -X POST "http://localhost:8000/api/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "leader_email": "your-email@gmail.com",
    "otp": "123456"
  }'
```
**Expected**: Team created, PDF generated, email sent

### Test 3: Manual Team Check-In
```bash
curl -X POST "http://localhost:8000/api/attendance/checkin" \
  -H "Content-Type: application/json" \
  -d '{"team_id":"HACKCSM-001"}'
```
**Expected**: JSON with `"status": "success"` and `attendance=true` (or 400/404 on error)

### Test 4: Get Team Info
```bash
curl "http://localhost:8000/api/teams/HACKCSM-001"
```
**Expected**: Team details with `"attendance_status": true`

---

## 🐛 Debugging Checklist

### ❌ Issue: OTP Email Not Received

**Step 1**: Check SMTP Config
```bash
grep SMTP .env
# Should show all 3 fields filled
```

**Step 2**: Test SMTP Connection
```python
import smtplib
from app.config import settings

try:
    with smtplib.SMTP(settings.SMTP_HOST, int(settings.SMTP_PORT), timeout=10) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
    print("✅ SMTP connection successful")
except Exception as e:
    print(f"❌ SMTP error: {e}")
```

**Step 3**: Check Email Spam Folder
- Gmail? Check spam/promotions tabs
- Look for: "TechXelarate" or "OTP"

**Step 4**: Enable Less Secure Apps (if not using app password)
- Gmail: https://myaccount.google.com/security
- Turn ON "Less secure app access"

**Common Errors**:
- `SMTPAuthenticationError`: Wrong credentials
- `SMTPNotSupportedError`: Check SMTP_PORT (should be 587)
- `Timeout error`: Network/firewall issue

---

### ❌ Issue: ID Cards Not Generated

**Check PDF File**:
```bash
ls -lh assets/HACK-*.pdf
# Should see: HACK-001_id_cards.pdf with size > 100KB
```

**Check Logs**:
```bash
# Look for: "✅ ID cards PDF generated successfully"
# If error, find: "❌ Failed to generate ID cards"
```

**Debug PDF Generation**:
```python
from app.pdf_generator import IDCardGenerator
from app.utils import generate_team_id, generate_access_key

team_id = generate_team_id(1)
access_key = generate_access_key(12)
members = [
  {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '+919876543210',
    'photo_path': None,
    'is_team_leader': True,
    'participant_id': f"{team_id}-000"
  }
]

gen = IDCardGenerator()
pdf_path = gen.generate_participant_id_cards(
  team_data={'team_id': team_id, 'team_name': 'Test', 'access_key': access_key},
  team_members_list=members,
  output_filename='test_id_cards.pdf'
)
print(f"Generated: {pdf_path}")
```

---

### ❌ Issue: Attendance Not Updating

**Check Database**:
```bash
# Connect to PostgreSQL
psql $DATABASE_URL

# Check team exists
SELECT team_id, attendance_status, checkin_time FROM teams 
WHERE team_id = 'HACKCSM-001';

# Should show: attendance_status=false initially
```

**Manually trigger check-in**:
```bash
curl -X POST "http://localhost:8000/api/attendance/checkin" \
  -H "Content-Type: application/json" \
  -d '{"team_id":"HACKCSM-001"}'
```

**Check Result**:
```bash
# Should return: "status": "success" and attendance=true
# Database should now show: attendance_status=true, checkin_time=<timestamp>
```

---

## 📋 Key Endpoints

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/register` | POST | Register team (JSON) | ✅ Working |
| `/api/register-multipart` | POST | Register team (with photos) | ✅ Working |
| `/api/verify-otp` | POST | Verify OTP, create team | ✅ Working |
| `/api/attendance/checkin` | POST | Manual team check-in (team_id) | ✅ Working |
| `/api/team/by-code/{code}` | GET | Get team info | ✅ Working |
| `/api/teams` | GET | List all teams | ✅ Available |

---

## 📊 Expected Response Formats

### OTP Registration Success
```json
{
  "status": "success",
  "message": "✅ OTP sent successfully to your email",
  "otp": "123456",
  "note": "OTP expires in 5 minutes"
}
```

### OTP Verification Success
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "team_id": "HACK-001",
  "team_code": "TEAM-K9X2V5",
  "team_name": "Innovators",
  "leader_name": "John Doe",
  "attendance_status": false,
  "checkin_time": null
}
```

### Manual Check-in Success
```json
{
  "status": "success",
  "team_id": "HACKCSM-001",
  "attendance": true
}
```

---

## 🔍 Logging Locations

### Server Logs
```bash
# Watch FastAPI logs
tail -f app.log

# Look for patterns:
# ✅ = Success
# ❌ = Error
# 📧 = Email
# 📱 = PDF
# 👤 = Team member
```

### Email Logs
**File**: `app.log`  
**Search**: `Send OTP` or `send_id_cards`

### Database Logs
**Postgres Logs**: Check your PostgreSQL installation  
**Query**: Enable logging with `psql` command

---

## ⚙️ Environment Variables Needed

```env
# Database (REQUIRED)
DATABASE_URL=postgresql://user:password@localhost:5432/hackathon

# SMTP (REQUIRED for production, optional for dev)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-specific-password

# Security (REQUIRED)
JWT_SECRET=your-super-secret-key-minimum-32-chars

# Admin (REQUIRED)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Server (OPTIONAL)
BASE_URL=http://localhost:8000
APP_HOST=0.0.0.0
APP_PORT=8000
```

---

## 🧪 Files Used for Testing

| File | Purpose | How to Use |
|------|---------|-----------|
| `test_complete_flow.py` | Full workflow test | `python test_complete_flow.py` |
| `test_email_config.py` | Test SMTP config | `python test_email_config.py` |
| `test_pdf_system.py` | Test PDF generation | `python test_pdf_system.py` |
| `debug_otp.py` | Debug OTP flow | `python debug_otp.py` |
| `validate_attendance_qr.py` | Validate manual check-in & card visuals | `python validate_attendance_qr.py` |

---

## 🎯 Success Checklist

After setup, verify:

- [ ] Server running: `http://localhost:8000/docs` loads
- [ ] SMTP config correct: `python test_email_config.py` passes
- [ ] OTP sent: Check email inbox
- [ ] ID cards generated: Check `assets/` folder
- [ ] PDF has all members: Open PDF and count pages
- [ ] Attendance shows true after manual check-in: Run `test_complete_flow.py`
- [ ] Attendance shows true: Query database after scan

---

## 🚨 Emergency Fixes

### Email Not Working
```bash
# Quick SMTP test
python -c "
from app.email_service import EmailService
config_ok = EmailService._get_smtp_config()
print(f'SMTP OK: {config_ok}')
"
```

### Database Connection Lost
```bash
# Check connection
psql \$DATABASE_URL -c 'SELECT 1'
# Should output: 1
```

### PDF Generation Memory Issue
```bash
# Clear temp files
rm -rf assets/*.pdf
rm -rf /tmp/pdf_*.tmp

# Restart server
```

### OTP Stuck/Expired
```python
# Clear OTP storage
from app.otp_manager import clear_all_otps
clear_all_otps()
```

---

## 📞 Quick Support Links

- **Gmail App Password**: https://myaccount.google.com/apppasswords
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **QR Code Format**: See `app/utils.py` for JSON structure

---

## 💡 Pro Tips

1. **Use Bearer Token for APIs**:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/teams
   ```

2. **Setup Multiple Email Aliases**:
   Create separate test email accounts for testing

3. **Monitor All Logs in One Window**:
   ```bash
   docker logs -f app 2>&1 | grep -E "✅|❌|📧"
   ```

4. **Backup Attendance Data**:
   ```bash
   psql $DATABASE_URL -c "COPY teams TO STDOUT CSV" > attendance_backup.csv
   ```


---

**Last Updated**: Feb 22, 2026  
**Version**: 2.0  
**Status**: ✅ Production Ready
