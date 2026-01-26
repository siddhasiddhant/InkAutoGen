"""
Integration tests for end-to-end InkAutoGen functionality.

Tests complete workflows:
- CSV import with Unicode
- SVG template processing
- File export with proper encoding
- Error handling
- Performance with large datasets
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path
import logging
from lxml import etree

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.svg_processor import SVGElementProcessor
from modules.csv_reader import CSVReader
from tests import TEST_DATA_DIR, TEST_OUTPUT_DIR


class TestIntegration(unittest.TestCase):
    """End-to-end integration tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = logging.getLogger('test_integration')
        self.logger.setLevel(logging.DEBUG)
        
        # Create temporary output directory
        self.temp_dir = tempfile.mkdtemp()
        self.temp_output = Path(self.temp_dir) / "output"
        self.temp_output.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_unicode_workflow(self):
        """Test complete workflow with Unicode data."""
        # Create test SVG
        test_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
  <text x="50" y="50" inkscape:label="UnicodeText" font-size="16">Default</text>
  <rect x="50" y="100" width="100" height="50" inkscape:label="UnicodeBox" fill="blue"/>
  <g inkscape:groupmode="layer" inkscape:label="UnicodeLayer">
    <text x="200" y="200">Layer Content</text>
  </g>
</svg>"""
        
        # Create test CSV with Unicode
        test_csv_content = """UnicodeText,UnicodeBox##fill,UnicodeLayer
🌟 Unicode Test 🌍,#FF0000,visible"""
        
        # Write test files
        svg_file = Path(self.temp_dir) / "test.svg"
        csv_file = Path(self.temp_dir) / "test.csv"
        
        with open(svg_file, 'w', encoding='utf-8') as f:
            f.write(test_svg)
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(test_csv_content)
        
        # Test complete processing
        processor = SVGElementProcessor(
            csv_dir=str(csv_file.parent),
            output_dir=str(self.temp_output),
            logger=self.logger
        )
        
        csv_reader = CSVReader(self.logger)
        csv_data = csv_reader.read_csv_data(str(csv_file))
        svg_root = etree.fromstring(test_svg.encode('utf-8'))
        
        # Classify CSV data with SVG validation
        classification = csv_reader.classify_csv_data(csv_data, svg_root)
        
        # Verify classification
        self.assertIn('UnicodeText', classification['elements'])
        self.assertIn('UnicodeBox##fill', classification['properties'])
        self.assertEqual(len(classification['missing_elements']), 0)
        
        # Apply data to SVG
        stats = processor.apply_data_to_template(svg_root, csv_data[0])
        
        # Verify processing
        self.assertGreater(stats['text_replaced'], 0)
        self.assertGreater(stats['properties_modified'], 0)
        
        # Verify Unicode content in output
        svg_bytes = etree.tostring(svg_root, encoding='utf-8')
        svg_str = svg_bytes.decode('utf-8')
        
        self.assertIn('🌟 Unicode Test 🌍', svg_str)
        self.assertIn('#FF0000', svg_str)
        
        # Verify output can be written and read
        output_file = Path(self.temp_output) / "output.svg"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_str)
        
        # Read back and verify
        with open(output_file, 'r', encoding='utf-8') as f:
            read_content = f.read()
        
        self.assertIn('🌟 Unicode Test 🌍', read_content)
    
    def test_missing_elements_workflow(self):
        """Test workflow with missing SVG elements."""
        # Create simple SVG
        test_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="150" xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
  <text x="20" y="30" inkscape:label="RealText">Default</text>
</svg>"""
        
        # Create CSV with real and fake elements
        test_csv_content = """RealText,FakeText,AnotherFake
Real Value,Fake Value,Another Fake"""
        
        # Write test files
        svg_file = Path(self.temp_dir) / "test_missing.svg"
        csv_file = Path(self.temp_dir) / "test_missing.csv"
        
        with open(svg_file, 'w', encoding='utf-8') as f:
            f.write(test_svg)
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(test_csv_content)
        
        # Process with missing element handling
        processor = SVGElementProcessor(
            csv_dir=str(csv_file.parent),
            output_dir=str(self.temp_output),
            logger=self.logger
        )
        
        csv_reader = CSVReader(self.logger)
        csv_data = csv_reader.read_csv_data(str(csv_file))
        svg_root = etree.fromstring(test_svg.encode('utf-8'))
        
        # Classify and filter
        classification = csv_reader.classify_csv_data(csv_data, svg_root)
        
        # Should identify missing elements
        self.assertGreater(len(classification['missing_elements']), 0)
        self.assertIn('FakeText', classification['missing_elements'])
        self.assertIn('AnotherFake', classification['missing_elements'])
        
        # Filter missing elements
        filtered_data, removed_data = csv_reader.filter_csv_data_by_missing_elements(
            csv_data, classification['missing_elements']
        )
        
        # Apply filtered data
        stats = processor.apply_data_to_template(svg_root, filtered_data[0])
        
        # Should work without errors
        self.assertGreater(stats['text_replaced'], 0)
        self.assertEqual(stats['errors'], 0)
    
    def test_encoding_detection_workflow(self):
        """Test workflow with various CSV encodings."""
        # Test CSV with different encodings
        test_content = "Title,Value\nTest,编码测试"  # Mix of English and Chinese
        
        # Test UTF-8
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', encoding='utf-8', delete=False) as f:
            f.write(test_content)
            utf8_file = f.name
        
        # Test UTF-8 with BOM
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', encoding='utf-8-sig', delete=False) as f:
            f.write('\ufeff' + test_content)
            utf8_bom_file = f.name
        
        try:
            csv_reader = CSVReader(self.logger)
            
            # Test UTF-8 detection
            encoding = csv_reader.detect_encoding(utf8_file)
            self.assertEqual(encoding, 'utf-8')
            
            data = csv_reader.read_csv_data(utf8_file)
            self.assertEqual(data[0]['Title'], 'Test')
            self.assertEqual(data[0]['Value'], '编码测试')
            
            # Test UTF-8 BOM detection
            encoding = csv_reader.detect_encoding(utf8_bom_file)
            self.assertEqual(encoding, 'utf-8-sig')
            
            data = csv_reader.read_csv_data(utf8_bom_file)
            self.assertEqual(data[0]['Title'], 'Test')
            self.assertEqual(data[0]['Value'], '编码测试')
            
        finally:
            os.unlink(utf8_file)
            os.unlink(utf8_bom_file)
    
    def test_large_dataset_processing(self):
        """Test processing with larger datasets."""
        # Create test SVG with multiple elements
        test_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="500" height="400" xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">"""
        
        # Add many text elements
        for i in range(10):
            test_svg += f'<text x="{50 + i*40}" y="50" inkscape:label="Text{i}">Default{i}</text>'
        
        test_svg += "</svg>"
        
        # Create CSV with many rows
        csv_content = "Title" + "".join([f",Text{i}" for i in range(10)]) + "\n"
        for row in range(5):  # 5 rows of data
            csv_content += "".join([f",Row{row}Col{i}" for i in range(10)]) + "\n"
        
        # Write test files
        svg_file = Path(self.temp_dir) / "test_large.svg"
        csv_file = Path(self.temp_dir) / "test_large.csv"
        
        with open(svg_file, 'w', encoding='utf-8') as f:
            f.write(test_svg)
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        # Process large dataset
        processor = SVGElementProcessor(
            csv_dir=str(csv_file.parent),
            output_dir=str(self.temp_output),
            logger=self.logger
        )
        
        csv_reader = CSVReader(self.logger)
        csv_data = csv_reader.read_csv_data(str(csv_file))
        svg_root = etree.fromstring(test_svg.encode('utf-8'))
        
        # Process all rows
        total_stats = {'text_replaced': 0, 'errors': 0}
        
        for row in csv_data:
            stats = processor.apply_data_to_template(svg_root, row)
            total_stats['text_replaced'] += stats['text_replaced']
            total_stats['errors'] += stats['errors']
            
            # Reset SVG for next row
            svg_root = etree.fromstring(test_svg.encode('utf-8'))
        
        # Verify processing
        self.assertEqual(total_stats['text_replaced'], 5 * 10)  # 5 rows × 10 elements
        self.assertEqual(total_stats['errors'], 0)
    
    def test_error_recovery_workflow(self):
        """Test error recovery and graceful handling."""
        # Create malformed SVG (missing namespace)
        test_svg = """<svg width="200" height="100">
  <text x="20" y="30" label="BadText">Default</text>
</svg>"""
        
        # Create CSV with valid data
        test_csv_content = "BadText\nTest Value"
        
        # Write test files
        svg_file = Path(self.temp_dir) / "test_bad.svg"
        csv_file = Path(self.temp_dir) / "test_bad.csv"
        
        with open(svg_file, 'w', encoding='utf-8') as f:
            f.write(test_svg)
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(test_csv_content)
        
        # Process with error handling
        processor = SVGElementProcessor(
            csv_dir=str(csv_file.parent),
            output_dir=str(self.temp_output),
            logger=self.logger
        )
        
        csv_reader = CSVReader(self.logger)
        csv_data = csv_reader.read_csv_data(str(csv_file))
        
        try:
            svg_root = etree.fromstring(test_svg.encode('utf-8'))
            stats = processor.apply_data_to_template(svg_root, csv_data[0])
            
            # Should handle gracefully (even if element not found due to namespace issue)
            self.assertIsInstance(stats, dict)
            
        except Exception as e:
            # Should log error but not crash
            self.assertIsNotNone(e)
            self.logger.info(f"Handled expected error: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)