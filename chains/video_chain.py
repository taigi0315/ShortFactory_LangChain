import ffmpeg
from typing import List
import os
from pathlib import Path
import json
import subprocess
from tools.ffmpeg_handler import FFmpegHandler
from utils.logger import setup_logger

# 로거 설정
logger = setup_logger("video_chain")

class VideoChain:
    def __init__(self):
        logger.info("VideoChain 초기화 중...")
        self.ffmpeg = FFmpegHandler()
        self.output_dir = Path("output/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("VideoChain 초기화 완료")
    
    def create_video(
        self,
        audio_files: List[str],
        subtitle_file: str,
        background_video: str,
        output_filename: str = "final_shorts.mp4"
    ) -> str:
        """
        최종 비디오를 생성합니다.
        
        Args:
            audio_files (List[str]): 오디오 파일 경로들의 리스트
            subtitle_file (str): 자막 파일 경로
            background_video (str): 배경 비디오 파일 경로
            output_filename (str): 출력 파일 이름
            
        Returns:
            str: 생성된 비디오 파일 경로
        """
        logger.info("비디오 생성 시작")
        logger.debug(f"입력 파일: {len(audio_files)}개의 오디오, {subtitle_file}, {background_video}")
        
        # 오디오 믹싱
        logger.info("오디오 믹싱 중...")
        mixed_audio = self.ffmpeg.mix_audio_files(audio_files)
        logger.debug(f"믹싱된 오디오: {mixed_audio}")
        
        # 비디오 생성
        logger.info("비디오 생성 중...")
        output_path = self.ffmpeg.create_video(
            audio_file=mixed_audio,
            subtitle_file=subtitle_file,
            background_video=background_video,
            output_filename=output_filename
        )
        logger.debug(f"생성된 비디오: {output_path}")
        
        # 임시 파일 정리
        logger.info("임시 파일 정리 중...")
        self.ffmpeg.cleanup_temp_files()
        logger.debug("임시 파일 정리 완료")
        
        logger.info(f"비디오 생성 완료: {output_path}")
        return output_path
    
    def _combine_audio_files(self, audio_files: List[str]) -> str:
        """
        여러 오디오 파일들을 하나로 결합합니다.
        
        Args:
            audio_files (List[str]): 오디오 파일 경로들의 리스트
            
        Returns:
            str: 결합된 오디오 파일의 경로
        """
        if not audio_files:
            raise ValueError("No audio files provided")
            
        # 임시 파일 생성
        temp_file = self.output_dir / "temp_combined.mp3"
        
        # 첫 번째 파일을 시작점으로 사용
        stream = ffmpeg.input(audio_files[0])
        
        # 나머지 파일들을 순차적으로 결합
        for audio_file in audio_files[1:]:
            next_stream = ffmpeg.input(audio_file)
            stream = ffmpeg.concat(stream, next_stream)
        
        # 최종 파일 저장
        stream = ffmpeg.output(stream, str(temp_file))
        ffmpeg.run(stream, overwrite_output=True)
        
        return str(temp_file) 