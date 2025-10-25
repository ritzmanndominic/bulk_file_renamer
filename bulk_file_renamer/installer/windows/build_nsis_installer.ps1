# Build NSIS Installer for Bulk File Renamer
Write-Host "Building Bulk File Renamer with NSIS..." -ForegroundColor Green

# Check if NSIS is installed
$nsisPaths = @(
    "C:\Program Files (x86)\NSIS\makensis.exe",
    "C:\Program Files\NSIS\makensis.exe",
    "makensis.exe"
)

$makensisPath = $null
foreach ($path in $nsisPaths) {
    if (Test-Path $path) {
        $makensisPath = $path
        break
    }
}

if ($makensisPath) {
    Write-Host "Found NSIS at: $makensisPath" -ForegroundColor Green
} else {
    Write-Host "Error: NSIS (makensis.exe) not found" -ForegroundColor Red
    Write-Host "Please install NSIS from https://nsis.sourceforge.io/" -ForegroundColor Yellow
    Write-Host "Common installation paths:" -ForegroundColor Yellow
    Write-Host "  - C:\Program Files (x86)\NSIS\" -ForegroundColor Yellow
    Write-Host "  - C:\Program Files\NSIS\" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check required files
Write-Host "Checking required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "..\..\dist\Bulk File Renamer.exe",
    "..\..\legal\en\eula.txt"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "Missing required files:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "All required files found!" -ForegroundColor Green

# Build the installer
Write-Host "Compiling NSIS installer..." -ForegroundColor Yellow
$result = & $makensisPath BulkFileRenamer.nsi

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "NSIS installer built successfully!" -ForegroundColor Green
    Write-Host "Output: BulkFileRenamer_Windows_Installer.exe" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Error: NSIS compilation failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Read-Host "Press Enter to continue"

