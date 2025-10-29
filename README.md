# Bulk File Renamer

A cross‑platform GUI tool to preview and safely rename many files with powerful filters and profiles. Built with PySide6.

Buy on [Itch.io](https://ritzmanndominic.itch.io/bulk-file-renamer) or [Gumroad](https://onedev.gumroad.com/l/bulk_file_renamer)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/dominic-ritzmann/bulk-file-renamer)

## Support me
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/ritzmanndominic)

## ✨ Features

- **📁 Easy File Management**: Add folders/files and drag & drop support
- **🏷️ Flexible Naming**: Prefix, suffix, base name, start number with optional extension lock
- **🧹 Auto-clean**: Remove special chars, replace spaces, convert case, remove accents
- **🔍 Advanced Filters**: Extensions, size (>, <, =), date (before/after), status
- **👁️ Live Preview**: Real-time preview with coloring, search, sorting, and lazy loading
- **💾 Profile System**: Save/load settings with recent profiles and configurable limits
- **↩️ Undo Support**: Undo last/selected operations (reverse chronological)
- **💾 Backup Options**: Optional backups to subfolder and operation logging
- **📊 Export & Validate**: Export preview (CSV/JSON), validate/simulate reports
- **🌍 Multilingual**: English/German localization with notifications

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Development Setup
```bash
# Clone the repository
git clone https://github.com/dominic-ritzmann/bulk-file-renamer.git
cd bulk-file-renamer

# Create virtual environment
python -m venv .venv

# Activate virtual environment
. .venv/Scripts/activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 🔨 Building Executables

### Windows/macOS
```bash
pyinstaller bulk_file_renamer.spec
```
The spec file bundles languages and legal documents.

## 🛡️ Safety & Best Practices

- **Always keep backups** of important files before renaming
- Use the **confirmation dialog** and **validate/simulate** features
- Enable **backup options** for critical operations
- The app is provided "as is" without warranties

## 🐛 Bug Reports & Support

Found a bug or have a feature request? Please help us improve by:

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Screenshots if applicable

[**Report a Bug**](https://github.com/dominic-ritzmann/bulk-file-renamer/issues/new?template=bug_report.md) | [**Request a Feature**](https://github.com/dominic-ritzmann/bulk-file-renamer/issues/new?template=feature_request.md)

## 📄 License

MIT License. See [LICENSE](LICENSE) file for details.

© 2025 Dominic Ritzmann

## 📋 Version

Current version: **1.0**

See `app/__init__.py` for the app version.
