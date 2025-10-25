# Bulk File Renamer

A cross‑platform GUI tool to preview and safely rename many files with powerful filters and profiles. Built with PySide6.

## Features
- Add folders/files and drag & drop
- Naming: prefix, suffix, base name, start number; optional extension lock
- Auto‑clean: remove special chars, replace spaces, convert case, remove accents
- Filters: extensions, size (>, <, =), date (before/after), status
- Live preview with coloring, search, sorting, lazy loading
- Profiles: save/load settings; recent profiles with configurable limit
- Undo last/selected operations (reverse chronological)
- Optional backups to a subfolder and operation logging
- Export preview (CSV/JSON), Validate/Simulate report
- English/German localization and notifications

## Install & Run (Dev)
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python main.py
```

## Build with PyInstaller
Windows/macOS (example):
```bash
pyinstaller bulk_file_renamer.spec
```
The spec bundles languages and legal documents.

## Safety
- Keep backups. Use confirmation, validate/simulate, and backup options.
- The app is provided "as is" without warranties (MIT License).

## [License](https://github.com/ritzmanndominic/bulk_file_renamer/blob/main/bulk_file_renamer/LICENSE)
MIT. See [LICENSE](https://github.com/ritzmanndominic/bulk_file_renamer/blob/main/bulk_file_renamer/LICENSE). © Dominic Ritzmann.

## [Report Issue](https://github.com/ritzmanndominic/bulk_file_renamer/issues)
Report any issues, feature improvements or questions [here](https://github.com/ritzmanndominic/bulk_file_renamer/issues).

## Version
Current version 1.0

See `app/__init__.py` for the app version.


