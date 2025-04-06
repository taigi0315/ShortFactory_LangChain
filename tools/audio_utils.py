import os
import subprocess
import wave
from pathlib import Path
from typing import List, Tuple

from utils.logger import setup_logger

# 로거 설정
logger = setup_logger("audio_utils")


class AudioUtils:
    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """
        오디오 파일의 길이를 초 단위로 반환합니다.

        Args:
            file_path (str): 오디오 파일 경로

        Returns:
            float: 오디오 파일의 길이(초)
        """
        logger.debug(f"오디오 파일 길이 확인: {file_path}")

        try:
            cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {file_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            duration = float(result.stdout.strip())
            logger.debug(f"오디오 길이: {duration}초")
            return duration
        except subprocess.CalledProcessError as e:
            logger.error(f"오디오 길이 확인 실패: {str(e)}")
            raise

    @staticmethod
    def create_silence(duration: float, output_file: str) -> None:
        # TODO: Implement silence generation
        pass

    @staticmethod
    def normalize_audio(file_path: str) -> str:
        """
        오디오 파일의 볼륨을 정규화합니다.

        Args:
            file_path (str): 오디오 파일 경로

        Returns:
            str: 정규화된 오디오 파일 경로
        """
        logger.info(f"오디오 정규화 시작: {file_path}")

        output_path = str(Path(file_path).with_suffix(".normalized.mp3"))

        try:
            cmd = f"ffmpeg -i {file_path} -filter:a loudnorm -ar 44100 {output_path}"
            subprocess.run(cmd, shell=True, check=True)
            logger.debug(f"오디오 정규화 완료: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"오디오 정규화 실패: {str(e)}")
            raise

    @staticmethod
    def combine_audio_files(audio_files: List[str], output_path: str) -> str:
        """
        여러 오디오 파일을 하나로 결합합니다.

        Args:
            audio_files (List[str]): 오디오 파일 경로들의 리스트
            output_path (str): 출력 파일 경로

        Returns:
            str: 결합된 오디오 파일 경로
        """
        logger.info(f"오디오 파일 결합 시작 - {len(audio_files)}개의 파일")

        try:
            # 파일 목록 생성
            with open("temp_list.txt", "w") as f:
                for file in audio_files:
                    f.write(f"file '{file}'\n")

            # FFmpeg로 파일 결합
            cmd = f"ffmpeg -f concat -safe 0 -i temp_list.txt -c copy {output_path}"
            subprocess.run(cmd, shell=True, check=True)

            # 임시 파일 삭제
            Path("temp_list.txt").unlink()

            logger.debug(f"오디오 파일 결합 완료: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"오디오 파일 결합 실패: {str(e)}")
            raise
