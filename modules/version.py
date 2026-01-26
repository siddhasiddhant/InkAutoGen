#!/usr/bin/env python3
"""
Version information for InkAutoGen extension.
"""

__version__ = "2.0.0"
__author__ = "Siddha Siddhant"
__email__ = "dev@siddhasiddhant.com"
__license__ = "MIT"

# Version information as dict for programmatic access
VERSION_INFO = {
    "major": 2,
    "minor": 0,
    "patch": 0,
    "full": __version__,
    "author": __author__,
    "email": __email__,
    "license": __license__
}


def get_version():
    """Get the full version string."""
    return __version__


def get_version_info():
    """Get complete version information."""
    return VERSION_INFO


def format_version(major=None, minor=None, patch=None):
    """Format version from components."""
    if major is None:
        major = VERSION_INFO["major"]
    if minor is None:
        minor = VERSION_INFO["minor"]
    if patch is None:
        patch = VERSION_INFO["patch"]
    return f"{major}.{minor}.{patch}"


# For backward compatibility
VERSION = __version__
