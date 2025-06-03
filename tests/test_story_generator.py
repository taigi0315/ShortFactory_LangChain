"""
Tests for the StoryGenerator class.
"""

import unittest
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import Generation, ChatGeneration, ChatResult

from src.generators.story_generator import StoryGenerator
from src.models.schemas import StoryWithScenes, CharacterDescription, Scene


class TestStoryGenerator(unittest.TestCase):
    """Test suite for the StoryGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = MagicMock(spec=BaseChatModel)
        
        # Create a sample valid response for the mock LLM
        sample_story = {
            "title": "The Magical Acorn Heist",
            "full_story_summary": "A mischievous squirrel attempts to steal a magical acorn from a grumpy wizard.",
            "overall_image_style": "Watercolor painting, vibrant colors, fantastical, soft lighting",
            "main_characters": [
                {"name": "Nibbles", "appearance": "Small red squirrel with a bushy tail and bright eyes"},
                {"name": "Wizardo", "appearance": "Elderly man with long gray beard, purple robes, and a pointed hat"}
            ],
            "scenes": [
                {
                    "scene_number": 1,
                    "visual_description": "A small cottage at the edge of a forest with a magical garden",
                    "narration_text": "In a small cottage at the edge of an enchanted forest lived a grumpy wizard named Wizardo."
                },
                {
                    "scene_number": 2,
                    "visual_description": "Nibbles the squirrel watches the garden from a tree branch",
                    "narration_text": "Nibbles the squirrel had been watching the wizard's garden for days, eyeing the giant golden acorn."
                }
            ]
        }
        self.sample_story = StoryWithScenes(**sample_story)
    
    @patch("src.generators.story_generator.PydanticOutputParser")
    def test_generate_structured_story_success(self, mock_parser_class):
        """Test successful story generation."""
        # Configure the mock parser
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.get_format_instructions.return_value = "Format instructions"
        
        # Configure chain to return our sample story
        mock_chain = MagicMock()
        self.mock_llm.side_effect = lambda x: mock_chain(x)
        mock_chain.invoke.return_value = self.sample_story
        
        # Create generator and patch the chain
        with patch("src.generators.story_generator.PromptTemplate"):
            story_generator = StoryGenerator(self.mock_llm)
            with patch.object(story_generator, "prompt_template") as mock_prompt:
                mock_prompt.__or__.return_value = mock_chain
                
                # Call the method
                result = story_generator.generate_structured_story("test subject", 2)
                
                # Assertions
                self.assertEqual(result, self.sample_story)
                self.assertEqual(result.title, "The Magical Acorn Heist")
                self.assertEqual(len(result.scenes), 2)
    
    @patch("src.generators.story_generator.PydanticOutputParser")
    def test_generate_structured_story_failure(self, mock_parser_class):
        """Test handling of story generation failure."""
        # Configure the mock parser
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.get_format_instructions.return_value = "Format instructions"
        
        # Configure chain to raise an exception
        mock_chain = MagicMock()
        self.mock_llm.side_effect = lambda x: mock_chain(x)
        mock_chain.invoke.side_effect = ValueError("Test error")
        
        # Create generator and patch the chain
        with patch("src.generators.story_generator.PromptTemplate"):
            story_generator = StoryGenerator(self.mock_llm)
            with patch.object(story_generator, "prompt_template") as mock_prompt:
                mock_prompt.__or__.return_value = mock_chain
                
                # Call the method
                result = story_generator.generate_structured_story("test subject", 2)
                
                # Assertions
                self.assertTrue(isinstance(result, str))
                self.assertTrue("Error:" in result)
    
    def test_initialization_with_none_llm(self):
        """Test initialization with None LLM raises ValueError."""
        with self.assertRaises(ValueError):
            StoryGenerator(None)


if __name__ == "__main__":
    unittest.main()
