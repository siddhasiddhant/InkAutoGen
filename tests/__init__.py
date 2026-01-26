"""
Test Suite for InkAutoGen Extension

This package contains comprehensive test cases for all InkAutoGen functionality:
- CSV processing and encoding detection
- SVG template processing and element manipulation
- Unicode text handling
- Layer visibility management
- Property modifications
- Image replacement
- File export functionality

Test Structure:
- test_csv_reader.py: CSV processing tests
- test_svg_processor.py: SVG processing tests
- test_unicode_handling.py: Unicode text tests
- test_integration.py: End-to-end integration tests

Sample Data:
- sample_data/: Test input files (CSV, SVG templates)
- output/: Test output files (generated SVGs, exports)
"""

import sys
import os
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "sample_data"
TEST_OUTPUT_DIR = Path(__file__).parent / "output"

# Ensure test directories exist
TEST_DATA_DIR.mkdir(exist_ok=True)
TEST_OUTPUT_DIR.mkdir(exist_ok=True)

__version__ = "1.0.0"
__author__ = "InkAutoGen Development Team"