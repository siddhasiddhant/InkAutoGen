#!/usr/bin/env python3
"""
Constants and configuration for InkAutoGen extension.
"""

from typing import List, Dict, Set, Tuple, FrozenSet, Final
import sys

# Default Configuration
DEFAULT_DPI: int = 300
DEFAULT_EXPORT_FORMAT: str = "png"
DEFAULT_FILENAME_PATTERN: str = "output_{count}"
DEFAULT_OVERWRITE: bool = True
DEFAULT_LOGGING: bool = False
DEFAULT_CSV_ENCODING: str = "autodetect"
DEFAULT_USE_RELATIVE_PATHS: bool = False
DEFAULT_MERGE_PDF: bool = False
DEFAULT_DELETE_INDIVIDUAL_PDFS: bool = False
DEFAULT_APPLY_LAYER_VISIBILITY: bool = False
DEFAULT_CREATE_LOG_FILE: bool = False


# Default date time format
DEFAULT_DATE_FORMAT: str = "yyyymmdd"
DEFAULT_TIME_FORMAT: str = "hhmmss"

# Default Paths
DEFAULT_TEMP_DIR: str = "/tmp" if not sys.platform.startswith('win') else r"C:\tmp"
LOG_FILENAME: str = "inkautogen.log"
EXPORT_CSV_FILENAME: str = "inkautogen.csv"

# Cache Settings
CACHE_ENABLED: bool = True
MAX_CACHE_SIZE: int = 100
CACHE_TTL: int = 3600  # 1 hour

# Performance Settings
MAX_CSV_ROWS: int = 10000

# File Security
MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
ALLOWED_CSV_EXTENSIONS: Set[str] = {".csv"}

# Validation Rules
VALIDATION_RULES: Dict[str, Tuple[int, int]] = {
    "dpi": (72, 1200),
    "filename_length": (1, 255),
    "max_filename_pattern_length": (1, 100)
}

# Row Selection Patterns
ROW_SELECTION_PATTERNS: Dict[str, str] = {
    "range": r'(\d+)-(\d+)',  # 1-5
    "single": r'(\d+)',       # 1,4,5,9
    "even": r'even',          # even rows only
    "odd": r'odd'             # odd rows only
}

# Filename Pattern Placeholders
FILENAME_PATTERNS: Dict[str, str] = {
    "count": r'\{count(?::(\d+))?\}',      # {count} or {count:3}
    "date": r'\{date(?::([^}]+))?\}',       # {date} or {date:dd-MMM-yyyy}
    "time": r'\{time\}',                    # {time}
    "csv_column": r'%([^%]+)%'              # %column_name%
}

# Logging Configuration
LOG_TIMESTAMPS_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DEFAULT_FORMAT: str = "%(levelname)s - %(message)s"
LOG_LEVELS: Dict[str, int] = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

# Export format constants with immutability guarantees
# Raster formats (pixel-based, supports transparency)
RASTER_FORMATS: Final[FrozenSet[str]] = frozenset({
    "png",    # Portable Network Graphics - lossless, transparency
    "jpg",    # JPEG - lossy compression, no transparency
    "jpeg",   # Same as jpg
    "tiff",   # Tagged Image File Format - lossless archival
    "webp"    # WebP - modern web format
})

VECTOR_FORMATS: Final[FrozenSet[str]] = frozenset({
    "svg",    # Scalable Vector Graphics - editable
    "pdf",    # Portable Document Format - print-ready
    "ps",     # PostScript - professional printing
    "eps"     # Encapsulated PostScript - compatible
})

# All formats (derived from subsets for consistency)
SUPPORTED_EXPORT_FORMATS: Final[FrozenSet[str]] = RASTER_FORMATS | VECTOR_FORMATS

# Supported CSV Encodings
SUPPORTED_ENCODINGS: List[str] = [
    "utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be",
    "utf-32", "utf-32-le", "utf-32-be", "cp1252", "iso-8859-1",
    "iso-8859-15", "latin-1", "windows-1252", "ascii"
]

# Encoding Configuration
ENCODING_MAP: Dict[str, str] = {
    'utf8': 'utf-8',
    'utf16': 'utf-16',
    'utf16le': 'utf-16-le',
    'utf16be': 'utf-16-be',
    'ascii': 'utf-8',  # ASCII is subset of UTF-8
    'windows1252': 'windows-1252',
    'cp1252': 'windows-1252',
    'iso88591': 'iso-8859-1',
    'latin1': 'latin-1'
}

PRIORITY_ENCODINGS: List[str] = [
    'utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be',
    'windows-1252', 'iso-8859-1', 'latin-1', 'ascii'
]

# Layer Visibility Mapping
LAYER_VISIBILITY_MAP: Dict[str, str] = {
    "invisible": "none",
    "visible": "inline",
    "no": "none",
    "yes": "inline",
    "hide": "none",
    "show": "inline", 
    "0": "none",
    "1": "inline", 
    "false": "none",
    "true": "inline",
    "none": "none", 
    "inline": "inline",
    "hidden": "none",
    "display":"inline"
}

# Color Alias Map to hex for matching aliases in tests
COLOR_ALIASES: Dict[str, str] = {
    'red': '#ff0000',
    'blue': '#0000ff',
    'green': '#00ff00',
    'yellow': '#ffff00',
    'black': '#000000',
    'white': '#ffffff',
    'orange': '#ffa500',
    'purple': '#800080',
    'pink': '#ffc0cb',
    'gray': '#808080',
    'grey': '#808080'
}

# Map property names to SVG attributes - comprehensive mapping for all supported properties
PROPERTY_ATTRIBUTE_MAP: Dict[str, str] = {
    # Fill Properties
    'fill': 'fill',
    'fill-opacity': 'fill-opacity',
    'fill-rule': 'fill-rule',
    
    # Stroke Properties
    'stroke': 'stroke',
    'stroke-width': 'stroke-width',
    'stroke-opacity': 'stroke-opacity',
    'stroke-dasharray': 'stroke-dasharray',
    'stroke-dashoffset': 'stroke-dashoffset',
    'stroke-linecap': 'stroke-linecap',
    'stroke-linejoin': 'stroke-linejoin',
    'stroke-miterlimit': 'stroke-miterlimit',
    
    # Font Properties
    'font-size': 'font-size',
    'font-family': 'font-family',
    'font-weight': 'font-weight',
    'font-style': 'font-style',
    'font-variant': 'font-variant',
    'letter-spacing': 'letter-spacing',
    'word-spacing': 'word-spacing',
    
    # Text Properties
    'text-anchor': 'text-anchor',
    'text-decoration': 'text-decoration',
    'writing-mode': 'writing-mode',
    'text-align': 'text-anchor',
    'text-transform': 'text-transform',
    'direction': 'direction',
    
    # Opacity Properties
    'opacity': 'opacity',
    
    # Dimensions
    'width': 'width',
    'height': 'height',
    
    # Position
    'x': 'x',
    'y': 'y',
    
    # Transformation Properties
    'transform': 'transform',
    'translate': 'transform',
    'rotate': 'transform',
    'scale': 'transform',
    'skewX': 'transform',
    'skewY': 'transform',
    
    # Filter Properties
    'filter': 'filter',
    'blur': 'filter',
    
    # Clip Path
    'clip-path': 'clip-path',
    
    # Visibility
    'visibility': 'visibility',
    'display': 'display'
}

# Security Configuration
SECURITY_INDICATORS: List[str] = [
    'path traversal', 'Unsafe characters', 'Empty file path',
    'Invalid file path', 'extension not allowed'
]

# Style Properties Configuration
STYLE_PROPERTIES: Set[str] = {
    'fill', 'fill-opacity', 'fill-rule', 'stroke', 'stroke-width', 'stroke-opacity',
    'stroke-dasharray', 'stroke-dashoffset', 'stroke-linecap', 'stroke-linejoin',
    'stroke-miterlimit', 'font-size', 'font-family', 'font-weight', 'font-style',
    'font-variant', 'letter-spacing', 'word-spacing', 'text-anchor',
    'text-decoration', 'writing-mode', 'text-align', 'text-transform', 'direction',
    'opacity', 'visibility', 'display'
}

# Element Type Configuration
TEXT_ELEMENT_TYPES: List[str] = ['text', 'tspan', 'flowpara', 'flowspan']
FONT_PROPERTIES: List[str] = ['font-size', 'font-family', 'text-anchor', 'font']
STYLE_PROPERTIES_TO_CHECK: List[str] = ['fill', 'stroke', 'opacity']
HREF_PROPERTIES: List[str] = ['href', 'xlink:href']

SHAPE_TYPES: List[str] = ['rect', 'circle', 'ellipse', 'path', 'line', 'polygon']
PROPERTIES_TO_CHECK: List[str] = ['fill', 'stroke', 'stroke-width', 'opacity']

# Element Types for Object Selection
SUPPORTED_ELEMENT_TYPES: Set[str] = {
    "text", "tspan", "flowpara", "flowspan", "image", "layer", "file"
}

# Element Types for Property Modification
SUPPORTED_PROPERTY_ELEMENTS: Set[str] = {
    "rect", "circle", "ellipse", "path", "line", "polyline", 
    "polygon", "text", "image", "g"
}

# File Security
ALLOWED_IMAGE_EXTENSIONS: Set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".tiff",
    ".pdf", ".eps", ".ps"
}

# Performance Settings
XML_PARSER_OPTIONS: Dict[str, bool] = {
    "remove_blank_text": False,
    "remove_comments": False,
    "resolve_entities": False
}

# Error Messages
ERROR_MESSAGES: Dict[str, str] = {
    "csv_not_found": "CSV file not found: {path}",
    "invalid_encoding": "Could not detect encoding, falling back to utf-8",
    "no_data": "No data found in CSV file",
    "invalid_key": "Invalid key format: {key}",
    "element_not_found": "No {element_type} elements found for: {value}",
    "export_failed": "Export failed: {error}",
    "pdf_merge_failed": "PDF merge failed: {error}",
    "file_too_large": "File too large: {size} bytes (max: {max_size})",
    "invalid_extension": "Invalid file extension: {ext}"
}

# Regular Expression Patterns

# CSV header patterns
# Element value header: <element label name>
# Property value header: <element label name>##<property name>
CSV_PROPERTY_SEPARATOR: str = "##"
CSV_HEADER_PATTERN: str = r'^([^#]+?)(?:##(.+))?$'

# SVG Namespaces
SVG_NAMESPACES: Dict[str, str] = {
    "svg": "http://www.w3.org/2000/svg",
    "inkscape": "http://www.inkscape.org/namespaces/inkscape",
    "xlink": "http://www.w3.org/1999/xlink"
}

# XPath Templates
XPATH_TEMPLATES: Dict[str, str] = {
    "text": ".//svg:text[normalize-space(text())='{var}']",
    "tspan": ".//svg:tspan[normalize-space(text())='{var}']",
    "flowpara": ".//svg:flowPara[normalize-space(text())='{var}']",
    "flowspan": ".//svg:flowSpan[normalize-space(text())='{var}']",
    "image": ".//svg:image[@id='{var}'] | .//image[@id='{var}']",
    "layer": ".//svg:g[@inkscape:groupmode='layer' and @inkscape:label='{var}']",
    "property": ".//svg:{type}[@{property}='{var}']"
}

# Layer XPath Patterns (fallback)
LAYER_XPATH_PATTERNS: List[str] = [
    ".//svg:g[@inkscape:groupmode='layer' and @inkscape:label='{var}']",
    ".//g[@inkscape:groupmode='layer' and @inkscape:label='{var}']",
    ".//svg:g[@inkscape:groupmode='layer' and contains(@inkscape:label, '{var}')]",
    "./descendant::svg:g[@inkscape:groupmode='layer' and @inkscape:label='{var}']"
]

# Common XPath Expressions
COMMON_XPATH_EXPRESSIONS: Dict[str, str] = {
    "labeled_elements": ".//*[@inkscape:label='{var}']",
    "id_elements": ".//*[@id='{var}']",
    "invisible_layers": "//svg:*[contains(@inkscape:groupmode, 'layer') and contains(@style, 'display:none')]",
    "text_elements": ".//svg:text | .//text",
    "image_elements": ".//svg:image | .//image",
    "layer_elements": ".//svg:g[@inkscape:groupmode='layer'] | .//g[@inkscape:groupmode='layer']",
    "labeled_element_generic": ".//svg:*[@inkscape:label='{var}']",
    "shape_element_base": ".//svg:{shape_type} | .//{shape_type}",
    "text_element_svg": ".//svg:text",
    "image_element_svg": ".//svg:image",
    "group_element_svg": ".//svg:g",
    "labeled_elements_generic": ".//*[@inkscape:label]",
    "id_elements_generic": ".//*[@id]"
}
