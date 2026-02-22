from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .config import settings
from .db import engine, Base
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import logging
from fastapi.staticfiles import StaticFiles
import os
import time

logging.basicConfig(level=logging.INFO)


app = FastAPI(title="Hackathon Registration API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Simple in-memory rate limiting (no Redis needed)
class RateLimitMiddleware(BaseHTTPMiddleware):
    # Store: {ip: (count, expiry_time)}
    rate_limit_store = {}
    
    async def dispatch(self, request: Request, call_next):
        client = request.client.host
        current_time = time.time()
        key = f"rl:{client}"
        
        # Check if IP is rate limited
        if key in self.rate_limit_store:
            count, expiry_time = self.rate_limit_store[key]
            if current_time < expiry_time:
                if count >= 5:
                    return JSONResponse({"detail": "⏱️ Too many requests. Try again in a moment."}, status_code=429)
                # Increment count
                self.rate_limit_store[key] = (count + 1, expiry_time)
            else:
                # Expired, reset
                self.rate_limit_store[key] = (1, current_time + 60)
        else:
            # New IP, set initial count
            self.rate_limit_store[key] = (1, current_time + 60)
        
        return await call_next(request)



app.add_middleware(RateLimitMiddleware)


@app.exception_handler(Exception)
async def all_exceptions_handler(request: Request, exc: Exception):
    return JSONResponse({"detail": str(exc)}, status_code=500)


app.include_router(router)

# Serve generated assets (QR images, PDFs)
assets_dir = os.path.join(os.getcwd(), "assets")
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir, exist_ok=True)
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.on_event("startup")
async def on_startup():
    # create DB tables (skip if DB not available for development)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logging.warning(f"Database not available during startup: {e}")


@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}
