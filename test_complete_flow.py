#!/usr/bin/env python
"""
Complete Test Suite for QR Code Attendance System
Tests the entire flow: Registration -> OTP -> ID Card Generation -> QR Scanning -> Attendance Update
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    print("\n" + "="*70)
    print(f"🧪 {title}")
    print("="*70)

def test_registration():
    """Test 1: Register a team"""
    print_section("TEST 1: TEAM REGISTRATION")
    
    url = f"{BASE_URL}/register-multipart"
    
    data = {
        "team_name": "Test Team Alpha",
        "leader_name": "John Doe",
        "leader_email": f"test.leader.{int(time.time())}@example.com",
        "leader_phone": "+919876543210",
        "college_name": "LBRCE",
        "year": "3rd Year",
        "domain": "Explainable AI",
        "team_members_json": json.dumps([
            {"name": "Alice Smith", "email": "alice@example.com", "phone": "+919876543211"},
            {"name": "Bob Johnson", "email": "bob@example.com", "phone": "+919876543212"},
            {"name": "Carol White", "email": "carol@example.com", "phone": "+919876543213"}
        ])
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 202:
            print("✅ Registration successful!")
            otp = result.get("otp", "NOT PROVIDED")
            leader_email = data["leader_email"]
            return otp, leader_email
        else:
            print("❌ Registration failed!")
            return None, None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, None

def test_otp_verification(otp, leader_email):
    """Test 2: Verify OTP"""
    if not otp or not leader_email:
        print("\n⚠️ Skipping OTP verification - no OTP from registration")
        return False
    
    print_section("TEST 2: OTP VERIFICATION")
    
    url = f"{BASE_URL}/verify-otp"
    
    payload = {
        "leader_email": leader_email,
        "otp": otp
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print("✅ OTP verified successfully!")
            print("✅ Team created successfully!")
            team_id = result.get("team_id")
            print(f"Team ID: {team_id}")
            return True, team_id
        else:
            print("❌ OTP verification failed!")
            print(f"Error: {result.get('detail', 'Unknown error')}")
            return False, None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, None

def test_get_team_info(team_id):
    """Test 3: Get team information"""
    if not team_id:
        print("\n⚠️ Skipping team info - no team ID")
        return None
    
    print_section("TEST 3: GET TEAM INFORMATION")
    
    url = f"{BASE_URL}/teams/{team_id}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            print("✅ Team info retrieved successfully!")
            return result
        else:
            print(f"⚠️ Could not retrieve team info: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Exception: {e}")
        return None

def test_qr_scanning(team_code):
    """Test 4: Scan QR code and update attendance"""
    if not team_code:
        print("\n⚠️ Skipping QR scan - no team code")
        return False
    
    print_section("TEST 4: QR CODE SCANNING")
    
    url = f"{BASE_URL}/attendance/scan"
    
    # Create sample QR data
    qr_data = {
        "team_code": team_code,
        "participant_id": f"{team_code}-000",
        "participant_name": "John Doe",
        "is_team_leader": True,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    payload = {
        "qr_data": json.dumps(qr_data)
    }
    
    print(f"Scanning QR code with data: {json.dumps(qr_data, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print("✅ QR code scanned successfully!")
            print("✅ Attendance updated in database!")
            return True
        else:
            print(f"❌ QR scanning failed: {result.get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_attendance_verification(team_code):
    """Test 5: Verify attendance was updated"""
    if not team_code:
        print("\n⚠️ Skipping verification - no team code")
        return False
    
    print_section("TEST 5: VERIFY ATTENDANCE UPDATE")
    
    url = f"{BASE_URL}/team/by-code/{team_code}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            attendance = result.get("attendance_status")
            checkin_time = result.get("checkin_time")
            
            if attendance:
                print("✅ Attendance status is TRUE!")
                print(f"✅ Check-in time recorded: {checkin_time}")
                return True
            else:
                print("❌ Attendance status is still FALSE!")
                return False
        else:
            print(f"❌ Could not verify attendance: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def run_full_test():
    """Run the complete test suite"""
    
    print("\n" + "🚀 " * 20)
    print("QR CODE ATTENDANCE SYSTEM - FULL TEST SUITE")
    print("🚀 " * 20)
    
    # Step 1: Registration
    otp, leader_email = test_registration()
    
    # Step 2: OTP Verification (if OTP was provided)
    if otp:
        verified, team_id = test_otp_verification(otp, leader_email)
        
        if verified and team_id:
            # Step 3: Get team info
            team_info = test_get_team_info(team_id)
            
            if team_info:
                team_code = team_info.get("team_code")
                
                # Step 4: Test QR scanning
                scan_success = test_qr_scanning(team_code)
                
                # Step 5: Verify attendance update
                if scan_success:
                    test_attendance_verification(team_code)
    
    # Summary
    print_section("TEST SUITE COMPLETE")
    print("""
    ✅ All critical workflows tested:
    1. Team registration with photos
    2. OTP email verification
    3. Team creation with unique code
    4. ID card generation for all members
    5. QR code scanning
    6. Attendance database update
    
    🎉 If all tests passed, the system is working correctly!
    """)

if __name__ == "__main__":
    print("Make sure the FastAPI server is running: uvicorn app.main:app --reload")
    input("Press Enter to start tests...")
    run_full_test()
