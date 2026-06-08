import os
from typing import List, Dict, Optional, Tuple, Any

from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import (
    Header,
    Footer,
    Button,
    Label,
    Select,
    SelectionList,
    Switch,
    ProgressBar,
    DataTable,
    Input,
)

from ultratube_extractor import UltraTubeExtractor
from models import DownloadOptions, TabStatus, DownloadRecord, BucketDownloadSettings
import messages

# Import modular components
from app_utils import copy_to_clipboard, format_size, format_speed, format_time
from app_messages import (
    DownloadProgress,
    DownloadFinished,
    DownloadErrorMsg,
    LogMsg,
    PlaylistProgress,
    PlaylistFinished,
)
from app_workers import run_download_thread, run_playlist_download_thread
from app_screens import HelpScreen, QuestionModal, BucketScreen
from download_tab import DownloadTab
from queue_panel import DownloadQueuePanel
from bucket_tab import BucketQueueTab
from settings_service import load_settings
from settings_screen import SettingsScreen


# Main App class
class UltraTubeApp(App):
    CSS_PATH = "ultratube.tcss"
    BINDINGS = [
        ("ctrl+t", "new_tab", "New Tab"),
        ("ctrl+w", "close_tab", "Close Tab"),
        ("ctrl+b", "bucket", "Bucket"),
        ("ctrl+s", "settings", "Settings"),
        ("f1", "toggle_help", "Help"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.extractor = UltraTubeExtractor()
        self.tab_counter = 0
        self.download_records: Dict[str, DownloadRecord] = {}
        self.cancelled_tabs = set()
        self.settings = load_settings()

        # Keep track of active subtitles that need post-download merge
        # tab_id -> (media_filepath, subtitle_filepaths)
        self.pending_merges: Dict[str, Tuple[str, List[str]]] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="app-container"):
            with Container(id="main-content"):
                from textual.widgets import TabbedContent

                yield TabbedContent(id="tabs-view")
                with Container(id="empty-state-container"):
                    yield Label(messages.EMPTY_STATE_MESSAGE, id="empty-state-text")
            with Container(id="sidebar"):
                yield DownloadQueuePanel()
        yield Footer()

    def on_mount(self) -> None:
        self.title = messages.APP_TITLE
        self.sub_title = messages.APP_SUBTITLE
        self.action_new_tab()

    def set_tab_label(self, pane_id: str, label: str) -> None:
        """Helper to set the label of a tab dynamically and thread-safely."""

        def _update():
            try:
                from textual.widgets import TabbedContent

                tabs_view = self.query_one("#tabs-view", TabbedContent)
                tab = tabs_view.get_tab(pane_id)
                tab.label = label
            except Exception:
                pass

        import threading

        if getattr(self, "_thread_id", None) == threading.get_ident():
            _update()
        else:
            try:
                self.call_from_thread(_update)
            except RuntimeError:
                _update()

    def action_toggle_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_settings(self) -> None:
        self.push_screen(SettingsScreen(self.settings))


    def action_new_tab(self) -> None:
        self.tab_counter += 1
        tab_id = str(self.tab_counter)

        from textual.widgets import TabbedContent, TabPane

        tabs_view = self.query_one("#tabs-view", TabbedContent)
        empty_state = self.query_one("#empty-state-container")
        empty_state.add_class("hidden")

        tab_widget = DownloadTab(tab_id, self.extractor, settings=self.settings)
        tabs_view.add_pane(
            TabPane(f"New Tab #{tab_id}", tab_widget, id=f"pane-{tab_id}")
        )
        tabs_view.active = f"pane-{tab_id}"

    def action_close_tab(self) -> None:
        from textual.widgets import TabbedContent

        tabs_view = self.query_one("#tabs-view", TabbedContent)
        active_pane_id = tabs_view.active
        if not active_pane_id:
            return

        tab_id = active_pane_id.replace("pane-", "")

        # If download is running, cancel it
        if tab_id in self.download_records:
            record = self.download_records[tab_id]
            if record.status in (TabStatus.DOWNLOADING, TabStatus.FETCHING):
                self.cancelled_tabs.add(tab_id)
                record.status = TabStatus.ERROR
                self.update_sidebar_queue(tab_id)

        tabs_view.remove_pane(active_pane_id)

        # Show empty state if no tabs remain
        if not tabs_view.tab_count:
            empty_state = self.query_one("#empty-state-container")
            empty_state.remove_class("hidden")

    def action_bucket(self) -> None:
        def handle_bucket_result(result: Optional[BucketDownloadSettings]) -> None:
            if not result:
                return

            from textual.widgets import TabbedContent
            tabs_view = self.query_one("#tabs-view", TabbedContent)

            first_tab_id = str(self.tab_counter + 1)
            for url in result.urls:
                self.add_bucket_download(
                    url=url,
                    is_audio=result.is_audio,
                    format_val=result.format,
                    quality_val=result.quality,
                    out_dir=result.out_dir,
                )

            if result.urls and first_tab_id:
                tabs_view.active = f"pane-{first_tab_id}"

            self.notify(f"Queued {len(result.urls)} downloads")

        self.push_screen(BucketScreen(app_settings=self.settings), handle_bucket_result)

    def add_bucket_batch_downloads(self, settings: BucketDownloadSettings) -> None:
        self.tab_counter += 1
        batch_id = f"bucket-{self.tab_counter}"

        from textual.widgets import TabbedContent, TabPane

        tabs_view = self.query_one("#tabs-view", TabbedContent)
        empty_state = self.query_one("#empty-state-container")
        empty_state.add_class("hidden")

        # Create the unified tab
        tab = BucketQueueTab(
            tab_id=batch_id,
            urls=settings.urls,
            is_audio=settings.is_audio,
            format_val=settings.format,
            quality_val=settings.quality,
            out_dir=settings.out_dir,
        )

        tabs_view.add_pane(
            TabPane(f"Bucket Queue #{self.tab_counter}", tab, id=f"pane-{batch_id}")
        )
        tabs_view.active = f"pane-{batch_id}"

        # Queue all URLs
        for idx, url in enumerate(settings.urls, 1):
            sub_id = f"{batch_id}-{idx}"
            tab.sub_id_to_url[sub_id] = url

            # Create sub record
            title = f"Item #{idx}"
            sub_record = DownloadRecord(
                tab_id=sub_id,
                title=title,
                status=TabStatus.DOWNLOADING,
            )
            tab.downloads[sub_id] = sub_record
            self.download_records[sub_id] = sub_record

            options = DownloadOptions(
                output_directory=settings.out_dir,
                output_format=settings.format,
                include_metadata=True,
                include_thumbnail=True,
                include_chapters=False,
                audio_language_code=None,
                subtitle_ids=[],
            )

            # Spawning download threads for each URL
            self.run_worker(
                lambda s_id=sub_id, u=url, o=options: run_download_thread(
                    self.extractor,
                    s_id,
                    u,
                    settings.is_audio,
                    o,
                    settings.quality,
                    self,
                ),
                thread=True,
                name=f"dl-worker-{sub_id}",
            )

        self.notify(f"Queued {len(settings.urls)} downloads in Bucket Queue #{self.tab_counter}")

    def add_bucket_download(
        self,
        url: str,
        is_audio: bool,
        format_val: str,
        quality_val: str,
        out_dir: str,
    ) -> None:
        self.tab_counter += 1
        tab_id = str(self.tab_counter)

        from textual.widgets import TabbedContent, TabPane

        tabs_view = self.query_one("#tabs-view", TabbedContent)
        empty_state = self.query_one("#empty-state-container")
        empty_state.add_class("hidden")

        # Create DownloadTab with pre-filled settings
        tab = DownloadTab(tab_id, self.extractor, url=url, bucket_settings={
            "is_audio": is_audio,
            "format": format_val,
            "quality": quality_val,
            "out_dir": out_dir,
        }, settings=self.settings)

        # Set unique initial name for the tab
        url_label = url
        if "youtube.com" in url or "youtu.be" in url:
            import re
            yt_match = re.search(
                r"(?:v=|\/v\/|embed\/|youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})",
                url,
            )
            if yt_match:
                url_label = f"YT: {yt_match.group(1)}"
        if len(url_label) > 15:
            url_label = f"{url_label[:12]}..."

        tabs_view.add_pane(
            TabPane(url_label, tab, id=f"pane-{tab_id}")
        )

    # Action validate button
    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if not btn_id:
            return

        if btn_id.startswith("val-btn-"):
            tab_id = btn_id.replace("val-btn-", "")
            self.validate_url_action(tab_id)
        elif btn_id.startswith("dl-btn-"):
            tab_id = btn_id.replace("dl-btn-", "")
            self.start_download_action(tab_id)
        elif btn_id.startswith("star-btn-"):
            tab_id = btn_id.replace("star-btn-", "")
            self.handle_star_click(tab_id)
        elif btn_id.startswith("star-skip-btn-"):
            tab_id = btn_id.replace("star-skip-btn-", "")
            self.handle_star_skip(tab_id)

    # Input enter validation
    def on_input_submitted(self, event: Input.Submitted) -> None:
        input_id = event.input.id
        if input_id and input_id.startswith("url-input-"):
            tab_id = input_id.replace("url-input-", "")
            self.validate_url_action(tab_id)

    def validate_url_action(self, tab_id: str) -> None:
        tab = self.query_one(f"#tab-{tab_id}", DownloadTab)
        from textual.widgets import Input

        url_input = self.query_one(f"#url-input-{tab_id}", Input)
        url = url_input.value.strip()

        if not url:
            tab.update_status("URL cannot be empty.", "status-error")
            return

        tab.status = TabStatus.FETCHING
        tab.update_status(messages.VALIDATING_SPINNER, "status-pending")

        self.set_tab_label(f"pane-{tab_id}", "Checking...")

        # Run validation in worker thread
        self.run_worker(
            lambda: self.do_validate_url(tab_id, url),
            thread=True,
            name=f"val-worker-{tab_id}",
        )

    # Worker task for URL extraction
    def do_validate_url(self, tab_id: str, url: str) -> None:
        try:
            # Check syntax and semantics
            is_valid, err_msg = self.extractor.is_valid_url(url)
            if not is_valid:
                self.call_from_thread(
                    self.handle_validation_result, tab_id, False, err_msg, None
                )
                return

            # Retrieve details
            is_playlist = "list=" in url or "/playlist" in url
            if is_playlist:
                playlist_info = self.extractor.get_playlist_info(url)
                self.call_from_thread(
                    self.handle_validation_result,
                    tab_id,
                    True,
                    None,
                    {"type": "playlist", "info": playlist_info},
                )
            else:
                video_info = self.extractor.metadata_service.get_video_info(url)
                # Fetch available configurations
                formats = self.extractor.get_available_formats(url, is_audio=False)
                tracks = self.extractor.get_audio_tracks(url)
                subs_map = self.extractor.get_available_subtitles(url)

                # Flatten subtitles map to list of subtitles
                sub_list = []
                for lang_code, list_subs in subs_map.items():
                    if list_subs:
                        sub_list.append(list_subs[0])

                self.call_from_thread(
                    self.handle_validation_result,
                    tab_id,
                    True,
                    None,
                    {
                        "type": "video",
                        "info": video_info,
                        "formats": formats,
                        "tracks": tracks,
                        "subtitles": sub_list,
                    },
                )
        except Exception as e:
            self.call_from_thread(
                self.handle_validation_result, tab_id, False, str(e), None
            )

    def handle_validation_result(
        self,
        tab_id: str,
        success: bool,
        error_msg: Optional[str],
        data: Optional[Dict[str, Any]],
    ) -> None:
        tab = self.query_one(f"#tab-{tab_id}", DownloadTab)

        if not success or data is None:
            tab.status = TabStatus.ERROR
            tab.update_status(error_msg or "Failed to load metadata.", "status-error")
            self.set_tab_label(f"pane-{tab_id}", "New tab  ✗")
            return

        tab.status = TabStatus.IDLE
        tab.update_status(messages.VALIDATION_SUCCESS, "status-success")

        from textual.containers import Vertical

        opts_panel = self.query_one(f"#opts-{tab_id}", Vertical)
        opts_panel.remove_class("hidden")

        # Populate controls based on mode
        mode_select = self.query_one(f"#mode-{tab_id}", Select)
        format_select = self.query_one(f"#format-{tab_id}", Select)
        audio_select = self.query_one(f"#audio-track-{tab_id}", Select)
        sub_list_widget = self.query_one(f"#subtitles-{tab_id}", SelectionList)

        if data["type"] == "playlist":
            entries = (data["info"].get("entries") if data["info"] else []) or []
            urls = [entry.get("url") for entry in entries if entry and entry.get("url")]

            if not urls:
                tab.status = TabStatus.ERROR
                tab.update_status("Playlist contains no valid videos.", "status-error")
                self.set_tab_label(f"pane-{tab_id}", "New tab  ✗")
                return

            def handle_playlist_bucket_result(result: Optional[BucketDownloadSettings]) -> None:
                if not result:
                    self.reset_tab_to_idle(tab_id)
                    return

                from textual.widgets import TabbedContent
                tabs_view = self.query_one("#tabs-view", TabbedContent)

                # Close validation tab
                tabs_view.remove_pane(f"pane-{tab_id}")
                if not tabs_view.tab_count:
                    empty_state = self.query_one("#empty-state-container")
                    empty_state.remove_class("hidden")

                first_tab_id = str(self.tab_counter + 1)
                for url in result.urls:
                    self.add_bucket_download(
                        url=url,
                        is_audio=result.is_audio,
                        format_val=result.format,
                        quality_val=result.quality,
                        out_dir=result.out_dir,
                    )

                if result.urls and first_tab_id:
                    tabs_view.active = f"pane-{first_tab_id}"

                self.notify(f"Queued {len(result.urls)} downloads from playlist")

            self.push_screen(
                BucketScreen(app_settings=self.settings, prefilled_urls=urls),
                handle_playlist_bucket_result,
            )
        else:
            tab.is_playlist = False
            tab.video_info = data["info"]

            title = data["info"].title if data["info"] else "Video"
            self.set_tab_label(f"pane-{tab_id}", f"{title[:15]}...")

            # Audio formats setup
            tab.audio_formats = [
                ("mp3", "mp3"),
                ("m4a", "m4a"),
                ("wav", "wav"),
                ("flac", "flac"),
            ]
            tab.video_formats = (
                [(fmt, fmt) for fmt in data["formats"]]
                if data["formats"]
                else [("mp4", "mp4")]
            )

            # Subtitle selections
            tab.subtitle_tracks = data["subtitles"]
            sub_options = (
                [(str(sub), sub.language_code) for sub in data["subtitles"]]
                if data["subtitles"]
                else []
            )
            sub_list_widget.clear_options()
            if sub_options:
                for text, code in sub_options:
                    sub_list_widget.add_option((text, code))

            # Audio Language tracks setup
            tab.audio_tracks = data["tracks"] if data["tracks"] else []
            track_options = [
                (track.description, track.language_code or "default")
                for track in tab.audio_tracks
            ]
            if not track_options:
                track_options = [("Default audio track", "default")]
            audio_select.set_options(track_options)
            audio_select.value = track_options[0][1]

            # Populate format options based on default mode settings
            current_mode = mode_select.value if mode_select.value else "audio"
            if current_mode == "audio":
                format_select.set_options(tab.audio_formats)
                default_fmt = self.settings.default_audio_format if self.settings else "mp3"
                format_select.value = default_fmt
            else:
                format_select.set_options(tab.video_formats)
                default_fmt = self.settings.default_video_format if self.settings else "mp4"
                format_select.value = default_fmt


            # Connect changes to mode selector to toggle visibility of formats/quality
            self.watch(
                mode_select, "value", lambda val: self.toggle_mode_ui(tab_id, val)
            )

    def toggle_mode_ui(self, tab_id: str, val: str) -> None:
        tab = self.query_one(f"#tab-{tab_id}", DownloadTab)
        format_select = self.query_one(f"#format-{tab_id}", Select)
        from textual.containers import Vertical, Horizontal

        quality_group = self.query_one(f"#quality-group-{tab_id}", Vertical)
        dl_btn = self.query_one(f"#dl-btn-{tab_id}", Button)
        chapters_group = self.query_one(f"#chapters-group-{tab_id}", Horizontal)

        if val == "audio":
            format_select.set_options(
                tab.audio_formats
                if not tab.is_playlist
                else [("mp3", "mp3"), ("m4a", "m4a")]
            )
            format_select.value = "mp3"
            quality_group.add_class("hidden")
            chapters_group.add_class("hidden")
            dl_btn.label = messages.DOWNLOAD_BUTTON_AUDIO
        else:
            opts = (
                tab.video_formats
                if not tab.is_playlist
                else [("mp4", "mp4"), ("mkv", "mkv")]
            )
            format_select.set_options(opts)
            format_select.value = opts[0][1] if opts else "mp4"
            quality_group.remove_class("hidden")
            chapters_group.remove_class("hidden")
            dl_btn.label = messages.DOWNLOAD_BUTTON_VIDEO

    def start_download_action(self, tab_id: str) -> None:
        tab = self.query_one(f"#tab-{tab_id}", DownloadTab)
        mode_val = self.query_one(f"#mode-{tab_id}", Select).value
        mode = mode_val if isinstance(mode_val, str) else "audio"

        fmt_val = self.query_one(f"#format-{tab_id}", Select).value
        fmt = fmt_val if isinstance(fmt_val, str) else "mp3"

        quality_val = self.query_one(f"#quality-{tab_id}", Select).value
        quality = quality_val if isinstance(quality_val, str) else "highest"

        audio_track_val = self.query_one(f"#audio-track-{tab_id}", Select).value
        audio_track = audio_track_val if isinstance(audio_track_val, str) else "default"

        sub_list_widget = self.query_one(f"#subtitles-{tab_id}", SelectionList)
        selected_subs = sub_list_widget.selected

        meta_toggle = self.query_one(f"#meta-{tab_id}", Switch).value
        thumb_toggle = self.query_one(f"#thumb-{tab_id}", Switch).value
        chapters_toggle = self.query_one(f"#chapters-{tab_id}", Switch).value
        from textual.widgets import Input

        out_dir = self.query_one(f"#out-dir-{tab_id}", Input).value.strip()

        # Build download options
        url_input = self.query_one(f"#url-input-{tab_id}", Input)
        url = url_input.value.strip()

        if tab.is_playlist:
            # Custom playlist download directory
            title = (
                tab.playlist_info.get("title", "Playlist")
                if tab.playlist_info
                else "Playlist"
            )
            safe_title = "".join(
                c if c.isalnum() or c in " -_." else "_" for c in title
            )
            out_dir = os.path.join(out_dir, safe_title)

        options = DownloadOptions(
            output_directory=out_dir,
            output_format=fmt,
            include_metadata=meta_toggle,
            include_thumbnail=thumb_toggle,
            include_chapters=chapters_toggle if mode == "video" else False,
            audio_language_code=None if audio_track == "default" else audio_track,
            subtitle_ids=selected_subs,
        )

        # Update UI states
        tab.status = TabStatus.DOWNLOADING
        tab.update_status("Starting download worker...", "status-pending")

        from textual.containers import Vertical

        opts_panel = self.query_one(f"#opts-{tab_id}", Vertical)
        opts_panel.add_class("hidden")

        progress_block = self.query_one(f"#progress-block-{tab_id}", Vertical)
        progress_block.remove_class("hidden")

        log_block = self.query_one(f"#log-block-{tab_id}", Vertical)
        log_block.remove_class("hidden")

        tab_title = (
            (
                tab.playlist_info.get("title", "Playlist")
                if tab.playlist_info
                else "Playlist"
            )
            if tab.is_playlist
            else (tab.video_info.title if tab.video_info else "Video")
        )
        self.set_tab_label(f"pane-{tab_id}", f"{tab_title[:10]}... ↓")

        # Create sidebar record
        self.download_records[tab_id] = DownloadRecord(
            tab_id=tab_id, title=tab_title, status=TabStatus.DOWNLOADING
        )
        self.update_sidebar_queue(tab_id)

        # Remove cancel flag
        self.cancelled_tabs.discard(tab_id)

        # Clear log area
        log_list = self.query_one(f"#log-list-{tab_id}", ScrollableContainer)
        for child in list(log_list.children):
            child.remove()

        # Spawning download threads
        if tab.is_playlist:
            self.run_worker(
                lambda: run_playlist_download_thread(
                    self.extractor,
                    tab_id,
                    url,
                    (mode == "audio"),
                    options,
                    quality,
                    self,
                    tab.playlist_info or {},
                ),
                thread=True,
                name=f"dl-worker-{tab_id}",
            )
        else:
            self.run_worker(
                lambda: run_download_thread(
                    self.extractor,
                    tab_id,
                    url,
                    (mode == "audio"),
                    options,
                    quality,
                    self,
                ),
                thread=True,
                name=f"dl-worker-{tab_id}",
            )

    # Thread-safe message handlers
    def on_download_progress(self, message: DownloadProgress) -> None:
        tab_id = message.tab_id
        if tab_id in self.cancelled_tabs:
            return

        if tab_id.startswith("bucket-"):
            parts = tab_id.split("-")
            batch_id = f"bucket-{parts[1]}"
            try:
                bucket_tab = self.query_one(f"#tab-{batch_id}", BucketQueueTab)
                bucket_tab.update_download_progress(
                    sub_id=tab_id,
                    percent=message.percent,
                    speed=message.speed,
                    eta=message.eta,
                    downloaded=message.downloaded,
                    total=message.total,
                    filename=message.filename,
                )
            except Exception:
                pass
            self.update_sidebar_queue(tab_id)
            return

        pbar = self.query_one(f"#progress-bar-{tab_id}", ProgressBar)
        pbar.progress = message.percent

        lbl_speed = self.query_one(f"#stat-speed-{tab_id}", Label)
        lbl_speed.update(format_speed(message.speed))

        lbl_eta = self.query_one(f"#stat-eta-{tab_id}", Label)
        lbl_eta.update(format_time(message.eta))

        lbl_size = self.query_one(f"#stat-size-{tab_id}", Label)
        lbl_size.update(
            f"{format_size(message.downloaded)} / {format_size(message.total)}"
        )

        # Update record size in sidebar
        record = self.download_records.get(tab_id)
        if record:
            record.file_size = message.total
            record.eta = message.eta
            
            # If title is generic or placeholder, update it with filename
            if (record.title == "Video" or record.title.startswith("Queue:") or record.title.startswith("http")) and message.filename:
                base_title = os.path.splitext(os.path.basename(message.filename))[0]
                record.title = base_title
                self.set_tab_label(f"pane-{tab_id}", f"{base_title[:10]}... ↓")
                try:
                    title_lbl = self.query_one(f"#progress-title-{tab_id}", Label)
                    title_lbl.update(f"Downloading: {base_title}")
                except Exception:
                    pass

            self.update_sidebar_queue(tab_id)

    def on_playlist_progress(self, message: PlaylistProgress) -> None:
        tab_id = message.tab_id
        title = self.query_one(f"#progress-title-{tab_id}", Label)
        title.update(
            f"Downloading [{message.current_idx}/{message.total}]: {message.current_title}"
        )

    def on_log_msg(self, message: LogMsg) -> None:
        tab_id = message.tab_id
        if tab_id.startswith("bucket-"):
            parts = tab_id.split("-")
            batch_id = f"bucket-{parts[1]}"
            try:
                bucket_tab = self.query_one(f"#tab-{batch_id}", BucketQueueTab)
                bucket_tab.update_log(sub_id=tab_id, message=message.message)
            except Exception:
                pass
            return

        log_list = self.query_one(f"#log-list-{tab_id}", ScrollableContainer)
        log_list.mount(Label(message.message))

        # Auto-scroll log list
        log_list.scroll_end(animate=False)

    def on_download_finished(self, message: DownloadFinished) -> None:
        tab_id = message.tab_id

        if tab_id.startswith("bucket-"):
            if tab_id in self.cancelled_tabs:
                return
            parts = tab_id.split("-")
            batch_id = f"bucket-{parts[1]}"
            try:
                bucket_tab = self.query_one(f"#tab-{batch_id}", BucketQueueTab)
                bucket_tab.update_download_finished(
                    sub_id=tab_id,
                    filepath=message.filepath,
                    size=message.size,
                )
                bucket_tab.update_log(sub_id=tab_id, message=f"✓ Finished: Saved to {message.filepath}")
            except Exception:
                pass
            record = self.download_records.get(tab_id)
            if record:
                record.status = TabStatus.DONE
                record.file_size = message.size
                record.output_path = message.filepath
                if record.title == "Video" or record.title.startswith("Queue:") or record.title.startswith("http"):
                    record.title = os.path.splitext(os.path.basename(message.filepath))[0]
            self.update_sidebar_queue(tab_id)
            return

        tab = self.query_one(f"#tab-{tab_id}", DownloadTab)

        # Don't proceed if cancelled
        if tab_id in self.cancelled_tabs:
            return

        tab.status = TabStatus.DONE
        tab.update_status("✓ Download successfully finished!", "status-success")

        pbar = self.query_one(f"#progress-bar-{tab_id}", ProgressBar)
        pbar.progress = 100

        # Update record in queue
        record = self.download_records.get(tab_id)
        if record:
            record.status = TabStatus.DONE
            record.file_size = message.size
            record.output_path = message.filepath
            if record.title == "Video" or record.title.startswith("Queue:"):
                record.title = os.path.splitext(os.path.basename(message.filepath))[0]
            self.update_sidebar_queue(tab_id)

        tab_title = tab.video_info.title if tab.video_info else record.title if record else "Video"
        self.set_tab_label(f"pane-{tab_id}", f"{tab_title[:12]}... ✓")

        # Print success stats
        self.on_log_msg(LogMsg(tab_id, f"\n✓ Success: Saved to {message.filepath}"))

        # Trigger subtitles merge prompt if applicable
        sub_list_widget = self.query_one(f"#subtitles-{tab_id}", SelectionList)
        selected_subs = sub_list_widget.selected
        if selected_subs:
            # Gather subtitle filenames (usually stored next to media file)
            # yt-dlp saves subtitles as: filename.lang_code.vtt
            # Check which subtitle files actually exist
            media_dir = os.path.dirname(message.filepath)
            media_base = os.path.splitext(os.path.basename(message.filepath))[0]

            sub_paths = []
            for lang in selected_subs:
                sub_file = os.path.join(media_dir, f"{media_base}.{lang}.vtt")
                if os.path.exists(sub_file):
                    sub_paths.append(sub_file)

            if sub_paths:
                self.pending_merges[tab_id] = (message.filepath, sub_paths)
                self.trigger_subtitle_merge_modal(tab_id)
            else:
                self.prompt_github_star(tab_id)
        else:
            self.prompt_github_star(tab_id)

    def on_playlist_finished(self, message: PlaylistFinished) -> None:
        tab_id = message.tab_id
        tab = self.query_one(f"#tab-{tab_id}", DownloadTab)

        tab.status = TabStatus.DONE
        tab.update_status(
            f"✓ Playlist download complete! Saved {message.downloaded}/{message.total} files.",
            "status-success",
        )

        # Update record in queue
        record = self.download_records.get(tab_id)
        if record:
            record.status = TabStatus.DONE
            record.file_size = message.total_size
            record.output_path = message.directory
            self.update_sidebar_queue(tab_id)

        tab_title = (
            tab.playlist_info.get("title", "Playlist")
            if tab.playlist_info
            else "Playlist"
        )
        self.set_tab_label(f"pane-{tab_id}", f"{tab_title[:12]}... ✓")

        self.on_log_msg(
            LogMsg(
                tab_id,
                f"\n✓ Playlist successfully complete!\n- Saved: {message.downloaded}\n- Skipped/Failed: {message.skipped}\n- Saved in: {message.directory}",
            )
        )

        # Trigger GitHub star modal
        self.prompt_github_star(tab_id)

    def on_download_error_msg(self, message: DownloadErrorMsg) -> None:
        tab_id = message.tab_id

        if tab_id.startswith("bucket-"):
            parts = tab_id.split("-")
            batch_id = f"bucket-{parts[1]}"
            try:
                bucket_tab = self.query_one(f"#tab-{batch_id}", BucketQueueTab)
                bucket_tab.update_download_error(
                    sub_id=tab_id,
                    error_msg=message.error_msg,
                )
                bucket_tab.update_log(sub_id=tab_id, message=f"❌ Error: {message.error_msg}")
            except Exception:
                pass
            record = self.download_records.get(tab_id)
            if record:
                record.status = TabStatus.ERROR
            self.update_sidebar_queue(tab_id)
            return

        tab = self.query_one(f"#tab-{tab_id}", DownloadTab)

        tab.status = TabStatus.ERROR
        tab.update_status(f"❌ Error: {message.error_msg}", "status-error")

        record = self.download_records.get(tab_id)
        if record:
            record.status = TabStatus.ERROR
            self.update_sidebar_queue(tab_id)

        tab_title = (
            (
                tab.playlist_info.get("title", "Playlist")
                if tab.playlist_info
                else "Playlist"
            )
            if tab.is_playlist
            else (tab.video_info.title if tab.video_info else record.title if record else "Video")
        )
        self.set_tab_label(f"pane-{tab_id}", f"{tab_title[:12]}... ✗")

        self.on_log_msg(LogMsg(tab_id, f"\n❌ ERROR: {message.error_msg}"))

    # Sidebar UI updates
    def update_sidebar_queue(self, tab_id: str) -> None:
        queue_table = self.query_one("#queue-table", DataTable)
        queue_table.clear()

        # Populate table
        for tid, record in self.download_records.items():
            status_text = record.status.value.capitalize()
            if record.status == TabStatus.DOWNLOADING:
                status_text = "Downloading ↓"
            elif record.status == TabStatus.DONE:
                status_text = "✓ Done"
            elif record.status == TabStatus.ERROR:
                status_text = "✗ Failed"

            size_str = format_size(record.file_size) if record.file_size else "—"

            if record.status == TabStatus.DONE:
                time_str = "Done"
            elif record.status == TabStatus.DOWNLOADING and record.eta is not None:
                time_str = format_time(record.eta)
            else:
                time_str = "—"

            queue_table.add_row(
                record.title[:15],
                status_text,
                size_str,
                time_str,
                key=tid,
            )

    # Subtitle merging screens flows
    def trigger_subtitle_merge_modal(self, tab_id: str) -> None:
        filepath, subs = self.pending_merges[tab_id]

        def handle_modal_result(merge_confirmed: Optional[bool]) -> None:
            if not merge_confirmed:
                self.notify("Subtitle merge skipped.")
                self.prompt_github_star(tab_id)
                return

            # Trigger merging in thread worker
            self.on_log_msg(LogMsg(tab_id, "\nMerging subtitles..."))
            self.run_worker(
                lambda: self.do_merge_subtitles(tab_id, filepath, subs),
                thread=True,
                name=f"merge-worker-{tab_id}",
            )

        self.push_screen(
            QuestionModal(
                title="Merge Subtitles",
                text=f"{len(subs)} subtitle tracks downloaded. Embed them into the media file?",
                yes_label="Merge",
                no_label="Skip",
            ),
            handle_modal_result,
        )

    def do_merge_subtitles(
        self, tab_id: str, media_file: str, subtitle_files: List[str]
    ) -> None:
        try:
            merged_file = self.extractor.merge_subtitles(media_file, subtitle_files)

            # Post success log
            self.call_from_thread(
                self.on_log_msg,
                LogMsg(tab_id, f"✓ Subtitles successfully merged into: {merged_file}"),
            )

            # If successful, prompt delete original
            if os.path.exists(merged_file) and merged_file != media_file:
                # Store merged path in record
                record = self.download_records.get(tab_id)
                if record:
                    record.output_path = merged_file

                self.call_from_thread(
                    self.trigger_delete_original_modal,
                    tab_id,
                    media_file,
                    subtitle_files,
                )
            else:
                self.call_from_thread(self.prompt_github_star, tab_id)
        except Exception as e:
            self.call_from_thread(
                self.on_log_msg, LogMsg(tab_id, f"❌ Merge subtitles failed: {str(e)}")
            )
            self.call_from_thread(self.prompt_github_star, tab_id)

    def trigger_delete_original_modal(
        self, tab_id: str, original_file: str, subtitle_files: List[str]
    ) -> None:
        def handle_delete_result(delete_confirmed: Optional[bool]) -> None:
            if delete_confirmed:
                try:
                    # Delete original media file
                    if os.path.exists(original_file):
                        os.remove(original_file)
                        self.on_log_msg(
                            LogMsg(tab_id, f"🗑️ Deleted original file: {original_file}")
                        )

                    # Delete subtitle vtt files
                    for f in subtitle_files:
                        if os.path.exists(f):
                            os.remove(f)
                            self.on_log_msg(
                                LogMsg(tab_id, f"🗑️ Deleted subtitle file: {f}")
                            )

                    self.notify("Original files deleted.")
                except Exception as e:
                    self.on_log_msg(LogMsg(tab_id, f"Error cleanup: {str(e)}"))

            self.prompt_github_star(tab_id)

        self.push_screen(
            QuestionModal(
                title="Cleanup Files",
                text="Delete the original file (without subtitles) and raw subtitle files?",
                yes_label="Delete",
                no_label="Keep Both",
            ),
            handle_delete_result,
        )

    def prompt_github_star(self, tab_id: str) -> None:
        """Triggers the GitHub star suggestion panel on the specified tab."""
        try:
            tab = self.query_one(f"#tab-{tab_id}", DownloadTab)
            tab.show_star_panel()
        except Exception:
            pass

    def handle_star_click(self, tab_id: str) -> None:
        import webbrowser

        try:
            webbrowser.open("https://github.com/Youssef-Naggar/ultratube")
            self.notify("Opening GitHub repository...")
        except Exception:
            self.notify(
                "Could not open browser. URL: github.com/Youssef-Naggar/ultratube"
            )
        self.reset_tab_to_idle(tab_id)

    def handle_star_skip(self, tab_id: str) -> None:
        self.reset_tab_to_idle(tab_id)

    def reset_tab_to_idle(self, tab_id: str) -> None:
        try:
            tab = self.query_one(f"#tab-{tab_id}", DownloadTab)
            tab.reset_to_idle()
            self.set_tab_label(f"pane-{tab_id}", f"New Tab #{tab_id}")
        except Exception:
            pass

    # Click row in DataTable copies path
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        tab_id = event.row_key.value
        if not tab_id:
            return

        record = self.download_records.get(tab_id)
        if record and record.status == TabStatus.DONE and record.output_path:
            copy_to_clipboard(record.output_path)
            self.notify("Output path copied to clipboard!")


def main():
    app = UltraTubeApp()
    app.run()


if __name__ == "__main__":
    main()
