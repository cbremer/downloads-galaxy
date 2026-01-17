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

## Usage

### Start the Server

```bash
python3 downloads-server.py
```

### Open in Browser

Navigate to [http://localhost:8000](http://localhost:8000)

### Reindex

Click the **Reindex** button to rescan your Downloads folder and see any new or changed files.

## Requirements

- Python 3.x
- A modern web browser

## How It Works

The Python server scans your `~/Downloads` folder and serves file metadata via a JSON API. The HTML page fetches this data and renders an interactive, animated visualization. No files are moved or modified - it's purely a viewer.

## License

MIT
