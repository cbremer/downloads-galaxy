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

from downloads_core import scan_path


def scan_downloads():
    """Scan the configured folder and return structured data."""
    return scan_path(DOWNLOADS_PATH)


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
