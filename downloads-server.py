#!/usr/bin/env python3
"""
Downloads Galaxy Server
Run this script and open http://localhost:8000 in your browser.
Click "Reindex" to refresh the file list from your Downloads folder.

Usage:
    python3 downloads-server.py [folder_path]

Examples:
    python3 downloads-server.py                    # Scan ~/Downloads (default)
    python3 downloads-server.py /path/to/folder    # Scan specified folder
    python3 downloads-server.py ~/Documents        # Scan Documents folder

To use a different port: PORT=8001 python3 downloads-server.py
"""

import argparse
import http.server
import json
import os
from pathlib import Path
from datetime import datetime
import mimetypes

def parse_args():
    parser = argparse.ArgumentParser(
        description='Downloads Galaxy - A cosmic file browser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                      Scan ~/Downloads (default)
  %(prog)s /path/to/folder      Scan specified folder
  %(prog)s ~/Documents          Scan Documents folder
  PORT=8001 %(prog)s            Use a different port
        '''
    )
    parser.add_argument(
        'folder',
        nargs='?',
        default=str(Path.home() / "Downloads"),
        help='Path to folder to index (default: ~/Downloads)'
    )
    return parser.parse_args()

args = parse_args()
DOWNLOADS_PATH = Path(args.folder).expanduser().resolve()
PORT = int(os.environ.get('PORT', 8000))

# File type categorization
FILE_CATEGORIES = {
    'video': ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v'],
    'audio': ['.mp3', '.m4a', '.wav', '.flac', '.aac', '.ogg', '.wma'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.heic', '.tiff'],
    'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.csv'],
    'archive': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
    'installer': ['.dmg', '.pkg', '.app', '.exe', '.msi'],
    'data': ['.json', '.xml', '.yaml', '.yml', '.sql', '.db'],
    'code': ['.py', '.js', '.ts', '.html', '.css', '.java', '.cpp', '.c', '.go', '.rs', '.rb'],
}

FOLDER_ICONS = {
    'video': '🎬',
    'music': '🎵',
    'images & screenshots': '🖼️',
    'ai & evals': '🤖',
    'forms & documents': '📋',
    'financial': '💰',
    'parenting & education podcasts': '👨‍👩‍👧',
    'installers & archives': '📦',
    'code projects': '💻',
    'manuals & reference': '📖',
    'misc': '✨',
}

def get_file_type(filename):
    ext = Path(filename).suffix.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return 'other'

def get_file_icon(filename, is_dir=False):
    if is_dir:
        return '📁'
    ext = Path(filename).suffix.lower()
    icons = {
        '.mp4': '🎥', '.mov': '🎥', '.avi': '🎥',
        '.mp3': '🎙️', '.m4a': '🎵', '.wav': '🎵',
        '.jpg': '📸', '.jpeg': '📸', '.png': '📱', '.webp': '🌐', '.gif': '🎞️',
        '.pdf': '📄', '.doc': '📝', '.docx': '📝', '.txt': '📝',
        '.zip': '📦', '.rar': '📦', '.7z': '📦',
        '.dmg': '💿', '.pkg': '📀',
        '.json': '📊', '.xml': '📊',
        '.py': '🐍', '.js': '📜', '.html': '🌐',
        '.srt': '📝', '.ics': '📅', '.pkpass': '🎟️',
    }
    return icons.get(ext, '📄')

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def scan_downloads():
    """Scan the Downloads folder and return structured data."""
    result = {
        'folders': [],
        'stats': {
            'total_files': 0,
            'total_size': 0,
            'categories': 0,
            'file_types': set()
        },
        'scanned_at': datetime.now().isoformat()
    }

    if not DOWNLOADS_PATH.exists():
        return result

    # Get all items in Downloads
    items = list(DOWNLOADS_PATH.iterdir())
    folders = []
    root_files = []

    for item in items:
        if item.name.startswith('.'):
            continue
        if item.name == '$RECYCLE.BIN':
            continue

        if item.is_dir():
            folder_data = scan_folder(item)
            if folder_data['files']:  # Only include non-empty folders
                folders.append(folder_data)
        else:
            file_data = get_file_data(item)
            if file_data:
                root_files.append(file_data)

    # Add root files as "Uncategorized" if any
    if root_files:
        folders.append({
            'name': 'Uncategorized',
            'icon': '📂',
            'category': 'other',
            'files': root_files,
            'total_size': sum(f['size_bytes'] for f in root_files)
        })

    # Sort folders by total size (largest first)
    folders.sort(key=lambda x: x['total_size'], reverse=True)

    result['folders'] = folders

    # Calculate stats
    all_files = []
    for folder in folders:
        all_files.extend(folder['files'])

    result['stats']['total_files'] = len(all_files)
    result['stats']['total_size'] = sum(f['size_bytes'] for f in all_files)
    result['stats']['total_size_formatted'] = format_size(result['stats']['total_size'])
    result['stats']['categories'] = len(folders)
    result['stats']['file_types'] = len(set(f['extension'] for f in all_files if f['extension']))

    return result

def scan_folder(folder_path):
    """Scan a single folder and return its data."""
    folder_name = folder_path.name
    files = []
    total_size = 0

    # Determine folder icon and category
    folder_lower = folder_name.lower()
    icon = FOLDER_ICONS.get(folder_lower, '📁')

    # Determine category based on folder name
    if 'video' in folder_lower:
        category = 'video'
    elif 'music' in folder_lower or 'audio' in folder_lower:
        category = 'audio'
    elif 'image' in folder_lower or 'screenshot' in folder_lower or 'photo' in folder_lower:
        category = 'image'
    elif 'document' in folder_lower or 'form' in folder_lower:
        category = 'document'
    elif 'install' in folder_lower or 'archive' in folder_lower:
        category = 'installer'
    elif 'financial' in folder_lower or 'finance' in folder_lower:
        category = 'document'
    elif 'ai' in folder_lower or 'eval' in folder_lower:
        category = 'document'
    elif 'podcast' in folder_lower or 'parenting' in folder_lower or 'education' in folder_lower:
        category = 'audio'
    elif 'code' in folder_lower or 'project' in folder_lower:
        category = 'archive'
    elif 'manual' in folder_lower or 'reference' in folder_lower:
        category = 'document'
    else:
        category = 'other'

    # Scan files (including subdirectories)
    try:
        for item in folder_path.rglob('*'):
            if item.is_file() and not item.name.startswith('.'):
                file_data = get_file_data(item, relative_to=folder_path)
                if file_data:
                    files.append(file_data)
                    total_size += file_data['size_bytes']
    except PermissionError:
        pass

    # Sort files by size (largest first)
    files.sort(key=lambda x: x['size_bytes'], reverse=True)

    # Limit to top 20 files per folder for display
    display_files = files[:20]
    hidden_count = len(files) - 20 if len(files) > 20 else 0

    return {
        'name': folder_name,
        'icon': icon,
        'category': category,
        'files': display_files,
        'total_files': len(files),
        'hidden_files': hidden_count,
        'total_size': total_size,
        'total_size_formatted': format_size(total_size)
    }

def get_file_data(file_path, relative_to=None):
    """Get data for a single file."""
    try:
        stat = file_path.stat()
        name = file_path.name
        if relative_to:
            try:
                name = str(file_path.relative_to(relative_to))
            except ValueError:
                name = file_path.name

        ext = file_path.suffix.lower()

        return {
            'name': name,
            'display_name': file_path.stem[:50] + ('...' if len(file_path.stem) > 50 else ''),
            'extension': ext[1:] if ext else '',
            'type': get_file_type(file_path.name),
            'icon': get_file_icon(file_path.name),
            'size_bytes': stat.st_size,
            'size': format_size(stat.st_size),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    except (PermissionError, OSError):
        return None

class DownloadsHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)

    def do_GET(self):
        if self.path == '/api/scan':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            data = scan_downloads()
            self.wfile.write(json.dumps(data, default=str).encode())
        elif self.path == '/' or self.path == '/index.html':
            self.path = '/downloads-viewer.html'
            return super().do_GET()
        else:
            return super().do_GET()

if __name__ == '__main__':
    print(f"\n🌌 Downloads Galaxy Server")
    print(f"=" * 40)
    print(f"📂 Scanning: {DOWNLOADS_PATH}")

    if not DOWNLOADS_PATH.exists():
        print(f"❌ Error: Folder does not exist: {DOWNLOADS_PATH}")
        exit(1)
    if not DOWNLOADS_PATH.is_dir():
        print(f"❌ Error: Path is not a folder: {DOWNLOADS_PATH}")
        exit(1)

    print(f"🌐 Open http://localhost:{PORT} in your browser")
    print(f"⌨️  Press Ctrl+C to stop\n")

    with http.server.HTTPServer(('', PORT), DownloadsHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")
