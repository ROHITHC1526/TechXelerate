#!/usr/bin/env python3
"""
Test script to verify PDF ID card generation system works correctly.
Run this to ensure all components are functioning before production deployment.
"""

import os
import sys
from pathlib import Path

# Test 1: Check dependencies
print("=" * 60)
print("Testing Professional ID Card System")
print("=" * 60)

print("\n1️⃣  Checking Python dependencies...")
required_packages = ['fastapi', 'sqlalchemy', 'PIL', 'reportlab', 'qrcode', 'pydantic']
missing = []

for pkg in required_packages:
    try:
        __import__(pkg)
        print(f"   ✓ {pkg}")
    except ImportError:
        print(f"   ✗ {pkg} - MISSING")
        missing.append(pkg)

if missing:
    print(f"\n❌ Missing packages: {', '.join(missing)}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 2: Check file structure
print("\n2️⃣  Checking file structure...")
required_files = [
    'app/pdf_generator.py',
    'app/quotes.py',
    'app/tasks.py',
    'app/config.py',
    'app/models.py',
    'app/routes.py',
    'app/schemas.py'
]

for f in required_files:
    if os.path.exists(f):
        print(f"   ✓ {f}")
    else:
        print(f"   ✗ {f} - MISSING")
        sys.exit(1)

# Test 3: Check assets directory
print("\n3️⃣  Checking assets directory...")
os.makedirs('assets', exist_ok=True)
print(f"   ✓ Assets directory ready: {os.path.abspath('assets')}")

# Test 4: Test imports
print("\n4️⃣  Testing module imports...")
try:
    from app.pdf_generator import IDCardGenerator
    print("   ✓ IDCardGenerator loaded")
    
    from app.quotes import get_random_quote, get_quote_by_index
    print("   ✓ Quotes module loaded")
    
    from app.tasks import send_otp_email_sync, generate_assets_and_email, send_id_cards_email
    print("   ✓ Tasks functions loaded")
    
    from app.config import settings
    print("   ✓ Config settings loaded")
    
    from app.schemas import RegisterIn, TeamOut, OTPIn
    print("   ✓ Schemas loaded")
    
except ImportError as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)

# Test 5: Test PDF generator instantiation
print("\n5️⃣  Testing PDF generator initialization...")
try:
    generator = IDCardGenerator(output_dir='assets')
    print("   ✓ IDCardGenerator instantiated successfully")
except Exception as e:
    print(f"   ✗ PDF generator error: {e}")
    sys.exit(1)

# Test 6: Test quote retrieval
print("\n6️⃣  Testing quote system...")
try:
    quote1 = get_random_quote()
    quote2 = get_quote_by_index(0)
    if quote1 and quote2:
        print(f"   ✓ Random quote: '{quote1[:50]}...'")
        print(f"   ✓ Indexed quote: '{quote2[:50]}...'")
    else:
        print("   ✗ Quotes not returned")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Quote system error: {e}")
    sys.exit(1)

# Test 7: Test mock team data
print("\n7️⃣  Testing with sample team data...")
try:
    sample_team_data = {
        'team_id': 'TEST001',
        'team_name': 'Test Team',
        'leader_name': 'Test Leader',
        'year': 'First Year',
        'domain': 'Explainable AI',
        'access_key': 'ABC123DEF456'
    }
    
    sample_members = [
        {'name': 'Member One', 'email': 'member1@example.com', 'phone': '9876543210'},
        {'name': 'Member Two', 'email': 'member2@example.com', 'phone': '9876543211'}
    ]
    
    # Test PDF generation (requires reportlab/PIL)
    output_path = generator.generate_participant_id_cards(
        team_data=sample_team_data,
        team_members_list=sample_members,
        output_filename='test_id_cards.pdf'
    )
    
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"   ✓ PDF generated: {output_path}")
        print(f"   ✓ File size: {file_size} bytes")
        
        # Clean up
        os.remove(output_path)
        print("   ✓ Test PDF cleaned up")
    else:
        print(f"   ✗ PDF not created at {output_path}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ✗ Sample data test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Check environment
print("\n8️⃣  Checking environment configuration...")
try:
    if settings.SMTP_HOST:
        print(f"   ✓ SMTP Host: {settings.SMTP_HOST}")
    else:
        print("   ⚠️  SMTP Host not configured")
    
    if settings.DATABASE_URL:
        print(f"   ✓ Database URL configured")
    else:
        print("   ✗ Database URL missing")
        sys.exit(1)
    
    if settings.JWT_SECRET:
        print(f"   ✓ JWT Secret configured")
    else:
        print("   ✗ JWT Secret missing")
        sys.exit(1)
        
except Exception as e:
    print(f"   ✗ Configuration error: {e}")
    sys.exit(1)

# Final summary
print("\n" + "=" * 60)
print("✅ All tests passed! System is ready for deployment.")
print("=" * 60)
print("\nNext steps:")
print("1. Ensure PostgreSQL is running: localhost:5432")
print("2. Ensure .env file has SMTP credentials configured")
print("3. Start FastAPI: python -m uvicorn app.main:app --reload")
print("4. Start Frontend: cd frontend && npm run dev")
print("5. Test at: http://localhost:3000/registration")
print("\nGenerated ID cards will be saved to: ./assets/")
print("=" * 60)
