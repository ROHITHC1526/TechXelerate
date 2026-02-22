#!/usr/bin/env python3
"""
Comprehensive OTP Email Debugging Script
Tests the entire OTP sending flow step by step
"""

import sys
import smtplib
from email.message import EmailMessage
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_otp_flow():
    """Test complete OTP sending flow"""
    
    print("\n" + "="*70)
    print("🔍 OTP EMAIL SENDING - COMPLETE DIAGNOSTIC")
    print("="*70 + "\n")
    
    # Step 1: Load environment
    print("📝 STEP 1: Loading Configuration")
    print("-" * 70)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Environment loaded")
    except Exception as e:
        print(f"❌ Failed to load .env: {e}")
        return False
    
    # Step 2: Check settings
    print("\n📝 STEP 2: Checking Settings")
    print("-" * 70)
    try:
        from app.config import settings
        
        print(f"SMTP_HOST: {settings.SMTP_HOST}")
        print(f"SMTP_PORT: {settings.SMTP_PORT}")
        print(f"SMTP_USER: {settings.SMTP_USER}")
        print(f"SMTP_PASS: {'*' * len(settings.SMTP_PASS) if settings.SMTP_PASS else 'NOT SET'}")
        
        if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASS]):
            print("\n❌ SMTP configuration incomplete!")
            return False
        
        print("\n✓ All settings configured")
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Test raw SMTP connection
    print("\n📝 STEP 3: Testing Raw SMTP Connection")
    print("-" * 70)
    try:
        print(f"Connecting to {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
        server = smtplib.SMTP(settings.SMTP_HOST, int(settings.SMTP_PORT), timeout=10)
        print("✓ Connected")
        
        print("Starting TLS...")
        server.starttls()
        print("✓ TLS started")
        
        print(f"Authenticating as {settings.SMTP_USER}...")
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        print("✓ Authenticated")
        
        server.quit()
        print("✓ Connection successful")
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Test EmailService._get_smtp_config
    print("\n📝 STEP 4: Testing EmailService Configuration Validation")
    print("-" * 70)
    try:
        from app.email_service import EmailService
        
        is_valid, error = EmailService._get_smtp_config()
        print(f"Configuration valid: {is_valid}")
        if error:
            print(f"Error message: {error}")
        else:
            print("✓ Configuration validated by EmailService")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Test EmailMessage creation
    print("\n📝 STEP 5: Testing Email Message Creation")
    print("-" * 70)
    try:
        test_otp = "123456"
        test_email = settings.SMTP_USER
        
        message = EmailMessage()
        message["From"] = settings.SMTP_USER
        message["To"] = test_email
        message["Subject"] = "🔐 Test OTP Email"
        
        plain_body = f"Test OTP: {test_otp}"
        html_body = f"<html><body><h2>Test OTP: {test_otp}</h2></body></html>"
        
        message.set_content(plain_body)
        message.add_alternative(html_body, subtype="html")
        
        print(f"✓ Message created successfully")
        print(f"  From: {message['From']}")
        print(f"  To: {message['To']}")
        print(f"  Subject: {message['Subject']}")
    except Exception as e:
        print(f"❌ Failed to create message: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 6: Test actual email send
    print("\n📝 STEP 6: Testing Actual Email Send")
    print("-" * 70)
    try:
        print(f"Sending test email to {test_email}...")
        
        with smtplib.SMTP(settings.SMTP_HOST, int(settings.SMTP_PORT), timeout=10) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(message)
        
        print(f"✓ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 7: Test EmailService.send_otp_email
    print("\n📝 STEP 7: Testing EmailService.send_otp_email()")
    print("-" * 70)
    try:
        from app.email_service import EmailService
        
        test_otp = "654321"
        test_email = settings.SMTP_USER
        
        print(f"Calling EmailService.send_otp_email('{test_email}', '{test_otp}')...")
        result = EmailService.send_otp_email(test_email, test_otp)
        
        print(f"Result: {result}")
        if result:
            print(f"✓ EmailService.send_otp_email() returned True")
        else:
            print(f"❌ EmailService.send_otp_email() returned False")
            return False
    except Exception as e:
        print(f"❌ Error calling EmailService: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 8: Test via tasks.send_otp_email_sync
    print("\n📝 STEP 8: Testing via tasks.send_otp_email_sync()")
    print("-" * 70)
    try:
        from app.tasks import send_otp_email_sync
        
        test_otp = "111222"
        test_email = settings.SMTP_USER
        
        print(f"Calling send_otp_email_sync('{test_email}', '{test_otp}')...")
        result = send_otp_email_sync(test_email, test_otp)
        
        print(f"Result: {result}")
        if result:
            print(f"✓ send_otp_email_sync() returned True")
        else:
            print(f"❌ send_otp_email_sync() returned False")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Success
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED! OTP SENDING SHOULD WORK!")
    print("="*70)
    print("\nCheck your email inbox (including SPAM folder) for test emails.")
    print("If you received test emails above, OTP sending is working correctly.\n")
    return True

if __name__ == "__main__":
    success = test_otp_flow()
    sys.exit(0 if success else 1)
