# UltraTube — Sprints & Tickets

---

## Sprint 1 — Foundation & Packaging
**Weeks 1–2** · Goal: app installs cleanly, static-ffmpeg replaces system FFmpeg, URL validation implemented

| ID | Type | Title | Points | Priority |
|----|------|-------|--------|----------|
| UT-001 | refactor | Replace system FFmpeg with `static-ffmpeg` | 3 | High |
| UT-002 | chore | Add `pyproject.toml` and pip entry point | 2 | High |
| UT-003 | feat | Implement `is_valid_url()` in `UltraTubeExtractor` | 3 | High |

**Sprint total: 8 points**

---

### UT-001 · Replace system FFmpeg with `static-ffmpeg`
**Type:** refactor | **Points:** 3 | **Priority:** High | **Depends on:** none

FileService resolves the bundled binary path on first use; no system FFmpeg install required.

**Acceptance criteria:**
- Add `static-ffmpeg` to `requirements.txt`
- Add `_get_ffmpeg_path()` to `FileService` — calls `static_ffmpeg.add_paths()` on first use
- Replace all hardcoded `"ffmpeg"` strings in `_run_ffmpeg_command()` with the resolved path
- Pass the resolved path into yt-dlp's `ffmpeg_location` option in `DownloadService`
- Remove FFmpeg from installation prerequisites in README

---

### UT-002 · Add `pyproject.toml` and pip entry point
**Type:** chore | **Points:** 2 | **Priority:** High | **Depends on:** UT-001

`pip install ultratube` installs successfully and the `ultratube` command works in the terminal.

**Acceptance criteria:**
- Create `pyproject.toml` with `[project]`, `[project.scripts]`, and `[build-system]` sections
- Register entry point: `ultratube = ultratube_app:main`
- Pin all runtime deps (yt-dlp, static-ffmpeg, textual, rich) with minimum versions
- Verify `pip install -e .` works in a clean virtualenv
- Test `ultratube --help` after install

---

### UT-003 · Implement `is_valid_url()` in `UltraTubeExtractor`
**Type:** feat | **Points:** 3 | **Priority:** High | **Depends on:** none

Two-layer check: syntax (regex) then semantic (yt-dlp probe). Returns a typed result so the TUI can show a human-readable reason on failure.

**Acceptance criteria:**
- Layer 1 — regex: match `youtube.com/watch`, `youtu.be/`, `youtube.com/playlist`, `youtube.com/shorts`
- Layer 2 — call `MetadataService.get_video_info()` in a try/except; return False on `ValueError`
- Return type: `tuple[bool, Optional[str]]` — the string is the human-readable error reason
- Unit tests: valid URL, malformed URL, private video URL, playlist URL

---

## Sprint 2 — TUI Shell & Navigation
**Weeks 3–4** · Goal: Textual app launches with header, footer, help overlay, and keyboard navigation

| ID | Type | Title | Points | Priority |
|----|------|-------|--------|----------|
| UT-004 | feat | Scaffold Textual app shell (`UltraTubeApp`) | 3 | High |
| UT-005 | feat | Add `HelpOverlay` widget (F1 toggle) | 2 | Medium |
| UT-006 | feat | Build `MainTabView` with multi-tab support | 5 | High |
| UT-007 | chore | Remove legacy `ultratube_main.py` CLI loop | 1 | Medium |

**Sprint total: 11 points**

---

### UT-004 · Scaffold Textual app shell (`UltraTubeApp`)
**Type:** feat | **Points:** 3 | **Priority:** High | **Depends on:** UT-002

App launches with a persistent header and footer; all global keybindings are registered.

**Acceptance criteria:**
- Create `ultratube_app.py` with `class UltraTubeApp(App)`
- Add persistent `Header` (app name + version) and `Footer` (key hint bar)
- Register global keybindings: Q to quit, F1 for help, Ctrl+T new tab, Ctrl+W close tab, Ctrl+Tab / Ctrl+Shift+Tab to cycle tabs
- Update entry point in `pyproject.toml` to launch `UltraTubeApp`
- Smoke test: app opens, Ctrl+C exits cleanly

---

### UT-005 · Add `HelpOverlay` widget (F1 toggle)
**Type:** feat | **Points:** 2 | **Priority:** Medium | **Depends on:** UT-004

Full keybinding reference rendered as a Rich table; dismissed with F1 or Escape.

**Acceptance criteria:**
- Build overlay as a Textual `Screen` or floating `Widget`
- Render keybinding table using Rich `Table`: Key | Action columns
- F1 and Escape both dismiss the overlay
- Overlay content is data-driven from a dict so it stays in sync with actual bindings

---

### UT-006 · Build `MainTabView` with multi-tab support
**Type:** feat | **Points:** 5 | **Priority:** High | **Depends on:** UT-004

Ctrl+T opens new tabs, Ctrl+W closes the current tab, Ctrl+Tab cycles between them.

**Acceptance criteria:**
- Use Textual's `TabbedContent` as the base
- Each tab has an ID, a label (default "New tab"), and a `TabStatus` indicator
- Enforce configurable max concurrent tabs (default: 4)
- Closing the last tab shows an empty-state prompt rather than crashing
- Tab label updates to the video title once metadata is fetched

---

### UT-007 · Remove legacy `ultratube_main.py` CLI loop
**Type:** chore | **Points:** 1 | **Priority:** Medium | **Depends on:** UT-004

All service, model, and extractor code is preserved; only the print-based UI loop is removed.

**Acceptance criteria:**
- Archive `ultratube_main.py` in a `legacy/` folder for reference
- Confirm no service file imports from `ultratube_main`
- Delete all `print()` / `input()` UI code from the main module

---

## Sprint 3 — Download Tab & URL Validation UX
**Weeks 5–6** · Goal: full single-download flow works end-to-end in the TUI

| ID | Type | Title | Points | Priority |
|----|------|-------|--------|----------|
| UT-008 | feat | URL input widget with inline validation feedback | 5 | High |
| UT-009 | feat | Build `OptionsPanel` widget | 8 | High |
| UT-010 | feat | Async download worker per tab with `ProgressWidget` | 8 | High |
| UT-011 | feat | Playlist download support in TUI | 5 | Medium |

**Sprint total: 26 points**

---

### UT-008 · URL input widget with inline validation feedback
**Type:** feat | **Points:** 5 | **Priority:** High | **Depends on:** UT-003, UT-006

Calls `is_valid_url()` and shows an inline error label before unlocking the `OptionsPanel`.

**Acceptance criteria:**
- Text `Input` widget at the top of each `DownloadTab`
- On blur or Enter: run syntactic check immediately (sync), then kick off async semantic check with a spinner
- Show a red inline error label with the human-readable reason on failure
- On success: show green ✓ and the video title fetched from cache; unlock `OptionsPanel`
- Pasting a new URL resets the tab to idle state

---

### UT-009 · Build `OptionsPanel` widget
**Type:** feat | **Points:** 8 | **Priority:** High | **Depends on:** UT-008

All download options rendered as TUI widgets; locked until the URL validates.

**Acceptance criteria:**
- Panel is locked/greyed out until the URL validates successfully
- `Select` for output format (populated from `get_available_formats()`)
- `Select` for video quality (hidden in audio mode)
- `Select` for audio language track (populated from `get_audio_tracks()`)
- Subtitle multi-select (populated from `get_available_subtitles()`)
- Three `Switch` toggles: metadata, thumbnail, chapters
- Output directory `Input` with default `~/Downloads`

---

### UT-010 · Async download worker per tab with `ProgressWidget`
**Type:** feat | **Points:** 8 | **Priority:** High | **Depends on:** UT-009

Real-time percentage, speed, and ETA; each tab runs its worker independently without blocking others.

**Acceptance criteria:**
- Run download in a Textual `worker` (async thread) so the UI stays responsive
- Hook yt-dlp's `progress_hooks` to post `ProgressUpdate` messages to the tab
- `ProgressWidget` renders: Rich `ProgressBar`, speed label (MB/s), ETA label
- On completion: show file size, elapsed time, and update tab label to ✓
- On error: show error message, update tab label to ✗; tab stays open for retry
- On completion: display the GitHub star prompt message

---

### UT-011 · Playlist download support in TUI
**Type:** feat | **Points:** 5 | **Priority:** Medium | **Depends on:** UT-010

Detected playlist URL switches the tab to playlist mode with per-item and overall progress.

**Acceptance criteria:**
- URL validator detects playlist URLs and sets the tab mode accordingly
- Options panel shows a playlist-specific notice ("audio track uses best available per video")
- Progress widget shows: item N of M + overall progress bar
- Per-item failures are logged inline; the batch continues without stopping

---

## Sprint 4 — Queue Panel, Distribution & Polish
**Weeks 7–8** · Goal: history panel, pip publish, winget manifest, app stable and documented

| ID | Type | Title | Points | Priority |
|----|------|-------|--------|----------|
| UT-012 | feat | Build `DownloadQueuePanel` history sidebar | 5 | Medium |
| UT-013 | feat | Subtitle merge modal post-download | 3 | Medium |
| UT-014 | chore | Build PyInstaller executable for Windows | 5 | High |
| UT-015 | chore | Publish to PyPI + author WinGet manifest | 3 | High |
| UT-016 | chore | Final polish: TCSS theming, resize handling, README | 3 | Low |

**Sprint total: 19 points**

---

### UT-012 · Build `DownloadQueuePanel` history sidebar
**Type:** feat | **Points:** 5 | **Priority:** Medium | **Depends on:** UT-010

Session-scoped history panel showing all downloads with title, status badge, size, elapsed time, and output path.

**Acceptance criteria:**
- Fixed right or bottom panel using Textual `Horizontal` / `Vertical` layout
- Rich `Table` with columns: title, status, size, time
- Status badge colours: gray=queued, amber=downloading, green=done, red=failed
- Selecting a completed row copies the output path to clipboard
- Panel collapses to icon-only bar below 100 terminal columns

---

### UT-013 · Subtitle merge modal post-download
**Type:** feat | **Points:** 3 | **Priority:** Medium | **Depends on:** UT-010

Modal dialog offers merge and optional deletion of the original file; only appears when subtitles were downloaded.

**Acceptance criteria:**
- Appears only when subtitle files were downloaded alongside the media
- Textual `ModalScreen` with Yes / No / Skip buttons
- Merge runs in a background worker (calls `FileService.merge_subtitles()`)
- On success: offers a "Delete original?" second prompt

---

### UT-014 · Build PyInstaller executable for Windows
**Type:** chore | **Points:** 5 | **Priority:** High | **Depends on:** UT-002

Single-file `.exe` bundles Python, all dependencies, and the static-ffmpeg binaries.

**Acceptance criteria:**
- Add `pyinstaller` to dev dependencies
- Write a `ultratube.spec` file: one-file mode, include `static_ffmpeg` binaries
- CI step (GitHub Actions) builds the `.exe` on `windows-latest`
- Output uploaded as a GitHub release artifact
- Verify the installer runs on a clean Windows VM with no Python installed

---

### UT-015 · Publish to PyPI + author WinGet manifest
**Type:** chore | **Points:** 3 | **Priority:** High | **Depends on:** UT-014

`pip install ultratube` and `winget install UltraTube` both work end-to-end.

**Acceptance criteria:**
- Publish to PyPI via `twine` (CI triggered on version tag push)
- Create WinGet manifest YAML: `PackageIdentifier`, `InstallerUrl` pointing to the `.exe` from UT-014
- Submit manifest PR to `microsoft/winget-pkgs`
- Verify `winget install UltraTube` on a clean Windows machine
- Verify `winget upgrade UltraTube` picks up a bumped version

---

### UT-016 · Final polish: TCSS theming, resize handling, README
**Type:** chore | **Points:** 3 | **Priority:** Low | **Depends on:** all above

App looks clean at 80, 120, and 200 column widths; documentation is complete.

**Acceptance criteria:**
- Write `ultratube.tcss` Textual stylesheet: colours, spacing, focus ring
- Test layout at 80, 120, and 200 terminal columns
- Hide queue panel below 100 columns
- Write README: installation (pip + winget), usage, keyboard shortcuts
- Add `CHANGELOG.md` for v1.0.0

---

## Dependency Map

```
UT-001 ──► UT-002 ──► UT-004 ──► UT-006 ──► UT-008 ──► UT-009 ──► UT-010 ──► UT-012
                                                                         │         └──► UT-013
UT-003 ─────────────────────────────────────────────────────────────────┘
                        UT-004 ──► UT-005
                        UT-004 ──► UT-007
                                             UT-010 ──► UT-011
                        UT-002 ──► UT-014 ──► UT-015
```

**Critical path:** UT-001 → UT-002 → UT-004 → UT-006 → UT-008 → UT-009 → UT-010

---

## Total Points Summary

| Sprint | Points | Tickets |
|--------|--------|---------|
| Sprint 1 — Foundation & Packaging | 8 | 3 |
| Sprint 2 — TUI Shell & Navigation | 11 | 4 |
| Sprint 3 — Download Tab & UX | 26 | 4 |
| Sprint 4 — Queue, Distribution & Polish | 19 | 5 |
| **Total** | **64** | **16** |
