import pytest
from unittest.mock import MagicMock, patch
from ultratube_app import UltraTubeApp
from app_screens import HelpScreen, QuestionModal, BucketScreen
from settings_screen import SettingsScreen
from download_tab import DownloadTab
from textual.widgets import TabbedContent, Label, Input, Button, SelectionList, Switch


@pytest.mark.anyio
async def test_app_composition_and_mounting():
    app = UltraTubeApp()
    async with app.run_test():
        # Verify title and version headers are loaded
        assert app.title == "UltraTube"
        
        # Verify tabbed content layout is mounted
        tabs_view = app.query_one("#tabs-view", TabbedContent)
        assert tabs_view is not None
        assert tabs_view.tab_count == 1  # Mount action opens a tab automatically


@pytest.mark.anyio
async def test_app_tab_creation_and_removal_shortcuts():
    app = UltraTubeApp()
    async with app.run_test() as pilot:
        tabs_view = app.query_one("#tabs-view", TabbedContent)
        assert tabs_view.tab_count == 1

        # Press ctrl+t to create a new tab
        await pilot.press("ctrl+t")
        assert tabs_view.tab_count == 2
        assert tabs_view.active == "pane-2"

        # Press ctrl+w to close the active tab
        await pilot.press("ctrl+w")
        assert tabs_view.tab_count == 1
        assert tabs_view.active == "pane-1"


@pytest.mark.anyio
async def test_app_help_screen_toggle():
    app = UltraTubeApp()
    async with app.run_test() as pilot:
        # Press F1 to toggle help screen
        await pilot.press("f1")
        assert isinstance(app.screen, HelpScreen)

        # Press escape to dismiss help screen
        await pilot.press("escape")
        assert app.screen == app.screen_stack[0]  # back to main screen


@pytest.mark.anyio
async def test_app_settings_navigation():
    app = UltraTubeApp()
    async with app.run_test() as pilot:
        # Press ctrl+s to open settings
        await pilot.press("ctrl+s")
        assert isinstance(app.screen, SettingsScreen)

        # Cancel setting dialog
        await pilot.press("escape")
        assert app.screen == app.screen_stack[0]


@pytest.mark.anyio
async def test_app_bucket_modal_navigation():
    app = UltraTubeApp()
    async with app.run_test() as pilot:
        # Press ctrl+b to open bucket dashboard
        await pilot.press("ctrl+b")
        assert isinstance(app.screen, BucketScreen)

        # Cancel bucket dashboard
        await pilot.press("escape")
        assert app.screen == app.screen_stack[0]


@pytest.mark.anyio
async def test_app_handle_validation_result_failure():
    app = UltraTubeApp()
    async with app.run_test():
        # Setup validation result failure on tab 1
        app.handle_validation_result(
            tab_id="1",
            success=False,
            error_msg="Unsupported URL or platform",
            data=None
        )
        
        tab = app.query_one("#tab-1", DownloadTab)
        status_label = tab.query_one("#status-label-1", Label)
        
        assert "Unsupported URL or platform" in str(status_label.render())
        assert tab.status.value == "error"
