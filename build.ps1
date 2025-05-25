<#
.SYNOPSIS
    Build 8ds.exe using PyInstaller.

.DESCRIPTION
    - Activates the virtual environment
    - Cleans previous build artifacts
    - Runs PyInstaller with flags for onefile, windowed, naming, and icon embedding
    - Outputs final exe in .\build
    - Cleans up temporary folders
#>

# 1. Activate venv
$activateScript = Join-Path $PSScriptRoot ".\.venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Error "Cannot find virtualenv activation script at $activateScript"
    exit 1
}

# 2. Clean previous outputs
Write-Host "Cleaning old builds..."
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue `
    "$PSScriptRoot\build", "$PSScriptRoot\dist", "$PSScriptRoot\*.spec"

# 3. Build with PyInstaller, using absolute manifest path
$manifestPath = Join-Path $PSScriptRoot "src\8ds.exe.manifest"
if (-Not (Test-Path $manifestPath)) {
    Write-Error "Manifest not found at $manifestPath"
    exit 1
}

# 4. Ensure icon exists
$iconPath = Join-Path $PSScriptRoot "assets\8ds.ico"
if (-Not (Test-Path $iconPath)) {
    Write-Error "Icon not found at $iconPath"
    exit 1
}


Write-Host "Running PyInstaller with manifest $manifestPath..."

pyinstaller `
    --onefile `
    --windowed `
    --name "8ds" `
    --icon $iconPath `
    --manifest $manifestPath `
    --distpath "build" `
    --workpath "build\_work" `
    --specpath "build\_work" `
    "src\main_gui.py"

# 5. Cleanup staging
Write-Host "Removing temporary work directory..."
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "build\_work"

Write-Host "✅ Build complete! Executable at build\8ds.exe"