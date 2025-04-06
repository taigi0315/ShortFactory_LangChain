import os
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from utils.logger import setup_logger

# 로거 설정
logger = setup_logger("youtube_uploader")


class YouTubeUploader:
    def __init__(self):
        logger.info("YouTubeUploader 초기화 중...")
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.client_secrets_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE")
        self.credentials_path = os.getenv("YOUTUBE_CREDENTIALS_PATH")

        if not all([self.api_key, self.client_secrets_file, self.credentials_path]):
            logger.error("YouTube API 설정이 완료되지 않았습니다")
            raise ValueError("YouTube API 설정이 필요합니다")

        self.youtube = self._get_youtube_service()
        logger.info("YouTubeUploader 초기화 완료")

    def _get_youtube_service(self):
        """YouTube API 서비스를 초기화합니다."""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_file,
                ["https://www.googleapis.com/auth/youtube.upload"],
            )

            if os.path.exists(self.credentials_path):
                credentials = Credentials.from_authorized_user_file(
                    self.credentials_path,
                    ["https://www.googleapis.com/auth/youtube.upload"],
                )
            else:
                credentials = flow.run_local_server(port=0)
                with open(self.credentials_path, "w") as token:
                    token.write(credentials.to_json())

            return build("youtube", "v3", credentials=credentials)
        except Exception as e:
            logger.error(f"YouTube 서비스 초기화 실패: {str(e)}")
            raise

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[list] = None,
        privacy_status: str = "private",
    ) -> bool:
        """
        YouTube에 비디오를 업로드합니다.

        Args:
            video_path (str): 비디오 파일 경로
            title (str): 비디오 제목
            description (str): 비디오 설명
            tags (Optional[list]): 태그 리스트
            privacy_status (str): 공개 상태 ("private", "unlisted", "public")

        Returns:
            bool: 업로드 성공 여부
        """
        try:
            logger.info(f"YouTube 업로드 시작: {video_path}")

            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags or [],
                },
                "status": {"privacyStatus": privacy_status},
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

            request = self.youtube.videos().insert(
                part=",".join(body.keys()), body=body, media_body=media
            )

            response = request.execute()
            logger.info(f"YouTube 업로드 완료: {response['id']}")
            return True

        except HttpError as e:
            logger.error(f"YouTube 업로드 실패: {str(e)}")
            raise
