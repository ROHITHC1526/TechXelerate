# 🚀 QUICK START & DEBUG REFERENCE

This project runs a FastAPI backend for team registration. Photo uploads,
attendance tracking, and check‑in functionality have been **disabled**; the
system now only handles OTP‑based registration and sends a confirmation email
with the submitted team details.

## ⚡ Setup

1. Populate `.env` with SMTP and database settings.
2. Start the server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
3. (Optional) run any existing tests; `pytest` is not installed by default.

---

## 🧪 Quick API Tests

```bash
# STEP 1 – request OTP
curl -X POST http://localhost:8000/api/register \
  -H 'Content-Type: application/json' \
  -d '{
      "team_name": "My Team",
      "leader_name": "Alice",
      "leader_email": "alice@example.com",
      "leader_phone": "1234567890",
      "college_name": "My College",
      "year": "3rd Year",
      "domain": "AI",
      "team_members": [{"name":"Bob","email":"bob@example.com","phone":"0987654321"}]
  }'

# STEP 2 – verify OTP
curl -X POST http://localhost:8000/api/verify-otp \
  -H 'Content-Type: application/json' \
  -d '{"leader_email":"alice@example.com","otp":"000000"}'
```

Replace the OTP value with the one you receive in the email (or returned
in development mode).

---

## 📋 Available Endpoints

| Endpoint                  | Method | Description                          |
|---------------------------|--------|--------------------------------------|
| `/api/register`           | POST   | Submit registration JSON and send OTP |
| `/api/verify-otp`         | POST   | Validate OTP and create team         |
| `/api/admin/teams`        | GET    | List all teams (admin only)          |
| `/api/admin/export`       | GET    | Export teams as CSV (admin only)     |
| `/api/stats`              | GET    | Retrieve basic statistics            |
| `/api/register-multipart`| POST   | **Deprecated** – returns 410 Gone    |

---

## 📝 Notes

* Photo handling and attendance logic have been removed from both the API and
the database schema.  `team_members` table no longer includes
`photo_path`, `attendance_status`, or `checkin_time`.
* Registration is now strictly JSON.  The front‑end should call `/api/register`.

---

## 🧾 Example Responses

**OTP Request Success**
```json
{ "status": "success", "message": "OTP sent", "otp": "123456" }
```

**OTP Verification Success**
```json
{
  "id": "uuid-string",
  "team_id": "HACK-001",
  "team_name": "Example Team",
  "leader_name": "Alice",
  "leader_email": "alice@example.com",
  "college_name": "College",
  "year": "3rd Year",
  "domain": "AI",
  "created_at": "2026-02-25T...Z"
}
```

---

*End of quick reference.*
