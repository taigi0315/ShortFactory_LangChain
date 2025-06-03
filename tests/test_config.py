"""
Tests for the Config class.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pytest

from src.config.config import Config


class TestConfig(unittest.TestCase):
    """Test suite for the Config class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Reset Config singleton state before each test
        if hasattr(Config, '_instance'):
            Config._instance = None
        
        # Use a temporary directory for test output
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    @patch('os.environ')
    @patch('src.config.config.load_dotenv')
    def test_load_environment_variables(self, mock_load_dotenv, mock_environ):
        """Test loading environment variables from .env file."""
        # Configure the mock environment variables
        mock_environ.get.side_effect = lambda key, default=None: {
            'OPENAI_API_KEY': 'test_openai_key',
            'GOOGLE_API_KEY': 'test_google_key',
            'ELEVEN_LABS_API_KEY': 'test_eleven_labs_key',
            'ELEVENLABS_VOICE_ID': 'test_voice_id',
            'GCP_PROJECT_ID': 'test-project',
            'GCP_LOCATION': 'us-central1',
            'OUTPUT_DIR': self.temp_dir
        }.get(key, default)
        
        # Initialize Config
        config = Config()
        
        # Verify dotenv was loaded
        mock_load_dotenv.assert_called_once()
        
        # Verify environment variables were loaded
        self.assertEqual(config.get_api_key('openai'), 'test_openai_key')
        self.assertEqual(config.get_api_key('google'), 'test_google_key')
        self.assertEqual(config.get_api_key('eleven_labs'), 'test_eleven_labs_key')
        self.assertEqual(config.ELEVENLABS_VOICE_ID, 'test_voice_id')
        self.assertEqual(config.GCP_PROJECT_ID, 'test-project')
        self.assertEqual(config.GCP_LOCATION, 'us-central1')
        self.assertEqual(config.OUTPUT_DIR, self.temp_dir)
    
    @patch('os.environ')
    @patch('src.config.config.load_dotenv')
    def test_default_values(self, mock_load_dotenv, mock_environ):
        """Test default values are used when environment variables are not set."""
        # Configure the mock to return None for all environment variables
        mock_environ.get.return_value = None
        
        # Initialize Config
        config = Config()
        
        # Verify default values were used
        self.assertEqual(config.ELEVENLABS_VOICE_ID, "21m00Tcm4TlvDq8ikWAM")  # Default voice ID
        self.assertEqual(config.GCP_PROJECT_ID, "default-project-id")  # Default project ID
        self.assertEqual(config.GCP_LOCATION, "us-central1")  # Default location
        self.assertEqual(config.OUTPUT_DIR, os.path.join(os.getcwd(), "outputs"))  # Default output directory
    
    @patch('os.environ')
    @patch('src.config.config.load_dotenv')
    @patch('os.makedirs')
    def test_create_directories(self, mock_makedirs, mock_load_dotenv, mock_environ):
        """Test creating output directories."""
        # Configure the mock environment variables
        mock_environ.get.side_effect = lambda key, default=None: {
            'OUTPUT_DIR': self.temp_dir
        }.get(key, default)
        
        # Initialize Config
        config = Config()
        
        # Call create directories method
        config.create_directories()
        
        # Verify directories were created
        mock_makedirs.assert_called()
        self.assertIn(self.temp_dir, mock_makedirs.call_args_list[0][0][0])
    
    @patch('os.environ')
    @patch('src.config.config.load_dotenv')
    def test_get_api_key_unknown_provider(self, mock_load_dotenv, mock_environ):
        """Test getting API key for an unknown provider."""
        # Initialize Config
        config = Config()
        
        # Verify getting API key for unknown provider returns None
        self.assertIsNone(config.get_api_key('unknown_provider'))
    
    @patch('os.environ')
    @patch('src.config.config.load_dotenv')
    def test_singleton_pattern(self, mock_load_dotenv, mock_environ):
        """Test Config follows the Singleton pattern."""
        # Configure the mock environment variables
        mock_environ.get.return_value = 'test_value'
        
        # Create first instance
        config1 = Config()
        
        # Create second instance
        config2 = Config()
        
        # Verify both instances are the same object
        self.assertIs(config1, config2)
        
        # Verify load_dotenv was called only once
        mock_load_dotenv.assert_called_once()


if __name__ == "__main__":
    unittest.main()
