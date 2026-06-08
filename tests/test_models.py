import pytest
from pydantic import ValidationError
from models import (
    VideoInfo,
    AudioTrack,
    Subtitle,
    DownloadOptions,
    ProcessOptions,
    TabStatus,
    DownloadRecord,
    BucketDownloadSettings,
)
from settings_service import AppSettings


def test_video_info_filename_safe_title():
    # Test safe titles
    video = VideoInfo(id="123", title="Safe Title 101")
    assert video.filename_safe_title == "Safe Title 101"

    # Test unsafe characters sanitization
    video_unsafe = VideoInfo(id="456", title="Title/With\\Unsafe*Chars?|<Hello>")
    assert video_unsafe.filename_safe_title == "Title_With_Unsafe_Chars___Hello_"


def test_audio_track_representation():
    track = AudioTrack(
        language="English",
        format_id="140",
        description="English audio (128kbps)",
        language_code="en",
        codec="mp4a.40.2",
        bitrate=128,
    )
    assert str(track) == "English audio (128kbps)"


def test_subtitle_representation():
    sub_normal = Subtitle(
        language="Spanish", language_code="es", format_id="vtt", is_auto_generated=False
    )
    assert str(sub_normal) == "Spanish"

    sub_auto = Subtitle(
        language="Arabic", language_code="ar", format_id="vtt", is_auto_generated=True
    )
    assert str(sub_auto) == "Arabic (auto-generated)"


def test_download_options_defaults():
    opts = DownloadOptions(output_directory="C:/Downloads", output_format="mp4")
    assert opts.output_directory == "C:/Downloads"
    assert opts.output_format == "mp4"
    assert opts.include_metadata is True
    assert opts.include_thumbnail is True
    assert opts.include_chapters is True
    assert opts.audio_language_code is None
    assert opts.subtitle_ids == []


def test_process_options_defaults():
    opts = ProcessOptions()
    assert opts.keep_original is False
    assert opts.output_format == "mp4"
    assert opts.quality_level is None


def test_download_record_creation():
    record = DownloadRecord(
        tab_id="tab-1",
        title="Testing Download",
        status=TabStatus.DOWNLOADING,
        file_size=1024000,
        elapsed=12.5,
        output_path="C:/Downloads/test.mp4",
        eta=5.0,
    )
    assert record.tab_id == "tab-1"
    assert record.title == "Testing Download"
    assert record.status == TabStatus.DOWNLOADING
    assert record.file_size == 1024000
    assert record.elapsed == 12.5
    assert record.output_path == "C:/Downloads/test.mp4"
    assert record.eta == 5.0


def test_bucket_download_settings_validation():
    # Valid model validation
    settings = BucketDownloadSettings(
        urls=["https://www.youtube.com/watch?v=123"],
        is_audio=False,
        format="mp4",
        quality="1080p",
        out_dir="C:/downloads",
    )
    assert settings.urls == ["https://www.youtube.com/watch?v=123"]
    assert settings.is_audio is False

    # Invalid type for urls
    with pytest.raises(ValidationError):
        BucketDownloadSettings(
            urls="not-a-list",
            is_audio=False,
            format="mp4",
            quality="1080p",
            out_dir="C:/downloads",
        )


def test_app_settings_validation_and_toggles():
    settings = AppSettings(
        out_dir="C:/custom",
        default_mode="video",
        default_audio_format="m4a",
        default_video_format="mkv",
        default_quality="720p",
        include_metadata=False,
        include_thumbnail=False,
        include_chapters=False,
    )
    assert settings.out_dir == "C:/custom"
    assert settings.default_mode == "video"
    assert settings.default_audio_format == "m4a"
    assert settings.default_video_format == "mkv"
    assert settings.default_quality == "720p"
    assert settings.include_metadata is False
    assert settings.include_thumbnail is False
    assert settings.include_chapters is False
