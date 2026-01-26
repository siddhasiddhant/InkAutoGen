#!/usr/bin/env python3
"""
Simple integration test to verify optimized code works.
"""

import sys
from pathlib import Path
from lxml import etree

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_functionality():
    """Test that basic functionality works after optimization."""
    print("🧪 Testing Basic Functionality After Optimization")
    print("=" * 50)
    
    # Test 1: Config constants are accessible
    try:
        from modules.config import (
            SECURITY_INDICATORS, STYLE_PROPERTIES, SHAPE_TYPES,
            PROPERTIES_TO_CHECK, COMMON_XPATH_EXPRESSIONS
        )
        print("✅ Config constants are accessible")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    # Test 2: CSV reader still works
    try:
        from modules.csv_reader import CSVReader
        import logging
        
        logger = logging.getLogger(__name__)
        reader = CSVReader(logger)
        print("✅ CSVReader can be instantiated")
    except Exception as e:
        print(f"❌ CSVReader failed: {e}")
        return False
    
    # Test 3: File exporter still works
    try:
        from modules.file_exporter import FileExporter
        exporter = FileExporter(logger)
        print("✅ FileExporter can be instantiated")
    except Exception as e:
        print(f"❌ FileExporter failed: {e}")
        return False
    
    # Test 4: Common utils are available
    try:
        from modules.utilities import (
            xpath_query, get_element_attributes, validate_required_value
        )
        print("✅ Common utils are accessible")
    except Exception as e:
        print(f"❌ Common utils failed: {e}")
        return False
    
    # Test 5: Basic SVG element operation
    try:
        from modules.utilities import get_element_attributes
        from lxml import etree
        
        # Create simple SVG
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <svg xmlns="http://www.w3.org/2000/svg" 
             xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
            <rect id="test-rect" inkscape:label="TestBox" x="10" y="10" width="100" height="50" style="fill:red"/>
        </svg>'''
        svg_root = etree.fromstring(svg_content.encode())
        
        # Test element attribute extraction
        attrs = get_element_attributes(svg_root[0])
        assert attrs['tag'] == 'rect'
        assert attrs['id'] == 'test-rect'
        print("✅ SVG element operations work")
    except Exception as e:
        print(f"❌ SVG operations failed: {e}")
        return False
    
    # Test 6: Security validation
    try:
        from modules.security import FileValidator
        
        # Test file validation (should not crash)
        result = FileValidator.validate_file_basics("nonexistent.png", {".png"})
        assert result['valid'] == False
        assert 'File not found' in result['errors'][0]
        print("✅ Security validation works")
    except Exception as e:
        print(f"❌ Security validation failed: {e}")
        return False
    
    # Test 7: Basic utilities work
    try:
        from modules.utilities import generate_output_filename, find_file
        
        # Test filename generation
        filename = generate_output_filename("test_{count}", 0, {})
        assert filename == "test_1"
        print("✅ Basic utilities work")
    except Exception as e:
        print(f"❌ Basic utilities failed: {e}")
        return False
    
    return True


def test_removed_code():
    """Test that removed code is actually gone."""
    print("\n🗑️ Testing Removed Code")
    print("-" * 20)
    
    # Test that removed modules can't be imported
    try:
        import modules.utilities_minimal
        print("❌ utilities_minimal still exists (should be removed)")
        return False
    except ImportError:
        print("✅ utilities_minimal properly removed")
    
    # Test that removed classes can't be imported
    try:
        from modules.performance import BatchProcessor
        print("❌ BatchProcessor still exists (should be removed)")
        return False
    except (ImportError, AttributeError):
        print("✅ BatchProcessor properly removed")
    
    return True


def test_config_consolidation():
    """Test that configuration is properly consolidated."""
    print("\n⚙️ Testing Configuration Consolidation")
    print("-" * 20)
    
    try:
        from modules.config import (
            SECURITY_INDICATORS, STYLE_PROPERTIES, ENCODING_MAP,
            PRIORITY_ENCODINGS, SHAPE_TYPES, PROPERTIES_TO_CHECK
        )
        
        # Test that all expected constants exist
        assert isinstance(SECURITY_INDICATORS, list)
        assert isinstance(STYLE_PROPERTIES, set)
        assert isinstance(ENCODING_MAP, dict)
        assert isinstance(PRIORITY_ENCODINGS, list)
        assert isinstance(SHAPE_TYPES, list)
        assert isinstance(PROPERTIES_TO_CHECK, list)
        
        print("✅ All configuration constants available")
        
        # Test some specific values
        assert 'path traversal' in SECURITY_INDICATORS
        assert 'fill' in STYLE_PROPERTIES
        assert 'rect' in SHAPE_TYPES
        assert 'fill' in PROPERTIES_TO_CHECK
        
        print("✅ Configuration values look correct")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    return True


def main():
    """Run all integration tests."""
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Removed Code", test_removed_code),
        ("Config Consolidation", test_config_consolidation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name}: FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed! Code optimization successful.")
        return True
    else:
        print("⚠️ Some integration tests failed. Review issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)