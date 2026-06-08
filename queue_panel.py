from textual.app import ComposeResult
from textual.widgets import Label, DataTable
from textual.containers import Vertical


class DownloadQueuePanel(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("Downloads Queue", classes="sidebar-title")
        table = DataTable(id="queue-table")
        table.add_columns("Title", "Status", "Size", "Time")
        yield table
