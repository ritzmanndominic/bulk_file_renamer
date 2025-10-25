# Build Windows Installer
Write-Host "Building Windows Installer..." -ForegroundColor Green

# Change to the windows installer directory
Push-Location installer\windows

try {
    # Run the windows build script
    & ".\build_nsis_installer.ps1"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Windows installer built successfully!" -ForegroundColor Green
        Write-Host "Output: installer\windows\BulkFileRenamer_Windows_Installer.exe" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "Error: Windows installer build failed!" -ForegroundColor Red
        exit 1
    }
} finally {
    # Return to original directory
    Pop-Location
}

