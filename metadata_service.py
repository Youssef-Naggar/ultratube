import time
from typing import List, Dict, Optional, Any, cast

import yt_dlp
from yt_dlp.utils import DownloadError

from models import VideoInfo, AudioTrack, Subtitle


def get_clean_language_name(lang_code: Optional[str], format_note: str) -> str:
    # A mapping of common ISO 639-1 language codes to English names
    LANG_MAP = {
        "en": "English",
        "ar": "Arabic",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
        "pt": "Portuguese",
        "ru": "Russian",
        "hi": "Hindi",
        "tr": "Turkish",
        "vi": "Vietnamese",
        "pl": "Polish",
        "nl": "Dutch",
        "th": "Thai",
        "id": "Indonesian",
        "sv": "Swedish",
        "no": "Norwegian",
        "fi": "Finnish",
        "da": "Danish",
    }

    clean_code = lang_code.lower().split("-")[0] if lang_code else None
    mapped_name = LANG_MAP.get(clean_code) if clean_code else None

    # Clean up the format note
    clean_note = ""
    if format_note:
        # Split by comma and take the first part
        parts = [p.strip() for p in format_note.split(",")]
        if parts:
            clean_note = parts[0]

    # Check if the clean_note is just a quality descriptor
    quality_descriptors = {
        "low",
        "medium",
        "high",
        "ultralow",
        "ultra low",
        "standard",
        "original",
        "rtmp",
    }
    is_just_quality = clean_note.lower() in quality_descriptors or clean_note.isdigit()

    if mapped_name:
        if clean_note and not is_just_quality:
            # If the clean_note contains the language or describes it, use it
            # e.g., "English original (default)" or "Arabic (translated)"
            return clean_note
        else:
            # e.g. if note is "medium", but language is "en" -> "English"
            desc = mapped_name
            if "original" in format_note.lower():
                desc += " (original)"
            elif "translated" in format_note.lower():
                desc += " (translated)"
            elif "dubbed" in format_note.lower():
                desc += " (dubbed)"
            return desc

    # If no mapped language code but we have a clean note that isn't just a quality
    if clean_note and not is_just_quality:
        return clean_note

    if clean_code and clean_code != "und":
        return clean_code.upper()

    return "Default"


class MetadataService:
    """Service for extracting and caching metadata from YouTube videos."""

    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize the metadata service.

        Args:
            cache_ttl: Time-to-live for cached metadata in seconds (default: 1 hour)
        """
        self._video_info_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_ttl = cache_ttl
        self.supported_audio_formats = ["mp3", "m4a", "wav", "flac"]
        self.supported_video_formats = ["mp4", "mkv", "webm"]

    def get_available_formats(self, url: str, is_audio: bool) -> List[str]:
        """
        Gets a list of available formats for a given URL that are supported by the application.

        For audio, this returns all supported audio formats as FFmpeg handles conversion.
        For video, this checks the available container formats from yt-dlp against
        the app's supported list.

        Args:
            url: The YouTube URL.
            is_audio: True if checking for audio formats, False for video formats.

        Returns:
            A list of available format strings (e.g., ['mp4', 'mkv']).
        """
        if is_audio:
            # For audio, we rely on FFmpeg for conversion, so all our supported formats are "available".
            return self.supported_audio_formats

        # For video, check what container formats are directly available from the source
        info = self.get_video_info(url)
        available_extensions = set()
        for f in info.formats:
            # Consider formats that have a video codec
            if f.get("vcodec") != "none":
                ext = f.get("ext")
                if isinstance(ext, str) and ext in self.supported_video_formats:
                    available_extensions.add(ext)

        # Return a sorted list for consistent UI display
        return sorted(list(available_extensions))

    def get_video_info(self, url: str) -> VideoInfo:
        """
        Get video information for a YouTube URL.

        Args:
            url: YouTube URL

        Returns:
            VideoInfo object with video metadata
        """
        # Check cache first
        current_time = time.time()
        if url in self._video_info_cache:
            cache_time = self._cache_timestamps.get(url, 0)
            if current_time - cache_time < self._cache_ttl:
                info = self._video_info_cache[url]
                return self._create_video_info(info)

        # Cache miss or expired, extract info
        info = self._extract_video_info(url)

        # Update cache
        self._video_info_cache[url] = info
        self._cache_timestamps[url] = current_time

        return self._create_video_info(info)

    def get_playlist_info(self, url: str) -> Dict[str, Any]:
        """
        Extracts information about a playlist, including a list of its video entries.

        Args:
            url: YouTube playlist URL

        Returns:
            Raw playlist information dictionary.

        Raises:
            ValueError: If the URL is not a valid playlist or if extraction fails.
        """
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "dump_single_json": True,
            "extract_flat": True,
        }

        try:
            with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info or info.get("_type") != "playlist":
                    raise ValueError("The provided URL is not a valid playlist.")
                return dict(info)
        except DownloadError as e:
            raise ValueError(f"Failed to extract playlist information: {str(e)}")

    def get_audio_tracks(self, url: str) -> List[AudioTrack]:
        """
        Get available audio tracks for a YouTube video.

        Args:
            url: YouTube URL

        Returns:
            List of AudioTrack objects
        """
        info = self.get_video_info(url)
        unique_tracks: Dict[str, AudioTrack] = {}

        for format in info.formats:
            # Filter for audio-only formats
            if (
                format.get("vcodec") == "none"
                and format.get("acodec") != "none"
                or format.get("resolution") == "audio only"
            ):
                format_id = format.get("format_id") or ""
                lang_code = format.get("language") or ""
                format_note = format.get("format_note", "") or ""

                language_name = get_clean_language_name(lang_code, format_note)

                # Use language_code or language_name as the unique key
                key = (
                    lang_code
                    if (lang_code and lang_code != "und")
                    else language_name.lower()
                )

                # Get audio format details
                abr = format.get("abr") or 0

                # Create description
                description = language_name

                track = AudioTrack(
                    language=language_name,
                    format_id=format_id,
                    description=description,
                    language_code=lang_code,
                    codec=format.get("acodec"),
                    bitrate=format.get("abr"),
                )

                if key not in unique_tracks:
                    unique_tracks[key] = track
                else:
                    # Keep the one with higher bitrate or preferred codec
                    existing_track = unique_tracks[key]
                    existing_abr = existing_track.bitrate or 0
                    if abr > existing_abr:
                        unique_tracks[key] = track

        return list(unique_tracks.values())

    def get_available_subtitles(self, url: str) -> Dict[str, List[Subtitle]]:
        """
        Get available subtitles for a YouTube video.

        Args:
            url: YouTube URL

        Returns:
            Dictionary of language codes to lists of Subtitle objects
        """
        info = self.get_video_info(url)
        subtitles: Dict[str, List[Subtitle]] = {}

        for lang_code, sub_list in info.subtitles.items():
            if not sub_list:
                continue

            subtitles[lang_code] = []
            for sub in sub_list:
                # Create subtitle object
                subtitle = Subtitle(
                    language=sub.get("name", lang_code),
                    language_code=lang_code,
                    format_id=sub.get("format_id", ""),
                    is_auto_generated="auto" in sub.get("name", "").lower(),
                )
                subtitles[lang_code].append(subtitle)

        return subtitles

    def _extract_video_info(self, url: str) -> Dict[str, Any]:
        """
        Extract information from a YouTube URL using yt-dlp.

        Args:
            url: YouTube URL

        Returns:
            Raw video information dictionary
        """
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "no_format_sort": True,
            "dump_single_json": True,
            "extractor_args": {"youtube": {"player_client": ["all"]}},
            "js_runtimes": {"node": {}},
            "remote_components": ["ejs:github"],
        }

        try:
            with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
                res = ydl.extract_info(url, download=False)
                return dict(res) if res else {}
        except DownloadError as e:
            raise ValueError(f"Failed to extract video information: {str(e)}")

    def _create_video_info(self, raw_info: Dict[str, Any]) -> VideoInfo:
        """
        Create a VideoInfo object from raw yt-dlp data.

        Args:
            raw_info: Raw video information from yt-dlp

        Returns:
            VideoInfo object
        """
        return VideoInfo(
            id=raw_info.get("id", ""),
            title=raw_info.get("title", "Untitled"),
            formats=raw_info.get("formats", []),
            subtitles=raw_info.get("subtitles", {}),
            duration=raw_info.get("duration"),
            thumbnail_url=raw_info.get("thumbnail"),
            description=raw_info.get("description"),
        )
