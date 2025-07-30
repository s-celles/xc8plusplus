# XC8++ LibTooling Transpiler

Professional C++ to C transpilation using LLVM/Clang LibTooling semantic analysis.

## Overview

This is the **professional implementation** of the XC8++ transpiler that replaces regex soup with real semantic analysis. It uses LLVM/Clang LibTooling for proper C++ AST analysis and type-safe transformations.

## Features

🔍 **Semantic AST Analysis**
- Uses Clang's RecursiveASTVisitor for proper C++ parsing
- No regex patterns or string manipulation
- Full type information and semantic understanding

🏗️ **Professional Architecture**
- LibTooling-based frontend actions
- Industry-standard Clang API usage
- Extensible visitor pattern implementation

⚡ **Type-Safe Transformations**
- C++ classes → C structs with proper field handling
- C++ methods → C functions with semantic parameter mapping
- C++ constructors/destructors → C init/cleanup functions
- C++ enums → C enums with value preservation

🎯 **XC8-Optimized Output**
- Generates XC8-compatible C code
- Microcontroller-specific optimizations
- Proper pragma and configuration handling
- Memory-efficient code generation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    XC8++ LibTooling Architecture            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   C++ Source    │───▶│  Clang Parser   │                │
│  │     Files       │    │   (Frontend)    │                │
│  └─────────────────┘    └─────────────────┘                │
│                                   │                        │
│                                   ▼                        │
│                        ┌─────────────────┐                │
│                        │   AST Context   │                │
│                        │  (Semantic)     │                │
│                        └─────────────────┘                │
│                                   │                        │
│                                   ▼                        │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ XC8Transpiler   │◀───│ AST Visitor     │                │
│  │ (Collector)     │    │ (Traversal)     │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                                                │
│           ▼                                                │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Code Generator  │───▶│   C Output      │                │
│  │ (Transformer)   │    │    File         │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Building

### Prerequisites

1. **LLVM/Clang Development Libraries**
   ```bash
   # Windows - Download from LLVM releases
   https://github.com/llvm/llvm-project/releases
   
   # Ubuntu/Debian
   sudo apt install llvm-dev clang-dev
   
   # macOS
   brew install llvm
   ```

2. **CMake 3.20+**
3. **C++17 compatible compiler**

### Build Instructions

**Windows:**
```cmd
# Run the build script
build-libtooling.bat

# Or manually:
mkdir build_libtooling
cd build_libtooling
cmake -G "Visual Studio 17 2022" -A x64 ^
    -DLLVM_DIR="C:\Program Files\LLVM\lib\cmake\llvm" ^
    -DClang_DIR="C:\Program Files\LLVM\lib\cmake\clang" ^
    ../src/libtooling
cmake --build . --config Release
```

**Linux/macOS:**
```bash
mkdir build_libtooling
cd build_libtooling
cmake -DCMAKE_BUILD_TYPE=Release ../src/libtooling
make -j$(nproc)
```

## Usage

### Standalone Tool

```bash
# Transpile single file
xc8pp-tool input.cpp -o output.c

# Transpile multiple files with verbose output
xc8pp-tool *.cpp -o project.c -v

# Show version
xc8pp-tool --version
```

### Python Integration

```python
from xc8plusplus.libtooling_transpiler import LibToolingTranspiler

# Create transpiler
transpiler = LibToolingTranspiler()

# Check availability
if transpiler.is_available():
    print("LibTooling transpiler ready!")
    
    # Transpile files
    success, info = transpiler.transpile_files(
        source_files=[Path("button.cpp"), Path("led.cpp")],
        output_file=Path("output.c"),
        include_dirs=[Path("../include")]
    )
    
    if success:
        print(f"Success! Found {info.classes_found} classes")
    else:
        print(f"Failed: {info.error_message}")
```

### CLI Integration

```bash
# Use LibTooling transpiler via CLI
xc8plusplus libtooling examples/arduino-multi -o libtooling_output.c -v

# Show transpiler information
xc8plusplus info

# Compare with Python-based transpiler
xc8plusplus batch examples/arduino-multi --output python_output
```

## C API

The transpiler provides a clean C API for integration with other languages:

```c
#include "XC8TranspilerAPI.h"

// Create transpiler
XC8TranspilerHandle handle = xc8_transpiler_create();

// Transpile files
const char* sources[] = {"button.cpp", "led.cpp", NULL};
const char* includes[] = {"../include", NULL};
XC8TranspilerInfo info;

XC8Result result = xc8_transpiler_process_files(
    handle, sources, includes, "output.c", &info
);

if (result == XC8_SUCCESS) {
    printf("Success! Generated %zu bytes of code\n", info.code_length);
}

// Cleanup
xc8_transpiler_info_free(&info);
xc8_transpiler_destroy(handle);
```

## Development

### Key Classes

- **`XC8Transpiler`**: Main AST visitor that collects semantic information
- **`XC8TranspilerConsumer`**: AST consumer that owns the transpiler
- **`XC8TranspilerAction`**: Frontend action for LibTooling integration
- **`LibToolingTranspiler`**: Python wrapper class

### Adding New C++ Features

1. **Add AST visitor method** in `XC8Transpiler.h`:
   ```cpp
   bool VisitNewCppConstruct(clang::NewCppConstruct *Declaration);
   ```

2. **Implement semantic analysis** in `XC8Transpiler.cpp`:
   ```cpp
   bool XC8Transpiler::VisitNewCppConstruct(NewCppConstruct *Declaration) {
       // Collect semantic information
       // Store in appropriate data structure
       return true;
   }
   ```

3. **Add code generation** in `GenerateCCode()`:
   ```cpp
   // Generate C equivalent using semantic information
   output << GenerateNewConstructToC(info);
   ```

## Testing

```bash
# Test standalone tool
cd examples/arduino-multi
../../build_libtooling/Release/xc8pp-tool.exe *.cpp -o test_output.c -v

# Test Python integration
python -c "
from src.xc8plusplus.libtooling_transpiler import transpile_project
from pathlib import Path
success = transpile_project(Path('examples/arduino-multi'), Path('test.c'))
print('Success!' if success else 'Failed!')
"

# Test compilation with XC8
xc8-wrapper cc -mcpu=16F876A test_output.c -o test.hex
```

## Comparison with Python Implementation

| Feature | Python Implementation | LibTooling Implementation |
|---------|----------------------|---------------------------|
| **Analysis Method** | AST dump string parsing | Native AST traversal |
| **Type Safety** | Limited, regex-based | Full semantic analysis |
| **Reliability** | Brittle, edge cases | Robust, comprehensive |
| **Performance** | Slow, multiple subprocess calls | Fast, single compilation |
| **Maintainability** | Regex soup, hard to extend | Clean architecture, extensible |
| **Professional** | Proof-of-concept | Production-ready |

## Benefits of LibTooling Approach

1. **No Regex Soup**: Direct AST manipulation, no string parsing
2. **Type Safety**: Full C++ type system integration
3. **Reliability**: Handles all C++ constructs correctly
4. **Performance**: Single compilation pass
5. **Extensibility**: Easy to add new C++ features
6. **Industry Standard**: Uses same APIs as clang-tidy, refactoring tools

## License

Apache 2.0 with LLVM Exception (same as LLVM/Clang)

## Contributing

1. Ensure LLVM/Clang development environment is set up
2. Build and test the LibTooling implementation
3. Add semantic analysis for new C++ constructs
4. Update Python wrapper and CLI integration
5. Add tests for new functionality

---

**🎯 This is the professional way to do C++ to C transpilation!**  
No more regex soup - pure semantic analysis with industry-standard tools.
