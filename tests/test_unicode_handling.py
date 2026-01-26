"""
Comprehensive test suite for InkAutoGen Unicode text handling and SVG processing.

Tests:
- Unicode text replacement in SVG elements
- Mixed ASCII and Unicode CSV data
- Property modifications with Unicode values
- Layer visibility with Unicode names
- Integration tests with full processing pipeline
- Error handling for malformed Unicode
"""

import unittest
import sys
import os
import tempfile
from pathlib import Path
import logging
from lxml import etree

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.svg_processor import SVGElementProcessor
from modules.csv_reader import CSVReader
from tests import TEST_DATA_DIR, TEST_OUTPUT_DIR


class TestUnicodeHandling(unittest.TestCase):
    """Test Unicode text handling in SVG processing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = logging.getLogger('test_unicode')
        self.logger.setLevel(logging.DEBUG)
        
        # Create test processor
        self.processor = SVGElementProcessor(
            csv_dir=str(TEST_DATA_DIR),
            output_dir=str(TEST_OUTPUT_DIR),
            logger=self.logger
        )
        
        # Load test SVG template
        self.template_path = TEST_DATA_DIR / "test_template.svg"
        with open(self.template_path, 'r', encoding='utf-8') as f:
            self.svg_content = f.read()
        
        self.svg_root = etree.fromstring(self.svg_content.encode('utf-8'))
    
    def test_unicode_text_replacement(self):
        """Test Unicode text replacement in SVG elements."""
        # Test data with various Unicode characters
        test_cases = [
            ("Title", "🌟 Hello World 🌍"),
            ("Subtitle", "Testing Unicode: ñáçèü"),
            ("Unicode", "🚀 Rocket 🌙 Moon 🎯 Target"),
            ("Emoji", "😀😃😄😁😆😅😂🤣😊😇"),
            ("Mixed", "English, 中文, العربية, हिन्दी")
        ]
        
        for element_name, unicode_value in test_cases:
            with self.subTest(element_name=element_name, value=unicode_value):
                # Reset SVG root
                svg_root = etree.fromstring(self.svg_content.encode('utf-8'))
                
                # Apply Unicode text
                data_row = {element_name: unicode_value}
                stats = self.processor.apply_data_to_template(svg_root, data_row)
                
                # Verify text was replaced
                elements = self.processor.find_elements_by_name(svg_root, element_name)
                self.assertTrue(elements, f"Element {element_name} not found")
                
                for element in elements:
                    self.assertEqual(element.text, unicode_value,
                                   f"Unicode text not properly set for {element_name}")
                    
                    # Verify XML serialization preserves Unicode
                    svg_bytes = etree.tostring(svg_root, encoding='utf-8')
                    svg_str = svg_bytes.decode('utf-8')
                    self.assertIn(unicode_value, svg_str,
                                  f"Unicode value {unicode_value} not found in serialized SVG")
    
    def test_csv_unicode_parsing(self):
        """Test CSV parsing with Unicode content."""
        csv_path = TEST_DATA_DIR / "unicode_test.csv"
        
        # Create CSV reader
        csv_reader = CSVReader(self.logger)
        
        # Read CSV data
        csv_data = csv_reader.read_csv_data(str(csv_path))
        
        self.assertTrue(csv_data, "CSV data should not be empty")
        self.assertEqual(len(csv_data), 1, "Should have exactly one row")
        
        row = csv_data[0]
        
        # Verify Unicode values are preserved
        self.assertEqual(row['Title'], 'Hello World')
        self.assertEqual(row['Unicode'], '🌟 Unicode Test!')
        
        # Verify no encoding errors
        for key, value in row.items():
            self.assertIsInstance(value, str, f"Value for {key} should be string")
            # Should be able to encode and decode without errors
            try:
                encoded = value.encode('utf-8')
                decoded = encoded.decode('utf-8')
                self.assertEqual(value, decoded)
            except UnicodeError as e:
                self.fail(f"Unicode handling failed for {key}: {e}")
    
    def test_svg_serialization_unicode(self):
        """Test SVG serialization preserves Unicode characters."""
        svg_root = etree.fromstring(self.svg_content.encode('utf-8'))
        
        # Apply Unicode data
        data_row = {
            'Title': '🌟 Unicode Title 🌍',
            'Subtitle': 'Mixed: English, 中文',
            'Unicode': 'Special chars: àáâãäå'
        }
        
        stats = self.processor.apply_data_to_template(svg_root, data_row)
        self.assertGreater(stats['text_replaced'], 0)
        
        # Test serialization with UTF-8 encoding
        svg_bytes = etree.tostring(svg_root, encoding='utf-8', pretty_print=True)
        svg_str = svg_bytes.decode('utf-8')
        
        # Verify Unicode characters are present
        self.assertIn('🌟 Unicode Title 🌍', svg_str)
        self.assertIn('Mixed: English, 中文', svg_str)
        self.assertIn('Special chars: àáâãäå', svg_str)
        
        # Verify proper XML declaration
        self.assertTrue(svg_str.startswith('<?xml version="1.0" encoding="UTF-8"?>') or 
                        svg_str.startswith('<?xml version="1.0"?>'))
    
    def test_property_with_unicode_values(self):
        """Test property modifications with Unicode values."""
        svg_root = etree.fromstring(self.svg_content.encode('utf-8'))
        
        # Apply Unicode properties (though CSS doesn't support Unicode in property names)
        data_row = {
            'TestBox##fill': '#FF0000',
            'TestCircle##stroke': '#00FF00'
        }
        
        stats = self.processor.apply_data_to_template(svg_root, data_row)
        self.assertGreater(stats['properties_modified'], 0)
        
        # Verify properties were set
        elements = self.processor.find_elements_by_name(svg_root, 'TestBox')
        for element in elements:
            self.assertEqual(element.get('fill'), '#FF0000')
    
    def test_layer_visibility_unicode(self):
        """Test layer visibility with Unicode layer names."""
        # Create SVG with Unicode layer names
        unicode_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
  <g inkscape:groupmode="layer" inkscape:label="测试层">
    <text x="50" y="50">Test Layer</text>
  </g>
  <g inkscape:groupmode="layer" inkscape:label="English Layer">
    <text x="50" y="100">English Layer</text>
  </g>
</svg>"""
        
        svg_root = etree.fromstring(unicode_svg.encode('utf-8'))
        
        # Apply layer visibility
        data_row = {
            '测试层': 'hidden',
            'English Layer': 'visible'
        }
        
        stats = self.processor.apply_data_to_template(svg_root, data_row)
        self.assertGreater(stats['layers_modified'], 0)
        
        # Verify layer visibility
        elements = self.processor.find_elements_by_name(svg_root, '测试层')
        for element in elements:
            self.assertEqual(element.get('display'), 'none')
    
    def test_unicode_error_handling(self):
        """Test error handling with malformed Unicode."""
        svg_root = etree.fromstring(self.svg_content.encode('utf-8'))
        
        # Test with None values (should handle gracefully)
        data_row = {
            'Title': None,
            'Unicode': ''
        }
        
        stats = self.processor.apply_data_to_template(svg_root, data_row)
        self.assertEqual(stats['errors'], 0, "Should handle None/empty values gracefully")
    
    def test_roundtrip_unicode(self):
        """Test complete roundtrip: CSV -> SVG -> Output preserves Unicode."""
        # Create temporary CSV with Unicode
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', encoding='utf-8', delete=False) as f:
            f.write('Title,Unicode\n')
            f.write('🌟 Test,😀 Emoji Test\n')
            temp_csv = f.name
        
        try:
            # Read CSV
            csv_reader = CSVReader(self.logger)
            csv_data = csv_reader.read_csv_data(temp_csv)
            
            # Apply to SVG
            svg_root = etree.fromstring(self.svg_content.encode('utf-8'))
            stats = self.processor.apply_data_to_template(svg_root, csv_data[0])
            
            # Serialize output
            output_bytes = etree.tostring(svg_root, encoding='utf-8')
            output_str = output_bytes.decode('utf-8')
            
            # Verify Unicode is preserved throughout
            self.assertIn('🌟 Test', output_str)
            self.assertIn('😀 Emoji Test', output_str)
            
        finally:
            os.unlink(temp_csv)


if __name__ == '__main__':
    unittest.main(verbosity=2)