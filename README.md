# UltraTube v1.0 Beta 📹
A powerful, feature-rich YouTube media downloader built in Python with a beautiful **Terminal User Interface (TUI)**.

> [!NOTE]
> This is the **v1.0-beta** branch of UltraTube, introducing a complete redesign from the CLI version to a modern, keyboard-driven terminal dashboard.

---

## 📋 Overview
UltraTube v1.0 Beta transitions the application from a linear command-line interface into a fully interactive terminal application built on [Textual](https://github.com/Textualize/textual). It allows you to search, configure, queue, and download YouTube videos and playlists concurrently with a sidebar download manager, custom tabs, settings panels, and an advanced batch "bucket" downloader.

---

## ✨ Key Features in v1.0 Beta

### 🖥️ Interactive Dashboard (TUI)
* **Tabbed Navigation**: Open multiple download tabs (`Ctrl+T`), work on different videos simultaneously, and close tabs (`Ctrl+W`) when done.
* **Real-time Queue Sidebar**: A dedicated sidebar showing active downloads, progress percentages, download speed, ETA, and file size.
* **Keyboard-Driven Shortcuts**: Navigate the interface with hotkeys (`Ctrl+S` for Settings, `Ctrl+B` for Bucket, `F1` for Help, `Q` to Quit).
* **Responsive Styling**: A premium dark-mode aesthetic defined with custom Textual CSS (`ultratube.tcss`).

### 📦 Batch "Bucket" Downloads
* Queue multiple URLs simultaneously in a batch.
* Configure global options (audio/video, output format, download directory) for the entire batch.
* Monitor batch progress with a dedicated unified status grid.

### ⚙️ Interactive Settings
* Custom output directory configuration.
* Default formats for both video and audio.
* Toggle default behavior for metadata tags, thumbnail embedding, and chapter extraction.

### 🛠️ Key Core Enhancements
* **Concurrent Download Workers**: Downloads run in the background on separate threads, preventing UI lockups.
* **Automatic Format Extraction**: Automatically queries and filters available formats, audio tracks (including dubbed languages), and subtitles.
* **Comprehensive Test Suite**: Included robust automated unit and TUI tests using `pytest`.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.8+
* **FFmpeg**: Must be installed and available in your system `PATH`.
  * **Windows**: Download from [ffmpeg.org](https://ffmpeg.org) and add the `bin` folder to your environment `PATH`.
  * **macOS**: `brew install ffmpeg`
  * **Linux**: `sudo apt install ffmpeg`

### Installation
1. Clone the repository and checkout the `v1.0-beta` branch:
   ```bash
   git clone https://github.com/Youssef-Naggar/ultratube.git
   cd ultratube
   git checkout v1.0-beta
   ```

2. Install the package dependencies (including `textual` and `yt-dlp`):
   ```bash
   pip install -r requirements.txt
   ```

### Running the App
Launch the TUI dashboard:
```bash
python ultratube_app.py
```

---

## ⌨️ Keyboard Shortcuts
* `Ctrl + T` - Open a new download tab.
* `Ctrl + W` - Close the active download tab.
* `Ctrl + B` - Open the Batch Bucket dialog.
* `Ctrl + S` - Open the Settings Screen.
* `F1` - Toggle the Help overlay.
* `Q` - Quit the application.

---

## 📊 Class Architecture
Refer to [ultratube-plantuml.txt](file:///c:/programming/projectes/ultratube%20v2/ultratube-plantuml.txt) in this directory for the complete UML class design diagram of the TUI application.

---

## 🧪 Running Tests
We have added a comprehensive test suite to verify the application. You can run all tests using:
```bash
pytest
```

---

## 🤝 Feedback & Contributions
We would love to hear your feedback on the v1.0 TUI redesign! Please feel free to open issues or submit Pull Requests in this branch. Once fully polished and stable, the `v1.0-beta` branch will be merged into the `main` branch.
