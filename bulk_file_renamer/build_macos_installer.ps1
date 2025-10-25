# Build macOS Installer
Write-Host "Building macOS Installer..." -ForegroundColor Green

# Check if we're on macOS
if ($env:OS -ne "Darwin" -and $IsMacOS -ne $true) {
    Write-Host "Error: This script must be run on macOS" -ForegroundColor Red
    Write-Host "Please run the installer creation on a macOS system" -ForegroundColor Yellow
    Write-Host "You can use the scripts in installer/macos/ directory" -ForegroundColor Yellow
    exit 1
}

# Change to the macOS installer directory
Push-Location installer\macos

try {
    # Make scripts executable
    Write-Host "Setting up macOS installer scripts..." -ForegroundColor Yellow
    
    # Run the macOS build script
    & ".\build_macos_installer.sh"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "macOS installer built successfully!" -ForegroundColor Green
        Write-Host "Output: installer\macos\BulkFileRenamer_macOS_Installer.dmg" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "Error: macOS installer build failed!" -ForegroundColor Red
        exit 1
    }
} finally {
    # Return to original directory
    Pop-Location
}

