# QR Code Format & Sample Data

## QR Code Data Structure

Each ID card contains a QR code that encodes attendance information. The QR code data is in **JSON format** and contains the following structure:

### QR Code Payload Format

```json
{
  "team_code": "TEAM-K9X2V5",
  "participant_id": "TEAM-K9X2V5-000",
  "participant_name": "John Doe",
  "is_team_leader": true,
  "timestamp": "2026-02-22T10:30:00"
}
```

### Field Descriptions

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| `team_code` | String | `TEAM-K9X2V5` | Unique team identifier for database lookup |
| `participant_id` | String | `TEAM-K9X2V5-000` | Unique participant identifier within team |
| `participant_name` | String | `John Doe` | Name of the participant for display |
| `is_team_leader` | Boolean | `true` | Whether participant is team leader or member |
| `timestamp` | ISO 8601 | `2026-02-22T10:30:00` | Creation timestamp of the QR code |

---

## Sample QR Codes for Testing

### Sample 1: Team Lead
```json
{
  "team_code": "TEAM-K9X2V5",
  "participant_id": "TEAM-K9X2V5-000",
  "participant_name": "John Doe",
  "is_team_leader": true,
  "timestamp": "2026-02-22T10:30:00"
}
```

### Sample 2: Team Member 1
```json
{
  "team_code": "TEAM-K9X2V5",
  "participant_id": "TEAM-K9X2V5-001",
  "participant_name": "Alice Smith",
  "is_team_leader": false,
  "timestamp": "2026-02-22T10:30:00"
}
```

### Sample 3: Team Member 2
```json
{
  "team_code": "TEAM-K9X2V5",
  "participant_id": "TEAM-K9X2V5-002",
  "participant_name": "Bob Johnson",
  "is_team_leader": false,
  "timestamp": "2026-02-22T10:30:00"
}
```

### Sample 4: Team Member 3
```json
{
  "team_code": "TEAM-K9X2V5",
  "participant_id": "TEAM-K9X2V5-003",
  "participant_name": "Carol White",
  "is_team_leader": false,
  "timestamp": "2026-02-22T10:30:00"
}
```

---

## QR Code Generation Process

### Step 1: QR Data Creation
```python
from app.utils import create_attendance_qr_data

qr_data = create_attendance_qr_data(
    team_code="TEAM-K9X2V5",
    participant_id="TEAM-K9X2V5-000",
    participant_name="John Doe",
    is_team_leader=True
)
# Returns: '{"team_code":"TEAM-K9X2V5","participant_id":"TEAM-K9X2V5-000",...}'
```

### Step 2: QR Code Image Generation
```python
import qrcode

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=8,
    border=2,
)
qr.add_data(qr_data)
qr.make(fit=True)

qr_img = qr.make_image(fill_color="black", back_color="transparent")
qr_img.save("id_card_qr.png")
```

### Step 3: QR Code Placement on ID Card
- **Position**: Bottom center of card
- **Size**: 200x200 pixels at 300 DPI
- **Color**: Black on transparent background
- **Below QR**: Participant ID text displayed for manual entry

### Step 4: PDF Generation
The QR code image is embedded in the PDF ID card with:
- Code number displayed below
- Team code at top of card
- Participant information centered
- Professional styling with neon design

---

## QR Code Scanning & Processing

### Scanning Flow

```
┌─────────────────────────────┐
│ Participant Shows ID Card   │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│ Organizer Scans QR Code     │
│ with Mobile Scanner App     │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ QR Data Extracted (JSON):                   │
│ {team_code, participant_id, name, ...}     │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ POST /api/attendance/scan                   │
│ Route: FastAPI Endpoint                     │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Parse & Validate QR Data                    │
│ 1. JSON validation                          │
│ 2. Field extraction                         │
│ 3. Team code lookup                         │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Database Query                              │
│ SELECT * FROM teams                         │
│ WHERE team_code = 'TEAM-K9X2V5'             │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Update Team Record                          │
│ SET attendance_status = true,               │
│     checkin_time = NOW()                    │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Return Success Response                     │
│ {status: "success", checkin_time: ...}      │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Display Confirmation to Organizer           │
│ "Welcome John Doe! Team: Test Team Alpha"   │
└─────────────────────────────────────────────┘
```

---

## ID Card Layout with QR Code

```
┌────────────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │  ← Neon left stripe
│ │                                  │
│ │         LBRCE                    │
│ │ (Header in cyan)                 │
│ │                                  │
│ │  ╔════════════════════════════╗  │
│ │  ║                            ║  │
│ │  ║   [PHOTO]                  ║  │
│ │  ║                            ║  │
│ │  ╚════════════════════════════╝  │  ← Photo with borders
│ │  (Circular with rings)           │
│ │                                  │
│ │        TechXelarate              │  ← Gold text
│ │        2026 HACKATHON            │
│ │                                  │
│ │  Code: TEAM-K9X2V5   ← Team code │
│ │                                  │
│ │    JOHN DOE                      │  ← Participant name
│ │    Team: Test Team Alpha         │
│ │    ┌──────────────────────────┐  │
│ │    │    HACK-001              │  │  ← Team ID
│ │    └──────────────────────────┘  │
│ │                                  │
│ │  Explainable AI | 3rd Year       │
│ │                                  │
│ │  "Innovation is seeing what      │  ← Quote
│ │   others don't see"              │
│ │                                  │
│ │          ┌─────────────────┐    │
│ │          │ ┌─────────────┐ │    │
│ │          │ │             │ │    │
│ │          │ │ [QR CODE]   │ │    │  ← QR Code
│ │          │ │             │ │    │
│ │          │ └─────────────┘ │    │
│ │          └─────────────────┘    │
│ │                                  │
│ │     TEAM-K9X2V5-000       ← ID  │
│ │                                  │
└────────────────────────────────────┘
```

---

## Scanning Examples

### Example 1: Scan at Check-in Point

**Device receives QR scan:**
```
Scan detected! Processing...

QR Code Data received:
{
  "team_code": "TEAM-K9X2V5",
  "participant_id": "TEAM-K9X2V5-000",
  "participant_name": "John Doe",
  "is_team_leader": true,
  "timestamp": "2026-02-22T10:30:00"
}

Sending to server...

Response received:
✅ Welcome John Doe!
Team: Test Team Alpha
Role: Team Lead
Status: Checked In ✓
Time: 10:35 AM
```

### Example 2: Multiple Scans from Same Team

**First scan (Team Lead):**
```
✅ Welcome John Doe!
Team: Test Team Alpha
Role: Team Lead
```

**Second scan (Member 1):**
```
✅ Welcome Alice Smith!
Team: Test Team Alpha
Role: Team Member
```

**Third scan (Member 2):**
```
✅ Welcome Bob Johnson!
Team: Test Team Alpha
Role: Team Member
```

---

## Error Scenarios

### Error 1: Invalid QR Code Format
**Scanned data:** `INVALID_QR_CODE_DATA`

**Server response:**
```json
{
  "detail": "❌ Invalid QR code format"
}
```

### Error 2: Malformed JSON in QR
**Scanned data:** `{invalid json`

**Server response:**
```json
{
  "detail": "❌ Invalid QR code format"
}
```

### Error 3: Team Code Not Found
**Scanned data:** (with team_code: "TEAM-XXXXXX")

**Server response:**
```json
{
  "detail": "❌ Team code TEAM-XXXXXX not found"
}
```

### Error 4: Missing Fields
**Scanned data:** `{"team_code": "TEAM-K9X2V5"}` (missing other fields)

**Server response:**
```json
{
  "detail": "❌ Invalid QR code: missing team_code or participant_id"
}
```

---

## Database Storage

### How QR Data is Used

**On successful scan, database is updated:**

```sql
UPDATE teams 
SET 
  attendance_status = true,
  checkin_time = '2026-02-22T10:35:00'
WHERE 
  team_code = 'TEAM-K9X2V5';
```

**Result in database:**

| team_id | team_code | team_name | attendance_status | checkin_time |
|---------|-----------|-----------|-------------------|--------------|
| HACK-001 | TEAM-K9X2V5 | Test Team Alpha | true | 2026-02-22T10:35:00 |
| HACK-002 | TEAM-L7M4Q8 | Team Beta | false | NULL |
| HACK-003 | TEAM-P2N9R5 | Team Gamma | true | 2026-02-22T10:40:00 |

---

## Live Testing Commands

### Generate a Test QR (Curl)

```bash
# Create JSON payload
QR_JSON='{"team_code":"TEAM-TEST123","participant_id":"TEAM-TEST123-000","participant_name":"Test Person","is_team_leader":true,"timestamp":"2026-02-22T10:30:00"}'

# Send to API
curl -X POST http://localhost:8000/api/attendance/scan \
  -H "Content-Type: application/json" \
  -d "{\"qr_data\": \"$QR_JSON\"}"
```

### Encode QR Code Online

Use an online QR code generator:
1. Go to https://www.qr-code-generator.com/
2. Paste the JSON payload
3. Generate QR code
4. Scan with mobile device
5. Mobile scanner returns the JSON
6. Forward to attendance endpoint

### Python QR Generator

```python
import qrcode
import json

data = {
    "team_code": "TEAM-TEST123",
    "participant_id": "TEAM-TEST123-000",
    "participant_name": "Test Person",
    "is_team_leader": True,
    "timestamp": "2026-02-22T10:30:00"
}

qr = qrcode.QRCode()
qr.add_data(json.dumps(data))
qr.make()

img = qr.make_image()
img.save("qr_code.png")
print("✅ QR code saved as qr_code.png")
```

---

## QR Code Specifications

### Error Correction Level
- **Level**: H (High)
- **Data Recovery**: ~30% of QR code can be damaged
- **Best for**: Printed ID cards that might get folded/wrinkled

### QR Code Version
- **Version**: 1 (automatically adjusted)
- **Data Capacity**: ~173 bytes
- **Our payload size**: ~120 bytes ✓

### Physical Specifications (on ID Card)
- **Size**: 200x200 pixels
- **DPI**: 300 (print quality)
- **Physical size**: ~17mm x 17mm when printed
- **Quiet zone**: 2 modules border

### Colors
- **Foreground**: Black (#000000)
- **Background**: Transparent (overlays on card)

---

## Best Practices

1. **Always validate JSON** before processing
2. **Use error_correction=H** for durability
3. **Include timestamp** for audit trail
4. **Display participant info** even if scan fails
5. **Log all scans** for debugging
6. **Handle duplicate scans** gracefully
7. **Provide clear UI feedback** to organizer
8. **Test offline mode** for unreliable networks

---

## References

- QRCode Python Library: https://github.com/lincolnloop/python-qrcode
- QR Code Specs: https://en.wikipedia.org/wiki/QR_code
- JSON Format: https://www.json.org/
- ISO 8601 Timestamps: https://en.wikipedia.org/wiki/ISO_8601
