"""
Visual Generator module for creating images from text descriptions using various providers.
"""

import os
import re
import logging
from typing import Optional, List, Literal

from src.models.schemas import CharacterDescription, GenerationResult
from src.config.config import Config

logger = logging.getLogger(__name__)

# Import providers conditionally to handle cases when some aren't available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI library not installed. DALL-E functionality will be unavailable.")
    OpenAI = None
    OPENAI_AVAILABLE = False

try:
    from google.cloud import aiplatform
    from vertexai.preview.vision_models import ImageGenerationModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    logger.warning("Google Cloud AI Platform or ImageGenerationModel not available. Vertex AI image generation functionality will be unavailable.")
    aiplatform = None
    ImageGenerationModel = None
    VERTEX_AI_AVAILABLE = False


class VisualGenerator:
    """
    Class for generating visual content (images) from text descriptions.
    Supports multiple providers: OpenAI DALL-E, Google Vertex AI Imagen, and has a placeholder for Stable Diffusion.
    """
    
    def __init__(self, 
                 provider: Literal["openai_dalle", "google_vertex_ai_image", "stable_diffusion_api"] = "google_vertex_ai_image",
                 gcp_project_id: str = None, 
                 gcp_location: str = None,
                 vertex_ai_imagen_model_id: str = None):
        """
        Initialize the VisualGenerator.
        
        Args:
            provider: The image generation provider to use
            gcp_project_id: Google Cloud Project ID (required for Vertex AI)
            gcp_location: Google Cloud region (required for Vertex AI)
            vertex_ai_imagen_model_id: Specific Vertex AI Imagen model ID
        """
        self.provider = provider
        self.api_key = None
        self.client = None
        self.vertex_ai_model = None
        self.gcp_project_id = gcp_project_id or Config.GCP_PROJECT_ID
        self.gcp_location = gcp_location or Config.GCP_LOCATION
        self.vertex_ai_imagen_model_id = vertex_ai_imagen_model_id or Config.VERTEX_AI_IMAGEN_MODEL_ID

        if self.provider == "openai_dalle":
            self._setup_openai_dalle()
        elif self.provider == "google_vertex_ai_image":
            self._setup_google_vertex_ai_image()
        elif self.provider == "stable_diffusion_api":
            self._setup_stable_diffusion_api()
        else:
            raise ValueError(f"Unsupported Visual provider: {provider}")

    def _setup_openai_dalle(self):
        """Sets up OpenAI DALL-E API key and client."""
        logger.info("Setting up OpenAI DALL-E Visual Generator...")
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI library is not available. Please install it with 'pip install openai'.")
            return
            
        try:
            self.api_key = Config.get_api_key("openai")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables.")
                
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI DALL-E client initialized.")
        except Exception as e:
            self.api_key = None
            self.client = None
            logger.error(f"Error setting up OpenAI DALL-E: {e}")

    def _setup_google_vertex_ai_image(self):
        """Sets up Google Cloud Vertex AI Image Generation."""
        logger.info("Setting up Google Vertex AI Image Generation...")
        if not VERTEX_AI_AVAILABLE:
            logger.error("Required Google Cloud AI Platform libraries not available. Please install them.")
            return
            
        if not self.gcp_project_id:
            logger.error("GCP_PROJECT_ID not provided. Cannot initialize Vertex AI.")
            return

        try:
            aiplatform.init(project=self.gcp_project_id, location=self.gcp_location)
            self.vertex_ai_model = ImageGenerationModel.from_pretrained(self.vertex_ai_imagen_model_id)
            logger.info(f"Google Vertex AI Imagen model '{self.vertex_ai_imagen_model_id}' initialized.")
            self.api_key = "VERTEX_AI_READY"  # Dummy key to indicate setup success
        except Exception as e:
            self.vertex_ai_model = None
            self.api_key = None
            logger.error(f"Error setting up Google Vertex AI Image Generation: {e}")
            logger.error("Ensure `google-cloud-aiplatform` is installed, GCP credentials/project are configured, and Vertex AI API is enabled.")

    def _setup_stable_diffusion_api(self):
        """Placeholder for Stable Diffusion API setup."""
        logger.info("Setting up Stable Diffusion API (placeholder).")
        logger.warning("Stable Diffusion API implementation is not complete.")
        self.api_key = None

    def generate_image(self,
                       overall_image_style: str,
                       main_characters: List[CharacterDescription],
                       scene_visual_description: str,
                       output_path: str,
                       quality: Literal["standard", "hd"] = "standard") -> GenerationResult:
        """
        Generates an image for a given scene's visual description, incorporating
        global style and consistent character descriptions.
        
        Args:
            overall_image_style: The overall visual style for all images
            main_characters: List of character descriptions for consistency
            scene_visual_description: Description of the specific scene to visualize
            output_path: Path where to save the generated image
            quality: Image quality setting (standard or hd)
            
        Returns:
            GenerationResult with success status and output information
        """
        if (self.provider == "openai_dalle" and not self.client) or \
           (self.provider == "google_vertex_ai_image" and not self.vertex_ai_model) or \
           (self.provider == "stable_diffusion_api" and not self.api_key):
            error_msg = f"Provider '{self.provider}' not properly set up. Cannot generate image."
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)

        # --- SMART PROMPT CONSTRUCTION ---
        final_image_prompt = overall_image_style

        processed_scene_desc = scene_visual_description
        for character in main_characters:
            pattern = r'\b' + re.escape(character.name) + r'\b'
            processed_scene_desc = re.sub(pattern, f"{character.name} ({character.appearance})", processed_scene_desc, flags=re.IGNORECASE)

        final_image_prompt += f", {processed_scene_desc}"
        # --- END SMART PROMPT CONSTRUCTION ---

        logger.info(f"Generating image for prompt: '{final_image_prompt[:100]}...'")

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if self.provider == "openai_dalle":
                return self._generate_openai_dalle_image(final_image_prompt, output_path, quality)
            elif self.provider == "google_vertex_ai_image":
                return self._generate_google_vertex_ai_image(final_image_prompt, output_path)
            elif self.provider == "stable_diffusion_api":
                return self._generate_stable_diffusion_image(final_image_prompt, output_path)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            error_msg = f"Error generating image: {e}"
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)

    def _generate_openai_dalle_image(self, prompt_text: str, output_path: str, quality: Literal["standard", "hd"]) -> GenerationResult:
        """
        Generates image using OpenAI DALL-E 3 API.
        
        Args:
            prompt_text: Text description for image generation
            output_path: Path where to save the generated image
            quality: Image quality setting (standard or hd)
            
        Returns:
            GenerationResult with success status and output information
        """
        if not self.client:
            return GenerationResult(success=False, output_path="", error="OpenAI client not initialized.")
            
        try:
            logger.info("Generating image with DALL-E 3...")
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt_text,
                size="1024x1024",
                quality=quality,
                n=1,
            )
            
            # Get image URL
            image_url = response.data[0].url
            
            # Download image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            with open(output_path, "wb") as f:
                f.write(image_response.content)
                
            logger.info(f"Image saved to {output_path}")
            return GenerationResult(success=True, output_path=output_path)
        except Exception as e:
            error_msg = f"Error generating DALL-E image: {e}"
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)

    def _generate_google_vertex_ai_image(self, prompt_text: str, output_path: str) -> GenerationResult:
        """
        Generates image using Google Vertex AI Image Generation.
        
        Args:
            prompt_text: Text description for image generation
            output_path: Path where to save the generated image
            
        Returns:
            GenerationResult with success status and output information
        """
        if not self.vertex_ai_model:
            return GenerationResult(success=False, output_path="", error="Vertex AI model not initialized.")
            
        try:
            logger.info("Generating image with Vertex AI Imagen...")
            response = self.vertex_ai_model.generate_images(
                prompt=prompt_text,
                # Additional parameters can be added here as needed
                # e.g., number of images to generate, etc.
            )
            
            # Save the first image
            response.images[0].save(output_path)
            logger.info(f"Image saved to {output_path}")
            return GenerationResult(success=True, output_path=output_path)
        except Exception as e:
            error_msg = f"Error generating Vertex AI image: {e}"
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)

    def _generate_stable_diffusion_image(self, prompt_text: str, output_path: str) -> GenerationResult:
        """
        Placeholder for generating image using Stable Diffusion API.
        
        Args:
            prompt_text: Text description for image generation
            output_path: Path where to save the generated image
            
        Returns:
            GenerationResult with success status and output information
        """
        # This is a placeholder that would be implemented with Stable Diffusion API
        logger.warning("Stable Diffusion API implementation is not complete. This is a placeholder.")
        error_msg = "Stable Diffusion API not implemented yet."
        return GenerationResult(success=False, output_path="", error=error_msg)
