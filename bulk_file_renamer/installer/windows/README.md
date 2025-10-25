# Bulk File Renamer - Windows Installer

This directory contains the NSIS script and build files for creating a Windows installer for Bulk File Renamer.

## Prerequisites

1. **NSIS**: Download and install from https://nsis.sourceforge.io/
2. **Built Application**: Ensure the application is built in the `dist/Bulk File Renamer/` directory

## Building the Installer

### Option 1: From Root Directory
```powershell
.\build_windows_installer.ps1
```

### Option 2: From Windows Directory
```powershell
cd installer\windows
.\build_nsis_installer.ps1
```

### Option 3: Manual Build
```cmd
cd installer\windows
makensis BulkFileRenamer.nsi
```

## Output

The installer will be created in `installer\windows\BulkFileRenamer_Windows_Installer.exe`

## Features

- **Clean Installation**: Only includes essential files (no cache, profiles, etc.)
- **Language Selection**: English and German support
- **Theme Selection**: Light, Dark, and System Default themes
- **Desktop Icon**: Optional desktop shortcut
- **Uninstall Support**: Complete removal of application and settings
- **Upgrade Support**: Automatically uninstalls previous versions

## File Structure

The installer includes:
- Main executable (`Bulk File Renamer.exe`)
- All runtime dependencies in `_internal/` directory
- Language files (English and German)
- Legal documents (EULA, Privacy Policy, Terms)
- User settings file (created during installation)

## Excluded Files

The following files are intentionally excluded from the installer:
- `__pycache__/` directories
- `profiles/` directory
- `history.json`
- `settings.json` (created fresh during installation)
- Build artifacts
- Test files

