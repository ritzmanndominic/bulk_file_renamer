# 🚀 Installation Guide

This guide will help you install Bulk File Renamer on your system.

## 📋 Prerequisites

- **Python 3.8 or higher**
- **pip package manager**
- **Git** (for development installation)

## 🖥️ Installation Methods

### Method 1: Development Installation (Recommended for Contributors)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dominic-ritzmann/bulk-file-renamer.git
   cd bulk-file-renamer
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment:**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

### Method 2: Pre-built Executables

#### Windows
1. Download the latest Windows installer from ...
2. Run the installer and follow the setup wizard
3. Launch from Start Menu or Desktop shortcut

## ❓ Troubleshooting

### Common Issues

**Python not found:**
- Make sure Python 3.8+ is installed and added to PATH
- Try using `python3` instead of `python`

**Permission errors:**
- Run terminal/command prompt as administrator (Windows)
- Use `sudo` for system-wide installation (macOS/Linux)

**Virtual environment issues:**
- Delete `.venv` folder and recreate it
- Make sure you're using the correct Python version

### Getting Help

- Report issues on [[GitHub Issues]](https://github.com/ritzmanndominic/bulk_file_renamer/issues)

## ✅ Verification

After installation, verify everything works:

1. Launch the application
2. Try adding a test folder with some files
3. Test the preview functionality
4. Verify all features are working
