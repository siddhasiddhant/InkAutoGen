# InkAutoGen API Reference

## 📚 Table of Contents

1. [Core Modules](#core-modules)
2. [CSV Reader API](#csv-reader-api)
3. [SVG Processor API](#svg-processor-api)
4. [File Exporter API](#file-exporter-api)
5. [Utilities API](#utilities-api)
6. [Security API](#security-api)
7. [Configuration API](#configuration-api)
8. [Exceptions API](#exceptions-api)
9. [Performance API](#performance-api)

## 🔧 Core Modules

### Main Extension (`inkautogen.py`)

#### Class: `InkAutoGen`
The main orchestrator class that coordinates all processing modules.

```python
class InkAutoGen(Effect):
    """Main Inkscape extension class for batch SVG processing."""
    
    def __init__(self):
        """Initialize the extension with default parameters."""
        
    def effect(self):
        """Main processing method called by Inkscape."""
        
    def process_batch(self) -> bool:
        """Process all CSV rows and generate output files."""
        
    def setup_logging(self) -> None:
        """Setup logging configuration."""
        
    def validate_arguments(self) -> bool:
        """Validate command-line arguments."""
```

**Key Methods:**
- `effect()`: Main entry point called by Inkscape
- `process_batch()`: Orchestrates the complete processing workflow
- `setup_logging()`: Configures logging based on user preferences

## 📊 CSV Reader API

### Class: `CSVReader`
Handles CSV data import with automatic encoding detection and validation.

```python
class CSVReader:
    """CSV data reader with encoding detection and validation."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize CSV reader with optional logger."""
        
    def read_csv_data(self, file_path: str) -> List[Dict[str, str]]:
        """Read CSV data with automatic encoding detection."""
        
    def classify_csv_data(self, data: List[Dict[str, str]]) -> Dict[str, Any]:
        """Classify CSV headers into element values and properties."""
        
    def filter_rows_by_range(self, data: List[Dict[str, str]], row_range: str) -> List[Dict[str, str]]:
        """Filter CSV rows by specified range."""
        
    def validate_csv_structure(self, data: List[Dict[str, str]]) -> bool:
        """Validate CSV data structure and content."""
        
    def detect_encoding(self, file_path: str) -> str:
        """Detect file encoding using multiple methods."""
        
    def filter_csv_data_by_missing_elements(self, data: List[Dict[str, str]], missing_elements: List[str]) -> Tuple[List[Dict[str, str]], List[str]]:
        """Filter CSV data and return removed columns."""
```

#### Method Details

##### `read_csv_data(file_path: str) -> List[Dict[str, str]]`
Reads CSV data with automatic encoding detection.

**Parameters:**
- `file_path`: Path to CSV file

**Returns:**
- List of dictionaries representing CSV rows

**Raises:**
- `CSVParsingError`: If CSV cannot be parsed
- `FileNotFoundError`: If file doesn't exist

**Example:**
```python
reader = CSVReader()
data = reader.read_csv_data("data.csv")
print(f"Loaded {len(data)} rows")
```

##### `classify_csv_data(data: List[Dict[str, str]]) -> Dict[str, Any]`
Classifies CSV headers into element values and properties.

**Parameters:**
- `data`: CSV data as list of dictionaries

**Returns:**
- Dictionary with classification results:
  - `element_values`: Headers for element replacement
  - `properties`: Headers for property modification
  - `layer_visibility`: Headers for layer visibility control

**Example:**
```python
classification = reader.classify_csv_data(data)
print(f"Element values: {len(classification['element_values'])}")
print(f"Properties: {len(classification['properties'])}")
```

##### `filter_rows_by_range(data: List[Dict[str, str]], row_range: str) -> List[Dict[str, str]]`
Filters CSV rows by specified range.

**Parameters:**
- `data`: Original CSV data
- `row_range`: Range string (e.g., "1-10", "5,8,12", "even")

**Returns:**
- Filtered CSV data

**Example:**
```python
filtered = reader.filter_rows_by_range(data, "1-10")
print(f"Filtered to {len(filtered)} rows")
```

## 🎨 SVG Processor API

### Class: `SVGProcessor`
Processes SVG templates and applies data transformations.

```python
class SVGProcessor:
    """SVG template processor for data-driven modifications."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize SVG processor with optional logger."""
        
    def find_elements_by_name(self, svg_root, element_name: str) -> List:
        """Find SVG elements by their label/name."""
        
    def process_element_value(self, element, value: str, element_type: str) -> None:
        """Process element value replacement (text, images, etc.)."""
        
    def process_element_property(self, element, property_name: str, property_value: str) -> None:
        """Process element property modifications."""
        
    def apply_layer_visibility(self, svg_root, layer_data: Dict[str, bool]) -> None:
        """Apply layer visibility based on CSV data."""
        
    def export_svg_to_csv(self, svg_path: str) -> List[Dict[str, str]]:
        """Export SVG elements to CSV template format."""
        
    def validate_svg_structure(self, svg_root) -> bool:
        """Validate SVG template structure."""
```

#### Method Details

##### `find_elements_by_name(svg_root, element_name: str) -> List`
Finds SVG elements by their label/name.

**Parameters:**
- `svg_root`: Root element of SVG document
- `element_name`: Element name to search for (e.g., "<name>")

**Returns:**
- List of matching SVG elements

**Example:**
```python
elements = processor.find_elements_by_name(svg_root, "<name>")
print(f"Found {len(elements)} elements")
```

##### `process_element_value(element, value: str, element_type: str) -> None`
Processes element value replacement.

**Parameters:**
- `element`: SVG element to modify
- `value`: New value to apply
- `element_type`: Type of element ("text", "image", etc.)

**Example:**
```python
processor.process_element_value(text_element, "John Doe", "text")
```

##### `process_element_property(element, property_name: str, property_value: str) -> None`
Processes element property modifications.

**Parameters:**
- `element`: SVG element to modify
- `property_name`: Property to modify (e.g., "fill", "font-size")
- `property_value`: New property value

**Example:**
```python
processor.process_element_property(element, "fill", "#ff0000")
```

## 📁 File Exporter API

### Class: `FileExporter`
Handles multi-format file export and post-processing operations.

```python
class FileExporter:
    """Multi-format file exporter with PDF merging capabilities."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize file exporter with optional logger."""
        
    def export_file(self, svg_path: str, output_path: str, export_format: str, dpi: int = 300) -> bool:
        """Export SVG to specified format using Inkscape."""
        
    def merge_pdf_files(self, pdf_files: List[str], output_path: str) -> bool:
        """Merge multiple PDF files into a single document."""
        
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files and directories."""
        
    def validate_export_path(self, output_path: str) -> bool:
        """Validate output path for security and permissions."""
        
    def get_supported_formats(self) -> Set[str]:
        """Get list of supported export formats."""
```

#### Method Details

##### `export_file(svg_path: str, output_path: str, export_format: str, dpi: int = 300) -> bool`
Exports SVG file to specified format.

**Parameters:**
- `svg_path`: Path to source SVG file
- `output_path`: Path for output file
- `export_format`: Target format ("png", "pdf", "svg", etc.)
- `dpi`: Resolution for raster formats (default: 300)

**Returns:**
- True if export successful, False otherwise

**Example:**
```python
exporter = FileExporter()
success = exporter.export_file("template.svg", "output.png", "png", dpi=300)
```

##### `merge_pdf_files(pdf_files: List[str], output_path: str) -> bool`
Merges multiple PDF files into a single document.

**Parameters:**
- `pdf_files`: List of PDF file paths to merge
- `output_path`: Path for merged PDF output

**Returns:**
- True if merge successful, False otherwise

**Example:**
```python
pdf_files = ["file1.pdf", "file2.pdf", "file3.pdf"]
success = exporter.merge_pdf_files(pdf_files, "merged.pdf")
```

## 🛠️ Utilities API

### Module: `utilities`
Helper functions for common operations.

```python
def generate_filename(pattern: str, csv_data: Dict[str, str], count: int) -> str:
    """Generate filename using pattern and CSV data."""

def create_xpath_query(element_name: str) -> str:
    """Create XPath query for finding elements by name."""

def parse_css_property(property_string: str) -> Dict[str, str]:
    """Parse CSS property string into dictionary."""

def setup_logging(log_level: str = "INFO", enable_timestamps: bool = False) -> logging.Logger:
    """Setup logging configuration."""

def validate_filename_pattern(pattern: str) -> bool:
    """Validate filename pattern for security."""

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""

def get_available_memory() -> int:
    """Get available system memory in bytes."""
```

#### Function Details

##### `generate_filename(pattern: str, csv_data: Dict[str, str], count: int) -> str`
Generates filename using pattern substitution.

**Parameters:**
- `pattern`: Filename pattern with placeholders
- `csv_data`: CSV row data for substitution
- `count`: Sequential count for this file

**Returns:**
- Generated filename string

**Example:**
```python
filename = generate_filename(
    "certificate_{name}_{count}.png",
    {"name": "John Doe"},
    1
)
# Result: "certificate_John_Doe_1.png"
```

##### `create_xpath_query(element_name: str) -> str`
Creates XPath query for finding elements.

**Parameters:**
- `element_name`: Element name to search for

**Returns:**
- XPath query string

**Example:**
```python
query = create_xpath_query("<name>")
# Result: "//*[@id='name' or @label='name']"
```

## 🔒 Security API

### Class: `SecurityValidator`
Handles security validation and sanitization.

```python
class SecurityValidator:
    """Security validator for file operations and content."""
    
    def __init__(self):
        """Initialize security validator."""
        
    def validate_file_path(self, file_path: str) -> bool:
        """Validate file path to prevent directory traversal."""
        
    def sanitize_svg_content(self, svg_content: str) -> str:
        """Sanitize SVG content to remove dangerous elements."""
        
    def validate_csv_data(self, data: Dict[str, str]) -> bool:
        """Validate CSV data for security issues."""
        
    def check_file_extension(self, file_path: str, allowed_extensions: Set[str]) -> bool:
        """Check if file extension is allowed."""
        
    def scan_for_malicious_patterns(self, content: str) -> bool:
        """Scan content for malicious patterns."""
```

#### Method Details

##### `validate_file_path(file_path: str) -> bool`
Validates file path for security.

**Parameters:**
- `file_path`: File path to validate

**Returns:**
- True if path is safe, False otherwise

**Example:**
```python
validator = SecurityValidator()
is_safe = validator.validate_file_path("data.csv")
```

##### `sanitize_svg_content(svg_content: str) -> str`
Sanitizes SVG content to remove dangerous elements.

**Parameters:**
- `svg_content`: Raw SVG content

**Returns:**
- Sanitized SVG content

**Example:**
```python
clean_svg = validator.sanitize_svg_content(malicious_svg)
```

## ⚙️ Configuration API

### Module: `config`
Configuration constants and settings.

```python
# Default Configuration
DEFAULT_DPI: int = 300
DEFAULT_EXPORT_FORMAT: str = "png"
DEFAULT_FILENAME_PATTERN: str = "output_{count}"
DEFAULT_OVERWRITE: bool = True
DEFAULT_LOGGING: bool = False
DEFAULT_CSV_ENCODING: str = "autodetect"

# Supported Formats
SUPPORTED_EXPORT_FORMATS: Set[str] = {"png", "pdf", "svg", "jpg", "jpeg", "eps", "tiff", "webp"}
ALLOWED_FILE_EXTENSIONS: Set[str] = {".svg", ".png", ".jpg", ".jpeg", ".pdf", ".eps", ".tiff", ".webp", ".csv"}

# Performance Settings
MAX_CSV_ROWS: int = 10000
CACHE_SIZE: int = 1000
TIMEOUT_SECONDS: int = 300

# Validation Rules
MAX_FILENAME_LENGTH: int = 255
MAX_FILE_SIZE_MB: int = 100
MIN_DPI: int = 72
MAX_DPI: int = 1200
```

#### Configuration Functions

```python
def get_default_config() -> Dict[str, Any]:
    """Get default configuration dictionary."""

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration settings."""

def get_supported_formats() -> Set[str]:
    """Get set of supported export formats."""

def get_format_info(format_name: str) -> Dict[str, Any]:
    """Get information about specific export format."""
```

## ⚠️ Exceptions API

### Exception Classes
Custom exception classes for error handling.

```python
class InkAutoGenError(Exception):
    """Base exception for InkAutoGen errors."""

class CSVParsingError(InkAutoGenError):
    """Exception raised when CSV parsing fails."""

class SVGProcessingError(InkAutoGenError):
    """Exception raised when SVG processing fails."""

class FileExportError(InkAutoGenError):
    """Exception raised when file export fails."""

class SecurityError(InkAutoGenError):
    """Exception raised for security violations."""

class ValidationError(InkAutoGenError):
    """Exception raised when validation fails."""

class PerformanceError(InkAutoGenError):
    """Exception raised for performance issues."""
```

#### Exception Usage

```python
try:
    reader = CSVReader()
    data = reader.read_csv_data("data.csv")
except CSVParsingError as e:
    logger.error(f"CSV parsing failed: {e}")
    # Handle error
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    # Handle error
```

## 📊 Performance API

### Class: `PerformanceMonitor`
Monitors and tracks performance metrics.

```python
class PerformanceMonitor:
    """Performance monitoring and tracking."""
    
    def __init__(self):
        """Initialize performance monitor."""
        
    def start_timer(self, operation_name: str) -> None:
        """Start timing an operation."""
        
    def end_timer(self, operation_name: str) -> float:
        """End timing and return duration."""
        
    def get_duration(self, operation_name: str) -> float:
        """Get duration of completed operation."""
        
    def track_memory_usage(self, operation_name: str) -> None:
        """Track memory usage for operation."""
        
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        
    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
```

#### Method Details

##### `start_timer(operation_name: str) -> None`
Starts timing an operation.

**Parameters:**
- `operation_name`: Name of operation to time

**Example:**
```python
monitor = PerformanceMonitor()
monitor.start_timer("csv_reading")
# ... perform operation
duration = monitor.end_timer("csv_reading")
```

##### `get_performance_report() -> Dict[str, Any]`
Gets comprehensive performance report.

**Returns:**
- Dictionary containing all performance metrics

**Example:**
```python
report = monitor.get_performance_report()
print(f"Total operations: {len(report['operations'])}")
print(f"Total time: {report['total_time']:.2f}s")
```

## 🔄 Integration Examples

### Complete Workflow Example
```python
from inkautogen import InkAutoGen
from modules.csv_reader import CSVReader
from modules.svg_processor import SVGProcessor
from modules.file_exporter import FileExporter

# Initialize components
csv_reader = CSVReader()
svg_processor = SVGProcessor()
file_exporter = FileExporter()

# Read CSV data
try:
    csv_data = csv_reader.read_csv_data("data.csv")
    classified_data = csv_reader.classify_csv_data(csv_data)
except CSVParsingError as e:
    print(f"CSV error: {e}")
    return

# Load SVG template
svg_tree = ET.parse("template.svg")
svg_root = svg_tree.getroot()

# Process each row
for i, row in enumerate(csv_data):
    # Create fresh copy of template
    svg_copy = deepcopy(svg_root)
    
    # Process element values
    for element_name in classified_data['element_values']:
        if element_name in row:
            elements = svg_processor.find_elements_by_name(svg_copy, element_name)
            for element in elements:
                svg_processor.process_element_value(element, row[element_name], "text")
    
    # Process properties
    for property_name in classified_data['properties']:
        if property_name in row:
            element_name, prop = property_name.split('##')
            elements = svg_processor.find_elements_by_name(svg_copy, element_name)
            for element in elements:
                svg_processor.process_element_property(element, prop, row[property_name])
    
    # Export file
    filename = generate_filename("output_{count}.png", row, i + 1)
    temp_svg_path = f"temp_{i}.svg"
    
    # Save temporary SVG
    temp_tree = ET.ElementTree(svg_copy)
    temp_tree.write(temp_svg_path)
    
    # Export to final format
    file_exporter.export_file(temp_svg_path, filename, "png", dpi=300)
    
    # Cleanup
    os.remove(temp_svg_path)

print("Processing complete!")
```

### Error Handling Example
```python
from modules.exceptions import *
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_with_error_handling(csv_path: str, svg_path: str, output_dir: str):
    """Process files with comprehensive error handling."""
    try:
        # Initialize components
        reader = CSVReader(logger)
        processor = SVGProcessor(logger)
        exporter = FileExporter(logger)
        
        # Validate inputs
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        if not os.path.exists(svg_path):
            raise FileNotFoundError(f"SVG file not found: {svg_path}")
        
        # Process data
        data = reader.read_csv_data(csv_path)
        
        if not data:
            raise ValidationError("CSV file is empty")
        
        # Continue processing...
        return True
        
    except CSVParsingError as e:
        logger.error(f"CSV parsing failed: {e}")
        return False
    except SVGProcessingError as e:
        logger.error(f"SVG processing failed: {e}")
        return False
    except FileExportError as e:
        logger.error(f"File export failed: {e}")
        return False
    except SecurityError as e:
        logger.error(f"Security violation: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
```

---

**For more detailed information, see the individual module documentation and test files.** 📚✨