import os
from typing import Dict, Any, Optional, TYPE_CHECKING

from ultratube_extractor import UltraTubeExtractor
from models import DownloadOptions
from app_messages import (
    DownloadProgress,
    DownloadFinished,
    DownloadErrorMsg,
    LogMsg,
    PlaylistProgress,
    PlaylistFinished,
)

if TYPE_CHECKING:
    from ultratube_app import UltraTubeApp


# Worker functions that run in background threads
def run_download_thread(
    extractor: UltraTubeExtractor,
    tab_id: str,
    url: str,
    is_audio: bool,
    options: DownloadOptions,
    quality: Optional[str],
    app_instance: "UltraTubeApp",
) -> None:
    def progress_callback(data):
        # Raise cancellation if tab was cancelled
        if tab_id in app_instance.cancelled_tabs:
            raise RuntimeError("Download cancelled by user")

        if data["status"] == "downloading":
            app_instance.call_from_thread(
                app_instance.post_message,
                DownloadProgress(
                    tab_id=tab_id,
                    percent=data["percent"],
                    speed=data["speed"],
                    eta=data.get("eta", 0),
                    downloaded=data["downloaded_bytes"],
                    total=data["total_bytes"],
                    filename=data.get("filename"),
                ),
            )
        elif data["status"] == "finished":
            app_instance.call_from_thread(
                app_instance.post_message,
                DownloadFinished(
                    tab_id=tab_id,
                    filepath=data["filename"],
                    size=data["total_bytes"],
                ),
            )

    def log_callback(msg):
        app_instance.call_from_thread(
            app_instance.post_message, LogMsg(tab_id=tab_id, message=msg)
        )

    try:
        if is_audio:
            media_file, subtitle_files = extractor.download_audio(
                url,
                options,
                progress_callback=progress_callback,
                log_callback=log_callback,
            )
        else:
            media_file, subtitle_files = extractor.download_video(
                url,
                quality or "highest",
                options,
                progress_callback=progress_callback,
                log_callback=log_callback,
            )

        if not media_file:
            app_instance.call_from_thread(
                app_instance.post_message,
                DownloadErrorMsg(
                    tab_id=tab_id,
                    error_msg="Download service failed to write media file.",
                ),
            )
    except Exception as e:
        app_instance.call_from_thread(
            app_instance.post_message,
            DownloadErrorMsg(tab_id=tab_id, error_msg=str(e)),
        )


def run_playlist_download_thread(
    extractor: UltraTubeExtractor,
    tab_id: str,
    url: str,
    is_audio: bool,
    options: DownloadOptions,
    quality: Optional[str],
    app_instance: "UltraTubeApp",
    playlist_info: Dict[str, Any],
) -> None:
    entries = playlist_info.get("entries") or []
    total_videos = len(entries)

    def log_callback(msg):
        app_instance.call_from_thread(
            app_instance.post_message, LogMsg(tab_id=tab_id, message=msg)
        )

    log_callback(
        f"Starting playlist download: {playlist_info.get('title', 'Playlist')} ({total_videos} items)"
    )

    downloaded_count = 0
    skipped_count = 0
    total_size = 0

    for idx, entry in enumerate(entries, 1):
        if tab_id in app_instance.cancelled_tabs:
            log_callback("Playlist download cancelled by user.")
            break

        if not entry:
            skipped_count += 1
            continue

        video_url = entry.get("url")
        video_title = entry.get("title", f"Item {idx}")

        log_callback(
            f"\n[Playlist Item {idx}/{total_videos}] Processing: {video_title}"
        )

        app_instance.call_from_thread(
            app_instance.post_message,
            PlaylistProgress(
                tab_id=tab_id,
                current_idx=idx,
                total=total_videos,
                current_title=video_title,
            ),
        )

        def item_progress_callback(data):
            if tab_id in app_instance.cancelled_tabs:
                raise RuntimeError("Download cancelled by user")

            if data["status"] == "downloading":
                app_instance.call_from_thread(
                    app_instance.post_message,
                    DownloadProgress(
                        tab_id=tab_id,
                        percent=data["percent"],
                        speed=data["speed"],
                        eta=data.get("eta", 0),
                        downloaded=data["downloaded_bytes"],
                        total=data["total_bytes"],
                        filename=data.get("filename"),
                    ),
                )

        try:
            item_options = DownloadOptions(
                output_directory=options.output_directory,
                output_format=options.output_format,
                include_metadata=options.include_metadata,
                include_thumbnail=options.include_thumbnail,
                include_chapters=options.include_chapters,
                audio_language_code=options.audio_language_code,
                subtitle_ids=options.subtitle_ids,
            )

            if is_audio:
                media_file, subtitle_files = extractor.download_audio(
                    video_url,
                    item_options,
                    progress_callback=item_progress_callback,
                    log_callback=log_callback,
                )
            else:
                media_file, subtitle_files = extractor.download_video(
                    video_url,
                    quality or "highest",
                    item_options,
                    progress_callback=item_progress_callback,
                    log_callback=log_callback,
                )

            if media_file:
                downloaded_count += 1
                log_callback(f"✓ Completed: {video_title}")
                if os.path.exists(media_file):
                    total_size += os.path.getsize(media_file)
            else:
                skipped_count += 1
                log_callback(f"✗ Failed: {video_title}")
        except Exception as e:
            skipped_count += 1
            log_callback(f"✗ Failed: {video_title} - {str(e)}")

    app_instance.call_from_thread(
        app_instance.post_message,
        PlaylistFinished(
            tab_id=tab_id,
            downloaded=downloaded_count,
            skipped=skipped_count,
            total=total_videos,
            total_size=total_size,
            directory=options.output_directory,
        ),
    )
