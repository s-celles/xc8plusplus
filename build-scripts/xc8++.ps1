# XC8++ - C++ Wrapper for XC8 Compiler
# Proof of Concept Implementation

param(
    [Parameter(Mandatory=$true)]
    [string[]]$InputFiles,
    
    [string]$MCpu = "pic16f877a",
    [string]$OutputDir = ".",
    [switch]$ShowVerbose,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
XC8++ - C++ Support for XC8 Compiler (Proof of Concept)

USAGE:
    xc8++.ps1 [options] file1.cpp [file2.c] [file3.cpp] ...

OPTIONS:
    -MCpu <device>     Target PIC device (default: pic16f877a)
    -OutputDir <dir>   Output directory (default: current directory)
    -ShowVerbose           Show verbose compilation output
    -Help              Show this help message

EXAMPLES:
    # Compile C++ files for PIC16F877A
    xc8++.ps1 -MCpu pic16f877a main.cpp utils.cpp

    # Mixed C/C++ compilation
    xc8++.ps1 main.c module.cpp helper.c

DISCOVERY: XC8's internal Clang compiler supports C++ with -x c++ flag!
This wrapper bypasses XC8 driver limitations and uses Clang directly.
"@
    exit 0
}

# Locate XC8 installation
$XC8_BASE = "C:\Program Files\Microchip\xc8\v3.00"
$XC8_CLANG = "$XC8_BASE\pic\bin\clang.exe"
$XC8_CC = "$XC8_BASE\bin\xc8-cc.exe"

if (!(Test-Path $XC8_CLANG)) {
    Write-Error "XC8 Clang not found at: $XC8_CLANG"
    Write-Error "Please install XC8 v3.00 or adjust the path in this script"
    exit 1
}

Write-Host "🎯 XC8++ Proof of Concept" -ForegroundColor Green
Write-Host "Using XC8 Clang: $XC8_CLANG" -ForegroundColor Cyan

$CppFiles = @()
$CFiles = @()
$ObjectFiles = @()

# Separate C++ and C files
foreach ($file in $InputFiles) {
    if (!(Test-Path $file)) {
        Write-Error "File not found: $file"
        exit 1
    }
    
    $ext = [System.IO.Path]::GetExtension($file).ToLower()
    switch ($ext) {
        ".cpp" { $CppFiles += $file }
        ".cxx" { $CppFiles += $file }
        ".cc"  { $CppFiles += $file }
        ".c"   { $CFiles += $file }
        default { 
            Write-Warning "Unknown file type: $file (treating as C)"
            $CFiles += $file
        }
    }
}

Write-Host "Found $($CppFiles.Count) C++ files and $($CFiles.Count) C files" -ForegroundColor Yellow

# Compile C++ files with XC8's Clang
foreach ($cppFile in $CppFiles) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($cppFile)
    $asmFile = Join-Path $OutputDir "$baseName.s"
    
    Write-Host "Compiling C++: $cppFile -> $asmFile" -ForegroundColor Cyan
    
    $clangArgs = @(
        "-x", "c++",
        "-S",
        $cppFile,
        "-o", $asmFile
    )
    
    if ($ShowVerbose) {
        $clangArgs += "-v"
    }
    
    & $XC8_CLANG @clangArgs
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "C++ compilation failed for: $cppFile"
        exit 1
    }
    
    $ObjectFiles += $asmFile
}

# For now, just show what would happen with C files
if ($CFiles.Count -gt 0) {
    Write-Host "C files would be compiled with standard XC8:" -ForegroundColor Yellow
    foreach ($cFile in $CFiles) {
        Write-Host "  xc8-cc -mcpu=$MCpu $cFile" -ForegroundColor Gray
    }
}

Write-Host "`n✅ C++ compilation successful!" -ForegroundColor Green
Write-Host "Generated assembly files: $($ObjectFiles -join ', ')" -ForegroundColor Green
Write-Host "`n🔄 Next steps for full implementation:" -ForegroundColor Yellow
Write-Host "  1. Integrate C++ assembly into XC8 linking pipeline" -ForegroundColor Gray
Write-Host "  2. Handle C++ runtime library requirements" -ForegroundColor Gray  
Write-Host "  3. Test linking with actual PIC targets" -ForegroundColor Gray
Write-Host "  4. Implement C++ standard library subset" -ForegroundColor Gray
