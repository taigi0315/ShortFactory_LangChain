"""
Video Assembler module for creating videos from images and audio narrations.
"""

import os
import logging
from typing import List, Optional

import moviepy.editor as mpy_editor
from moviepy.audio.AudioClip import AudioClip
from moviepy.video.VideoClip import ImageClip

from src.models.schemas import GenerationResult

logger = logging.getLogger(__name__)

class VideoAssembler:
    """
    Class for assembling videos from images and audio narrations.
    Uses MoviePy for video processing and assembly.
    """
    
    def __init__(self):
        """Initialize the VideoAssembler."""
        logger.info("VideoAssembler initialized.")

    def assemble_video(self,
                      image_paths: List[str],
                      audio_paths: List[str],
                      audio_durations: List[float],
                      output_video_path: str,
                      image_transition_duration: float = 0.5,
                      fps: int = 24) -> GenerationResult:
        """
        Assembles a video from a list of image files and corresponding audio narration.
        
        Args:
            image_paths: List of paths to the image files
            audio_paths: List of paths to the audio narration files
            audio_durations: List of durations for each audio file
            output_video_path: Path where to save the output video
            image_transition_duration: Duration of transition between images
            fps: Frames per second for the output video
            
        Returns:
            GenerationResult with success status and output information
        """
        logger.info("Starting video assembly process...")
        if len(image_paths) != len(audio_paths) or len(audio_paths) != len(audio_durations):
            error_msg = "Length mismatch: image_paths, audio_paths, and audio_durations must have the same length."
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)
            
        if not image_paths:
            error_msg = "No images provided for video assembly."
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
            
        try:
            # Create video clips for each scene
            scene_clips = []
            
            for i, (img_path, audio_path, audio_duration) in enumerate(zip(image_paths, audio_paths, audio_durations)):
                logger.info(f"Processing scene {i+1}...")
                
                # Create image clip with duration matching the audio
                img_clip = ImageClip(img_path, duration=audio_duration)
                
                # Add audio to the image clip
                audio_clip = mpy_editor.AudioFileClip(audio_path)
                video_clip = img_clip.set_audio(audio_clip)
                
                scene_clips.append(video_clip)
                
            # Concatenate all clips
            logger.info(f"Concatenating {len(scene_clips)} scenes...")
            final_clip = mpy_editor.concatenate_videoclips(scene_clips, method="compose", transition=mpy_editor.VideoFileClip.fadein(image_transition_duration) if image_transition_duration > 0 else None)
            
            # Write output video file
            logger.info(f"Writing video file to {output_video_path}...")
            final_clip.write_videofile(output_video_path, fps=fps, codec="libx264", audio_codec="aac")
            
            logger.info(f"Video assembly complete. Video saved to {output_video_path}")
            return GenerationResult(success=True, output_path=output_video_path)
        except Exception as e:
            error_msg = f"Error during video assembly: {e}"
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)
            
    def create_slideshow_with_background_music(self,
                                             image_paths: List[str],
                                             output_video_path: str, 
                                             background_music_path: Optional[str] = None,
                                             slide_duration: float = 3.0,
                                             transition_duration: float = 0.5,
                                             fps: int = 24) -> GenerationResult:
        """
        Creates a slideshow video from a list of images with optional background music.
        
        Args:
            image_paths: List of paths to the image files
            output_video_path: Path where to save the output video
            background_music_path: Optional path to background music file
            slide_duration: Duration to show each image
            transition_duration: Duration of transition between images
            fps: Frames per second for the output video
            
        Returns:
            GenerationResult with success status and output information
        """
        logger.info("Starting slideshow creation...")
        if not image_paths:
            error_msg = "No images provided for slideshow creation."
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
            
        try:
            # Create clips for each image
            clips = [ImageClip(img_path, duration=slide_duration) for img_path in image_paths]
            
            # Concatenate all clips with transitions
            if transition_duration > 0:
                concat_clip = mpy_editor.concatenate_videoclips(clips, method="compose", transition=mpy_editor.VideoFileClip.fadein(transition_duration))
            else:
                concat_clip = mpy_editor.concatenate_videoclips(clips, method="compose")
            
            # Add background music if provided
            if background_music_path and os.path.exists(background_music_path):
                audio = mpy_editor.AudioFileClip(background_music_path)
                # Loop the audio if it's shorter than the video
                if audio.duration < concat_clip.duration:
                    audio = mpy_editor.afx.audio_loop(audio, duration=concat_clip.duration)
                else:
                    # Trim audio if longer than the video
                    audio = audio.subclip(0, concat_clip.duration)
                concat_clip = concat_clip.set_audio(audio)
                
            # Write output video file
            logger.info(f"Writing slideshow video file to {output_video_path}...")
            concat_clip.write_videofile(output_video_path, fps=fps, codec="libx264", audio_codec="aac" if background_music_path else None)
            
            logger.info(f"Slideshow creation complete. Video saved to {output_video_path}")
            return GenerationResult(success=True, output_path=output_video_path)
        except Exception as e:
            error_msg = f"Error during slideshow creation: {e}"
            logger.error(error_msg)
            return GenerationResult(success=False, output_path="", error=error_msg)
