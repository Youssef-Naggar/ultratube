import pytest
from unittest.mock import MagicMock, patch
from ultratube_extractor import UltraTubeExtractor
from models import DownloadOptions, VideoInfo, AudioTrack, Subtitle


def test_is_valid_url_syntax_check():
    extractor = UltraTubeExtractor()

    # Empty URL
    is_valid, msg = extractor.is_valid_url("")
    assert is_valid is False
    assert "cannot be empty" in msg.lower()

    # Malformed URL
    is_valid, msg = extractor.is_valid_url("not-a-url")
    assert is_valid is False
    assert "invalid url format" in msg.lower()

    is_valid, msg = extractor.is_valid_url("ftp://youtube.com/watch?v=123")
    assert is_valid is False
    assert "invalid url format" in msg.lower()


@patch("ultratube_extractor.MetadataService")
def test_is_valid_url_semantic_success(mock_meta_cls):
    # Setup mock
    mock_meta = mock_meta_cls.return_value
    mock_meta.get_video_info.return_value = MagicMock(spec=VideoInfo)

    extractor = UltraTubeExtractor()
    is_valid, msg = extractor.is_valid_url("https://www.youtube.com/watch?v=abc12345678")

    assert is_valid is True
    assert msg is None
    mock_meta.get_video_info.assert_called_once_with("https://www.youtube.com/watch?v=abc12345678")


@patch("ultratube_extractor.MetadataService")
def test_is_valid_url_semantic_value_error(mock_meta_cls):
    # Unsupported URL case
    mock_meta = mock_meta_cls.return_value
    mock_meta.get_video_info.side_effect = ValueError("Unsupported URL")

    extractor = UltraTubeExtractor()
    is_valid, msg = extractor.is_valid_url("https://unsupported.com/video")
    assert is_valid is False
    assert "unsupported platform" in msg.lower()

    # Private or deleted video case
    mock_meta.get_video_info.side_effect = ValueError("Private video")
    is_valid, msg = extractor.is_valid_url("https://www.youtube.com/watch?v=private")
    assert is_valid is False
    assert "private, deleted, or offline" in msg.lower()


@patch("ultratube_extractor.MetadataService")
def test_is_valid_url_semantic_generic_error(mock_meta_cls):
    mock_meta = mock_meta_cls.return_value
    mock_meta.get_video_info.side_effect = RuntimeError("Connection timed out")

    extractor = UltraTubeExtractor()
    is_valid, msg = extractor.is_valid_url("https://www.youtube.com/watch?v=timeout")
    assert is_valid is False
    assert "network or extraction error" in msg.lower()


@patch("ultratube_extractor.MetadataService")
def test_facade_delegation_to_metadata_service(mock_meta_cls):
    mock_meta = mock_meta_cls.return_value
    extractor = UltraTubeExtractor()

    # get_available_formats
    extractor.get_available_formats("url_fmt", is_audio=True)
    mock_meta.get_available_formats.assert_called_once_with("url_fmt", True)

    # get_audio_tracks
    extractor.get_audio_tracks("url_tracks")
    mock_meta.get_audio_tracks.assert_called_once_with("url_tracks")

    # get_available_subtitles
    extractor.get_available_subtitles("url_subs")
    mock_meta.get_available_subtitles.assert_called_once_with("url_subs")

    # get_playlist_info
    extractor.get_playlist_info("url_playlist")
    mock_meta.get_playlist_info.assert_called_once_with("url_playlist")


@patch("ultratube_extractor.DownloadService")
def test_facade_delegation_to_download_service(mock_dl_cls):
    mock_dl = mock_dl_cls.return_value
    extractor = UltraTubeExtractor()
    options = DownloadOptions(output_directory="C:/Downloads", output_format="mp3")

    # download_audio
    extractor.download_audio("url_audio", options)
    mock_dl.download_audio.assert_called_once_with("url_audio", options, None, None)

    # download_video
    extractor.download_video("url_video", "1080p", options)
    mock_dl.download_video.assert_called_once_with("url_video", "1080p", options, None, None)


@patch("ultratube_extractor.FileService")
def test_facade_delegation_to_file_service(mock_file_cls):
    mock_file = mock_file_cls.return_value
    mock_file.merge_subtitles.return_value = "C:/merged.mp4"
    
    extractor = UltraTubeExtractor()
    result = extractor.merge_subtitles("C:/video.mp4", ["C:/sub.vtt"], "C:/merged.mp4")

    mock_file.merge_subtitles.assert_called_once_with("C:/video.mp4", ["C:/sub.vtt"], "C:/merged.mp4")
    assert result == "C:/merged.mp4"
