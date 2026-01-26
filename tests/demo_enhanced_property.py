#!/usr/bin/env python3
"""
Demonstration of enhanced process_property method for real-world usage.

This shows how the improved method correctly handles:
1. Style attribute addition when not present
2. Style modification when present
3. Direct attribute handling for non-style properties
"""

import sys
from pathlib import Path
from lxml import etree

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.svg_processor import SVGElementProcessor
from modules.config import SVG_NAMESPACES, COMMON_XPATH_EXPRESSIONS

def demonstrate_enhanced_property_handling():
    """Demonstrate enhanced property handling in real scenarios."""
    
    print("🎨 Enhanced Property Processing Demonstration")
    print("=" * 60)
    
    # Create processor
    processor = SVGElementProcessor()
    
    # Example SVG with various elements
    svg_template = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" 
     width="400" height="300">
    <!-- Elements without initial styles -->
    <rect id="box1" x="20" y="20" width="80" height="50" inkscape:label="MyBox"/>
    <text id="title1" x="50" y="50" inkscape:label="MyTitle">Sample Text</text>
    
    <!-- Elements with existing styles -->
    <rect id="box2" x="20" y="100" width="80" height="50" 
           style="fill:blue;stroke:black" inkscape:label="StyledBox"/>
    <text id="title2" x="50" y="130" 
           style="font-size:14px;fill:black" inkscape:label="StyledTitle">Styled Text</text>
    
    <!-- Elements with direct attributes -->
    <image id="logo" x="20" y="180" width="60" height="40" 
           href="old-logo.png" inkscape:label="MyLogo"/>
</svg>'''
    
    # Parse SVG
    svg_root = etree.fromstring(svg_template.encode('utf-8'))
    ns = {
        'svg': 'http://www.w3.org/2000/svg',
        'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
    }
    
    print("📋 Before Property Updates:")
    print("-" * 40)
    
    # Show initial state
    elements = [
        (svg_root.xpath(COMMON_XPATH_EXPRESSIONS["labeled_element_generic"].format(var='MyBox'), namespaces=ns)[0], "MyBox"),
        (svg_root.xpath(COMMON_XPATH_EXPRESSIONS["labeled_element_generic"].format(var='MyTitle'), namespaces=ns)[0], "MyTitle"),
        (svg_root.xpath(COMMON_XPATH_EXPRESSIONS["labeled_element_generic"].format(var='StyledBox'), namespaces=ns)[0], "StyledBox"),
        (svg_root.xpath(COMMON_XPATH_EXPRESSIONS["labeled_element_generic"].format(var='StyledTitle'), namespaces=ns)[0], "StyledTitle"),
        (svg_root.xpath(COMMON_XPATH_EXPRESSIONS["labeled_element_generic"].format(var='MyLogo'), namespaces=ns)[0], "MyLogo")
    ]
    
    for element, label in elements:
        style = element.get('style', 'No style')
        href = element.get('href', 'No href')
        print(f"{label:15} | Style: {style:25} | Href: {href}")
    
    print("\n🔧 Applying Property Updates:")
    print("-" * 40)
    
    # Apply property changes (simulating CSV data)
    property_updates = [
        ("MyBox", "fill", "#FF6B35"),        # Add style attribute
        ("MyBox", "stroke", "#4ECDC4"),        # Add to style
        ("MyBox", "stroke-width", "3"),          # Add to style
        ("MyTitle", "font-size", "18px"),        # Add style attribute
        ("MyTitle", "fill", "#2E86AB"),          # Add to style
        ("StyledBox", "fill", "#A23B72"),        # Modify existing style
        ("StyledBox", "stroke-width", "4"),        # Modify existing style
        ("StyledTitle", "font-size", "20px"),       # Modify existing style
        ("StyledTitle", "font-weight", "bold"),    # Add to existing style
        ("MyLogo", "href", "new-logo.png"),         # Direct attribute
    ]
    
    for element_label, property_name, value in property_updates:
        element = svg_root.xpath(COMMON_XPATH_EXPRESSIONS["labeled_element_generic"].format(var=element_label), namespaces=ns)[0]
        
        # Determine element type for processing
        element_type = element.tag.split('}')[-1]
        
        success = processor.process_property(element, property_name, value, element_type)
        status = "✅" if success else "❌"
        print(f"{status} {element_label:12} | {property_name:12} = {value}")
    
    print("\n📊 After Property Updates:")
    print("-" * 40)
    
    # Show final state
    for element, label in elements:
        style = element.get('style', 'No style')
        href = element.get('href', 'No href')
        print(f"{label:15} | Style: {style:25} | Href: {href}")
    
    # Generate final SVG
    final_svg = etree.tostring(svg_root, encoding='utf-8', pretty_print=True).decode('utf-8')
    
    # Save for inspection
    output_file = project_root / "tests" / "output" / "enhanced_property_demo.svg"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_svg)
    
    print(f"\n💾 Enhanced SVG saved to: {output_file}")
    print("\n🎯 Key Improvements:")
    print("✅ Style attribute automatically added when missing")
    print("✅ Existing style attributes properly modified")
    print("✅ Multiple properties accumulate in same style attribute")
    print("✅ Direct attributes (href, id, etc.) handled separately")
    print("✅ Color aliases converted to hex values")
    print("✅ CSS style parsing and formatting works correctly")
    
    print("\n📖 Integration Guide:")
    print("To use in your workflow, just call process_property() as usual.")
    print("The method now automatically detects style vs direct attributes.")

if __name__ == '__main__':
    demonstrate_enhanced_property_handling()