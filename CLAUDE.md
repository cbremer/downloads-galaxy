# CLAUDE.md

This file provides context for Claude Code when working on this project.

## Project Overview

Downloads Galaxy is a space-themed visual file browser for the macOS Downloads folder. It consists of two files that work together:

## Architecture

### `downloads-server.py`
Python HTTP server that:
- Serves the HTML page at `/`
- Provides `/api/scan` endpoint that scans `~/Downloads` and returns JSON
- Recursively scans subfolders (up to 20 files shown per folder)
- Categorizes files by type (video, audio, image, document, archive, installer, data, code)
- Runs on port 8000

### `downloads-viewer.html`
Single-page HTML/CSS/JS application that:
- Fetches data from `/api/scan` on load and when "Reindex" is clicked
- Renders folders as "constellations" with files as "celestial bodies"
- Includes animated starfield background, hover effects, and filter buttons
- Shows server connection status in bottom-right corner
- Works standalone (shows error message if server not running)

## Key Design Decisions

- **Read-only**: Never modifies or moves files
- **Self-contained**: No external dependencies beyond Python stdlib
- **macOS focused**: Assumes `~/Downloads` path structure

## Common Tasks

### Adding a new file type
1. Add extension to `FILE_CATEGORIES` dict in `downloads-server.py`
2. Add icon mapping in `get_file_icon()` function
3. Optionally add CSS styles for `.type-{category}` in HTML

### Changing the scanned directory
Modify `DOWNLOADS_PATH` at top of `downloads-server.py`

### Adjusting files shown per folder
Change the `[:20]` slice in `scan_folder()` function
