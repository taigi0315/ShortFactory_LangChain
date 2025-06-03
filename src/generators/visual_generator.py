# visual_generator.py (Updated with more debug prints)

import os
import re
import logging
from typing import Optional, List, Literal

# Assuming these are correctly defined and imported from your project structure
from src.models.schemas import CharacterDescription, GenerationResult
from src.config.config import Config

logger = logging.getLogger(__name__)
# Set logging level to INFO to see more details during debugging
logging.basicConfig(level=logging.INFO)


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
    def __init__(self,
                 provider: Literal["openai_dalle", "google_vertex_ai_image", "stable_diffusion_api"] = "google_vertex_ai_image",
                 gcp_project_id: str = None,
                 gcp_location: str = None,
                 vertex_ai_imagen_model_id: str = None):
        logger.info(f"VisualGenerator initializing with provider: {provider}")
        self.provider = provider
        self.api_key = None
        self.client = None
        self.vertex_ai_model = None
        # Use provided args or fallback to Config
        self.gcp_project_id = gcp_project_id if gcp_project_id is not None else Config.GCP_PROJECT_ID
        self.gcp_location = gcp_location if gcp_location is not None else Config.GCP_LOCATION
        self.vertex_ai_imagen_model_id = vertex_ai_imagen_model_id if vertex_ai_imagen_model_id is not None else Config.VERTEX_AI_IMAGEN_MODEL_ID

        logger.info(f"Configured GCP Project ID: {self.gcp_project_id}")
        logger.info(f"Configured GCP Location: {self.gcp_location}")
        logger.info(f"Configured Vertex AI Imagen Model ID: {self.vertex_ai_imagen_model_id}")


        if self.provider == "openai_dalle":
            self._setup_openai_dalle()
        elif self.provider == "google_vertex_ai_image":
            self._setup_google_vertex_ai_image()
        elif self.provider == "stable_diffusion_api":
            self._setup_stable_diffusion_api()
        else:
            raise ValueError(f"Unsupported Visual provider: {provider}")

        logger.info(f"VisualGenerator initialization complete. self.vertex_ai_model is: {self.vertex_ai_model}")


    def _setup_openai_dalle(self):
        logger.info("Setting up OpenAI DALL-E Visual Generator...")
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI library is not available. Please install it with 'pip install openai'.")
            return

        try:
            self.api_key = Config.get_api_key("openai") # Assuming Config.get_api_key handles os.getenv
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables.")

            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI DALL-E client initialized.")
        except Exception as e:
            self.api_key = None
            self.client = None
            logger.error(f"Error setting up OpenAI DALL-E: {e}")

    def _setup_google_vertex_ai_image(self):
        logger.info("Setting up Google Vertex AI Image Generation...")
        logger.info(f"VERTEX_AI_AVAILABLE: {VERTEX_AI_AVAILABLE}")
        if not VERTEX_AI_AVAILABLE:
            logger.error("Required Google Cloud AI Platform libraries not available. Please install them.")
            return

        if not self.gcp_project_id:
            logger.error("GCP_PROJECT_ID not provided. Cannot initialize Vertex AI.")
            return

        try:
            logger.info(f"Initializing aiplatform with project='{self.gcp_project_id}', location='{self.gcp_location}'")
            aiplatform.init(project=self.gcp_project_id, location=self.gcp_location)
            logger.info(f"Loading ImageGenerationModel from_pretrained('{self.vertex_ai_imagen_model_id}')")
            self.vertex_ai_model = ImageGenerationModel.from_pretrained(self.vertex_ai_imagen_model_id)
            logger.info(f"Google Vertex AI Imagen model '{self.vertex_ai_imagen_model_id}' initialized successfully.")
            self.api_key = "VERTEX_AI_READY" # Dummy key to indicate setup success
        except Exception as e:
            self.vertex_ai_model = None
            self.api_key = None
            logger.error(f"Error setting up Google Vertex AI Image Generation: {e}")
            logger.error("Ensure `google-cloud-aiplatform` is installed, GCP credentials/project are configured, and Vertex AI API is enabled.")
            logger.error(f"Specific error during init/from_pretrained: {e}")


    def _setup_stable_diffusion_api(self):
        logger.info("Setting up Stable Diffusion API (placeholder).")
        logger.warning("Stable Diffusion API implementation is not complete.")
        self.api_key = None

    def generate_image(self,
                       overall_image_style: str,
                       main_characters: List[CharacterDescription],
                       scene_visual_description: str,
                       output_path: str,
                       quality: Literal["standard", "hd"] = "standard") -> GenerationResult:
        logger.info(f"Attempting to generate image with provider: {self.provider}")
        logger.info(f"Current self.vertex_ai_model status: {self.vertex_ai_model}")

        if (self.provider == "openai_dalle" and not self.client) or \
           (self.provider == "google_vertex_ai_image" and not self.vertex_ai_model) or \
           (self.provider == "stable_diffusion_api" and not self.api_key):
            error_msg = f"Provider '{self.provider}' not properly set up. Cannot generate image. (self.vertex_ai_model is {self.vertex_ai_model})"
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)

        # --- SMART PROMPT CONSTRUCTION ---
        final_image_prompt = overall_image_style

        processed_scene_desc = scene_visual_description
        for character in main_characters:
            pattern = r'\b' + re.escape(character.name) + r'\b'
            # Replace character name with its detailed appearance, enclosed in parentheses for clarity in prompt
            processed_scene_desc = re.sub(pattern, f"{character.name} ({character.appearance})", processed_scene_desc, flags=re.IGNORECASE)

        final_image_prompt += f", {processed_scene_desc}"
        # --- END SMART PROMPT CONSTRUCTION ---

        logger.info(f"Final image prompt: '{final_image_prompt[:100]}...'")

        try:
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
        if not self.client: return GenerationResult(success=False, output_path="", error="OpenAI client not initialized.")
        try:
            logger.info("Generating image with DALL-E 3...")
            response = self.client.images.generate(model="dall-e-3", prompt=prompt_text, size="1024x1024", quality=quality, n=1)
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            with open(output_path, "wb") as f: f.write(image_response.content)
            logger.info(f"Image saved to {output_path}")
            return GenerationResult(success=True, output_path=output_path)
        except Exception as e:
            error_msg = f"Error generating DALL-E image: {e}"
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)

    def _generate_google_vertex_ai_image(self, prompt_text: str, output_path: str) -> GenerationResult:
        if not self.vertex_ai_model: return GenerationResult(success=False, output_path="", error="Vertex AI model not initialized.")
        try:
            logger.info("Generating image with Vertex AI Imagen...")
            response = self.vertex_ai_model.generate_images(prompt=prompt_text, number_of_images=1)
            if response.images:
                image_data_bytes = response.images[0].image_bytes
                with open(output_path, "wb") as f: f.write(image_data_bytes)
                logger.info(f"Image saved to {output_path}")
                return GenerationResult(success=True, output_path=output_path)
            else:
                error_msg = "No image found in Vertex AI response (response.images was empty or null)."
                logger.error(error_msg)
                return GenerationResult(success=False, output_path="", error=error_msg)
        except Exception as e:
            error_msg = f"Error generating Vertex AI image: {e}"
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)

    def _generate_stable_diffusion_image(self, prompt_text: str, output_path: str) -> GenerationResult:
        logger.warning("Stable Diffusion API implementation is not complete. This is a placeholder.")
        error_msg = "Stable Diffusion API not implemented yet."
        return GenerationResult(success=False, output_path="", error=error_msg)