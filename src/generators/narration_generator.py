"""
Narration Generator module for creating audio narrations from text using various TTS providers.
"""

import os
import logging
import requests
from typing import Optional, Literal
from pydub import AudioSegment

from src.models.schemas import GenerationResult
from src.config.config import Config

logger = logging.getLogger(__name__)

class NarrationGenerator:
    """
    Class for generating audio narrations from text using various TTS providers.
    Currently supports ElevenLabs and has a placeholder for Google Cloud TTS.
    """
    
    def __init__(self, provider: Literal["elevenlabs", "google_cloud_tts"] = "elevenlabs",
                 elevenlabs_voice_id: str = None):
        """
        Initialize the NarrationGenerator.
        
        Args:
            provider: The TTS provider to use
            elevenlabs_voice_id: The voice ID to use with ElevenLabs
        """
        self.provider = provider
        self.api_key = None
        self.elevenlabs_voice_id = elevenlabs_voice_id or Config.ELEVENLABS_VOICE_ID

        if self.provider == "elevenlabs":
            self._setup_elevenlabs()
        elif self.provider == "google_cloud_tts":
            self._setup_google_cloud_tts()
        else:
            raise ValueError(f"Unsupported TTS provider: {provider}")

    def _setup_elevenlabs(self):
        """Sets up ElevenLabs API key and headers."""
        logger.info("Setting up ElevenLabs Narration Generator...")
        try:
            self.api_key = Config.get_api_key("elevenlabs")
            if not self.api_key:
                raise ValueError("ELEVEN_LABS_API_KEY not found in environment variables.")
                
            self.headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            self.elevenlabs_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
            logger.info("ElevenLabs setup complete.")
        except Exception as e:
            self.api_key = None
            logger.error(f"Error setting up ElevenLabs: {e}")
            logger.error("Please ensure ELEVEN_LABS_API_KEY is in your environment variables.")

    def _setup_google_cloud_tts(self):
        """Placeholder for Google Cloud TTS setup."""
        logger.info("Setting up Google Cloud TTS...")
        logger.info("Requires Google Cloud project, billing, and specific service account credentials.")
        try:
            # This would be extended to use the Google Cloud TTS client in a real implementation
            self.api_key = Config.get_api_key("google")
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables.")
            logger.info("Google Cloud TTS setup complete.")
        except Exception as e:
            self.api_key = None
            logger.error(f"Error setting up Google Cloud TTS: {e}")

    def generate_narration(self, text: str, output_path: str) -> GenerationResult:
        """
        Generates narration audio for a given text and saves it to a file.
        
        Args:
            text: The text to convert to speech
            output_path: Path where to save the generated audio file
            
        Returns:
            GenerationResult with success status and output information
        """
        if not self.api_key:
            error_msg = f"API Key not set for {self.provider}. Cannot generate narration."
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)

        try:
            if self.provider == "elevenlabs":
                result = self._generate_elevenlabs_narration(text, output_path)
            elif self.provider == "google_cloud_tts":
                result = self._generate_google_cloud_tts_narration(text, output_path)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
            if result.success:
                result.duration = self.get_audio_duration(result.output_path)
                
            return result
        except Exception as e:
            error_msg = f"Error generating narration: {e}"
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)

    def _generate_elevenlabs_narration(self, text: str, output_path: str) -> GenerationResult:
        """
        Generates narration using ElevenLabs API.
        
        Args:
            text: The text to convert to speech
            output_path: Path where to save the generated audio file
            
        Returns:
            GenerationResult with success status and output information
        """
        if not self.api_key:
            return GenerationResult(success=False, output_path="", error="ElevenLabs API key not set.")
            
        json_data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        try:
            logger.info(f"Generating ElevenLabs narration for text: '{text[:50]}...'")
            response = requests.post(self.elevenlabs_url, json=json_data, headers=self.headers, stream=True)
            response.raise_for_status()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"Narration saved to {output_path}")
            return GenerationResult(success=True, output_path=output_path)
        except requests.exceptions.RequestException as e:
            error_msg = f"Error during ElevenLabs narration: {e} - {getattr(response, 'text', '')}"
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)

    def _generate_google_cloud_tts_narration(self, text: str, output_path: str) -> GenerationResult:
        """
        Generates narration using Google Cloud TTS.
        
        Args:
            text: The text to convert to speech
            output_path: Path where to save the generated audio file
            
        Returns:
            GenerationResult with success status and output information
        """
        # This is a placeholder that would be implemented with the Google Cloud TTS client
        logger.info(f"Generating Google Cloud TTS narration for: '{text[:50]}...'")
        
        # Placeholder implementation, would actually call Google Cloud TTS API here
        error_msg = "Google Cloud TTS implementation not complete. This is a placeholder."
        logger.warning(error_msg)
        return GenerationResult(success=False, output_path="", error=error_msg)

    def get_audio_duration(self, audio_path: str) -> float:
        """
        Gets the duration of an audio file in seconds.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Duration of the audio in seconds
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0
        except Exception as e:
            logger.error(f"Error getting audio duration for {audio_path}: {e}")
            return 0.0
