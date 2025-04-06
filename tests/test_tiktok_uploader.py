from unittest.mock import Mock, patch

import pytest

from tools.tiktok_uploader import TikTokUploader


@pytest.fixture
def mock_requests():
    with patch("tools.tiktok_uploader.requests") as mock_requests:
        yield mock_requests


@pytest.fixture
def tiktok_uploader(mock_requests):
    with patch.dict(
        "os.environ",
        {"TIKTOK_ACCESS_TOKEN": "test_token", "TIKTOK_OPEN_ID": "test_open_id"},
    ):
        uploader = TikTokUploader()
        return uploader


def test_upload_video_success(tiktok_uploader, mock_requests):
    # 테스트 데이터 설정
    video_path = "test_video.mp4"
    caption = "Test Caption"
    hashtags = ["test", "video"]

    # mock 응답 설정
    mock_requests.post.return_value.status_code = 200
    mock_requests.post.return_value.json.return_value = {
        "data": {"upload_url": "https://test.upload.url"}
    }
    mock_requests.put.return_value.status_code = 200
    mock_requests.put.return_value.json.return_value = {
        "data": {"video_id": "test_video_id"}
    }

    # 테스트 실행
    result = tiktok_uploader.upload_video(
        video_path=video_path, caption=caption, hashtags=hashtags
    )

    # 검증
    assert result is True
    assert mock_requests.post.call_count == 2  # upload_url 요청과 포스트 생성
    assert mock_requests.put.call_count == 1  # 비디오 업로드


def test_upload_video_failure(tiktok_uploader, mock_requests):
    # 테스트 데이터 설정
    video_path = "test_video.mp4"

    # mock 실패 응답 설정
    mock_requests.post.return_value.status_code = 400
    mock_requests.post.return_value.text = "Upload failed"

    # 테스트 실행 및 검증
    with pytest.raises(Exception) as exc_info:
        tiktok_uploader.upload_video(
            video_path=video_path, caption="Test", hashtags=["test"]
        )
    assert "Upload failed" in str(exc_info.value)
