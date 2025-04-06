from unittest.mock import Mock, patch

import pytest

from tools.instagram_uploader import InstagramUploader


@pytest.fixture
def mock_instagram_api():
    with patch("tools.instagram_uploader.Client") as mock_client:
        mock_api = Mock()
        mock_client.return_value = mock_api
        yield mock_api


@pytest.fixture
def instagram_uploader(mock_instagram_api):
    with patch.dict(
        "os.environ",
        {"INSTAGRAM_USERNAME": "test_user", "INSTAGRAM_PASSWORD": "test_pass"},
    ):
        uploader = InstagramUploader()
        return uploader


def test_upload_video_success(instagram_uploader, mock_instagram_api):
    # 테스트 데이터 설정
    video_path = "test_video.mp4"
    caption = "Test Caption"
    hashtags = ["test", "video"]

    # mock 응답 설정
    mock_instagram_api.post_video.return_value = {"status": "ok"}

    # 테스트 실행
    result = instagram_uploader.upload_video(
        video_path=video_path, caption=caption, hashtags=hashtags
    )

    # 검증
    assert result is True
    mock_instagram_api.post_video.assert_called_once_with(
        video_path,
        caption=f"{caption}\n\n{' '.join(hashtags)}",
        video_size=(1080, 1920),
    )


def test_upload_video_failure(instagram_uploader, mock_instagram_api):
    # 테스트 데이터 설정
    video_path = "test_video.mp4"

    # mock 실패 응답 설정
    mock_instagram_api.post_video.return_value = {"status": "error"}

    # 테스트 실행 및 검증
    with pytest.raises(Exception) as exc_info:
        instagram_uploader.upload_video(
            video_path=video_path, caption="Test", hashtags=["test"]
        )
    assert "업로드 실패" in str(exc_info.value)
