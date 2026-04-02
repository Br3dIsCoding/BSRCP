# Build a single-file GUI + CLI redeem tool for Streamer.bot.
# Run from PowerShell:  cd d:\TWITCH\Redeems ; .\build_exe.ps1
# Requires: pip install pyinstaller  (use the same venv you use to run the app)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

$Python = if (Test-Path "$Root\.venv\Scripts\python.exe") {
  "$Root\.venv\Scripts\python.exe"
} else {
  "py"
}

# PyInstaller on Windows: source;folder_inside_bundle
$Data = "no_cursing;no_cursing"

& $Python -m PyInstaller `
  --noconfirm --clean `
  --onefile `
  --windowed `
  --name BSRCP `
  --add-data $Data `
  --hidden-import chaos_controls.chaos `
  --hidden-import no_cursing.noswears `
  --hidden-import ScreenTurn.screen_flip `
  gui.py

Write-Host "Done. Output: $Root\dist\BSRCP.exe"
Write-Host "Copy BSRCP.exe plus your config.json (optional) into one folder. Double-click for GUI, or call with --chaos etc."
