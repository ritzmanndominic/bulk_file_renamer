# Installation Notes

## Required Software

### NSIS (Nullsoft Scriptable Install System)
1. Download NSIS from: https://nsis.sourceforge.io/
2. Install the software (default installation is fine)
3. Make sure `makensis.exe` is in your PATH, or use the full path to the executable

### Alternative: Use Full Path
If NSIS is not in your PATH, you can modify the build scripts to use the full path:

**For build_nsis_installer.ps1:**
```powershell
& "C:\Program Files (x86)\NSIS\makensis.exe" BulkFileRenamer.nsi
```

## Testing the Installer

1. Build the installer using the build script: `.\build_nsis_installer.ps1`
2. Run the generated installer: `installer\windows\BulkFileRenamer_Windows_Installer.exe`
3. Test the installation process:
   - Language selection
   - Theme selection
   - Desktop icon creation
   - Application launch
4. Test the uninstaller
5. Test upgrade scenario (install, then install again)

## Troubleshooting

### Common Issues:
- **"makensis not found"**: Install NSIS and ensure it's in PATH
- **"Source file not found"**: Ensure the dist directory exists with the built application
- **"Icon file not found"**: Ensure assets/app.ico exists
- **"License file not found"**: Ensure legal/en/eula.txt exists

### File Requirements:
- `dist/Bulk File Renamer/Bulk File Renamer.exe` (main executable)
- `dist/Bulk File Renamer/_internal/` (runtime dependencies)
- `assets/app.ico` (application icon)
- `legal/en/eula.txt` (license file)
- `legal/en/privacy.txt` (privacy policy)

