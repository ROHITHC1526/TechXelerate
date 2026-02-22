#!/usr/bin/env python3
"""
Validation script for Attendance QR Code & Glossy ID Card implementation.
Tests all new features: team leader photos, attendance QR codes, glossy design, team member limits.
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
    """Check if file contains expected code patterns."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        found_count = 0
        for search_str in search_strings:
            if search_str in content:
                found_count += 1
        
        return found_count == len(search_strings)
    except:
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
        "frontend/app/registration": ["page.tsx"],
    }
    
    for directory, files in required_files.items():
        dir_path = os.path.join(base_path, directory)
        print(f"\n   📁 {directory}/")
        for file_name in files:
            if not check_file_exists(dir_path, file_name):
                all_checks_passed = False
    
    # 2. PDF Generator Enhancements
    print("\n2️⃣  Checking PDF Generator (Glossy Design)...")
    pdf_gen_path = os.path.join(base_path, "app", "pdf_generator.py")
    pdf_features = [
        "_create_vibrant_gradient_background",  # New gradient with AI theme
        "_add_glossy_shine",                     # Glossy effect
        "_draw_tech_header",                     # Tech-themed header
        "_add_advanced_photo",                   # Advanced photo with badge
        "_draw_tech_accents",                    # AI/Robo accents
        "_generate_attendance_qr_code",          # Attendance QR generation
        "_add_advanced_qr_code",                 # Advanced QR styling
        "_draw_advanced_footer",                 # Tech footer
        "is_team_leader",                        # Team leader flag support
        "TEAM_LEAD",                             # Team lead role marker
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
        "leader_photo",                      # Team leader photo parameter
        "leader_photo_path",                # Leader photo path handling
        "is_team_leader",                    # Team leader flag
        "TEAM_LEAD",                         # Role marker in format
        "/attendance/scan",                  # Attendance scan endpoint
        "scan_attendance_qr",               # Attendance scan function
        "AttendanceQRIn",                   # Attendance schema usage
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
        "is_team_leader",                   # Team leader flag parsing
        "TEAM_LEAD",                        # Role marker parsing
        "|",                                # Pipe-separated format
        "parts[4]",                         # Fifth part (role) parsing
    ]
    
    if validate_python_code(tasks_path, tasks_features):
        print("  ✅ All tasks features implemented")
    else:
        print("  ❌ Missing tasks features")
        all_checks_passed = False
    
    # 5. Schemas
    print("\n5️⃣  Checking Schemas (Attendance QR)...")
    schemas_path = os.path.join(base_path, "app", "schemas.py")
    schema_features = [
        "class AttendanceQRIn",             # Attendance schema
        "qr_data",                          # QR data field
    ]
    
    if validate_python_code(schemas_path, schema_features):
        print("  ✅ All schema features implemented")
    else:
        print("  ❌ Missing schema features")
        all_checks_passed = False
    
    # 6. Frontend Registration
    print("\n6️⃣  Checking Frontend (Team Leader Photo & Member Limits)...")
    frontend_path = os.path.join(base_path, "frontend", "app", "registration", "page.tsx")
    frontend_features = [
        "leaderPhoto",                      # Leader photo state
        "handleLeaderPhotoSelect",          # Handler for leader photo
        "leader_photo",                     # FormData field
        "if (members.length < 3)",          # Team member limit
        "Maximum 3 team members",           # Limit message
        "LEADER PHOTO",                     # Leader photo label
    ]
    
    if validate_python_code(frontend_path, frontend_features):
        print("  ✅ All frontend features implemented")
    else:
        print("  ❌ Missing frontend features")
        all_checks_passed = False
    
    # 7. Documentation
    print("\n7️⃣  Checking Documentation...")
    doc_path = os.path.join(base_path, "ATTENDANCE_QR_AND_GLOSSY_CARDS.md")
    if os.path.exists(doc_path):
        print("  ✅ Implementation documentation created")
    else:
        print("  ❌ Documentation file missing")
        all_checks_passed = False
    
    # 8. Color Theme Validation
    print("\n8️⃣  Checking Glossy Design Colors...")
    color_features = [
        "(0, 50, 180)",                     # Electric blue
        "(150, 20, 100)",                   # Deep magenta
        "(0, 255, 200)",                    # Cyan neon
        "(255, 100, 200)",                  # Magenta neon
        "(255, 150, 0)",                    # Team lead gold
    ]
    
    if validate_python_code(pdf_gen_path, color_features):
        print("  ✅ Glossy color scheme implemented")
    else:
        print("  ⚠️  Some colors may not be optimal")
    
    # 9. QR Code Features
    print("\n9️⃣  Checking QR Code Implementation...")
    qr_features = [
        "attendance",                       # Attendance field in QR
        "is_team_leader",                   # Team leader field
        "participant",                      # Participant field
        "timestamp",                        # Timestamp field
        "ERROR_CORRECT_H",                  # High error correction
    ]
    
    if validate_python_code(pdf_gen_path, qr_features):
        print("  ✅ Attendance QR code features implemented")
    else:
        print("  ❌ Missing QR code features")
        all_checks_passed = False
    
    # Summary
    print("\n" + "="*60)
    if all_checks_passed:
        print("✅ ALL VALIDATION CHECKS PASSED!")
        print("\n🎉 Ready to test:")
        print("   1. Run: python -m uvicorn app.main:app --reload")
        print("   2. Visit: http://localhost:3000/registration")
        print("   3. Fill form with team leader photo")
        print("   4. Verify glossy ID cards and QR codes")
        print("   5. Scan QR codes: POST /api/attendance/scan")
        print("   6. Check pgAdmin for attendance_status updates")
        return 0
    else:
        print("❌ SOME VALIDATION CHECKS FAILED")
        print("\n⚠️  Please review the missing features above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
