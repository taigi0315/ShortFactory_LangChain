"""
Tests for the NarrationGenerator class.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pytest
from pydub import AudioSegment

from src.generators.narration_generator import NarrationGenerator
from src.models.schemas import GenerationResult


class TestNarrationGenerator(unittest.TestCase):
    """Test suite for the NarrationGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_audio_path = os.path.join(self.temp_dir, "test_narration.mp3")
        
        # Create a small test audio file
        self.create_test_audio()
        
    def create_test_audio(self):
        """Create a test audio file for duration testing."""
        # Create a 2-second silent audio segment
        silent_segment = AudioSegment.silent(duration=2000)
        os.makedirs(os.path.dirname(self.test_audio_path), exist_ok=True)
        silent_segment.export(self.test_audio_path, format="mp3")
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove test audio file if it exists
        if os.path.exists(self.test_audio_path):
            os.remove(self.test_audio_path)
            
        # Remove temp directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    @patch('src.generators.narration_generator.Config')
    @patch('requests.post')
    def test_generate_elevenlabs_narration_success(self, mock_post, mock_config):
        """Test successful narration generation with ElevenLabs."""
        # Configure mocks
        mock_config.get_api_key.return_value = "test_api_key"
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [b"test audio content"]
        mock_post.return_value = mock_response
        
        # Initialize the generator
        generator = NarrationGenerator(provider="elevenlabs")
        
        # Create a temp file for the output
        output_path = os.path.join(self.temp_dir, "output.mp3")
        
        # Call the method
        result = generator.generate_narration("Test narration text", output_path)
        
        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(result.output_path, output_path)
        self.assertEqual(result.error, "")
        mock_post.assert_called_once()
        
    @patch('src.generators.narration_generator.Config')
    @patch('requests.post')
    def test_generate_elevenlabs_narration_failure(self, mock_post, mock_config):
        """Test handling of narration generation failure with ElevenLabs."""
        # Configure mocks
        mock_config.get_api_key.return_value = "test_api_key"
        
        # Create a mock response that raises an exception
        mock_post.side_effect = Exception("Test error")
        
        # Initialize the generator
        generator = NarrationGenerator(provider="elevenlabs")
        
        # Create a temp file for the output
        output_path = os.path.join(self.temp_dir, "output.mp3")
        
        # Call the method
        result = generator.generate_narration("Test narration text", output_path)
        
        # Assertions
        self.assertFalse(result.success)
        self.assertEqual(result.output_path, "")
        self.assertIn("Test error", result.error)
    
    @patch('src.generators.narration_generator.Config')
    def test_invalid_provider(self, mock_config):
        """Test initialization with invalid provider raises ValueError."""
        mock_config.get_api_key.return_value = "test_api_key"
        
        with self.assertRaises(ValueError):
            NarrationGenerator(provider="invalid_provider")
    
    @patch('src.generators.narration_generator.Config')
    def test_get_audio_duration(self, mock_config):
        """Test getting audio duration."""
        # Configure mocks
        mock_config.get_api_key.return_value = "test_api_key"
        
        # Initialize the generator
        generator = NarrationGenerator(provider="elevenlabs")
        
        # Call the method
        duration = generator.get_audio_duration(self.test_audio_path)
        
        # Assertions
        self.assertAlmostEqual(duration, 2.0, places=1)
    
    @patch('src.generators.narration_generator.Config')
    def test_no_api_key(self, mock_config):
        """Test behavior when API key is not set."""
        # Configure mocks
        mock_config.get_api_key.return_value = None
        
        # Initialize the generator
        generator = NarrationGenerator(provider="elevenlabs")
        
        # Call the method
        result = generator.generate_narration("Test narration text", "output.mp3")
        
        # Assertions
        self.assertFalse(result.success)
        self.assertIn("API Key not set", result.error)


if __name__ == "__main__":
    unittest.main()
