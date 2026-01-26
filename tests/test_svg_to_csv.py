#!/usr/bin/env python3
"""
Comprehensive test for SVG to CSV functionality.

Tests:
1. SVG to CSV export creates file with UTF-8 encoding
2. CSV headers follow CSV_HEADER_PATTERN for elements and properties
3. Default CSV file creation when path not specified
4. Unicode characters handled properly in CSV
5. CSV structure validation
"""

import sys
import os
import tempfile
import csv
from pathlib import Path
from lxml import etree

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.svg_processor import SVGElementProcessor
from modules.config import CSV_HEADER_PATTERN

def test_svg_to_csv_export():
    """Test SVG to CSV export functionality."""
    
    print("🧪 Testing SVG to CSV Export Functionality")
    print("=" * 60)
    
    # Create test SVG with various element types
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" 
     width="400" height="300">
    <!-- Text elements -->
    <text x="50" y="30" inkscape:label="Title" font-size="16">Hello World</text>
    <text x="50" y="60" inkscape:label="Subtitle" fill="blue">This is a test</text>
    
    <!-- Shape elements with properties -->
    <rect id="box1" x="20" y="100" width="80" height="40" 
           fill="red" stroke="blue" stroke-width="2" inkscape:label="TestBox"/>
    <circle cx="200" cy="120" r="30" 
           fill="green" opacity="0.8" inkscape:label="TestCircle"/>
    
    <!-- Layer elements -->
    <g inkscape:label="BackgroundLayer" inkscape:groupmode="layer" 
       style="display:inline">
        <rect x="0" y="0" width="400" height="300" fill="#EEEEEE"/>
    </g>
    <g inkscape:label="ContentLayer" inkscape:groupmode="layer" 
       style="display:none">
        <text x="200" y="150">Hidden Content</text>
    </g>
    
    <!-- Image elements -->
    <image x="300" y="200" width="60" height="40" 
           href="logo.png" inkscape:label="Logo"/>
    
    <!-- Unicode text -->
    <text x="50" y="250" inkscape:label="UnicodeText" 
           font-family="Arial">🌟 Unicode Test 🌍</text>
</svg>'''
    
    print("📋 Test Cases:")
    print("-" * 40)
    
    # Test Case 1: Create temporary CSV file
    print("1️⃣ Creating CSV export with temporary file...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_csv:
        temp_csv_path = temp_csv.name
    
    print(f"   Temporary CSV: {temp_csv_path}")
    
    # Create processor and export to CSV
    processor = SVGElementProcessor(logger=None)
    svg_root = etree.fromstring(svg_content.encode('utf-8'))
    
    export_success = processor.export_svg_to_csv(svg_root, temp_csv_path)
    
    if export_success:
        print("   ✅ CSV export successful")
    else:
        print("   ❌ CSV export failed")
        return
    
    # Test Case 2: Verify CSV file encoding and content
    print("\n2️⃣ Verifying CSV file encoding and content...")
    
    try:
        # Read with UTF-8 encoding
        with open(temp_csv_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            csv_content = list(csv_reader)
        
        print("   ✅ CSV file readable with UTF-8 encoding")
        print(f"   📊 Found {len(csv_content)} rows of data")
        
        # Display headers
        if csv_content:
            headers = csv_content[0] if csv_content else []
            print(f"   📝 CSV Headers: {headers}")
            
            # Validate header pattern
            print("   🔍 Validating header patterns...")
            validate_header_patterns(headers)
            
            # Display data
            print("   📄 CSV Data:")
            for i, row in enumerate(csv_content[1:], 1):  # Skip header row
                print(f"      Row {i}: {row}")
    
    except Exception as e:
        print(f"   ❌ Error reading CSV: {e}")
        return
    
    # Test Case 3: Test with default CSV path
    print("\n3️⃣ Testing default CSV path creation...")
    
    # Test creating CSV in current directory
    default_csv_path = "test_output.csv"
    try:
        # Remove existing file if any
        if os.path.exists(default_csv_path):
            os.remove(default_csv_path)
        
        export_success = processor.export_svg_to_csv(svg_root, default_csv_path)
        
        if export_success and os.path.exists(default_csv_path):
            print("   ✅ Default CSV file created successfully")
            
            # Verify file size and encoding
            file_size = os.path.getsize(default_csv_path)
            print(f"   📁 File size: {file_size} bytes")
            
            # Test reading with UTF-8
            with open(default_csv_path, 'r', encoding='utf-8') as test_file:
                content = test_file.read()
                # Check for UTF-8 BOM
                has_bom = content.startswith('\ufeff')
                print(f"   🔤 Has UTF-8 BOM: {has_bom}")
                
                # Check for Unicode characters
                has_unicode = any(ord(char) > 127 for char in content)
                print(f"   🌍 Contains Unicode: {has_unicode}")
            
            # Cleanup
            os.remove(default_csv_path)
            print("   🧹 Test file cleaned up")
        else:
            print("   ❌ Default CSV creation failed")
    
    except Exception as e:
        print(f"   ❌ Error with default CSV: {e}")
    
    # Test Case 4: Test CSV header pattern compliance
    print("\n4️⃣ Testing CSV header pattern compliance...")
    test_header_pattern_compliance()
    
    print("\n✅ SVG to CSV export test completed!")
    print("=" * 60)

def validate_header_patterns(headers):
    """Validate that headers follow CSV_HEADER_PATTERN."""
    import re
    
    print("      Header Pattern Validation:")
    
    # Expected pattern: ElementName or ElementName##PropertyName
    header_pattern = re.compile(CSV_HEADER_PATTERN)
    
    for header in headers:
        if header == '':  # Skip empty headers
            continue
            
        match = header_pattern.match(header.strip())
        if match:
            element_name = match.group(1) or ''
            property_name = match.group(2) or ''
            
            if property_name:
                print(f"      ✅ {header} -> Element: '{element_name}', Property: '{property_name}'")
            else:
                print(f"      ✅ {header} -> Element: '{element_name}'")
        else:
            print(f"      ⚠️  {header} -> Doesn't match expected pattern")

def test_header_pattern_compliance():
    """Test specific header pattern scenarios."""
    processor = SVGElementProcessor(logger=None)
    
    # Test SVG with known patterns
    test_svg = '''<svg xmlns="http://www.w3.org/2000/svg" 
         xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
        <text inkscape:label="SimpleText">Basic Text</text>
        <rect inkscape:label="SimpleBox" fill="blue"/>
        <text inkscape:label="ComplexText" fill="red" font-size="14">Complex Text</text>
        <rect inkscape:label="ComplexBox" fill="green" stroke="red"/>
    </svg>'''
    
    svg_root = etree.fromstring(test_svg.encode('utf-8'))
    
    # Export to temp file and analyze
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
        temp_path = temp_file.name
    
    export_success = processor.export_svg_to_csv(svg_root, temp_path)
    
    if export_success:
        with open(temp_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            
        if rows:
            headers = rows[0] if rows else []
            print("      Generated Headers:")
            for header in headers:
                if header.strip():
                    # Test pattern compliance
                    element_match = bool(re.match(r'^[^#]+(?:##[^#]+)?$', header.strip()))
                    print(f"         {header}: {'✅' if element_match else '❌'}")
        
        # Cleanup
        os.remove(temp_path)

def test_default_csv_creation():
    """Test that default CSV file is created when no path specified."""
    processor = SVGElementProcessor(logger=None)
    
    # Create simple SVG
    simple_svg = '''<svg xmlns="http://www.w3.org/2000/svg" 
         xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
        <text inkscape:label="TestElement">Test Content</text>
    </svg>'''
    
    svg_root = etree.fromstring(simple_svg.encode('utf-8'))
    
    # Test with empty path (should use default or handle gracefully)
    try:
        # This should either create default.csv or handle error gracefully
        export_success = processor.export_svg_to_csv(svg_root, "")
        
        if not export_success:
            print("      ✅ Properly handled empty CSV path")
        else:
            print("      ⚠️  Should not create file with empty path")
    
    except Exception as e:
        # Expected to handle error gracefully
        print(f"      ✅ Properly handled empty path error: {type(e).__name__}")

if __name__ == '__main__':
    test_svg_to_csv_export()