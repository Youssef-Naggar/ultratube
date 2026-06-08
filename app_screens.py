import os
from typing import Optional, Any, List

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label, DataTable, Button, TextArea, Select, Input
from textual.screen import ModalScreen, Screen
import messages
from models import BucketDownloadSettings


class HelpScreen(ModalScreen):
    """Overlay displaying application keyboard shortcuts."""

    def compose(self) -> ComposeResult:
        with Container(id="help-dialog"):
            yield Label(messages.HELP_TITLE, id="help-title")

            table = DataTable(id="help-table")
            table.add_columns("Key", "Action")
            table.add_rows(
                [
                    ("Ctrl+T", "Open a new download tab"),
                    ("Ctrl+W", "Close the current tab"),
                    ("Ctrl+B", "Open bucket download dialog"),
                    ("Ctrl+Tab", "Switch to the next tab"),
                    ("F1", "Toggle this help screen"),
                    ("Escape", "Dismiss overlay / cancel current tab download"),
                    ("Q", "Quit UltraTube"),
                ]
            )
            yield table
            yield Label("Press F1 or Escape to close", id="help-footer")

    def on_key(self, event) -> None:
        if event.key in ("escape", "f1"):
            self.dismiss()


class QuestionModal(ModalScreen[bool]):
    """Standard Yes/No dialog screen."""

    def __init__(
        self, title: str, text: str, yes_label: str = "Yes", no_label: str = "No"
    ):
        super().__init__()
        self.dialog_title = title
        self.dialog_text = text
        self.yes_label = yes_label
        self.no_label = no_label

    def compose(self) -> ComposeResult:
        with Container(id="help-dialog"):
            yield Label(f"[bold cyan]{self.dialog_title}[/bold cyan]", id="help-title")
            yield Label(self.dialog_text, classes="modal-text")
            with Horizontal(classes="modal-buttons"):
                yield Button(
                    self.yes_label,
                    variant="primary",
                    id="yes-btn",
                    classes="modal-btn-yes",
                )
                yield Button(self.no_label, variant="default", id="no-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes-btn":
            self.dismiss(True)
        else:
            self.dismiss(False)


class BucketScreen(Screen[Optional[BucketDownloadSettings]]):
    """Full-screen dashboard for pasting multiple URLs and configuring bulk download options."""

    BINDINGS = [
        ("escape", "cancel", "Cancel & Back"),
        ("ctrl+d", "submit", "Queue & Download"),
    ]

    def __init__(
        self,
        app_settings: Optional[Any] = None,
        prefilled_urls: Optional[List[str]] = None,
    ):
        super().__init__()
        self.app_settings = app_settings
        self.prefilled_urls = prefilled_urls

    def compose(self) -> ComposeResult:
        with Horizontal(id="bucket-screen-container"):
            # Left panel - URLs and Preview
            with Vertical(id="bucket-left-panel"):
                yield Label("📥 BUCKET DOWNLOADS", id="bucket-screen-title")
                yield Label(
                    "Paste Video/Audio URLs (one per line):",
                    classes="bucket-label",
                )
                urls_text = "\n".join(self.prefilled_urls) if self.prefilled_urls else ""
                yield TextArea(
                    text=urls_text,
                    placeholder="https://www.youtube.com/watch?v=...\nhttps://...",
                    id="bucket-urls",
                )
                yield Label(
                    "Parsed: 0 valid URLs / 0 invalid",
                    id="bucket-parsed-count",
                    classes="status-label",
                )

            # Right panel - Configuration
            with Vertical(id="bucket-right-panel"):
                yield Label("🎛️ GLOBAL CONFIGURATION", classes="options-title")

                yield Label("Download Type", classes="group-label")
                
                default_mode = self.app_settings.default_mode if self.app_settings else "audio"
                yield Select(
                    [("🎵 Audio Only", "audio"), ("🎥 Video + Audio", "video")],
                    value=default_mode,
                    id="bucket-mode",
                )

                yield Label("Output Format", classes="group-label mt-1")
                yield Select([], id="bucket-format")

                # Setup quality selector visibility based on default mode
                quality_group_classes = "hidden"
                if self.app_settings and self.app_settings.default_mode == "video":
                    quality_group_classes = ""

                with Vertical(classes=quality_group_classes, id="bucket-quality-group"):
                    yield Label("Video Quality", classes="group-label mt-1")
                    
                    default_quality = self.app_settings.default_quality if self.app_settings else "highest"
                    yield Select(
                        [
                            ("Highest Available", "highest"),
                            ("1080p (Full HD)", "1080p"),
                            ("720p (HD)", "720p"),
                            ("480p", "480p"),
                            ("360p", "360p"),
                            ("240p", "240p"),
                        ],
                        value=default_quality,
                        id="bucket-quality",
                    )

                yield Label("Save to Folder", classes="group-label mt-1")
                
                default_dir = self.app_settings.out_dir if self.app_settings else os.path.expanduser("~/Downloads")
                yield Input(
                    value=default_dir,
                    id="bucket-out-dir",
                )

                # Action buttons
                with Horizontal(classes="bucket-buttons-container"):
                    yield Button(
                        "Queue & Download",
                        variant="primary",
                        id="bucket-dl-btn",
                        classes="bucket-btn-yes",
                    )
                    yield Button(
                        "Cancel & Back",
                        variant="default",
                        id="bucket-cancel-btn",
                        classes="bucket-btn-no",
                    )

    def on_mount(self) -> None:
        default_mode = self.app_settings.default_mode if self.app_settings else "audio"
        self.update_formats_dropdown(default_mode)
        self.validate_urls_realtime()

    def update_formats_dropdown(self, mode: str) -> None:
        fmt_select = self.query_one("#bucket-format", Select)
        if mode == "audio":
            fmt_select.set_options(
                [
                    ("mp3", "mp3"),
                    ("m4a", "m4a"),
                    ("wav", "wav"),
                    ("flac", "flac"),
                ]
            )
            
            default_fmt = self.app_settings.default_audio_format if self.app_settings else "mp3"
            fmt_select.value = default_fmt
            self.query_one("#bucket-quality-group").add_class("hidden")
        else:
            fmt_select.set_options(
                [("mp4", "mp4"), ("mkv", "mkv"), ("webm", "webm")]
            )
            
            default_fmt = self.app_settings.default_video_format if self.app_settings else "mp4"
            fmt_select.value = default_fmt
            self.query_one("#bucket-quality-group").remove_class("hidden")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "bucket-mode":
            self.update_formats_dropdown(str(event.value))

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if event.text_area.id == "bucket-urls":
            self.validate_urls_realtime()

    def validate_urls_realtime(self) -> None:
        urls_text = self.query_one("#bucket-urls", TextArea).text.strip()
        urls = [
            line.strip() for line in urls_text.splitlines() if line.strip()
        ]

        valid_count = 0
        invalid_count = 0

        for url in urls:
            # Simple client-side syntax validation
            if url.startswith("http://") or url.startswith("https://"):
                valid_count += 1
            else:
                invalid_count += 1

        lbl = self.query_one("#bucket-parsed-count", Label)
        if urls:
            lbl.update(
                f"Parsed: {valid_count} valid URLs / {invalid_count} invalid"
            )
            if invalid_count > 0:
                lbl.remove_class("status-success")
                lbl.add_class("status-error")
            else:
                lbl.remove_class("status-error")
                lbl.add_class("status-success")
        else:
            lbl.update("Parsed: 0 valid URLs / 0 invalid")
            lbl.remove_class("status-success", "status-error")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_submit(self) -> None:
        self.submit_settings()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "bucket-dl-btn":
            self.submit_settings()
        elif event.button.id == "bucket-cancel-btn":
            self.dismiss(None)

    def submit_settings(self) -> None:
        urls_text = self.query_one("#bucket-urls", TextArea).text.strip()
        urls = [
            line.strip() for line in urls_text.splitlines() if line.strip()
        ]

        if not urls:
            self.app.notify("Please enter at least one URL.", severity="error")
            return

        mode_val = self.query_one("#bucket-mode", Select).value
        mode = mode_val if isinstance(mode_val, str) else "audio"

        fmt_val = self.query_one("#bucket-format", Select).value
        fmt = fmt_val if isinstance(fmt_val, str) else "mp3"

        quality_val = self.query_one("#bucket-quality", Select).value
        quality = quality_val if isinstance(quality_val, str) else "highest"

        out_dir = self.query_one("#bucket-out-dir", Input).value.strip()

        if not out_dir:
            self.app.notify("Save folder cannot be empty.", severity="error")
            return

        try:
            settings = BucketDownloadSettings(
                urls=urls,
                is_audio=(mode == "audio"),
                format=fmt,
                quality=quality,
                out_dir=out_dir,
            )
            self.dismiss(settings)
        except Exception as e:
            self.app.notify(
                f"Invalid configurations: {str(e)}", severity="error"
            )

