import os
from typing import List, Optional, Any, Tuple, cast

import yt_dlp
from yt_dlp.utils import DownloadError

from metadata_service import MetadataService
from models import DownloadOptions


class YtDlpLogger:
    """Redirects yt-dlp logs to our TUI logs."""

    def __init__(self, log_callback=None):
        self.log_callback = log_callback

    def debug(self, message: str) -> None:
        # Suppress progress-like download lines from the log tab
        if self.log_callback and not message.startswith("[download]"):
            self.log_callback(f"[Debug] {message.strip()}")

    def info(self, message: str) -> None:
        if self.log_callback:
            self.log_callback(f"[Info] {message.strip()}")

    def warning(self, message: str) -> None:
        if self.log_callback:
            self.log_callback(f"[Warning] {message.strip()}")

    def error(self, message: str) -> None:
        if self.log_callback:
            self.log_callback(f"[Error] {message.strip()}")


def make_progress_hook(progress_callback):
    """Creates a hook for yt-dlp to report progress back to a callback."""

    def hook(d):
        if not progress_callback:
            return

        status = d.get("status")
        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            percent = (downloaded / total * 100) if total > 0 else 0.0
            speed = d.get("speed") or 0.0
            eta = d.get("eta") or 0
            filename = d.get("filename", "")

            progress_callback(
                {
                    "status": "downloading",
                    "percent": percent,
                    "downloaded_bytes": downloaded,
                    "total_bytes": total,
                    "speed": speed,
                    "eta": eta,
                    "filename": filename,
                }
            )
        elif status == "finished":
            total = d.get("total_bytes") or d.get("downloaded_bytes", 0)
            filename = d.get("filename", "")
            progress_callback(
                {"status": "finished", "total_bytes": total, "filename": filename}
            )
        elif status == "error":
            progress_callback(
                {"status": "error", "error": d.get("error", "Unknown error")}
            )

    return hook


class DownloadService:
    """Service for downloading media from YouTube and other platforms."""

    def __init__(self, metadata_service: MetadataService):
        """
        Initialize the download service.

        Args:
            metadata_service: Service for retrieving video metadata
        """
        self.metadata_service = metadata_service

    def download_audio(
        self,
        url: str,
        options: DownloadOptions,
        progress_callback=None,
        log_callback=None,
    ) -> Tuple[Optional[str], List[str]]:
        """
        Download audio from a URL.

        Args:
            url: URL to download from
            options: Download options
            progress_callback: Callback for progress updates
            log_callback: Callback for logger outputs

        Returns:
            Tuple containing (path to downloaded audio file, list of subtitle file paths)
        """
        # Ensure the output directory exists
        os.makedirs(options.output_directory, exist_ok=True)

        # Resolve ffmpeg location
        from file_service import FileService

        ffmpeg_path = FileService().get_ffmpeg_path()

        # Configure format selector to respect selected language track
        format_selector = "bestaudio/best"
        if options.audio_language_code:
            format_selector = (
                f"bestaudio[language={options.audio_language_code}]/bestaudio/best"
            )

        # Configure yt-dlp options
        ydl_opts = {
            "format": format_selector,
            "outtmpl": os.path.join(
                options.output_directory, f"%(title).150s.{options.output_format}"
            ),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": options.output_format,
                    "preferredquality": "192",
                },
            ],
            "ffmpeg_location": ffmpeg_path,
            "quiet": True,
            "noprogress": True,
            "logger": YtDlpLogger(log_callback),
            "progress_hooks": [make_progress_hook(progress_callback)],
            "ignoreerrors": False,
            "extractor_args": {"youtube": {"player_client": ["all"]}},
            "js_runtimes": {"node": {}},
            "remote_components": ["ejs:github"],
        }

        # Add optional postprocessors
        if options.include_thumbnail:
            ydl_opts["writethumbnail"] = True
            ydl_opts["postprocessors"].append({"key": "EmbedThumbnail"})

        if options.include_metadata:
            ydl_opts["postprocessors"].append({"key": "FFmpegMetadata"})

        if log_callback:
            log_callback("Starting audio download...")

        audio_file_path: Optional[str] = None

        try:
            with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    # Try resolving actual file path
                    if info.get("requested_downloads"):
                        raw_path = info["requested_downloads"][0].get("filepath")
                        audio_file_path = cast(Optional[str], raw_path)
                    else:
                        raw_path = info.get("_filename")
                        audio_file_path = cast(Optional[str], raw_path)

                    # Fallback to manual path generation if needed
                    if not isinstance(audio_file_path, str) or not os.path.exists(
                        audio_file_path
                    ):
                        title = (info.get("title") or "audio") if info else "audio"
                        safe_title = "".join(
                            c if c.isalnum() or c in " -_." else "_" for c in title
                        )
                        safe_title = safe_title[:150]
                        audio_file_path = os.path.join(
                            options.output_directory,
                            f"{safe_title}.{options.output_format}",
                        )

            if log_callback:
                log_callback("Audio download complete!")
        except DownloadError as e:
            if log_callback:
                log_callback(f"Error downloading audio: {str(e)}")
            return None, []

        # Download subtitles if requested
        subtitle_files = []
        if options.subtitle_ids:
            if log_callback:
                log_callback("Downloading subtitles...")
            subtitle_files = self.download_subtitles(
                url, options.subtitle_ids, options.output_directory, log_callback
            )

        return audio_file_path, subtitle_files

    def download_video(
        self,
        url: str,
        quality: str,
        options: DownloadOptions,
        progress_callback=None,
        log_callback=None,
    ) -> Tuple[Optional[str], List[str]]:
        """
        Download video from a URL.

        Args:
            url: URL to download from
            quality: Desired video quality
            options: Download options
            progress_callback: Callback for progress updates
            log_callback: Callback for logger outputs

        Returns:
            Tuple containing (path to downloaded video file, list of subtitle file paths)
        """
        # Ensure the output directory exists
        os.makedirs(options.output_directory, exist_ok=True)

        # Resolve ffmpeg location
        from file_service import FileService

        ffmpeg_path = FileService().get_ffmpeg_path()

        # Map quality to format selector
        format_map = {
            "highest": "bestvideo[ext=mp4]",
            "1080p": "bestvideo[height<=1080][ext=mp4]",
            "720p": "bestvideo[height<=720][ext=mp4]",
            "480p": "bestvideo[height<=480][ext=mp4]",
            "360p": "bestvideo[height<=360][ext=mp4]",
            "240p": "bestvideo[height<=240][ext=mp4]",
        }
        format_selector = format_map.get(quality, "bestvideo[ext=mp4]")

        # Use flexible language selection
        if options.audio_language_code:
            format_selector += f"+bestaudio[language={options.audio_language_code}]"
        else:
            format_selector += "+bestaudio[ext=m4a]"

        # Add fallback option
        height = (
            quality[:-1] if quality.endswith("p") and quality[:-1].isdigit() else "1080"
        )
        format_selector += f"/best[height<={height}][ext=mp4]/best"

        # Configure yt-dlp options
        ydl_opts = {
            "format": format_selector,
            "outtmpl": os.path.join(options.output_directory, "%(title).150s.%(ext)s"),
            "merge_output_format": options.output_format,
            "postprocessors": [],
            "ffmpeg_location": ffmpeg_path,
            "quiet": True,
            "noprogress": True,
            "logger": YtDlpLogger(log_callback),
            "progress_hooks": [make_progress_hook(progress_callback)],
            "ignoreerrors": False,
            "extractor_args": {"youtube": {"player_client": ["all"]}},
            "js_runtimes": {"node": {}},
            "remote_components": ["ejs:github"],
        }

        # Add optional features
        if options.include_thumbnail:
            ydl_opts["writethumbnail"] = True
            ydl_opts["postprocessors"].append({"key": "EmbedThumbnail"})

        if options.include_metadata:
            ydl_opts["postprocessors"].append({"key": "FFmpegMetadata"})

        if options.include_chapters:
            ydl_opts["embedchapters"] = True

        if log_callback:
            log_callback(f"Starting {quality} video download...")
        video_file_path: Optional[str] = None

        try:
            with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    # Try resolving actual file path
                    if info.get("requested_downloads"):
                        raw_path = info["requested_downloads"][0].get("filepath")
                        video_file_path = cast(Optional[str], raw_path)
                    else:
                        raw_path = info.get("_filename")
                        video_file_path = cast(Optional[str], raw_path)

                    # Fallback to manual path generation if needed
                    if not isinstance(video_file_path, str) or not os.path.exists(
                        video_file_path
                    ):
                        title = (info.get("title") or "video") if info else "video"
                        safe_title = "".join(
                            c if c.isalnum() or c in " -_." else "_" for c in title
                        )
                        safe_title = safe_title[:150]
                        video_file_path = os.path.join(
                            options.output_directory,
                            f"{safe_title}.{options.output_format}",
                        )

            if log_callback:
                log_callback("Video download complete!")
        except DownloadError as e:
            if log_callback:
                log_callback(f"Error downloading video: {str(e)}")
            return None, []

        # Download subtitles if requested
        subtitle_files = []
        if options.subtitle_ids:
            if log_callback:
                log_callback("Downloading subtitles...")
            subtitle_files = self.download_subtitles(
                url, options.subtitle_ids, options.output_directory, log_callback
            )

        return video_file_path, subtitle_files

    def download_subtitles(
        self, url: str, subtitle_ids: List[str], output_dir: str, log_callback=None
    ) -> List[str]:
        """
        Download subtitles as .vtt files for a given URL.

        Args:
            url: URL to download from
            subtitle_ids: List of subtitle language codes to download
            output_dir: Directory to save the downloaded subtitles
            log_callback: Callback for logger outputs

        Returns:
            List of paths to downloaded subtitle files
        """
        if not subtitle_ids:
            return []

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Configure yt-dlp options
        ydl_opts = {
            "writesubtitles": True,
            "subtitleslangs": subtitle_ids,
            "subtitlesformat": "vtt",
            "skip_download": True,
            "quiet": True,
            "logger": YtDlpLogger(log_callback),
            "outtmpl": os.path.join(output_dir, "%(title).150s"),
        }

        subtitle_files = []

        try:
            with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = (info.get("title") or "video") if info else "video"
                # Normalize the title to a safe filename
                safe_title = "".join(
                    c if c.isalnum() or c in " -_." else "_" for c in video_title
                )
                safe_title = safe_title[:150]
                base_path = os.path.join(output_dir, safe_title)

                # Construct the expected subtitle file paths
                for lang in subtitle_ids:
                    sub_path = f"{base_path}.{lang}.vtt"
                    if os.path.exists(sub_path):
                        subtitle_files.append(sub_path)
                        if log_callback:
                            log_callback(f"Downloaded subtitle: {sub_path}")

        except Exception as e:
            if log_callback:
                log_callback(f"Error downloading subtitles: {str(e)}")

        return subtitle_files
