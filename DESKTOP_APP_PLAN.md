# Desktop App Plan for Downloads Galaxy

## Goals
- Deliver a native desktop experience that preserves the current “galaxy” concept.
- Keep the app read-only and low-maintenance.
- Reuse existing Python scanning logic to avoid duplicated behavior.

## Phase 1: Prototype (implemented in this repo)
1. **Extract shared scanner logic** into a module (`downloads_core.py`) used by both web server and desktop app.
2. **Build a Tkinter desktop shell** (`downloads-desktop.py`) with:
   - Folder picker for changing the indexed directory.
   - “Reindex” action.
   - Category/folder list plus file detail table.
   - Basic stats (file count, category count, total size, scan timestamp).
3. **Maintain read-only behavior** (no file modification).
4. **Document usage** in `README.md`.

## Phase 2: Productization
1. **Visual parity pass**
   - Bring over more of the cosmic visual language (color themes, iconography, subtle animations).
   - Add richer charts (category breakdown by size and count).
2. **Desktop UX enhancements**
   - File preview metadata panel.
   - Open-in-Finder / Reveal path actions.
   - Search and filter controls.
3. **Performance + resilience**
   - Background scanning thread with progress indicator.
   - Incremental refresh mode.
   - Better handling for large folder trees and permission errors.

## Phase 3: Distribution
1. **Package for macOS**
   - Use `pyinstaller` to build a standalone `.app` bundle.
   - Add app icon, code signing, and notarization pipeline.
2. **Release automation**
   - Tag-based builds via CI.
   - Publish release artifacts with checksum + changelog.
3. **Optional cross-platform support**
   - Validate on Windows/Linux path semantics and shell actions.

## Proposed Architecture
- `downloads_core.py`: source of truth for categorization and scan output.
- `downloads-server.py`: web API + static UI host (existing behavior).
- `downloads-desktop.py`: native GUI client consuming shared scanner APIs directly.

## Success Criteria
- Users can run one command to launch desktop app prototype.
- Desktop and web variants produce compatible stats and file categorizations.
- No data mutation occurs in any app mode.
