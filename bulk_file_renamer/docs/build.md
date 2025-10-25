# 🔨 Build Instructions

Complete guide to building Bulk File Renamer from source code.

## 📋 Prerequisites

### Required Software
- **Python 3.8 or higher**
- **pip package manager**
- **Git** (for cloning the repository)

### Platform-Specific Requirements

#### Windows
- **Visual Studio Build Tools** (for some Python packages)
- **Windows SDK** (recommended)
- **NSIS** (for Windows installer creation)

#### macOS
- **Xcode Command Line Tools**: `xcode-select --install`
- **Homebrew** (recommended for package management)
- **create-dmg** (for DMG creation): `brew install create-dmg`

#### Linux
- **Build essentials**: `sudo apt-get install build-essential`
- **Python development headers**: `sudo apt-get install python3-dev`
- **Additional packages** may be required depending on distribution

## 🚀 Development Build

### 1. Clone the Repository
```bash
git clone https://github.com/dominic-ritzmann/bulk-file-renamer.git
cd bulk-file-renamer
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 4. Run the Application
```bash
python main.py
```

## 📦 Building Executables

### Using PyInstaller

#### Windows Build
```bash
# Basic build
pyinstaller --onefile --windowed \
    --name "Bulk File Renamer" \
    --add-data "languages;languages" \
    --add-data "legal;legal" \
    --add-data "assets;assets" \
    --icon "assets/app.ico" \
    main.py

# Advanced build with optimization
pyinstaller --onefile --windowed \
    --name "Bulk File Renamer" \
    --add-data "languages;languages" \
    --add-data "legal;legal" \
    --add-data "assets;assets" \
    --icon "assets/app.ico" \
    --optimize 2 \
    --strip \
    --noupx \
    main.py
```

#### macOS Build
```bash
# Basic build
pyinstaller --onefile --windowed \
    --name "Bulk File Renamer" \
    --add-data "languages:languages" \
    --add-data "legal:legal" \
    --add-data "assets:assets" \
    --osx-bundle-identifier "com.dominic-ritzmann.bulk-file-renamer" \
    --icon "assets/app.icns" \
    main.py

# Advanced build with optimization
pyinstaller --onefile --windowed \
    --name "Bulk File Renamer" \
    --add-data "languages:languages" \
    --add-data "legal:legal" \
    --add-data "assets:assets" \
    --osx-bundle-identifier "com.dominic-ritzmann.bulk-file-renamer" \
    --icon "assets/app.icns" \
    --optimize 2 \
    --strip \
    main.py
```

#### Linux Build
```bash
# Basic build
pyinstaller --onefile --windowed \
    --name "Bulk File Renamer" \
    --add-data "languages:languages" \
    --add-data "legal:legal" \
    --add-data "assets:assets" \
    --icon "assets/app.png" \
    main.py
```

### Build Output
- **Executable**: `dist/Bulk File Renamer.exe` (Windows) or `dist/Bulk File Renamer` (macOS/Linux)
- **Build files**: `build/` directory contains temporary build files
- **Spec file**: `Bulk File Renamer.spec` (auto-generated)

## 🏗️ Creating Installers

### Windows Installers

#### NSIS Installer
```bash
# Navigate to installer directory
cd installer/windows

# Build NSIS installer
makensis BulkFileRenamer.nsi
```

#### Inno Setup Installer
```bash
# Navigate to installer directory
cd installer/windows

# Build Inno Setup installer (requires Inno Setup)
iscc BulkFileRenamer.iss
```

### macOS Installers

#### DMG Installer
```bash
# Navigate to installer directory
cd installer/macos

# Make script executable
chmod +x build_macos_installer.sh

# Build DMG installer
./build_macos_installer.sh
```

#### PKG Installer
```bash
# Navigate to installer directory
cd installer/macos

# Make script executable
chmod +x create_pkg.sh

# Build PKG installer
./create_pkg.sh
```

## 🔧 Build Configuration

### PyInstaller Options

#### Essential Options
- `--onefile`: Create a single executable file
- `--windowed`: Hide console window (GUI application)
- `--name`: Set the executable name
- `--icon`: Set the application icon
- `--add-data`: Include additional files/directories

#### Optimization Options
- `--optimize 2`: Maximum Python optimization
- `--strip`: Remove debug symbols
- `--noupx`: Disable UPX compression (faster startup)

#### Platform-Specific Options
- `--osx-bundle-identifier`: macOS bundle identifier
- `--target-arch`: Target architecture (x86_64, arm64)

### Build Scripts

#### Automated Build Script
```bash
#!/bin/bash
# build.sh - Automated build script

set -e

echo "Building Bulk File Renamer..."

# Clean previous builds
rm -rf build/ dist/

# Build executable
pyinstaller --onefile --windowed \
    --name "Bulk File Renamer" \
    --add-data "languages:languages" \
    --add-data "legal:legal" \
    --add-data "assets:assets" \
    --icon "assets/app.icns" \
    --optimize 2 \
    main.py

echo "Build complete! Executable: dist/Bulk File Renamer"
```

## 🐛 Troubleshooting Build Issues

### Common Issues

#### Import Errors
```
ModuleNotFoundError: No module named 'PySide6'
```
**Solution**: Install dependencies with `pip install -r requirements.txt`

#### Icon Not Found
```
FileNotFoundError: [Errno 2] No such file or directory: 'assets/app.ico'
```
**Solution**: Ensure icon files exist in the `assets/` directory

#### Data Files Not Included
```
FileNotFoundError: languages/en.json not found
```
**Solution**: Check `--add-data` paths and ensure files exist

#### Large Executable Size
**Solutions**:
- Use `--exclude-module` to exclude unused modules
- Use `--optimize 2` for Python optimization
- Consider `--onedir` instead of `--onefile` for smaller size

### Platform-Specific Issues

#### Windows
- **Antivirus false positives**: Common with PyInstaller executables
- **Missing Visual C++ Redistributable**: Install latest version
- **Path length limitations**: Use shorter paths

#### macOS
- **Code signing issues**: May need developer certificate
- **Gatekeeper warnings**: Common with unsigned executables
- **Architecture compatibility**: Ensure correct target architecture

#### Linux
- **Missing system libraries**: Install required packages
- **GLIBC version compatibility**: Check system requirements
- **Desktop integration**: May need additional packages

## 📊 Build Performance

### Optimization Tips
1. **Use virtual environments** to avoid conflicts
2. **Clean build directories** between builds
3. **Exclude unnecessary modules** with `--exclude-module`
4. **Use `--optimize 2`** for production builds
5. **Consider `--onedir`** for faster startup

### Build Times
- **Development build**: 30-60 seconds
- **Production build**: 2-5 minutes
- **Installer creation**: 1-3 minutes

## 🔍 Testing Builds

### Basic Testing
1. **Run the executable** on target system
2. **Test core functionality** (add files, rename, preview)
3. **Check file associations** and icons
4. **Verify data files** are included correctly

### Advanced Testing
1. **Test on clean system** (no Python installed)
2. **Check different user permissions**
3. **Test with various file types** and sizes
4. **Verify installer functionality**

## 📝 Build Notes

### Version Information
- **Version**: Set in `app/__init__.py`
- **Build date**: Automatically included in builds
- **Git commit**: Can be included for development builds

### Signing and Notarization
- **Windows**: Code signing with Authenticode
- **macOS**: Code signing and notarization
- **Linux**: GPG signing (optional)

### Distribution
- **GitHub Releases**: Upload installers and executables
- **Package managers**: Consider platform-specific packages
- **Direct download**: Provide direct download links

---

**Need Help?** Check our [Troubleshooting Guide](troubleshooting.md) or [GitHub Issues](https://github.com/ritzmanndominic/bulk_file_renamer/issues)!
