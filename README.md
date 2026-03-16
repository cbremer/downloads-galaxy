# Downloads Galaxy

A space-themed visual file browser for your Downloads folder. View your files as constellations in a cosmic interface with live reindexing.

## Features

- **Cosmic UI** - Animated starfield background with orbital rings and twinkling stars
- **Category Constellations** - Files organized by folder, displayed as themed constellations
- **Color-coded File Types** - Videos (red), audio (teal), images (gold), documents (slate), installers (blue), archives (purple)
- **Size Indicators** - Visual bars showing relative file sizes
- **Interactive Hover Effects** - Glowing spotlight follows your cursor
- **Filter Buttons** - Show only specific file types
- **Live Reindexing** - Rescan your Downloads folder with one click
- **Desktop Prototype** - Tkinter-based native app prototype with folder picker, stats, and file table

## Usage

### Web App

Start the server:

```bash
python3 downloads-server.py
```

To scan a specific folder, pass it as an argument:

```bash
python3 downloads-server.py /path/to/folder
```

More examples:

```bash
# Scan an external drive
python3 downloads-server.py /Volumes/MyDrive

# Use a different port
PORT=8001 python3 downloads-server.py /path/to/folder
```

Open in browser: [http://localhost:8000](http://localhost:8000)

### Desktop Prototype

Launch the desktop app:

```bash
python3 downloads-desktop.py
```

Or index a different folder on launch:

```bash
python3 downloads-desktop.py /path/to/folder
```

Inside the desktop app:
- Use **Choose Folder** to pick a new folder.
- Click **Reindex** to refresh results.
- Select a folder constellation on the left to view files on the right.

## Desktop Migration Plan

A staged plan for taking this prototype to a production desktop release is documented in:

- `DESKTOP_APP_PLAN.md`

## Requirements

- Python 3.x
- For web mode: a modern web browser
- For desktop mode: Tkinter (included with most Python distributions)

## How It Works

The shared scanner module (`downloads_core.py`) indexes the target folder and classifies files. The web server (`downloads-server.py`) exposes that data as JSON and renders the HTML visualization. The desktop prototype (`downloads-desktop.py`) calls the same scanner logic directly to render a native UI. No files are moved or modified - it's purely a viewer.

## License

MIT
