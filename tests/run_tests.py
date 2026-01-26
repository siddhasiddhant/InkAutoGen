#!/usr/bin/env python3
"""
Test runner for InkAutoGen test suite.

This script runs all test suites and provides a summary of results.
Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --verbose          # Run with verbose output
    python run_tests.py --specific <test>  # Run specific test module
"""

import sys
import os
import unittest
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def discover_and_run_tests(test_pattern=None, verbosity=2):
    """Discover and run tests matching the pattern."""
    # Test directory
    test_dir = Path(__file__).parent
    
    # Discover tests
    if test_pattern:
        # Run specific test module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(f"tests.{test_pattern}")
    else:
        # Discover all tests
        discovery = unittest.TestLoader().discover(
            start_dir=str(test_dir),
            pattern='test_*.py'
        )
        suite = discovery
    
    # Run tests
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    # Return exit code based on results
    return 0 if result.wasSuccessful() else 1

def print_test_info():
    """Print information about available tests."""
    test_dir = Path(__file__).parent
    test_files = list(test_dir.glob('test_*.py'))
    
    print("Available test modules:")
    for test_file in test_files:
        module_name = test_file.stem
        print(f"  - {module_name}")
    
    print(f"\nTotal test modules: {len(test_files)}")

def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description='InkAutoGen Test Runner')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Run with verbose output')
    parser.add_argument('--specific', '-s', type=str,
                      help='Run specific test module (e.g., unicode_handling)')
    parser.add_argument('--list', '-l', action='store_true',
                      help='List available test modules')
    parser.add_argument('--unit', '-u', action='store_true',
                      help='Run unit tests only (fast)')
    
    args = parser.parse_args()
    
    if args.list:
        print_test_info()
        return 0
    
    # Set verbosity
    verbosity = 2 if args.verbose else 1
    
    print("=" * 70)
    print("INKAUTOGEN TEST SUITE")
    print("=" * 70)
    
    if args.specific:
        print(f"Running specific test: {args.specific}")
    else:
        print("Running all test suites")
    
    print(f"Verbosity level: {verbosity}")
    print("=" * 70)
    
    # Run tests
    exit_code = discover_and_run_tests(
        test_pattern=args.specific,
        verbosity=verbosity
    )
    
    # Print summary
    print("=" * 70)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())