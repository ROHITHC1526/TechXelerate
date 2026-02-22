#!/usr/bin/env python
"""Debug PDF generation to find the issue."""

import os
import logging
from pathlib import Path

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

from app.pdf_generator import IDCardGenerator

# Clean up any old debug files
debug_dir = Path('assets')
for f in debug_dir.glob('*DEBUG*'):
    try:
        f.unlink()
        print(f"Deleted old debug file: {f.name}")
    except:
        pass

team_data = {
    'team_id': 'DEBUG-001',
    'team_name': 'Debug Team',
    'domain': 'Web Dev',
    'year': '2nd',
}

team_members = [
    {'name': 'Member 1'},
    {'name': 'Member 2'},
]

try:
    print("\n" + "="*60)
    print("STARTING PDF GENERATION")
    print("="*60)
    generator = IDCardGenerator(output_dir='assets')
    pdf_path = generator.generate_participant_id_cards(
        team_data, 
        team_members, 
        'DEBUG-001_id_cards.pdf'
    )
    print(f"\n✅ PDF generation returned: {pdf_path}")
    
    # Check what files exist NOW
    print("\n" + "="*60)
    print("FILES CREATED:")
    print("="*60)
    for f in sorted(debug_dir.glob('*DEBUG*')):
        size_kb = f.stat().st_size / 1024
        print(f"{f.name}: {size_kb:.2f} KB")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
