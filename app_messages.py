from typing import Optional
from textual.message import Message


class DownloadProgress(Message):
    def __init__(
        self,
        tab_id: str,
        percent: float,
        speed: float,
        eta: float,
        downloaded: int,
        total: int,
        filename: Optional[str] = None,
    ):
        super().__init__()
        self.tab_id = tab_id
        self.percent = percent
        self.speed = speed
        self.eta = eta
        self.downloaded = downloaded
        self.total = total
        self.filename = filename



class DownloadFinished(Message):
    def __init__(self, tab_id: str, filepath: str, size: int):
        super().__init__()
        self.tab_id = tab_id
        self.filepath = filepath
        self.size = size


class DownloadErrorMsg(Message):
    def __init__(self, tab_id: str, error_msg: str):
        super().__init__()
        self.tab_id = tab_id
        self.error_msg = error_msg


class LogMsg(Message):
    def __init__(self, tab_id: str, message: str):
        super().__init__()
        self.tab_id = tab_id
        self.message = message


class PlaylistProgress(Message):
    def __init__(self, tab_id: str, current_idx: int, total: int, current_title: str):
        super().__init__()
        self.tab_id = tab_id
        self.current_idx = current_idx
        self.total = total
        self.current_title = current_title


class PlaylistFinished(Message):
    def __init__(
        self,
        tab_id: str,
        downloaded: int,
        skipped: int,
        total: int,
        total_size: int,
        directory: str,
    ):
        super().__init__()
        self.tab_id = tab_id
        self.downloaded = downloaded
        self.skipped = skipped
        self.total = total
        self.total_size = total_size
        self.directory = directory
