"""Shared scanning logic for Downloads Galaxy clients."""

from datetime import datetime
from pathlib import Path

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
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_file_data(file_path, relative_to=None):
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


def scan_folder(folder_path):
    folder_name = folder_path.name
    files = []
    total_size = 0

    folder_lower = folder_name.lower()
    icon = FOLDER_ICONS.get(folder_lower, '📁')

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

    try:
        for item in folder_path.rglob('*'):
            if item.is_file() and not item.name.startswith('.'):
                file_data = get_file_data(item, relative_to=folder_path)
                if file_data:
                    files.append(file_data)
                    total_size += file_data['size_bytes']
    except PermissionError:
        pass

    files.sort(key=lambda x: x['size_bytes'], reverse=True)

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


def scan_path(scan_path: Path):
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

    if not scan_path.exists():
        return result

    items = list(scan_path.iterdir())
    folders = []
    root_files = []

    for item in items:
        if item.name.startswith('.') or item.name == '$RECYCLE.BIN':
            continue

        if item.is_dir():
            folder_data = scan_folder(item)
            if folder_data['files']:
                folders.append(folder_data)
        else:
            file_data = get_file_data(item)
            if file_data:
                root_files.append(file_data)

    if root_files:
        total = sum(f['size_bytes'] for f in root_files)
        folders.append({
            'name': 'Uncategorized',
            'icon': '📂',
            'category': 'other',
            'files': root_files,
            'total_files': len(root_files),
            'hidden_files': 0,
            'total_size': total,
            'total_size_formatted': format_size(total),
        })

    folders.sort(key=lambda x: x['total_size'], reverse=True)
    result['folders'] = folders

    all_files = []
    for folder in folders:
        all_files.extend(folder['files'])

    result['stats']['total_files'] = len(all_files)
    result['stats']['total_size'] = sum(f['size_bytes'] for f in all_files)
    result['stats']['total_size_formatted'] = format_size(result['stats']['total_size'])
    result['stats']['categories'] = len(folders)
    result['stats']['file_types'] = len(set(f['extension'] for f in all_files if f['extension']))

    return result
