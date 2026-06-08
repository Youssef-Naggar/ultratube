"""
YouTubeExtractor: Main facade that coordinates the services for YouTube downloading.
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple

from metadata_service import MetadataService
from download_service import DownloadService, DownloadOptions
from file_service import FileService
from models import AudioTrack, Subtitle


class UltraTubeExtractor:
    """Main facade for the YouTube downloader."""

    def __init__(self):
        """Initialize the YouTube extractor with its required services."""
        self.metadata_service = MetadataService()
        self.download_service = DownloadService(self.metadata_service)
        self.file_service = FileService()

    def is_valid_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if the URL is syntactically correct and can be parsed by yt-dlp.

        Args:
            url: The URL to validate.

        Returns:
            A tuple of (is_valid, error_message).
        """
        if not url:
            return False, "URL cannot be empty."

        # Layer 1: Syntactic check (simple HTTP/HTTPS URL pattern)
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if not url_pattern.match(url):
            return (
                False,
                "Invalid URL format. Please enter a valid HTTP/HTTPS web address.",
            )

        # Layer 2: Semantic check (attempting to fetch metadata via yt-dlp)
        try:
            self.metadata_service.get_video_info(url)
            return True, None
        except ValueError as e:
            err_msg = str(e)
            if "Unsupported URL" in err_msg:
                return (
                    False,
                    "Unsupported platform or website. yt-dlp does not support this link.",
                )
            return (
                False,
                "Could not access media. The link may be private, deleted, or offline.",
            )
        except Exception as e:
            return False, f"Network or extraction error: {str(e)}"

    def get_available_formats(self, url: str, is_audio: bool) -> List[str]:
        """
        Gets available formats for a video that are supported by the app.

        Args:
            url: The YouTube URL.
            is_audio: True for audio formats, False for video formats.

        Returns:
            A list of supported, available format strings.
        """
        return self.metadata_service.get_available_formats(url, is_audio)

    def get_audio_tracks(self, url: str) -> List[AudioTrack]:
        """
        Get available audio tracks for a YouTube video.

        Args:
            url: The YouTube URL

        Returns:
            A list of AudioTrack objects
        """
        return self.metadata_service.get_audio_tracks(url)

    def get_available_subtitles(self, url: str) -> Dict[str, List[Subtitle]]:
        """
        Get available subtitles for a YouTube video.

        Args:
            url: The YouTube URL

        Returns:
            A dictionary of subtitle language codes to Subtitle objects
        """
        return self.metadata_service.get_available_subtitles(url)

    def get_playlist_info(self, url: str) -> Dict[str, Any]:
        """
        Get information about a playlist, including all its video entries.

        Args:
            url: The YouTube playlist URL.

        Returns:
            A dictionary with playlist metadata.
        """
        return self.metadata_service.get_playlist_info(url)

    def download_audio(
        self,
        url: str,
        options: DownloadOptions,
        progress_callback=None,
        log_callback=None,
    ) -> Tuple[Optional[str], List[str]]:
        """
        Download audio from a URL based on the provided options.

        Args:
            url: URL to download from
            options: A DownloadOptions object with all required parameters.
            progress_callback: Optional progress update callback.
            log_callback: Optional log callback.

        Returns:
            Tuple containing (path to downloaded audio file, list of subtitle file paths)
        """
        return self.download_service.download_audio(
            url, options, progress_callback, log_callback
        )

    def download_video(
        self,
        url: str,
        quality: str,
        options: DownloadOptions,
        progress_callback=None,
        log_callback=None,
    ) -> Tuple[Optional[str], List[str]]:
        """
        Download video from a URL based on the provided options.

        Args:
            url: URL to download from
            quality: Desired video quality (e.g. 'highest', '1080p')
            options: A DownloadOptions object with all required parameters.
            progress_callback: Optional progress update callback.
            log_callback: Optional log callback.

        Returns:
            Tuple containing (path to downloaded video file, list of subtitle file paths)
        """
        return self.download_service.download_video(
            url, quality, options, progress_callback, log_callback
        )

    def merge_subtitles(
        self,
        media_file: str,
        subtitle_files: List[str],
        output_file: Optional[str] = None,
    ) -> str:
        """
        Merge subtitles into a media file.

        Args:
            media_file: Path to the media file
            subtitle_files: List of subtitle file paths
            output_file: Path to save the merged file (optional)

        Returns:
            Path to the merged file
        """
        if not output_file:
            # Generate output file name dynamically based on original extension
            base_name, ext = os.path.splitext(os.path.basename(media_file))
            directory = os.path.dirname(media_file)
            output_file = os.path.join(directory, f"{base_name}_with_subs{ext}")

        return self.file_service.merge_subtitles(
            media_file, subtitle_files, output_file
        )
