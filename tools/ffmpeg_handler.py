import subprocess
from pathlib import Path
from typing import List

import ffmpeg

from utils.logger import setup_logger

# 로거 설정
logger = setup_logger("ffmpeg_handler")


class FFmpegHandler:
    def __init__(self):
        logger.info("FFmpegHandler 초기화 중...")
        self.temp_dir = Path("output/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info("FFmpegHandler 초기화 완료")

    def mix_audio_files(self, audio_files: List[str]) -> str:
        """
        여러 오디오 파일을 하나로 믹싱합니다.

        Args:
            audio_files (List[str]): 오디오 파일 경로들의 리스트

        Returns:
            str: 믹싱된 오디오 파일 경로
        """
        logger.info(f"오디오 믹싱 시작 - {len(audio_files)}개의 파일")

        # 임시 파일 경로
        output_file = self.temp_dir / "mixed_audio.mp3"

        # FFmpeg 명령어 구성
        inputs = []
        filter_complex = []

        for i, file in enumerate(audio_files):
            inputs.append(f"-i {file}")
            filter_complex.append(f"[{i}:a]")

        filter_complex.append(f"concat=n={len(audio_files)}:v=0:a=1[outa]")

        # FFmpeg 실행
        cmd = f"ffmpeg {' '.join(inputs)} -filter_complex '{' '.join(filter_complex)}' -map '[outa]' {output_file}"
        logger.debug(f"FFmpeg 명령어: {cmd}")

        try:
            subprocess.run(cmd, shell=True, check=True)
            logger.debug(f"오디오 믹싱 완료: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            logger.error(f"오디오 믹싱 실패: {str(e)}")
            raise

    def create_video(
        self,
        audio_file: str,
        subtitle_file: str,
        background_video: str,
        output_filename: str,
    ) -> str:
        """
        비디오를 생성합니다.

        Args:
            audio_file (str): 오디오 파일 경로
            subtitle_file (str): 자막 파일 경로
            background_video (str): 배경 비디오 파일 경로
            output_filename (str): 출력 파일 이름

        Returns:
            str: 생성된 비디오 파일 경로
        """
        logger.info("비디오 생성 시작")
        logger.debug(f"입력 파일: {audio_file}, {subtitle_file}, {background_video}")

        output_path = Path("output/videos") / output_filename

        try:
            # FFmpeg 스트림 설정
            stream = ffmpeg.input(background_video)
            audio = ffmpeg.input(audio_file)

            # 자막 추가
            stream = ffmpeg.filter(stream, "subtitles", subtitle_file)

            # 오디오와 비디오 결합
            stream = ffmpeg.output(
                stream,
                audio,
                str(output_path),
                acodec="aac",
                vcodec="libx264",
                preset="medium",
                movflags="faststart",
            )

            # FFmpeg 실행
            ffmpeg.run(stream, overwrite_output=True)
            logger.debug(f"비디오 생성 완료: {output_path}")
            return str(output_path)
        except ffmpeg.Error as e:
            logger.error(f"비디오 생성 실패: {str(e)}")
            raise

    def cleanup_temp_files(self):
        """
        임시 파일들을 정리합니다.
        """
        logger.info("임시 파일 정리 시작")

        try:
            for file in self.temp_dir.glob("*"):
                file.unlink()
            logger.debug("임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {str(e)}")
            raise
