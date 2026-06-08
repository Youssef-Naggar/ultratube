import os
import json
from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    """Global configuration settings for UltraTube downloads."""

    out_dir: str = Field(
        default_factory=lambda: os.path.expanduser("~/Downloads")
    )
    default_mode: str = "audio"  # "audio" or "video"
    default_audio_format: str = "mp3"  # "mp3", "m4a", "wav", "flac"
    default_video_format: str = "mp4"  # "mp4", "mkv", "webm"
    default_quality: str = "highest"  # "highest", "1080p", "720p", etc.
    include_metadata: bool = True
    include_thumbnail: bool = True
    include_chapters: bool = True


SETTINGS_FILE = os.path.expanduser("~/.ultratube_settings.json")


def load_settings() -> AppSettings:
    """Load settings from ~/.ultratube_settings.json, falling back to defaults."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return AppSettings.model_validate(data)
        except Exception:
            pass
    return AppSettings()


def save_settings(settings: AppSettings) -> None:
    """Save settings to ~/.ultratube_settings.json."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            f.write(settings.model_dump_json(indent=2))
    except Exception:
        pass
