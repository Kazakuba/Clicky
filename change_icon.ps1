# Clicky Automation Icon Changer
# This script will help you change the application icon and rebuild the app

Write-Host "=== Clicky Automation Icon Changer ===" -ForegroundColor Cyan
Write-Host "This script will help you change the application icon and rebuild the app."
Write-Host

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "Found $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Python not found! Please ensure Python is installed and in your PATH." -ForegroundColor Red
    Write-Host "`nPress any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# Check for parameters
$imagePath = $args[0]

if ([string]::IsNullOrEmpty($imagePath)) {
    Write-Host "No image file specified." -ForegroundColor Yellow
    Write-Host
    Write-Host "Usage options:"
    Write-Host "  1. Run with image path: .\change_icon.ps1 path\to\your\icon.png"
    Write-Host "  2. Continue without arguments to use interactive mode"
    Write-Host
    $continue = Read-Host "Do you want to continue in interactive mode? (Y/N)"
    
    if ($continue -ne "Y" -and $continue -ne "y") {
        exit
    }
    
    # Run the conversion script in interactive mode
    python resources\images\convert_to_ico.py
}
else {
    # Run the conversion script with the provided argument
    python resources\images\convert_to_ico.py "$imagePath"
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 