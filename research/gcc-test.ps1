# Test if XC8 is GCC-based

Write-Host "Testing XC8 GCC Compatibility" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Check for XC8 (try both xc8 and xc8-cc)
$xc8 = Get-Command "xc8" -ErrorAction SilentlyContinue
if (!$xc8) {
    $xc8 = Get-Command "xc8-cc" -ErrorAction SilentlyContinue
}

if (!$xc8) {
    Write-Host "Error: XC8 not found in PATH" -ForegroundColor Red
    Write-Host "Expected: xc8.exe or xc8-cc.exe" -ForegroundColor Red
    exit 1
}

Write-Host "Found XC8: $($xc8.Name)" -ForegroundColor Green

# Create test C file
@"
int main() {
    return 0;
}
"@ | Out-File -FilePath "test.c" -Encoding ASCII

Write-Host "Compiling test file with verbose output..." -ForegroundColor Yellow
try {
    if ($xc8.Name -eq "xc8-cc.exe") {
        $output = & xc8-cc -v test.c -o test.out 2>&1
    } else {
        $output = & xc8 -v test.c -o test.out 2>&1
    }
    $output | Out-File -FilePath "xc8-verbose.log" -Encoding UTF8
    
    Write-Host ""
    Write-Host "Searching for GCC indicators in output:" -ForegroundColor Yellow
    $gccRefs = $output | Select-String -Pattern "gcc" -CaseSensitive:$false
    if ($gccRefs) {
        $gccRefs | ForEach-Object { Write-Host "  $_" -ForegroundColor Green }
    } else {
        Write-Host "  No GCC references found" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Checking for typical GCC command patterns:" -ForegroundColor Yellow
    $gccTools = $output | Select-String -Pattern "(cc1|collect2|ld|as)"
    if ($gccTools) {
        $gccTools | ForEach-Object { Write-Host "  $_" -ForegroundColor Green }
    } else {
        Write-Host "  No typical GCC tools found" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Analysis saved to: xc8-verbose.log" -ForegroundColor Green
    Write-Host "Review this file for GCC compatibility indicators." -ForegroundColor Green
    
} catch {
    Write-Host "Error running XC8: $_" -ForegroundColor Red
}

# Cleanup
Remove-Item -Path "test.c", "test.out" -ErrorAction SilentlyContinue
