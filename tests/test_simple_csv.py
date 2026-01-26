#!/usr/bin/env python3
"""
Simple test to verify SVG to CSV functionality works.
"""

import sys
import tempfile
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Try direct import test
print("Testing imports...")

try:
    from modules.svg_processor import SVGElementProcessor
    print("✅ SVGElementProcessor imported successfully")
except ImportError as e:
    print(f"❌ SVGElementProcessor import failed: {e}")
    sys.exit(1)

try:
    from modules.config import CSV_HEADER_PATTERN
    print(f"✅ Config imported, CSV_HEADER_PATTERN: {CSV_HEADER_PATTERN}")
except ImportError as e:
    print(f"❌ Config import failed: {e}")
    sys.exit(1)

# Create simple test
processor = SVGElementProcessor()
print("✅ SVGElementProcessor created successfully")

# Create simple SVG
from lxml import etree

simple_svg = '''<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
    <text inkscape:label="TestText">Hello World</text>
    <rect inkscape:label="TestBox" fill="blue"/>
</svg>'''

svg_root = etree.fromstring(simple_svg.encode('utf-8'))

# Test CSV export
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
    temp_path = temp_file.name
    
success = processor.export_svg_to_csv(svg_root, temp_path)
print(f"CSV export result: {success}")

if success and os.path.exists(temp_path):
    # Read and display CSV content
    with open(temp_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print("CSV content:")
        print(content)
    os.remove(temp_path)
    print("✅ SVG to CSV export working correctly!")
else:
    print("❌ CSV export failed")