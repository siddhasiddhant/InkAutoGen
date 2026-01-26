"""
Comprehensive test suite for SVG processing functionality.

Tests:
- Element finding by label and ID
- Text element replacement
- Shape property modifications
- Image replacement
- Layer visibility control
- SVG validation
- Error handling
"""

import unittest
import sys
import tempfile
import os
from pathlib import Path
import logging
from lxml import etree

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.svg_processor import SVGElementProcessor
from modules.csv_reader import CSVReader
from tests import TEST_DATA_DIR, TEST_OUTPUT_DIR


class TestSVGProcessing(unittest.TestCase):
    """Test SVG processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = logging.getLogger('test_svg')
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
    
    def test_find_elements_by_label(self):
        """Test finding elements by inkscape:label."""
        # Test finding various element types
        test_elements = [
            ('Title', 'text'),
            ('TestBox', 'rect'),
            ('BackgroundLayer', 'g'),
            ('TestImage', 'image')
        ]
        
        for element_name, expected_tag in test_elements:
            with self.subTest(element_name=element_name):
                elements = self.processor.find_elements_by_name(self.svg_root, element_name)
                
                self.assertTrue(elements, f"Element {element_name} should be found")
                self.assertGreater(len(elements), 0, f"At least one {element_name} element should exist")
                
                # Check element type
                found_tags = [elem.tag for elem in elements]
                self.assertIn(expected_tag, found_tags, 
                           f"Expected tag {expected_tag} for element {element_name}")
    
    def test_find_elements_by_id(self):
        """Test finding elements by ID when label not available."""
        # Create SVG with ID-based elements
        svg_with_ids = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <text id="title_text" x="10" y="10">Title</text>
  <rect id="box_rect" x="20" y="20" width="50" height="30"/>
  <g id="layer_group">
    <circle cx="40" cy="40" r="10"/>
  </g>
</svg>"""
        
        svg_root = etree.fromstring(svg_with_ids.encode('utf-8'))
        
        # Test finding by ID
        test_cases = [
            ('title_text', 'text'),
            ('box_rect', 'rect'),
            ('layer_group', 'g')
        ]
        
        for element_id, expected_tag in test_cases:
            with self.subTest(element_id=element_id):
                elements = self.processor.find_elements_by_name(svg_root, element_id)
                
                self.assertTrue(elements, f"Element with ID {element_id} should be found")
                self.assertEqual(elements[0].get('id'), element_id)
                self.assertEqual(elements[0].tag, expected_tag)
    
    def test_text_element_processing(self):
        """Test text element replacement."""
        svg_root = etree.fromstring(self.svg_content.encode('utf-8'))
        
        # Test text replacement
        data_row = {
            'Title': 'New Title Text',
            'Subtitle': 'New Subtitle'
        }
        
        stats = self.processor.apply_data_to_template(svg_root, data_row)
        
        self.assertGreater(stats['text_replaced'], 0)
        
        # Verify text was changed
        elements = self.processor.find_elements_by_name(svg_root, 'Title')
        for element in elements:
            self.assertEqual(element.text, 'New Title Text')
    
    def test_property_modifications(self):
        """Test SVG property modifications."""
        svg_root = etree.fromstring(self.svg_content.encode('utf-8'))
        
        # Test property changes
        data_row = {
            'TestBox##fill': '#FF0000',
            'TestCircle##stroke': '#00FF00',
            'Title##font-size': '20px'
        }
        
        stats = self.processor.apply_data_to_template(svg_root, data_row)
        
        self.assertGreater(stats['properties_modified'], 0)
        
        # Verify properties
        elements = self.processor.find_elements_by_name(svg_root, 'TestBox')
        for element in elements:
            self.assertEqual(element.get('fill'), '#FF0000')
        
        elements = self.processor.find_elements_by_name(svg_root, 'Title')
        for element in elements:
            self.assertEqual(element.get('font-size'), '20px')
    
    def test_layer_visibility_control(self):
        """Test layer visibility control."""
        svg_root = etree.fromstring(self.svg_content.encode('utf-8'))
        
        # Test layer visibility
        data_row = {
            'BackgroundLayer': 'visible',
            'ContentLayer': 'hidden',
            'HiddenLayer': 'visible'
        }
        
        stats = self.processor.apply_data_to_template(svg_root, data_row)
        
        self.assertGreater(stats['layers_modified'], 0)
        
        # Verify visibility changes
        background_elements = self.processor.find_elements_by_name(svg_root, 'BackgroundLayer')
        for element in background_elements:
            self.assertEqual(element.get('display'), 'inline')  # visible
        
        content_elements = self.processor.find_elements_by_name(svg_root, 'ContentLayer')
        for element in content_elements:
            self.assertEqual(element.get('display'), 'none')  # hidden
    
    def test_image_replacement(self):
        """Test image href replacement."""
        svg_root = etree.fromstring(self.svg_content.encode('utf-8'))
        
        # Test image replacement
        data_row = {
            'TestImage': 'new_test_image.png'
        }
        
        stats = self.processor.apply_data_to_template(svg_root, data_row)
        
        # Note: Image replacement requires file existence testing
        # This test mainly checks that the method doesn't crash
        self.assertIsInstance(stats, dict)
    
    def test_svg_validation(self):
        """Test SVG validation functionality."""
        # Test valid SVG
        is_valid, issues = self.processor.validate_svg(self.svg_root)
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)
        
        # Test invalid SVG (missing dimensions)
        invalid_svg = etree.fromstring('<svg><text>Test</text></svg>'.encode('utf-8'))
        is_valid, issues = self.processor.validate_svg(invalid_svg)
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
    
    def test_element_caching(self):
        """Test element lookup caching functionality."""
        # Clear cache first
        self.processor.clear_element_cache()
        
        # First lookup - should miss cache
        elements1 = self.processor.find_elements_by_name(self.svg_root, 'Title')
        
        # Second lookup - should hit cache
        elements2 = self.processor.find_elements_by_name(self.svg_root, 'Title')
        
        self.assertEqual(len(elements1), len(elements2))
        
        # Cache should contain results
        cache_key = f"{id(self.svg_root)}_Title"
        self.assertIn(cache_key, self.processor._element_cache)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        svg_root = etree.fromstring(self.svg_content.encode('utf-8'))
        
        # Test with non-existent element
        data_row = {
            'NonExistent': 'Test Value'
        }
        
        stats = self.processor.apply_data_to_template(svg_root, data_row)
        self.assertGreater(stats['errors'], 0)
        
        # Test with invalid property
        data_row = {
            'Title##invalid_property': 'value'
        }
        
        stats = self.processor.apply_data_to_template(svg_root, data_row)
        # Should handle gracefully without crashing
        self.assertIsInstance(stats, dict)
    
    def test_color_property_validation(self):
        """Test color property validation."""
        svg_root = etree.fromstring(self.svg_content.encode('utf-8'))
        
        # Test various color formats
        test_colors = [
            ('#FF0000', '#FF0000'),  # Hex
            ('red', '#FF0000'),         # Color name
            ('rgb(255,0,0)', '#FF0000'),  # RGB (if supported)
        ]
        
        for input_color, expected_output in test_colors:
            with self.subTest(color=input_color):
                data_row = {'TestBox##fill': input_color}
                stats = self.processor.apply_data_to_template(svg_root, data_row)
                
                elements = self.processor.find_elements_by_name(svg_root, 'TestBox')
                for element in elements:
                    actual_color = element.get('fill')
                    self.assertEqual(actual_color, expected_output,
                                   f"Color {input_color} not properly converted")


class TestCSVProcessingWithSVG(unittest.TestCase):
    """Test CSV processing with SVG integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = logging.getLogger('test_csv_svg')
        self.logger.setLevel(logging.DEBUG)
        
        self.processor = SVGElementProcessor(logger=self.logger)
        self.csv_reader = CSVReader(self.logger)
    
    def test_csv_classification_with_svg_validation(self):
        """Test CSV classification validates against SVG elements."""
        # Load test SVG
        template_path = TEST_DATA_DIR / "test_template.svg"
        with open(template_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        svg_root = etree.fromstring(svg_content.encode('utf-8'))
        
        # Test CSV data with valid and invalid elements
        csv_data = [
            {
                'Title': 'Valid Title',
                'Subtitle': 'Valid Subtitle', 
                'NonExistent': 'Invalid Element',
                'TestBox##fill': '#FF0000',
                'InvalidElement##stroke': '#00FF00'
            }
        ]
        
        # Classify with SVG validation
        classification = self.csv_reader.classify_csv_data(csv_data, svg_root)
        
        # Check classification results
        self.assertIn('Title', classification['elements'])
        self.assertIn('Subtitle', classification['elements'])
        self.assertIn('NonExistent', classification['missing_elements'])
        self.assertIn('TestBox##fill', classification['properties'])
        
        # Verify missing elements are identified
        self.assertGreater(len(classification['missing_elements']), 0)
    
    def test_missing_elements_filtering(self):
        """Test filtering of missing elements from CSV data."""
        # Create test data with missing elements
        original_data = [
            {'Title': 'Valid', 'NonExistent': 'Invalid'},
            {'Subtitle': 'Also Valid', 'AnotherMissing': 'Also Invalid'}
        ]
        
        missing_elements = ['NonExistent', 'AnotherMissing']
        
        # Filter data
        filtered_data, removed_data = self.csv_reader.filter_csv_data_by_missing_elements(
            original_data, missing_elements
        )
        
        # Verify filtering worked
        self.assertEqual(len(filtered_data), len(original_data))
        
        for row in filtered_data:
            self.assertNotIn('NonExistent', row)
            self.assertNotIn('AnotherMissing', row)
            self.assertIn('Title', row)  # Valid element should remain


if __name__ == '__main__':
    unittest.main(verbosity=2)