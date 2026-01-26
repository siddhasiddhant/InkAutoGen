#!/usr/bin/env python3
"""
Custom exception classes for InkAutoGen extension.
"""

from typing import Optional, Any, Dict

class InkAutoGenError(Exception):
    """Base exception class for InkAutoGen extension."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

class CSVProcessingError(InkAutoGenError):
    """Raised when CSV processing fails."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 line_number: Optional[int] = None, **kwargs):
        context = kwargs.get('context', {})
        if file_path:
            context['file_path'] = file_path
        if line_number:
            context['line_number'] = line_number
        super().__init__(message, error_code="CSV_ERROR", context=context, **kwargs)


class SVGTemplateError(InkAutoGenError):
    """Raised when SVG template processing fails."""
    
    def __init__(self, message: str, element_type: Optional[str] = None,
                 element_id: Optional[str] = None, **kwargs):
        context = kwargs.get('context', {})
        if element_type:
            context['element_type'] = element_type
        if element_id:
            context['element_id'] = element_id
        super().__init__(message, error_code="SVG_ERROR", context=context, **kwargs)


class FileSecurityError(InkAutoGenError):
    """Raised when file security checks fail."""
    
    def __init__(self, message: str, file_path: Optional[str] = None,
                 reason: Optional[str] = None, **kwargs):
        context = kwargs.get('context', {})
        if file_path:
            context['file_path'] = file_path
        if reason:
            context['reason'] = reason
        super().__init__(message, error_code="SECURITY_ERROR", context=context, **kwargs)


class ExportError(InkAutoGenError):
    """Raised when file export fails."""
    
    def __init__(self, message: str, export_format: Optional[str] = None,
                 output_path: Optional[str] = None, **kwargs):
        context = kwargs.get('context', {})
        if export_format:
            context['export_format'] = export_format
        if output_path:
            context['output_path'] = output_path
        super().__init__(message, error_code="EXPORT_ERROR", context=context, **kwargs)


class ValidationError(InkAutoGenError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field_name: Optional[str] = None,
                 field_value: Optional[Any] = None, **kwargs):
        context = kwargs.get('context', {})
        if field_name:
            context['field_name'] = field_name
        if field_value is not None:
            context['field_value'] = str(field_value)
        super().__init__(message, error_code="VALIDATION_ERROR", context=context, **kwargs)


class PerformanceError(InkAutoGenError):
    """Raised when performance limits are exceeded."""
    
    def __init__(self, message: str, limit_type: Optional[str] = None,
                 current_value: Optional[Any] = None, limit: Optional[Any] = None, **kwargs):
        context = kwargs.get('context', {})
        if limit_type:
            context['limit_type'] = limit_type
        if current_value is not None:
            context['current_value'] = str(current_value)
        if limit is not None:
            context['limit'] = str(limit)
        super().__init__(message, error_code="PERFORMANCE_ERROR", context=context, **kwargs)


class ConfigurationError(InkAutoGenError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_value: Optional[Any] = None, **kwargs):
        context = kwargs.get('context', {})
        if config_key:
            context['config_key'] = config_key
        if config_value is not None:
            context['config_value'] = str(config_value)
        super().__init__(message, error_code="CONFIG_ERROR", context=context, **kwargs)
