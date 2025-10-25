# Bulk File Renamer - macOS Installer

This directory contains scripts for creating a professional macOS PKG installer for Bulk File Renamer.

## Quick Start

```bash
./build_installer.sh
```

This will build the app and create a professional PKG installer with GUI installation wizard.

## Features

- **Professional GUI Installation**: Like Chrome, Adobe, and other major software
- **Readable Text**: All text is properly styled and readable
- **English Interface**: Consistent English language throughout
- **Automatic Installation**: Installs directly to Applications folder
- **System Requirements Check**: Verifies macOS compatibility
- **Progress Bars**: Real-time installation progress

## Output

- **`BulkFileRenamer_macOS_Installer.pkg`** - Professional PKG installer
- **Size**: ~35MB
- **Format**: Standard macOS PKG with installation wizard

## Installation Experience

1. User downloads the PKG file
2. User double-clicks to start installation
3. Professional installation wizard appears
4. User accepts license agreement
5. Installation progress bar shows
6. App is automatically installed to Applications
7. User can launch from Applications or Spotlight

## Requirements

- macOS 10.15 (Catalina) or later
- Xcode Command Line Tools
- Python 3.8+ with PyInstaller

## Files

- `build_installer.sh` - Main build script
- `create_pkg.sh` - PKG installer creation
- `README.md` - This file


