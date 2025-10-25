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

### Windows
```bash
pyinstaller --onefile --windowed \
    --name "Bulk File Renamer" \
    --add-data "languages;languages" \
    --add-data "legal;legal" \
    --add-data "assets;assets" \
    --icon "assets/app.ico" \
    main.py
```

### macOS
```bash
pyinstaller --onefile --windowed \
    --name "Bulk File Renamer" \
    --add-data "languages:languages" \
    --add-data "legal:legal" \
    --add-data "assets:assets" \
    --osx-bundle-identifier "com.dominic-ritzmann.bulk-file-renamer" \
    --icon "assets/app.icns" \
    main.py
```

The commands bundle languages, legal documents, and assets into the executable.

## Safety
- Keep backups. Use confirmation, validate/simulate, and backup options.
- The app is provided "as is" without warranties.

## License
Bulk File Renamer License. See LICENSE. © 2025 Dominic Ritzmann.

## Version
See `app/__init__.py` for the app version.





