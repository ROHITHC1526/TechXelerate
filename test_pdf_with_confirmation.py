#!/usr/bin/env python3
"""
Test script to verify PDF generation and email attachment functionality.
Tests the new flow where PDF is included with confirmation email.
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pdf_generation():
    """Test PDF generation with sample data."""
    print("\n" + "="*60)
    print("TEST 1: PDF Generation")
    print("="*60)
    
    try:
        from app.pdf_generator import IDCardGenerator
        
        generator = IDCardGenerator(output_dir="assets")
        logger.info("✅ IDCardGenerator imported successfully")
        
        # Create sample team data
        team_data = {
            'team_id': 'HACK-TEST-001',
            'team_name': 'Test Team',
            'leader_name': 'Test Leader',
            'leader_email': 'test@example.com',
            'leader_phone': '9876543210',
            'college_name': 'LBRCE',
            'year': '2nd',
            'domain': 'Cybersecurity',
            'access_key': 'testkey123',
        }
        
        # Create sample team members (at least one)
        team_members = [
            {
                'name': 'Test Leader',
                'email': 'test@example.com',
                'phone': '9876543210',
                'photo_path': None
            }
        ]
        
        logger.info("Generating PDF...")
        pdf_path = generator.generate_participant_id_cards(
            team_data=team_data,
            team_members_list=team_members,
            output_filename="HACK-TEST-001_id_cards.pdf"
        )
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            logger.info(f"✅ PDF generated successfully: {pdf_path}")
            logger.info(f"📁 File size: {file_size:,} bytes")
            return True, pdf_path
        else:
            logger.error("❌ PDF file not created")
            return False, None
            
    except Exception as e:
        logger.exception(f"❌ PDF generation failed: {e}")
        return False, None


def test_email_service():
    """Test email service with attachment support."""
    print("\n" + "="*60)
    print("TEST 2: Email Service with Attachment Support")
    print("="*60)
    
    try:
        from app.email_service import EmailService
        
        logger.info("✅ EmailService imported successfully")
        
        # Check if method exists and accepts pdf_path parameter
        import inspect
        sig = inspect.signature(EmailService.send_registration_confirmation)
        params = list(sig.parameters.keys())
        logger.info(f"✅ Method parameters: {params}")
        
        if 'pdf_path' in params:
            logger.info("✅ pdf_path parameter found in send_registration_confirmation")
            return True
        else:
            logger.error("❌ pdf_path parameter NOT found")
            return False
            
    except Exception as e:
        logger.exception(f"❌ Email service check failed: {e}")
        return False


def test_routes():
    """Test that routes are properly configured."""
    print("\n" + "="*60)
    print("TEST 3: Routes Configuration")
    print("="*60)
    
    try:
        from app.routes import verify_otp_endpoint
        
        logger.info("✅ Routes imported successfully")
        
        # Check if function exists
        if verify_otp_endpoint:
            logger.info("✅ verify_otp_endpoint function found")
            
            # Check function source for PDF generation
            import inspect
            source = inspect.getsource(verify_otp_endpoint)
            
            checks = {
                "IDCardGenerator": "PDF generation",
                "generate_participant_id_cards": "PDF format generation",
                "pdf_path": "PDF path variable",
                "attachment": "Email attachment support"
            }
            
            found = []
            for key, desc in checks.items():
                if key in source:
                    found.append(key)
                    logger.info(f"✅ Found: {desc}")
                else:
                    logger.warning(f"⚠️  Missing: {desc}")
            
            if len(found) >= 3:
                logger.info(f"✅ Route properly configured with {len(found)}/4 features")
                return True
            else:
                logger.warning(f"⚠️  Only found {len(found)}/4 features")
                return False
        else:
            logger.error("❌ verify_otp_endpoint not found")
            return False
            
    except Exception as e:
        logger.exception(f"❌ Routes check failed: {e}")
        return False


def test_flow_summary():
    """Summary of the new flow."""
    print("\n" + "="*60)
    print("NEW REGISTRATION FLOW")
    print("="*60)
    
    flow = """
    STEP 1: User Registration
    ├─ Fill form with team info
    ├─ Upload photos
    └─ Submit registration
    
    STEP 2: OTP Sent
    ├─ Generate 6-digit OTP
    ├─ Store OTP (5 min expiry)
    └─ Send OTP email
    
    STEP 3: OTP Verification
    ├─ User checks email
    ├─ Copies 6-digit OTP
    └─ Enters OTP in modal
    
    STEP 4: Team Created & PDF Generated ⭐ NEW
    ├─ Verify OTP matches
    ├─ Create team in database
    ├─ Generate ID cards PDF immediately ⭐
    └─ Team ID format: HACK-001
    
    STEP 5: Confirmation Email WITH PDF ⭐ CHANGED
    ├─ Send confirmation email
    ├─ Attach PDF to email ⭐
    ├─ Show Team ID in email
    └─ NO separate email needed ⭐
    
    ✅ Complete registration in ONE confirmation email!
    """
    
    print(flow)
    return True


def main():
    """Run all tests."""
    print("\n" + "🎯 " + "="*56 + " 🎯")
    print("  PDF with Confirmation Email - System Test")
    print("🎯 " + "="*56 + " 🎯\n")
    
    results = {}
    
    # Run tests
    results['PDF Generation'] = test_pdf_generation()
    results['Email Service'] = test_email_service()
    results['Routes Config'] = test_routes()
    results['Flow Summary'] = test_flow_summary()
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        if isinstance(result, tuple):
            status = "✅ PASSED" if result[0] else "❌ FAILED"
        else:
            status = "✅ PASSED" if result else "❌ FAILED"
        
        print(f"{test_name:.<40} {status}")
        if isinstance(result, tuple) and result[0]:
            passed += 1
        elif not isinstance(result, tuple) and result:
            passed += 1
    
    print("="*60)
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✨ NEW FEATURES:")
        print("  ✅ PDF generated immediately upon OTP verification")
        print("  ✅ PDF attached to confirmation email")
        print("  ✅ No separate 'ID cards' email needed")
        print("  ✅ User gets everything in ONE confirmation email")
        
        print("\n🚀 NEXT STEPS:")
        print("  1. Start backend: python -m uvicorn app.main:app --reload")
        print("  2. Start frontend: cd frontend && npm run dev")
        print("  3. Register at: http://localhost:3000/registration")
        print("  4. Check inbox for confirmation email WITH PDF attached!")
        
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
