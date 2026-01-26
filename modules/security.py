#!/usr/bin/env python3
"""
Security utilities for InkAutoGen extension.
"""

import os
import re
import hashlib
import logging
from pathlib import Path
from typing import Optional, Set, List
from urllib.parse import urlparse

import config
from exceptions import FileSecurityError

logger = logging.getLogger(__name__)

class FileValidator:
    """Validates file security and integrity."""
    
    # Dangerous file extensions
    DANGEROUS_EXTENSIONS: Set[str] = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
        '.jar', '.app', '.deb', '.rpm', '.dmg', '.pkg', '.msi', '.sh',
        '.ps1', '.py', '.pl', '.rb', '.php', '.asp', '.jsp', '.cgi'
    }
    
    # Dangerous patterns in file content
    DANGEROUS_PATTERNS: List[re.Pattern] = [
        re.compile(r'<script[^>]*>', re.IGNORECASE),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'vbscript:', re.IGNORECASE),
        re.compile(r'data:text/html', re.IGNORECASE),
        re.compile(r'eval\s*\(', re.IGNORECASE),
        re.compile(r'exec\s*\(', re.IGNORECASE),
        re.compile(r'system\s*\(', re.IGNORECASE),
    ]
    
    # Safe path patterns
    SAFE_PATH_PATTERN: re.Pattern = re.compile(r'^[a-zA-Z0-9._/-]+$')
    
    @classmethod
    def validate_file_path(cls, file_path: str, allowed_extensions: Optional[Set[str]] = None) -> bool:
        """
        Validate file path for security.
        
        Args:
            file_path: Path to validate
            allowed_extensions: Set of allowed file extensions
            
        Returns:
            True if path is safe
            
        Raises:
            FileSecurityError: If path is unsafe
        """
        logger.info(f"Validating file path: {file_path}")
        if not file_path:
            logger.error("Empty file path provided")
            raise FileSecurityError("Empty file path", reason="empty_path")
        
        # Convert to absolute path and normalize
        try:
            abs_path = os.path.abspath(file_path)
            normalized_path = os.path.normpath(abs_path)
            logger.debug(f"Normalized path: {normalized_path}")
        except (ValueError, OSError) as e:
            logger.error(f"Invalid file path: {file_path}, error: {e}")
            raise FileSecurityError(f"Invalid file path: {file_path}", reason="invalid_path") from e
        
        # Check for path traversal attempts
        if '..' in file_path or file_path.startswith('~'):
            logger.error(f"Path traversal attempt detected: {file_path}")
            raise FileSecurityError(f"Unsafe path traversal: {file_path}", reason="path_traversal")
        
        # Check path pattern
        if not cls.SAFE_PATH_PATTERN.match(file_path):
            logger.error(f"Unsafe characters in path: {file_path}")
            raise FileSecurityError(f"Unsafe characters in path: {file_path}", reason="unsafe_chars")
        
        # Check file extension
        if allowed_extensions:
            file_ext = Path(file_path).suffix.lower()
            logger.debug(f"Checking extension {file_ext} against allowed extensions: {allowed_extensions}")
            if file_ext not in allowed_extensions:
                logger.error(f"File extension not allowed: {file_ext}")
                raise FileSecurityError(
                    f"File extension not allowed: {file_ext}",
                    reason="disallowed_extension"
                )
        
        # Check for dangerous extensions
        file_ext = Path(file_path).suffix.lower()
        logger.debug(f"Checking for dangerous extension: {file_ext}")
        if file_ext in cls.DANGEROUS_EXTENSIONS:
            logger.error(f"Dangerous file extension detected: {file_ext}")
            raise FileSecurityError(
                f"Dangerous file extension: {file_ext}",
                reason="dangerous_extension"
            )
        
        logger.info(f"File path validation successful: {file_path}")
        return True
    
    @classmethod
    def validate_file_size(cls, file_path: str) -> bool:
        """
        Validate file size.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if size is acceptable
            
        Raises:
            FileSecurityError: If file is too large
        """
        logger.info(f"Validating file size for: {file_path}")
        try:
            file_size = os.path.getsize(file_path)
            logger.debug(f"File size: {file_size} bytes, max allowed: {config.MAX_FILE_SIZE} bytes")
            if file_size > config.MAX_FILE_SIZE:
                logger.error(f"File too large: {file_size} bytes (max: {config.MAX_FILE_SIZE})")
                raise FileSecurityError(
                    config.ERROR_MESSAGES["file_too_large"].format(
                        size=file_size, max_size=config.MAX_FILE_SIZE
                    ),
                    reason="file_too_large"
                )
            logger.info(f"File size validation successful: {file_path}")
            return True
        except OSError as e:
            logger.error(f"Cannot access file: {file_path}, error: {e}")
            raise FileSecurityError(f"Cannot access file: {file_path}", reason="access_error") from e
    
    @classmethod
    def validate_file_content(cls, file_path: str, content_type: str = "csv") -> bool:
        """
        Validate file content for dangerous patterns.
        
        Args:
            file_path: Path to file
            content_type: Type of content (csv, image, etc.)
            
        Returns:
            True if content is safe
            
        Raises:
            FileSecurityError: If content contains dangerous patterns
        """
        logger.info(f"Validating file content for {content_type}: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(8192)  # Read first 8KB for pattern detection
            logger.debug(f"Read {len(content)} bytes from file for content validation")
            
            # Check for dangerous patterns
            for i, pattern in enumerate(cls.DANGEROUS_PATTERNS):
                if pattern.search(content):
                    logger.error(f"Dangerous pattern detected (pattern {i}) in {content_type} file: {file_path}")
                    raise FileSecurityError(
                        f"Dangerous content detected in {content_type} file",
                        reason="dangerous_content"
                    )
            
            logger.info(f"File content validation successful: {file_path}")
            return True
        except (UnicodeDecodeError, OSError) as e:
            # For binary files (like images), we can't check text patterns
            if content_type == "image":
                logger.debug(f"Skipping content validation for binary image file: {file_path}")
                return True
            logger.error(f"Cannot read file content: {file_path}, error: {e}")
            raise FileSecurityError(f"Cannot read file content: {file_path}", reason="read_error") from e
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename for safe use.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        logger.info(f"Sanitizing filename: {filename}")
        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"|?*\x00-\x1f]', '', filename)
        logger.debug(f"Removed dangerous characters")
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)
        logger.debug(f"Removed control characters")
        
        # Replace multiple spaces with single space
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')
        
        # Ensure filename is not empty
        if not sanitized:
            logger.warning("Sanitized filename is empty, using default")
            sanitized = "unnamed_file"
        
        # Truncate if too long
        if len(sanitized) > 255:
            logger.debug(f"Filename too long ({len(sanitized)} chars), truncating to 255")
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext
        
        logger.info(f"Sanitized filename: {sanitized}")
        return sanitized
    
    @classmethod
    def validate_csv_file(cls, csv_path: str) -> bool:
        """
        Comprehensive CSV file validation.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            True if CSV file is valid
            
        Raises:
            FileSecurityError: If CSV file is invalid
        """
        logger.info(f"Starting comprehensive CSV validation: {csv_path}")
        # Validate file path
        cls.validate_file_path(csv_path, config.ALLOWED_CSV_EXTENSIONS)
        
        # Validate file size
        cls.validate_file_size(csv_path)
        
        # Validate file content
        cls.validate_file_content(csv_path, "csv")
        
        logger.info(f"CSV file validation completed successfully: {csv_path}")
        return True
    
    @classmethod
    def validate_image_file(cls, image_path: str) -> bool:
        """
        Comprehensive image file validation.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if image file is valid
            
        Raises:
            FileSecurityError: If image file is invalid
        """
        logger.info(f"Starting comprehensive image validation: {image_path}")
        # Validate file path
        cls.validate_file_path(image_path, config.ALLOWED_IMAGE_EXTENSIONS)
        
        # Validate file size
        cls.validate_file_size(image_path)
        
        # Validate file content (basic check for images)
        cls.validate_file_content(image_path, "image")
        
        logger.info(f"Image file validation completed successfully: {image_path}")
        return True


class SecurityUtils:
    """General security utilities."""
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """
        Sanitize user input for safe processing.
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        logger.debug(f"Sanitizing input (length: {len(text) if text else 0}, max: {max_length})")
        if not text:
            logger.debug("Empty input, returning empty string")
            return ""
        
        # Truncate if too long
        if len(text) > max_length:
            logger.debug(f"Input truncated from {len(text)} to {max_length} characters")
            text = text[:max_length]
        
        # Remove null bytes and control characters
        text = text.replace('\x00', '')
        text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        logger.debug(f"Input sanitized successfully (result length: {len(text)})")
        return text
    
    @staticmethod
    def generate_safe_hash(data: str, salt: str = "") -> str:
        """
        Generate a safe hash for data.
        
        Args:
            data: Data to hash
            salt: Salt for hashing
            
        Returns:
            Safe hash string
        """
        logger.debug(f"Generating SHA256 hash (salt: {'provided' if salt else 'none'})")
        combined = f"{data}{salt}"
        hash_result = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        logger.debug(f"Hash generated: {hash_result[:16]}...")
        return hash_result
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL for safety.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is safe
        """
        logger.debug(f"Validating URL: {url}")
        try:
            parsed = urlparse(url)
            logger.debug(f"Parsed URL - scheme: {parsed.scheme}, hostname: {parsed.hostname}")
            
            # Only allow http and https schemes
            if parsed.scheme not in ('http', 'https'):
                logger.warning(f"URL scheme not allowed: {parsed.scheme}")
                return False
            
            # Disallow localhost and private IPs in production
            # (This is a basic check - more sophisticated checks may be needed)
            if parsed.hostname in ('localhost', '127.0.0.1', '::1'):
                logger.warning(f"URL hostname not allowed: {parsed.hostname}")
                return False
            
            logger.info(f"URL validation successful: {url}")
            return True
        except Exception as e:
            logger.error(f"URL validation error for {url}: {e}")
            return False
