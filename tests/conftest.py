"""
Pytest configuration file for the ShortFactory project.
"""

import os
import sys
import pytest

# Add the project directory to the path
# This allows the tests to import modules from the src directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
