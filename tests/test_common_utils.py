#!/usr/bin/env python3
"""
Comprehensive test cases for common utility module.

Tests all utility functions to ensure they work correctly
after code optimization and refactoring.
"""

import sys
import os
import tempfile
from pathlib import Path
from lxml import etree
from unittest.mock import Mock, patch
import logging

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.utilities import (
    xpath_query, get_element_attributes, log_element_change,
    safe_execute, update_svg_style_property, validate_required_value,
    clean_string, validate_file_basics, safe_dict_get, logged_iterate
)
from modules.config import SVG_NAMESPACES, COMMON_XPATH_EXPRESSIONS


def test_xpath_query():
    """Test XPath query functionality."""
    print("Testing xpath_query...")
    
    # Create test SVG with proper namespaces
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <svg xmlns="http://www.w3.org/2000/svg" 
         xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
        <rect id="test-rect" inkscape:label="TestBox" x="10" y="10" width="100" height="50"/>
        <text inkscape:label="TestText">Hello World</text>
    </svg>'''
    svg_root = etree.fromstring(svg_content.encode())
    
    # Test labeled elements search
    elements = xpath_query(svg_root, "labeled_elements", name="TestBox")
    assert len(elements) == 1
    assert elements[0].get('inkscape:label') == "TestBox"
    print("  ✓ Labeled elements search works")
    
    # Test shape element search
    elements = xpath_query(svg_root, "shape_element_base", shape_type="rect")
    assert len(elements) == 1
    assert elements[0].tag.endswith('rect')
    print("  ✓ Shape element search works")
    
    # Test text element search
    elements = xpath_query(svg_root, "text_element_svg")
    assert len(elements) == 1
    print("  ✓ Text element search works")


def test_get_element_attributes():
    """Test element attribute extraction."""
    print("Testing get_element_attributes...")
    
    # Create test element
    svg_content = '''
    <rect id="test-id" inkscape:label="test-label" x="10" y="10">Test Content</rect>
    '''
    element = etree.fromstring(svg_content.encode())
    
    attrs = get_element_attributes(element)
    
    assert attrs['id'] == 'test-id'
    assert attrs['label'] == 'test-label'
    assert attrs['tag'] == 'rect'
    assert attrs['text'] == 'Test Content'
    print("  ✓ Element attribute extraction works")
    
    # Test with missing attributes
    svg_content_missing = '<rect/>'
    element_missing = etree.fromstring(svg_content_missing.encode())
    
    attrs_missing = get_element_attributes(element_missing)
    assert attrs_missing['id'] == 'no-id'
    assert attrs_missing['label'] == 'no-label'
    print("  ✓ Missing attribute handling works")


def test_log_element_change():
    """Test logging functionality."""
    print("Testing log_element_change...")
    
    # Create mock logger
    mock_logger = Mock()
    
    # Test with all parameters
    log_element_change(mock_logger, "fill color", "MyBox", 
                   current="red", new="blue", level="debug")
    
    mock_logger.debug.assert_called_once()
    call_args = mock_logger.debug.call_args[0][0]
    assert "fill color: MyBox" in call_args
    assert "current: 'red'" in call_args
    assert "new: 'blue'" in call_args
    print("  ✓ Logging with all parameters works")
    
    # Test with no logger
    log_element_change(None, "test", "element")  # Should not crash
    print("  ✓ No logger handling works")


def test_safe_execute():
    """Test safe execution wrapper."""
    print("Testing safe_execute...")
    
    mock_logger = Mock()
    
    # Test successful operation
    def successful_op():
        return "success"
    
    success, result = safe_execute(successful_op, mock_logger, "test operation")
    
    assert success == True
    assert result == "success"
    mock_logger.debug.assert_called_with("✓ test operation completed successfully")
    print("  ✓ Successful operation handling works")
    
    # Test failed operation
    def failed_op():
        raise ValueError("Test error")
    
    success, result = safe_execute(failed_op, mock_logger, "test operation", return_on_error="error_result")
    
    assert success == False
    assert result == "error_result"
    mock_logger.error.assert_called_with("✗ test operation failed: Test error")
    print("  ✓ Failed operation handling works")
    
    # Test with raise_on_error=True
    try:
        safe_execute(failed_op, mock_logger, "test operation", raise_on_error=True)
        assert False, "Should have raised exception"
    except ValueError:
        print("  ✓ Exception re-raising works")


def test_update_svg_style_property():
    """Test SVG style property updates."""
    print("Testing update_svg_style_property...")
    
    # Create test element
    svg_content = '<rect style="fill:red;stroke:blue"/>'
    element = etree.fromstring(svg_content.encode())
    mock_logger = Mock()
    
    # Test style update
    success = update_svg_style_property(element, "fill", "#00FF00", mock_logger)
    
    assert success == True
    new_style = element.get('style')
    assert "fill:#00FF00" in new_style
    assert "stroke:blue" in new_style
    print("  ✓ Style property update works")
    
    # Test no change needed
    success_no_change = update_svg_style_property(element, "fill", "#00FF00", mock_logger)
    assert success_no_change == False
    print("  ✓ No change detection works")
    
    # Test adding new property
    success_new = update_svg_style_property(element, "opacity", "0.5", mock_logger)
    assert success_new == True
    assert "opacity:0.5" in element.get('style')
    print("  ✓ New property addition works")


def test_validate_required_value():
    """Test value validation."""
    print("Testing validate_required_value...")
    
    mock_logger = Mock()
    
    # Test valid values
    assert validate_required_value("hello", mock_logger, "test_value") == True
    assert validate_required_value(123, mock_logger, "test_value") == True
    print("  ✓ Valid value validation works")
    
    # Test invalid values
    assert validate_required_value(None, mock_logger, "test_value") == False
    assert validate_required_value("", mock_logger, "test_value") == False
    assert validate_required_value("   ", mock_logger, "test_value") == False
    print("  ✓ Invalid value detection works")
    
    # Test without logger
    assert validate_required_value("hello") == True
    print("  ✓ No logger handling works")


def test_clean_string():
    """Test string cleaning."""
    print("Testing clean_string...")
    
    # Test basic cleaning
    assert clean_string("  hello world  ") == "hello world"
    assert clean_string(123) == "123"
    assert clean_string(None) == None
    print("  ✓ Basic string cleaning works")
    
    # Test with empty not allowed
    assert clean_string("", allow_empty=False) == None
    assert clean_string("   ", allow_empty=False) == None
    print("  ✓ Empty string rejection works")
    
    # Test with empty allowed
    assert clean_string("", allow_empty=True) == ""
    assert clean_string("   ", allow_empty=True) == ""
    print("  ✓ Empty string allowance works")
    
    # Test without stripping
    assert clean_string("  hello  ", strip=False) == "  hello  "
    print("  ✓ No strip option works")


def test_validate_file_basics():
    """Test file validation."""
    print("Testing validate_file_basics...")
    
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.png', delete=False) as f:
        f.write("test content")
        temp_file = f.name
    
    try:
        # Test valid file
        result = validate_file_basics(temp_file, {'.png', '.jpg'})
        
        assert result['valid'] == True
        assert result['file_size'] > 0
        assert result['extension'] == '.png'
        assert len(result['errors']) == 0
        print("  ✓ Valid file validation works")
        
        # Test invalid extension
        result_invalid = validate_file_basics(temp_file, {'.txt', '.csv'})
        
        assert result_invalid['valid'] == False
        assert "File extension not allowed" in result_invalid['errors'][0]
        print("  ✓ Invalid extension detection works")
        
        # Test non-existent file
        result_missing = validate_file_basics("/non/existent/file.png")
        
        assert result_missing['valid'] == False
        assert "File not found" in result_missing['errors'][0]
        print("  ✓ Missing file detection works")
        
    finally:
        os.unlink(temp_file)


def test_safe_dict_get():
    """Test dictionary access with fallbacks."""
    print("Testing safe_dict_get...")
    
    test_dict = {"color": "red", "fill": "blue"}
    
    # Test primary key found
    assert safe_dict_get(test_dict, "color") == "red"
    print("  ✓ Primary key access works")
    
    # Test fallback key used
    result = safe_dict_get(test_dict, "background", fallbacks=["fill", "color"])
    assert result == "blue"  # Should use fill as fallback
    print("  ✓ Fallback key access works")
    
    # Test default used
    result_default = safe_dict_get(test_dict, "missing", default="default_value")
    assert result_default == "default_value"
    print("  ✓ Default value works")
    
    # Test with empty values
    test_dict_empty = {"color": "", "fill": "blue"}
    result_empty = safe_dict_get(test_dict_empty, "color", fallbacks=["fill"])
    assert result_empty == "blue"  # Should skip empty color and use fill
    print("  ✓ Empty value skipping works")


def test_logged_iterate():
    """Test logged iteration."""
    print("Testing logged_iterate...")
    
    test_items = ["item1", "item2", "item3", "item4", "item5"]
    mock_logger = Mock()
    
    # Test normal iteration
    result_indices = []
    result_items = []
    
    for idx, item in logged_iterate(test_items, mock_logger, "test processing", show_progress=True):
        result_indices.append(idx)
        result_items.append(item)
    
    assert result_indices == [0, 1, 2, 3, 4]
    assert result_items == test_items
    
    # Check that progress was logged
    debug_calls = mock_logger.debug.call_args_list
    assert any("Starting test processing: 5 items" in str(call) for call in debug_calls)
    assert any("test processing completed: 5 items processed" in str(call) for call in debug_calls)
    print("  ✓ Progress logging works")
    
    # Test without progress
    mock_logger.reset_mock()
    result_no_progress = list(logged_iterate(test_items, mock_logger, show_progress=False))
    assert len(result_no_progress) == 5
    assert mock_logger.debug.call_count == 0
    print("  ✓ No progress option works")


def test_config_integration():
    """Test integration with config module."""
    print("Testing config integration...")
    
    # Test that all expected keys exist
    assert "labeled_elements" in COMMON_XPATH_EXPRESSIONS
    assert "id_elements" in COMMON_XPATH_EXPRESSIONS
    assert "shape_element_base" in COMMON_XPATH_EXPRESSIONS
    assert "text_element_svg" in COMMON_XPATH_EXPRESSIONS
    print("  ✓ XPath expressions available")
    
    # Test namespace handling
    assert "svg" in SVG_NAMESPACES
    assert "inkscape" in SVG_NAMESPACES
    assert "xlink" in SVG_NAMESPACES
    print("  ✓ Namespaces available")


def run_all_tests():
    """Run all test functions."""
    print("🧪 Running Common Utils Test Suite")
    print("=" * 50)
    
    tests = [
        test_xpath_query,
        test_get_element_attributes,
        test_log_element_change,
        test_safe_execute,
        test_update_svg_style_property,
        test_validate_required_value,
        test_clean_string,
        test_validate_file_basics,
        test_safe_dict_get,
        test_logged_iterate,
        test_config_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"✅ {test_func.__name__} PASSED\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} FAILED: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Common utils are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)