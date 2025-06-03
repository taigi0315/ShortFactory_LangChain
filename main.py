"""
Entry point for the ShortFactory application.
This is a simplified interface that runs the main application module.
"""
import sys
import os

# Add src directory to Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the main function from the src package
try:
    from src.main import main
except ImportError as e:
    print(f"Error importing ShortFactory module: {e}")
    print("Make sure you have installed all required dependencies.")
    sys.exit(1)

if __name__ == "__main__":
    # Run the main function from the src module
    main()