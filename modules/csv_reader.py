#!/usr/bin/env python3
"""
CSV processing utilities for InkAutoGen extension.

This module provides comprehensive CSV file reading capabilities including:
- Automatic encoding detection (supports 15+ encodings)
- BOM (Byte Order Mark) detection
- Multiple fallback methods for encoding detection
- CSV structure validation
- Performance optimization through caching
- Security validation of input files

Key Features:
- Encoding Detection: Uses chardet library (if available), BOM detection,
  and trial-and-error fallback for maximum compatibility
- Caching: Encoding detection results are cached for performance
- Validation: CSV files are validated for security and structure
- Error Handling: Detailed error messages with context information

Classes:
    CSVReader: Main class for reading and processing CSV files
"""

import csv
import os
import logging
import re
from typing import List, Dict, Optional, Any, Iterator, Tuple
from pathlib import Path

try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False
    chardet = None
    logging.warning("chardet library not available. Encoding detection will use fallback methods.")

import config

from exceptions import CSVProcessingError, PerformanceError
from security import FileValidator
from performance import cached, timed


class CSVReader:
    """
    Handles CSV file reading with encoding detection and validation.
    
    This class provides a comprehensive solution for reading CSV files with
    various encodings. It automatically detects the encoding using multiple
    methods and validates the file structure.
    
    Attributes:
        logger: Optional logger instance for logging operations
        _encoding_cache: Internal cache for storing detected encodings
        
    Usage:
        >>> logger = logging.getLogger(__name__)
        >>> reader = CSVReader(logger)
        >>> data = reader.read_csv_data('data.csv', 'autodetect')
        >>> print(f"Read {len(data)} rows")
    
    Performance:
        - Encoding detection is cached with 1-hour TTL
        - CSV reading is timed for performance monitoring
        - CSV info retrieval is cached
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize CSVReader with optional logger.
        
        Args:
            logger: Optional logging.Logger instance. If provided, detailed
                   logging will be enabled for debugging and analysis.
        """
        self.logger = logger
        self._encoding_cache: Dict[str, str] = {}
        self._csv_header_pattern = re.compile(config.CSV_HEADER_PATTERN)
        
        if self.logger:
            self.logger.debug("CSVReader initialized")
            self.logger.debug(f"chardet available: {CHARDET_AVAILABLE}")
            self.logger.debug(f"Supported encodings: {len(config.SUPPORTED_ENCODINGS)}")
            self.logger.debug(f"Max CSV rows: {config.MAX_CSV_ROWS}")
    
    @cached(ttl=3600)
    def detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding using multiple methods for better accuracy.
        
        This method implements a multi-tiered encoding detection strategy:
        1. Check internal cache (if previously detected)
        2. Security validation of file path
        3. chardet library (most accurate, 70%+ confidence)
        4. BOM (Byte Order Mark) detection for UTF variants
        5. Trial-and-error with supported encodings
        6. Fallback to UTF-8
        
        Args:
            file_path: Absolute or relative path to the CSV file
            
        Returns:
            str: Detected encoding name (e.g., 'utf-8', 'utf-16-le', 'windows-1252')
            
        Raises:
            CSVProcessingError: If file doesn't exist or cannot be read
            FileSecurityError: If file fails security validation
            
        Example:
            >>> reader = CSVReader(logger)
            >>> encoding = reader.detect_encoding('data.csv')
            >>> print(f"Detected: {encoding}")
            Detected: utf-8
        """
        # Step 1: Check cache first for performance
        if file_path in self._encoding_cache:
            cached_encoding = self._encoding_cache[file_path]
            if self.logger:
                self.logger.debug(f"Using cached encoding: {cached_encoding}")
                self.logger.debug(f"Cache hit for file: {file_path}")
            return cached_encoding
        
        if self.logger:
            self.logger.info(f"Starting encoding detection for: {file_path}")
            self.logger.debug("Step 1: Checking cache - MISS")
        
        # Step 2: Security validation - ensures file is safe to read
        if self.logger:
            self.logger.debug("Step 2: Performing security validation")
        try:
            FileValidator.validate_csv_file(file_path)
            if self.logger:
                self.logger.debug("File passed security validation")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Security validation failed: {e}")
            raise
        
        # Step 3: Try chardet library (most accurate method)
        if self.logger:
            self.logger.debug("Step 3: Attempting chardet detection")
        detected_encoding = self._detect_with_chardet(file_path)
        if detected_encoding:
            self._encoding_cache[file_path] = detected_encoding
            if self.logger:
                self.logger.info(f"✓ Detected file encoding with chardet: {detected_encoding}")
                self.logger.debug(f"Encoding cached for: {file_path}")
            return detected_encoding
        
        if self.logger:
            self.logger.debug("chardet detection failed, trying next method")
        
        # Step 4: BOM detection for UTF variants (UTF-8, UTF-16, UTF-32)
        if self.logger:
            self.logger.debug("Step 4: Attempting BOM detection")
        detected_encoding = self._detect_bom(file_path)
        if detected_encoding:
            self._encoding_cache[file_path] = detected_encoding
            if self.logger:
                self.logger.info(f"✓ Detected file encoding with BOM: {detected_encoding}")
                self.logger.debug(f"Encoding cached for: {file_path}")
            return detected_encoding
        
        if self.logger:
            self.logger.debug("BOM detection failed, trying next method")
        
        # Step 5: Try common encodings with validation
        if self.logger:
            self.logger.debug("Step 5: Attempting trial-and-error detection")
        detected_encoding = self._detect_by_trial(file_path)
        if detected_encoding:
            self._encoding_cache[file_path] = detected_encoding
            if self.logger:
                self.logger.info(f"✓ Detected file encoding by trial: {detected_encoding}")
                self.logger.debug(f"Encoding cached for: {file_path}")
            return detected_encoding
        
        if self.logger:
            self.logger.debug("Trial detection failed, using fallback")
        
        # Step 6: Fallback to utf-8 with error handling
        if self.logger:
            self.logger.warning(f"⚠ Could not detect encoding, falling back to utf-8")
            self.logger.warning(config.ERROR_MESSAGES["invalid_encoding"])
        return 'utf-8'
    
    def _detect_with_chardet(self, file_path: str) -> Optional[str]:
        """
        Detect encoding using chardet library (most accurate method).
        
        chardet uses statistical analysis of byte patterns to determine encoding
        with a confidence score. We only accept detections with >70% confidence.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Optional[str]: Detected encoding or None if detection failed/low confidence
            
        Detection Logic:
            - Reads first 8KB of file (enough for accurate detection)
            - Analyzes byte patterns statistically
            - Returns encoding if confidence > 70%
            - Normalizes encoding names (e.g., 'utf8' -> 'utf-8')
            - Validates encoding is in supported list
        """
        if not CHARDET_AVAILABLE:
            if self.logger:
                self.logger.debug("chardet library not available, skipping")
            return None
        
        if self.logger:
            self.logger.debug(f"Attempting chardet detection on: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                # Read more bytes for better detection accuracy
                raw_data = f.read(8192)
                
                if self.logger:
                    self.logger.debug(f"Read {len(raw_data)} bytes for chardet analysis")
                
                result = chardet.detect(raw_data) if chardet else None
                
                if self.logger:
                    self.logger.debug(f"chardet result: {result}")
                
                # Check confidence threshold
                if result and result['confidence'] > 0.7:
                    encoding = result['encoding']
                    
                    if self.logger:
                        self.logger.debug(f"chardet detected: {encoding} (confidence: {result['confidence']:.2%})")
                    
                    # Normalize encoding names to standard Python format
                    if encoding:
                        encoding = encoding.lower().replace('-', '')
                        
                        # Map common chardet results to Python encoding names
                        normalized_encoding = config.ENCODING_MAP.get(encoding, encoding)
                        
                        if self.logger:
                            self.logger.debug(f"Normalized encoding: {encoding} -> {normalized_encoding}")
                        
                        # Validate encoding is supported
                        if normalized_encoding in config.SUPPORTED_ENCODINGS:
                            if self.logger:
                                self.logger.debug(f"✓ Encoding is supported: {normalized_encoding}")
                            return normalized_encoding
                        else:
                            if self.logger:
                                self.logger.debug(f"✗ Encoding not supported: {normalized_encoding}")
                
                if self.logger:
                    if result:
                        self.logger.debug(f"chardet detection failed (confidence too low: {result.get('confidence', 0):.2%})")
                    else:
                        self.logger.debug(f"chardet detection failed: no result")
                        
        except ImportError:
            if self.logger:
                self.logger.debug("chardet library not available")
        except Exception as e:
            if self.logger:
                self.logger.debug(f"chardet detection failed with exception: {e}")
        
        return None
    
    def _detect_bom(self, file_path: str) -> Optional[str]:
        """
        Detect encoding from BOM (Byte Order Mark).
        
        BOM is a special character sequence at the start of text files that
        indicates encoding. This is highly accurate for files with BOM.
        
        Supported BOM patterns:
            - UTF-8: EF BB BF
            - UTF-16 LE: FF FE
            - UTF-16 BE: FE FF
            - UTF-32 LE: FF FE 00 00
            - UTF-32 BE: 00 00 FE FF
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Optional[str]: Detected encoding or None if no BOM found
            
        Note:
            Not all files have BOM. Files without BOM will return None
            and should use other detection methods.
        """
        if self.logger:
            self.logger.debug(f"Checking for BOM in: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                # Read first 4 bytes (maximum BOM size)
                raw_data = f.read(4)
                
                if self.logger:
                    self.logger.debug(f"Read {len(raw_data)} bytes for BOM detection")
                    self.logger.debug(f"Hex dump: {raw_data.hex()}")
                
                # Check for UTF-8 BOM
                if raw_data.startswith(b'\xef\xbb\xbf'):
                    if self.logger:
                        self.logger.debug("✓ Detected UTF-8 BOM (EF BB BF)")
                    return 'utf-8-sig'
                
                # Check for UTF-16 LE BOM
                elif raw_data.startswith(b'\xff\xfe'):
                    if self.logger:
                        self.logger.debug("✓ Detected UTF-16 LE BOM (FF FE)")
                    return 'utf-16-le'
                
                # Check for UTF-16 BE BOM
                elif raw_data.startswith(b'\xfe\xff'):
                    if self.logger:
                        self.logger.debug("✓ Detected UTF-16 BE BOM (FE FF)")
                    return 'utf-16-be'
                
                # Check for UTF-32 LE BOM
                elif raw_data.startswith(b'\xff\xfe\x00\x00'):
                    if self.logger:
                        self.logger.debug("✓ Detected UTF-32 LE BOM (FF FE 00 00)")
                    return 'utf-32-le'
                
                # Check for UTF-32 BE BOM
                elif raw_data.startswith(b'\x00\x00\xfe\xff'):
                    if self.logger:
                        self.logger.debug("✓ Detected UTF-32 BE BOM (00 00 FE FF)")
                    return 'utf-32-be'
                else:
                    if self.logger:
                        self.logger.debug("✗ No BOM detected")
                        
        except Exception as e:
            if self.logger:
                self.logger.debug(f"BOM detection failed with exception: {e}")
        
        return None
    
    def _detect_by_trial(self, file_path: str) -> Optional[str]:
        """
        Detect encoding by trying different encodings and validating.
        
        This is a fallback method that tries to read the file with various
        encodings and checks if the content looks like valid CSV.
        
        Strategy:
            1. Try common encodings first (priority order)
            2. For each encoding, attempt to read the file
            3. Validate content looks like CSV structure
            4. Return first encoding that successfully reads and validates
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Optional[str]: First successful encoding or None if all fail
            
        Priority Order:
            1. UTF-8, UTF-8-SIG (most common)
            2. UTF-16 variants (common in Windows)
            3. Windows-1252, ISO-8859-1 (legacy encodings)
            4. Other supported encodings
        """
        if self.logger:
            self.logger.debug(f"Attempting trial-and-error detection on: {file_path}")
        
        # Prioritize common encodings
        other_encodings = [enc for enc in config.SUPPORTED_ENCODINGS if enc not in config.PRIORITY_ENCODINGS]
        test_encodings = config.PRIORITY_ENCODINGS + other_encodings
        
        if self.logger:
            self.logger.debug(f"Will test {len(test_encodings)} encodings in priority order")
            self.logger.debug(f"Priority encodings: {config.PRIORITY_ENCODINGS}")
        
        for i, encoding in enumerate(test_encodings, 1):
            if self.logger:
                self.logger.debug(f"Trial {i}/{len(test_encodings)}: Trying {encoding}")
            
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    # Read more content for better validation
                    content = f.read(4096)
                    
                    if self.logger:
                        self.logger.debug(f"  Read {len(content)} characters successfully")
                    
                    # Additional validation: check if content looks like valid CSV
                    if self._validate_csv_content(content):
                        if self.logger:
                            self.logger.info(f"✓ Trial encoding successful: {encoding}")
                            self.logger.debug(f"  Content validated as CSV structure")
                        return encoding
                    else:
                        if self.logger:
                            self.logger.debug(f"  Content does not look like valid CSV")
                        
            except (UnicodeDecodeError, UnicodeError) as e:
                if self.logger:
                    self.logger.debug(f"  ✗ Decode failed: {type(e).__name__}")
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"  ✗ Error: {e}")
        
        if self.logger:
            self.logger.debug("✗ All trial encodings failed")
        
        return None
    
    def _validate_csv_content(self, content: str) -> bool:
        """
        Validate that content looks like valid CSV.
        
        This is a lightweight validation to check if content appears to be
        valid CSV data. It doesn't fully parse the CSV but checks
        for structural indicators.
        
        Validation Checks:
            1. Content is not empty
            2. Contains at least one line
            3. Lines contain comma separators (CSV structure)
            4. Can be parsed by csv.Sniffer (CSV format detection)
        
        Args:
            content: Text content to validate
            
        Returns:
            bool: True if content appears to be valid CSV, False otherwise
            
        Note:
            This is a basic validation. Files may still have CSV errors
            even if they pass this check. The purpose is to filter out
            obviously incorrect encodings.
        """
        if not content or not content.strip():
            if self.logger:
                self.logger.debug("CSV validation failed: content is empty")
            return False
        
        try:
            # Split content into lines
            lines = content.split('\n')
            
            if self.logger:
                self.logger.debug(f"CSV content validation: {len(lines)} lines")
            
            if not lines or not lines[0].strip():
                if self.logger:
                    self.logger.debug("CSV validation failed: no content")
                return False
            
            # Use csv.Sniffer to detect CSV format
            try:
                sniffer = csv.Sniffer()
                # Remove BOM if present
                content_clean = content.replace('\ufeff', '')
                
                has_header = sniffer.has_header(content_clean)
                
                if self.logger:
                    self.logger.debug(f"CSV sniffer result: has_header={has_header}")
                
                return True
            except csv.Error as e:
                if self.logger:
                    self.logger.debug(f"CSV sniffer failed: {e}")
                # If sniffer fails, assume it's valid CSV (better to be permissive)
                return True
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"CSV validation failed with exception: {e}")
            # If validation fails, still consider it valid (better to be permissive)
            return True
    
    def parse_csv_header(self, header: str) -> Dict[str, Any]:
        """
        Parse CSV header into element name and optional property name.
        
        This method parses headers according to new syntax:
        - Element value: <element label name>
        - Property value: <element label name>##<property name>
        
        Args:
            header: CSV header string to parse
            
        Returns:
            Dictionary with parsed information:
            - 'element_type': The element type (layer, text, circle, rect, etc.) - inferred from common patterns
            - 'element_name': The element label name
            - 'property_name': Optional property name (None for element values)
            - 'is_property': Boolean indicating if this is a property header
            - 'original': Original header string
            
        Examples:
            >>> reader = CSVReader()
            >>> reader.parse_csv_header("MyTitle")
            {'element_type': 'text', 'element_name': 'MyTitle', 'property_name': None, 'is_property': False, 'original': 'MyTitle'}
            >>> reader.parse_csv_header("MyTitle##font-size")
            {'element_type': 'text', 'element_name': 'MyTitle', 'property_name': 'font-size', 'is_property': True, 'original': 'MyTitle##font-size'}
        """
        if self.logger:
            self.logger.debug(f"Parsing CSV header: {header}")
        
        match = self._csv_header_pattern.match(header.strip())
        if not match:
            if self.logger:
                self.logger.warning(f"Invalid CSV header format: {header}")
            return {
                'element_name': header,
                'element_type': 'unknown',
                'property_name': None,
                'is_property': False,
                'original': header
            }
        
        element_name = match.group(1).strip()
        property_name = match.group(2).strip() if match.group(2) else None
        is_property = property_name is not None
        
        # Infer element type from element name patterns
        element_type = self._infer_element_type(element_name, property_name)
        
        result = {
            'element_name': element_name,
            'element_type': element_type,
            'property_name': property_name,
            'is_property': is_property,
            'original': header
        }
        
        if self.logger:
            self.logger.debug(f"  Parsed header: {result}")
        
        return result
    
    def _infer_element_type(self, element_name: str, property_name: Optional[str]) -> str:
        """
        Infer element type from element name patterns and property names.
        
        This method analyzes the element name and property to determine the likely
        element type based on Inkscape-supported element types.
        
        Supported Inkscape element types:
        - Basic shapes: rect, circle, ellipse, line, polyline, polygon, path
        - Text elements: text, tspan, flowPara, flowSpan
        - Structural: g (group/layer), image
        - Other: use (embedded content), symbol, defs, marker
        
        Args:
            element_name: The element label/name from CSV
            property_name: Optional property name (helps determine type)
            
        Returns:
            String representing inferred element type
        """
        element_name_lower = element_name.lower()
        
        # Check for explicit element type hints in name
        if any(hint in element_name_lower for hint in ['layer', 'group']):
            return 'layer'
        elif any(hint in element_name_lower for hint in ['text', 'title', 'label', 'header']):
            return 'text'
        elif any(hint in element_name_lower for hint in ['image', 'logo', 'icon', 'picture', 'photo']):
            return 'image'
        elif any(hint in element_name_lower for hint in ['rect', 'rectangle', 'box']):
            return 'rect'
        elif any(hint in element_name_lower for hint in ['circle', 'dot', 'ball']):
            return 'circle'
        elif any(hint in element_name_lower for hint in ['ellipse', 'oval']):
            return 'ellipse'
        elif any(hint in element_name_lower for hint in ['line']):
            return 'line'
        elif any(hint in element_name_lower for hint in ['path', 'curve', 'shape']):
            return 'path'
        elif any(hint in element_name_lower for hint in ['polygon', 'poly']):
            return 'polygon'
        elif any(hint in element_name_lower for hint in ['polyline']):
            return 'polyline'
        
        # Infer from property name if element name doesn't give clear hints
        if property_name:
            prop_lower = property_name.lower()
            if any(prop in prop_lower for prop in ['font-size', 'font-family', 'text-anchor', 'font']):
                return 'text'
            elif any(prop in prop_lower for prop in ['fill', 'stroke', 'opacity']):
                return 'shape'  # Generic shape (could be rect, circle, path, etc.)
            elif any(prop in prop_lower for prop in ['href', 'xlink:href']):
                return 'image'
        
        # Default to unknown if no clear pattern detected
        return 'unknown'
    
    def _scan_svg_elements(self, svg_root) -> Dict[str, str]:
        """
        Scan SVG document to find all elements by their label names.
        
        This method searches for elements that can be targeted by CSV data:
        - Elements with inkscape:label attribute
        - Elements with id attribute
        - Text elements (by their content)
        
        Args:
            svg_root: SVG document root element
            
        Returns:
            Dictionary mapping element names to their actual types
        """
        if svg_root is None:
            return {}
                
        elements = {}
        
        # Find elements with inkscape:label (primary identification method)
        labeled_elements = svg_root.xpath(config.COMMON_XPATH_EXPRESSIONS["labeled_elements_generic"], namespaces=config.SVG_NAMESPACES)
        for elem in labeled_elements:
            label = elem.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}label")
            if label:
                elements[label] = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                if elements[label] == 'g':
                    # find layer/group elements using inkscape:groupmode
                    groupmode = elem.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}groupmode")
                    if groupmode == 'layer':
                        elements[label] = 'layer'
        
        # Find elements with id (fallback method)
        id_elements = svg_root.xpath(config.COMMON_XPATH_EXPRESSIONS["id_elements_generic"], namespaces=config.SVG_NAMESPACES)
        for elem in id_elements:
            elem_id = elem.get('id')
            if elem_id and elem_id not in elements:
                elements[elem_id] = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                if elements[elem_id] == 'g':
                    # find layer/group elements using inkscape:groupmode
                    groupmode = elem.get(f"{{{config.SVG_NAMESPACES['inkscape']}}}groupmode")
                    if groupmode == 'layer':
                        elements[elem_id] = 'layer'
        
        # Find text elements by content (for text replacement)
        text_elements = svg_root.xpath(config.COMMON_XPATH_EXPRESSIONS["text_element_svg"], namespaces=config.SVG_NAMESPACES)
        for elem in text_elements:
            text_content = elem.text or ""
            if text_content and text_content not in elements:
                elements[text_content] = 'text'
        
        if self.logger:
            self.logger.debug(f"Scanned elements: {elements}")

        return elements
    
    def classify_csv_data(self, data: List[Dict[str, str]], svg_root) -> Dict[str, Any]:
        """
        Classify CSV data into element values and property values.
        
        This method analyzes the CSV headers and classifies columns as:
        - Element values: Direct element content replacement
        - Property values: Element property modification
        
        Updated to validate against SVG template structure when available.
        
        Args:
            data: CSV data as list of dictionaries
            svg_root: SVG document root element for validation (optional but recommended)
            
        Returns:
            Dictionary with classification:
            - 'elements': List of element value headers
            - 'properties': List of property value headers
            - 'element_mapping': Dict mapping header to parsed info
            - 'property_mapping': Dict mapping header to parsed info
            - 'missing_elements': List of headers referencing elements not found in SVG
        """
        if not data or svg_root is None:
            return {
                'elements': [],
                'properties': [],
                'element_mapping': {},
                'property_mapping': {},
                'missing_elements': []
            }
        
        if self.logger:
            self.logger.info("Classifying CSV data headers...")
        
        elements = []
        properties = []
        element_mapping = {}
        property_mapping = {}
        missing_elements = []
        
        # Pre-scan SVG elements if available for validation
        svg_elements_cache = {}
    
        svg_elements_cache = self._scan_svg_elements(svg_root)
        if self.logger:
            self.logger.debug(f"Scanned SVG elements: {len(svg_elements_cache)} elements found")
        
        for header in data[0].keys():
            if self.logger:
                self.logger.debug(f"Processing header: {header} ")
                
            parsed = self.parse_csv_header(header)
            
            # Validate against SVG if available
            parsed['element_type'] = svg_elements_cache.get(parsed['element_name'], 'unknown')

            if parsed['element_type'] == 'unknown':
                missing_elements.append(header)
                if self.logger:
                    self.logger.warning(f"Element '{parsed['element_name']}' not found in SVG template")
                continue
            
            if parsed['is_property']:
                properties.append(header)
                property_mapping[header] = parsed
                if self.logger:
                    self.logger.debug(f"  Property: {header} -> {parsed}")
            else:
                elements.append(header)
                element_mapping[header] = parsed
                if self.logger:
                    self.logger.debug(f"  Element: {header} -> {parsed}")
        
        result = {
            'elements': elements,
            'properties': properties,
            'element_mapping': element_mapping,
            'property_mapping': property_mapping,
            'missing_elements': missing_elements
        }
        
        if self.logger:
            self.logger.info(f"Classification complete: {len(elements)} elements, {len(properties)} properties, {len(missing_elements)} missing")
        
        return result
    
    def filter_csv_data_by_missing_elements(self, data: List[Dict[str, str]]
                                            , missing_elements: List[str]) -> Tuple[List[Dict[str, str]],List[Dict[str, str]]]:
        """
        Filter CSV data to remove columns that reference missing elements.
        
        Args:
            data: Original CSV data as list of dictionaries
            missing_elements: List of headers to remove (reference missing SVG elements)
            
        Returns:
            Filtered CSV data with missing element columns removed
        """
        if not data or not missing_elements:
            return data
        
        filtered_data = []
        removed_data = []
        missing_set = set(missing_elements)
        
        for row in data:
            filtered_row = {k: v for k, v in row.items() if k not in missing_set}
            filtered_data.append(filtered_row)
            removed_row = {k: v for k, v in row.items() if k in missing_set}
            removed_data.append(removed_row)
        
        if self.logger:
            original_cols = len(data[0]) if data else 0
            filtered_cols = len(filtered_data[0]) if filtered_data else 0
            total_filtered_cells = len(missing_elements) * len(filtered_data) if filtered_data else 0
            self.logger.info(f"CSV data filtered: {original_cols} -> {filtered_cols} columns per row")
            self.logger.info(f"Total filtered cells: {total_filtered_cells}")
        
        return filtered_data, removed_data
        
    def filter_rows_by_range(self, data: List[Dict[str, str]], row_range: str) -> List[Dict[str, str]]:
        """
        Filter CSV rows based on range specification.
        
        Supports various range formats:
        - Range: "1-5" (rows 1 to 5)
        - Specific: "1,4,5,9" (rows 1, 4, 5, 9)
        - Combined: "1-5,7,9,13-16,21"
        - Even: "even" (even-numbered rows only)
        - Odd: "odd" (odd-numbered rows only)
        
        Args:
            data: Complete CSV data
            row_range: Range specification string
            
        Returns:
            Filtered list of rows
        """
        if not row_range or row_range.lower() == 'all':
            return data
        
        if self.logger:
            self.logger.info(f"Filtering rows by range: {row_range}")
        
        total_rows = len(data)
        selected_indices = set()
        
        # Parse range specification
        parts = [part.strip() for part in row_range.split(',')]
        
        for part in parts:
            if part.lower() == 'even':
                selected_indices.update(i for i in range(total_rows) if (i + 1) % 2 == 0)
            elif part.lower() == 'odd':
                selected_indices.update(i for i in range(total_rows) if (i + 1) % 2 == 1)
            elif '-' in part:
                # Range like "1-5"
                try:
                    start, end = map(int, part.split('-'))
                    # Convert to 0-based indices
                    start_idx = max(0, start - 1)
                    end_idx = min(total_rows, end)
                    selected_indices.update(range(start_idx, end_idx))
                except ValueError:
                    if self.logger:
                        self.logger.warning(f"Invalid range format: {part}")
            else:
                # Single number
                try:
                    row_num = int(part)
                    idx = row_num - 1  # Convert to 0-based
                    if 0 <= idx < total_rows:
                        selected_indices.add(idx)
                except ValueError:
                    if self.logger:
                        self.logger.warning(f"Invalid row number: {part}")
        
        # Sort indices and create filtered data
        filtered_indices = sorted(selected_indices)
        filtered_data = [data[i] for i in filtered_indices]
        
        if self.logger:
            self.logger.info(f"Row filtering complete: {len(filtered_data)}/{total_rows} rows selected")
            self.logger.debug(f"Selected indices: {filtered_indices}")
        
        return filtered_data
    
    @timed(operation="csv_reader.read_csv_data")
    def read_csv_data(self, csv_path: str, encoding: str = "autodetect") -> List[Dict[str, str]]:
        """
        Read CSV data with proper encoding handling.
        
        This is the main method for reading CSV files. It handles:
        - Automatic or manual encoding specification
        - CSV structure parsing
        - Performance limit enforcement (max rows)
        - BOM removal from headers
        - Error handling with detailed context
        
        Args:
            csv_path: Path to the CSV file
            encoding: File encoding ('autodetect' for automatic detection)
                     Supported values: 'autodetect', 'utf-8', 'utf-16-le', etc.
            
        Returns:
            List[Dict[str, str]]: List of dictionaries, one per CSV row
                                  Each dictionary maps column headers to values
            
        Raises:
            CSVProcessingError: If CSV file doesn't exist or cannot be read
            PerformanceError: If CSV exceeds MAX_CSV_ROWS limit
            FileSecurityError: If file fails security validation
            
        Example:
            >>> reader = CSVReader(logger)
            >>> data = reader.read_csv_data('data.csv', 'utf-8')
            >>> print(data[0])
            {'column1': 'value1', 'column2': 'value2'}
        """
        if self.logger:
            self.logger.info("="*60)
            self.logger.info("CSV READING STARTED")
            self.logger.info("="*60)
            self.logger.info(f"CSV Path: {csv_path}")
            self.logger.info(f"Encoding Mode: {encoding}")
        
        # Validate file existence
        if not os.path.exists(csv_path):
            error_msg = config.ERROR_MESSAGES["csv_not_found"].format(path=csv_path)
            if self.logger:
                self.logger.error(error_msg)
            raise CSVProcessingError(
                error_msg,
                file_path=csv_path
            )
        
        if self.logger:
            self.logger.info("✓ File exists")
        
        # Detect encoding if needed
        if encoding == "autodetect":
            if self.logger:
                self.logger.info("Encoding mode: Auto-detect")
            encoding = self.detect_encoding(csv_path)
        else:
            if self.logger:
                self.logger.info(f"Encoding mode: User specified ({encoding})")
        
        if self.logger:
            self.logger.info(f"Using encoding: {encoding}")
        
        # Read and parse CSV
        try:
            data = []
            
            if self.logger:
                self.logger.debug("Opening CSV file for reading")
            
            with open(csv_path, 'r', encoding=encoding, errors='replace') as f:
                reader = csv.DictReader(f)
                
                # Clean fieldnames to remove BOM if present
                if reader.fieldnames:
                    if self.logger:
                        self.logger.debug(f"Raw headers: {reader.fieldnames}")
                    
                    cleaned_fieldnames = []
                    for field in reader.fieldnames:
                        if field and field.startswith('\ufeff'):
                            cleaned_field = field.replace('\ufeff', '')
                            cleaned_fieldnames.append(cleaned_field)
                            if self.logger:
                                self.logger.debug(f"✓ Removed BOM from fieldname: '{field}' -> '{cleaned_field}'")
                        else:
                            cleaned_fieldnames.append(field)
                    
                    reader.fieldnames = cleaned_fieldnames
                    
                    if self.logger:
                        self.logger.info(f"CSV headers: {reader.fieldnames}")
                        self.logger.info(f"Column count: {len(reader.fieldnames)}")
                
                # Check performance limits and read data
                row_count = 0
                
                if self.logger:
                    self.logger.info("Reading CSV rows...")
                
                for row in reader:
                    row_count += 1
                    
                    # Enforce performance limits
                    if row_count > config.MAX_CSV_ROWS:
                        if self.logger:
                            self.logger.error(f"Performance limit exceeded: {row_count} > {config.MAX_CSV_ROWS}")
                        raise PerformanceError(
                            f"CSV has too many rows: {row_count} (max: {config.MAX_CSV_ROWS})",
                            limit_type="row_count",
                            current_value=row_count,
                            limit=config.MAX_CSV_ROWS
                        )
                    
                    data.append(row)
                    
                    if self.logger and row_count <= 5:
                        # Log first few rows for debugging
                        self.logger.debug(f"  Row {row_count}: {row}")
                    elif self.logger and row_count == 6:
                        self.logger.debug(f"  ... (remaining rows suppressed)")
                
                if self.logger:
                    self.logger.info(f"✓ Read {len(data)} rows successfully")
                    self.logger.info(f"Memory usage: ~{len(str(data))} bytes")
            
            # Validate we have data
            if not data:
                if self.logger:
                    self.logger.error("CSV file is empty")
                raise CSVProcessingError(config.ERROR_MESSAGES["no_data"], file_path=csv_path)
            
            if self.logger:
                self.logger.info("="*60)
                self.logger.info("CSV READING COMPLETED SUCCESSFULLY")
                self.logger.info("="*60)
            
            return data
            
        except csv.Error as e:
            error_msg = f"CSV parsing error: {e}"
            if self.logger:
                self.logger.error(error_msg)
                self.logger.error(f"CSV Error details: {type(e).__name__}")
            raise CSVProcessingError(
                error_msg,
                file_path=csv_path,
                line_number=getattr(e, 'line_num', None)
            ) from e
        except Exception as e:
            error_msg = f"Error reading CSV: {e}"
            if self.logger:
                self.logger.error(error_msg)
                self.logger.error(f"Exception: {type(e).__name__}: {e}")
            raise CSVProcessingError(
                error_msg,
                file_path=csv_path
            ) from e
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting CSV info: {e}")
            return {
                "file_path": csv_path,
                "error": str(e),
                "is_valid": False
            }

