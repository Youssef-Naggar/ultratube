# UltraTube — User Stories & Feature Inventory

---

## 1. Existing Features (Current CLI)

### US-01 · Download Audio from a Single Video
**As a** user,  
**I want to** paste a YouTube URL and download its audio track,  
**so that** I can listen to it offline without video data.

**Acceptance criteria:**
- User provides a YouTube URL
- App fetches and displays available audio formats (mp3, m4a, wav, flac)
- User selects a format or accepts the default
- File is saved to the chosen output directory
- Filename is sanitized to be filesystem-safe

---

### US-02 · Download Video from a Single URL
**As a** user,  
**I want to** download a YouTube video at a chosen quality,  
**so that** I can watch it offline at the resolution I need.

**Acceptance criteria:**
- User selects from quality presets: highest, 1080p, 720p, 480p, 360p, 240p
- App maps quality to the best matching yt-dlp format selector
- Output is merged into the selected container (mp4, mkv, webm)
- File is saved to the chosen output directory

---

### US-03 · Select Output Format
**As a** user,  
**I want to** choose the output container/codec before downloading,  
**so that** the file is compatible with my player or workflow.

**Acceptance criteria:**
- For audio: choices are mp3, m4a, wav, flac (FFmpeg handles conversion)
- For video: only formats that the source actually has are shown
- A sensible default is pre-selected if the user skips

---

### US-04 · Select Audio Language Track
**As a** user,  
**I want to** pick a specific audio language track (e.g., dubbed version),  
**so that** I get the right language in the output file.

**Acceptance criteria:**
- App lists all available audio tracks with language name, codec, and bitrate
- User can pick one or accept the default track
- Selected language code is passed to the format selector in yt-dlp

---

### US-05 · Download Subtitles
**As a** user,  
**I want to** download subtitle tracks alongside the media,  
**so that** I can read along or share the file with captions.

**Acceptance criteria:**
- App lists all available subtitle tracks (manual and auto-generated, labelled)
- User can select one or more language codes (comma-separated in CLI)
- Subtitles are saved as `.vtt` files in the same output directory

---

### US-06 · Merge Subtitles into Media File
**As a** user,  
**I want to** embed downloaded subtitles directly into the media file,  
**so that** I have a single self-contained file with captions.

**Acceptance criteria:**
- After download, user is prompted whether to merge
- FFmpeg muxes the `.vtt` tracks into the container using `mov_text` codec
- Output is saved as `<title>_with_subs.<ext>`
- User is offered the option to delete the original un-merged file

---

### US-07 · Include Metadata
**As a** user,  
**I want to** embed video metadata (title, artist, description) into the file,  
**so that** my media library software picks it up automatically.

**Acceptance criteria:**
- Toggle on/off before downloading
- Uses yt-dlp's `FFmpegMetadata` post-processor

---

### US-08 · Include Thumbnail
**As a** user,  
**I want to** embed the video thumbnail into the file,  
**so that** the cover art appears in my media player.

**Acceptance criteria:**
- Toggle on/off before downloading
- Uses yt-dlp's `EmbedThumbnail` post-processor

---

### US-09 · Include Chapters
**As a** user,  
**I want to** embed chapter markers into downloaded videos,  
**so that** I can jump to sections in my media player.

**Acceptance criteria:**
- Toggle on/off before downloading (video only)
- Uses yt-dlp's `embedchapters` option

---

### US-10 · Download an Entire Playlist (Audio or Video)
**As a** user,  
**I want to** provide a playlist URL and download all its videos,  
**so that** I can archive or listen to a whole series offline.

**Acceptance criteria:**
- App fetches playlist metadata (title, video count, entries)
- Creates a subdirectory named after the playlist
- Applies the same format/quality/options to every video
- Reports per-video progress and handles individual failures gracefully without stopping the whole batch

---

### US-11 · Choose Output Directory
**As a** user,  
**I want to** specify where files are saved,  
**so that** downloads land in the right folder on my system.

**Acceptance criteria:**
- Default is `~/Downloads`
- User can override with any valid path
- Directory is created automatically if it does not exist

---

### US-12 · Metadata Caching
**As a** user,  
**I want** metadata for a URL to be fetched only once per session,  
**so that** repeated queries for the same video are fast.

**Acceptance criteria:**
- `MetadataService` caches raw info with a 1-hour TTL
- Second call for the same URL within TTL returns cached data immediately

---

## 2. New Features (Planned)

### US-13 · TUI Application Shell
**As a** user,  
**I want** a full-screen terminal user interface instead of a plain CLI prompt loop,  
**so that** the app is easier to navigate, visually clear, and feels modern.

**Acceptance criteria:**
- Built with **Textual** (layout, widgets, reactive state) and **Rich** (styled output, tables, progress bars)
- Has a persistent header with the app name and a footer with key bindings
- All interactions use keyboard navigation — no raw `input()` calls
- Responsive layout adapts to different terminal sizes

---

### US-14 · Multi-Tab Downloads (Concurrent Sessions)
**As a** user,  
**I want to** open multiple download tabs simultaneously,  
**so that** I can queue and run several downloads at the same time without waiting for each to finish.

**Acceptance criteria:**
- A "New Tab" action (e.g., `Ctrl+T`) opens a fresh download session tab
- Each tab is independent: its own URL, options, and progress state
- Tabs can be closed individually (`Ctrl+W`)
- Downloads in each tab run concurrently using `asyncio` workers
- A tab label shows the video title (or "New Tab") and a status indicator (idle / downloading / done / error)
- Maximum concurrent downloads is configurable (default: 4)

---

### US-15 · Real-Time Download Progress Bar
**As a** user,  
**I want to** see a live progress bar during a download,  
**so that** I know how far along it is and how fast it's going.

**Acceptance criteria:**
- Shows percentage complete, download speed (MB/s), and ETA
- Updates in real-time without blocking the UI (async download worker)
- Progress bar is rendered per-tab so multiple downloads are tracked separately
- On completion, shows final file size and elapsed time

---

### US-16 · Static FFmpeg (No System Dependency)
**As a** user,  
**I want** the app to use its own bundled FFmpeg binary,  
**so that** I don't have to install FFmpeg separately on my system.

**Acceptance criteria:**
- Replaces `subprocess` FFmpeg calls with **`static-ffmpeg`** (PyPI package)
- `static-ffmpeg` auto-downloads the correct platform binary on first run
- `FileService` and `DownloadService` use the binary path returned by `static_ffmpeg.add_paths()`
- Installation instructions do not mention FFmpeg as a prerequisite

---

### US-17 · Install via pip
**As a** developer or power user,  
**I want to** install UltraTube with a single `pip install` command,  
**so that** I can get it running immediately in any Python environment.

**Acceptance criteria:**
- Project has a `pyproject.toml` (or `setup.py`) with all dependencies declared
- Entry point registered so `ultratube` runs from the terminal after install
- All dependencies (yt-dlp, textual, rich, static-ffmpeg) are pinned in `requirements.txt`

---

### US-18 · Install via winget (Windows)
**As a** Windows user,  
**I want to** install UltraTube with `winget install UltraTube`,  
**so that** I don't need Python or pip knowledge to get started.

**Acceptance criteria:**
- A WinGet manifest (YAML) is published to the Windows Package Manager Community Repository
- The manifest wraps a self-contained installer (e.g., PyInstaller-built `.exe`)
- Installed binary is added to `PATH` automatically
- `winget upgrade UltraTube` works for future versions

---

### US-19 · Download Queue / History Panel
**As a** user,  
**I want to** see all past and pending downloads in a side panel,  
**so that** I can track what has finished, what failed, and what is still in progress.

**Acceptance criteria:**
- Panel lists each download with: title (truncated), status badge, file size, and elapsed time
- Statuses: Queued · Downloading · Done ✓ · Failed ✗
- Clicking a completed item reveals the output file path
- Persists within the session (not across restarts in v1)

---

### US-20 · Keyboard-Driven Navigation
**As a** user,  
**I want** all app actions accessible via keyboard shortcuts,  
**so that** I can operate the app entirely without a mouse.

**Acceptance criteria:**

| Key | Action |
|-----|--------|
| `Ctrl+T` | New download tab |
| `Ctrl+W` | Close current tab |
| `Ctrl+Tab` | Next tab |
| `Ctrl+Shift+Tab` | Previous tab |
| `Enter` | Confirm / Start download |
| `Escape` | Cancel / Back |
| `F1` | Toggle help overlay |
| `Q` | Quit app |

---

## 3. Updated PlantUML Architecture Diagram

```plantuml
@startuml UltraTube Architecture (Updated Textual TUI Edition)

skinparam backgroundColor white
skinparam packageStyle rectangle
skinparam classFontSize 13
skinparam classFontName Arial
skinparam classAttributeFontSize 11
skinparam classAttributeFontName Arial

title UltraTube - YouTube Media Downloader Architecture

' ─────────────────────────────────────────────
package "TUI Layer (Modular - Textual App & Widgets)" {
  class UltraTubeApp << (F,orchid) ultratube_app.py >> {
    + extractor: UltraTubeExtractor
    + tab_counter: int
    + download_records: Dict[str, DownloadRecord]
    + cancelled_tabs: set
    + pending_merges: Dict[str, Tuple]
    + settings: AppSettings
    + compose()
    + on_mount()
    + set_tab_label(pane_id, label)
    + action_toggle_help()
    + action_settings()
    + action_new_tab()
    + action_close_tab()
    + action_bucket()
    + add_bucket_batch_downloads(settings)
    + add_bucket_download(url, ...)
    + on_button_pressed(event)
    + on_input_submitted(event)
    + validate_url_action(tab_id)
    + do_validate_url(tab_id, url)
    + handle_validation_result(tab_id, success, error_msg, data)
    + toggle_mode_ui(tab_id, val)
    + start_download_action(tab_id)
    + on_download_progress(message)
    + on_playlist_progress(message)
    + on_log_msg(message)
    + on_download_finished(message)
    + on_playlist_finished(message)
    + on_download_error_msg(message)
    + update_sidebar_queue(tab_id)
    + trigger_subtitle_merge_modal(tab_id)
    + do_merge_subtitles(tab_id, media_file, subtitle_files)
    + trigger_delete_original_modal(tab_id, ...)
    + prompt_github_star(tab_id)
    + handle_star_click(tab_id)
    + handle_star_skip(tab_id)
    + reset_tab_to_idle(tab_id)
    + on_data_table_row_selected(event)
  }

  class DownloadTab << (W,lightblue) download_tab.py >> {
    + tab_id: str
    + extractor: UltraTubeExtractor
    + url: Optional[str]
    + bucket_settings: Optional[Dict]
    + settings: Optional[AppSettings]
    + status: TabStatus
    + is_playlist: bool
    + playlist_info: Optional[Dict]
    + video_info: Optional[VideoInfo]
    + audio_formats: List
    + video_formats: List
    + audio_tracks: List
    + subtitle_tracks: List
    + compose()
    + update_status(text, status_class)
    + show_star_panel()
    + reset_to_idle()
    + on_mount()
  }

  class BucketQueueTab << (W,lightblue) bucket_tab.py >> {
    + tab_id: str
    + urls: List[str]
    + is_audio: bool
    + format_val: str
    + quality_val: str
    + out_dir: str
    + downloads: Dict[str, DownloadRecord]
    + sub_id_to_url: Dict[str, str]
    + row_keys: Dict[str, Any]
    + compose()
    + on_mount()
    + update_download_progress()
    + update_download_finished()
    + update_download_error()
    + update_log()
    + update_overall_progress()
  }

  class DownloadQueuePanel << (W,lightblue) queue_panel.py >> {
    + compose()
  }

  class HelpScreen << (S,lightgrey) app_screens.py >> {
    + compose()
    + on_key()
  }

  class QuestionModal << (S,lightgrey) app_screens.py >> {
    + dialog_title: str
    + dialog_text: str
    + yes_label: str
    + no_label: str
    + compose()
    + on_button_pressed()
  }

  class BucketScreen << (S,lightgrey) app_screens.py >> {
    + app_settings: Optional[AppSettings]
    + prefilled_urls: Optional[List[str]]
    + compose()
    + on_mount()
    + update_formats_dropdown(mode)
    + on_select_changed(event)
    + on_text_area_changed(event)
    + validate_urls_realtime()
    + action_cancel()
    + action_submit()
    + on_button_pressed(event)
    + submit_settings()
  }

  class SettingsScreen << (S,lightgrey) settings_screen.py >> {
    + settings: AppSettings
    + compose()
    + action_cancel()
    + action_submit()
    + on_button_pressed(event)
    + save_preferences_action()
  }

  class WorkerMessages << (M,gold) app_messages.py >> {
    + DownloadProgress
    + DownloadFinished
    + DownloadErrorMsg
    + LogMsg
    + PlaylistProgress
    + PlaylistFinished
  }

  class WorkerThreads << (T,lightgreen) app_workers.py >> {
    + run_download_thread()
    + run_playlist_download_thread()
  }
}

' ─────────────────────────────────────────────
package "Core" {
  class UltraTubeExtractor {
    - metadata_service: MetadataService
    - download_service: DownloadService
    - file_service: FileService
    + is_valid_url(url: str)
    + get_available_formats(url, is_audio)
    + get_audio_tracks(url)
    + get_available_subtitles(url)
    + get_playlist_info(url)
    + download_audio(url, options, ...)
    + download_video(url, quality, options, ...)
    + merge_subtitles(media_file, subtitle_files, ...)
  }
}

' ─────────────────────────────────────────────
package "Services" {
  class DownloadService {
    - metadata_service: MetadataService
    + download_audio(url, options, progress_callback, log_callback)
    + download_video(url, quality, options, progress_callback, log_callback)
    + download_subtitles(url, subtitle_ids, output_dir, log_callback)
  }

  class MetadataService {
    - _video_info_cache: Dict
    - _cache_timestamps: Dict
    - _cache_ttl: int
    - supported_audio_formats: List[str]
    - supported_video_formats: List[str]
    + get_available_formats(url, is_audio)
    + get_video_info(url)
    + get_playlist_info(url)
    + get_audio_tracks(url)
    + get_available_subtitles(url)
  }

  class FileService {
    + merge_subtitles(media_file, subtitle_files, output_file)
    + process_download(file_path, options)
    + cleanup_temp_files(files)
    + get_ffmpeg_path()
  }

  class YtDlpLogger << (C,lightyellow) download_service.py >> {
    + log_callback: callable
    + debug(message)
    + info(message)
    + warning(message)
    + error(message)
    + error(message)
  }
}

' ─────────────────────────────────────────────
package "Models" {
  class VideoInfo {
    + id: str
    + title: str
    + formats: List[Dict]
    + subtitles: Dict
    + duration: Optional[int]
    + thumbnail_url: Optional[str]
    + description: Optional[str]
    + filename_safe_title()
  }

  class AudioTrack {
    + language: str
    + format_id: str
    + description: str
    + language_code: Optional[str]
    + codec: Optional[str]
    + bitrate: Optional[int]
  }

  class Subtitle {
    + language: str
    + language_code: str
    + format_id: str
    + is_auto_generated: bool
  }

  class DownloadOptions {
    + output_directory: str
    + output_format: str
    + include_metadata: bool
    + include_thumbnail: bool
    + include_chapters: bool
    + audio_language_code: Optional[str]
    + subtitle_ids: List[str]
  }

  class ProcessOptions {
    + keep_original: bool
    + output_format: str
    + quality_level: Optional[int]
  }

  class DownloadRecord {
    + tab_id: str
    + title: str
    + status: TabStatus
    + file_size: Optional[int]
    + elapsed: Optional[float]
    + output_path: Optional[str]
    + eta: Optional[float]
  }

  class BucketDownloadSettings {
    + urls: List[str]
    + is_audio: bool
    + format: str
    + quality: str
    + out_dir: str
  }

  class AppSettings << (C,lightyellow) settings_service.py >> {
    + out_dir: str
    + default_mode: str
    + default_audio_format: str
    + default_video_format: str
    + default_quality: str
    + include_metadata: bool
    + include_thumbnail: bool
    + include_chapters: bool
  }

  enum TabStatus {
    IDLE
    FETCHING
    DOWNLOADING
    DONE
    ERROR
  }
}

' ─────────────────────────────────────────────
' Relationships

UltraTubeApp *-- "many" DownloadTab : creates (via TabbedContent)
UltraTubeApp *-- "many" BucketQueueTab : creates (via TabbedContent)
UltraTubeApp *-- DownloadQueuePanel : renders
UltraTubeApp ..> HelpScreen : pushes
UltraTubeApp ..> QuestionModal : pushes
UltraTubeApp ..> BucketScreen : pushes
UltraTubeApp ..> SettingsScreen : pushes
UltraTubeApp ..> WorkerMessages : listens to
UltraTubeApp --> UltraTubeExtractor : coordinates
UltraTubeApp --> AppSettings : holds & configures

UltraTubeExtractor *-- DownloadService
UltraTubeExtractor *-- MetadataService
UltraTubeExtractor *-- FileService

DownloadService --> MetadataService : uses
DownloadService --> DownloadOptions : uses
DownloadService --> YtDlpLogger : uses
FileService --> ProcessOptions : uses

MetadataService --> VideoInfo : returns
MetadataService --> AudioTrack : returns
MetadataService --> Subtitle : returns

DownloadQueuePanel --> DownloadRecord : displays table of
DownloadTab --> TabStatus : state tracking
DownloadTab ..> WorkerThreads : starts
DownloadTab --> AppSettings : references

BucketQueueTab *-- "many" DownloadRecord : manages & displays
BucketQueueTab --> TabStatus : state tracking

BucketScreen ..> BucketDownloadSettings : creates & returns
BucketScreen --> AppSettings : reads defaults from

SettingsScreen --> AppSettings : modifies & saves via settings_service

WorkerThreads ..> WorkerMessages : posts
WorkerThreads --> UltraTubeExtractor : uses

DownloadRecord --> TabStatus : state tracking
```

---

## 4. `requirements.txt`

```text
# ── Core downloader ──────────────────────────────────────
yt-dlp>=2024.11.18

# ── FFmpeg (bundled, no system install required) ─────────
static-ffmpeg>=2.5

# ── TUI framework ────────────────────────────────────────
textual>=0.80.0
rich>=13.9.0

# ── Dev / packaging (not installed by default) ───────────
# pyinstaller>=6.11.0   # for building the winget .exe
# build>=1.2.0          # for `python -m build`
# twine>=5.0.0          # for uploading to PyPI
```

---

## 5. Feature Summary Table

| # | Feature | Status |
|---|---------|--------|
| US-01 | Download audio (single URL) | ✅ Existing |
| US-02 | Download video (single URL) | ✅ Existing |
| US-03 | Select output format | ✅ Existing |
| US-04 | Select audio language track | ✅ Existing |
| US-05 | Download subtitles (.vtt) | ✅ Existing |
| US-06 | Merge subtitles into media file | ✅ Existing |
| US-07 | Embed metadata | ✅ Existing |
| US-08 | Embed thumbnail | ✅ Existing |
| US-09 | Embed chapters | ✅ Existing |
| US-10 | Playlist download | ✅ Existing |
| US-11 | Custom output directory | ✅ Existing |
| US-12 | Metadata caching (1h TTL) | ✅ Existing |
| US-13 | Textual + Rich TUI shell | 🆕 New |
| US-14 | Multi-tab concurrent downloads | 🆕 New |
| US-15 | Real-time per-tab progress bar | 🆕 New |
| US-16 | Bundled FFmpeg via static-ffmpeg | 🆕 New |
| US-17 | `pip install ultratube` | 🆕 New |
| US-18 | `winget install UltraTube` | 🆕 New |
| US-19 | Download queue / history panel | 🆕 New |
| US-20 | Full keyboard navigation | 🆕 New |
