#!/usr/bin/env python3
"""
Setup script for InkAutoGen - Batch Processing for Inkscape
"""

import os
from setuptools import setup, find_packages

# Read the version from version.py
def get_version():
    """Get version from version.py module."""
    version_file = os.path.join(os.path.dirname(__file__), 'modules', 'version.py')
    version_dict = {}
    with open(version_file, 'r') as f:
        exec(f.read(), version_dict)
    return version_dict.get('__version__', '2.0.0')

# Read README for long description
def get_long_description():
    """Get long description from README.md if available."""
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "InkAutoGen - Batch Processing for Inkscape"

setup(
    name="inkautogen",
    version=get_version(),
    author="Siddha Siddhant",
    author_email="dev@siddhasiddhant.com",
    description="Automated batch SVG template processing with CSV data for Inkscape",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/siddhasiddhant/inkautogen",
    license="MIT",
    packages=find_packages(exclude=['tests*', 'docs*', 'examples*']),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "lxml>=4.9.0",
        "chardet>=5.0.0",
        "PyPDF2>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "inkautogen=inkautogen:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
