#!/usr/bin/env python3
"""Simple test to verify Unicode handling fix."""

import sys
from pathlib import Path
from lxml import etree

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_unicode_serialization():
    """Test Unicode handling in SVG serialization."""
    
    # Create SVG with Unicode text
    unicode_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
  <text x="50" y="50" inkscape:label="UnicodeTest" font-size="16">🌟 Unicode Test 🌍</text>
</svg>"""
    
    # Parse SVG
    svg_root = etree.fromstring(unicode_svg.encode('utf-8'))
    
    # Test old method (problematic)
    print("Testing OLD method (encoding='unicode'):")
    try:
        old_str = etree.tostring(svg_root, encoding='unicode', pretty_print=True, xml_declaration=False)
        print(f"OLD Result length: {len(old_str)}")
        print(f"OLD Contains Unicode: {'🌟' in old_str}")
        print(f"OLD Sample: {old_str[:100]}...")
    except Exception as e:
        print(f"OLD Method Error: {e}")
    
    # Test new method (fixed)
    print("\nTesting NEW method (encoding='utf-8'):")
    try:
        new_bytes = etree.tostring(svg_root, encoding='utf-8', pretty_print=True, xml_declaration=False)
        new_str = new_bytes.decode('utf-8')
        print(f"NEW Result length: {len(new_str)}")
        print(f"NEW Contains Unicode: {'🌟' in new_str}")
        print(f"NEW Sample: {new_str[:100]}...")
    except Exception as e:
        print(f"NEW Method Error: {e}")
    
    # Compare results
    print("\n=== COMPARISON ===")
    try:
        old_str = etree.tostring(svg_root, encoding='unicode', pretty_print=True, xml_declaration=False)
        new_bytes = etree.tostring(svg_root, encoding='utf-8', pretty_print=True, xml_declaration=False)
        new_str = new_bytes.decode('utf-8')
        
        print("Both methods completed - checking Unicode preservation:")
        print(f"OLD method preserves Unicode: {'🌟' in old_str}")
        print(f"NEW method preserves Unicode: {'🌟' in new_str}")
        
        if '🌟' in new_str and '🌟' not in old_str:
            print("✅ NEW method correctly handles Unicode, OLD method fails")
        elif '🌟' in old_str and '🌟' in new_str:
            print("⚠️ Both methods work (possible platform difference)")
        else:
            print("❌ Unicode handling issue detected")
            
    except Exception as e:
        print(f"Comparison failed: {e}")

def test_unicode_roundtrip():
    """Test Unicode roundtrip through SVG processing."""
    
    # Create SVG with various Unicode characters
    test_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
  <text inkscape:label="Emoji">😀😃😄😁😆😅😂🤣😊😇</text>
  <text inkscape:label="Chinese">中文测试</text>
  <text inkscape:label="Arabic">اختبار العربية</text>
  <text inkscape:label="Mixed">Hello 🌍 World 中文!</text>
</svg>"""
    
    print("=== UNICODE ROUNDTRIP TEST ===")
    
    # Parse and re-serialize using new method
    svg_root = etree.fromstring(test_svg.encode('utf-8'))
    
    # Test new UTF-8 method
    svg_bytes = etree.tostring(svg_root, encoding='utf-8', pretty_print=True)
    svg_str = svg_bytes.decode('utf-8')
    
    print(f"Original length: {len(test_svg)}")
    print(f"Serialized length: {len(svg_str)}")
    
    # Check for Unicode preservation
    unicode_tests = [
        ('😀😃😄😁😆😅😂🤣😊😇', 'Emoji'),
        ('中文测试', 'Chinese'),
        ('اختبار العربية', 'Arabic'),
        ('Hello 🌍 World 中文!', 'Mixed')
    ]
    
    all_preserved = True
    for text, description in unicode_tests:
        preserved = text in svg_str
        status = "✅" if preserved else "❌"
        print(f"{status} {description}: {text[:20]}... preserved: {preserved}")
        if not preserved:
            all_preserved = False
    
    print(f"\n=== RESULT: {'✅ ALL UNICODE PRESERVED' if all_preserved else '❌ SOME UNICODE LOST'} ===")

if __name__ == '__main__':
    test_unicode_serialization()
    test_unicode_roundtrip()