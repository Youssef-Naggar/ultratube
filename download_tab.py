import os
from typing import Optional, Dict, Any
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import (
    Label,
    Input,
    Button,
    Select,
    SelectionList,
    Switch,
    ProgressBar,
)

from ultratube_extractor import UltraTubeExtractor
from models import TabStatus
from settings_service import AppSettings
import messages


class DownloadTab(Vertical):
    def __init__(
        self,
        tab_id: str,
        extractor: UltraTubeExtractor,
        url: Optional[str] = None,
        bucket_settings: Optional[Dict[str, Any]] = None,
        settings: Optional[AppSettings] = None,
    ):
        super().__init__(id=f"tab-{tab_id}")
        self.tab_id = tab_id
        self.extractor = extractor
        self.url = url
        self.bucket_settings = bucket_settings
        self.settings = settings

        self.status = TabStatus.IDLE
        self.is_playlist = False
        self.playlist_info = None
        self.video_info = None

        # Data arrays loaded from URL validation
        self.audio_formats = []
        self.video_formats = []
        self.audio_tracks = []
        self.subtitle_tracks = []

    def compose(self) -> ComposeResult:
        with ScrollableContainer(classes="tab-scroll-container"):
            # URL input section
            with Container(classes="url-section", id=f"url-section-{self.tab_id}"):
                yield Label("Paste Video, Audio, or Playlist Link:")
                with Horizontal(classes="url-input-container"):
                    yield Input(
                        value=self.url or "",
                        placeholder=messages.URL_INPUT_PLACEHOLDER,
                        classes="url-input",
                        id=f"url-input-{self.tab_id}",
                    )
                    yield Button(
                        "Validate",
                        classes="validate-button",
                        id=f"val-btn-{self.tab_id}",
                    )
                yield Label(
                    messages.URL_INPUT_HELP,
                    classes="status-label",
                    id=f"status-label-{self.tab_id}",
                )

            # Options panel (initially hidden/collapsed)
            with Vertical(classes="options-container hidden", id=f"opts-{self.tab_id}"):
                yield Label("Configure Download Settings", classes="options-title")

                with Container(classes="options-grid"):
                    with Vertical(classes="options-group"):
                        yield Label(
                            messages.MODE_SELECTOR_PROMPT, classes="group-label"
                        )
                        mode_val = "audio"
                        if self.bucket_settings:
                            mode_val = "audio" if self.bucket_settings["is_audio"] else "video"
                        elif self.settings:
                            mode_val = self.settings.default_mode

                        yield Select(
                            [("🎵 Audio Only", "audio"), ("🎥 Video + Audio", "video")],
                            value=mode_val,
                            id=f"mode-{self.tab_id}",
                        )

                    with Vertical(classes="options-group"):
                        yield Label(
                            messages.FORMAT_SELECTOR_PROMPT, classes="group-label"
                        )
                        fmt_options = []
                        fmt_value = Select.NULL
                        if self.bucket_settings:
                            if self.bucket_settings["is_audio"]:
                                fmt_options = [("mp3", "mp3"), ("m4a", "m4a"), ("wav", "wav"), ("flac", "flac")]
                            else:
                                fmt_options = [("mp4", "mp4"), ("mkv", "mkv"), ("webm", "webm")]
                            fmt_value = self.bucket_settings["format"]
                        elif self.settings:
                            if self.settings.default_mode == "audio":
                                fmt_options = [("mp3", "mp3"), ("m4a", "m4a"), ("wav", "wav"), ("flac", "flac")]
                                fmt_value = self.settings.default_audio_format
                            else:
                                fmt_options = [("mp4", "mp4"), ("mkv", "mkv"), ("webm", "webm")]
                                fmt_value = self.settings.default_video_format

                        yield Select(fmt_options, value=fmt_value, id=f"format-{self.tab_id}")

                with Container(classes="options-grid"):
                    quality_group_classes = "options-group hidden"
                    if self.bucket_settings and not self.bucket_settings["is_audio"]:
                        quality_group_classes = "options-group"
                    elif self.settings and self.settings.default_mode == "video":
                        quality_group_classes = "options-group"

                    with Vertical(
                        classes=quality_group_classes,
                        id=f"quality-group-{self.tab_id}",
                    ):
                        yield Label(
                            messages.QUALITY_SELECTOR_PROMPT, classes="group-label"
                        )
                        
                        quality_val = "highest"
                        if self.bucket_settings:
                            quality_val = self.bucket_settings["quality"]
                        elif self.settings:
                            quality_val = self.settings.default_quality

                        yield Select(
                            [
                                ("Highest Available", "highest"),
                                ("1080p (Full HD)", "1080p"),
                                ("720p (HD)", "720p"),
                                ("480p", "480p"),
                                ("360p", "360p"),
                                ("240p", "240p"),
                            ],
                            value=quality_val,
                            id=f"quality-{self.tab_id}",
                        )


                    with Vertical(
                        classes="options-group", id=f"audio-track-group-{self.tab_id}"
                    ):
                        yield Label(messages.AUDIO_TRACK_PROMPT, classes="group-label")
                        yield Select([], id=f"audio-track-{self.tab_id}")

                with Vertical(classes="options-group mt-1"):
                    yield Label(
                        messages.SUBTITLE_SELECTOR_PROMPT, classes="group-label"
                    )
                    yield SelectionList(id=f"subtitles-{self.tab_id}")

                meta_val = self.settings.include_metadata if self.settings else True
                thumb_val = self.settings.include_thumbnail if self.settings else True
                chapters_val = self.settings.include_chapters if self.settings else True

                chapters_group_classes = "toggle-item hidden"
                if self.settings and self.settings.default_mode == "video":
                    chapters_group_classes = "toggle-item"

                with Horizontal(classes="toggles-group"):
                    with Horizontal(classes="toggle-item"):
                        yield Label(messages.TOGGLE_METADATA)
                        yield Switch(value=meta_val, id=f"meta-{self.tab_id}")
                    with Horizontal(classes="toggle-item"):
                        yield Label(messages.TOGGLE_THUMBNAIL)
                        yield Switch(value=thumb_val, id=f"thumb-{self.tab_id}")
                    with Horizontal(
                        classes=chapters_group_classes, id=f"chapters-group-{self.tab_id}"
                    ):
                        yield Label(messages.TOGGLE_CHAPTERS)
                        yield Switch(value=chapters_val, id=f"chapters-{self.tab_id}")

                # Output directory
                yield Label(messages.OUTPUT_DIR_PROMPT, classes="group-label mt-1")
                
                default_dir = os.path.expanduser("~/Downloads")
                if self.bucket_settings:
                    default_dir = self.bucket_settings["out_dir"]
                elif self.settings:
                    default_dir = self.settings.out_dir

                with Horizontal(classes="output-dir-container"):
                    yield Input(
                        value=default_dir,
                        id=f"out-dir-{self.tab_id}",
                        classes="output-dir-input",
                    )


                yield Button(
                    messages.DOWNLOAD_BUTTON_AUDIO,
                    id=f"dl-btn-{self.tab_id}",
                    classes="download-action-btn",
                )

            # Progress widget (initially hidden)
            with Vertical(
                classes="progress-container hidden", id=f"progress-block-{self.tab_id}"
            ):
                yield Label(
                    "Downloading...",
                    classes="progress-title",
                    id=f"progress-title-{self.tab_id}",
                )
                yield ProgressBar(
                    total=100, show_percentage=True, id=f"progress-bar-{self.tab_id}"
                )
                with Container(classes="progress-stats-grid"):
                    with Vertical(classes="stat-item"):
                        yield Label("Speed", classes="stat-label")
                        yield Label(
                            "0.0 MB/s",
                            classes="stat-value",
                            id=f"stat-speed-{self.tab_id}",
                        )
                    with Vertical(classes="stat-item"):
                        yield Label("ETA", classes="stat-label")
                        yield Label(
                            "0:00", classes="stat-value", id=f"stat-eta-{self.tab_id}"
                        )
                    with Vertical(classes="stat-item"):
                        yield Label("Progress", classes="stat-label")
                        yield Label(
                            "0 B / 0 B",
                            classes="stat-value",
                            id=f"stat-size-{self.tab_id}",
                        )

            # Logs view console
            with Vertical(
                classes="log-container hidden", id=f"log-block-{self.tab_id}"
            ):
                yield Label("Terminal Output Log:", classes="log-title")
                yield ScrollableContainer(id=f"log-list-{self.tab_id}")

            # GitHub Star Suggestion Panel (initially hidden)
            with Vertical(classes="star-panel hidden", id=f"star-panel-{self.tab_id}"):
                yield Label(
                    "Thank you for using UltraTube!", classes="star-panel-title"
                )
                yield Label(
                    "Enjoying the app? Please consider giving it a ⭐ on GitHub to support the project!",
                    classes="star-panel-text",
                )
                with Horizontal(classes="star-panel-buttons"):
                    yield Button(
                        "Star on GitHub",
                        variant="success",
                        id=f"star-btn-{self.tab_id}",
                        classes="star-btn-yes",
                    )
                    yield Button(
                        "Maybe Later",
                        variant="default",
                        id=f"star-skip-btn-{self.tab_id}",
                        classes="star-btn-no",
                    )

    def update_status(self, text: str, status_class: str = "") -> None:
        lbl = self.query_one(f"#status-label-{self.tab_id}", Label)
        lbl.remove_class("status-success", "status-error", "status-pending")
        if status_class:
            lbl.add_class(status_class)
        lbl.update(text)

    def show_star_panel(self) -> None:
        """Hides the options, progress, and logs, and displays the GitHub star panel."""
        self.query_one(f"#url-section-{self.tab_id}").add_class("hidden")
        self.query_one(f"#opts-{self.tab_id}").add_class("hidden")
        self.query_one(f"#progress-block-{self.tab_id}").add_class("hidden")
        self.query_one(f"#log-block-{self.tab_id}").add_class("hidden")
        self.query_one(f"#star-panel-{self.tab_id}").remove_class("hidden")

    def reset_to_idle(self) -> None:
        """Resets the tab to the idle state to allow another download."""
        self.status = TabStatus.IDLE
        self.is_playlist = False
        self.playlist_info = None
        self.video_info = None
        self.audio_formats = []
        self.video_formats = []
        self.audio_tracks = []
        self.subtitle_tracks = []

        # Clear inputs
        url_input = self.query_one(f"#url-input-{self.tab_id}", Input)
        url_input.value = ""

        # Update status message to prompt
        self.update_status(messages.URL_INPUT_HELP)

        # Show URL section, hide others
        self.query_one(f"#url-section-{self.tab_id}").remove_class("hidden")
        self.query_one(f"#opts-{self.tab_id}").add_class("hidden")
        self.query_one(f"#progress-block-{self.tab_id}").add_class("hidden")
        self.query_one(f"#log-block-{self.tab_id}").add_class("hidden")
        self.query_one(f"#star-panel-{self.tab_id}").add_class("hidden")

    def on_mount(self) -> None:
        if self.bucket_settings:
            from typing import cast
            from ultratube_app import UltraTubeApp

            app = cast(UltraTubeApp, self.app)
            app.call_after_refresh(app.start_download_action, self.tab_id)
