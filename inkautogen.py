#!/usr/bin/env python3
"""
InkAutoGen Main Extension Module

This module provides the main Inkscape extension for batch SVG template processing.
It orchestrates CSV data import, SVG template modification, and multi-format export.

Main Components:
    - InkAutoGen: Main extension class that coordinates all processing modules
    - Module Initialization: Sets up CSV reader, SVG processor, file exporter
    - Batch Processing: Processes multiple CSV rows to generate multiple outputs
    - Export Management: Handles file export, PDF merging, and cleanup

Usage:
    When running as Inkscape extension:
    1. Open SVG template in Inkscape
    2. Extensions → Export → InkAutoGen
    3. Select CSV file and configure options
    4. Click Apply to process

Dependencies:
    - inkex: Inkscape extension API (when running in Inkscape)
    - lxml: XML/SVG parsing and manipulation
    - modules/svg_processor: SVG template processing
    - modules/csv_reader: CSV data import with encoding detection
    - modules/file_exporter: File export operations
    - modules/config: Configuration constants
    - modules/exceptions: Custom exception classes

Author: InkAutoGen Development Team
Version: 1.4.0
License: See LICENSE file
"""

import sys
import os
import shutil
import tempfile
import uuid
import logging
from pathlib import Path
from typing import Optional, List


# ============================================================================
# Import and Library Availability Check
# ============================================================================

try:
    from inkex import Effect, SvgDocumentElement, Boolean
    from inkex.command import inkscape
    from lxml import etree
    import argparse
    INKSCAPE_AVAILABLE = True
except ImportError:
    INKSCAPE_AVAILABLE = False
    Effect = object
    SvgDocumentElement = None
    Boolean = bool
    inkscape = None

# ============================================================================
# Module Path Setup
# ============================================================================

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))


# ============================================================================
# Internal Module Imports
# ============================================================================

import config
import utilities

from svg_processor import SVGElementProcessor
from csv_reader import CSVReader
from file_exporter import FileExporter, PDFMerger
from version import get_version, get_version_info
from exceptions import ConfigurationError

# Version information
__version__ = get_version()
VERSION_INFO = get_version_info()


# ============================================================================
# Main Extension Class
# ============================================================================

class InkAutoGen(Effect if INKSCAPE_AVAILABLE else object):
    """
    Main Inkscape extension class for batch SVG template processing.
    
    This class orchestrates the entire workflow of reading CSV data,
    applying it to SVG templates, and exporting results in various formats.
    
    Attributes:
        logger (Optional[logging.Logger]): Logger instance for debugging and monitoring
        element_processor (Optional[SVGElementProcessor]): Coordinator for template application
        csv_reader (Optional[CSVReader]): Reader for CSV data files
        file_exporter (Optional[FileExporter]): Handler for file exports
        pdf_merger (Optional[PDFMerger]): Handler for PDF merging operations
    
    Example:
        Running programmatically:
        >>> extension = InkAutoGen()
        >>> extension.options.csv_path = 'data.csv'
        >>> extension.options.export_format = 'pdf'
        >>> extension.options.dpi = 300
        >>> extension.effect()
    """

    def __init__(self):
        """
        Initialize InkAutoGen extension with argument parsers.
        
        This method sets up all command-line arguments that are exposed
        through the Inkscape extension interface (.inx file).
        
        Note:
            Actual configuration values are populated by Inkscape when the
            extension is invoked through the UI. Default values are provided
            for programmatic usage.
        """
        super(InkAutoGen, self).__init__()
        
        # Initialize argument parser for programmatic usage
        #self.arg_parser = argparse.ArgumentParser()
        #self.arg_parser: Optional[argparse.ArgumentParser] = None
        
        self._add_arguments()
        
        # ====================================================================
        # Instance Attribute Initialization
        # ====================================================================
        
        self.logger: Optional[logging.Logger] = None
        self.element_processor: Optional[SVGElementProcessor] = None
        self.csv_reader: Optional[CSVReader] = None
        self.file_exporter: Optional[FileExporter] = None
        self.pdf_merger: Optional[PDFMerger] = None
        
        # New: track UI option for relative paths (default False)
        self.is_use_relative_path: bool = False


    # ====================================================================
    # Argument Parser Configuration
    # ====================================================================
    def _add_arguments(self):
        # CSV Input Configuration

        # page tab option
        self.arg_parser.add_argument(
            '--tab', 
            type=str, 
            dest='tab',
            help='Tab selection in the extension dialog'
        )

        self.arg_parser.add_argument(
            "--csv_path",
            type=str,
            default="",
            help="Path to CSV file containing data for template substitution"
        )
        self.arg_parser.add_argument(
            "--csv_encoding",
            type=str,
            default="autodetect",
            help="CSV file encoding (e.g., utf-8, utf-16, autodetect)"
        )
        
        # Output Configuration
        self.arg_parser.add_argument(
            "--export_format",
            type=str,
            default="png",
            help="Export output format (png, pdf, svg, jpg, eps, etc.)"
        )
        self.arg_parser.add_argument(
            "--dpi",
            type=int,
            default=config.DEFAULT_DPI,
            help="DPI for raster output formats (72-1200, default: 300)"
        )
        self.arg_parser.add_argument(
            "--filename_pattern",
            type=str,
            default="output_{}",
            help="Output filename pattern (supports {} for index [optional], %ColumnName% for CSV column values)"
        )
        self.arg_parser.add_argument(
            "--output_path",
            type=str,
            default="",
            help="Output directory path for saved files (default: /tmp or C:\\tmp)"
        )
        self.arg_parser.add_argument(
            "--overwrite",
            type=Boolean,
            default=True,
            help="Overwrite existing output files (true/false)"
        )
        
        # PDF Configuration
        self.arg_parser.add_argument(
            "--merge_pdf",
            type=Boolean,
            default=False,
            help="Merge multiple PDF outputs into single file (true/false)"
        )
        self.arg_parser.add_argument(
            "--delete_individual_pdfs",
            type=Boolean,
            default=False,
            help="Delete individual PDF files after merging (true/false)"
        )
        
        # Debugging Configuration
        self.arg_parser.add_argument(
            "--enable_logging",
            type=Boolean,
            default=False,
            help="Enable detailed logging to output file (true/false)"
        )
        
        # Debugging Configuration
        self.arg_parser.add_argument(
            "--relative_path",
            type=Boolean,
            default=False,
            help="Use relative paths instead of absolute paths for image references in SVGs (true/false)"
        )
        
        # Advanced Options
        self.arg_parser.add_argument(
            "--apply_layer_visibility",
            type=Boolean,
            default=False,
            help="Apply data to elements only if respective layer is visible (true/false)"
        )
        
        self.arg_parser.add_argument(
            "--export_csv_enabled",
            type=Boolean,
            default=False,
            help="Export data to CSV (SVG scanning)"
        )
        
        self.arg_parser.add_argument(
            "--export_csv_path",
            type=str,
            default="",
            help="Path for CSV export (SVG scanning)"
        )
        
        self.arg_parser.add_argument(
            "--row_range",
            type=str,
            default="all",
            help="Rows to consider from CSV (e.g., 1-5, 1,4,5,9, even, odd, all)"
        )
        
        self.arg_parser.add_argument(
            "--log_level",
            type=str,
            default="INFO",
            help="Log level for debugging (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        )
        
        self.arg_parser.add_argument(
            "--disable_log_timestamps",
            type=Boolean,
            default=False,
            help="Disable date/time stamps in log entries for cleaner output"
        )

    def initialize_modules(self, logger: Optional[logging.Logger] = None, csv_path: Optional[str] = None
                           , output_path: Optional[str] = None, is_use_relative_path: bool = False) -> None:
        """
        Initialize all processing modules for the extension.

        This method creates instances of all required modules and passes
        the logger to them for debugging and monitoring.

        Args:
            logger: Optional logger instance for debugging. If None, no logging occurs.
            csv_path: Optional path to CSV file. Used to extract directory for image search.

        Modules Initialized:
            - CSVReader: Parses CSV header patterns with SVG validation
            - SVGElementProcessor: Handles SVG element operations
            - SVGTemplateProcessor: Coordinates template application
            - CSVReader: Reads CSV data
            - FileExporter: Handles file export operations
            - PDFMerger: Merges PDF files

        Note:
            This method should be called before any processing operations to ensure
            all modules are properly initialized.
        """
        if logger:
            logger.debug("Initializing processing modules...")

        # Extract CSV directory for image path resolution
        csv_dir = None
        if csv_path and os.path.exists(csv_path):
            csv_dir = os.path.dirname(os.path.abspath(csv_path))
            if logger:
                logger.debug(f"CSV directory for image search: {csv_dir}")

        # Initialize SVG processing modules
        self.element_processor = SVGElementProcessor(csv_dir=csv_dir, output_dir=output_path
                                                     , is_use_relative_path=is_use_relative_path, logger=logger)

        # Initialize data and file handling modules
        self.csv_reader = CSVReader(logger)
        self.file_exporter = FileExporter(logger)
        self.pdf_merger = PDFMerger(logger)

        if logger:
            logger.debug("All modules initialized successfully")

    def process_batch(self, csv_data: List[dict], csv_classification: dict, missing_elements: List[str], svg_str: str
                      , output_dir: str, export_format: str, dpi: int, filename_pattern: str, overwrite: bool
                      , apply_layer_visibility: bool, removed_csv_data: List[dict]) -> tuple[List[str], List[str]]:
        """
        Process batch of CSV rows to generate output files.
        
        This method handles Phase 5 of the workflow - the main batch processing loop.
        It processes each CSV row, applies data to the SVG template, and exports files.
        
        Args:
            csv_data: List of CSV row dictionaries
            csv_classification: Classified CSV data structure
            missing_elements: List of missing SVG elements
            svg_str: Serialized SVG template string
            output_dir: Directory for output files
            export_format: Target export format
            dpi: Resolution for raster formats
            filename_pattern: Pattern for output filenames
            overwrite: Whether to overwrite existing files
            apply_layer_visibility: Whether to apply layer visibility
            removed_csv_data: Removed CSV data for filename generation
            
        Returns:
            Tuple of (generated_files, pdf_files)
            
        Raises:
            Exception: For processing errors (logged and handled)
        """
        generated_files: List[str] = []
        pdf_files: List[str] = []
        temp_working_dir = tempfile.mkdtemp()

        if self.logger:
            self.logger.info("=" * 80)
            self.logger.info("BATCH PROCESSING")
            self.logger.info("=" * 80)
            self.logger.info(f"Temp working directory: {temp_working_dir}")
            self.logger.info(f"Processing {len(csv_data)} rows...")

        # Process each CSV row
        for idx, row in enumerate(csv_data):
            if self.logger:
                self.logger.info("=" * 60)
                self.logger.info(f"Processing row {idx + 1}/{len(csv_data)}")
                self.logger.info("=" * 60)
                self.logger.debug(f"Row data keys: {list(row.keys())}")
                self.logger.debug(f"Row data values: {list(row.values())}")

            # Generate unique temporary SVG filename
            temp_svg_file = os.path.join(temp_working_dir, f'temp_{uuid.uuid4().hex}.svg')

            try:
                # Parse template string to create new XML tree
                parser = etree.XMLParser(remove_blank_text=False, remove_comments=False)
                temp_root = etree.fromstring(svg_str, parser=parser)

                # Initialize statistics tracking
                stats = {
                    'text_replaced': 0,
                    'layers_modified': 0,
                    'images_replaced': 0,
                    'properties_modified': 0,
                    'errors': 0
                }

                # First process layer visibility for temp_root
                if self.logger:
                    self.logger.debug('First processing layer visibility.')

                if csv_classification and csv_classification.get('element_mapping'):
                    elDic = dict()
                    for id, data in csv_classification['element_mapping'].items():
                        if id not in missing_elements:
                            if data.get('element_type') == 'layer':
                                # insert into elDic
                                elDic[id] = row[id].strip().lower()
                    if len(elDic) > 0:
                        self.element_processor.apply_layer_visibility(svg_root=temp_root, layer_data=elDic, stats=stats)

                # Check condition for consideration of visible layer only
                if apply_layer_visibility:
                    self.element_processor.remove_invisible_layers(svg_root=temp_root,stats=stats)
                    if self.logger:
                        self.logger.debug("Removed invisible layers from template SVG root")

                # Now process for element properties
                if self.logger:
                    self.logger.debug('Now processing for element properties')
                    
                for id, data in csv_classification['property_mapping'].items():
                    if id not in missing_elements:
                        elements = self.element_processor.find_elements_by_name(temp_root,data.get('element_name'))
                        for element in elements:
                            self.element_processor.process_property(element=element, property_name=data.get('property_name')
                                                                    ,value=row[id], element_type=data.get('element_type'))

                # Now process for elements
                if self.logger:
                    self.logger.debug('Now processing for elements value')

                for id, data in csv_classification['element_mapping'].items():
                    if id not in missing_elements:
                        elements = self.element_processor.find_elements_by_name(temp_root,data.get('element_name'))
                        for element in elements:
                            if data.get('element_type') == 'text':
                                self.element_processor.process_text_element(element=element
                                                                            , variable_name=data.get('element_name'), value=row[id])
                            if data.get('element_type') == 'image':
                                self.element_processor.process_image_element(element=element
                                                                             , variable_name=data.get('element_name'), value=row[id])
                
                # Serialize to string with proper UTF-8 encoding for Unicode support
                output_bytes = etree.tostring(temp_root, encoding='utf-8', pretty_print=False, xml_declaration=False)
                output_str = output_bytes.decode('utf-8')

                # Write processed SVG to temporary file
                with open(temp_svg_file, 'w', encoding='utf-8', newline='') as f:
                    f.write(output_str)

                if self.logger:
                    self.logger.debug(f"Temporary SVG written: {temp_svg_file}")
                    self.logger.debug(f"Output SVG size: {len(output_str)} characters")

                # Generate output filename with CSV column support
                output_filename = utilities.generate_output_filename(filename_pattern, idx, row, removed_csv_data[idx], self.logger, len(csv_data))

                # Only add extension if not already present in filename
                if not output_filename.lower().endswith(f'.{export_format.lower()}'):
                    output_file = os.path.join(output_dir, f"{output_filename}.{export_format}")
                else:
                    output_file = os.path.join(output_dir, output_filename)

                if self.logger:
                    self.logger.info(f"Output file: {output_file}")

                # Export to final format
                export_success = self.file_exporter.export_file( temp_svg_file, output_file
                                                                , export_format, dpi, overwrite)

                if export_success:
                    generated_files.append(output_file)
                    if export_format == 'pdf':
                        pdf_files.append(output_file)

                    print(f"Exported: {output_file}", file=sys.stderr)
                    if self.logger:
                        self.logger.info(f"Successfully exported: {output_file}")
                else:
                    print(f"Skipped (overwrite disabled): {output_file}", file=sys.stderr)
                    if self.logger:
                        self.logger.warning(f"Skipped (overwrite disabled): {output_file}")

                # Clean up temporary SVG file
                if os.path.exists(temp_svg_file):
                    os.remove(temp_svg_file)

                if self.logger:
                    self.logger.debug(f"Temporary SVG cleaned up: {temp_svg_file}")

            except Exception as e:
                error_msg = f"Error processing row {idx + 1}: {e}"
                print(error_msg, file=sys.stderr)
                if self.logger:
                    self.logger.error(error_msg, exc_info=True)
                if os.path.exists(temp_svg_file):
                    try:
                        os.remove(temp_svg_file)
                    except:
                        pass

        # Clean up temporary working directory
        try:
            shutil.rmtree(temp_working_dir)
            if self.logger:
                self.logger.info(f"Removed temp directory: {temp_working_dir}")
        except Exception as e:
            error_msg = f"Failed to remove temp directory: {e}"
            print(error_msg, file=sys.stderr)
            if self.logger:
                self.logger.error(error_msg)

        return generated_files, pdf_files

    def validate_configuration(self) -> None:
        """
        Validate configuration parameters before processing.
        
        This method performs validation checks on all user-provided configuration
        parameters to ensure they are valid and within acceptable ranges.
        Invalid parameters will raise a ConfigurationError with descriptive messages.
        
        Raises:
            ConfigurationError: If any validation check fails. The error includes:
                              - The specific parameter that failed validation
                              - The invalid value that was provided
                              - Expected value range or format
        
        Validation Checks:
            1. DPI: Must be integer between 72 and 1200
            2. Export Format: Must not be empty, max length 10 characters
            3. Filename Pattern: Must contain {} placeholder
        
        Example:
            >>> self.options.dpi = 150
            >>> self.options.export_format = "png"
            >>> self.options.filename_pattern = "output_{}"
            >>> self.validate_configuration()  # No exception, valid config
        
            >>> self.options.dpi = 1500
            >>> self.validate_configuration()
            ConfigurationError: DPI must be between 72 and 1200, got: 1500
        """
        if self.logger:
            self.logger.debug("Starting configuration validation...")
        
        # ====================================================================
        # DPI Validation
        # ====================================================================
        
        dpi = self.options.dpi
        dpi_min, dpi_max = config.VALIDATION_RULES.get('dpi', (72, 1200))
        
        if not isinstance(dpi, int) or dpi < dpi_min or dpi > dpi_max:
            error_msg = f"DPI must be between {dpi_min} and {dpi_max}, got: {dpi}"
            if self.logger:
                self.logger.error(error_msg)
            raise ConfigurationError(
                error_msg,
                config_key="dpi",
                config_value=dpi
            )
        
        if self.logger:
            self.logger.debug(f"DPI validation passed: {dpi}")
        
        # ====================================================================
        # Export Format Validation
        # ====================================================================
        
        export_format = self.options.export_format.lower()
        if not export_format or len(export_format) > 10:
            error_msg = f"Invalid export format: {export_format}"
            if self.logger:
                self.logger.error(error_msg)
            raise ConfigurationError(
                error_msg,
                config_key="export_format",
                config_value=export_format
            )
        
        if self.logger:
            self.logger.debug(f"Export format validation passed: {export_format}")
        
        # ====================================================================
        # Filename Pattern Validation
        # ====================================================================

        filename_pattern = self.options.filename_pattern
        if not filename_pattern:
            error_msg = "Filename pattern cannot be empty"
            if self.logger:
                self.logger.error(error_msg)
            raise ConfigurationError(
                error_msg,
                config_key="filename_pattern",
                config_value=filename_pattern
            )

        if self.logger:
            self.logger.debug(f"Filename pattern validation passed: {filename_pattern}")


    def effect(self):
        """
        Main processing method called by Inkscape.
        
        This is the entry point for the extension when invoked from Inkscape.
        It orchestrates the entire workflow:
            1. Validate configuration
            2. Setup logging
            3. Initialize modules
            4. Read CSV data
            5. Process each row and generate output files
            6. Merge PDFs if requested
            7. Cleanup temporary files
        
        Processing Flow:
            - CSV data is read once
            - SVG template is serialized to string for reuse
            - For each CSV row:
                * Parse template string to create new XML tree
                * Apply data replacements
                * Remove blank text nodes
                * Serialize and save to temporary file
                * Export to final format
            - Merge PDFs if requested
            - Clean up temporary files
        
        Error Handling Strategy:
            - Configuration errors: Stop processing immediately
            - CSV reading errors: Stop processing immediately
            - Row processing errors: Log error and continue with next row
            - Export errors: Log error and continue
            - Cleanup errors: Log error but don't fail
        
        Returns:
            None (results written to output directory)
        
        Side Effects:
            - Creates output files in the specified directory
            - Creates temporary files in temp directory
            - Creates log file if logging is enabled
            - Modifies Inkscape document (temporary changes only)
        
        Example:
            Running from Inkscape UI:
            1. Open SVG template
            2. Extensions → Export → InkAutoGen
            3. Select CSV file and options
            4. Click Apply (calls this method)
        
        Note:
            This method is called automatically by Inkscape when the extension
            is invoked. It should not be called directly in most cases.
        """
        # ====================================================================
        # Phase 1: Configuration and Setup
        # ====================================================================
        
        # Extract configuration values for easier access
        export_format = self.options.export_format.lower()
        dpi = self.options.dpi
        filename_pattern = self.options.filename_pattern
        merge_pdf = self.options.merge_pdf
        delete_individual_pdfs = self.options.delete_individual_pdfs
        overwrite = self.options.overwrite
        enable_logging = self.options.enable_logging
        disable_log_timestamps = self.options.disable_log_timestamps
        relative_path = self.options.relative_path if export_format == 'svg' else False
        apply_layer_visibility = self.options.apply_layer_visibility
        export_csv_enabled = self.options.export_csv_enabled
        export_csv_path = self.options.export_csv_path
        row_range = self.options.row_range
        csv_encoding = self.options.csv_encoding
        log_level = self.options.log_level

        csv_path = self.options.csv_path
        
        # Validate CSV file path
        if not csv_path or not os.path.exists(csv_path):
            error_msg = f"CSV file not found or path not provided: {csv_path}"
            print(error_msg, file=sys.stderr)
            return
        
        # Validate all configuration parameters
        try:
            self.validate_configuration()
        except ConfigurationError as e:
            error_msg = f"Configuration error: {e}"
            print(error_msg, file=sys.stderr)
            if self.logger:
                self.logger.error(error_msg)
            return
        
        # Ensure output directory exists
        output_path = self.options.output_path
        if not output_path:
            """
            if sys.platform.startswith('win'):
                path = r'C:\tmp'
            else:
                path = '/tmp'
            """
            output_path = config.DEFAULT_TEMP_DIR
            if self.logger:
                self.logger.debug(f"No output path provided, using default: {output_path}")
        
        output_path = os.path.abspath(output_path)
        os.makedirs(output_path, exist_ok=True)
        
        # Setup logging
        self.logger = utilities.setup_logging(output_path, enable_logging, log_level, disable_log_timestamps)

        svg_root = self.document.getroot()

        # Handle CSV export if requested
        if export_csv_enabled and export_csv_path:
            if self.logger:
                self.logger.info("=" * 80)
                self.logger.info("CSV EXPORT MODE")
                self.logger.info("=" * 80)
            
            # Initialize modules for CSV export
            self.initialize_modules(self.logger, csv_path, output_path, relative_path)
            
            if self.logger:
                self.logger.info("Starting SVG to CSV export...")  

            # Export SVG to CSV
            export_success = self.element_processor.export_svg_to_csv(svg_root, export_csv_path)
            
            if export_success:
                print(f"SVG elements exported to CSV: {export_csv_path} {config.EXPORT_CSV_FILENAME}", file=sys.stderr)
                if self.logger:
                    self.logger.info(f"SVG elements exported to CSV: {export_csv_path} {config.EXPORT_CSV_FILENAME}")
            else:
                print("CSV export failed", file=sys.stderr)
                if self.logger:
                    self.logger.warning("CSV export failed")
            return
        
        # ====================================================================
        # Phase 2: Module Initialization
        # ====================================================================
        
        # Initialize all processing modules with CSV path for image resolution
        self.initialize_modules(self.logger, csv_path, output_path, relative_path)

        # Log configuration parameters
        if self.logger:
            self.logger.info("=" * 80)
            self.logger.info("CONFIGURATION")
            self.logger.info("=" * 80)
            self.logger.info(f"Enable Logging: {enable_logging}")
            if enable_logging:
                self.logger.info(f"  Log Level: {log_level}")
                self.logger.info(f"  Disable Timestamps: {disable_log_timestamps}")
            if export_csv_enabled:
                self.logger.info(f"CSV Export Enabled: {export_csv_enabled}")
                self.logger.info(f"  CSV Export Path: {export_csv_path}")
            else:
                self.logger.info(f"CSV Path: {csv_path}")
                self.logger.info(f"CSV Encoding: {csv_encoding}")
                self.logger.info(f"Row Range: {row_range}")
                self.logger.info(f"Export Format: {export_format}")
                self.logger.info(f"DPI: {dpi}")
                self.logger.info(f"Use Relative Paths: {relative_path}")
                self.logger.info(f"Apply Layer Visibility: {apply_layer_visibility}")
                self.logger.info(f"Output Path: {output_path}")
                self.logger.info(f"Filename Pattern: {filename_pattern}")
                self.logger.info(f"Overwrite: {overwrite}")
                self.logger.info(f"Merge PDF: {merge_pdf}")
                if merge_pdf:
                    self.logger.info(f"Delete Individual PDFs: {delete_individual_pdfs}")
        
        # ====================================================================
        # Phase 3: CSV Data Import
        # ====================================================================
        
        if self.logger:
            self.logger.info("=" * 80)
            self.logger.info("CSV DATA IMPORT")
            self.logger.info("=" * 80)
        
        try:
            csv_data = self.csv_reader.read_csv_data(csv_path, csv_encoding)
            if self.logger:
                self.logger.info(f"Successfully read {len(csv_data)} rows from CSV")
                self.logger.debug(f"CSV data shape: {len(csv_data)} rows x {len(csv_data[0]) if csv_data else 0} columns")
            
            # Apply row range filtering if specified
            if row_range and row_range.lower() != 'all':
                original_count = len(csv_data)
                csv_data = self.csv_reader.filter_rows_by_range(csv_data, row_range)
                if self.logger:
                    self.logger.info(f"Row range filtering: {original_count} -> {len(csv_data)} rows")
        except Exception as e:
            error_msg = f"Error reading CSV: {e}"
            print(error_msg, file=sys.stderr)
            if self.logger:
                self.logger.error(error_msg, exc_info=True)
            return
        
        # Validate that data was read
        if not csv_data:
            error_msg = "No data found in CSV file"
            print(error_msg, file=sys.stderr)
            if self.logger:
                self.logger.error(error_msg)
            return
        
        if self.logger:
            self.logger.info("=" * 80)
            self.logger.info("CSV DATA CLASSIFICATION")
            self.logger.info("=" * 80)
        
        # Classify CSV data once at the beginning for optimization
        csv_classification = None
        if csv_data:
            # Get SVG root for validation
            csv_classification = self.csv_reader.classify_csv_data(csv_data, svg_root)
            if self.logger:
                self.logger.info(f"CSV classification: {len(csv_classification['elements'])} elements, {len(csv_classification['properties'])} properties")
                if csv_classification.get('missing_elements'):
                    self.logger.warning(f"Missing elements in SVG: {csv_classification['missing_elements']}")
        
        # ====================================================================
        # Phase 4: Template Preparation
        # ====================================================================
        
        output_dir = output_path
        
        if self.logger:
            self.logger.info("=" * 80)
            self.logger.info("TEMPLATE PREPARATION")
            self.logger.info("=" * 80)
            self.logger.debug("Cleaning template SVG tree...")
                
        # Serialize template to string for reuse - use UTF-8 encoding to handle Unicode properly
        svg_bytes = etree.tostring(svg_root, encoding='utf-8', pretty_print=True, xml_declaration=False)
        svg_str = svg_bytes.decode('utf-8')

        if self.logger:
            self.logger.info(f"Template SVG size: {len(svg_str)} characters")
            self.logger.debug(f"Template root element: {svg_root.tag}")

        # ====================================================================
        # Phase 4.5: Filter Missing Elements from CSV Data
        # ====================================================================
        
        if csv_classification and csv_classification.get('missing_elements'):
            missing_elements = csv_classification.get('missing_elements', [])
            if self.logger:
                self.logger.info("=" * 80)
                self.logger.info("FILTERING MISSING ELEMENTS")
                self.logger.info("=" * 80)
                self.logger.info(f"Found {len(missing_elements)} CSV headers referencing missing elements: {missing_elements}")
            
            # Remove missing element columns from all CSV rows
            csv_data, removed_csv_data  = self.csv_reader.filter_csv_data_by_missing_elements(csv_data, missing_elements)
            
            if self.logger:
                self.logger.info(f"Total filtered cells: {len(missing_elements) * len(csv_data)}")
                self.logger.debug('removed csv data:')
                self.logger.debug(removed_csv_data)
            
            # Check if all elements were filtered out
            if not csv_data or not csv_data[0]:
                if self.logger:
                    self.logger.warning("All CSV columns reference missing elements - no data to process")
                print("Warning: All CSV columns reference missing SVG elements. No files will be generated.", file=sys.stderr)
                return
            elif self.logger:
                final_col_count = len(csv_data[0])
                self.logger.info(f"Proceeding with batch processing using {final_col_count} valid columns")
        
        if False:
            self.logger.info("-" * 80)
            self.logger.info('csv data after filtering missing elements:')
            for row in csv_data:
                self.logger.info(row)
            self.logger.info("-" * 80)
            self.logger.info("csv classification of elements:")
            if csv_classification and csv_classification.get('element_mapping'):
                for header, data in csv_classification['element_mapping'].items():
                    if header not in missing_elements:
                        self.logger.info(f"{header}: {data}")
            self.logger.info("-" * 80)
            self.logger.info("csv classification of properties:")
            if csv_classification and csv_classification.get('property_mapping'):
                for header, data in csv_classification['property_mapping'].items():
                    if header not in missing_elements:
                        self.logger.info(f"{header}: {data}")
            self.logger.info("-" * 80)

        # ====================================================================
        # Phase 5: Batch Processing Loop
        # ====================================================================
        
        generated_files, pdf_files = self.process_batch(csv_data=csv_data, csv_classification=csv_classification, missing_elements=missing_elements
                                                        , svg_str=svg_str, output_dir=output_path, export_format=export_format, dpi=dpi
                                                        , filename_pattern=filename_pattern, overwrite=overwrite
                                                        , apply_layer_visibility=apply_layer_visibility, removed_csv_data=removed_csv_data)

        # ====================================================================
        # Phase 6: PDF Merging (if requested)
        # ====================================================================

        if merge_pdf and export_format == 'pdf' and len(pdf_files) > 1:
            if self.logger:
                self.logger.info("=" * 80)
                self.logger.info("PDF MERGING")
                self.logger.info("=" * 80)
                self.logger.info(f"Merge PDF option: {merge_pdf}")
                self.logger.info(f"Export format: {export_format}")
                self.logger.info(f"PDF files to merge: {len(pdf_files)}")
                self.logger.info(f"PDF files list: {pdf_files}")

            merged_filename = 'output_merged'

            # Only add extension if not already present in filename
            if not merged_filename.lower().endswith('.pdf'):
                merged_output = os.path.join(output_dir, f"{merged_filename}.pdf")
            else:
                merged_output = os.path.join(output_dir, merged_filename)

            if self.pdf_merger.merge_pdfs(pdf_files, merged_output):
                print(f"Merged PDF created: {merged_output}", file=sys.stderr)
                if self.logger:
                    self.logger.info(f"Successfully created merged PDF: {merged_output}")

                # Delete individual PDFs if requested
                if delete_individual_pdfs:
                    if self.logger:
                        self.logger.info("Deleting individual PDF files...")

                    for pdf in pdf_files:
                        try:
                            os.remove(pdf)
                            print(f"Deleted individual PDF: {pdf}", file=sys.stderr)
                            if self.logger:
                                self.logger.info(f"Deleted: {pdf}")
                        except Exception as e:
                            error_msg = f"Failed to delete {pdf}: {e}"
                            print(error_msg, file=sys.stderr)
                            if self.logger:
                                self.logger.error(error_msg)
            else:
                if self.logger:
                    self.logger.error("Failed to merge PDF files")

        # ====================================================================
        # Phase 7: Final Summary
        # ====================================================================

        # Log final summary
        if self.logger:
            self.logger.info("=" * 80)
            self.logger.info("PROCESSING SUMMARY")
            self.logger.info("=" * 80)
            self.logger.info(f"Total CSV rows processed: {len(csv_data)}")
            self.logger.info(f"Total files generated: {len(generated_files)}")
            self.logger.info(f"PDF files generated: {len(pdf_files)}")
            self.logger.info(f"Processing successful: {len(generated_files) == len(csv_data)}")
            self.logger.info("=" * 80)
            self.logger.info("InkAutoGen Extension Completed")
            self.logger.info("=" * 80)
            self.logger.debug("Extension processing finished")
            self.logger.disabled = True



# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    """
    Main entry point for running the extension as a standalone script.
    
    This allows the extension to be run outside of Inkscape for testing
    and debugging purposes. When run through Inkscape, the .inx file
    handles the invocation.
    
    Example:
        Running standalone:
        $ python3 inkautogen.py --csv_path=data.csv --export_format=pdf
    """
    try:

        # Create and run extension
        InkAutoGen().run()
    except Exception as e:
        print(f"Extension failed: {e}")
        sys.exit(1)
