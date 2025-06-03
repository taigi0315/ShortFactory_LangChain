"""
Tests for the VideoAssembler class.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pytest
import moviepy.editor as mpy_editor

from src.assemblers.video_assembler import VideoAssembler
from src.models.schemas import GenerationResult


class TestVideoAssembler(unittest.TestCase):
    """Test suite for the VideoAssembler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test image and audio paths
        self.test_image_paths = [
            os.path.join(self.temp_dir, "image1.png"),
            os.path.join(self.temp_dir, "image2.png")
        ]
        self.test_audio_paths = [
            os.path.join(self.temp_dir, "audio1.mp3"),
            os.path.join(self.temp_dir, "audio2.mp3")
        ]
        self.test_audio_durations = [3.0, 4.0]
        self.test_output_path = os.path.join(self.temp_dir, "output_video.mp4")
        
        # Create dummy test files
        self.create_test_files()
    
    def create_test_files(self):
        """Create dummy test image and audio files."""
        # Create dummy image files
        for path in self.test_image_paths:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(b'dummy image data')
                
        # Create dummy audio files
        for path in self.test_audio_paths:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(b'dummy audio data')
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove test directory if it exists
        if os.path.exists(self.temp_dir):
            # Remove test files
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)

    @patch('moviepy.editor.ImageClip')
    @patch('moviepy.editor.AudioFileClip')
    @patch('moviepy.editor.concatenate_videoclips')
    def test_assemble_video_success(self, mock_concatenate, mock_audio_clip, mock_image_clip):
        """Test successful video assembly."""
        # Create mocks for moviepy classes
        mock_img_clip = MagicMock()
        mock_audio = MagicMock()
        mock_video_clip = MagicMock()
        mock_final_clip = MagicMock()
        
        # Configure mocks
        mock_image_clip.return_value = mock_img_clip
        mock_audio_clip.return_value = mock_audio
        mock_img_clip.set_audio.return_value = mock_video_clip
        mock_concatenate.return_value = mock_final_clip
        
        # Initialize the assembler
        assembler = VideoAssembler()
        
        # Call the method
        result = assembler.assemble_video(
            self.test_image_paths,
            self.test_audio_paths,
            self.test_audio_durations,
            self.test_output_path
        )
        
        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(result.output_path, self.test_output_path)
        mock_image_clip.assert_called()
        mock_audio_clip.assert_called()
        mock_concatenate.assert_called_once()
        mock_final_clip.write_videofile.assert_called_once()
    
    def test_assemble_video_length_mismatch(self):
        """Test handling of length mismatch between images, audios, and durations."""
        # Initialize the assembler
        assembler = VideoAssembler()
        
        # Call the method with mismatched lengths
        result = assembler.assemble_video(
            self.test_image_paths,  # 2 images
            [self.test_audio_paths[0]],  # 1 audio
            self.test_audio_durations,  # 2 durations
            self.test_output_path
        )
        
        # Assertions
        self.assertFalse(result.success)
        self.assertIn("Length mismatch", result.error)
    
    def test_assemble_video_empty_inputs(self):
        """Test handling of empty input lists."""
        # Initialize the assembler
        assembler = VideoAssembler()
        
        # Call the method with empty inputs
        result = assembler.assemble_video(
            [],  # No images
            [],  # No audios
            [],  # No durations
            self.test_output_path
        )
        
        # Assertions
        self.assertFalse(result.success)
        self.assertIn("No images provided", result.error)
    
    @patch('moviepy.editor.ImageClip')
    @patch('moviepy.editor.AudioFileClip')
    @patch('moviepy.editor.concatenate_videoclips')
    def test_assemble_video_exception_handling(self, mock_concatenate, mock_audio_clip, mock_image_clip):
        """Test exception handling during video assembly."""
        # Configure mock to raise an exception
        mock_image_clip.side_effect = Exception("Test error")
        
        # Initialize the assembler
        assembler = VideoAssembler()
        
        # Call the method
        result = assembler.assemble_video(
            self.test_image_paths,
            self.test_audio_paths,
            self.test_audio_durations,
            self.test_output_path
        )
        
        # Assertions
        self.assertFalse(result.success)
        self.assertIn("Error during video assembly", result.error)
        self.assertIn("Test error", result.error)
    
    @patch('moviepy.editor.ImageClip')
    @patch('moviepy.editor.AudioFileClip')
    @patch('moviepy.editor.concatenate_videoclips')
    def test_create_slideshow_with_background_music(self, mock_concatenate, mock_audio_clip, mock_image_clip):
        """Test creating a slideshow with background music."""
        # Create mocks
        mock_img_clip = MagicMock()
        mock_audio = MagicMock()
        mock_audio.duration = 10.0  # 10 seconds of audio
        mock_final_clip = MagicMock()
        
        # Configure mocks
        mock_image_clip.return_value = mock_img_clip
        mock_audio_clip.return_value = mock_audio
        mock_concatenate.return_value = mock_final_clip
        mock_final_clip.duration = 6.0  # 6 seconds of video (2 slides at 3.0 seconds each)
        
        # Create a test music path
        test_music_path = os.path.join(self.temp_dir, "background_music.mp3")
        with open(test_music_path, 'wb') as f:
            f.write(b'dummy music data')
        
        # Initialize the assembler
        assembler = VideoAssembler()
        
        # Call the method
        result = assembler.create_slideshow_with_background_music(
            self.test_image_paths,
            self.test_output_path,
            test_music_path
        )
        
        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(result.output_path, self.test_output_path)
        mock_image_clip.assert_called()
        mock_audio_clip.assert_called_once_with(test_music_path)
        mock_concatenate.assert_called_once()
        mock_final_clip.write_videofile.assert_called_once()


if __name__ == "__main__":
    unittest.main()
