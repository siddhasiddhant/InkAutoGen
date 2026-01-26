# InkAutoGen Test Suite

Professional testing framework for the InkAutoGen SVG automation extension.

## 📁 Overview

This test suite provides comprehensive coverage for all InkAutoGen functionality after code optimization. The suite is designed for both developers and testers to verify system behavior, identify regressions, and validate new features.

## 🏗️ Structure

```
tests/
├── README.md                          # This file - Test suite guide
├── run_tests.py                       # Main test runner with CLI
├── conftest.py                         # PyTest configuration and fixtures
├── unit/                               # Unit tests for individual modules
│   ├── __init__.py
│   ├── test_config.py                 # Configuration constants
│   ├── test_common_utils.py            # Common utilities
│   ├── test_svg_processor.py          # SVG processing
│   ├── test_csv_reader.py              # CSV reading
│   ├── test_file_exporter.py           # File exporting
│   ├── test_security.py                # Security validation
│   └── test_performance.py             # Performance utilities
├── integration/                         # End-to-end integration tests
│   ├── __init__.py
│   ├── test_basic_workflow.py         # Basic CSV→SVG workflow
│   ├── test_layer_visibility.py        # Layer operations
│   ├── test_image_processing.py        # Image handling
│   ├── test_property_modification.py  # Style modifications
│   └── test_error_handling.py          # Error scenarios
├── fixtures/                            # Test data and assets
│   ├── svg_templates/                 # Sample SVG files
│   ├── csv_samples/                   # Sample CSV files
│   └── test_data/                     # Generated test assets
└── utils/                               # Test utilities
    ├── __init__.py
    ├── test_helpers.py                # Shared test utilities
    ├── assertions.py                  # Custom assertions
    └── mocks.py                      # Test doubles
```

## 🚀 Quick Start

### For Developers
```bash
# Run all tests with verbose output
python tests/run_tests.py --verbose

# Run specific test category
python tests/run_tests.py --unit
python tests/run_tests.py --integration
python tests/run_tests.py --security

# Run specific test file
python tests/run_tests.py unit/test_svg_processor.py
```

### For Testers/QA
```bash
# Run with detailed reporting
python tests/run_tests.py --report --output test_report.html

# Run with coverage analysis
python tests/run_tests.py --coverage --min-coverage 80

# Run performance benchmarks
python tests/run_tests.py --benchmark
```

## 📊 Test Categories

### Unit Tests (`unit/`)
- **Configuration Tests**: Validate all constants and settings
- **Common Utils Tests**: Test reusable utility functions
- **SVG Processor Tests**: Test SVG element manipulation
- **CSV Reader Tests**: Test CSV parsing and validation
- **File Exporter Tests**: Test export functionality
- **Security Tests**: Test file validation and security
- **Performance Tests**: Test caching and optimization

### Integration Tests (`integration/`)
- **Basic Workflow**: Complete CSV→SVG export process
- **Layer Operations**: Layer visibility and management
- **Image Processing**: Image replacement and validation
- **Property Modification**: Style and attribute changes
- **Error Handling**: Exception scenarios and recovery

## 🎯 Key Features

### Test Runner CLI
- **Multiple execution modes**: Unit, integration, all
- **Flexible filtering**: By module, category, or keyword
- **Detailed reporting**: Console, HTML, JSON formats
- **Coverage analysis**: Line and branch coverage with thresholds
- **Performance monitoring**: Execution time and memory usage
- **Continuous integration**: JUnit XML output for CI/CD

### Test Data Management
- **Fixtures**: Reusable test assets and data
- **Parameterized tests**: Data-driven test execution
- **Mock support**: External dependency isolation
- **Temporary environments**: Isolated test execution
- **Cleanup automation**: Post-test resource management

## 📈 Coverage Areas

### Core Functionality
- ✅ Configuration consolidation
- ✅ Common utility functions
- ✅ SVG element processing
- ✅ CSV data reading
- ✅ File export operations
- ✅ Security validation
- ✅ Error handling patterns

### Edge Cases
- ✅ Invalid input handling
- ✅ Malformed file recovery
- ✅ Performance edge cases
- ✅ Memory constraint scenarios
- ✅ Concurrent access patterns

### Integration Scenarios
- ✅ Complete workflows
- ✅ Cross-module interactions
- ✅ Real-world file processing
- ✅ Error propagation
- ✅ Performance characteristics

## 🔧 Configuration

### Environment Variables
```bash
INKAUTOGEN_TEST_DATA_DIR="/path/to/test/fixtures"
INKAUTOGEN_TEST_OUTPUT_DIR="/tmp/inkautogen_tests"
INKAUTOGEN_TEST_TIMEOUT=30                    # seconds
INKAUTOGEN_TEST_PARALLEL=4                     # worker threads
```

### Configuration Files
- `tests/test_config.json` - Test execution settings
- `tests/coverage_config.json` - Coverage requirements
- `tests/benchmark_config.json` - Performance baselines

## 📋 Test Examples

### Basic SVG Processing Test
```python
# Using the test framework
from tests.utils.test_helpers import create_test_svg, assert_svg_modification
from tests.unit.test_svg_processor import TestSVGProcessor

def test_custom_scenario():
    # Create test SVG
    svg_content = create_test_svg("template_with_layers.svg")
    
    # Process modification
    processor = TestSVGProcessor()
    result = processor.process_text_element(svg_root, "TestText", "New Value")
    
    # Assert result
    assert_svg_modification(result, expected_changes={"TestText": "New Value"})
```

### Integration Test Example
```python
# Complete workflow test
from tests.integration.test_basic_workflow import TestBasicWorkflow

def test_csv_to_svg_export():
    workflow = TestBasicWorkflow()
    
    # Setup test data
    test_data = workflow.create_test_csv("sample_data.csv")
    test_template = workflow.create_svg_template("template.svg")
    
    # Execute workflow
    results = workflow.execute_export(test_data, test_template)
    
    # Validate results
    workflow.assert_export_success(results)
    workflow.assert_output_files_created(results)
```

## 🚦 Usage Guidelines

### For Adding New Tests
1. **Create test file** in appropriate category (`unit/` or `integration/`)
2. **Follow naming convention**: `test_<functionality>.py`
3. **Inherit from base classes**: Use provided test utilities
4. **Use fixtures**: Place test data in `fixtures/` directory
5. **Document purpose**: Add docstring explaining test scenario
6. **Include assertions**: Use framework's assertion helpers

### For Running Tests
1. **Environment setup**: Ensure test dependencies installed
2. **Database isolation**: Use separate test database/cache
3. **File cleanup**: Tests should not leave artifacts
4. **Parallel execution**: Use provided parallel test runner
5. **Result analysis**: Review detailed reports for insights

## 📚 Documentation References

- **Test Results**: `tests/reports/` directory
- **Coverage Reports**: `tests/coverage/` directory
- **Benchmark Data**: `tests/benchmarks/` directory
- **API Documentation**: Individual test file docstrings
- **Examples**: `tests/examples/` directory

## 🔍 Troubleshooting

### Common Issues
- **Import errors**: Check `PYTHONPATH` includes project root
- **Fixture not found**: Verify file paths in test fixtures
- **Timeout failures**: Increase `INKAUTOGEN_TEST_TIMEOUT`
- **Memory issues**: Reduce `INKAUTOGEN_TEST_PARALLEL`

### Debug Mode
```bash
# Run with maximum debugging output
python tests/run_tests.py --debug --verbose --no-cleanup

# Individual test debugging
python tests/run_tests.py --debug --test test_svg_processor::test_text_replacement
```

## 🎯 Success Criteria

### Test Suite Success
- ✅ All unit tests pass (>95% coverage)
- ✅ All integration tests complete successfully
- ✅ No new regressions introduced
- ✅ Performance within acceptable thresholds
- ✅ Security validation effective
- ✅ Documentation completeness ≥ 90%
- ✅ All tests reproducible

### Quality Gates
- ✅ Code coverage ≥ 80%
- ✅ No critical vulnerabilities
- ✅ Performance regression ≤ 5%
- ✅ All tests reproducible
- ✅ Professional test documentation

---

This test suite ensures that code optimizations maintain functionality while providing comprehensive validation for both development and testing workflows.