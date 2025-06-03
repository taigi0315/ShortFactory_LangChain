"""
Configuration module for the ShortFactory application.
Contains settings for output directories, API providers, and other global configurations.
"""

import os
from typing import Dict, Optional, Literal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the ShortFactory application."""
    
    # Story Generation Configuration
    STORY_SUBJECT = os.getenv("STORY_SUBJECT", "A mischievous squirrel trying to steal a giant acorn from a grumpy wizard's garden.")
    NUM_SCENES = int(os.getenv("NUM_SCENES", "4"))  # Desired number of scenes for the story

    # Narration Configuration
    TTS_PROVIDER = os.getenv("TTS_PROVIDER", "elevenlabs")  # Options: "elevenlabs", "google_cloud_tts"
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4Fnqa80wBMgs")  # Default voice ID

    # Image Generation Configuration
    IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "google_vertex_ai_image")  # Options: "openai_dalle", "google_vertex_ai_image", "stable_diffusion_api"
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")  # Google Cloud Project ID
    GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")  # Google Cloud region
    VERTEX_AI_IMAGEN_MODEL_ID = os.getenv("VERTEX_AI_IMAGEN_MODEL_ID", "imagegeneration@002")

    # Video Assembly Configuration
    IMAGE_TRANSITION_DURATION = float(os.getenv("IMAGE_TRANSITION_DURATION", "0.5"))  # Duration of fade transition between images
    VIDEO_FPS = int(os.getenv("VIDEO_FPS", "24"))  # Frames per second for output video

    # Output Directories
    BASE_OUTPUT_DIR = os.getenv("BASE_OUTPUT_DIR", "shortfactory_output")
    STORY_AUDIOS_DIR = os.path.join(BASE_OUTPUT_DIR, "story_audios")
    STORY_IMAGES_DIR = os.path.join(BASE_OUTPUT_DIR, "story_images")
    FINAL_VIDEOS_DIR = os.path.join(BASE_OUTPUT_DIR, "final_videos")
    
    @classmethod
    def create_output_directories(cls) -> Dict[str, str]:
        """Create output directories if they don't exist."""
        os.makedirs(cls.STORY_AUDIOS_DIR, exist_ok=True)
        os.makedirs(cls.STORY_IMAGES_DIR, exist_ok=True)
        os.makedirs(cls.FINAL_VIDEOS_DIR, exist_ok=True)
        
        return {
            "base": cls.BASE_OUTPUT_DIR,
            "audios": cls.STORY_AUDIOS_DIR,
            "images": cls.STORY_IMAGES_DIR,
            "videos": cls.FINAL_VIDEOS_DIR
        }
    
    @classmethod
    def get_api_key(cls, provider: Literal["openai", "elevenlabs", "google"]) -> Optional[str]:
        """Get API key for the specified provider."""
        key_mapping = {
            "openai": "OPENAI_API_KEY",
            "elevenlabs": "ELEVEN_LABS_API_KEY",
            "google": "GOOGLE_API_KEY"
        }
        
        env_var = key_mapping.get(provider)
        if not env_var:
            return None
            
        return os.getenv(env_var)
