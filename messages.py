# UI Messages and Constants for UltraTube

APP_TITLE = "UltraTube"
APP_SUBTITLE = ""

FOOTER_KEYS = "Ctrl+T New tab  |  Ctrl+W Close tab  |  Ctrl+B Bucket  |  F1 Help  |  Q Quit"

EMPTY_STATE_MESSAGE = (
    "No active downloads.\n\n"
    "Press [bold cyan]Ctrl+T[/bold cyan] to open a new download tab and get started!"
)

HELP_TITLE = "Keyboard Shortcuts"

URL_INPUT_PLACEHOLDER = (
    "Enter video, audio, or playlist URL (e.g., YouTube, Vimeo, SoundCloud...)"
)
URL_INPUT_HELP = "Press Enter to validate the URL and fetch available formats."

VALIDATING_SPINNER = "Validating URL and fetching formats..."

ERROR_INVALID_URL = (
    "That doesn't look like a valid URL. Please check the address and try again."
)
ERROR_UNSUPPORTED_PLATFORM = (
    "Unsupported platform or website. yt-dlp does not support this link."
)
ERROR_ACCESS_DENIED = (
    "Could not reach this link. It may be private, deleted, or offline."
)
ERROR_NETWORK = (
    "Could not connect. Please check your internet connection and try again."
)

VALIDATION_SUCCESS = "✓ Metadata successfully loaded!"

MODE_SELECTOR_PROMPT = "Download Type"
FORMAT_SELECTOR_PROMPT = "Output Format"
QUALITY_SELECTOR_PROMPT = "Video Quality"
AUDIO_TRACK_PROMPT = "Audio Language Track"
SUBTITLE_SELECTOR_PROMPT = "Download Subtitles (Optional)"
SUBTITLE_NONE_AVAILABLE = "No subtitles available for this link"

TOGGLE_METADATA = "Embed Metadata"
TOGGLE_THUMBNAIL = "Embed Thumbnail"
TOGGLE_CHAPTERS = "Embed Chapters (Video only)"

OUTPUT_DIR_PROMPT = "Save to Folder"

DOWNLOAD_BUTTON_AUDIO = "Download Audio"
DOWNLOAD_BUTTON_VIDEO = "Download Video"
DOWNLOAD_BUTTON_PLAYLIST = "Download Playlist"

STAR_PROMPT = (
    "Enjoying UltraTube?\n"
    "Please consider giving it a ⭐ on GitHub — it helps a lot!\n"
    "→ [bold cyan]github.com/your-username/ultratube[/bold cyan]"
)
