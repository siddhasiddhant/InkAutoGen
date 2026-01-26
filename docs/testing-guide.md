# InkAutoGen Testing Guide

## 📚 Table of Contents

1. [Testing Overview](#testing-overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Writing Tests](#writing-tests)
6. [Test Data Management](#test-data-management)
7. [Performance Testing](#performance-testing)
8. [Integration Testing](#integration-testing)
9. [Debugging Tests](#debugging-tests)
10. [Continuous Integration](#continuous-integration)

## 🎯 Testing Overview
This test suite provides comprehensive coverage for all InkAutoGen functionality after code optimization. The suite is designed for both
developers and testers to verify system behavior, identify regressions, and validate new features. 

### Testing Philosophy
InkAutoGen follows a comprehensive testing strategy to ensure reliability, performance, and security:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Validate performance requirements
- **Security Tests**: Verify security measures

### Test Coverage Goals
- **Code Coverage**: Minimum 90% line coverage
- **Branch Coverage**: Minimum 85% branch coverage
- **Critical Paths**: 100% coverage for core functionality
- **Error Handling**: 100% coverage for exception scenarios

## 📁 Test Structure

### Test Directory Organization
```
tests/
├── __init__.py                 # Test initialization
├── conftest.py                 # Pytest configuration and fixtures
├── run_tests.py                # Custom test runner
├── unit/                       # Unit tests
│   ├── test_csv_reader.py
│   ├── test_svg_processor.py
│   ├── test_file_exporter.py
│   ├── test_utilities.py
│   ├── test_security.py
│   └── test_exceptions.py
├── integration/                # Integration tests
│   ├── test_csv_to_svg.py
│   ├── test_svg_to_export.py
│   └── test_full_workflow.py
├── performance/                # Performance tests
│   ├── test_batch_processing.py
│   ├── test_memory_usage.py
│   └── test_large_files.py
├── security/                  # Security tests
│   ├── test_input_validation.py
│   ├── test_file_security.py
│   └── test_path_traversal.py
├── fixtures/                   # Test data and resources
│   ├── csv_files/
│   ├── svg_templates/
│   ├── expected_outputs/
│   └── test_images/
└── utils/                      # Test utilities and helpers
    ├── test_helpers.py
    ├── mock_data.py
    └── assertion_helpers.py
```

### Test Files Naming Convention
- **Unit Tests**: `test_<module_name>.py`
- **Integration Tests**: `test_<feature>_integration.py`
- **Performance Tests**: `test_<performance_aspect>.py`
- **Security Tests**: `test_<security_aspect>.py`

## 🚀 Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Ensure Inkscape is available for integration tests
inkscape --version
```

### Basic Test Execution

#### 1. Run All Tests
```bash
cd tests
python3 -m pytest
```

#### 2. Run Specific Test Categories
```bash
# Unit tests only
pytest unit/

# Integration tests only
pytest integration/

# Performance tests only
pytest performance/

# Security tests only
pytest security/
```

#### 3. Run Specific Test Files
```bash
# Single test file
pytest test_csv_reader.py

# Multiple test files
pytest test_csv_reader.py test_svg_processor.py
```

#### 4. Run Specific Test Methods
```bash
# Specific test method
pytest test_csv_reader.py::TestCSVReader::test_read_csv_data

# Tests matching pattern
pytest -k "test_read_csv"
```

### Test Runner Options

#### 1. Custom Test Runner
```bash
# Use the custom test runner
python3 run_tests.py

# With options
python3 run_tests.py --coverage --performance --verbose
```

#### 2. Pytest Options
```bash
# Verbose output
pytest -v

# With coverage
pytest --cov=modules --cov-report=html

# Stop on first failure
pytest -x

# Run failed tests only
pytest --lf

# Parallel execution
pytest -n auto
```

## 📊 Usage Examples

### Command Line:
```bash
# Default behavior (with timestamps)
python3 inkautogen.py template.svg data.csv --enable_logging

# Disable timestamps for cleaner output
python3 inkautogen.py template.svg data.csv --enable_logging --disable_log_timestamps

# Combine with other options
python3 inkautogen.py template.svg data.csv \
  --export_format=pdf \
  --enable_logging \
  --disable_log_timestamps \
  --log_level=DEBUG
```

## 📋 Test Categories

### 1. Unit Tests

#### CSV Reader Tests
```python
# tests/unit/test_csv_reader.py
import pytest
from modules.csv_reader import CSVReader
from modules.exceptions import CSVParsingError

class TestCSVReader:
    def setup_method(self):
        """Setup test fixtures."""
        self.reader = CSVReader()
    
    def test_read_csv_data_success(self):
        """Test successful CSV reading."""
        # Arrange
        csv_path = "fixtures/csv_files/simple_test.csv"
        
        # Act
        result = self.reader.read_csv_data(csv_path)
        
        # Assert
        assert len(result) == 3
        assert "name" in result[0]
        assert result[0]["name"] == "John Doe"
    
    def test_read_csv_data_invalid_file(self):
        """Test handling of invalid CSV file."""
        # Arrange
        csv_path = "fixtures/csv_files/invalid_file.csv"
        
        # Act & Assert
        with pytest.raises(CSVParsingError):
            self.reader.read_csv_data(csv_path)
    
    def test_classify_csv_data_mixed_types(self):
        """Test CSV data classification with mixed types."""
        # Arrange
        data = [
            {"name": "John", "button##fill": "#ff0000"},
            {"name": "Jane", "button##fill": "#00ff00"}
        ]
        
        # Act
        result = self.reader.classify_csv_data(data)
        
        # Assert
        assert "element_values" in result
        assert "properties" in result
        assert "name" in result["element_values"]
        assert "button##fill" in result["properties"]
```

#### SVG Processor Tests
```python
# tests/unit/test_svg_processor.py
import pytest
import lxml.etree as ET
from modules.svg_processor import SVGProcessor

class TestSVGProcessor:
    def setup_method(self):
        """Setup test fixtures."""
        self.processor = SVGProcessor()
        self.svg_root = ET.parse("fixtures/svg_templates/simple_template.svg").getroot()
    
    def test_find_elements_by_name_success(self):
        """Test successful element finding."""
        # Act
        elements = self.processor.find_elements_by_name(self.svg_root, "<name>")
        
        # Assert
        assert len(elements) == 1
        assert elements[0].get("id") == "name_element"
    
    def test_find_elements_by_name_not_found(self):
        """Test element not found."""
        # Act
        elements = self.processor.find_elements_by_name(self.svg_root, "<nonexistent>")
        
        # Assert
        assert len(elements) == 0
    
    def test_process_text_element(self):
        """Test text element processing."""
        # Arrange
        element = self.svg_root.find(".//text[@id='name_element']")
        new_value = "Test Name"
        
        # Act
        self.processor.process_text_element(element, new_value)
        
        # Assert
        assert element.text == new_value
```

### 2. Integration Tests

#### Full Workflow Tests
```python
# tests/integration/test_full_workflow.py
import pytest
import os
import tempfile
from inkautogen import InkAutoGen

class TestFullWorkflow:
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = "fixtures/csv_files/test_data.csv"
        self.svg_template = "fixtures/svg_templates/certificate_template.svg"
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_certificate_generation(self):
        """Test complete certificate generation workflow."""
        # Arrange
        extension = InkAutoGen()
        extension.args.csv_file = self.csv_path
        extension.args.output_directory = self.temp_dir
        extension.args.export_format = "png"
        extension.args.filename_pattern = "certificate_{name}"
        
        # Act
        extension.effect()
        
        # Assert
        output_files = os.listdir(self.temp_dir)
        assert len(output_files) == 3  # 3 rows in CSV
        
        # Check specific files exist
        assert "certificate_John_Doe.png" in output_files
        assert "certificate_Jane_Smith.png" in output_files
```

### 3. Performance Tests

#### Batch Processing Tests
```python
# tests/performance/test_batch_processing.py
import pytest
import time
from modules.performance import PerformanceMonitor
from modules.csv_reader import CSVReader

class TestBatchProcessing:
    def setup_method(self):
        """Setup performance test environment."""
        self.monitor = PerformanceMonitor()
        self.reader = CSVReader()
    
    def test_large_csv_processing_performance(self):
        """Test performance with large CSV files."""
        # Arrange
        large_csv = "fixtures/csv_files/large_test_1000_rows.csv"
        max_time = 10.0  # seconds
        
        # Act
        start_time = time.time()
        data = self.reader.read_csv_data(large_csv)
        end_time = time.time()
        
        # Assert
        processing_time = end_time - start_time
        assert processing_time < max_time
        assert len(data) == 1000
    
    def test_memory_usage_during_processing(self):
        """Test memory usage during batch processing."""
        import psutil
        import os
        
        # Arrange
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Act
        # Process large batch
        large_csv = "fixtures/csv_files/large_test_1000_rows.csv"
        data = self.reader.read_csv_data(large_csv)
        
        # Cleanup
        del data
        
        # Assert
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        max_increase = 100 * 1024 * 1024  # 100MB
        
        assert memory_increase < max_increase
```

### 4. Security Tests

#### Input Validation Tests
```python
# tests/security/test_input_validation.py
import pytest
from modules.security import SecurityValidator
from modules.exceptions import SecurityError

class TestInputValidation:
    def setup_method(self):
        """Setup security test environment."""
        self.validator = SecurityValidator()
    
    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks."""
        # Arrange
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM"
        ]
        
        # Act & Assert
        for path in malicious_paths:
            with pytest.raises(SecurityError):
                self.validator.validate_file_path(path)
    
    def test_script_injection_prevention(self):
        """Test prevention of script injection in SVG content."""
        # Arrange
        malicious_svg = '''
        <svg>
            <script>alert('xss')</script>
            <text id="test">javascript:alert('xss')</text>
        </svg>
        '''
        
        # Act
        sanitized = self.validator.sanitize_svg_content(malicious_svg)
        
        # Assert
        assert "<script>" not in sanitized
        assert "javascript:" not in sanitized
```

## ✍️ Writing Tests

### Test Structure Template

#### 1. Basic Test Class
```python
import pytest
from modules.module_to_test import ClassToTest

class TestClassToTest:
    def setup_method(self):
        """Setup test fixtures before each test."""
        self.instance = ClassToTest()
    
    def teardown_method(self):
        """Cleanup after each test."""
        if hasattr(self, 'instance'):
            del self.instance
    
    def test_method_success_case(self):
        """Test successful case."""
        # Arrange
        input_data = "test_input"
        expected_output = "expected_output"
        
        # Act
        result = self.instance.method_to_test(input_data)
        
        # Assert
        assert result == expected_output
    
    def test_method_error_case(self):
        """Test error handling."""
        # Arrange
        invalid_input = "invalid_input"
        
        # Act & Assert
        with pytest.raises(ExpectedException):
            self.instance.method_to_test(invalid_input)
```

#### 2. Parameterized Tests
```python
import pytest

@pytest.mark.parametrize("input_data,expected_output", [
    ("input1", "output1"),
    ("input2", "output2"),
    ("input3", "output3"),
])
def test_parameterized_method(input_data, expected_output):
    """Test method with multiple inputs."""
    instance = ClassToTest()
    result = instance.method_to_test(input_data)
    assert result == expected_output
```

### Test Fixtures

#### 1. Custom Fixtures
```python
# tests/conftest.py
import pytest
import tempfile
import os

@pytest.fixture
def temp_directory():
    """Create temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def sample_csv_data():
    """Provide sample CSV data for testing."""
    return [
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Jane Smith", "email": "jane@example.com"}
    ]

@pytest.fixture
def mock_svg_processor():
    """Create mock SVG processor for testing."""
    from unittest.mock import Mock
    mock_processor = Mock()
    mock_processor.find_elements_by_name.return_value = []
    mock_processor.process_element_value.return_value = None
    return mock_processor
```

#### 2. Using Fixtures
```python
def test_with_fixtures(temp_directory, sample_csv_data):
    """Test using custom fixtures."""
    # Use temp_directory
    assert os.path.exists(temp_directory)
    
    # Use sample_csv_data
    assert len(sample_csv_data) == 2
    assert sample_csv_data[0]["name"] == "John Doe"
```

## 📊 Test Data Management

### Test Data Organization

#### 1. CSV Test Files
```
tests/fixtures/csv_files/
├── simple_test.csv              # Basic test data
├── large_test_1000_rows.csv     # Performance testing
├── invalid_format.csv           # Error testing
├── unicode_test.csv             # Unicode handling
├── empty_rows.csv               # Edge case testing
└── special_characters.csv       # Special character handling
```

#### 2. SVG Template Files
```
tests/fixtures/svg_templates/
├── simple_template.svg          # Basic template
├── complex_template.svg         # Multiple element types
├── invalid_template.svg         # Malformed SVG
├── large_template.svg           # Performance testing
└── unicode_template.svg         # Unicode content
```

#### 3. Expected Outputs
```
tests/fixtures/expected_outputs/
├── simple_output.png
├── complex_output.pdf
├── certificate_output.svg
└── error_cases/
```

### Test Data Generation

#### 1. CSV Data Generator
```python
# tests/utils/test_data_generator.py
import csv
import random
from typing import List, Dict

class TestDataGenerator:
    def generate_csv_data(self, num_rows: int, filename: str):
        """Generate test CSV data."""
        first_names = ["John", "Jane", "Bob", "Alice", "Charlie"]
        last_names = ["Doe", "Smith", "Johnson", "Brown", "Davis"]
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['name', 'email', 'department', 'photo']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for i in range(num_rows):
                name = f"{random.choice(first_names)} {random.choice(last_names)}"
                email = f"{name.lower().replace(' ', '.')}@example.com"
                department = random.choice(["Engineering", "Marketing", "Sales"])
                photo = f"photo_{i}.jpg"
                
                writer.writerow({
                    'name': name,
                    'email': email,
                    'department': department,
                    'photo': photo
                })
```

#### 2. SVG Template Generator
```python
# tests/utils/svg_generator.py
import xml.etree.ElementTree as ET

class SVGTemplateGenerator:
    def generate_simple_template(self, filename: str):
        """Generate simple SVG template for testing."""
        svg = ET.Element("svg", {
            "width": "800",
            "height": "600",
            "xmlns": "http://www.w3.org/2000/svg"
        })
        
        # Add text element
        text = ET.SubElement(svg, "text", {
            "id": "name_element",
            "x": "400",
            "y": "300",
            "text-anchor": "middle",
            "font-size": "24"
        })
        text.text = "<name>"
        
        # Add rectangle
        rect = ET.SubElement(svg, "rect", {
            "id": "frame",
            "x": "50",
            "y": "50",
            "width": "700",
            "height": "500",
            "fill": "none",
            "stroke": "black",
            "stroke-width": "2"
        })
        
        tree = ET.ElementTree(svg)
        tree.write(filename, encoding='unicode', xml_declaration=True)
```

## ⚡ Performance Testing

### Performance Test Framework

#### 1. Benchmark Decorator
```python
# tests/utils/performance_helpers.py
import time
import functools
from typing import Callable

def benchmark(max_time: float):
    """Decorator for benchmarking test performance."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            assert execution_time < max_time, f"Performance test failed: {execution_time:.2f}s > {max_time:.2f}s"
            
            return result
        return wrapper
    return decorator

# Usage
@benchmark(max_time=5.0)
def test_csv_reading_performance():
    """Test CSV reading performance."""
    reader = CSVReader()
    data = reader.read_csv_data("large_test.csv")
    assert len(data) > 0
```

#### 2. Memory Profiling
```python
# tests/utils/memory_profiler.py
import psutil
import os
from typing import Callable

def profile_memory(max_memory_mb: float):
    """Decorator for profiling memory usage."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            result = func(*args, **kwargs)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = final_memory - initial_memory
            
            assert memory_used < max_memory_mb, f"Memory test failed: {memory_used:.2f}MB > {max_memory_mb:.2f}MB"
            
            return result
        return wrapper
    return decorator
```

### Performance Test Cases

#### 1. Large File Processing
```python
# tests/performance/test_large_files.py
import pytest
from tests.utils.performance_helpers import benchmark
from tests.utils.memory_profiler import profile_memory

class TestLargeFileProcessing:
    @benchmark(max_time=30.0)
    @profile_memory(max_memory_mb=500.0)
    def test_large_csv_processing(self):
        """Test processing of large CSV files."""
        reader = CSVReader()
        data = reader.read_csv_data("fixtures/csv_files/large_test_10000_rows.csv")
        
        assert len(data) == 10000
        assert all("name" in row for row in data)
    
    @benchmark(max_time=60.0)
    def test_large_svg_processing(self):
        """Test processing of complex SVG templates."""
        processor = SVGProcessor()
        svg_root = load_large_svg_template()
        
        elements = processor.find_elements_by_name(svg_root, "<name>")
        
        assert len(elements) > 0
```

## 🔗 Integration Testing

### Integration Test Framework

#### 1. End-to-End Test Setup
```python
# tests/integration/test_e2e_workflow.py
import pytest
import os
import tempfile
import subprocess
from pathlib import Path

class TestE2EWorkflow:
    def setup_method(self):
        """Setup end-to-end test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_dir = Path(__file__).parent.parent / "fixtures"
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_inkscape_workflow(self):
        """Test complete workflow through Inkscape interface."""
        # Arrange
        csv_file = self.test_data_dir / "csv_files" / "simple_test.csv"
        svg_template = self.test_data_dir / "svg_templates" / "simple_template.svg"
        
        # Copy template to temp directory
        temp_template = Path(self.temp_dir) / "template.svg"
        import shutil
        shutil.copy(svg_template, temp_template)
        
        # Act - Run Inkscape with extension
        cmd = [
            "inkscape",
            "--actions=",
            f"FileOpen:{temp_template};",
            f"Extension:export.inkautogen;csv_file={csv_file};",
            f"output_directory={self.temp_dir};",
            "export_format=png;",
            "FileQuit"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Assert
        assert result.returncode == 0
        output_files = list(Path(self.temp_dir).glob("*.png"))
        assert len(output_files) > 0
```

#### 2. Component Integration Tests
```python
# tests/integration/test_component_integration.py
import pytest
from modules.csv_reader import CSVReader
from modules.svg_processor import SVGProcessor
from modules.file_exporter import FileExporter

class TestComponentIntegration:
    def test_csv_to_svg_integration(self):
        """Test integration between CSV reader and SVG processor."""
        # Arrange
        csv_reader = CSVReader()
        svg_processor = SVGProcessor()
        
        csv_data = csv_reader.read_csv_data("fixtures/csv_files/test_data.csv")
        svg_root = load_svg_template("fixtures/svg_templates/test_template.svg")
        
        # Act
        for row in csv_data:
            for column, value in row.items():
                if column.startswith('<') and column.endswith('>'):
                    elements = svg_processor.find_elements_by_name(svg_root, column)
                    for element in elements:
                        svg_processor.process_element_value(element, value, "text")
        
        # Assert
        # Verify elements were processed correctly
        processed_elements = svg_processor.find_elements_by_name(svg_root, "<name>")
        assert len(processed_elements) > 0
```

## 🐛 Debugging Tests

### Debugging Tools

#### 1. Test Debugging Helpers
```python
# tests/utils/debug_helpers.py
import pprint
import logging
from typing import Any

def debug_print(data: Any, label: str = "DEBUG"):
    """Print data with pretty formatting for debugging."""
    print(f"\n=== {label} ===")
    if isinstance(data, (dict, list)):
        pprint.pprint(data)
    else:
        print(data)
    print("=" * (len(label) + 8))

def setup_test_logging():
    """Setup detailed logging for test debugging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def save_debug_output(data: Any, filename: str):
    """Save data to file for debugging."""
    with open(filename, 'w') as f:
        if isinstance(data, (dict, list)):
            pprint.pprint(data, f)
        else:
            f.write(str(data))
```

#### 2. Test Failure Analysis
```python
# tests/utils/failure_analyzer.py
import pytest
import traceback
from typing import List

class TestFailureAnalyzer:
    def __init__(self):
        self.failures: List[dict] = []
    
    def pytest_runtest_makereport(self, item, call):
        """Analyze test failures."""
        if call.when == "call" and call.excinfo is not None:
            failure_info = {
                "test_name": item.name,
                "error_type": call.excinfo.type.__name__,
                "error_message": str(call.excinfo.value),
                "traceback": traceback.format_exception(
                    call.excinfo.type,
                    call.excinfo.value,
                    call.excinfo.tb
                )
            }
            self.failures.append(failure_info)
    
    def generate_failure_report(self, output_file: str):
        """Generate failure analysis report."""
        with open(output_file, 'w') as f:
            f.write("Test Failure Analysis Report\n")
            f.write("=" * 40 + "\n\n")
            
            for failure in self.failures:
                f.write(f"Test: {failure['test_name']}\n")
                f.write(f"Error: {failure['error_type']}\n")
                f.write(f"Message: {failure['error_message']}\n")
                f.write("Traceback:\n")
                f.write(''.join(failure['traceback']))
                f.write("\n" + "-" * 40 + "\n\n")
```

### Common Test Issues

#### 1. Fixture Problems
```python
# Debugging fixture issues
def test_with_fixture_debugging(temp_directory):
    """Debug test with fixture issues."""
    debug_print(temp_directory, "Temp Directory")
    debug_print(os.path.exists(temp_directory), "Directory Exists")
    debug_print(os.listdir(temp_directory), "Directory Contents")
    
    # Test logic here
```

#### 2. Mock Issues
```python
# Debugging mock issues
def test_with_mock_debugging(mock_svg_processor):
    """Debug test with mock issues."""
    debug_print(mock_svg_processor, "Mock Processor")
    debug_print(mock_svg_processor.method_calls, "Method Calls")
    debug_print(mock_svg_processor.call_args_list, "Call Arguments")
    
    # Test logic here
```

## 🔄 Continuous Integration

### CI Configuration

#### 1. GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test InkAutoGen

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.7, 3.8, 3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Install Inkscape
      run: |
        sudo apt-get update
        sudo apt-get install -y inkscape
    
    - name: Run unit tests
      run: |
        cd tests
        pytest unit/ -v --cov=modules --cov-report=xml
    
    - name: Run integration tests
      run: |
        cd tests
        pytest integration/ -v
    
    - name: Run performance tests
      run: |
        cd tests
        pytest performance/ -v --benchmark-only
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./tests/coverage.xml
```

#### 2. Test Configuration
```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=modules
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    security: Security tests
    slow: Slow running tests
```

### Quality Gates

#### 1. Coverage Requirements
```python
# tests/conftest.py
def pytest_configure(config):
    """Configure pytest with quality gates."""
    # Set minimum coverage requirements
    config.option.cov_fail_under = 90

def pytest_sessionfinish(session, exitstatus):
    """Enforce quality gates."""
    # Check coverage
    if hasattr(session.config, 'cov'):
        total_coverage = session.config.cov.total_coverage
        if total_coverage < 90:
            print(f"Coverage {total_coverage}% below required 90%")
            session.shouldfail = "Coverage requirements not met"
```

#### 2. Performance Gates
```python
# tests/performance/performance_gates.py
import pytest
import time

@pytest.mark.performance
def test_performance_gate():
    """Enforce performance requirements."""
    max_response_time = 5.0  # seconds
    
    start_time = time.time()
    # Run critical performance test
    result = run_critical_performance_test()
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response_time < max_response_time, f"Performance gate failed: {response_time}s > {max_response_time}s"
```

## 📊 Test Reporting

### Coverage Reports

#### 1. HTML Coverage Report
```bash
# Generate detailed HTML coverage report
pytest --cov=modules --cov-report=html

# View report
open htmlcov/index.html
```

#### 2. Coverage Configuration
```python
# .coveragerc
[run]
source = modules
omit = 
    */tests/*
    */test_*
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError

[html]
directory = htmlcov
```

### Test Metrics

#### 1. Test Metrics Collection
```python
# tests/utils/metrics_collector.py
import time
import psutil
from typing import Dict, List

class TestMetricsCollector:
    def __init__(self):
        self.metrics: List[Dict] = []
    
    def start_test(self, test_name: str):
        """Start collecting metrics for a test."""
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
    
    def end_test(self, test_name: str, passed: bool):
        """End collecting metrics for a test."""
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        metric = {
            "test_name": test_name,
            "duration": end_time - self.start_time,
            "memory_used": end_memory - self.start_memory,
            "passed": passed
        }
        
        self.metrics.append(metric)
    
    def generate_report(self, output_file: str):
        """Generate metrics report."""
        with open(output_file, 'w') as f:
            f.write("Test Metrics Report\n")
            f.write("=" * 30 + "\n\n")
            
            for metric in self.metrics:
                f.write(f"Test: {metric['test_name']}\n")
                f.write(f"Duration: {metric['duration']:.3f}s\n")
                f.write(f"Memory: {metric['memory_used'] / 1024 / 1024:.2f}MB\n")
                f.write(f"Status: {'PASSED' if metric['passed'] else 'FAILED'}\n")
                f.write("-" * 30 + "\n")
```

---

**Happy testing!** 🧪✨