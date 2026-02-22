Production deployment

Requirements:
- Docker & Docker Compose

1) Copy `.env.example` to `.env` and set values (DATABASE_URL, REDIS_URL, SMTP creds, JWT secret, BASE_URL)

2) Build and run:

```bash
docker-compose up --build -d
```

3) Verify services:

- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000

Notes:
- Celery worker is started as `worker` service.
- Generated assets (QR/png, PDF) are available under `/assets` route from backend.
- Admin export endpoint is at `/api/admin/export` and requires admin JWT from `/api/admin/login`.
