import json
import os
from typing import Optional

import requests

from utils.logger import setup_logger

# 로거 설정
logger = setup_logger("tiktok_uploader")

class TikTokUploader:
    def __init__(self):
        logger.info("TikTokUploader 초기화 중...")
        self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        self.open_id = os.getenv("TIKTOK_OPEN_ID")

        if not all([self.access_token, self.open_id]):
            logger.error("TikTok API 설정이 완료되지 않았습니다")
            raise ValueError("TikTok API 설정이 필요합니다")

        self.base_url = "https://open.tiktokapis.com/v2"
        logger.info("TikTokUploader 초기화 완료")

    def upload_video(
        self, video_path: str, caption: str, hashtags: Optional[list] = None
    ) -> bool:
        """
        TikTok에 비디오를 업로드합니다.

        Args:
            video_path (str): 비디오 파일 경로
            caption (str): 비디오 설명
            hashtags (Optional[list]): 해시태그 리스트

        Returns:
            bool: 업로드 성공 여부
        """
        try:
            logger.info(f"TikTok 업로드 시작: {video_path}")

            # 1. 비디오 업로드 URL 가져오기
            upload_url = self._get_upload_url()

            # 2. 비디오 파일 업로드
            video_id = self._upload_video_file(upload_url, video_path)

            # 3. 포스트 생성
            self._create_post(video_id, caption, hashtags)

            logger.info("TikTok 업로드 완료")
            return True

        except Exception as e:
            logger.error(f"TikTok 업로드 실패: {str(e)}")
            raise

    def _get_upload_url(self) -> str:
        """비디오 업로드 URL을 가져옵니다."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            f"{self.base_url}/video/upload/",
            headers=headers,
            json={"source_info": {"source": "FILE_UPLOAD"}},
        )

        if response.status_code != 200:
            raise Exception(f"업로드 URL 요청 실패: {response.text}")

        return response.json()["data"]["upload_url"]

    def _upload_video_file(self, upload_url: str, video_path: str) -> str:
        """비디오 파일을 업로드합니다."""
        with open(video_path, "rb") as f:
            response = requests.put(upload_url, data=f)

        if response.status_code != 200:
            raise Exception(f"비디오 업로드 실패: {response.text}")

        return response.json()["data"]["video_id"]

    def _create_post(
        self, video_id: str, caption: str, hashtags: Optional[list] = None
    ):
        """포스트를 생성합니다."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        data = {"video_id": video_id, "caption": caption, "hashtags": hashtags or []}

        response = requests.post(
            f"{self.base_url}/video/publish/", headers=headers, json=data
        )

        if response.status_code != 200:
            raise Exception(f"포스트 생성 실패: {response.text}")
