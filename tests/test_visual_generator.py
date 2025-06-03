"""
Tests for the VisualGenerator class.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pytest

from src.generators.visual_generator import VisualGenerator
from src.models.schemas import CharacterDescription, GenerationResult


class TestVisualGenerator(unittest.TestCase):
    """Test suite for the VisualGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.png")
        
        # Sample test data
        self.overall_style = "Watercolor painting, vibrant colors, fantastical, soft lighting"
        self.main_characters = [
            CharacterDescription(
                name="Nibbles", 
                appearance="Small red squirrel with a bushy tail and bright eyes"
            ),
            CharacterDescription(
                name="Wizardo", 
                appearance="Elderly man with long gray beard, purple robes, and a pointed hat"
            )
        ]
        self.scene_description = "Nibbles steals the magical acorn while Wizardo sleeps under a tree"
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove test directory if it exists
        if os.path.exists(self.temp_dir):
            # Remove any files in the directory
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)
    
    @patch('src.generators.visual_generator.Config')
    @patch('src.generators.visual_generator.OpenAI')
    @patch('requests.get')
    def test_generate_dalle_image_success(self, mock_get, mock_openai_class, mock_config):
        """Test successful image generation with DALL-E."""
        # Configure mocks
        mock_config.get_api_key.return_value = "test_api_key"
        
        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_data = MagicMock()
        mock_data.url = "https://test-url.com/image.png"
        mock_response = MagicMock()
        mock_response.data = [mock_data]
        mock_client.images.generate.return_value = mock_response
        
        # Mock the image download
        mock_get_response = MagicMock()
        mock_get_response.raise_for_status.return_value = None
        mock_get_response.content = b"test image content"
        mock_get.return_value = mock_get_response
        
        # Initialize the generator with DALL-E provider
        with patch('src.generators.visual_generator.OPENAI_AVAILABLE', True):
            generator = VisualGenerator(provider="openai_dalle")
            
            # Call the method
            result = generator.generate_image(
                self.overall_style,
                self.main_characters,
                self.scene_description,
                self.test_image_path
            )
            
            # Assertions
            self.assertTrue(result.success)
            self.assertEqual(result.output_path, self.test_image_path)
            mock_client.images.generate.assert_called_once()
            mock_get.assert_called_once_with("https://test-url.com/image.png")
    
    @patch('src.generators.visual_generator.Config')
    @patch('src.generators.visual_generator.aiplatform')
    @patch('src.generators.visual_generator.ImageGenerationModel')
    def test_generate_vertex_ai_image_success(self, mock_image_model_class, mock_aiplatform, mock_config):
        """Test successful image generation with Google Vertex AI."""
        # Configure mocks
        mock_config.get_api_key.return_value = "test_api_key"
        mock_config.GCP_PROJECT_ID = "test-project"
        mock_config.GCP_LOCATION = "us-central1"
        
        # Mock the Vertex AI model and response
        mock_model = MagicMock()
        mock_image_model_class.from_pretrained.return_value = mock_model
        mock_image = MagicMock()
        mock_response = MagicMock()
        mock_response.images = [mock_image]
        mock_model.generate_images.return_value = mock_response
        
        # Initialize the generator with Vertex AI provider
        with patch('src.generators.visual_generator.VERTEX_AI_AVAILABLE', True):
            generator = VisualGenerator(
                provider="google_vertex_ai_image",
                gcp_project_id="test-project",
                gcp_location="us-central1"
            )
            
            # Call the method
            result = generator.generate_image(
                self.overall_style,
                self.main_characters,
                self.scene_description,
                self.test_image_path
            )
            
            # Assertions
            self.assertTrue(result.success)
            self.assertEqual(result.output_path, self.test_image_path)
            mock_aiplatform.init.assert_called_once_with(project="test-project", location="us-central1")
            mock_model.generate_images.assert_called_once()
    
    @patch('src.generators.visual_generator.Config')
    def test_generate_image_invalid_provider(self, mock_config):
        """Test initialization with invalid provider raises ValueError."""
        mock_config.get_api_key.return_value = "test_api_key"
        
        with self.assertRaises(ValueError):
            VisualGenerator(provider="invalid_provider")
    
    @patch('src.generators.visual_generator.Config')
    @patch('src.generators.visual_generator.OPENAI_AVAILABLE', False)
    def test_provider_not_available(self, mock_config):
        """Test behavior when the requested provider is not available."""
        mock_config.get_api_key.return_value = "test_api_key"
        
        # Initialize with unavailable provider
        generator = VisualGenerator(provider="openai_dalle")
        
        # Call the method
        result = generator.generate_image(
            self.overall_style,
            self.main_characters,
            self.scene_description,
            self.test_image_path
        )
        
        # Assertions
        self.assertFalse(result.success)
        self.assertIn("not properly set up", result.error)
    
    @patch('src.generators.visual_generator.Config')
    @patch('src.generators.visual_generator.OpenAI')
    def test_smart_prompt_construction(self, mock_openai_class, mock_config):
        """Test that character descriptions are properly integrated into the prompt."""
        # Configure mocks
        mock_config.get_api_key.return_value = "test_api_key"
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.data = [MagicMock(url="https://test-url.com/image.png")]
        mock_client.images.generate.return_value = mock_response
        
        # Initialize the generator
        with patch('src.generators.visual_generator.OPENAI_AVAILABLE', True):
            with patch('requests.get') as mock_get:
                mock_get_response = MagicMock()
                mock_get_response.content = b"test image content"
                mock_get.return_value = mock_get_response
                
                generator = VisualGenerator(provider="openai_dalle")
                
                # Call the method
                result = generator.generate_image(
                    self.overall_style,
                    self.main_characters,
                    "Nibbles steals the magical acorn",
                    self.test_image_path
                )
                
                # Get the prompt that was passed to the client
                call_args = mock_client.images.generate.call_args
                prompt = call_args[1]['prompt']
                
                # Assertions
                self.assertIn("Watercolor painting", prompt)
                self.assertIn("Small red squirrel", prompt)  # Character description should be included


if __name__ == "__main__":
    unittest.main()
