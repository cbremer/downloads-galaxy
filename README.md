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

To scan a specific folder, pass it as an argument:

```bash
python3 downloads-server.py /path/to/folder
```

**Note:** If running from a different directory, either use the full path to the script:

```bash
python3 /path/to/downloads-galaxy/downloads-server.py /path/to/folder
```

Or change to the script's directory first:

```bash
cd /path/to/downloads-galaxy
python3 downloads-server.py /path/to/folder
```

More examples:

```bash
# Scan an external drive
python3 downloads-server.py /Volumes/MyDrive

# Use a different port
PORT=8001 python3 downloads-server.py /path/to/folder
```

### Open in Browser

Navigate to [http://localhost:8000](http://localhost:8000)

### Reindex

Click the **Reindex** button to rescan your folder and see any new or changed files.

## Requirements

- Python 3.x
- A modern web browser

## How It Works

The Python server scans the specified folder (or `~/Downloads` by default) and serves file metadata via a JSON API. The HTML page fetches this data and renders an interactive, animated visualization. No files are moved or modified - it's purely a viewer.

## License

MIT
