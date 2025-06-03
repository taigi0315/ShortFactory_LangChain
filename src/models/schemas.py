"""
Pydantic models for structured data in the ShortFactory application.
These models define the structure for story generation, scene descriptions,
and other data used throughout the application pipeline.
"""

from typing import List, Literal
from pydantic import BaseModel, Field


class CharacterDescription(BaseModel):
    """Model for character descriptions to ensure consistency across scenes."""
    name: str = Field(description="The name of the character.")
    appearance: str = Field(description="A detailed, consistent visual description of the character's appearance, "
                                      "including specific features, clothing, and colors, for uniform image generation across scenes.")


class Scene(BaseModel):
    """Model for individual scenes within a story."""
    scene_number: int = Field(description="The sequential number of the scene.")
    visual_description: str = Field(description="A concise and highly detailed visual description for image/video generation "
                                              "of this specific scene, integrating global style and character appearances. (max 30 words)")
    narration_text: str = Field(description="The exact text to be narrated for this scene.")


class StoryWithScenes(BaseModel):
    """Main model for a complete structured story with its scenes."""
    title: str = Field(description="A catchy title for the short story.")
    full_story_summary: str = Field(description="A brief summary of the entire story.")
    overall_image_style: str = Field(description="A consistent and descriptive style instruction for all images/videos in the story "
                                                "(e.g., 'Watercolor painting, vibrant colors, fantastical, soft lighting', "
                                                "'Gritty cyberpunk, neon lights, rainy street, realistic'). "
                                                "This should be used as a prefix for every visual_description.")
    main_characters: List[CharacterDescription] = Field(description="Detailed and consistent visual descriptions for the main characters "
                                                                   "to ensure uniformity across scenes.")
    scenes: List[Scene] = Field(description="A list of distinct scenes composing the story, each with its visual and narration details.")


class GenerationResult(BaseModel):
    """Model for tracking the success status and output paths of generation steps."""
    success: bool = Field(description="Whether the generation was successful.")
    output_path: str = Field(description="Path to the generated output file, if successful.")
    error: str = Field(default="", description="Error message, if generation failed.")
    duration: float = Field(default=0.0, description="Duration of audio in seconds, if applicable.")


class VideoCreationConfig(BaseModel):
    """Configuration settings for the video creation process."""
    story_subject: str = Field(description="The subject of the story to be generated.")
    num_scenes: int = Field(description="Number of scenes to generate for the story.")
    tts_provider: Literal["elevenlabs", "google_cloud_tts"] = Field(description="Provider for text-to-speech narration generation.")
    elevenlabs_voice_id: str = Field(description="Voice ID for ElevenLabs TTS provider.")
    image_provider: Literal["openai_dalle", "google_vertex_ai_image", "stable_diffusion_api"] = Field(description="Provider for image generation.")
    gcp_project_id: str = Field(description="Google Cloud Project ID for Vertex AI services.")
    gcp_location: str = Field(description="Google Cloud region for Vertex AI services.")
    vertex_ai_imagen_model_id: str = Field(description="Specific Vertex AI Imagen model ID.")
    image_transition_duration: float = Field(description="Duration of fade transition between images in seconds.")
    video_fps: int = Field(description="Frames per second for the output video.")
    output_directories: dict = Field(description="Dictionary of output directories for various assets.")
