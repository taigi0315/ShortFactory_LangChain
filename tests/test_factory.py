"""
Tests for the ShortVideoFactory class.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pytest

from src.core.factory import ShortVideoFactory
from src.models.schemas import (
    StoryWithScenes, Scene, CharacterDescription, 
    GenerationResult, VideoCreationConfig
)


class TestShortVideoFactory(unittest.TestCase):
    """Test suite for the ShortVideoFactory class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        self.test_output_dir = os.path.join(self.temp_dir, "outputs")
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # Create mock generators and assembler
        self.mock_story_generator = MagicMock()
        self.mock_narration_generator = MagicMock()
        self.mock_visual_generator = MagicMock()
        self.mock_video_assembler = MagicMock()
        
        # Create a sample story for testing
        self.sample_story = StoryWithScenes(
            title="Test Story",
            full_story_summary="A short test story",
            overall_image_style="Cartoon style",
            main_characters=[
                CharacterDescription(name="Character1", appearance="Description1"),
                CharacterDescription(name="Character2", appearance="Description2")
            ],
            scenes=[
                Scene(
                    scene_number=1, 
                    visual_description="Scene 1 description", 
                    narration_text="Scene 1 narration"
                ),
                Scene(
                    scene_number=2, 
                    visual_description="Scene 2 description", 
                    narration_text="Scene 2 narration"
                )
            ]
        )
        
        # Create a sample config
        self.video_config = VideoCreationConfig(
            output_dir=self.test_output_dir,
            scenes_per_story=2,
            subject="Test subject",
            llm_provider="test_llm",
            tts_provider="test_tts",
            image_provider="test_image"
        )
        
        # Initialize the factory with mocks
        self.factory = ShortVideoFactory(
            story_generator=self.mock_story_generator,
            narration_generator=self.mock_narration_generator,
            visual_generator=self.mock_visual_generator,
            video_assembler=self.mock_video_assembler,
            video_config=self.video_config
        )
        
        # Configure mocks to return successful results
        self.mock_story_generator.generate_structured_story.return_value = self.sample_story
        
        # Mock successful narration generation
        def mock_generate_narration(text, output_path):
            # Create an empty file for the test
            with open(output_path, 'wb') as f:
                f.write(b'dummy audio data')
            return GenerationResult(
                success=True,
                output_path=output_path,
                error=""
            )
        self.mock_narration_generator.generate_narration.side_effect = mock_generate_narration
        self.mock_narration_generator.get_audio_duration.return_value = 3.0
        
        # Mock successful image generation
        def mock_generate_image(style, chars, desc, output_path):
            # Create an empty file for the test
            with open(output_path, 'wb') as f:
                f.write(b'dummy image data')
            return GenerationResult(
                success=True,
                output_path=output_path,
                error=""
            )
        self.mock_visual_generator.generate_image.side_effect = mock_generate_image
        
        # Mock successful video assembly
        def mock_assemble_video(images, audios, durations, output_path):
            # Create an empty file for the test
            with open(output_path, 'wb') as f:
                f.write(b'dummy video data')
            return GenerationResult(
                success=True,
                output_path=output_path,
                error=""
            )
        self.mock_video_assembler.assemble_video.side_effect = mock_assemble_video
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove test directory if it exists
        if os.path.exists(self.test_output_dir):
            # Remove files in the directory
            for file in os.listdir(self.test_output_dir):
                os.remove(os.path.join(self.test_output_dir, file))
            os.rmdir(self.test_output_dir)
        
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_create_short_video_success(self):
        """Test successful end-to-end video creation."""
        # Call the create method
        result = self.factory.create_short_video()
        
        # Assertions
        self.assertTrue(result.success)
        self.assertTrue(os.path.exists(result.output_path))
        
        # Verify all components were called
        self.mock_story_generator.generate_structured_story.assert_called_once_with(
            "Test subject", 2
        )
        self.assertEqual(self.mock_narration_generator.generate_narration.call_count, 2)
        self.assertEqual(self.mock_visual_generator.generate_image.call_count, 2)
        self.mock_video_assembler.assemble_video.assert_called_once()
    
    def test_create_short_video_story_failure(self):
        """Test handling of story generation failure."""
        # Configure the mock to return an error
        self.mock_story_generator.generate_structured_story.return_value = "Error: Test error"
        
        # Call the create method
        result = self.factory.create_short_video()
        
        # Assertions
        self.assertFalse(result.success)
        self.assertIn("Failed to generate story", result.error)
        
        # Verify only story generator was called, and others were not
        self.mock_story_generator.generate_structured_story.assert_called_once()
        self.mock_narration_generator.generate_narration.assert_not_called()
        self.mock_visual_generator.generate_image.assert_not_called()
        self.mock_video_assembler.assemble_video.assert_not_called()
    
    def test_create_short_video_narration_failure(self):
        """Test handling of narration generation failure."""
        # Configure the narration mock to return an error for the first call
        self.mock_narration_generator.generate_narration.side_effect = [
            GenerationResult(
                success=False,
                output_path="",
                error="Test narration error"
            ),
            GenerationResult(
                success=True,
                output_path=os.path.join(self.test_output_dir, "audio2.mp3"),
                error=""
            )
        ]
        
        # Call the create method
        result = self.factory.create_short_video()
        
        # Assertions
        self.assertFalse(result.success)
        self.assertIn("Failed to generate narration", result.error)
        
        # Verify story and narration generators were called, but not beyond that
        self.mock_story_generator.generate_structured_story.assert_called_once()
        self.mock_narration_generator.generate_narration.assert_called_once()
        self.mock_visual_generator.generate_image.assert_not_called()
        self.mock_video_assembler.assemble_video.assert_not_called()
    
    def test_create_short_video_visual_failure(self):
        """Test handling of visual generation failure."""
        # Configure the visual generator mock to return an error for the first call
        self.mock_visual_generator.generate_image.side_effect = [
            GenerationResult(
                success=False,
                output_path="",
                error="Test image error"
            ),
            GenerationResult(
                success=True,
                output_path=os.path.join(self.test_output_dir, "image2.png"),
                error=""
            )
        ]
        
        # Call the create method
        result = self.factory.create_short_video()
        
        # Assertions
        self.assertFalse(result.success)
        self.assertIn("Failed to generate image", result.error)
        
        # Verify story, narration, and visual generators were called, but not video assembly
        self.mock_story_generator.generate_structured_story.assert_called_once()
        self.assertEqual(self.mock_narration_generator.generate_narration.call_count, 2)
        self.mock_visual_generator.generate_image.assert_called_once()
        self.mock_video_assembler.assemble_video.assert_not_called()
    
    def test_create_short_video_assembly_failure(self):
        """Test handling of video assembly failure."""
        # Configure the video assembler mock to return an error
        self.mock_video_assembler.assemble_video.return_value = GenerationResult(
            success=False,
            output_path="",
            error="Test assembly error"
        )
        
        # Call the create method
        result = self.factory.create_short_video()
        
        # Assertions
        self.assertFalse(result.success)
        self.assertIn("Failed to assemble video", result.error)
        
        # Verify all components were called
        self.mock_story_generator.generate_structured_story.assert_called_once()
        self.assertEqual(self.mock_narration_generator.generate_narration.call_count, 2)
        self.assertEqual(self.mock_visual_generator.generate_image.call_count, 2)
        self.mock_video_assembler.assemble_video.assert_called_once()


if __name__ == "__main__":
    unittest.main()
