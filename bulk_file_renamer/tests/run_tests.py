#!/usr/bin/env python3
# Copyright (c) 2024 Dominic Ritzmann. All rights reserved.
# 
# This software is licensed under the Bulk File Renamer License.
# See LICENSE file for full license terms.

"""
Test runner script for the bulk file renamer application.
This script runs all tests and provides a comprehensive test report.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_tests(test_pattern=None, verbose=False, coverage=False, parallel=False):
    """
    Run the test suite with the specified options.
    
    Args:
        test_pattern: Pattern to match test files (e.g., "test_file_operations")
        verbose: Enable verbose output
        coverage: Enable coverage reporting
        parallel: Run tests in parallel
    """
    
    # Get the test directory
    test_dir = Path(__file__).parent
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test directory
    cmd.append(str(test_dir))
    
    # Add pattern if specified
    if test_pattern:
        cmd.extend(["-k", test_pattern])
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Add parallel execution if requested
    if parallel:
        try:
            import pytest_xdist
            cmd.extend(["-n", "auto"])
        except ImportError:
            print("Warning: pytest-xdist not installed, running tests sequentially")
    
    # Add additional pytest options
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker handling
        "--disable-warnings",  # Disable warnings for cleaner output
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("=" * 60)
    
    # Run the tests
    try:
        result = subprocess.run(cmd, cwd=test_dir.parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def list_test_files():
    """List all available test files."""
    test_dir = Path(__file__).parent
    
    test_files = []
    for file in test_dir.glob("test_*.py"):
        if file.name != "run_tests.py":
            test_files.append(file.stem)
    
    print("Available test files:")
    for test_file in sorted(test_files):
        print(f"  - {test_file}")
    
    return test_files


def run_specific_tests():
    """Run tests for specific features."""
    test_categories = {
        "file_operations": "Test file operations (add, rename, delete)",
        "naming": "Test naming utilities and preview generation",
        "settings": "Test settings management",
        "profiles": "Test profile management",
        "ui": "Test UI components",
        "integration": "Test component integration",
        "all": "Run all tests"
    }
    
    print("Available test categories:")
    for category, description in test_categories.items():
        print(f"  {category}: {description}")
    
    return test_categories


def main():
    """Main function to handle command line arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Run tests for the bulk file renamer application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py -v                 # Run all tests with verbose output
  python run_tests.py -k file_operations # Run only file operation tests
  python run_tests.py --coverage         # Run tests with coverage report
  python run_tests.py --parallel         # Run tests in parallel
  python run_tests.py --list             # List available test files
  python run_tests.py --categories       # List test categories
        """
    )
    
    parser.add_argument(
        "-k", "--pattern",
        help="Pattern to match test files or test names"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Enable coverage reporting"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available test files"
    )
    
    parser.add_argument(
        "--categories",
        action="store_true",
        help="List available test categories"
    )
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.list:
        list_test_files()
        return 0
    
    if args.categories:
        run_specific_tests()
        return 0
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("Error: pytest is not installed. Please install it with:")
        print("  pip install pytest")
        return 1
    
    # Check if PySide6 is available
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print("Error: PySide6 is not installed. Please install it with:")
        print("  pip install PySide6")
        return 1
    
    # Run the tests
    print("Bulk File Renamer - Test Suite")
    print("=" * 60)
    
    returncode = run_tests(
        test_pattern=args.pattern,
        verbose=args.verbose,
        coverage=args.coverage,
        parallel=args.parallel
    )
    
    if returncode == 0:
        print("\n" + "=" * 60)
        print("All tests passed! ✅")
    else:
        print("\n" + "=" * 60)
        print("Some tests failed! ❌")
    
    return returncode


if __name__ == "__main__":
    sys.exit(main())
