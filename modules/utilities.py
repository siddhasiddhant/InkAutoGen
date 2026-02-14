#!/usr/bin/env python3
"""
InkAutoGen Common Utility Module

This module provides general-purpose reusable functions for common patterns, utility functions used across the InkAutoGen extension.
These utilities include filename generation, XML/SVG processing, and string manipulation to reduce duplication and improve maintainability.

Key Functions:
    - generate_output_filename: Generate filenames from patterns with CSV value replacement
    - sanitize_filename: Sanitize filenames for cross-platform compatibility

    - xpath_query: Standardized XPath queries with namespace handling
    - get_element_attributes: Extract common SVG element attributes
    - log_element_change: Consistent logging format for element changes
    - safe_execute: Error handling with consistent logging
    - update_svg_style_property: Update CSS properties in SVG elements
    - validate_required_value: Validate input values consistently
    - clean_string: String cleaning and validation

Author: InkAutoGen Development Team
Version: 1.0.0
"""

import sys
import os
import re
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any, Callable, Tuple, Iterator

import config
import utilities

def setup_logging(output_path: str, enable_logging: bool, log_level: str = "INFO"
                    , disable_log_timestamps: bool = False) -> Optional[logging.Logger]:
    """
    Setup logging to file if enabled by user.
    
    This method configures file-based logging for debugging and monitoring
    purposes. Log files are created in the output directory and contain
    detailed information about the processing workflow.
    
    Args:
        output_path: Directory where log file will be created
        enable_logging: Whether to enable logging (True) or disable (False)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        disable_log_timestamps: Whether to disable date/time stamps in log entries (True) or keep them (False)
    
    Returns:
        Logger instance if logging is enabled, None otherwise
    
    Log File Details:
        - Location: {output_path}/inkautogen.log
        - Mode: Overwrite (mode='w') - new log for each run
        - Level: DEBUG (most verbose)
        - Format: With timestamps: %(asctime)s - %(levelname)s - %(message)s
        - Format: Without timestamps: %(levelname)s - %(message)s
        - Handlers: File handler + console handler (INFO level)
    
    Implementation Notes:
        - Uses named logger 'InkAutoGen' instead of root logger
        - Adds handlers directly to logger (not using basicConfig)
        - Prevents propagation to root logger to avoid conflicts
        - Removes existing handlers to prevent duplicates on re-runs
        - Custom formatter based on disable_log_timestamps preference
    
    Log Content Includes:
        - Configuration parameters
        - CSV reading status and row count
        - Template processing statistics
        - File export status
        - Error messages and stack traces
        - Summary statistics
    
    Examples:
        >>> logger = setup_logging("/tmp", True)  # With timestamps
        >>> logger.info("Processing started")
        # Log entry: 2024-01-25 14:30:15 - INFO - Processing started
        
        >>> logger = setup_logging("/tmp", True, "INFO", True)  # Without timestamps
        >>> logger.info("Processing started")
        # Log entry: INFO - Processing started
        
        # Log file created at /tmp/inkautogen.log
    """
    if not enable_logging:
        # Logging disabled
        return None
    
    log_file = os.path.join(output_path, config.LOG_FILENAME)
    
    try:
        # Create a specific logger for this extension (not root logger)
        logger = logging.getLogger('InkAutoGen')
        
        # Set log level based on user selection
        logger.setLevel(config.LOG_LEVELS.get(log_level.upper(), logging.INFO))
        
        # Remove any existing handlers to avoid duplicates
        if logger.handlers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
        
        # Create custom formatter based on timestamp preference
        if disable_log_timestamps:
            # Formatter without timestamps for cleaner output
            custom_format = config.LOG_DEFAULT_FORMAT
        else:
            # Use default format with timestamps
            custom_format = config.LOG_TIMESTAMPS_FORMAT
        
        # Create file handler
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(config.LOG_LEVELS.get(log_level.upper(), logging.INFO))
        file_handler.setFormatter(logging.Formatter(custom_format))
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        # Also add console handler for visibility
        '''
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(custom_format))
        logger.addHandler(console_handler)
        '''
        # Prevent propagation to root logger to avoid duplicate logs
        logger.propagate = False
        
        # Log session start information
        logger.info("=" * 80)
        logger.info("InkAutoGen Extension Started")
        logger.info(f"Log file: {log_file}")
        logger.info("=" * 80)
        
        return logger
    except Exception as e:
        error_msg = f"Warning: Failed to setup logging: {e}"
        print(f"Warning: {error_msg}", file=sys.stderr)
        return None

def generate_output_filename(filename_pattern: str, idx: int, row: Dict[str, str], removed_row: Dict[str, str]
                             ,logger: Optional[logging.Logger] = None, total_rows: int = 1) -> str:
    """
    Generate output filename from pattern with support for new placeholder formats.

    This method supports filename generation with multiple placeholder types:

    New Placeholders:
    - {count} - iteration counter (1-based)
    - {count:digit} - zero-padded counter based on total rows
    - {date} - system date in default format (yyyymmdd)
    - {date:format} - system date in custom format (e.g., dd-MMM-yyyy)
    - {time} - system time in hhmmss format
    - %csv_header_name% - CSV column value replacement

    Args:
        filename_pattern: User-specified filename pattern
        idx: Current iteration index (0-based)
        row: Current CSV row dict with column values
        logger: Optional logger instance for debugging
        total_rows: Total number of rows for digit formatting

    Returns:
        Generated filename with all placeholders replaced and sanitized

    Examples:
        >>> generate_output_filename("output_{count}", 0, {}, total_rows=100)
        'output_001'
        >>> generate_output_filename("doc_{date:dd-MMM-yyyy}", 0, {})
        'doc_24-Jan-2026'
        >>> generate_output_filename("invoice_%InvoiceNumber%", 0, {"InvoiceNumber": "INV-001"})
        'invoice_INV-001'
    """

    if logger:
        logger.debug(f"Generating filename from pattern: {filename_pattern}")
        logger.debug(f"  Index: {idx}, Total rows: {total_rows}")

    # Step 1: Replace {count} and {count:digit} placeholders
    count_pattern = re.compile(config.FILENAME_PATTERNS['count'])
    count_matches = list(count_pattern.finditer(filename_pattern))
    
    for match in count_matches:
        digit_format = match.group(1)  # None for {count}, digit for {count:3}
        count_value = idx + 1  # Convert to 1-based
        
        if digit_format:
            # Zero-pad based on specified digits or total rows
            try:
                num_digits = int(digit_format)
                count_str = str(count_value).zfill(num_digits)
            except ValueError:
                # Invalid digit format, use total rows-based padding
                num_digits = len(str(total_rows))
                count_str = str(count_value).zfill(num_digits)
        else:
            count_str = str(count_value)
        
        filename_pattern = filename_pattern.replace(match.group(0), count_str)
        if logger:
            logger.debug(f"Replaced {match.group(0)} with: {count_str}")

    # Step 2: Replace {date} and {date:format} placeholders
    date_pattern = re.compile(config.FILENAME_PATTERNS['date'])
    date_matches = list(date_pattern.finditer(filename_pattern))
    
    for match in date_matches:
        date_format = match.group(1) or config.DEFAULT_DATE_FORMAT
        current_date = datetime.now()
        
        # Convert Python format to strftime format
        if date_format == 'yyyymmdd':
            strftime_format = '%Y%m%d'
        elif date_format == 'dd-MMM-yyyy':
            strftime_format = '%d-%b-%Y'
        elif date_format == 'MMM-dd-yyyy':
            strftime_format = '%b-%d-%Y'
        elif date_format == 'yyyy-mm-dd':
            strftime_format = '%Y-%m-%d'
        elif date_format == 'dd/mm/yyyy':
            strftime_format = '%d/%m/%Y'
        elif date_format == 'mm/dd/yyyy':
            strftime_format = '%m/%d/%Y'
        else:
            # Use as-is if it's a valid strftime format
            strftime_format = date_format
        
        try:
            formatted_date = current_date.strftime(strftime_format)
        except ValueError:
            # Invalid format, fallback to default
            formatted_date = current_date.strftime('%Y%m%d')
            if logger:
                logger.warning(f"Invalid date format '{date_format}', using default yyyymmdd")
        
        filename_pattern = filename_pattern.replace(match.group(0), formatted_date)
        if logger:
            logger.debug(f"Replaced {match.group(0)} with: {formatted_date}")

    # Step 3: Replace {time} placeholder
    if '{time}' in filename_pattern:
        current_time = datetime.now()
        formatted_time = current_time.strftime('%H%M%S')
        filename_pattern = filename_pattern.replace('{time}', formatted_time)
        if logger:
            logger.debug(f"Replaced {{time}} with: {formatted_time}")

    # Step 4: Replace %csv_header_name% placeholders
    csv_pattern = re.compile(config.FILENAME_PATTERNS['csv_column'])
    csv_matches = list(csv_pattern.finditer(filename_pattern))
    
    for match in csv_matches:
        column_name = match.group(1)
        full_match = match.group(0)
        
        if column_name in row:
            value = str(row[column_name])
            filename_pattern = filename_pattern.replace(full_match, value)
            if logger:
                logger.debug(f"Replaced %{column_name}% with: {value}")
        elif removed_row and column_name in removed_row:
            value = str(removed_row[column_name])
            filename_pattern = filename_pattern.replace(full_match, value)
            if logger:
                logger.debug(f"Replaced %{column_name}% with: {value} : data from non svg column")
        else:
            if logger:
                logger.debug(f"CSV column '{column_name}' not found in row")
            # Replace with empty string if column not found
            filename_pattern = filename_pattern.replace(full_match, '')

    # Step 5: Sanitize filename
    filename = sanitize_filename(filename_pattern)

    if logger:
        logger.debug(f"Generated filename: {filename}")

    return filename


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for cross-platform compatibility.

    This function performs following operations:
    - Replaces ampersand (&) characters with underscore
    - Replaces spaces with underscores (collapses multiple spaces)
    - Removes unpaired % signs
    - Replaces characters not allowed in filenames on most OS: <>:"/\\|?*#
    - Removes control characters (0x00-0x1f, 0x7f-0x9f)
    - Trims whitespace and underscores from beginning and end

    Args:
        filename: Input filename to sanitize

    Returns:
        Sanitized filename safe for all major operating systems

    Examples:
        >>> sanitize_filename("Hello World.txt")
        'Hello_World.txt'
        >>> sanitize_filename("  file  ")
        'file'
        >>> sanitize_filename("_filename_")
        'filename'
        >>> sanitize_filename("file<name>.txt")
        'file_name_.txt'
        >>> sanitize_filename("file\\path/name.txt")
        'file_path_name.txt'
        >>> sanitize_filename("file  name.pdf")
        'file_name.pdf'
        >>> sanitize_filename("test&value")
        'test_value'
        >>> sanitize_filename("invoice#123")
        'invoice_123'
        >>> sanitize_filename("file%name")
        'filename'
        >>> sanitize_filename("file%%name")
        'file___name'
    """
    # Replace ampersand characters with underscore
    #filename = filename.replace('&', '_')

    # Replace one or more whitespace (space, tab, newline) with single underscore
    # Note: Don't use \s as it matches control characters
    filename = re.sub(r'[ \t\r\n]+', '_', filename)

    # Replace characters not allowed in filenames on most OS
    filename = re.sub(r'[<>:"/\\|?*%&$@#]', '_', filename)

    # Remove control characters (0x00-0x1f, 0x7f-0x9f)
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)

    # Trim whitespace and underscores from ends
    filename = filename.strip().strip('_')

    return filename


def find_file(filename: str, search_dir: str, output_dir: str, logger: Optional[logging.Logger] = None) -> Optional[Dict[str, str]]:
    """
    Search for a file in directory and its subdirectories.

    This method searches recursively for an file with the given filename.
    If the filename contains path separators, it is returned as-is (assumed to be correct).
    If search_dir is provided, it searches from that directory. Otherwise, uses csv_dir.

    The search includes:
    1. Specified search directory (or csv_dir)
    2. Current working directory as fallback

    Args:
        filename: filename to search for (e.g., "logo.png", "images/photo.png")
        search_dir: Optional directory to search from.

    Returns:
        Dictionary with 'absolute' and 'relative' keys containing paths, or None if not found.

    Example:
        >>> processor = SVGElementProcessor(csv_dir="/path/to/project")
        >>> result = processor.find_file("logo.png")
        >>> result['absolute']
        '/path/to/project/logo.png'
        >>> result['relative']
        'logo.png'
        >>> result = processor.find_file("logo.png", search_dir="/path/to/project/assets")
        >>> result['relative']
        'assets/logo.png'
    """
    if logger:
        logger.debug(f"Searching for file '{filename}'...")

    # If filename contains path separator, return as-is with both paths
    if os.path.sep in filename or '/' in filename:
        if os.path.isabs(filename):
            abs_path = filename
            rel_path = filename
        else:
            abs_path = os.path.abspath(filename)
            rel_path = filename
        return {'absolute': abs_path, 'relative': rel_path}

    # Determine search directories (csv_dir and current working directory)
    search_dirs = []

    # Primary search directory
    base_dir = search_dir
    if logger:
        logger.debug(f"Searching for file '{filename}' starting from directory: {base_dir}")

    if base_dir and os.path.isdir(base_dir):
        search_dirs.append(base_dir)
        if logger:
            logger.debug(f"Searching for file '{filename}' in: {base_dir}")

    # Fallback: current working directory
    cwd = os.getcwd()
    if cwd != base_dir and os.path.isdir(cwd):
        search_dirs.append(cwd)
        if logger:
            logger.debug(f"Also searching in current directory: {cwd}")

    # Search for file in all directories
    for search_base_dir in search_dirs:
        for root, dirs, files in os.walk(search_base_dir):
            if filename in files:
                found_path = os.path.join(root, filename)

                # Calculate relative path from the search directory
                try:
                        #rel_path = os.path.relpath(found_path, search_base_dir)
                        rel_path = os.path.relpath(found_path, output_dir)
                except ValueError:
                    # Different drives on Windows, use absolute path
                    rel_path = found_path

                if logger:
                    logger.debug(f"Found file at: {found_path}")
                    logger.debug(f"Relative path with respective to output path: {rel_path}")
                    
                return {'absolute': found_path, 'relative': rel_path}

    if logger:
        logger.warning(f"File not found in any search directory: {filename}")

    return None

def convert_color_to_hex(color_value: str, logger: Optional[logging.Logger] = None) -> str:
    """
    Convert color alias name to hex value using COLOR_ALIASES map.
    
    Args:
        color_value: Color value from CSV (could be name, hex, rgb, etc.)
    
    Returns:
        Hex color value if alias found, original value otherwise
    
    Example:
        >>> convert_color_to_hex("red")
        '#ff0000'
        >>> convert_color_to_hex("#00ff00")
        '#00ff00'
        >>> convert_color_to_hex("rgb(255,0,0)")
        'rgb(255,0,0)'
    """
    # If already hex or complex format, return as-is
    if not color_value:
        if logger:
            logger.debug("No color value provided, returning as-is.")
        return color_value
    
    color_value = str(color_value).strip()
    
    # Check if it's a hex color
    if color_value.startswith('#') and len(color_value) in [4, 7]:
        if logger:
            logger.debug(f"Color value '{color_value}' is already in hex format.")
        return color_value
    
    # Check if it's rgb/rgba/hsl format
    if color_value.lower().startswith(('rgb', 'rgba', 'hsl', 'hsla')):
        if logger:
            logger.debug(f"Color value '{color_value}' is in complex format, returning as-is.")
        return color_value
    
    # Check color aliases
    color_lower = color_value.lower()
    if color_lower in config.COLOR_ALIASES:
        hex_value = config.COLOR_ALIASES[color_lower]
        if logger:
            logger.debug(f"Converted color alias '{color_value}' to hex value '{hex_value}'.")
        return hex_value
    
    if logger:
        logger.debug(f"No alias found for color '{color_value}', returning original value.")
        
    # Return original if not an alias
    return color_value


def is_valid_color(value: str, logger: Optional[logging.Logger] = None) -> bool:
    """
    Validate if value is a valid color.
    
    Args:
        value: Color value to validate
    
    Returns:
        True if valid color, False otherwise
    """
    if not value:
        return False
    
    value = str(value).strip()
    
    # Check hex color
    if value.startswith('#') and len(value) in [4, 7]:
        return True
    
    # Check if it's a color alias (including those in COLOR_ALIASES)
    color_aliases = list(config.COLOR_ALIASES.keys())
    if value.lower() in color_aliases:
        return True
    
    # Check rgb/rgba
    if value.startswith('rgb') and value.endswith(')'):
        return True
    
    # Check hsl/hsla
    if value.startswith('hsl') and value.endswith(')'):
        return True
    
    return False


def parse_style(style_string: str) -> Dict[str, str]:
    """
    Parse CSS style string into dictionary.
    
    Args:
        style_string: CSS style attribute value (e.g., "fill:red;stroke:blue;display:none")
    
    Returns:
        Dictionary of property-value pairs
    
    Examples:
        >>> parse_style("fill:red;stroke:blue")
        {'fill': 'red', 'stroke': 'blue'}
        >>> parse_style("display:none; font-size:16px")
        {'display': 'none', 'font-size': '16px'}
    """
    if not style_string:
        return {}
    
    styles = {}
    for declaration in style_string.split(';'):
        declaration = declaration.strip()
        if ':' in declaration:
            property_name, value = declaration.split(':', 1)
            styles[property_name.strip()] = value.strip()
    
    return styles


def format_style(style_dict: Dict[str, str]) -> str:
    """
    Format dictionary of CSS properties into style string.
    
    Args:
        style_dict: Dictionary of property-value pairs
    
    Returns:
        CSS style string (e.g., "fill:red;stroke:blue;display:none")
    
    Examples:
        >>> format_style({'fill': 'red', 'stroke': 'blue'})
        'fill:red;stroke:blue'
        >>> format_style({'display': 'none', 'font-size': '16px'})
        'display:none;font-size:16px'
    """
    if not style_dict:
        return ""
    
    return ';'.join(f"{prop}:{value}" for prop, value in style_dict.items())


def xpath_query(svg_root, expression_key: str, name: str = None, **kwargs) -> List[Any]:
    """
    Execute XPath query with common namespace handling.
    
    Provides consistent XPath query execution with proper namespace handling
    and supports parameterized expressions.
    
    Args:
        svg_root: XML/SVG root element
        expression_key: Key for XPath expression template
        name: Variable name to substitute in expression (optional)
        **kwargs: Additional parameters for expression formatting
        
    Returns:
        List of matching elements
        
    Example:
        >>> elements = xpath_query(svg_root, "labeled_elements", name="MyBox")
        >>> elements = xpath_query(svg_root, "shape_element_base", shape_type="rect")
    """
    if expression_key not in config.COMMON_XPATH_EXPRESSIONS:
        raise ValueError(f"Unknown XPath expression key: {expression_key}")
    
    xpath_expr = config.COMMON_XPATH_EXPRESSIONS[expression_key]
    
    if name:
        xpath_expr = xpath_expr.format(var=name, **kwargs)
    elif kwargs:
        xpath_expr = xpath_expr.format(**kwargs)
    
    return svg_root.xpath(xpath_expr, namespaces=config.SVG_NAMESPACES)


def get_element_attributes(element) -> Dict[str, str]:
    """
    Get common SVG element attributes in a consistent format.
    
    Extracts frequently accessed attributes from SVG elements with
    standardized default values for missing attributes.
    
    Args:
        element: lxml element object
        
    Returns:
        Dictionary containing:
            - id: Element ID or 'no-id'
            - label: Inkscape label or 'no-label'
            - tag: Element tag name
            - text: Element text content or ''
            
    Example:
        >>> attrs = get_element_attributes(element)
        >>> print(f"Processing {attrs['tag']} with label '{attrs['label']}'")
    """
    return {
        'id': element.get('id', 'no-id'),
        'label': element.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}label", 'no-label'),
        'tag': element.tag.split('}')[-1] if '}' in element.tag else element.tag,
        'text': element.text or ''
    }


def log_element_change(logger, operation: str, element_name: str, 
                   current: Optional[str] = None, new: Optional[str] = None, 
                   level: str = "debug", additional_info: Optional[str] = None):
    """
    Log element changes with consistent formatting.
    
    Provides standardized logging format for element modifications
    to make debugging and tracing easier.
    
    Args:
        logger: Logger instance
        operation: Description of operation performed
        element_name: Name/identifier of element
        current: Current value (optional)
        new: New value (optional)
        level: Log level ('debug', 'info', 'warning', 'error')
        additional_info: Extra information to log (optional)
        
    Example:
        >>> log_element_change(logger, "fill color", "MyBox", 
        ...               current="red", new="blue")
    """
    if not logger:
        return
    
    message_parts = [f"{operation}: {element_name}"]
    
    if current is not None:
        message_parts.append(f"current: '{current}'")
    if new is not None:
        message_parts.append(f"new: '{new}'")
    if additional_info:
        message_parts.append(additional_info)
    
    message = " | ".join(message_parts)
    
    log_func = getattr(logger, level, logger.debug)
    log_func(message)


def safe_execute(operation: Callable, logger=None, operation_name: str = "operation", 
               return_on_error: Any = False, raise_on_error: bool = False) -> Tuple[bool, Any]:
    """
    Execute operation with consistent error handling and logging.
    
    Provides standardized error handling for operations throughout the
    application with optional logging and configurable error behavior.
    
    Args:
        operation: Callable function to execute
        logger: Logger instance for logging (optional)
        operation_name: Description of operation for logging
        return_on_error: Value to return if operation fails (default: False)
        raise_on_error: If True, re-raise exception instead of handling
        
    Returns:
        Tuple of (success: bool, result: Any)
        
    Example:
        >>> success, result = safe_execute(process_image, logger, "image processing")
        >>> if not success:
        ...     print(f"Failed to process image: {result}")
    """
    try:
        result = operation()
        if logger:
            logger.debug(f"✓ {operation_name} completed successfully")
        return True, result
    except Exception as e:
        error_msg = f"✗ {operation_name} failed: {e}"
        if logger:
            logger.error(error_msg)
        
        if raise_on_error:
            raise
            
        return False, return_on_error


def update_svg_style_property(element, property_name: str, value: str, logger=None) -> bool:
    """
    Update a single CSS property in an element's style attribute.
    
    Handles both adding new properties and modifying existing ones in the
    style attribute of SVG elements.
    
    Args:
        element: SVG element to modify
        property_name: CSS property name to update
        value: New value for the property
        logger: Logger instance (optional)
        
    Returns:
        True if element was modified, False otherwise
        
    Example:
        >>> success = update_svg_style_property(rect, "fill", "#FF0000")
        >>> if success:
        ...     print("Rectangle color updated")
    """
    
    # Get current style attribute
    current_style = element.get('style', '')
    
    if logger:
        log_element_change(logger, "style property", get_element_attributes(element)['label'], 
                        current=current_style, new=f"{property_name}:{value}")
    
    # Parse current style into dictionary
    style_dict = utilities.parse_style(current_style)
    current_value = style_dict.get(property_name, '')
    
    # Check if value needs to be changed
    if str(current_value) == str(value):
        if logger:
            logger.debug(f"  No change needed for {property_name}")
        return False
    
    # Update property value
    style_dict[property_name] = value
    
    # Format back to CSS string
    new_style = utilities.format_style(style_dict)
    
    # Set the new style attribute
    element.set('style', new_style)
    
    if logger:
        logger.debug(f"  ✓ Updated {property_name}: '{current_value}' -> '{value}'")
    
    return True


def validate_required_value(value: Any, logger=None, value_name: str = "value") -> bool:
    """
    Validate that a required value is present and not empty.
    
    Provides consistent validation for required parameters across
    the application with optional logging.
    
    Args:
        value: Value to validate
        logger: Logger instance (optional)
        value_name: Name of the value for error messages
        
    Returns:
        True if value is valid, False otherwise
        
    Example:
        >>> if not validate_required_value(filename, logger, "filename"):
        ...     return None
    """
    if value is None or (isinstance(value, str) and value.strip() == ''):
        if logger:
            logger.debug(f"✗ {value_name} is required but not provided")
        return False
    
    if logger:
        logger.debug(f"✓ {value_name} validation passed: '{value}'")
    
    return True


def clean_string(value: Any, allow_empty: bool = False, strip: bool = True) -> Optional[str]:
    """
    Clean and validate string values consistently.
    
    Converts any value to string, optionally strips whitespace,
    and validates based on allow_empty parameter.
    
    Args:
        value: Value to clean (any type)
        allow_empty: If False, returns None for empty strings
        strip: If True, strips leading/trailing whitespace
        
    Returns:
        Cleaned string or None if invalid
        
    Example:
        >>> clean_string("  hello world  ")
        'hello world'
        >>> clean_string("", allow_empty=False)
        None
    """
    if value is None:
        return None
    
    # Convert to string
    str_value = str(value)
    
    # Strip whitespace if requested
    if strip:
        str_value = str_value.strip()
    
    # Return None if empty and not allowed
    if not str_value and not allow_empty:
        return None
    
    return str_value


def validate_file_basics(file_path: str, allowed_extensions: Optional[set] = None, 
                     max_size: Optional[int] = None) -> Dict[str, Any]:
    """
    Validate file existence, size, and extension consistently.
    
    Performs basic file validation checks with consistent error
    reporting and optional size/extension validation.
    
    Args:
        file_path: Path to file to validate
        allowed_extensions: Set of allowed extensions (optional)
        max_size: Maximum allowed file size in bytes (optional)
        
    Returns:
        Dictionary with validation results:
            - valid: Boolean indicating if file passes all checks
            - errors: List of error messages
            - file_size: Actual file size in bytes
            - extension: File extension
            
    Example:
        >>> result = validate_file_basics("image.png", {".png", ".jpg"}, max_size=1024*1024)
        >>> if not result['valid']:
        ...     print("Validation failed:", result['errors'])
    """    
    errors = []
    result = {'valid': True, 'errors': errors}
    
    # Check if file exists
    if not os.path.exists(file_path):
        errors.append(f"File not found: {file_path}")
        result['valid'] = False
        return result
    
    # Get file info
    file_size = os.path.getsize(file_path)
    file_ext = os.path.splitext(file_path)[1].lower()
    
    result['file_size'] = file_size
    result['extension'] = file_ext
    
    # Check file size
    size_limit = max_size or config.MAX_FILE_SIZE
    if file_size > size_limit:
        errors.append(f"File too large: {file_size} bytes (max: {size_limit})")
        result['valid'] = False
    
    # Check extension
    if allowed_extensions and file_ext not in allowed_extensions:
        errors.append(f"File extension not allowed: {file_ext}")
        result['valid'] = False
    
    return result


def safe_dict_get(dictionary: Dict, key: str, default: str = "", 
                fallbacks: Optional[List[str]] = None) -> str:
    """
    Get dictionary value with multiple fallback options.
    
    Attempts to retrieve a value from dictionary with primary key,
    then tries fallback keys if primary is not found.
    
    Args:
        dictionary: Dictionary to search
        key: Primary key to look for
        default: Default value if no keys found
        fallbacks: List of fallback keys to try (optional)
        
    Returns:
        Found value or default
        
    Example:
        >>> config = {"color": "red", "fill": "blue"}
        >>> value = safe_dict_get(config, "background", fallbacks=["fill", "color"])
        'blue'
    """
    # Try primary key first
    if key in dictionary:
        value = dictionary[key]
        if value not in (None, ''):
            return str(value)
    
    # Try fallback keys
    if fallbacks:
        for fallback_key in fallbacks:
            if fallback_key in dictionary:
                value = dictionary[fallback_key]
                if value not in (None, ''):
                    return str(value)
    
    return default


def logged_iterate(items: List, logger, operation_name: str = "processing", 
                show_progress: bool = True) -> Iterator[Tuple[int, Any]]:
    """
    Iterate with optional progress logging.
    
    Provides consistent iteration pattern with optional progress
    reporting for debugging and user feedback.
    
    Args:
        items: List of items to iterate
        logger: Logger instance
        operation_name: Description of operation for logging
        show_progress: If True, logs progress information
        
    Yields:
        Tuple of (index, item) for each item in list
        
    Example:
        >>> for idx, item in logged_iterate(files, logger, "file processing"):
        ...     # Process each file with automatic progress logging
        ...     process_file(item)
    """
    total_items = len(items)
    
    if logger and show_progress:
        logger.debug(f"Starting {operation_name}: {total_items} items")
    
    for idx, item in enumerate(items):
        if logger and show_progress and (idx + 1) % 10 == 0 or idx == total_items - 1:
            progress = (idx + 1) / total_items * 100
            logger.debug(f"  {operation_name}: {idx + 1}/{total_items} ({progress:.1f}%)")
        
        yield idx, item
    
    if logger and show_progress:
        logger.debug(f"✓ {operation_name} completed: {total_items} items processed")

