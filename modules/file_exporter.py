#!/usr/bin/env python3
"""
File Export Utilities Module for InkAutoGen Extension

This module provides comprehensive file export functionality including:
- SVG file copying
- Multi-format export (PDF, PNG, SVG, JPG, EPS, etc.) via Inkscape
- PDF merging using PyPDF2 or pdfunite
- Temporary file management
- Security validation for export paths

Architecture:
    The module is organized into three main classes:
    
    1. FileExporter
       Handles individual file export operations to various formats.
       Supports both vector formats (SVG, PDF, EPS) and raster formats (PNG, JPG).
       
    2. PDFMerger
       Merges multiple PDF files into a single PDF.
       Attempts PyPDF2 first, falls back to pdfunite.
       
    3. TempFileManager
       Manages temporary file and directory creation/cleanup.
       Implements context manager protocol for automatic cleanup.

Export Format Support:
    Vector Formats:
    - svg: Direct file copy (no Inkscape needed)
    - pdf: Exported via Inkscape with text preservation
    - eps: Encapsulated PostScript via Inkscape
    - emf: Enhanced Metafile via Inkscape
    
    Raster Formats (require DPI setting):
    - png: Portable Network Graphics (default for web)
    - jpg: JPEG format (lossy compression)
    - png96: PNG at 96 DPI
    - png72: PNG at 72 DPI
    - png300: PNG at 300 DPI
    - png600: PNG at 600 DPI

PDF Merge Strategy:
    1. Try PyPDF2 (pure Python, no external dependencies)
    2. Fallback to pdfunite (external command-line tool)
    3. Raise error if both methods fail

Performance:
    All export operations are decorated with @timed for performance monitoring.
    Execution time is logged for optimization analysis.

Security:
    - File paths are validated against allowed extensions
    - Path traversal attempts are blocked
    - Temp files are tracked for proper cleanup

Usage Examples:
    # Export single file
    >>> exporter = FileExporter(logger)
    >>> success = exporter.export_file(
    ...     input_svg_path='template.svg',
    ...     output_path='output.png',
    ...     export_format='png',
    ...     dpi=300
    ... )
    
    # Merge PDFs
    >>> merger = PDFMerger(logger)
    >>> success = merger.merge_pdfs(
    ...     pdf_files=['doc1.pdf', 'doc2.pdf'],
    ...     output_path='merged_output.pdf'
    ... )
    
    # Use temp file manager
    >>> with TempFileManager(logger) as temp_mgr:
    ...     temp_file = temp_mgr.create_temp_file('.svg')
    ...     # Use temp_file...
    ...     # Auto-cleanup on exit

Dependencies:
    - inkex: Inkscape extension API (optional, for Inkscape integration)
    - PyPDF2: Optional PDF merge library (pip install PyPDF2)
    - pdfunite: Optional command-line tool (system package)
    - lxml: For SVG XML manipulation (indirect via svg_processor)
    
Error Handling:
    All methods raise ExportError or ValidationError for clean error handling.
    Errors include detailed context for debugging.

Author: InkAutoGen Development Team
Version: 1.5.0
License: See LICENSE file
"""

import os
import shutil
import subprocess
import tempfile
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    from inkex.command import inkscape
except ImportError:
    inkscape = None

import config
from exceptions import ExportError, ValidationError
from security import FileValidator
from performance import timed


class FileExporter:
    """
    Handles single file export operations to various formats.
    
    This class provides a unified interface for exporting SVG files to different
    formats including vector (PDF, SVG, EPS) and raster (PNG, JPG) formats.
    
    Key Features:
    - Automatic format detection (vector vs raster)
    - DPI support for raster formats
    - SVG encoding preservation for raster export
    - Overwrite control to prevent data loss
    - Performance monitoring via @timed decorator
    - Detailed logging at all levels
    
    Attributes:
        logger: Optional logging instance for debug output
        allow_mock: If True, bypasses Inkscape validation (for testing)
    
    Examples:
        >>> exporter = FileExporter(logger)
        >>> exporter.export_file('input.svg', 'output.pdf', 'pdf', dpi=300)
        True
        
        >>> # Export PNG at custom DPI
        >>> exporter.export_file('input.svg', 'output.png', 'png', dpi=600)
        True
    """
    
    def __init__(self, logger: Optional[Any] = None, allow_mock: bool = False):
        """
        Initialize FileExporter with optional logger and mock mode.
        
        Args:
            logger: Optional logging instance for debug output
            allow_mock: If True, bypasses Inkscape validation for testing
            
        Mock Mode:
            When allow_mock=True, the exporter won't validate Inkscape availability.
            This is useful for unit testing without Inkscape installed.
        """
        self.logger = logger
        self.allow_mock = allow_mock
        
        if self.logger:
            self.logger.info("FileExporter initialized")
            self.logger.debug(f"Mock mode: {allow_mock}")
        
        if not allow_mock:
            self._validate_inkscape_availability()
    
    def _validate_inkscape_availability(self) -> None:
        """
        Validate that Inkscape is available for export operations.
        
        This check ensures that the Inkscape command interface is available.
        If Inkscape is not available and mock mode is disabled,
        an ExportError is raised.
        
        Raises:
            ExportError: If Inkscape command interface is not available
        """
        if inkscape is None and not self.allow_mock:
            if self.logger:
                self.logger.error("Inkscape command interface not available")
                self.logger.error("Ensure Inkscape is installed and inkex module is available")
            raise ExportError("Inkscape command interface not available")
        
        if self.logger:
            self.logger.debug("Inkscape command interface validated successfully")
    
    @timed(operation="file_exporter.export_file")
    def export_file(self, input_svg_path: str, output_path: str, export_format: str,
                   dpi: int = config.DEFAULT_DPI, overwrite: bool = True) -> bool:
        """
        Export SVG file to specified format.
        
        This is the main export method that orchestrates:
        1. Parameter validation
        2. File existence/overwrite check
        3. Output directory creation
        4. Format-specific export (SVG copy or Inkscape export)
        5. Error handling with detailed context
        
        Export Flow:
        1. Validate parameters (path, format, DPI)
        2. Check if output exists and overwrite setting
        3. Create output directory if needed
        4. Export based on format type:
           - SVG format: Direct file copy (fast)
           - Other formats: Export via Inkscape command
        5. Log success/failure with details
        
        Args:
            input_svg_path: Path to input SVG file to export
            output_path: Path to output file (with extension)
            export_format: Export format (pdf, png, svg, jpg, eps, etc.)
            dpi: DPI for raster formats (72-1200, default: 300)
            overwrite: Whether to overwrite existing files (default: True)
            
        Returns:
            True if export successful, False if skipped (file exists, overwrite=False)
            
        Raises:
            ExportError: If export fails (Inkscape error, file system error)
            ValidationError: If parameters are invalid (bad path, unsupported format, invalid DPI)
            
        Examples:
            >>> exporter = FileExporter()
            >>> exporter.export_file('template.svg', 'output.pdf', 'pdf')
            True
            
            >>> # Export PNG at high DPI
            >>> exporter.export_file('template.svg', 'output.png', 'png', dpi=600)
            True
            
            >>> # Skip if file exists
            >>> exporter.export_file('template.svg', 'output.pdf', 'pdf', overwrite=False)
            False  # File exists and overwrite is False
        """
        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info("FILE EXPORT OPERATION")
            self.logger.info("=" * 60)
            self.logger.info(f"Input SVG: {input_svg_path}")
            self.logger.info(f"Output path: {output_path}")
            self.logger.info(f"Export format: {export_format}")
            self.logger.info(f"DPI: {dpi}")
            self.logger.info(f"Overwrite: {overwrite}")
        
        # Validate parameters
        self._validate_export_parameters(input_svg_path, output_path, export_format, dpi)
        
        if self.logger:
            self.logger.debug("Export parameters validated successfully")
        
        # Check if file exists and overwrite setting
        if os.path.exists(output_path) and not overwrite:
            if self.logger:
                self.logger.info(f"File exists and overwrite disabled, skipping: {output_path}")
            return False
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            if self.logger:
                self.logger.info(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        else:
            if self.logger:
                self.logger.debug(f"Output directory exists: {output_dir}")
        
        try:
            # Export based on format type
            if export_format == 'svg':
                if self.logger:
                    self.logger.info("Exporting as SVG (direct copy)")
                return self._export_svg(input_svg_path, output_path)
            else:
                if self.logger:
                    self.logger.info(f"Exporting via Inkscape ({export_format} format)")
                return self._export_via_inkscape(input_svg_path, output_path, export_format, dpi)
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Export failed with exception: {type(e).__name__}")
                self.logger.error(f"Exception details: {e}")
            raise ExportError(
                config.ERROR_MESSAGES["export_failed"].format(error=e),
                export_format=export_format,
                output_path=output_path
            ) from e
    
    def _validate_export_parameters(self, input_svg_path: str, output_path: str,
                                   export_format: str, dpi: int) -> None:
        """
        Validate export parameters.
        
        Performs comprehensive validation:
        1. Input SVG file existence
        2. Output path validity
        3. Output path security (no traversal attacks)
        4. Export format support
        5. DPI range (72-1200)
        
        Args:
            input_svg_path: Input SVG path to validate
            output_path: Output file path to validate
            export_format: Export format to validate
            dpi: DPI setting to validate
            
        Raises:
            ValidationError: If any parameter is invalid
            
        Validation Rules:
        - Input SVG must exist and be readable
        - Output path must not be empty
        - Output path must not contain invalid characters
        - Export format must be in SUPPORTED_EXPORT_FORMATS
        - DPI must be integer between 72 and 1200
        """
        if self.logger:
            self.logger.debug("Validating export parameters...")
        
        # Validate input SVG exists
        if not input_svg_path or not os.path.exists(input_svg_path):
            if self.logger:
                self.logger.error(f"Input SVG file does not exist: {input_svg_path}")
            raise ValidationError("Input SVG file does not exist", field_name="input_svg_path")
        
        if self.logger:
            self.logger.debug(f"Input SVG file validated: {input_svg_path}")
        
        # Validate output path is not empty
        if not output_path:
            if self.logger:
                self.logger.error("Output path cannot be empty")
            raise ValidationError("Output path cannot be empty", field_name="output_path")
        
        # Validate output path for security
        FileValidator.validate_file_path(output_path, config.ALLOWED_IMAGE_EXTENSIONS)
        
        if self.logger:
            self.logger.debug(f"Output path validated: {output_path}")
        
        # Validate export format is supported
        if export_format not in config.SUPPORTED_EXPORT_FORMATS:
            if self.logger:
                self.logger.error(f"Unsupported export format: {export_format}")
                self.logger.debug(f"Supported formats: {config.SUPPORTED_EXPORT_FORMATS}")
            raise ValidationError(
                f"Unsupported export format: {export_format}",
                field_name="export_format",
                value=export_format
            )

        if not isinstance(dpi, int) or dpi < 72 or dpi > 1200:
            raise ValidationError(
                f"DPI must be between 72 and 1200, got: {dpi}",
                field_name="dpi",
                value=str(dpi)
            )
        
        if self.logger:
            self.logger.debug(f"Export format validated: {export_format}")
        
        # Validate DPI range
        if not isinstance(dpi, int) or dpi < 72 or dpi > 1200:
            if self.logger:
                self.logger.error(f"Invalid DPI: {dpi}")
            raise ValidationError(
                f"DPI must be between 72 and 1200, got: {dpi}",
                field_name="dpi",
                field_value=str(dpi)
            )
        
        if self.logger:
            self.logger.debug(f"DPI validated: {dpi}")
    
    def _export_svg(self, input_svg_path: str, output_path: str) -> bool:
        """
        Export SVG file (copy operation).
        
        For SVG format, we perform a direct file copy since no conversion
        is needed. This is much faster than going through Inkscape.
        
        Uses shutil.copy2 to preserve metadata.
        
        Args:
            input_svg_path: Input SVG path
            output_path: Output SVG path
            
        Returns:
            True if copy successful
            
        Notes:
        - Preserves file metadata (permissions, timestamps)
        - Does not go through Inkscape (fast path)
        - No DPI setting needed for SVG format
        """
        if self.logger:
            self.logger.info(f"Copying SVG file: {input_svg_path} -> {output_path}")
        
        shutil.copy2(input_svg_path, output_path)
        
        if self.logger:
            self.logger.debug(f"SVG file copied successfully to: {output_path}")
            self.logger.info(f"File size: {os.path.getsize(output_path)} bytes")
        
        return True
    
    def _export_via_inkscape(self, input_svg_path: str, output_path: str,
                           export_format: str, dpi: int) -> bool:
        """
        Export using Inkscape command.
        
        This method uses the Inkscape command-line interface to export
        SVG files to various formats. It handles both vector and raster
        formats, with special handling for raster formats to preserve text encoding.
        
        Export Process:
        1. Build export arguments (type, filename, DPI for raster)
        2. For raster formats: Ensure SVG has UTF-8 encoding declaration
        3. Execute Inkscape command via inkex
        4. Verify output file was created
        
        Args:
            input_svg_path: Input SVG path
            output_path: Output file path
            export_format: Export format (pdf, png, jpg, eps, etc.)
            dpi: DPI for raster formats
            
        Returns:
            True if export successful
            
        Raises:
            ExportError: If Inkscape command interface is not available
        """
        # Build export arguments
        export_args = {
            'export_type': export_format,
            'export_filename': output_path,
        }
        
        # Add DPI for raster formats
        if export_format in config.RASTER_FORMATS:
            export_args['export_dpi'] = dpi
            if self.logger:
                self.logger.info(f"Raster format detected, using DPI: {dpi}")
        
        if self.logger:
            cmd_preview = f"inkscape {input_svg_path} --export-type {export_format} --export-filename {output_path}"
            if export_format in config.RASTER_FORMATS:
                cmd_preview += f" --export-dpi {dpi}"
            self.logger.debug(f"Export command: {cmd_preview}")
        
        # Execute export with encoding considerations
        if inkscape is not None:
            # For raster formats, ensure text encoding is preserved
            if export_format in config.RASTER_FORMATS:
                if self.logger:
                    self.logger.info("Ensuring UTF-8 encoding for raster export...")
                self._ensure_svg_encoding(input_svg_path, export_format)
            
            if self.logger:
                self.logger.info("Executing Inkscape export command...")
            
            inkscape(input_svg_path, **export_args)
            
            # Verify output file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if self.logger:
                    self.logger.info(f"Export completed successfully")
                    self.logger.info(f"Output file created: {output_path}")
                    self.logger.info(f"Output file size: {file_size} bytes")
            else:
                if self.logger:
                    self.logger.error(f"Export command completed but output file not found: {output_path}")
        else:
            if self.logger:
                self.logger.error("Inkscape command interface not available")
            raise ExportError("Inkscape command interface not available")
        
        if self.logger:
            self.logger.debug("Export command completed successfully")
        
        return True
    
    def _ensure_svg_encoding(self, svg_path: str, export_format: str) -> None:
        """
        Ensure SVG file has proper encoding for raster export.
        
        When exporting to raster formats via Inkscape, it's important that
        the SVG file has a proper XML declaration with UTF-8 encoding.
        Without this, text elements may be rendered incorrectly.
        
        Process:
        1. Read SVG file content
        2. Check if XML declaration with encoding exists
        3. If not, add/fix XML declaration
        4. Write back with proper encoding
        
        Args:
            svg_path: Path to SVG file
            export_format: Export format (for logging only)
        """
        if self.logger:
            self.logger.info(f"Checking SVG encoding for {export_format} export...")
        
        try:
            # Read the SVG file
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if content already has proper XML declaration with encoding
            first_line = content.split('\n')[0] if '\n' in content else content
            if content.startswith('<?xml') and 'encoding=' in first_line:
                if self.logger:
                    self.logger.debug("SVG already has proper XML encoding declaration")
                return
            
            # Add proper XML declaration with encoding
            lines = content.split('\n')
            if lines[0].startswith('<?xml'):
                # Replace existing declaration without encoding
                lines[0] = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                if self.logger:
                    self.logger.debug("Replacing existing XML declaration with UTF-8 encoding")
            else:
                # Insert XML declaration at the beginning
                lines.insert(0, '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
                if self.logger:
                    self.logger.debug("Adding XML declaration with UTF-8 encoding")
            
            # Write back with proper encoding
            with open(svg_path, 'w', encoding='utf-8', newline='') as f:
                f.write('\n'.join(lines))
            
            if self.logger:
                self.logger.info(f"Added UTF-8 encoding declaration to SVG for {export_format} export")
        
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to ensure SVG encoding: {e}")
                self.logger.warning("Continuing anyway - Inkscape might still work")
            # Continue anyway - Inkscape might still work
    
    def batch_export(self, input_svg_paths: List[str], output_dir: str,
                    export_format: str, dpi: int = config.DEFAULT_DPI,
                    filename_pattern: str = "output_{}",
                    overwrite: bool = True) -> List[str]:
        """
        Export multiple SVG files.
        
        This method processes a list of SVG files, exporting each one
        with an incrementing filename based on the pattern.
        
        Args:
            input_svg_paths: List of input SVG paths
            output_dir: Output directory
            export_format: Export format
            dpi: DPI for raster formats
            filename_pattern: Filename pattern with {} placeholder
            overwrite: Whether to overwrite existing files
            
        Returns:
            List of successfully exported file paths
            
        Examples:
            >>> exporter = FileExporter()
            >>> files = ['doc1.svg', 'doc2.svg', 'doc3.svg']
            >>> exported = exporter.batch_export(files, '/output', 'png', dpi=300)
            ['/output/doc1.png', '/output/doc2.png', '/output/doc3.png']
        """
        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info("BATCH EXPORT OPERATION")
            self.logger.info("=" * 60)
            self.logger.info(f"Input files: {len(input_svg_paths)}")
            self.logger.info(f"Output directory: {output_dir}")
            self.logger.info(f"Export format: {export_format}")
            self.logger.info(f"Filename pattern: {filename_pattern}")
        
        exported_files = []
        
        for idx, input_path in enumerate(input_svg_paths):
            if self.logger:
                self.logger.debug(f"Processing file {idx + 1}/{len(input_svg_paths)}: {input_path}")
            
            try:
                filename = filename_pattern.format(idx + 1)
                output_path = os.path.join(output_dir, f"{filename}.{export_format}")
                
                if self.logger:
                    self.logger.info(f"Exporting to: {output_path}")
                
                if self.export_file(input_path, output_path, export_format, dpi, overwrite):
                    exported_files.append(output_path)
                    if self.logger:
                        self.logger.info(f"Successfully exported: {output_path}")
                else:
                    if self.logger:
                        self.logger.warning(f"Skipped (overwrite disabled): {output_path}")
            
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to export {input_path}: {e}")
        
        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info(f"BATCH EXPORT SUMMARY")
            self.logger.info("=" * 60)
            self.logger.info(f"Total files processed: {len(input_svg_paths)}")
            self.logger.info(f"Successfully exported: {len(exported_files)}")
            self.logger.info(f"Failed: {len(input_svg_paths) - len(exported_files)}")
        
        return exported_files


class PDFMerger:
    """
    Handles PDF merging operations.
    
    This class provides functionality to merge multiple PDF files into a single
    PDF document. It implements a fallback strategy to ensure compatibility
    across different environments.
    
    Merge Strategy:
        1. Try PyPDF2 (pure Python library)
           - Pros: No external dependencies
           - Cons: May have issues with some PDF features
        2. Fallback to pdfunite (command-line tool)
           - Pros: More robust PDF handling
           - Cons: Requires external installation
        
    Special Cases:
        - Single PDF: Directly copies the file (no merge needed)
        - No PDFs: Raises ExportError
        - Multiple tools fail: Raises ExportError
    
    Attributes:
        logger: Optional logging instance for debug output
    
    Examples:
        >>> merger = PDFMerger(logger)
        >>> merger.merge_pdfs(['doc1.pdf', 'doc2.pdf'], 'merged_output.pdf')
        True
    """
    
    def __init__(self, logger: Optional[Any] = None):
        """
        Initialize PDFMerger with optional logger.
        
        Args:
            logger: Optional logging instance for debug output
        """
        self.logger = logger
        
        if self.logger:
            self.logger.info("PDFMerger initialized")
    
    @timed(operation="file_exporter.merge_pdfs")
    def merge_pdfs(self, pdf_files: List[str], output_path: str) -> bool:
        """
        Merge multiple PDF files into one.
        
        This is the main merge method that orchestrates:
        1. PDF count validation
        2. Single PDF special case (just copy)
        3. PyPDF2 merge attempt
        4. pdfunite merge attempt (fallback)
        5. Error handling if all attempts fail
        
        Args:
            pdf_files: List of PDF file paths to merge
            output_path: Output path for merged PDF
            
        Returns:
            True if merge successful
            
        Raises:
            ExportError: If merge fails (no PDFs, no tools available)
            
        Examples:
            >>> merger = PDFMerger()
            >>> merger.merge_pdfs(['doc1.pdf', 'doc2.pdf', 'doc3.pdf'], 'merged_output.pdf')
            True
        """
        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info("PDF MERGE OPERATION")
            self.logger.info("=" * 60)
            self.logger.info(f"Input PDFs: {len(pdf_files)} files")
            self.logger.info(f"Output path: {output_path}")
        
        # Validate PDF files list
        if not pdf_files:
            if self.logger:
                self.logger.error("No PDF files provided for merge")
            raise ExportError("No PDF files to merge")
        
        if len(pdf_files) == 1:
            # Only one file, just copy it
            if self.logger:
                self.logger.info("Only one PDF file, performing copy instead of merge")
            shutil.copy2(pdf_files[0], output_path)
            if self.logger:
                self.logger.info(f"Copied single PDF to: {output_path}")
            return True
        
        if self.logger:
            self.logger.debug(f"Processing {len(pdf_files)} PDF files for merge")
            for idx, pdf in enumerate(pdf_files):
                self.logger.debug(f"  PDF {idx + 1}: {pdf}")
        
        # Try PyPDF2 first
        if self._try_pypdf2_merge(pdf_files, output_path):
            return True
        
        # Fallback to pdfunite
        if self._try_pdfunite_merge(pdf_files, output_path):
            return True
        
        # Both methods failed
        error_msg = config.ERROR_MESSAGES["pdf_merge_failed"].format(error="No PDF merge tool available")
        if self.logger:
            self.logger.error("All PDF merge methods failed")
            self.logger.error(error_msg)
        
        raise ExportError(error_msg)
    
    def _try_pypdf2_merge(self, pdf_files: List[str], output_path: str) -> bool:
        """
        Try merging using PyPDF2.
        
        PyPDF2 is a pure Python library for PDF manipulation.
        It's the preferred method as it doesn't require external tools.
        
        Process:
        1. Import PyPDF2
        2. Create PdfMerger instance
        3. Append each PDF file
        4. Write merged output
        5. Close merger
        
        Args:
            pdf_files: List of PDF files
            output_path: Output path
            
        Returns:
            True if successful, False if PyPDF2 not available or merge failed
        """
        try:
            from PyPDF2 import PdfMerger
            
            if self.logger:
                self.logger.info("Attempting to merge PDF files using PyPDF2...")
            
            merger = PdfMerger()
            
            for idx, pdf in enumerate(pdf_files):
                if self.logger:
                    self.logger.debug(f"Adding to merge ({idx + 1}/{len(pdf_files)}): {pdf}")
                
                # Verify PDF file exists before adding
                if not os.path.exists(pdf):
                    if self.logger:
                        self.logger.warning(f"PDF file does not exist, skipping: {pdf}")
                    continue
                
                merger.append(pdf)
            
            if self.logger:
                self.logger.info("Writing merged PDF...")
            
            merger.write(output_path)
            merger.close()
            
            # Verify output file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if self.logger:
                    self.logger.info("PDF merge completed using PyPDF2")
                    self.logger.info(f"Merged PDF created: {output_path}")
                    self.logger.info(f"File size: {file_size} bytes")
                return True
            else:
                if self.logger:
                    self.logger.error("PyPDF2 merge completed but output file not found")
                return False
        
        except ImportError:
            if self.logger:
                self.logger.warning("PyPDF2 not available (pip install PyPDF2)")
            return False
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"PyPDF2 merge failed: {type(e).__name__}")
                self.logger.error(f"Error details: {e}")
            return False
    
    def _try_pdfunite_merge(self, pdf_files: List[str], output_path: str) -> bool:
        """
        Try merging using pdfunite.
        
        pdfunite is a command-line tool for PDF manipulation.
        It's used as a fallback when PyPDF2 is not available.
        
        Process:
        1. Build command with input files and output
        2. Execute via subprocess
        3. Verify output file was created
        
        Args:
            pdf_files: List of PDF files
            output_path: Output path
            
        Returns:
            True if successful, False if pdfunite not available or merge failed
        """
        try:
            if self.logger:
                self.logger.info("Attempting to merge PDF files using pdfunite...")
            
            # Build command: pdfunite input1.pdf input2.pdf ... output.pdf
            cmd = ['pdfunite'] + pdf_files + [output_path]
            
            if self.logger:
                self.logger.debug(f"Running: {' '.join(cmd)}")
            
            # Execute command
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Verify output file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if self.logger:
                    self.logger.info("PDF merge completed using pdfunite")
                    self.logger.info(f"Merged PDF created: {output_path}")
                    self.logger.info(f"File size: {file_size} bytes")
                return True
            else:
                if self.logger:
                    self.logger.error("pdfunite merge completed but output file not found")
                return False
        
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            if self.logger:
                self.logger.error(f"pdfunite merge failed: {type(e).__name__}")
                self.logger.error(f"Error details: {e}")
            return False


class TempFileManager:
    """
    Manages temporary files and directories.
    
    This class provides automatic cleanup of temporary resources through
    context manager protocol. It tracks all created temp files and
    directories, ensuring they are cleaned up when done.
    
    Features:
    - Automatic cleanup on context exit
    - Tracking of temp files and directories
    - Customizable file prefixes and suffixes
    - Error handling during cleanup
    
    Attributes:
        logger: Optional logging instance for debug output
        temp_dirs: List of created temporary directories
        temp_files: List of created temporary files
    
    Examples:
        >>> with TempFileManager(logger) as temp_mgr:
        ...     temp_file = temp_mgr.create_temp_file('.svg')
        ...     # Use temp_file...
        ...     # Auto-cleanup on exit
    """
    
    def __init__(self, logger: Optional[Any] = None):
        """
        Initialize TempFileManager with optional logger.
        
        Args:
            logger: Optional logging instance for debug output
        """
        self.logger = logger
        self.temp_dirs: List[str] = []
        self.temp_files: List[str] = []
        
        if self.logger:
            self.logger.info("TempFileManager initialized")
    
    def create_temp_dir(self) -> str:
        """
        Create a temporary directory.
        
        Creates a temporary directory using tempfile.mkdtemp() and
        tracks it for automatic cleanup.
        
        Returns:
            Path to temporary directory
            
        Examples:
            >>> temp_mgr = TempFileManager()
            >>> temp_dir = temp_mgr.create_temp_dir()
            '/tmp/tmpXXXXXX'
        """
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        
        if self.logger:
            self.logger.info(f"Created temporary directory: {temp_dir}")
        
        return temp_dir
    
    def create_temp_file(self, suffix: str = "", prefix: str = "inkautogen_") -> str:
        """
        Create a temporary file.
        
        Creates a temporary file with specified suffix and prefix.
        The file is created but not deleted, allowing it to be used
        and then cleaned up later.
        
        Args:
            suffix: File suffix/extension (e.g., '.svg', '.tmp')
            prefix: File prefix for naming
            
        Returns:
            Path to temporary file
            
        Examples:
            >>> temp_mgr = TempFileManager()
            >>> temp_file = temp_mgr.create_temp_file('.svg')
            '/tmp/inkautogen_XXXXXX.svg'
        """
        temp_file = tempfile.NamedTemporaryFile(
            suffix=suffix, prefix=prefix, delete=False
        )
        temp_file.close()
        
        self.temp_files.append(temp_file.name)
        
        if self.logger:
            self.logger.info(f"Created temporary file: {temp_file.name}")
        
        return temp_file.name
    
    def cleanup(self) -> None:
        """
        Clean up all temporary files and directories.
        
        This method is called automatically when exiting the context manager.
        It removes all tracked temporary files and directories.
        
        Process:
        1. Remove all temporary files
        2. Remove all temporary directories
        3. Clear tracking lists
        
        Note:
        Errors during cleanup are logged but don't raise exceptions,
        ensuring cleanup doesn't break the application.
        """
        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info("CLEANUP OPERATION")
            self.logger.info("=" * 60)
        
        # Clean up temporary files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    if self.logger:
                        self.logger.debug(f"Removed temporary file: {temp_file}")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Failed to remove temporary file {temp_file}: {e}")
        
        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    if self.logger:
                        self.logger.debug(f"Removed temporary directory: {temp_dir}")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")
        
        # Clear lists
        self.temp_files.clear()
        self.temp_dirs.clear()
        
        if self.logger:
            remaining_files = len(self.temp_files) + len(self.temp_dirs)
            self.logger.info(f"Cleanup completed. Remaining tracked items: {remaining_files}")
    
    def __enter__(self):
        """
        Context manager entry.
        
        Returns self for use in 'with' statement.
        """
        if self.logger:
            self.logger.debug("Entering TempFileManager context")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        
        Calls cleanup() when exiting 'with' block.
        Handles exceptions gracefully.
        """
        if self.logger:
            self.logger.debug("Exiting TempFileManager context")
            if exc_type is not None:
                self.logger.debug(f"Exception occurred: {exc_type}")
        
        self.cleanup()
