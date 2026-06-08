import subprocess


def copy_to_clipboard(text: str) -> None:
    """Copies text to the system clipboard on Windows using standard CLI utility."""
    try:
        process = subprocess.Popen("clip", stdin=subprocess.PIPE, shell=True, text=True)
        process.communicate(input=text)
    except Exception:
        # Fallback if subprocess fails
        pass


def format_size(bytes_size: float) -> str:
    """Helper to format file size."""
    if not bytes_size:
        return "—"
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def format_speed(bytes_per_sec: float) -> str:
    """Helper to format speed."""
    if not bytes_per_sec:
        return "0.0 MB/s"
    mb = bytes_per_sec / (1024 * 1024)
    return f"{mb:.2f} MB/s"


def format_time(seconds: float) -> str:
    """Helper to format duration/ETA."""
    if not seconds:
        return "0:00"
    seconds_int = int(seconds)
    minutes, seconds_rem = divmod(seconds_int, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds_rem:02d}"
    return f"{minutes}:{seconds_rem:02d}"
