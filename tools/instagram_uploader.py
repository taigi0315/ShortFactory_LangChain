import os
import time
from typing import Optional

from instagram_private_api import Client, ClientCompatPatch

from utils.logger import setup_logger

# 로거 설정
logger = setup_logger("instagram_uploader")


class InstagramUploader:
    def __init__(self):
        logger.info("InstagramUploader 초기화 중...")
        self.username = os.getenv("INSTAGRAM_USERNAME")
        self.password = os.getenv("INSTAGRAM_PASSWORD")

        if not all([self.username, self.password]):
            logger.error("Instagram API 설정이 완료되지 않았습니다")
            raise ValueError("Instagram API 설정이 필요합니다")

        self.api = self._login()
        logger.info("InstagramUploader 초기화 완료")

    def _login(self) -> Client:
        """Instagram API에 로그인합니다."""
        try:
            api = Client(self.username, self.password)
            return api
        except Exception as e:
            logger.error(f"Instagram 로그인 실패: {str(e)}")
            raise

    def upload_video(
        self, video_path: str, caption: str, hashtags: Optional[list] = None
    ) -> bool:
        """
        Instagram에 비디오를 업로드합니다.

        Args:
            video_path (str): 비디오 파일 경로
            caption (str): 비디오 설명
            hashtags (Optional[list]): 해시태그 리스트

        Returns:
            bool: 업로드 성공 여부
        """
        try:
            logger.info(f"Instagram 업로드 시작: {video_path}")

            # 해시태그를 캡션에 추가
            if hashtags:
                caption = f"{caption}\n\n{' '.join(hashtags)}"

            # 비디오 업로드
            result = self.api.post_video(
                video_path,
                caption=caption,
                video_size=(1080, 1920),  # Instagram Reels 크기
            )

            if result.get("status") == "ok":
                logger.info("Instagram 업로드 완료")
                return True
            else:
                raise Exception(f"업로드 실패: {result}")

        except Exception as e:
            logger.error(f"Instagram 업로드 실패: {str(e)}")
            raise
