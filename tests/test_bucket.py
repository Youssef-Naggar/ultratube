import pytest
from pydantic import ValidationError

# We import BucketDownloadSettings from models once implemented
# For now, we will handle potential import failure in the TDD setup
try:
    from models import BucketDownloadSettings
except ImportError:
    BucketDownloadSettings = None


def parse_urls_text(text: str) -> list[str]:
    """Helper to parse raw text area content into list of sanitized URLs."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def test_parse_urls_text():
    raw_text = """
    https://www.youtube.com/watch?v=abc12345678
    
      https://youtu.be/xyz98765432  
      
    """
    urls = parse_urls_text(raw_text)
    assert urls == [
        "https://www.youtube.com/watch?v=abc12345678",
        "https://youtu.be/xyz98765432",
    ]


def test_bucket_download_settings_valid():
    if BucketDownloadSettings is None:
        pytest.skip("BucketDownloadSettings is not yet defined in models.py")

    settings = BucketDownloadSettings(
        urls=["https://www.youtube.com/watch?v=abc12345678"],
        is_audio=True,
        format="mp3",
        quality="highest",
        out_dir="C:/Users/youss/Downloads",
    )
    assert settings.urls == ["https://www.youtube.com/watch?v=abc12345678"]
    assert settings.is_audio is True
    assert settings.format == "mp3"
    assert settings.quality == "highest"
    assert settings.out_dir == "C:/Users/youss/Downloads"


def test_bucket_download_settings_invalid_urls():
    if BucketDownloadSettings is None:
        pytest.skip("BucketDownloadSettings is not yet defined in models.py")

    with pytest.raises(ValidationError):
        BucketDownloadSettings(
            urls="not-a-list",  # Should be List[str]
            is_audio=True,
            format="mp3",
            quality="highest",
            out_dir="C:/Users/youss/Downloads",
        )


@pytest.mark.anyio
async def test_bucket_screen_validation():
    from ultratube_app import UltraTubeApp
    from app_screens import BucketScreen
    from textual.widgets import TextArea, Label

    app = UltraTubeApp()
    async with app.run_test() as pilot:
        await app.push_screen(BucketScreen())
        screen = app.screen
        assert isinstance(screen, BucketScreen)
        
        text_area = screen.query_one("#bucket-urls", TextArea)
        text_area.text = "https://youtube.com/watch?v=123\ninvalid-url"
        screen.validate_urls_realtime()
        
        parsed_lbl = screen.query_one("#bucket-parsed-count", Label)
        assert "1 valid" in str(parsed_lbl.render())
        assert "1 invalid" in str(parsed_lbl.render())
        
        await pilot.press("escape")


def test_app_settings_defaults():
    try:
        from settings_service import AppSettings
    except ImportError:
        pytest.skip("settings_service.py is not yet implemented")

    settings = AppSettings()
    assert settings.default_mode == "audio"
    assert settings.default_audio_format == "mp3"
    assert settings.include_metadata is True


def test_settings_save_load(tmp_path):
    try:
        from settings_service import load_settings, save_settings, AppSettings
        import settings_service
    except ImportError:
        pytest.skip("settings_service.py is not yet implemented")

    original_file = settings_service.SETTINGS_FILE
    temp_file = str(tmp_path / "settings.json")
    settings_service.SETTINGS_FILE = temp_file

    try:
        settings = AppSettings(default_mode="video", default_audio_format="m4a")
        save_settings(settings)

        loaded = load_settings()
        assert loaded.default_mode == "video"
        assert loaded.default_audio_format == "m4a"
    finally:
        settings_service.SETTINGS_FILE = original_file


@pytest.mark.anyio
async def test_settings_screen_rendering():
    from ultratube_app import UltraTubeApp
    from settings_screen import SettingsScreen
    from textual.widgets import Input, Select

    app = UltraTubeApp()
    async with app.run_test():
        await app.push_screen(SettingsScreen(app.settings))
        screen = app.screen
        assert isinstance(screen, SettingsScreen)

        out_dir_input = screen.query_one("#settings-out-dir", Input)
        assert out_dir_input.value == app.settings.out_dir

        mode_select = screen.query_one("#settings-mode", Select)
        assert mode_select.value == app.settings.default_mode


@pytest.mark.anyio
async def test_bucket_screen_prefilled_urls():
    from app_screens import BucketScreen
    from textual.widgets import TextArea, Label

    urls = ["https://youtube.com/watch?v=1", "https://youtube.com/watch?v=2"]
    screen = BucketScreen(prefilled_urls=urls)

    from ultratube_app import UltraTubeApp
    app = UltraTubeApp()
    async with app.run_test() as pilot:
        await app.push_screen(screen)
        text_area = screen.query_one("#bucket-urls", TextArea)
        assert text_area.text == "https://youtube.com/watch?v=1\nhttps://youtube.com/watch?v=2"

        parsed_lbl = screen.query_one("#bucket-parsed-count", Label)
        assert "2 valid" in str(parsed_lbl.render())
        await pilot.press("escape")


@pytest.mark.anyio
async def test_playlist_validation_redirect_and_spawn():
    from ultratube_app import UltraTubeApp
    from app_screens import BucketScreen
    from models import BucketDownloadSettings
    from textual.widgets import TabbedContent, TabPane

    app = UltraTubeApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        # Simulate validation callback yielding a playlist
        playlist_data = {
            "type": "playlist",
            "info": {
                "title": "My Test Playlist",
                "entries": [
                    {"url": "https://youtube.com/watch?v=1"},
                    {"url": "https://youtube.com/watch?v=2"},
                ]
            }
        }

        # We trigger handle_validation_result on pane-1 (which is the default new tab spawned on mount)
        app.handle_validation_result("1", True, None, playlist_data)
        await pilot.pause()

        # Verify it pushed BucketScreen
        assert isinstance(app.screen, BucketScreen)
        assert app.screen.prefilled_urls == ["https://youtube.com/watch?v=1", "https://youtube.com/watch?v=2"]

        # Dismiss with settings
        settings = BucketDownloadSettings(
            urls=["https://youtube.com/watch?v=1", "https://youtube.com/watch?v=2"],
            is_audio=True,
            format="mp3",
            quality="highest",
            out_dir="C:/downloads",
        )
        await app.screen.dismiss(settings)
        await pilot.pause()

        # The screen stack is back to default
        assert app.screen == app.screen_stack[0]

        # The tabs should contain pane-2 and pane-3 (spawns 2, 3 as standard download tabs, pane-1 is removed)
        tabs_view = app.query_one("#tabs-view", TabbedContent)
        assert tabs_view.tab_count == 2

        # The IDs of tabs should correspond to sub-tab counter
        panes = list(tabs_view.query(TabPane))
        tab_ids = [pane.id for pane in panes]
        assert "pane-1" not in tab_ids
        assert "pane-2" in tab_ids
        assert "pane-3" in tab_ids
