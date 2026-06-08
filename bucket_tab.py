import os
from typing import Dict, Any, List, Optional
from textual.app import ComposeResult
from textual.containers import Vertical, ScrollableContainer
from textual.widgets import Label, DataTable, ProgressBar
from models import DownloadRecord, TabStatus
from app_utils import format_size, format_speed, format_time


class BucketQueueTab(Vertical):
    """A single unified tab displaying a table of all downloads in a bucket batch."""

    def __init__(
        self,
        tab_id: str,
        urls: List[str],
        is_audio: bool,
        format_val: str,
        quality_val: str,
        out_dir: str,
    ):
        super().__init__(id=f"tab-{tab_id}")
        self.tab_id = tab_id
        self.urls = urls
        self.is_audio = is_audio
        self.format_val = format_val
        self.quality_val = quality_val
        self.out_dir = out_dir

        self.downloads: Dict[str, DownloadRecord] = {}
        # Map sub_id -> url
        self.sub_id_to_url: Dict[str, str] = {}
        # Map sub_id -> row_key
        self.row_keys: Dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        with ScrollableContainer(classes="tab-scroll-container"):
            # Header card showing aggregated progress
            with Vertical(
                classes="progress-container", id=f"bucket-header-{self.tab_id}"
            ):
                yield Label(
                    "Bulk Downloads Progress",
                    classes="progress-title",
                    id=f"bucket-progress-title-{self.tab_id}",
                )
                yield ProgressBar(
                    total=100,
                    show_percentage=True,
                    id=f"bucket-progress-bar-{self.tab_id}",
                )

            # Grid/Table for individual downloads
            yield Label("Downloading Items:", classes="group-label mt-1")
            table = DataTable(id=f"bucket-table-{self.tab_id}", classes="bucket-table")
            table.add_columns(
                "URL / Title", "Status", "Size", "Progress", "Speed", "ETA"
            )
            yield table

            # Log block console
            with Vertical(
                classes="log-container bucket-log-block", id=f"bucket-log-block-{self.tab_id}"
            ):
                yield Label("Bulk Download Log:", classes="log-title")
                yield ScrollableContainer(id=f"bucket-log-list-{self.tab_id}", classes="bucket-log-list")

    def on_mount(self) -> None:
        table = self.query_one(f"#bucket-table-{self.tab_id}", DataTable)
        for sub_id, record in self.downloads.items():
            url = self.sub_id_to_url[sub_id]
            # Add row to DataTable and store row_key
            row_key = table.add_row(
                url, "Pending", "—", "0%", "—", "—", key=sub_id
            )
            self.row_keys[sub_id] = row_key

    def update_download_progress(
        self,
        sub_id: str,
        percent: float,
        speed: float,
        eta: float,
        downloaded: int,
        total: int,
        filename: Optional[str] = None,
    ) -> None:
        try:
            table = self.query_one(f"#bucket-table-{self.tab_id}", DataTable)
            record = self.downloads.get(sub_id)
            if record:
                record.status = TabStatus.DOWNLOADING
                record.file_size = total
                record.eta = eta
                if filename and (
                    record.title == "Video" or record.title.startswith("http")
                ):
                    record.title = os.path.splitext(os.path.basename(filename))[0]

            title_text = (
                record.title if record else self.sub_id_to_url.get(sub_id, "Video")
            )
            if len(title_text) > 30:
                title_text = f"{title_text[:27]}..."

            table.update_cell(sub_id, "URL / Title", title_text)
            table.update_cell(sub_id, "Status", "Downloading")
            table.update_cell(sub_id, "Size", format_size(total) if total else "—")
            table.update_cell(sub_id, "Progress", f"{int(percent)}%")
            table.update_cell(sub_id, "Speed", format_speed(speed))
            table.update_cell(sub_id, "ETA", format_time(eta))

            self.update_overall_progress()
        except Exception:
            pass

    def update_download_finished(
        self, sub_id: str, filepath: str, size: int
    ) -> None:
        try:
            table = self.query_one(f"#bucket-table-{self.tab_id}", DataTable)
            record = self.downloads.get(sub_id)
            if record:
                record.status = TabStatus.DONE
                record.file_size = size
                record.output_path = filepath
                if record.title == "Video" or record.title.startswith("http"):
                    record.title = os.path.splitext(os.path.basename(filepath))[0]

            title_text = (
                record.title if record else self.sub_id_to_url.get(sub_id, "Video")
            )
            if len(title_text) > 30:
                title_text = f"{title_text[:27]}..."

            table.update_cell(sub_id, "URL / Title", title_text)
            table.update_cell(sub_id, "Status", "✓ Done")
            table.update_cell(sub_id, "Size", format_size(size) if size else "—")
            table.update_cell(sub_id, "Progress", "100%")
            table.update_cell(sub_id, "Speed", "—")
            table.update_cell(sub_id, "ETA", "—")

            self.update_overall_progress()
        except Exception:
            pass

    def update_download_error(self, sub_id: str, error_msg: str) -> None:
        try:
            table = self.query_one(f"#bucket-table-{self.tab_id}", DataTable)
            record = self.downloads.get(sub_id)
            if record:
                record.status = TabStatus.ERROR

            title_text = (
                record.title if record else self.sub_id_to_url.get(sub_id, "Video")
            )
            if len(title_text) > 30:
                title_text = f"{title_text[:27]}..."

            table.update_cell(sub_id, "URL / Title", title_text)
            table.update_cell(sub_id, "Status", "❌ Failed")
            table.update_cell(sub_id, "Progress", "—")
            table.update_cell(sub_id, "Speed", "—")
            table.update_cell(sub_id, "ETA", "—")

            self.update_overall_progress()
        except Exception:
            pass

    def update_log(self, sub_id: str, message: str) -> None:
        try:
            log_list = self.query_one(
                f"#bucket-log-list-{self.tab_id}", ScrollableContainer
            )
            record = self.downloads.get(sub_id)
            prefix = (
                f"[{record.title[:15] if record else sub_id}] " if sub_id else ""
            )
            log_list.mount(Label(f"{prefix}{message}"))
            log_list.scroll_end(animate=False)
        except Exception:
            pass

    def update_overall_progress(self) -> None:
        total_items = len(self.downloads)
        if total_items == 0:
            return

        finished_items = sum(
            1 for d in self.downloads.values() if d.status == TabStatus.DONE
        )
        failed_items = sum(
            1 for d in self.downloads.values() if d.status == TabStatus.ERROR
        )

        overall_pct = int((finished_items / total_items) * 100)

        pbar = self.query_one(
            f"#bucket-progress-bar-{self.tab_id}", ProgressBar
        )
        pbar.progress = overall_pct

        title = self.query_one(
            f"#bucket-progress-title-{self.tab_id}", Label
        )
        title.update(
            f"Bulk Downloads: {finished_items} done / {failed_items} failed / {total_items} total ({overall_pct}%)"
        )
