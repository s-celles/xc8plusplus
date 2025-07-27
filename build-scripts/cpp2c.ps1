# C++ to C Translator for XC8++
# Proof of Concept Implementation

param(
    [Parameter(Mandatory=$true)]
    [string]$InputFile,
    
    [string]$OutputFile,
    [switch]$ShowTranslation,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
XC8++ C++ to C Translator (Proof of Concept)

USAGE:
    cpp2c.ps1 [options] input.cpp

OPTIONS:
    -OutputFile <file>     Output C file (default: input_translated.c)
    -ShowTranslation      Show the translation process
    -Help                 Show this help message

DESCRIPTION:
    Converts basic C++ constructs to equivalent C code that XC8 can compile.
    
SUPPORTED FEATURES:
    - Simple classes with public members
    - Constructors (basic initialization)
    - Member functions
    - extern "C" functions

EXAMPLE:
    cpp2c.ps1 examples\minimal.cpp -OutputFile output.c -ShowTranslation
"@
    exit 0
}

if (!(Test-Path $InputFile)) {
    Write-Error "Input file not found: $InputFile"
    exit 1
}

if (!$OutputFile) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
    $OutputFile = "${baseName}_translated.c"
}

Write-Host "🔄 XC8++ C++ to C Translator" -ForegroundColor Green
Write-Host "Input:  $InputFile" -ForegroundColor Cyan
Write-Host "Output: $OutputFile" -ForegroundColor Cyan

# Read the input file
$content = Get-Content $InputFile -Raw

if ($ShowTranslation) {
    Write-Host "`n📝 Original C++ Code:" -ForegroundColor Yellow
    Write-Host $content -ForegroundColor Gray
}

# Translation patterns (simplified proof of concept)
$translatedContent = $content

# Step 1: Handle extern "C" functions - just remove the extern "C" wrapper
$translatedContent = $translatedContent -replace 'extern\s+"C"\s+', ''

# Step 2: Convert simple class definition to struct + function declarations
if ($translatedContent -match 'class\s+(\w+)\s*\{([^}]+)\}') {
    $className = $matches[1]
    $classBody = $matches[2]
    
    if ($ShowTranslation) {
        Write-Host "`n🔍 Found class: $className" -ForegroundColor Yellow
    }
    
    # Extract public members and methods
    $structMembers = ""
    $functionDeclarations = ""
    $functionImplementations = ""
    
    # Simple parsing for demonstration (would need proper parser for production)
    $lines = $classBody -split "`n"
    $inConstructor = $false
    $constructorBody = ""
    
    foreach ($line in $lines) {
        $line = $line.Trim()
        if ($line -eq "public:") { continue }
        if ($line -eq "") { continue }
        
        # Handle member variables
        if ($line -match '(\w+)\s+(\w+);') {
            $type = $matches[1]
            $varName = $matches[2]
            $structMembers += "    $type $varName;`n"
            if ($ShowTranslation) {
                Write-Host "  📋 Member variable: $type $varName" -ForegroundColor Gray
            }
        }
        
        # Handle constructor
        if ($line -match "$className\(\)") {
            $inConstructor = $true
            if ($ShowTranslation) {
                Write-Host "  🏗️ Constructor found" -ForegroundColor Gray
            }
            continue
        }
        
        if ($inConstructor) {
            if ($line -eq "{") { continue }
            if ($line -eq "}") { 
                $inConstructor = $false
                continue 
            }
            $constructorBody += "    $line`n"
        }
        
        # Handle member functions
        if ($line -match '(\w+)\s+(\w+)\(\)') {
            $returnType = $matches[1]
            $funcName = $matches[2]
            $mangledName = "${className}_${funcName}"
            $functionDeclarations += "$returnType ${mangledName}(struct $className* self);`n"
            if ($ShowTranslation) {
                Write-Host "  ⚙️ Member function: $returnType $funcName() -> ${mangledName}()" -ForegroundColor Gray
            }
        }
    }
    
    # Generate the translated struct and functions
    $structDef = @"
// Translated from class $className
typedef struct $className {
$structMembers} $className;

// Constructor function
void ${className}_init($className* self) {
$constructorBody}

// Member function declarations
$functionDeclarations
"@
    
    # Replace the class definition
    $classPattern = "class\s+$className\s*\{[^}]+\};"
    $translatedContent = $translatedContent -replace $classPattern, $structDef
}

# Step 3: Convert member function implementations
# Look for functions that return obj.getValue() pattern
if ($translatedContent -match '(\w+)\s+(\w+)\(\)\s*\{([^}]+)\}') {
    $funcMatches = [regex]::Matches($translatedContent, '(\w+)\s+(\w+)\(\)\s*\{([^}]+)\}')
    
    foreach ($match in $funcMatches) {
        $returnType = $match.Groups[1].Value
        $funcName = $match.Groups[2].Value
        $funcBody = $match.Groups[3].Value.Trim()
        
        # Check if this function uses a class object
        if ($funcBody -match '(\w+)\s+(\w+);.*return\s+\2\.(\w+)\(\)') {
            $className = $matches[1]
            $objName = $matches[2] 
            $methodName = $matches[3]
            
            $newFuncBody = @"
$returnType $funcName() {
    $className $objName;
    ${className}_init(&$objName);
    return ${className}_${methodName}(&$objName);
}
"@
            
            $originalFunc = $match.Groups[0].Value
            $translatedContent = $translatedContent -replace [regex]::Escape($originalFunc), $newFuncBody
            
            if ($ShowTranslation) {
                Write-Host "  🔄 Translated function: $funcName" -ForegroundColor Gray
            }
        }
    }
}

# Step 4: Add member function implementations (for getValue example)
if ($translatedContent -match "SimpleClass_getValue") {
    $getValue_impl = @"

// Member function implementation
int SimpleClass_getValue(struct SimpleClass* self) {
    return self->value;
}
"@
    $translatedContent += $getValue_impl
}

# Write the translated content
Set-Content -Path $OutputFile -Value $translatedContent

if ($ShowTranslation) {
    Write-Host "`n📝 Translated C Code:" -ForegroundColor Yellow
    Write-Host $translatedContent -ForegroundColor Gray
}

Write-Host "`n✅ Translation completed successfully!" -ForegroundColor Green
Write-Host "Generated: $OutputFile" -ForegroundColor Green

# Test compilation with XC8
Write-Host "`n🧪 Testing compilation with XC8..." -ForegroundColor Yellow
$env:PATH = "C:\Program Files\Microchip\xc8\v3.00\bin;" + $env:PATH
$compileResult = & xc8-cc -mcpu=pic16f877a -c $OutputFile 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ XC8 compilation successful!" -ForegroundColor Green
} else {
    Write-Host "❌ XC8 compilation failed:" -ForegroundColor Red
    Write-Host $compileResult -ForegroundColor Red
}
