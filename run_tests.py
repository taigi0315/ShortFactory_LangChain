#!/usr/bin/env python
"""
Test runner script for the ShortFactory project.
This script makes it easy to run all tests or specific test modules.
"""

import os
import sys
import argparse
import subprocess


def run_tests(test_path=None, verbose=False):
    """Run the tests using pytest.
    
    Args:
        test_path: Optional path to specific test file or directory
        verbose: If True, run tests with verbose output
    """
    # Build the pytest command
    # Use sys.executable to ensure we're using the pytest from the current Python environment
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add verbosity if requested
    if verbose:
        cmd.append("-v")
    
    # Add coverage reporting
    cmd.extend(["--cov=src", "--cov-report=term"])
    
    # Add specific test path if provided
    if test_path:
        cmd.append(test_path)
    
    # Run the tests
    result = subprocess.run(cmd)
    return result.returncode


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run ShortFactory tests")
    parser.add_argument(
        "test_path", 
        nargs="?", 
        default=None,
        help="Specific test file or directory to run"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    exit_code = run_tests(args.test_path, args.verbose)
    sys.exit(exit_code)
