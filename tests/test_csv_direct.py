#!/usr/bin/env python3
"""
Test SVG to CSV functionality by running from project root.
"""

import os
import sys
import tempfile
from pathlib import Path

# Change to project directory
project_dir = Path(__file__).parent
os.chdir(project_dir)

# Add current directory to Python path
sys.path.insert(0, str(project_dir))

print(f"Working directory: {os.getcwd()}")
print(f"Project directory: {project_dir}")

# Test imports
try:
    from modules.svg_processor import SVGElementProcessor
    from modules.config import CSV_HEADER_PATTERN
    print("✅ Imports successful")
    print(f"CSV_HEADER_PATTERN: {CSV_HEADER_PATTERN}")
    
    # Create processor
    processor = SVGElementProcessor()
    
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

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()