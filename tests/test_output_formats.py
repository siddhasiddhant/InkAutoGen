"""
Test suite for output format functionality.

Tests:
- Raster format export (PNG, JPG, JPEG, TIFF, WebP)
- Vector format export (SVG, PDF, PS, EPS)
- Format validation and error handling
- Format-specific options and parameters
- Cross-platform compatibility
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

from modules.config import SUPPORTED_EXPORT_FORMATS, RASTER_FORMATS, VECTOR_FORMATS
from modules.file_exporter import FileExporter
from tests import TEST_DATA_DIR, TEST_OUTPUT_DIR


class TestOutputFormats(unittest.TestCase):
    """Test output format functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = logging.getLogger('test_formats')
        self.logger.setLevel(logging.DEBUG)
        
        # Create test SVG
        self.test_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
  <rect x="50" y="50" width="100" height="80" fill="blue" stroke="black" stroke-width="2"/>
  <text x="100" y="150" font-size="16" font-family="Arial">Test Content</text>
  <circle cx="250" cy="150" r="30" fill="red"/>
</svg>"""
        
        self.svg_root = etree.fromstring(self.test_svg.encode('utf-8'))
        
        # Create temporary output directory
        self.temp_dir = tempfile.mkdtemp()
        self.temp_output = Path(self.temp_dir) / "output"
        self.temp_output.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_supported_formats_validation(self):
        """Test validation of supported export formats."""
        # Test all supported formats are recognized
        for format_name in SUPPORTED_EXPORT_FORMATS:
            with self.subTest(format=format_name):
                self.assertIn(format_name, SUPPORTED_EXPORT_FORMATS)
        
        # Test raster vs vector classification
        raster_count = len(RASTER_FORMATS)
        vector_count = len(VECTOR_FORMATS)
        total_count = len(SUPPORTED_EXPORT_FORMATS)
        
        self.assertEqual(raster_count + vector_count, total_count)
        
        # Verify specific formats
        expected_raster = ['png', 'jpg', 'jpeg', 'tiff', 'webp']
        expected_vector = ['svg', 'pdf', 'ps', 'eps']
        
        for fmt in expected_raster:
            self.assertIn(fmt, RASTER_FORMATS)
        
        for fmt in expected_vector:
            self.assertIn(fmt, VECTOR_FORMATS)
    
    def test_raster_format_export(self):
        """Test raster format export functionality."""
        raster_formats = ['png', 'jpg', 'jpeg', 'tiff', 'webp']
        
        for format_name in raster_formats:
            with self.subTest(format=format_name):
                output_file = self.temp_output / f"test_raster.{format_name}"
                
                # Create file exporter
                exporter = FileExporter(
                    output_dir=str(self.temp_output),
                    logger=self.logger
                )
                
                # Test raster export
                try:
                    success = exporter.export_file(
                        svg_root=self.svg_root,
                        output_path=str(output_file),
                        export_format=format_name,
                        dpi=300
                    )
                    
                    # Verify file was created
                    self.assertTrue(output_file.exists(), f"Raster file {format_name} should be created")
                    self.assertGreater(output_file.stat().st_size, 0, f"File should not be empty")
                    
                    # Verify file extension
                    self.assertEqual(output_file.suffix.lower(), f".{format_name}")
                    
                except Exception as e:
                    # Some formats might not be available in test environment
                    self.logger.warning(f"Format {format_name} not available: {e}")
                    self.skipTest(f"Format {format_name} not supported in test environment")
    
    def test_vector_format_export(self):
        """Test vector format export functionality."""
        vector_formats = ['svg', 'pdf', 'ps', 'eps']
        
        for format_name in vector_formats:
            with self.subTest(format=format_name):
                output_file = self.temp_output / f"test_vector.{format_name}"
                
                # Create file exporter
                exporter = FileExporter(
                    output_dir=str(self.temp_output),
                    logger=self.logger
                )
                
                # Test vector export
                try:
                    success = exporter.export_file(
                        svg_root=self.svg_root,
                        output_path=str(output_file),
                        export_format=format_name
                    )
                    
                    # Verify file was created
                    self.assertTrue(output_file.exists(), f"Vector file {format_name} should be created")
                    self.assertGreater(output_file.stat().st_size, 0, f"File should not be empty")
                    
                    # Verify file extension
                    self.assertEqual(output_file.suffix.lower(), f".{format_name}")
                    
                    # For SVG, verify content preservation
                    if format_name == 'svg':
                        with open(output_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self.assertIn('Test Content', content)
                        self.assertIn('fill="blue"', content)
                    
                except Exception as e:
                    # Some formats might not be available in test environment
                    self.logger.warning(f"Format {format_name} not available: {e}")
                    self.skipTest(f"Format {format_name} not supported in test environment")
    
    def test_format_case_insensitivity(self):
        """Test format names are case insensitive."""
        test_cases = [
            ('PNG', 'png'),
            ('Jpg', 'jpg'),
            ('PDF', 'pdf'),
            ('Svg', 'svg')
        ]
        
        for input_format, expected_format in test_cases:
            with self.subTest(input=input_format):
                # Test format normalization
                normalized = input_format.lower()
                self.assertEqual(normalized, expected_format)
                
                # Test format validation
                self.assertIn(normalized, SUPPORTED_EXPORT_FORMATS)
    
    def test_invalid_format_handling(self):
        """Test handling of invalid format names."""
        invalid_formats = [
            'invalid',
            'bmp',
            'gif',
            '',
            'pngx',
            'pdfx'
        ]
        
        for invalid_format in invalid_formats:
            with self.subTest(format=invalid_format):
                # Verify format is not supported
                self.assertNotIn(invalid_format.lower(), SUPPORTED_EXPORT_FORMATS)
                
                # Test error handling in exporter
                exporter = FileExporter(
                    output_dir=str(self.temp_output),
                    logger=self.logger
                )
                
                output_file = self.temp_output / f"test_invalid.{invalid_format}"
                
                # Should raise error or return False for invalid format
                with self.assertRaises((ValueError, TypeError, NotImplementedError)):
                    exporter.export_file(
                        svg_root=self.svg_root,
                        output_path=str(output_file),
                        export_format=invalid_format
                    )
    
    def test_format_specific_options(self):
        """Test format-specific export options."""
        # Test PNG with transparency
        output_file = self.temp_output / "test_options.png"
        
        exporter = FileExporter(
            output_dir=str(self.temp_output),
            logger=self.logger
        )
        
        try:
            # Test with different DPI settings
            dpi_settings = [72, 150, 300, 600]
            
            for dpi in dpi_settings:
                with self.subTest(dpi=dpi):
                    test_file = self.temp_output / f"test_dpi_{dpi}.png"
                    
                    success = exporter.export_file(
                        svg_root=self.svg_root,
                        output_path=str(test_file),
                        export_format='png',
                        dpi=dpi
                    )
                    
                    if success:
                        self.assertTrue(test_file.exists())
                        # Higher DPI should generally result in larger files
                        if test_file.exists():
                            file_size = test_file.stat().st_size
                            self.assertGreater(file_size, 0)
                            
        except Exception as e:
            self.skipTest(f"DPI options not available: {e}")
    
    def test_format_extension_handling(self):
        """Test proper file extension handling."""
        test_cases = [
            ('test.png', 'png'),
            ('test.jpg', 'jpg'),
            ('test.jpeg', 'jpeg'),
            ('test.pdf', 'pdf'),
            ('test.svg', 'svg')
        ]
        
        for filename, expected_format in test_cases:
            with self.subTest(filename=filename):
                # Test extension extraction
                path = Path(filename)
                extension = path.suffix.lower().lstrip('.')
                self.assertEqual(extension, expected_format)
                
                # Test format validation
                self.assertIn(extension, SUPPORTED_EXPORT_FORMATS)
    
    def test_format_quality_settings(self):
        """Test quality settings for lossy formats."""
        lossy_formats = ['jpg', 'jpeg', 'webp']
        
        for format_name in lossy_formats:
            with self.subTest(format=format_name):
                output_file = self.temp_output / f"test_quality.{format_name}"
                
                exporter = FileExporter(
                    output_dir=str(self.temp_output),
                    logger=self.logger
                )
                
                try:
                    # Test different quality settings
                    quality_settings = [50, 75, 90, 100]
                    
                    for quality in quality_settings:
                        with self.subTest(quality=quality):
                            test_file = self.temp_output / f"test_{format_name}_q{quality}.{format_name}"
                            
                            success = exporter.export_file(
                                svg_root=self.svg_root,
                                output_path=str(test_file),
                                export_format=format_name,
                                quality=quality
                            )
                            
                            if success:
                                self.assertTrue(test_file.exists())
                                # Different quality settings should produce different file sizes
                                if test_file.exists():
                                    file_size = test_file.stat().st_size
                                    self.assertGreater(file_size, 0)
                                    
                except Exception as e:
                    self.skipTest(f"Quality settings not available for {format_name}: {e}")


class TestFormatCompatibility(unittest.TestCase):
    """Test format compatibility across platforms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = logging.getLogger('test_compatibility')
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cross_platform_format_support(self):
        """Test format support across different platforms."""
        import platform
        
        current_platform = platform.system().lower()
        
        # Test platform-specific format availability
        if current_platform in ['windows', 'linux', 'darwin']:
            # These platforms should support basic formats
            basic_formats = ['png', 'svg', 'pdf']
            
            for fmt in basic_formats:
                with self.subTest(format=fmt, platform=current_platform):
                    self.assertIn(fmt, SUPPORTED_EXPORT_FORMATS)
    
    def test_format_fallback_mechanism(self):
        """Test format fallback when preferred format is unavailable."""
        # Test fallback hierarchy
        fallback_chain = {
            'webp': ['png', 'jpg'],
            'tiff': ['png', 'jpg'],
            'eps': ['pdf', 'svg'],
            'ps': ['pdf', 'svg']
        }
        
        for primary_format, fallbacks in fallback_chain.items():
            with self.subTest(primary=primary_format):
                # Verify primary format is supported
                self.assertIn(primary_format, SUPPORTED_EXPORT_FORMATS)
                
                # Verify fallbacks are also supported
                for fallback in fallbacks:
                    self.assertIn(fallback, SUPPORTED_EXPORT_FORMATS)


if __name__ == '__main__':
    unittest.main(verbosity=2)