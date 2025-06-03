"""
Main entry point for the ShortFactory application.
"""

import os
import logging
import argparse
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from src.core.factory import ShortVideoFactory
from src.config.config import Config
from src.utils.logger import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

def create_llm(llm_provider: str = "gemini"):
    """
    Create and return an LLM based on the specified provider.
    
    Args:
        llm_provider: LLM provider to use ('gemini' or 'openai')
        
    Returns:
        A configured LangChain LLM
    """
    if llm_provider.lower() == "gemini":
        api_key = Config.get_api_key("google")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
            
        logger.info("Initializing Gemini Pro LLM...")
        return ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)
    elif llm_provider.lower() == "openai":
        api_key = Config.get_api_key("openai")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
            
        logger.info("Initializing OpenAI GPT LLM...")
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="ShortFactory - Create short videos with AI")
    parser.add_argument("--subject", type=str, help="Subject for the story", default=Config.STORY_SUBJECT)
    parser.add_argument("--scenes", type=int, help="Number of scenes", default=Config.NUM_SCENES)
    parser.add_argument("--llm", type=str, choices=["gemini", "openai"], default="gemini", help="LLM provider to use")
    parser.add_argument("--tts", type=str, choices=["elevenlabs", "google_cloud_tts"], default=Config.TTS_PROVIDER, 
                        help="TTS provider to use")
    parser.add_argument("--image", type=str, choices=["openai_dalle", "google_vertex_ai_image", "stable_diffusion_api"], 
                        default=Config.IMAGE_PROVIDER, help="Image generation provider to use")
    
    args = parser.parse_args()
    
    try:
        # Create LLM
        llm = create_llm(args.llm)
        
        # Create factory
        factory = ShortVideoFactory(llm)
        
        # Override config with command line arguments
        factory.config.story_subject = args.subject
        factory.config.num_scenes = args.scenes
        factory.config.tts_provider = args.tts
        factory.config.image_provider = args.image
        
        # Create video
        logger.info(f"Starting video creation for subject: '{args.subject}' with {args.scenes} scenes...")
        result = factory.create_video()
        
        if result["success"]:
            logger.info(f"Video creation successful! Video saved to: {result['video']['video_path']}")
            return 0
        else:
            logger.error(f"Video creation failed: {result.get('error', 'Unknown error')}")
            logger.info(f"Steps completed: {', '.join(result.get('steps_completed', []))}")
            return 1
    except Exception as e:
        logger.exception(f"Error in main: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
