#!/usr/bin/env python
"""
Simple startup test to verify all modules load correctly.
"""

import sys
import os

print("Testing imports...")

try:
    from app.config import settings
    print("[OK] app.config")
except Exception as e:
    print(f"[ERROR] app.config: {e}")
    sys.exit(1)

try:
    from app.otp_manager import store_otp, verify_otp
    print("[OK] app.otp_manager")
except Exception as e:
    print(f"[ERROR] app.otp_manager: {e}")
    sys.exit(1)

try:
    from app.tasks import send_otp_email_sync, generate_assets_and_email
    print("[OK] app.tasks")
except Exception as e:
    print(f"[ERROR] app.tasks: {e}")
    sys.exit(1)

try:
    from app.routes import router
    print("[OK] app.routes")
except Exception as e:
    print(f"[ERROR] app.routes: {e}")
    sys.exit(1)

try:
    from app.main import app
    print("[OK] app.main")
except Exception as e:
    print(f"[ERROR] app.main: {e}")
    sys.exit(1)

print("\n[SUCCESS] All imports OK!")
print("You can now run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
