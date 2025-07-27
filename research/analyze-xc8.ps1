# XC8 Architecture Analysis Script

Write-Host "XC8 Compiler Architecture Analysis" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Check XC8 installation (try both xc8 and xc8-cc)
$xc8 = Get-Command "xc8" -ErrorAction SilentlyContinue
if (!$xc8) {
    $xc8 = Get-Command "xc8-cc" -ErrorAction SilentlyContinue
}

if ($xc8) {
    Write-Host "XC8 Installation Found:" -ForegroundColor Green
    Write-Host "  Path: $($xc8.Source)" -ForegroundColor Green
    
    try {
        if ($xc8.Name -eq "xc8-cc.exe") {
            $version = & xc8-cc --version 2>&1 | Select-Object -First 1
        } else {
            $version = & xc8 --version 2>&1 | Select-Object -First 1
        }
        Write-Host "  Version: $version" -ForegroundColor Green
    } catch {
        Write-Host "  Version: Unknown" -ForegroundColor Yellow
    }
    
    # Try to determine XC8 installation directory
    $xc8Dir = Split-Path -Parent (Split-Path -Parent $xc8.Source)
    Write-Host "  Installation Directory: $xc8Dir" -ForegroundColor Green
    
    # Look for key files that indicate GCC usage
    Write-Host ""
    Write-Host "Searching for GCC indicators:" -ForegroundColor Yellow
    Get-ChildItem -Path $xc8Dir -Recurse -Name "*gcc*" -ErrorAction SilentlyContinue | Select-Object -First 10
    Get-ChildItem -Path $xc8Dir -Recurse -Name "cc1*" -ErrorAction SilentlyContinue | Select-Object -First 10
    Get-ChildItem -Path $xc8Dir -Recurse -Name "collect2*" -ErrorAction SilentlyContinue | Select-Object -First 10
    
    # Check for source or documentation
    Write-Host ""
    Write-Host "Looking for source or documentation:" -ForegroundColor Yellow
    Get-ChildItem -Path $xc8Dir -Recurse -Include "*.txt", "*.md", "*.pdf" -ErrorAction SilentlyContinue | 
        Where-Object { $_.Name -match "(source|gcc|build)" } | 
        Select-Object -First 10 -ExpandProperty FullName
        
} else {
    Write-Host "XC8 not found. Please install XC8 compiler." -ForegroundColor Red
    Write-Host "Download from: https://www.microchip.com/mplab/compilers" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Analysis complete. Review findings above." -ForegroundColor Green
Write-Host "Update research/xc8-architecture.md with results." -ForegroundColor Green
