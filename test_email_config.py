#!/usr/bin/env python3
"""
Test script to verify SMTP/Email configuration is working correctly.
Run this before starting your application.
"""

import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
TEST_EMAIL = os.getenv("SMTP_USER", "")  # Send test email to configured sender

def test_smtp_connection():
    """Test SMTP connection and credentials."""
    print("\n" + "="*60)
    print("TESTING SMTP CONFIGURATION")
    print("="*60)
    
    print(f"\nSMTP Host: {SMTP_HOST}")
    print(f"SMTP Port: {SMTP_PORT}")
    print(f"SMTP User: {SMTP_USER}")
    print(f"SMTP Pass: {'*' * len(SMTP_PASS) if SMTP_PASS else 'NOT SET'}")
    
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]):
        print("\n❌ ERROR: SMTP configuration incomplete in .env file!")
        print("   Please set: SMTP_HOST, SMTP_USER, SMTP_PASS")
        return False
    
    try:
        print("\n▶ Connecting to SMTP server...")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        print("✓ Connected successfully")
        
        print("▶ Starting TLS...")
        server.starttls()
        print("✓ TLS started")
        
        print("▶ Authenticating...")
        server.login(SMTP_USER, SMTP_PASS)
        print("✓ Authentication successful")
        
        print("\n✓ SMTP configuration is VALID!")
        
        # Test sending a test email
        print("\n▶ Sending test email...")
        message = EmailMessage()
        message["From"] = SMTP_USER
        message["To"] = TEST_EMAIL
        message["Subject"] = "Hackathon Registration - SMTP Test"
        
        message.set_content("This is a test email to verify SMTP configuration is working.")
        message.add_alternative(
            "<html><body><h2>Test Email</h2><p>SMTP configuration is working!</p></body></html>",
            subtype="html"
        )
        
        server.send_message(message)
        print(f"✓ Test email sent to {TEST_EMAIL}")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ AUTHENTICATION FAILED: {e}")
        print("   - Check SMTP_USER and SMTP_PASS in .env")
        print("   - For Gmail: Use an App Password (not your regular password)")
        return False
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP ERROR: {e}")
        print("   - Check SMTP_HOST and SMTP_PORT")
        print("   - Check internet connection")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_otp_send():
    """Test OTP sending function."""
    print("\n" + "="*60)
    print("TESTING OTP SEND FUNCTION")
    print("="*60)
    
    try:
        from app.config import settings
        from app.tasks import send_otp_email_sync
        
        # Use a test OTP
        test_otp = "123456"
        test_email = SMTP_USER
        
        print(f"\n▶ Sending test OTP {test_otp} to {test_email}...")
        result = send_otp_email_sync(test_email, test_otp)
        
        if result:
            print("✓ OTP sent successfully!")
            return True
        else:
            print("❌ OTP send failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing OTP function: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 HACKATHON REGISTRATION - EMAIL CONFIGURATION TEST\n")
    
    # Test SMTP connection
    smtp_ok = test_smtp_connection()
    
    if smtp_ok:
        print("\n" + "="*60)
        print("All tests passed! ✓")
        print("="*60)
        print("\nYour email configuration is working correctly.")
        print("OTP emails should be sent successfully during registration.\n")
    else:
        print("\n" + "="*60)
        print("Configuration issues detected! ❌")
        print("="*60)
        print("\nPlease fix the above issues before running the application.\n")
