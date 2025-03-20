#!/usr/bin/env python
# tests/run_tests.py
"""
Test runner script for the StudiumDashboard project.

This script discovers and runs all tests in the tests directory,
providing a unified way to execute the test suite.

Usage:
    python run_tests.py           # Run all tests
    python run_tests.py -v        # Run all tests with verbose output
    python run_tests.py <pattern> # Run tests matching the pattern
"""

import unittest
import sys
import os


def run_tests(pattern=None, verbosity=1):
    """
    Discover and run tests, optionally filtered by pattern.

    Args:
        pattern: Pattern to filter test files (default: None)
        verbosity: Verbosity level (1=normal, 2=verbose)

    Returns:
        True if all tests passed, False otherwise
    """
    # Add project root to path to ensure imports work correctly
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    print(f"{'=' * 70}")
    print(f"Running StudiumDashboard tests")
    print(f"{'=' * 70}")

    # Create test suite
    loader = unittest.TestLoader()

    if pattern:
        print(f"Running tests matching pattern: {pattern}")
        suite = loader.loadTestsFromName(pattern)
    else:
        start_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Discovering tests in: {start_dir}")
        suite = loader.discover(start_dir)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Print summary
    print(f"\n{'=' * 70}")
    print(f"Test Summary:")
    print(f"  Ran {result.testsRun} tests")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    print(f"{'=' * 70}")

    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    # Parse command line arguments
    verbosity = 1
    pattern = None

    if len(sys.argv) > 1:
        if sys.argv[1] == "-v":
            verbosity = 2
        else:
            pattern = sys.argv[1]

    # Run tests
    success = run_tests(pattern, verbosity)

    # Set exit code based on test results
    sys.exit(0 if success else 1)