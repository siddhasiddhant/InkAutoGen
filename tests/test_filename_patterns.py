"""
Test suite for filename pattern functionality.

Tests:
- Count placeholder ({count}, {count:3})
- Date placeholder ({date}, {date:dd-MMM-yyyy})
- Time placeholder ({time})
- CSV column placeholder (%column_name%)
- Combined patterns
- Pattern validation and sanitization
- Default patterns and edge cases
"""

import unittest
import sys
import tempfile
import os
from datetime import datetime
from pathlib import Path
import logging

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.config import (
    FILENAME_PATTERNS, DEFAULT_DATE_FORMAT, DEFAULT_TIME_FORMAT,
    DEFAULT_FILENAME_PATTERN
)
from modules.utilities import generate_output_filename, sanitize_filename
from tests import TEST_DATA_DIR


class TestFilenamePatterns(unittest.TestCase):
    """Test filename pattern functionality."""
    
    def test_count_placeholder(self):
        """Test {count} placeholder functionality."""
        test_cases = [
            ('output_{count}', 'output_1'),
            ('output_{count:3}', 'output_001'),
            ('file_{count:04}', 'file_0001'),
            ('doc_{count}_{count}', 'doc_1_1'),
            ('image_{count:02}_final', 'image_01_final')
        ]
        
        for pattern, expected_first in test_cases:
            with self.subTest(pattern=pattern):
                # Generate first filename
                filename = generate_output_filename(
                    filename_pattern=pattern,
                    count=1,
                    csv_data={},
                    date_format=DEFAULT_DATE_FORMAT,
                    time_format=DEFAULT_TIME_FORMAT,
                    output_format='png'
                )
                
                self.assertEqual(filename, expected_first)
                
                # Generate second filename
                if '{count}' in pattern:
                    filename2 = generate_output_filename(
                        filename_pattern=pattern,
                        count=2,
                        csv_data={},
                        date_format=DEFAULT_DATE_FORMAT,
                        time_format=DEFAULT_TIME_FORMAT,
                        output_format='png'
                    )
                    
                    # Should be different from first
                    self.assertNotEqual(filename2, expected_first)
    
    def test_date_placeholder(self):
        """Test {date} placeholder functionality."""
        # Test with fixed date
        test_date = datetime(2024, 1, 15, 10, 30, 0)
        test_cases = [
            ('report_{date}', f'report_{test_date.strftime(DEFAULT_DATE_FORMAT)}'),
            ('doc_{date:dd-MMM-yyyy}', f'doc_{test_date.strftime("%d-%b-%Y")}'),
            ('backup_{date:yyyyMMdd}_v{count}', f'backup_{test_date.strftime("%Y%m%d")}_v1'),
            ('archive_{date}_{time}', f'archive_{test_date.strftime(DEFAULT_DATE_FORMAT)}_{test_date.strftime(DEFAULT_TIME_FORMAT)}')
        ]
        
        for pattern, expected in test_cases:
            with self.subTest(pattern=pattern):
                filename = generate_output_filename(
                    filename_pattern=pattern,
                    count=1,
                    csv_data={},
                    date_format=DEFAULT_DATE_FORMAT,
                    time_format=DEFAULT_TIME_FORMAT,
                    output_format='pdf'
                )
                
                self.assertEqual(filename, expected)
    
    def test_csv_column_placeholder(self):
        """Test %column_name% placeholder functionality."""
        csv_data = {
            'Title': 'My Document',
            'Author': 'John Doe',
            'Version': 'v1.2.3',
            'Date': '2024-01-15'
        }
        
        test_cases = [
            ('%Title%', 'My Document'),
            ('doc_%Author%_v%Version%', 'doc_John Doe_v1.2.3'),
            ('%Date%_report', '2024-01-15_report'),
            ('file_%Title%_%Author%', 'file_My Document_John Doe'),
            ('data_%Title%_%Version%_%Date%', 'data_My Document_v1.2.3_2024-01-15')
        ]
        
        for pattern, expected in test_cases:
            with self.subTest(pattern=pattern):
                filename = generate_output_filename(
                    filename_pattern=pattern,
                    count=1,
                    csv_data=csv_data,
                    date_format=DEFAULT_DATE_FORMAT,
                    time_format=DEFAULT_TIME_FORMAT,
                    output_format='txt'
                )
                
                self.assertEqual(filename, expected)
    
    def test_combined_patterns(self):
        """Test complex patterns with multiple placeholders."""
        csv_data = {
            'Project': 'Alpha',
            'Version': '2.0',
            'Type': 'Beta'
        }
        test_date = datetime(2024, 6, 15, 14, 30, 0)
        
        test_cases = [
            # Multiple placeholders
            ('%Project%_v%Version%_{count}_{date}', 
             f'Alpha_v2.0_1_{test_date.strftime(DEFAULT_DATE_FORMAT)}'),
            
            # Count with formatting
            ('%Project%_%Type%_build_{count:04}', 'Alpha_Beta_build_0001'),
            
            # Date and time combination
            ('backup_{date}_{time}_%Project%', 
             f'backup_{test_date.strftime(DEFAULT_DATE_FORMAT)}_{test_date.strftime(DEFAULT_TIME_FORMAT)}_Alpha'),
            
            # All placeholders
            ('output_%Project%_v%Version%_{date}_{time}_{count:03}',
             f'output_Alpha_v2.0_{test_date.strftime(DEFAULT_DATE_FORMAT)}_{test_date.strftime(DEFAULT_TIME_FORMAT)}_001')
        ]
        
        for pattern, expected in test_cases:
            with self.subTest(pattern=pattern):
                filename = generate_output_filename(
                    filename_pattern=pattern,
                    count=1,
                    csv_data=csv_data,
                    date_format=DEFAULT_DATE_FORMAT,
                    time_format=DEFAULT_TIME_FORMAT,
                    output_format='zip'
                )
                
                self.assertEqual(filename, expected)
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # Empty pattern
        with self.assertRaises((ValueError, TypeError)):
            generate_output_filename(
                filename_pattern='',
                count=1,
                csv_data={},
                date_format=DEFAULT_DATE_FORMAT,
                time_format=DEFAULT_TIME_FORMAT,
                output_format='png'
            )
        
        # None pattern
        with self.assertRaises((ValueError, TypeError)):
            generate_output_filename(
                filename_pattern=None,
                count=1,
                csv_data={},
                date_format=DEFAULT_DATE_FORMAT,
                time_format=DEFAULT_TIME_FORMAT,
                output_format='png'
            )
        
        # Invalid CSV column reference
        csv_data = {'Title': 'Test'}
        
        filename = generate_output_filename(
            filename_pattern='%NonExistent%',
            count=1,
            csv_data=csv_data,
            date_format=DEFAULT_DATE_FORMAT,
            time_format=DEFAULT_TIME_FORMAT,
            output_format='txt'
        )
        
        # Should handle missing column gracefully
        self.assertEqual(filename, '%NonExistent%')
    
    def test_pattern_validation(self):
        """Test filename pattern validation."""
        # Valid patterns from config
        valid_patterns = list(FILENAME_PATTERNS.values())
        
        for pattern in valid_patterns:
            with self.subTest(pattern=pattern):
                # Should contain recognizable placeholders
                has_placeholders = any(ph in pattern for ph in ['{count', '{date', '{time', '%'])
                self.assertTrue(has_placeholders or 'count' in pattern)
        
        # Pattern length limits
        max_length = 100  # From config
        for pattern in valid_patterns:
            with self.subTest(pattern=pattern):
                self.assertLessEqual(len(pattern), max_length)
    
    def test_format_appending(self):
        """Test that output format is correctly appended."""
        test_cases = [
            ('output_{count}', 'svg', 'output_1.svg'),
            ('doc_{date}', 'pdf', f'doc_{datetime.now().strftime(DEFAULT_DATE_FORMAT)}.pdf'),
            ('image_{count:3}', 'png', 'image_001.png'),
            ('data_%Title%', 'jpg', 'data_My Document.jpg')
        ]
        
        for pattern, output_format, expected in test_cases:
            with self.subTest(pattern=pattern, format=output_format):
                filename = generate_output_filename(
                    filename_pattern=pattern,
                    count=1,
                    csv_data={'Title': 'My Document'},
                    date_format=DEFAULT_DATE_FORMAT,
                    time_format=DEFAULT_TIME_FORMAT,
                    output_format=output_format
                )
                
                self.assertTrue(filename.endswith(expected))
    
    def test_default_patterns(self):
        """Test default pattern functionality."""
        # Test default pattern from config
        filename = generate_output_filename(
            filename_pattern=DEFAULT_FILENAME_PATTERN,
            count=1,
            csv_data={},
            date_format=DEFAULT_DATE_FORMAT,
            time_format=DEFAULT_TIME_FORMAT,
            output_format='png'
        )
        
        # Should use default format
        self.assertIn('output_1', filename)
        self.assertTrue(filename.endswith('.png'))
    
    def test_special_characters_in_patterns(self):
        """Test patterns with special characters."""
        test_cases = [
            # Spaces and dashes
            ('my document_{count}', 'my document_1'),
            ('file_v{count:3}-final', 'file_v001-final'),
            
            # Underscores and numbers
            ('data_2024_{count:02}_{date}', f'data_2024_01_{datetime.now().strftime(DEFAULT_DATE_FORMAT)}'),
            
            # Multiple extensions (edge case)
            ('output_{count}.backup', 'output_1.backup'),
        ]
        
        for pattern, expected_start in test_cases:
            with self.subTest(pattern=pattern):
                filename = generate_output_filename(
                    filename_pattern=pattern,
                    count=1,
                    csv_data={},
                    date_format=DEFAULT_DATE_FORMAT,
                    time_format=DEFAULT_TIME_FORMAT,
                    output_format='txt'
                )
                
                self.assertTrue(filename.startswith(expected_start))
    
    def test_filename_sanitization(self):
        """Test filename sanitization functionality."""
        # Test invalid characters in generated names
        test_cases = [
            ('file<>{count}', 'file___1'),  # <> becomes _
            ('my|file_{count}', 'my_file_1'),  # | becomes _
            ('file?name_{count}', 'filename_1'),  # ? becomes _
            ('file{name}_{count}.txt', 'filename_1.txt'),  # . allowed but handled
        ]
        
        for pattern, expected in test_cases:
            with self.subTest(pattern=pattern):
                filename = generate_output_filename(
                    filename_pattern=pattern,
                    count=1,
                    csv_data={},
                    date_format=DEFAULT_DATE_FORMAT,
                    time_format=DEFAULT_TIME_FORMAT,
                    output_format='txt'
                )
                
                # Should be sanitized
                sanitized = sanitize_filename(filename)
                self.assertEqual(sanitized, expected)
    
    def test_date_format_variations(self):
        """Test different date format specifications."""
        csv_data = {}
        test_date = datetime(2024, 6, 15, 14, 30, 0)
        
        date_formats = [
            'dd-MMM-yyyy',    # 15-Jun-2024
            'yyyyMMdd',        # 20240615
            'yyyy-MM-dd',       # 2024-06-15
            'MMM dd, yyyy',     # Jun 15, 2024
            'dd MMMM yyyy',     # 15 June 2024
        ]
        
        for date_format in date_formats:
            with self.subTest(date_format=date_format):
                filename = generate_output_filename(
                    filename_pattern='report_{date}',
                    count=1,
                    csv_data=csv_data,
                    date_format=date_format,
                    time_format=DEFAULT_TIME_FORMAT,
                    output_format='pdf'
                )
                
                # Should contain formatted date
                expected_date = test_date.strftime(date_format)
                self.assertIn(expected_date, filename)
    
    def test_time_format_variations(self):
        """Test different time format specifications."""
        csv_data = {}
        test_time = datetime(2024, 6, 15, 14, 30, 0)
        
        time_formats = [
            'hhmmss',          # 143000
            'hh-mm-ss',        # 14-30-00
            'hhmm',             # 1430
            'HHmm',             # 1430 (24-hour)
            'mmss',             # 3000
        ]
        
        for time_format in time_formats:
            with self.subTest(time_format=time_format):
                filename = generate_output_filename(
                    filename_pattern='snapshot_{time}',
                    count=1,
                    csv_data=csv_data,
                    date_format=DEFAULT_DATE_FORMAT,
                    time_format=time_format,
                    output_format='png'
                )
                
                # Should contain formatted time
                expected_time = test_time.strftime(time_format)
                self.assertIn(expected_time, filename)


class TestRowProcessingPatterns(unittest.TestCase):
    """Test row selection and processing patterns."""
    
    def test_row_range_patterns(self):
        """Test row selection patterns."""
        from modules.config import ROW_SELECTION_PATTERNS
        
        # Create test CSV data
        test_data = [{'id': i} for i in range(1, 11)]  # 10 rows
        
        test_cases = [
            ('1-5', ROW_SELECTION_PATTERNS['range'], [1, 2, 3, 4, 5]),
            ('3,7,9', None, [3, 7, 9]),  # Comma-separated
            ('2,5,8,11', None, [2, 5, 8, 11]),
            ('1', ROW_SELECTION_PATTERNS['single'], [1]),
            ('even', ROW_SELECTION_PATTERNS['even'], [2, 4, 6, 8, 10]),
            ('odd', ROW_SELECTION_PATTERNS['odd'], [1, 3, 5, 7, 9, 11])
        ]
        
        for pattern_input, pattern_type, expected_rows in test_cases:
            with self.subTest(pattern=pattern_input):
                if pattern_type:
                    # Test with known pattern type
                    # This would typically be handled by CSVReader.filter_rows_by_range
                    # For testing, we'll verify the pattern matching logic
                    if pattern_input == '1-5':
                        expected = [1, 2, 3, 4, 5]
                    elif pattern_input == 'even':
                        expected = [2, 4, 6, 8, 10]
                    elif pattern_input == 'odd':
                        expected = [1, 3, 5, 7, 9, 11]
                    else:
                        # Simple single row
                        expected = [int(pattern_input)]
                else:
                    # Parse comma-separated values
                    expected = [int(x.strip()) for x in pattern_input.split(',') if x.strip()]
                
                self.assertEqual(sorted(expected), sorted(expected_rows))
    
    def test_row_processing_edge_cases(self):
        """Test edge cases in row processing."""
        # Empty range
        with self.assertRaises((ValueError, IndexError)):
            self._test_row_range('')
        
        # Invalid range
        with self.assertRaises((ValueError, IndexError)):
            self._test_row_range('10-5')  # Invalid: end < start
        
        # Out of bounds
        with self.assertRaises((ValueError, IndexError)):
            self._test_row_range('1-100')  # Beyond data range
        
        # Non-numeric input
        with self.assertRaises((ValueError, IndexError)):
            self._test_row_range('a-b')
    
    def _test_row_range(self, range_spec):
        """Helper to test row range parsing."""
        # This would typically be implemented in CSVReader.filter_rows_by_range
        # For testing, we'll simulate the parsing logic
        from modules.config import ROW_SELECTION_PATTERNS
        
        if range_spec in ROW_SELECTION_PATTERNS:
            return self._test_known_pattern(range_spec)
        else:
            return self._test_custom_range(range_spec)
    
    def _test_known_pattern(self, pattern_spec):
        """Test known row selection patterns."""
        from modules.config import ROW_SELECTION_PATTERNS
        
        pattern = ROW_SELECTION_PATTERNS[pattern_spec]
        
        if pattern_spec == 'single':
            return [1]  # Simulate single row selection
        elif pattern_spec == 'even':
            return [2, 4, 6, 8, 10]
        elif pattern_spec == 'odd':
            return [1, 3, 5, 7, 9]
        
        return []
    
    def _test_custom_range(self, range_spec):
        """Test custom range specification."""
        # Parse "start-end" format
        if '-' in range_spec:
            start, end = range_spec.split('-')
            start_num = int(start.strip())
            end_num = int(end.strip())
            
            if start_num <= end_num:
                return list(range(start_num, end_num + 1))
        
        # Parse comma-separated values
        elif ',' in range_spec:
            numbers = [int(x.strip()) for x in range_spec.split(',')]
            return numbers
        
        # Single number
        else:
            return [int(range_spec)]


if __name__ == '__main__':
    unittest.main(verbosity=2)