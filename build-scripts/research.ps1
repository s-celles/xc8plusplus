# XC8++ Research and Development Script (PowerShell)
# This script will help research the feasibility of XC8++ implementation

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$SubCommand = ""
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "XC8++ Research and Development Tool" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

function Show-Help {
    Write-Host @"
Usage: .\research.ps1 <command> [options]

Commands:
    research        Run research tasks
    analyze-xc8     Analyze XC8 compiler architecture
    test-memory     Test memory constraints on target devices
    poc             Create proof of concept (if feasible)
    help            Show this help message

Research Commands:
    research download-xc8       Download XC8 source code
    research analyze-source     Analyze XC8 compiler structure
    research check-gcc          Check if XC8 is GCC-based
    research memory-calc        Calculate C++ memory overhead
    research feasibility        Run complete feasibility assessment

Examples:
    .\research.ps1 research download-xc8    # Download XC8 source for analysis
    .\research.ps1 analyze-xc8              # Analyze XC8 compiler architecture
    .\research.ps1 research feasibility     # Run complete feasibility study
"@
}

function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow
    
    $missingTools = @()
    $warnings = @()
    
    # Check for optional tools (warn if missing, don't fail)
    if (!(Get-Command "gcc" -ErrorAction SilentlyContinue)) { 
        $warnings += "gcc (optional - needed for development phase)" 
    }
    if (!(Get-Command "git" -ErrorAction SilentlyContinue)) { 
        $warnings += "git (optional - for version control)" 
    }
    
    # Check for essential tools for research phase
    if (!(Get-Command "powershell" -ErrorAction SilentlyContinue)) { 
        $missingTools += "PowerShell" 
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host "Optional tools not found (install later if needed):" -ForegroundColor Yellow
        $warnings | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    }
    
    if ($missingTools.Count -gt 0) {
        Write-Host "Error: Missing essential tools: $($missingTools -join ', ')" -ForegroundColor Red
        Write-Host "Please install missing tools and try again." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Prerequisites check passed for research phase." -ForegroundColor Green
    if ($warnings.Count -gt 0) {
        Write-Host "Note: Some optional tools are missing but research can proceed." -ForegroundColor Cyan
    }
}

function Get-XC8Source {
    Write-Host "Researching XC8 source code availability..." -ForegroundColor Yellow
    
    Write-Host "Note: XC8 source code availability needs to be researched." -ForegroundColor Cyan
    Write-Host "Check Microchip's website for:" -ForegroundColor Cyan
    Write-Host "  1. XC8 source code downloads" -ForegroundColor Cyan
    Write-Host "  2. Licensing terms (GPL compatibility)" -ForegroundColor Cyan
    Write-Host "  3. Available versions" -ForegroundColor Cyan
    
    # Create research directory structure
    $researchDir = Join-Path $ProjectRoot "research"
    $downloadsDir = Join-Path $researchDir "downloads"
    $analysisDir = Join-Path $researchDir "analysis"
    
    New-Item -ItemType Directory -Force -Path $downloadsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $analysisDir | Out-Null
    
    # Document findings
    $researchFile = Join-Path $researchDir "xc8-source-research.md"
    
    $researchContent = @'
# XC8 Source Code Research

## Research Status
- [ ] Located XC8 source code downloads
- [ ] Verified licensing terms
- [ ] Downloaded source for analysis
- [ ] Extracted and organized source code

## Findings
*Update this section with research findings*

### Source Code Availability
- URL: TBD
- License: TBD
- Versions: TBD

### Download Commands
```powershell
# Commands to download XC8 source (to be determined)
# Invoke-WebRequest -Uri <XC8_SOURCE_URL> -OutFile xc8-source.zip
# Expand-Archive xc8-source.zip -DestinationPath xc8-source
```

## Next Steps
1. Research Microchip website for XC8 source downloads
2. Verify license compatibility
3. Download and extract source code
4. Begin architecture analysis
'@
    
    $researchContent | Out-File -FilePath $researchFile -Encoding UTF8
    
    Write-Host "Research template created in: $researchFile" -ForegroundColor Green
    Write-Host "Please update this file with your findings." -ForegroundColor Green
}

function Test-XC8Architecture {
    Write-Host "Analyzing XC8 compiler architecture..." -ForegroundColor Yellow
    
    # Check if XC8 is installed (try both xc8 and xc8-cc)
    $xc8Path = Get-Command "xc8" -ErrorAction SilentlyContinue
    if (!$xc8Path) {
        $xc8Path = Get-Command "xc8-cc" -ErrorAction SilentlyContinue
    }
    
    if ($xc8Path) {
        Write-Host "Found XC8 installation: $($xc8Path.Source)" -ForegroundColor Green
        try {
            if ($xc8Path.Name -eq "xc8-cc.exe") {
                $xc8Version = & xc8-cc --version 2>&1 | Select-Object -First 1
            } else {
                $xc8Version = & xc8 --version 2>&1 | Select-Object -First 1
            }
            Write-Host "Version: $xc8Version" -ForegroundColor Green
        } catch {
            Write-Host "Version: Unknown" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Warning: XC8 not found in PATH" -ForegroundColor Yellow
        Write-Host "Please install XC8 compiler for analysis" -ForegroundColor Yellow
        Write-Host "Expected paths: xc8.exe or xc8-cc.exe" -ForegroundColor Yellow
    }
    
    # Create analysis script
    $analysisScript = Join-Path $ProjectRoot "research\analyze-xc8.ps1"
    
    $analysisContent = @'
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
'@
    
    $analysisContent | Out-File -FilePath $analysisScript -Encoding UTF8
    
    Write-Host "Created analysis script: $analysisScript" -ForegroundColor Green
    
    # Run the analysis if XC8 is available
    if ($xc8Path) {
        Write-Host "Running XC8 analysis..." -ForegroundColor Yellow
        & PowerShell -File $analysisScript
    }
}

function Test-GCCCompatibility {
    Write-Host "Checking XC8 GCC compatibility..." -ForegroundColor Yellow
    
    # Create a test script to determine if XC8 uses GCC infrastructure
    $gccTestScript = Join-Path $ProjectRoot "research\gcc-test.ps1"
    
    $gccTestContent = @'
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
'@
    
    $gccTestContent | Out-File -FilePath $gccTestScript -Encoding UTF8
    
    Write-Host "Created GCC compatibility test: $gccTestScript" -ForegroundColor Green
    
    # Check for XC8 (try both xc8 and xc8-cc)
    $xc8Available = Get-Command "xc8" -ErrorAction SilentlyContinue
    if (!$xc8Available) {
        $xc8Available = Get-Command "xc8-cc" -ErrorAction SilentlyContinue
    }
    
    if ($xc8Available) {
        Write-Host "Running GCC compatibility test..." -ForegroundColor Yellow
        Push-Location (Join-Path $ProjectRoot "research")
        & PowerShell -File "gcc-test.ps1"
        Pop-Location
    } else {
        Write-Host "XC8 not found in PATH. Please add XC8 to PATH to run tests." -ForegroundColor Yellow
        Write-Host "Example: `$env:PATH = 'C:\Program Files\Microchip\xc8\v3.00\bin;' + `$env:PATH" -ForegroundColor Cyan
    }
}

function Test-MemoryOverhead {
    Write-Host "Calculating C++ memory overhead..." -ForegroundColor Yellow
    
    # Create a test to measure C++ overhead
    $cTestFile = Join-Path $ProjectRoot "research\memory-test.c"
    $cppTestFile = Join-Path $ProjectRoot "research\memory-test.cpp"
    
    $cContent = @'
// Test C file for memory overhead baseline
#include <stdint.h>

uint8_t global_var = 0;

void simple_function(uint8_t param) {
    global_var = param;
}

int main() {
    simple_function(42);
    return 0;
}
'@
    
    $cppContent = @'
// Test C++ file for memory overhead measurement
#include <stdint.h>

class SimpleClass {
    uint8_t value;
public:
    SimpleClass(uint8_t v) : value(v) {}
    void setValue(uint8_t v) { value = v; }
    uint8_t getValue() const { return value; }
};

SimpleClass global_obj(0);

int main() {
    global_obj.setValue(42);
    return 0;
}
'@
    
    $cContent | Out-File -FilePath $cTestFile -Encoding ASCII
    $cppContent | Out-File -FilePath $cppTestFile -Encoding ASCII
    
    Write-Host "Created memory test files:" -ForegroundColor Green
    Write-Host "  - research/memory-test.c (C baseline)" -ForegroundColor Green
    Write-Host "  - research/memory-test.cpp (C++ comparison)" -ForegroundColor Green
    Write-Host ""
    Write-Host "To measure overhead:" -ForegroundColor Cyan
    Write-Host "  1. Compile both with XC8 (when C++ support is available)" -ForegroundColor Cyan
    Write-Host "  2. Compare code size and memory usage" -ForegroundColor Cyan
    Write-Host "  3. Document findings in research/memory-constraints.md" -ForegroundColor Cyan
}

function Start-FeasibilityAssessment {
    Write-Host "Running complete feasibility assessment..." -ForegroundColor Yellow
    
    Write-Host "1. Downloading/researching XC8 source..." -ForegroundColor Cyan
    Get-XC8Source
    
    Write-Host ""
    Write-Host "2. Analyzing XC8 architecture..." -ForegroundColor Cyan
    Test-XC8Architecture
    
    Write-Host ""
    Write-Host "3. Checking GCC compatibility..." -ForegroundColor Cyan
    Test-GCCCompatibility
    
    Write-Host ""
    Write-Host "4. Creating memory overhead tests..." -ForegroundColor Cyan
    Test-MemoryOverhead
    
    Write-Host ""
    Write-Host "Feasibility assessment setup complete!" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Review generated files in research/ directory" -ForegroundColor Cyan
    Write-Host "  2. Install XC8 compiler if not already installed" -ForegroundColor Cyan
    Write-Host "  3. Run analysis scripts" -ForegroundColor Cyan
    Write-Host "  4. Research XC8 source code availability" -ForegroundColor Cyan
    Write-Host "  5. Update RESEARCH.md with findings" -ForegroundColor Cyan
    Write-Host "  6. Make go/no-go decision based on results" -ForegroundColor Cyan
}

# Main command processing
switch ($Command.ToLower()) {
    "research" {
        switch ($SubCommand.ToLower()) {
            "download-xc8" {
                Test-Prerequisites
                Get-XC8Source
            }
            "analyze-source" {
                Test-XC8Architecture
            }
            "check-gcc" {
                Test-GCCCompatibility
            }
            "memory-calc" {
                Test-MemoryOverhead
            }
            "feasibility" {
                Test-Prerequisites
                Start-FeasibilityAssessment
            }
            default {
                Write-Host "Unknown research command: $SubCommand" -ForegroundColor Red
                Show-Help
            }
        }
    }
    "analyze-xc8" {
        Test-XC8Architecture
    }
    "test-memory" {
        Test-MemoryOverhead
    }
    "poc" {
        Write-Host "Proof of concept not yet implemented." -ForegroundColor Yellow
        Write-Host "Run feasibility assessment first: .\research.ps1 research feasibility" -ForegroundColor Cyan
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
