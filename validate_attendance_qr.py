#!/usr/bin/env python3
"""
# (obsolete) validation script for attendance features & ID card design.
# Attendance and QR features have been removed from current backend.
Originally built for QR scanning; now validates new manual check‑in endpoint
and ensures team leader photo support and updated card visuals.
"""

import json
import os
import sys
from pathlib import Path

def check_file_exists(path: str, file_name: str) -> bool:
    """Check if file exists and report."""
    full_path = os.path.join(path, file_name)
    if os.path.exists(full_path):
        print(f"  ✅ {file_name}")
        return True
    else:
        print(f"  ❌ {file_name} (MISSING)")
        return False

def validate_python_code(file_path: str, search_strings: list[str]) -> bool:
    """Check if file contains expected code patterns.

    Uses UTF-8 encoding so that files containing emojis or other
    non‑ASCII characters are parsed correctly. On error the exception
    is printed for debugging and the function returns False.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        found_count = 0
        for search_str in search_strings:
            if search_str in content:
                found_count += 1
        
        return found_count == len(search_strings)
    except Exception as exc:
        print(f"  ⚠️  Error reading {file_path}: {exc}")
        return False

def main():
    print("\n" + "="*60)
    print("🧪 ATTENDANCE QR CODE & GLOSSY ID CARD VALIDATION")
    print("="*60)
    
    base_path = Path(__file__).parent
    all_checks_passed = True
    
    # 1. File Structure Check
    print("\n1️⃣  Checking File Structure...")
    required_files = {
        "app": ["pdf_generator.py", "routes.py", "tasks.py", "schemas.py"],
        "frontend/app/checkin": ["page.tsx"],
    }
    
    for directory, files in required_files.items():
        dir_path = os.path.join(base_path, directory)
        print(f"\n   📁 {directory}/")
        for file_name in files:
            if not check_file_exists(dir_path, file_name):
                all_checks_passed = False
    
    # 2. PDF Generator Enhancements
    print("\n2️⃣  Checking PDF Generator (Updated ID card design)...")
    pdf_gen_path = os.path.join(base_path, "app", "pdf_generator.py")
    # we expect the new gradient + status section and a visible
    # "Verified Participant" string; QR helper functions should
    # have been removed from this file entirely.
    pdf_features = [
        "_create_gradient_background",
        "_add_status_section",
        "Verified Participant",
    ]

    if validate_python_code(pdf_gen_path, pdf_features):
        print("  ✅ All PDF generator features implemented")
    else:
        print("  ❌ Missing PDF generator features")
        all_checks_passed = False
    
    # 3. Routes Enhancements  
    print("\n3️⃣  Checking Routes (Team Leader & Attendance)...")
    routes_path = os.path.join(base_path, "app", "routes.py")
    routes_features = [
        "/attendance/checkin",              # manual attendance endpoint
        "TeamCheckinIn",
    ]
    
    if validate_python_code(routes_path, routes_features):
        print("  ✅ All routes features implemented")
    else:
        print("  ❌ Missing routes features")
        all_checks_passed = False
    
    # 4. Tasks Enhancements
    print("\n4️⃣  Checking Tasks (Team Member Format Parsing)...")
    tasks_path = os.path.join(base_path, "app", "tasks.py")
    tasks_features = [
        "participant_id",                   # Unique ID generation
        "TEAM_LEAD",                        # Role marker parsing
    ]
    
    if validate_python_code(tasks_path, tasks_features):
        print("  ✅ All tasks features implemented")
    else:
        print("  ❌ Missing tasks features")
        all_checks_passed = False
    
    # 5. Schemas
    print("\n5️⃣  Checking Schemas (Manual Attendance)...")
    schemas_path = os.path.join(base_path, "app", "schemas.py")
    schema_features = [
        "class TeamCheckinIn",
        "team_id",
    ]
    
    if validate_python_code(schemas_path, schema_features):
        print("  ✅ All schema features implemented")
    else:
        print("  ❌ Missing schema features")
        all_checks_passed = False
    
    # 6. Frontend Check-in
    print("\n6️⃣  Checking Frontend (Manual Check-in UI)...")
    frontend_path = os.path.join(base_path, "frontend", "app", "checkin", "page.tsx")
    frontend_features = [
        "Team ID",                          # input label
        "/api/attendance/checkin",         # fetch endpoint URL
    ]
    
    if validate_python_code(frontend_path, frontend_features):
        print("  ✅ All frontend features implemented")
    else:
        print("  ❌ Missing frontend features")
        all_checks_passed = False
    
    # 7. Documentation
    print("\n7️⃣  Checking Documentation...")
    # the original validation expected a single file by name, but during
    # the refactor we updated a pair of quick-reference guides instead.
    possible_docs = [
        "QUICK_REFERENCE.md",
        "QUICK_REFERENCE_QR_CARDS.md",
        "ATTENDANCE_QR_AND_GLOSSY_CARDS.md",
    ]
    found_doc = False
    for fname in possible_docs:
        if os.path.exists(os.path.join(base_path, fname)):
            print(f"  ✅ Documentation file present: {fname}")
            found_doc = True
            break
    if not found_doc:
        print("  ❌ Documentation file missing (one of the quick reference guides)")
        all_checks_passed = False
    
    # 8. Color Theme Validation
    print("\n8️⃣  Checking Glossy Design Colors...")
    color_features = [
        "gradient_start",                   # gradient definitions
        "neon_green",
        "neon_cyan",
        "neon_magenta",
        "neon_orange",
    ]
    
    if validate_python_code(pdf_gen_path, color_features):
        print("  ✅ Glossy color scheme implemented")
    else:
        print("  ⚠️  Some colors may not be optimal")
    
    # 9️⃣  QR Code Features
    print("\n9️⃣  QR Code Features (should be deprecated and absent)...")
    qr_features = [
        "import qrcode",                  # should not be present
    ]
    
    if validate_python_code(pdf_gen_path, qr_features):
        print("  ❌ QR-related code still present")
        all_checks_passed = False
    else:
        print("  ✅ No QR code remnants found")
    
    # Summary
    print("\n" + "="*60)
    if all_checks_passed:
        print("✅ ALL VALIDATION CHECKS PASSED!")
        print("\n🎉 Ready to test:")
        print("   1. Run: python -m uvicorn app.main:app --reload")
        print("   2. Visit: http://localhost:3000/registration")
        print("   3. Fill form with team leader photo")
        print("   4. Verify glossy ID cards are generated (no QR codes)")
        print("   5. Use manual check-in: POST /api/attendance/checkin")
        print("   6. Verify team attendance_status updates in database")
        return 0
    else:
        print("❌ SOME VALIDATION CHECKS FAILED")
        print("\n⚠️  Please review the missing features above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
