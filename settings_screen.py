from typing import cast
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Input, Button, Select, Switch
from textual.screen import Screen
from settings_service import AppSettings, save_settings
from app_screens import HelpScreen
from app_utils import copy_to_clipboard

GITHUB_REPO_URL = "https://github.com/youss/ultratube"


class SettingsScreen(Screen[None]):
    """Full-screen dashboard for modifying and saving global download preferences."""

    BINDINGS = [
        ("escape", "cancel", "Cancel & Back"),
        ("ctrl+s", "submit", "Save Preferences"),
    ]

    def __init__(self, settings: AppSettings):
        super().__init__(id="settings-screen")
        self.settings = settings

    def compose(self) -> ComposeResult:
        with Horizontal(id="settings-screen-container"):
            # Left panel - Settings Form (60% width)
            with Vertical(id="settings-left-panel"):
                yield Label("⚙️ APPLICATION PREFERENCES", id="settings-screen-title")

                yield Label("Default Save Folder", classes="group-label")
                yield Input(
                    value=self.settings.out_dir,
                    id="settings-out-dir",
                    placeholder="Enter absolute path for destination folder...",
                    classes="output-dir-input",
                )

                # Default choices grid
                yield Label("Default Download Choices", classes="group-label mt-1")
                with Horizontal(classes="toggles-group"):
                    with Vertical(classes="options-group settings-half-width"):
                        yield Label("Default Mode", classes="group-label")
                        yield Select(
                            [
                                ("🎵 Audio Only", "audio"),
                                ("🎥 Video + Audio", "video"),
                            ],
                            value=self.settings.default_mode,
                            id="settings-mode",
                        )
                    with Vertical(classes="options-group settings-half-width"):
                        yield Label("Default Video Quality", classes="group-label")
                        yield Select(
                            [
                                ("Highest Available", "highest"),
                                ("1080p (Full HD)", "1080p"),
                                ("720p (HD)", "720p"),
                                ("480p", "480p"),
                                ("360p", "360p"),
                                ("240p", "240p"),
                            ],
                            value=self.settings.default_quality,
                            id="settings-quality",
                        )

                with Horizontal(classes="toggles-group mt-1"):
                    with Vertical(classes="options-group settings-half-width"):
                        yield Label("Default Audio Format", classes="group-label")
                        yield Select(
                            [
                                ("mp3", "mp3"),
                                ("m4a", "m4a"),
                                ("wav", "wav"),
                                ("flac", "flac"),
                            ],
                            value=self.settings.default_audio_format,
                            id="settings-audio-format",
                        )
                    with Vertical(classes="options-group settings-half-width"):
                        yield Label("Default Video Format", classes="group-label")
                        yield Select(
                            [("mp4", "mp4"), ("mkv", "mkv"), ("webm", "webm")],
                            value=self.settings.default_video_format,
                            id="settings-video-format",
                        )

            # Right panel - Toggles and Actions (40% width)
            with Vertical(id="settings-right-panel"):
                yield Label("DEFAULT FEATURE SWITCHES", classes="options-title")

                yield Label("Embed Metadata", classes="group-label")
                yield Switch(value=self.settings.include_metadata, id="settings-meta")

                yield Label("Embed Thumbnail", classes="group-label mt-1")
                yield Switch(value=self.settings.include_thumbnail, id="settings-thumb")

                yield Label("Split Chapters", classes="group-label mt-1")
                yield Switch(value=self.settings.include_chapters, id="settings-chapters")

                # Help shortcuts
                yield Label("Need Help?", classes="group-label mt-1")
                yield Button(
                    "📖 View Keyboard Shortcuts",
                    id="settings-help-btn",
                    classes="settings-help-button",
                )

                # Feedback card
                with Vertical(classes="options-container", id="settings-feedback-card"):
                    yield Label("Enjoying UltraTube?", classes="options-title")
                    yield Label(
                        "Please consider giving it a ⭐ on GitHub to support the project!",
                        classes="group-label",
                    )
                    yield Button(
                        "⭐ Copy GitHub Repo URL",
                        id="settings-github-btn",
                        classes="settings-github-button",
                    )

                # Buttons container
                with Horizontal(classes="settings-buttons-container"):
                    yield Button(
                        "Save Preferences",
                        variant="primary",
                        id="settings-save-btn",
                        classes="settings-save-button",
                    )
                    yield Button(
                        "Cancel & Back",
                        variant="default",
                        id="settings-cancel-btn",
                        classes="settings-cancel-button",
                    )

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_submit(self) -> None:
        self.save_preferences_action()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "settings-save-btn":
            self.save_preferences_action()
        elif event.button.id == "settings-cancel-btn":
            self.dismiss(None)
        elif event.button.id == "settings-help-btn":
            self.app.push_screen(HelpScreen())
        elif event.button.id == "settings-github-btn":
            copy_to_clipboard(GITHUB_REPO_URL)
            self.app.notify("GitHub Repository URL copied to clipboard!", severity="information")

    def save_preferences_action(self) -> None:
        out_dir = self.query_one("#settings-out-dir", Input).value.strip()
        if not out_dir:
            self.app.notify("Default save folder path cannot be empty.", severity="error")
            return

        mode_val = self.query_one("#settings-mode", Select).value
        mode = mode_val if isinstance(mode_val, str) else "audio"

        audio_fmt_val = self.query_one("#settings-audio-format", Select).value
        audio_fmt = audio_fmt_val if isinstance(audio_fmt_val, str) else "mp3"

        video_fmt_val = self.query_one("#settings-video-format", Select).value
        video_fmt = video_fmt_val if isinstance(video_fmt_val, str) else "mp4"

        quality_val = self.query_one("#settings-quality", Select).value
        quality = quality_val if isinstance(quality_val, str) else "highest"

        meta = self.query_one("#settings-meta", Switch).value
        thumb = self.query_one("#settings-thumb", Switch).value
        chapters = self.query_one("#settings-chapters", Switch).value

        self.settings.out_dir = out_dir
        self.settings.default_mode = mode
        self.settings.default_audio_format = audio_fmt
        self.settings.default_video_format = video_fmt
        self.settings.default_quality = quality
        self.settings.include_metadata = meta
        self.settings.include_thumbnail = thumb
        self.settings.include_chapters = chapters

        save_settings(self.settings)

        from ultratube_app import UltraTubeApp
        app = cast(UltraTubeApp, self.app)
        app.settings = self.settings

        self.app.notify("Preferences saved successfully!", severity="information")
        self.dismiss(None)
