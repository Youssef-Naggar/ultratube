# UltraTube — TUI Menu Messages & User Flows

All messages shown in the TUI interface, organized by screen and flow. Every string listed here is a candidate for a constants file (e.g. `messages.py`) to keep the UI copy in one place.

---

## App-Level Messages

### Header
```
UltraTube  v1.0.0
```

### Footer (key hints — always visible)
```
Ctrl+T New tab    Ctrl+W Close tab    Ctrl+Tab Next    F1 Help    Q Quit
```

### Empty state (no tabs open)
```
No downloads yet.
Press Ctrl+T to open a new tab and start downloading.
```

---

## Help Overlay (F1)

### Title
```
Keyboard shortcuts
```

### Keybinding table

| Key | Action |
|-----|--------|
| `Ctrl+T` | Open a new download tab |
| `Ctrl+W` | Close the current tab |
| `Ctrl+Tab` | Next tab |
| `Ctrl+Shift+Tab` | Previous tab |
| `Enter` | Confirm / start download |
| `Escape` | Cancel / dismiss overlay |
| `F1` | Toggle this help screen |
| `Q` | Quit UltraTube |

### Dismiss hint
```
Press F1 or Escape to close
```

---

## Tab Labels & Status Indicators

| State | Tab label format |
|-------|-----------------|
| Idle (no URL yet) | `New tab` |
| Validating URL | `Checking...` |
| URL invalid | `New tab  ✗` |
| Metadata fetched | `{video title}` |
| Downloading | `{video title}  ↓` |
| Complete | `{video title}  ✓` |
| Error | `{video title}  ✗` |
| Playlist mode | `{playlist title}  ↓` |

---

## Flow 1 — Single Audio Download

### Step 1 · URL input
```
Enter a YouTube URL to get started
```
*(placeholder text inside the input field)*

#### Validating (spinner shown)
```
Checking URL...
```

#### Validation failed — not a YouTube URL
```
That doesn't look like a YouTube URL. Please enter a link from youtube.com or youtu.be.
```

#### Validation failed — video unavailable
```
Could not reach this video. It may be private, deleted, or region-restricted.
```

#### Validation failed — network error
```
Could not connect to YouTube. Check your internet connection and try again.
```

#### Validation passed
```
✓  {video title}
```
*(green label appears below the input; OptionsPanel unlocks)*

---

### Step 2 · Options Panel — Audio mode

**Mode selector prompt:**
```
What do you want to download?
```
Options: `Audio` · `Video`

**Format selector prompt:**
```
Audio format
```
Options populated from `get_available_formats()` — e.g. `mp3  ·  m4a  ·  wav  ·  flac`

**Audio track selector prompt:**
```
Audio language
```
Options populated from `get_audio_tracks()` — e.g. `English (m4a, 128k)  ·  Arabic (m4a, 128k) [dubbed]`

If no alternate tracks exist:
```
Default track (only one available)
```

**Subtitle selector prompt:**
```
Download subtitles  (optional)
```
Options populated from `get_available_subtitles()` — e.g. `English  ·  Arabic  ·  English (auto-generated)`

If no subtitles available:
```
No subtitles available for this video
```

**Toggle labels:**
```
Embed metadata
Embed thumbnail
```
*(chapters toggle hidden in audio mode)*

**Output directory prompt:**
```
Save to
```
Default value: `~/Downloads`

**Start button:**
```
Download audio
```

---

### Step 3 · Downloading

```
Downloading audio...

{Rich ProgressBar}

  Speed    {x.x MB/s}
  ETA      {m:ss}
  Size     {x.x MB} / {total MB}
```

---

### Step 4 · Download complete

```
✓  Download complete

  File     {filename}.{ext}
  Saved to {output_directory}
  Size     {x.x MB}
  Time     {elapsed}s
```

**GitHub star prompt** *(shown after every successful download)*:
```
Enjoying UltraTube? Please consider giving it a ⭐ on GitHub — it helps a lot!
→  github.com/your-username/ultratube
```

---

### Step 4a · Subtitle merge prompt (modal — only when subtitles were downloaded)

```
Subtitles downloaded

{N} subtitle file(s) are ready. Would you like to embed them into the media file?

  [ Merge subtitles ]   [ Skip ]
```

#### Merging in progress
```
Merging subtitles...
```

#### Merge complete
```
✓  Subtitles merged into {filename_with_subs}.{ext}

Delete the original file without subtitles?

  [ Yes, delete ]   [ Keep both ]
```

#### Merge failed
```
Could not merge subtitles. The original file has been kept.
{error reason}
```

---

## Flow 2 — Single Video Download

Identical to Flow 1 except for the following differences in the Options Panel:

**Mode selected:** `Video`

**Quality selector prompt:**
```
Video quality
```
Options: `Highest available  ·  1080p  ·  720p  ·  480p  ·  360p  ·  240p`

**Chapters toggle** (video only):
```
Embed chapters
```

**Start button:**
```
Download video
```

**Downloading message:**
```
Downloading video...
```

**Complete message — same as audio, file extension reflects video container.**

---

## Flow 3 — Playlist Download

### Step 1 · URL input (playlist detected)

After validation passes and a playlist URL is detected:
```
✓  Playlist: {playlist title}
   {N} videos
```
*(options panel unlocks in playlist mode)*

---

### Step 2 · Options Panel — Playlist mode

All options are the same as single-file mode with one additional notice:

**Audio track notice:**
```
ℹ  Audio track — best available will be chosen for each video individually
```

**Subtitle notice:**
```
ℹ  Subtitle selection is based on the first video. Not all videos may have the selected languages.
```

**Output directory notice:**
```
Files will be saved in:  {output_directory}/{playlist_title}/
```

**Start button:**
```
Download playlist
```

---

### Step 3 · Downloading playlist

```
Downloading playlist: {playlist title}

  Video {N} of {total}:  {current video title}

  {Rich ProgressBar — current video}

  Speed    {x.x MB/s}
  ETA      {m:ss}

  Overall  {Rich ProgressBar — N/total}
```

**Per-video completion inline log:**
```
✓  {video title}  ({x.x MB})
```

**Per-video failure inline log:**
```
✗  {video title}  — skipped: {reason}
```

---

### Step 4 · Playlist download complete

```
✓  Playlist download complete

  Saved     {N} of {total} videos
  Skipped   {X} videos  (see log above)
  Saved to  {output_directory}/{playlist_title}/
  Total     {x.x MB}
  Time      {elapsed}
```

**GitHub star prompt** *(same as single-file flow)*:
```
Enjoying UltraTube? Please consider giving it a ⭐ on GitHub — it helps a lot!
→  github.com/your-username/ultratube
```

---

## Flow 4 — Concurrent Downloads (Multi-Tab)

No special messages beyond what is shown per-tab. The queue panel sidebar shows the combined view:

### Queue panel header
```
Downloads
```

### Queue panel row format

| Title | Status | Size | Time |
|-------|--------|------|------|
| {video title} | Queued | — | — |
| {video title} | Downloading ↓ | {x.x MB} / {total} | {elapsed} |
| {video title} | ✓ Done | {x.x MB} | {elapsed}s |
| {video title} | ✗ Failed | — | — |

### Max tabs reached
```
Maximum of 4 concurrent downloads reached.
Close a tab to open a new one.
```

### Copying output path (on row select)
```
Path copied to clipboard
```

---

## Error & Edge Case Messages

### File already exists
```
A file named {filename} already exists in {directory}.
Overwrite it, or choose a different output folder.

  [ Overwrite ]   [ Change folder ]   [ Cancel ]
```

### Disk space warning (less than 500 MB free)
```
⚠  Low disk space — {x.x MB} remaining in {directory}.
The download may fail if space runs out.

  [ Continue anyway ]   [ Cancel ]
```

### Download interrupted by user (Escape during download)
```
Cancel this download?

  [ Yes, cancel ]   [ Keep going ]
```

### Download cancelled
```
Download cancelled.
The partial file has been removed.
```

### Unsupported URL (not YouTube)
```
UltraTube only supports YouTube URLs (youtube.com and youtu.be).
```

### yt-dlp update available (shown once per session at startup)
```
ℹ  A newer version of yt-dlp is available. Run  pip install -U yt-dlp  to update.
```

### App quit with active downloads
```
{N} download(s) still in progress.
Quitting now will cancel them and delete any partial files.

  [ Quit anyway ]   [ Keep downloading ]
```

---

## Full Flow Summary

```
App launch
  └── Empty state: "Press Ctrl+T to start"
        └── Ctrl+T → New tab
              ├── Enter URL → Validating...
              │     ├── Invalid → Error label → (user corrects URL)
              │     └── Valid → ✓ Video title / Playlist title
              │           └── Options Panel unlocks
              │                 ├── Select mode: Audio / Video
              │                 ├── Select format
              │                 ├── Select quality (video only)
              │                 ├── Select audio track
              │                 ├── Select subtitles (optional)
              │                 ├── Toggle metadata / thumbnail / chapters
              │                 ├── Set output directory
              │                 └── Press Enter → Download starts
              │                       ├── Progress bar: speed / ETA / size
              │                       ├── [Escape] → Cancel prompt
              │                       └── Complete
              │                             ├── ✓ Done message + file info
              │                             ├── ⭐ GitHub star prompt
              │                             └── [if subtitles] → Merge modal
              │                                   ├── Merge → ✓ Merged
              │                                   │     └── Delete original? → Yes / No
              │                                   └── Skip
              └── Ctrl+T → Another tab (concurrent download)
```
