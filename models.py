from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pydantic import BaseModel


@dataclass
class VideoInfo:
    """Information about a YouTube video."""

    id: str
    title: str
    formats: List[Dict[str, Any]] = field(default_factory=list)
    subtitles: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    duration: Optional[int] = None
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None

    @property
    def filename_safe_title(self) -> str:
        """Return a filename-safe version of the title."""
        return "".join(c if c.isalnum() or c in " -_." else "_" for c in self.title)


@dataclass
class AudioTrack:
    """Information about an audio track."""

    language: str
    format_id: str
    description: str
    language_code: Optional[str] = None
    codec: Optional[str] = None
    bitrate: Optional[int] = None

    def __str__(self) -> str:
        return self.description


@dataclass
class Subtitle:
    """Information about a subtitle track."""

    language: str
    language_code: str
    format_id: str
    is_auto_generated: bool = False

    def __str__(self) -> str:
        auto_str = " (auto-generated)" if self.is_auto_generated else ""
        return f"{self.language}{auto_str}"


@dataclass
class DownloadOptions:
    """Options for downloading media."""

    output_directory: str
    output_format: str
    include_metadata: bool = True
    include_thumbnail: bool = True
    include_chapters: bool = True
    audio_language_code: Optional[str] = None
    subtitle_ids: List[str] = field(default_factory=list)


@dataclass
class ProcessOptions:
    """Options for processing media files."""

    keep_original: bool = False
    output_format: str = "mp4"
    quality_level: Optional[int] = None


class TabStatus(str, Enum):
    IDLE = "idle"
    FETCHING = "fetching"
    DOWNLOADING = "downloading"
    DONE = "done"
    ERROR = "error"


@dataclass
class DownloadRecord:
    """A record representing a download in the queue/history."""

    tab_id: str
    title: str
    status: TabStatus
    file_size: Optional[int] = None
    elapsed: Optional[float] = None
    output_path: Optional[str] = None
    eta: Optional[float] = None


class BucketDownloadSettings(BaseModel):
    """Configuration settings for a bulk download bucket."""

    urls: List[str]
    is_audio: bool
    format: str
    quality: str
    out_dir: str
