#!/usr/bin/env python3
"""
Test script to verify new OTP + sequential Team ID registration flow
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_new_flow():
    """Test the new registration flow"""
    
    print("\n" + "="*70)
    print("🧪 TESTING NEW OTP + SEQUENTIAL TEAM ID REGISTRATION FLOW")
    print("="*70 + "\n")
    
    # Test 1: Import routes
    print("TEST 1: Testing Routes Import")
    print("-" * 70)
    try:
        from app import routes
        print("✅ Routes module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import routes: {e}")
        return False
    
    # Test 2: Check sequential Team ID function
    print("\nTEST 2: Testing Sequential Team ID Generation")
    print("-" * 70)
    try:
        seq_ids = []
        for i in range(1, 6):
            team_id = routes.generate_team_id_sequential(i)
            seq_ids.append(team_id)
            print(f"  Seq {i:>2}: {team_id}")
        
        # Verify format
        expected = ["HACK-001", "HACK-002", "HACK-003", "HACK-004", "HACK-005"]
        if seq_ids == expected:
            print("✅ Sequential Team ID generation working correctly")
        else:
            print(f"❌ Team IDs don't match expected: {seq_ids} vs {expected}")
            return False
    except Exception as e:
        print(f"❌ Error generating Team IDs: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Check OTP Manager
    print("\nTEST 3: Testing OTP Storage & Verification")
    print("-" * 70)
    try:
        from app.otp_manager import store_otp, verify_otp, get_otp, delete_otp
        
        test_email = "test@example.com"
        test_otp = "123456"
        
        # Store OTP
        store_otp(test_email, test_otp, expiry_seconds=300)
        print(f"✅ OTP stored for {test_email}")
        
        # Get OTP
        retrieved = get_otp(test_email)
        if retrieved == test_otp:
            print(f"✅ OTP retrieved correctly: {retrieved}")
        else:
            print(f"❌ OTP retrieval failed: {retrieved} vs {test_otp}")
            return False
        
        # Verify OTP
        if verify_otp(test_email, test_otp):
            print(f"✅ OTP verification passed")
        else:
            print(f"❌ OTP verification failed")
            return False
        
        # Delete OTP
        delete_otp(test_email)
        if get_otp(test_email) is None:
            print(f"✅ OTP cleaned up successfully")
        else:
            print(f"❌ OTP cleanup failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing OTP: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Check Email Service
    print("\nTEST 4: Testing Email Service Methods")
    print("-" * 70)
    try:
        from app.email_service import EmailService
        
        # Check methods exist
        methods = [
            'send_otp_email',
            'send_registration_confirmation',
            'send_id_cards_email'
        ]
        
        for method_name in methods:
            if hasattr(EmailService, method_name):
                print(f"✅ Method found: {method_name}")
            else:
                print(f"❌ Method missing: {method_name}")
                return False
        
        print("✅ All email methods present")
    except Exception as e:
        print(f"❌ Error testing email service: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Registration Data Storage
    print("\nTEST 5: Testing Registration Data Storage")
    print("-" * 70)
    try:
        from app.otp_manager import (
            store_registration_data,
            get_registration_data,
            delete_registration_data
        )
        
        test_email = "reg@example.com"
        test_data = {
            "team_name": "TestTeam",
            "leader_name": "TestLeader",
            "leader_email": test_email,
            "team_members": []
        }
        
        # Store data
        store_registration_data(test_email, test_data, expiry_seconds=300)
        print(f"✅ Registration data stored")
        
        # Get data
        retrieved = get_registration_data(test_email)
        if retrieved == test_data:
            print(f"✅ Registration data retrieved correctly")
        else:
            print(f"❌ Registration data mismatch")
            return False
        
        # Delete data
        delete_registration_data(test_email)
        if get_registration_data(test_email) is None:
            print(f"✅ Registration data cleaned up")
        else:
            print(f"❌ Registration data cleanup failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing registration data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Success!
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    print("\nNew OTP + Sequential Team ID system is ready!")
    print("\nFlow Summary:")
    print("  1. User registers → OTP sent to email")
    print("  2. User enters OTP → Verified")
    print("  3. Team created with sequential ID (HACK-###)")
    print("  4. Confirmation email sent")
    print("  5. ID cards generated & emailed\n")
    
    return True

if __name__ == "__main__":
    success = test_new_flow()
    sys.exit(0 if success else 1)
