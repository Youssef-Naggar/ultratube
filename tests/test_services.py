import pytest
import os
import sys
import time
from unittest.mock import MagicMock, patch
from metadata_service import MetadataService, get_clean_language_name
from file_service import FileService
from download_service import DownloadService, YtDlpLogger
from models import DownloadOptions, ProcessOptions


def test_get_clean_language_name():
    # Test valid mapped code
    assert get_clean_language_name("en", "") == "English"
    assert get_clean_language_name("ar-EG", "") == "Arabic"
    assert get_clean_language_name("es", "Spanish original") == "Spanish original"

    # Test unmapped but valid string
    assert get_clean_language_name("und", "custom-language") == "custom-language"

    # Test default/unknown fallback
    assert get_clean_language_name("und", "") == "Default"
    assert get_clean_language_name(None, "") == "Default"


@patch("metadata_service.MetadataService._extract_video_info")
def test_metadata_service_cache_and_ttl(mock_extract):
    raw_data = {
        "id": "abc",
        "title": "Cached Video",
        "formats": [],
        "subtitles": {},
        "duration": 60,
    }
    mock_extract.return_value = raw_data

    service = MetadataService(cache_ttl=2)

    # First fetch (cache miss)
    info1 = service.get_video_info("https://youtube.com/watch?v=abc")
    assert info1.title == "Cached Video"
    assert mock_extract.call_count == 1

    # Second fetch within TTL (cache hit)
    info2 = service.get_video_info("https://youtube.com/watch?v=abc")
    assert info2.title == "Cached Video"
    assert mock_extract.call_count == 1  # count stays 1

    # Sleep to trigger TTL expiration
    time.sleep(2.5)

    # Third fetch after TTL (cache miss)
    info3 = service.get_video_info("https://youtube.com/watch?v=abc")
    assert info3.title == "Cached Video"
    assert mock_extract.call_count == 2  # extractor called again


@patch("shutil.which")
def test_file_service_ffmpeg_path_resolution(mock_which):
    file_service = FileService()

    # Case 1: PyInstaller bundler exists
    sys._MEIPASS = "C:/fake_meipass"
    try:
        # Mock os.path.exists
        with patch("os.path.exists", return_value=True):
            ffmpeg_path = file_service.get_ffmpeg_path()
            assert ffmpeg_path == os.path.join("C:/fake_meipass", "ffmpeg.exe")
    finally:
        delattr(sys, "_MEIPASS")

    # Case 2: System which resolution
    mock_which.return_value = "C:/windows/system32/ffmpeg.exe"
    ffmpeg_path_sys = file_service.get_ffmpeg_path()
    assert ffmpeg_path_sys == "C:/windows/system32/ffmpeg.exe"


@patch("subprocess.run")
def test_file_service_run_ffmpeg_command(mock_sub_run):
    file_service = FileService()
    mock_sub_run.return_value = MagicMock(stdout="FFmpeg version x.y.z", stderr="", returncode=0)

    # Mock get_ffmpeg_path to avoid dependency checks
    with patch.object(file_service, "get_ffmpeg_path", return_value="C:/ffmpeg"):
        result = file_service._run_ffmpeg_command(["ffmpeg", "-version"])
        assert result == "FFmpeg version x.y.z"
        mock_sub_run.assert_called_once()


@patch("yt_dlp.YoutubeDL")
def test_download_service_audio_options_mapping(mock_ytdl):
    mock_meta = MagicMock()
    dl_service = DownloadService(mock_meta)
    
    opts = DownloadOptions(
        output_directory="C:/Downloads",
        output_format="mp3",
        include_metadata=True,
        include_thumbnail=True,
    )

    with patch("os.path.exists", return_value=True):
        dl_service.download_audio("https://youtube.com/watch?v=abc", opts)

        # Check that YoutubeDL was instantiated with mapped parameters
        mock_ytdl.assert_called_once()
        ydl_args = mock_ytdl.call_args[0][0]
        
        assert ydl_args["ffmpeg_location"] is not None
        assert ydl_args["writethumbnail"] is True
        assert any(pp["key"] == "EmbedThumbnail" for pp in ydl_args["postprocessors"])
        assert any(pp["key"] == "FFmpegMetadata" for pp in ydl_args["postprocessors"])
        assert any(pp["key"] == "FFmpegExtractAudio" for pp in ydl_args["postprocessors"])
