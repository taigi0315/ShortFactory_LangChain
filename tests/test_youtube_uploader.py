from unittest.mock import Mock, patch

import pytest

from tools.youtube_uploader import YouTubeUploader


@pytest.fixture
def mock_youtube_service():
    with patch("tools.youtube_uploader.build") as mock_build:
        mock_service = Mock()
        mock_build.return_value = mock_service
        yield mock_service


@pytest.fixture
def youtube_uploader(mock_youtube_service):
    with patch.dict(
        "os.environ",
        {
            "YOUTUBE_API_KEY": "test_key",
            "YOUTUBE_CLIENT_SECRETS_FILE": "test_secrets.json",
            "YOUTUBE_CREDENTIALS_PATH": "test_credentials.json",
        },
    ):
        uploader = YouTubeUploader()
        return uploader


def test_upload_video_success(youtube_uploader, mock_youtube_service):
    # 테스트 데이터 설정
    video_path = "test_video.mp4"
    title = "Test Video"
    description = "Test Description"
    tags = ["test", "video"]

    # mock 설정
    mock_videos = Mock()
    mock_videos.insert.return_value.execute.return_value = {"id": "test_video_id"}
    mock_youtube_service.videos.return_value = mock_videos

    # 테스트 실행
    result = youtube_uploader.upload_video(
        video_path=video_path, title=title, description=description, tags=tags
    )

    # 검증
    assert result is True
    mock_videos.insert.assert_called_once()
    call_args = mock_videos.insert.call_args[1]
    assert call_args["body"]["snippet"]["title"] == title
    assert call_args["body"]["snippet"]["description"] == description
    assert call_args["body"]["snippet"]["tags"] == tags


def test_upload_video_failure(youtube_uploader, mock_youtube_service):
    # 테스트 데이터 설정
    video_path = "test_video.mp4"

    # mock 설정
    mock_videos = Mock()
    mock_videos.insert.return_value.execute.side_effect = Exception("Upload failed")
    mock_youtube_service.videos.return_value = mock_videos

    # 테스트 실행 및 검증
    with pytest.raises(Exception) as exc_info:
        youtube_uploader.upload_video(
            video_path=video_path, title="Test", description="Test"
        )
    assert str(exc_info.value) == "Upload failed"
