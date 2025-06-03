"""
Core Factory module for orchestrating the ShortVideo creation process.
"""

import os
import logging
from typing import List, Dict, Optional, Tuple, Union

from langchain_core.language_models import BaseChatModel

from src.models.schemas import StoryWithScenes, GenerationResult, VideoCreationConfig
from src.generators.story_generator import StoryGenerator
from src.generators.narration_generator import NarrationGenerator
from src.generators.visual_generator import VisualGenerator
from src.assemblers.video_assembler import VideoAssembler
from src.config.config import Config

logger = logging.getLogger(__name__)

class ShortVideoFactory:
    """
    Main factory class for orchestrating the entire short video creation process.
    Coordinates between story generation, narration, image generation, and video assembly.
    """
    
    def __init__(self, llm: BaseChatModel, config: Optional[VideoCreationConfig] = None):
        """
        Initialize the ShortVideoFactory with necessary components.
        
        Args:
            llm: LangChain compatible language model for story generation
            config: Optional configuration for the video creation process
        """
        # Create default config if none provided
        if config is None:
            # Get output directories
            output_dirs = Config.create_output_directories()
            
            config = VideoCreationConfig(
                story_subject=Config.STORY_SUBJECT,
                num_scenes=Config.NUM_SCENES,
                tts_provider=Config.TTS_PROVIDER,
                elevenlabs_voice_id=Config.ELEVENLABS_VOICE_ID,
                image_provider=Config.IMAGE_PROVIDER,
                gcp_project_id=Config.GCP_PROJECT_ID,
                gcp_location=Config.GCP_LOCATION,
                vertex_ai_imagen_model_id=Config.VERTEX_AI_IMAGEN_MODEL_ID,
                image_transition_duration=Config.IMAGE_TRANSITION_DURATION,
                video_fps=Config.VIDEO_FPS,
                output_directories=output_dirs
            )
            
        self.config = config
        
        # Initialize components
        self.story_generator = StoryGenerator(llm)
        self.narration_generator = NarrationGenerator(
            provider=config.tts_provider,
            elevenlabs_voice_id=config.elevenlabs_voice_id
        )
        self.visual_generator = VisualGenerator(
            provider=config.image_provider,
            gcp_project_id=config.gcp_project_id,
            gcp_location=config.gcp_location,
            vertex_ai_imagen_model_id=config.vertex_ai_imagen_model_id
        )
        self.video_assembler = VideoAssembler()
        
        logger.info("ShortVideoFactory initialized with all components.")
        
    def create_video(self, subject: Optional[str] = None, num_scenes: Optional[int] = None) -> Dict[str, Union[bool, str, Dict]]:
        """
        Execute the full video creation pipeline: story -> narration -> visuals -> assembly.
        
        Args:
            subject: Optional subject override for story generation
            num_scenes: Optional number of scenes override
            
        Returns:
            Dictionary with process results and output paths
        """
        final_subject = subject or self.config.story_subject
        final_num_scenes = num_scenes or self.config.num_scenes
        
        logger.info(f"Starting video creation for subject: '{final_subject}' with {final_num_scenes} scenes...")
        
        # 1. Generate structured story
        story_result = self.generate_story(final_subject, final_num_scenes)
        if not story_result["success"]:
            return {
                "success": False,
                "error": f"Story generation failed: {story_result.get('error', 'Unknown error')}",
                "steps_completed": []
            }
        
        structured_story = story_result["story"]
        
        # 2. Generate narrations for each scene
        narration_results = self.generate_narrations(structured_story)
        if not narration_results["success"]:
            return {
                "success": False,
                "error": f"Narration generation failed: {narration_results.get('error', 'Unknown error')}",
                "steps_completed": ["story"],
                "story": story_result
            }
            
        # 3. Generate visuals for each scene
        visual_results = self.generate_visuals(structured_story)
        if not visual_results["success"]:
            return {
                "success": False,
                "error": f"Visual generation failed: {visual_results.get('error', 'Unknown error')}",
                "steps_completed": ["story", "narration"],
                "story": story_result,
                "narration": narration_results
            }
            
        # 4. Assemble video from narrations and visuals
        valid_scene_data = self._collect_valid_scene_data(narration_results["results"], visual_results["results"])
        
        if not valid_scene_data:
            return {
                "success": False,
                "error": "No valid scene data for video assembly.",
                "steps_completed": ["story", "narration", "visuals"],
                "story": story_result,
                "narration": narration_results,
                "visuals": visual_results
            }
            
        video_result = self.assemble_video(valid_scene_data)
        
        return {
            "success": video_result["success"],
            "error": video_result.get("error", ""),
            "steps_completed": ["story", "narration", "visuals", "video"] if video_result["success"] else ["story", "narration", "visuals"],
            "story": story_result,
            "narration": narration_results,
            "visuals": visual_results,
            "video": video_result
        }
            
    def generate_story(self, subject: str, num_scenes: int) -> Dict[str, Union[bool, str, StoryWithScenes]]:
        """
        Generate a structured story with scenes.
        
        Args:
            subject: Subject for the story
            num_scenes: Number of scenes to generate
            
        Returns:
            Dictionary with success flag, story object and error if any
        """
        logger.info(f"Generating story for subject: '{subject}' with {num_scenes} scenes...")
        
        try:
            result = self.story_generator.generate_structured_story(subject, num_scenes)
            
            if isinstance(result, StoryWithScenes):
                logger.info(f"Successfully generated story: '{result.title}'")
                return {"success": True, "story": result}
            else:
                error_msg = f"Story generation returned unexpected result: {result}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error during story generation: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def generate_narrations(self, story: StoryWithScenes) -> Dict[str, Union[bool, str, List[GenerationResult]]]:
        """
        Generate narrations for all scenes in the story.
        
        Args:
            story: Structured story with scenes
            
        Returns:
            Dictionary with success flag, results list and error if any
        """
        logger.info(f"Generating narrations for {len(story.scenes)} scenes...")
        
        narration_results = []
        audio_dir = self.config.output_directories.get("audios", "shortfactory_output/story_audios")
        os.makedirs(audio_dir, exist_ok=True)
        
        try:
            for scene in story.scenes:
                audio_path = os.path.join(audio_dir, f"scene_{scene.scene_number}_narration.mp3")
                result = self.narration_generator.generate_narration(scene.narration_text, audio_path)
                narration_results.append(result)
                
                if result.success:
                    logger.info(f"Generated narration for scene {scene.scene_number}, duration: {result.duration:.2f}s")
                else:
                    logger.error(f"Failed to generate narration for scene {scene.scene_number}: {result.error}")
                
            # Check if at least one narration succeeded
            if any(result.success for result in narration_results):
                return {"success": True, "results": narration_results}
            else:
                return {"success": False, "error": "All narration generation attempts failed.", "results": narration_results}
                
        except Exception as e:
            error_msg = f"Error during narration generation: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "results": narration_results}
            
    def generate_visuals(self, story: StoryWithScenes) -> Dict[str, Union[bool, str, List[GenerationResult]]]:
        """
        Generate visuals for all scenes in the story.
        
        Args:
            story: Structured story with scenes
            
        Returns:
            Dictionary with success flag, results list and error if any
        """
        logger.info(f"Generating visuals for {len(story.scenes)} scenes...")
        
        visual_results = []
        images_dir = self.config.output_directories.get("images", "shortfactory_output/story_images")
        os.makedirs(images_dir, exist_ok=True)
        
        try:
            for scene in story.scenes:
                image_path = os.path.join(images_dir, f"scene_{scene.scene_number}_image.png")
                result = self.visual_generator.generate_image(
                    overall_image_style=story.overall_image_style,
                    main_characters=story.main_characters,
                    scene_visual_description=scene.visual_description,
                    output_path=image_path
                )
                visual_results.append(result)
                
                if result.success:
                    logger.info(f"Generated image for scene {scene.scene_number}")
                else:
                    logger.error(f"Failed to generate image for scene {scene.scene_number}: {result.error}")
                
            # Check if at least one visual succeeded
            if any(result.success for result in visual_results):
                return {"success": True, "results": visual_results}
            else:
                return {"success": False, "error": "All image generation attempts failed.", "results": visual_results}
                
        except Exception as e:
            error_msg = f"Error during visual generation: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "results": visual_results}
            
    def assemble_video(self, valid_scene_data: List[Tuple[str, str, float]]) -> Dict[str, Union[bool, str, GenerationResult]]:
        """
        Assemble final video from valid scene data.
        
        Args:
            valid_scene_data: List of tuples (image_path, audio_path, audio_duration)
            
        Returns:
            Dictionary with success flag, video result and error if any
        """
        if not valid_scene_data:
            error_msg = "No valid scene data provided for video assembly."
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
            
        videos_dir = self.config.output_directories.get("videos", "shortfactory_output/final_videos")
        os.makedirs(videos_dir, exist_ok=True)
        
        video_path = os.path.join(videos_dir, "final_video.mp4")
        
        try:
            # Unpack scene data
            image_paths = [item[0] for item in valid_scene_data]
            audio_paths = [item[1] for item in valid_scene_data]
            audio_durations = [item[2] for item in valid_scene_data]
            
            # Assemble video
            result = self.video_assembler.assemble_video(
                image_paths=image_paths,
                audio_paths=audio_paths,
                audio_durations=audio_durations,
                output_video_path=video_path,
                image_transition_duration=self.config.image_transition_duration,
                fps=self.config.video_fps
            )
            
            if result.success:
                logger.info(f"Successfully assembled video: {video_path}")
                return {"success": True, "result": result, "video_path": video_path}
            else:
                error_msg = f"Video assembly failed: {result.error}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg, "result": result}
                
        except Exception as e:
            error_msg = f"Error during video assembly: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _collect_valid_scene_data(self, narration_results: List[GenerationResult], visual_results: List[GenerationResult]) -> List[Tuple[str, str, float]]:
        """
        Collect valid scene data from narration and visual results.
        
        Args:
            narration_results: List of narration generation results
            visual_results: List of visual generation results
            
        Returns:
            List of tuples (image_path, audio_path, audio_duration) for valid scenes
        """
        valid_scene_data = []
        
        for i, (narration, visual) in enumerate(zip(narration_results, visual_results)):
            if narration.success and visual.success:
                valid_scene_data.append((visual.output_path, narration.output_path, narration.duration))
            else:
                logger.warning(f"Skipping scene {i+1} due to failed generation (narration success: {narration.success}, visual success: {visual.success})")
                
        return valid_scene_data
