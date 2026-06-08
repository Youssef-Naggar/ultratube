# Graph Report - ultratube v2  (2026-06-09)

## Corpus Check
- 26 files · ~22,643 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 622 nodes · 987 edges · 38 communities (26 shown, 12 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 130 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a64f4611`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 41|Community 41]]

## God Nodes (most connected - your core abstractions)
1. `UltraTubeApp` - 66 edges
2. `UltraTubeExtractor` - 33 edges
3. `DownloadOptions` - 24 edges
4. `BucketScreen` - 21 edges
5. `MetadataService` - 20 edges
6. `DownloadRecord` - 20 edges
7. `TabStatus` - 19 edges
8. `HelpScreen` - 17 edges
9. `BucketQueueTab` - 16 edges
10. `FileService` - 16 edges

## Surprising Connections (you probably didn't know these)
- `MetadataService` --semantically_similar_to--> `DownloadService`  [INFERRED] [semantically similar]
  metadata_service.py → download_service.py
- `Project Dependencies` --references--> `DownloadService`  [INFERRED]
  requirements.txt → download_service.py
- `Sprints & Tickets` --cites--> `FileService`  [EXTRACTED]
  sprints_and_tickets.md → file_service.py
- `Project Dependencies` --references--> `FileService`  [INFERRED]
  requirements.txt → file_service.py
- `PlantUML Architecture Diagram` --cites--> `UltraTubeApp`  [EXTRACTED]
  ultratube-plantuml.txt → ultratube_app.py

## Hyperedges (group relationships)
- **TUI View Architecture** — ultratube_app_ultratubeapp, ultratube_app_downloadtab, ultratube_app_downloadqueuepanel, ultratube_app_helpscreen, ultratube_app_questionmodal [EXTRACTED 1.00]
- **Facade Pattern Coordination Flow** — ultratube_extractor_ultratubeextractor, metadata_service_metadataservice, download_service_downloadservice, file_service_fileservice [EXTRACTED 1.00]
- **Domain Data Modeling** — models_videoinfo, models_audiotrack, models_subtitle, models_downloadoptions, models_processoptions, models_downloadrecord [INFERRED 0.95]

## Communities (38 total, 12 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.17
Nodes (7): Helper to set the label of a tab dynamically and thread-safely., Helper to set the label of a tab dynamically and thread-safely., Helper to set the label of a tab dynamically and thread-safely., Helper to set the label of a tab dynamically and thread-safely., Helper to set the label of a tab dynamically and thread-safely., Helper to set the label of a tab dynamically and thread-safely., Helper to set the label of a tab dynamically and thread-safely.

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (34): Enum, get_clean_language_name(), MetadataService, Gets a list of available formats for a given URL that are supported by the appli, Get video information for a YouTube URL.          Args:             url: YouTube, Get video information for a YouTube URL.          Args:             url: YouTube, Extracts information about a playlist, including a list of its video entries., Extracts information about a playlist, including a list of its video entries. (+26 more)

### Community 2 - "Community 2"
Cohesion: 0.18
Nodes (8): copy_to_clipboard(), Copies text to the system clipboard on Windows using standard CLI utility., Save settings to ~/.ultratube_settings.json., save_settings(), Configuration tab for modifying and saving global download preferences., SettingsTab, copy_to_clipboard(), Copies text to the system clipboard on Windows using standard CLI utility.

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (26): DownloadService, YtDlpLogger, FileService, MetadataService, AudioTrack, DownloadOptions, DownloadRecord, ProcessOptions (+18 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (31): 1. Architectural Overview, 2. File Directory, 3.1 TUI Layer (View / Controller), 3.2 Core Layer (Facade), 3.3 Services Layer, 3.4 Models Layer, 3. Layered Components Detail, 4. Concurrency & Thread-Safe UI Updates (+23 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (43): 1.1 Ubiquitous Language & Model Alignment, 1.2 Structural Building Blocks, 1.3 Strategic Boundary Enforcement, 2.1 The Micro-Cycle Execution Algorithm, 2.2 Test Separation & Clarity, 3.1 Vulnerability Class Defenses, 4.1 Diagnostic Checklist Rules, 5.1 The Required Security & Quality Toolchain (+35 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (28): 1. Existing Features (Current CLI), 2. New Features (Planned), 3. Updated PlantUML Architecture Diagram, 4. `requirements.txt`, 5. Feature Summary Table, code:plantuml (@startuml UltraTube Architecture (Updated Textual TUI Editio), code:text (# ── Core downloader ──────────────────────────────────────), UltraTube — User Stories & Feature Inventory (+20 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (24): code:block1 (UT-001 ──► UT-002 ──► UT-004 ──► UT-006 ──► UT-008 ──► UT-00), Dependency Map, Sprint 1 — Foundation & Packaging, Sprint 2 — TUI Shell & Navigation, Sprint 3 — Download Tab & URL Validation UX, Sprint 4 — Queue Panel, Distribution & Polish, Total Points Summary, UltraTube — Sprints & Tickets (+16 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (36): code:block10 (Could not connect to YouTube. Check your internet connection), code:block11 (✓  {video title}), code:block12 (What do you want to download?), code:block13 (Audio format), code:block14 (Audio language), code:block15 (Default track (only one available)), code:block16 (Download subtitles  (optional)), code:block17 (No subtitles available for this video) (+28 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (45): Message, DownloadErrorMsg, DownloadFinished, DownloadProgress, LogMsg, PlaylistFinished, PlaylistProgress, run_download_thread() (+37 more)

### Community 10 - "Community 10"
Cohesion: 0.04
Nodes (45): App-Level Messages, code:block1 (UltraTube  v1.0.0), code:block2 (Ctrl+T New tab    Ctrl+W Close tab    Ctrl+Tab Next    F1 He), code:block28 (Video quality), code:block29 (Embed chapters), code:block3 (No downloads yet.), code:block30 (Download video), code:block31 (Downloading video...) (+37 more)

### Community 11 - "Community 11"
Cohesion: 0.20
Nodes (8): Download video from a URL.          Args:             url: URL to download from, Download video from a URL.          Args:             url: URL to download from, Download video from a URL.          Args:             url: URL to download from, Download video from a URL.          Args:             url: URL to download from, Download subtitles as .vtt files for a given URL.          Args:             url, Download subtitles as .vtt files for a given URL.          Args:             url, Download subtitles as .vtt files for a given URL.          Args:             url, Download subtitles as .vtt files for a given URL.          Args:             url

### Community 21 - "Community 21"
Cohesion: 0.07
Nodes (25): BaseModel, str, BucketModal, BucketScreen, Modal screen for pasting multiple URLs and download options., Full-screen dashboard for pasting multiple URLs and configuring bulk download op, BucketDownloadSettings, Configuration settings for a bulk download bucket. (+17 more)

### Community 24 - "Community 24"
Cohesion: 0.15
Nodes (11): format_size(), format_speed(), format_time(), Helper to format file size., Helper to format speed., Helper to format duration/ETA., BucketQueueTab, A single unified tab displaying a table of all downloads in a bucket batch. (+3 more)

### Community 25 - "Community 25"
Cohesion: 0.13
Nodes (15): App quit with active downloads, code:block45 (A file named {filename} already exists in {directory}.), code:block46 (⚠  Low disk space — {x.x MB} remaining in {directory}.), code:block47 (Cancel this download?), code:block48 (Download cancelled.), code:block49 (UltraTube only supports YouTube URLs (youtube.com and youtu.), code:block50 (ℹ  A newer version of yt-dlp is available. Run  pip install ), code:block51 ({N} download(s) still in progress.) (+7 more)

### Community 26 - "Community 26"
Cohesion: 0.15
Nodes (11): FileService, Clean up temporary files.                  Args:             files: List of file, Clean up temporary files.          Args:             files: List of file paths t, Resolve the absolute path to the FFmpeg binary.         Works in development and, Resolve the absolute path to the FFmpeg binary.         Works in development and, Service for file operations related to media processing., Run an FFmpeg command.                  Args:             command: FFmpeg comman, Run an FFmpeg command.          Args:             command: FFmpeg command as a l (+3 more)

### Community 27 - "Community 27"
Cohesion: 0.10
Nodes (9): DownloadTab, Hides the options, progress, and logs, and displays the GitHub star panel., Resets the tab to the idle state to allow another download., Hides the options, progress, and logs, and displays the GitHub star panel., Resets the tab to the idle state to allow another download., Hides the options, progress, and logs, and displays the GitHub star panel., Resets the tab to the idle state to allow another download., DownloadQueuePanel (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.14
Nodes (11): QuestionModal, Standard Yes/No dialog screen., Standard Yes/No dialog screen., Standard Yes/No dialog screen., Triggers the GitHub star suggestion panel on the specified tab., Triggers the GitHub star suggestion panel on the specified tab., Triggers the GitHub star suggestion panel on the specified tab., Triggers the GitHub star suggestion panel on the specified tab. (+3 more)

### Community 30 - "Community 30"
Cohesion: 0.18
Nodes (7): ModalScreen, HelpScreen, Overlay displaying application keyboard shortcuts., Overlay displaying application keyboard shortcuts., Overlay displaying application keyboard shortcuts., HelpScreen, Overlay displaying application keyboard shortcuts.

### Community 31 - "Community 31"
Cohesion: 0.24
Nodes (3): Full-screen dashboard for modifying and saving global download preferences., SettingsScreen, test_settings_screen_rendering()

### Community 32 - "Community 32"
Cohesion: 0.22
Nodes (7): DownloadService, Service for downloading media from YouTube and other platforms., Service for downloading media from YouTube and other platforms., Initialize the download service.          Args:             metadata_service: Se, Initialize the download service.          Args:             metadata_service: Se, Initialize the YouTube extractor with its required services., Initialize the YouTube extractor with its required services.

### Community 33 - "Community 33"
Cohesion: 0.25
Nodes (3): Redirects yt-dlp logs to our TUI logs., Redirects yt-dlp logs to our TUI logs., YtDlpLogger

### Community 34 - "Community 34"
Cohesion: 0.33
Nodes (4): make_progress_hook(), Creates a hook for yt-dlp to report progress back to a callback., Download audio from a URL.          Args:             url: URL to download from, Download audio from a URL.          Args:             url: URL to download from

### Community 35 - "Community 35"
Cohesion: 0.33
Nodes (5): FileService: Handles file operations for the YouTube downloader., ProcessOptions, Options for processing media files., Options for processing media files., Options for processing media files.

## Knowledge Gaps
- **154 isolated node(s):** `code:mermaid (graph TD)`, `2. File Directory`, ``UltraTubeApp` (in `ultratube_app.py`)`, ``DownloadTab` (in `download_tab.py`)`, ``BucketQueueTab` (in `bucket_tab.py`)` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `UltraTubeApp` connect `Community 29` to `Community 0`, `Community 2`, `Community 36`, `Community 9`, `Community 21`, `Community 24`, `Community 27`, `Community 28`, `Community 30`, `Community 31`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Why does `UltraTubeExtractor` connect `Community 9` to `Community 32`, `Community 1`, `Community 21`, `Community 23`, `Community 26`, `Community 27`, `Community 29`, `Community 30`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `MetadataService` connect `Community 1` to `Community 32`, `Community 33`, `Community 34`, `Community 9`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `UltraTubeApp` (e.g. with `DownloadTab` and `SettingsScreen`) actually correct?**
  _`UltraTubeApp` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `UltraTubeExtractor` (e.g. with `DownloadTab` and `UltraTubeApp`) actually correct?**
  _`UltraTubeExtractor` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `str` (e.g. with `.on_select_changed()` and `.submit_settings()`) actually correct?**
  _`str` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `DownloadOptions` (e.g. with `YtDlpLogger` and `DownloadService`) actually correct?**
  _`DownloadOptions` has 13 INFERRED edges - model-reasoned connections that need verification._