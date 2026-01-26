# InkAutoGen Developer Guide

## 📚 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Module Structure](#module-structure)
3. [Core Components](#core-components)
4. [Development Setup](#development-setup)
5. [Code Organization](#code-organization)
6. [API Reference](#api-reference)
7. [Extending the Extension](#extending-the-extension)
8. [Testing and Debugging](#testing-and-debugging)
9. [Performance Considerations](#performance-considerations)
10. [Security Guidelines](#security-guidelines)

## 🏗️ Architecture Overview

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Inkscape Extension Layer                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │   inkautogen.py │  │  inkautogen.inx │  │   UI/CLI Layer  ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Core Processing Layer                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │   CSV Reader    │  │  SVG Processor  │  │  File Exporter  ││
│  │                 │  │                 │  │                 ││
│  │ • Encoding      │  │ • Element       │  │ • Multi-format  ││
│  │ • Validation    │  │   Processing    │  │ • PDF Merging   ││
│  │ • Classification│  │ • Property      │  │ • Temp Mgmt     ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Support Services Layer                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │   Utilities     │  │   Security      │  │   Performance    ││
│  │                 │  │                 │  │                 ││
│  │ • XPath         │  │ • Validation    │  │ • Monitoring    ││
│  │ • Filename      │  │ • Sanitization  │  │ • Timing        ││
│  │ • Logging       │  │ • File Checks   │  │ • Memory        ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Design Principles
1. **Modular Architecture**: Each component has a single responsibility
2. **Loose Coupling**: Modules interact through well-defined interfaces
3. **Error Resilience**: Comprehensive error handling and recovery
4. **Performance First**: Optimized for batch processing
5. **Security Focused**: Input validation and safe operations

## 📁 Module Structure

### Core Modules
```
modules/
├── __init__.py              # Module initialization
├── config.py               # Configuration constants
├── csv_reader.py           # CSV data processing
├── svg_processor.py        # SVG template processing
├── file_exporter.py        # File export operations
├── utilities.py            # Helper functions
├── security.py             # Security validation
├── exceptions.py           # Custom exceptions
├── performance.py          # Performance monitoring
└── version.py              # Version information
```

### Module Dependencies
```
inkautogen.py
    ├── csv_reader.py
    ├── svg_processor.py
    ├── file_exporter.py
    ├── utilities.py
    ├── config.py
    ├── exceptions.py
    └── version.py

csv_reader.py
    ├── utilities.py
    ├── config.py
    ├── exceptions.py
    └── security.py

svg_processor.py
    ├── utilities.py
    ├── config.py
    ├── exceptions.py
    └── security.py

file_exporter.py
    ├── utilities.py
    ├── config.py
    ├── exceptions.py
    └── performance.py
```

## 🔧 Core Components

### 1. Main Extension (`inkautogen.py`)

#### Class: `InkAutoGen`
The main orchestrator that coordinates all processing modules.

```python
class InkAutoGen(Effect):
    """Main Inkscape extension class for batch SVG processing."""
    
    def __init__(self):
        """Initialize the extension with default parameters."""
        
    def effect(self):
        """Main processing method called by Inkscape."""
        
    def process_batch(self):
        """Process all CSV rows and generate output files."""
```

#### Key Responsibilities
- Parse command-line arguments from Inkscape interface
- Initialize and coordinate all processing modules
- Manage the complete workflow from CSV input to file output
- Handle error recovery and logging

### 2. CSV Reader (`modules/csv_reader.py`)

#### Class: `CSVReader`
Handles CSV data import with automatic encoding detection and validation.

```python
class CSVReader:
    """CSV data reader with encoding detection and validation."""
    
    def read_csv_data(self, file_path: str) -> List[Dict[str, str]]:
        """Read CSV data with automatic encoding detection."""
        
    def classify_csv_data(self, data: List[Dict[str, str]]) -> Dict[str, Any]:
        """Classify CSV headers into element values and properties."""
        
    def filter_rows_by_range(self, data: List[Dict[str, str]], row_range: str) -> List[Dict[str, str]]:
        """Filter CSV rows by specified range."""
```

#### Key Features
- **Multi-tiered Encoding Detection**: chardet, BOM detection, trial-and-error
- **Data Validation**: Structure validation and security checks
- **Header Classification**: Intelligent parsing of element vs. property columns
- **Performance Optimization**: Caching and row limit enforcement

### 3. SVG Processor (`modules/svg_processor.py`)

#### Class: `SVGProcessor`
Processes SVG templates and applies data transformations.

```python
class SVGProcessor:
    """SVG template processor for data-driven modifications."""
    
    def find_elements_by_name(self, svg_root, element_name: str) -> List:
        """Find SVG elements by their label/name."""
        
    def process_element_value(self, element, value: str, element_type: str):
        """Process element value replacement (text, images, etc.)."""
        
    def process_element_property(self, element, property_name: str, property_value: str):
        """Process element property modifications."""
```

#### Processing Pipeline
1. **Element Discovery**: XPath-based element finding
2. **Value Processing**: Text replacement, image substitution
3. **Property Modification**: Style changes, transformations
4. **Template Application**: Grouped operations for performance

### 4. File Exporter (`modules/file_exporter.py`)

#### Class: `FileExporter`
Handles multi-format file export and post-processing operations.

```python
class FileExporter:
    """Multi-format file exporter with PDF merging capabilities."""
    
    def export_file(self, svg_path: str, output_path: str, export_format: str, dpi: int):
        """Export SVG to specified format using Inkscape."""
        
    def merge_pdf_files(self, pdf_files: List[str], output_path: str):
        """Merge multiple PDF files into a single document."""
        
    def cleanup_temp_files(self):
        """Clean up temporary files and directories."""
```

#### Export Capabilities
- **Vector Formats**: SVG, PDF, EPS, PostScript
- **Raster Formats**: PNG, JPG, TIFF, WebP (72-1200 DPI)
- **PDF Operations**: Merging, individual file deletion
- **Temp Management**: Automatic cleanup

## 🛠️ Development Setup

### Prerequisites
- **Python** 3.7+
- **Inkscape** 1.0+ with development files
- **Git** for version control
- **Text Editor** or IDE (VS Code recommended)

### Environment Setup

#### 1. Clone Repository
```bash
git clone https://github.com/siddhasiddhant/InkAutoGen.git
cd InkAutoGen
```

#### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

#### 4. Setup Development Tools
```bash
# Pre-commit hooks
pip install pre-commit
pre-commit install

# Testing framework
pip install pytest pytest-cov pytest-mock

# Code quality
pip install flake8 black mypy
```

### IDE Configuration

#### VS Code Settings
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

## 📝 Code Organization

### File Structure Conventions

#### 1. Module Organization
```python
#!/usr/bin/env python3
"""
Module docstring explaining purpose and functionality.

Author: InkAutoGen Development Team
Version: 2.0.0
License: MIT
"""

# Standard library imports
import os
import sys
from typing import List, Dict, Optional, Tuple

# Third-party imports
import lxml.etree as ET

# Local imports
from .config import DEFAULT_SETTING
from .exceptions import InkAutoGenError
```

#### 2. Class Organization
```python
class ClassName:
    """
    Brief description of the class.
    
    Detailed description of functionality and usage.
    
    Attributes:
        attr1: Description of attribute
        attr2: Description of attribute
    
    Methods:
        method1: Description of method
        method2: Description of method
    """
    
    def __init__(self, param1: str, param2: Optional[int] = None):
        """Initialize the class with parameters."""
        self.attr1 = param1
        self.attr2 = param2 or DEFAULT_VALUE
```

#### 3. Method Organization
```python
def method_name(self, param1: str, param2: int) -> bool:
    """
    Brief description of the method.
    
    Args:
        param1: Description of parameter
        param2: Description of parameter
    
    Returns:
        Description of return value
    
    Raises:
        SpecificError: Description of when error occurs
    """
    # Implementation
    return result
```

### Coding Standards

#### 1. Naming Conventions
- **Classes**: `PascalCase` (e.g., `CSVReader`)
- **Methods/Functions**: `snake_case` (e.g., `process_element_value`)
- **Variables**: `snake_case` (e.g., `element_name`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_DPI`)
- **Private**: `_leading_underscore` (e.g., `_internal_method`)

#### 2. Type Hints
```python
from typing import List, Dict, Optional, Tuple, Union

def process_data(
    data: List[Dict[str, str]], 
    config: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    """Process data with optional configuration."""
    pass
```

#### 3. Error Handling
```python
try:
    result = risky_operation()
except SpecificError as e:
    self.logger.error(f"Specific error occurred: {e}")
    raise InkAutoGenError(f"Processing failed: {e}") from e
except Exception as e:
    self.logger.error(f"Unexpected error: {e}")
    raise InkAutoGenError("Unexpected processing error") from e
```

## 🔌 API Reference

### Core Interfaces

#### CSVReader Interface
```python
class CSVReaderInterface:
    """Interface for CSV data reading operations."""
    
    def read_csv_data(self, file_path: str) -> List[Dict[str, str]]:
        """Read CSV data with encoding detection."""
        pass
    
    def classify_csv_data(self, data: List[Dict[str, str]]) -> Dict[str, Any]:
        """Classify CSV headers and data."""
        pass
    
    def validate_csv_structure(self, data: List[Dict[str, str]]) -> bool:
        """Validate CSV data structure."""
        pass
```

#### SVGProcessor Interface
```python
class SVGProcessorInterface:
    """Interface for SVG processing operations."""
    
    def find_elements_by_name(self, svg_root, element_name: str) -> List:
        """Find elements by name/label."""
        pass
    
    def process_element_value(self, element, value: str, element_type: str):
        """Process element value replacement."""
        pass
    
    def process_element_property(self, element, property_name: str, property_value: str):
        """Process element property modification."""
        pass
```

#### FileExporter Interface
```python
class FileExporterInterface:
    """Interface for file export operations."""
    
    def export_file(self, svg_path: str, output_path: str, export_format: str, dpi: int):
        """Export file to specified format."""
        pass
    
    def merge_pdf_files(self, pdf_files: List[str], output_path: str):
        """Merge PDF files."""
        pass
```

### Configuration System

#### Config Module Structure
```python
# Default values
DEFAULT_DPI: int = 300
DEFAULT_EXPORT_FORMAT: str = "png"
DEFAULT_FILENAME_PATTERN: str = "output_{count}"

# Validation rules
SUPPORTED_EXPORT_FORMATS: Set[str] = {"png", "pdf", "svg", "jpg", "eps"}
ALLOWED_FILE_EXTENSIONS: Set[str] = {".svg", ".png", ".jpg", ".jpeg", ".pdf"}

# Performance settings
MAX_CSV_ROWS: int = 10000
CACHE_SIZE: int = 1000
TIMEOUT_SECONDS: int = 300
```

## 🚀 Extending the Extension

### Adding New Export Formats

#### 1. Update Configuration
```python
# modules/config.py
SUPPORTED_EXPORT_FORMATS.add("new_format")
DEFAULT_EXPORT_FORMAT_OPTIONS["new_format"] = {
    "extension": ".new_ext",
    "dpi_required": False,
    "vector": True
}
```

#### 2. Extend File Exporter
```python
# modules/file_exporter.py
def export_new_format(self, svg_path: str, output_path: str, **kwargs):
    """Export SVG to new format."""
    cmd = [
        "inkscape",
        "--export-type=new_format",
        f"--export-filename={output_path}",
        svg_path
    ]
    return self._execute_export_command(cmd)
```

#### 3. Update UI
```xml
<!-- inkautogen.inx -->
<option value="new_format">New Format (.new_ext)</option>
```

### Adding New Element Processors

#### 1. Create Processor Class
```python
# modules/element_processors/new_processor.py
class NewElementProcessor:
    """Processor for new element type."""
    
    def can_process(self, element) -> bool:
        """Check if element can be processed."""
        return element.tag == "new_element_tag"
    
    def process(self, element, value: str, context: Dict[str, Any]):
        """Process the element with new value."""
        # Implementation
        pass
```

#### 2. Register Processor
```python
# modules/svg_processor.py
from .element_processors.new_processor import NewElementProcessor

class SVGProcessor:
    def __init__(self):
        self.element_processors = [
            NewElementProcessor(),
            # ... other processors
        ]
```

### Adding New Validation Rules

#### 1. Extend Security Module
```python
# modules/security.py
def validate_new_feature(self, data: str) -> bool:
    """Validate new feature data."""
    dangerous_patterns = [
        r"dangerous_pattern",
        r"another_pattern"
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, data, re.IGNORECASE):
            return False
    
    return True
```

#### 2. Update Validation Pipeline
```python
# modules/csv_reader.py
def validate_data(self, data: Dict[str, str]) -> bool:
    """Validate all data using security rules."""
    if not self.security.validate_new_feature(data.get("new_field", "")):
        raise ValidationError("Invalid new feature data")
    
    return True
```

## 🧪 Testing and Debugging

### Testing Framework

#### 1. Unit Tests
```python
# tests/test_csv_reader.py
import pytest
from modules.csv_reader import CSVReader

class TestCSVReader:
    def setup_method(self):
        """Setup test fixtures."""
        self.reader = CSVReader()
    
    def test_read_csv_data_success(self):
        """Test successful CSV reading."""
        # Test implementation
        pass
    
    def test_read_csv_data_invalid_file(self):
        """Test handling of invalid CSV file."""
        # Test implementation
        pass
```

#### 2. Integration Tests
```python
# tests/test_integration.py
import pytest
from inkautogen import InkAutoGen

class TestIntegration:
    def test_full_workflow(self):
        """Test complete processing workflow."""
        # Test implementation
        pass
```

#### 3. Performance Tests
```python
# tests/test_performance.py
import time
import pytest
from modules.performance import PerformanceMonitor

class TestPerformance:
    def test_batch_processing_performance(self):
        """Test batch processing performance."""
        monitor = PerformanceMonitor()
        
        with monitor.timer("batch_processing"):
            # Process large batch
            pass
        
        assert monitor.get_duration("batch_processing") < 10.0
```

### Debugging Tools

#### 1. Logging Configuration
```python
# modules/utilities.py
def setup_debug_logging():
    """Setup detailed logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('debug.log'),
            logging.StreamHandler()
        ]
    )
```

#### 2. Debug Mode
```python
# inkautogen.py
def enable_debug_mode(self):
    """Enable debug mode with detailed logging."""
    self.debug = True
    setup_debug_logging()
    self.logger.setLevel(logging.DEBUG)
```

#### 3. Performance Profiling
```python
# modules/performance.py
import cProfile
import pstats

def profile_processing(func):
    """Decorator for profiling processing functions."""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = func(*args, **kwargs)
        
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)
        
        return result
    return wrapper
```

## ⚡ Performance Considerations

### Memory Management

#### 1. XML Tree Cleanup
```python
# modules/svg_processor.py
def cleanup_xml_tree(self, tree):
    """Clean up XML tree to free memory."""
    # Clear element references
    for element in tree.iter():
        element.clear()
    
    # Remove tree reference
    del tree
```

#### 2. Batch Processing
```python
# modules/csv_reader.py
def process_in_batches(self, data: List[Dict], batch_size: int = 100):
    """Process data in batches to manage memory."""
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        yield batch
```

### Caching Strategy

#### 1. Element Caching
```python
# modules/svg_processor.py
def cache_element_lookup(self, svg_root):
    """Cache element lookups for performance."""
    if not self._element_cache:
        self._element_cache = {}
        for element in svg_root.iter():
            label = element.get('id') or element.get('label')
            if label and label.startswith('<'):
                self._element_cache[label] = element
```

#### 2. File Caching
```python
# modules/file_exporter.py
def cache_exported_files(self, file_hash: str, file_path: str):
    """Cache exported files to avoid re-export."""
    self._file_cache[file_hash] = file_path
```

### Optimization Techniques

#### 1. Lazy Loading
```python
# modules/csv_reader.py
def lazy_load_csv(self, file_path: str):
    """Lazy load CSV data for large files."""
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield row
```

#### 2. Parallel Processing
```python
# modules/file_exporter.py
import concurrent.futures

def parallel_export(self, files_to_export: List[Tuple]):
    """Export files in parallel for better performance."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(self.export_file, *args)
            for args in files_to_export
        ]
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
```

## 🔒 Security Guidelines

### Input Validation

#### 1. File Path Validation
```python
# modules/security.py
def validate_file_path(self, file_path: str) -> bool:
    """Validate file path to prevent directory traversal."""
    # Normalize path
    normalized = os.path.normpath(file_path)
    
    # Check for directory traversal
    if '..' in normalized or normalized.startswith('/'):
        return False
    
    # Check allowed extensions
    allowed_extensions = {'.svg', '.png', '.jpg', '.csv'}
    if not any(normalized.endswith(ext) for ext in allowed_extensions):
        return False
    
    return True
```

#### 2. Content Sanitization
```python
# modules/security.py
def sanitize_svg_content(self, svg_content: str) -> str:
    """Sanitize SVG content to remove dangerous elements."""
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'data:text/html',
    ]
    
    sanitized = svg_content
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    return sanitized
```

### Error Handling

#### 1. Safe Error Messages
```python
# modules/exceptions.py
class InkAutoGenError(Exception):
    """Base exception for InkAutoGen errors."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message
```

#### 2. Logging Security
```python
# modules/utilities.py
def secure_log_message(self, message: str, data: Dict[str, Any]) -> str:
    """Create secure log message without sensitive data."""
    # Remove sensitive fields
    safe_data = {k: v for k, v in data.items() if k not in SENSITIVE_FIELDS}
    
    return f"{message} - Data: {safe_data}"
```

## 📚 Additional Resources

### Development Tools
- **Inkscape Documentation**: [https://inkscape.org/doc/](https://inkscape.org/doc/)
- **Python Extension Guide**: [Inkscape Python Extension Tutorial](https://inkscape.org/doc/inkscape-extension/tutorial/)
- **lxml Documentation**: [https://lxml.de/](https://lxml.de/)

### Best Practices
- **Code Style**: PEP 8 compliance with Black formatting
- **Testing**: pytest with coverage reporting
- **Documentation**: docstrings following Google style
- **Version Control**: Git with conventional commits

### Community Resources
- **GitHub Issues**: [Project Issues](https://github.com/siddhasiddhant/InkAutoGen/issues)
- **Discussions**: [GitHub Discussions](https://github.com/siddhasiddhant/InkAutoGen/discussions)
- **Wiki**: [Project Wiki](https://github.com/siddhasiddhant/InkAutoGen/wiki)

---

**Happy coding!** 🚀✨