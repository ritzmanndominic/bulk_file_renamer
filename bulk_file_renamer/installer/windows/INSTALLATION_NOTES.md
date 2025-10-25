# Installation Notes

## Required Software

### Inno Setup
1. Download Inno Setup from: https://jrsoftware.org/isinfo.php
2. Install the software (default installation is fine)
3. Make sure `iscc.exe` is in your PATH, or use the full path to the executable

### Alternative: Use Full Path
If Inno Setup is not in your PATH, you can modify the build scripts to use the full path:

**For build_installer.bat:**
```batch
"C:\Program Files (x86)\Inno Setup 6\iscc.exe" installer\BulkFileRenamer.iss
```

**For build_installer.ps1:**
```powershell
& "C:\Program Files (x86)\Inno Setup 6\iscc.exe" installer\BulkFileRenamer.iss
```

## Testing the Installer

1. Build the installer using one of the build scripts
2. Run the generated installer: `installer\Output\BulkFileRenamer_Windows_Installer.exe`
3. Test the installation process:
   - Language selection
   - Theme selection
   - Desktop icon creation
   - Application launch
4. Test the uninstaller
5. Test upgrade scenario (install, then install again)

## Troubleshooting

### Common Issues:
- **"iscc not found"**: Install Inno Setup and ensure it's in PATH
- **"Source file not found"**: Ensure the dist directory exists with the built application
- **"Icon file not found"**: Ensure assets/app.ico exists
- **"License file not found"**: Ensure legal/en/eula.txt exists

### File Requirements:
- `dist/Bulk File Renamer/Bulk File Renamer.exe` (main executable)
- `dist/Bulk File Renamer/_internal/` (runtime dependencies)
- `assets/app.ico` (application icon)
- `legal/en/eula.txt` (license file)
- `legal/en/privacy.txt` (privacy policy)

