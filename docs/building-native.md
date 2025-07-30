# Building the Native XC8++ Transpiler

This guide shows how to build and use the native C++ transpiler using LLVM LibTooling.

## Overview

The XC8++ project includes two transpiler backends:

1. **Native C++ Backend** (Professional) - Uses LLVM LibTooling for semantic AST analysis
2. **Python Backend** (Fallback) - Uses Clang AST dumps with Python parsing

The native backend provides superior performance and more accurate transpilation.

## Prerequisites

### Required Software

1. **CMake 3.20+**
   - Download from: https://cmake.org/download/
   - Ensure `cmake` is in your PATH

2. **LLVM/Clang Development Libraries**
   - **Windows**: Download LLVM from https://releases.llvm.org/
   - **Linux**: `sudo apt-get install llvm-dev clang-dev` (Ubuntu/Debian)
   - **macOS**: `brew install llvm` (Homebrew)

3. **C++ Compiler**
   - **Windows**: Visual Studio 2019+ or Visual Studio Build Tools
   - **Linux**: GCC 9+ or Clang 10+
   - **macOS**: Xcode Command Line Tools

4. **Python 3.8+** with development headers
   - **Windows**: Install from python.org
   - **Linux**: `sudo apt-get install python3-dev`
   - **macOS**: Use Homebrew or system Python

### Checking Prerequisites

Run this PowerShell script to check your system:

```powershell
# Check CMake
if (Get-Command cmake -ErrorAction SilentlyContinue) {
    Write-Host "✅ CMake found: $(cmake --version | Select-String -Pattern '\d+\.\d+\.\d+')"
} else {
    Write-Host "❌ CMake not found"
}

# Check Clang
if (Get-Command clang -ErrorAction SilentlyContinue) {
    Write-Host "✅ Clang found: $(clang --version | Select-String -Pattern '\d+\.\d+\.\d+')"
} else {
    Write-Host "❌ Clang not found"
}

# Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "✅ Python found: $(python --version)"
} else {
    Write-Host "❌ Python not found"
}
```

## Building the Native Transpiler

### Method 1: Using the Build Script (Recommended)

The easiest way to build the native transpiler:

```powershell
# Navigate to the project directory
cd xc8plusplus

# Run the build script
.\build-scripts\build_native.ps1

# For a clean build with tests
.\build-scripts\build_native.ps1 -Clean -Test

# For a debug build
.\build-scripts\build_native.ps1 -BuildType Debug
```

### Method 2: Manual CMake Build

If you prefer manual control:

```powershell
# Create build directory
mkdir build_libtooling
cd build_libtooling

# Configure
cmake -G "Visual Studio 17 2022" -DCMAKE_BUILD_TYPE=Release ..

# Build
cmake --build . --config Release --parallel

# Test (optional)
ctest --output-on-failure --config Release

# Install (optional)
cmake --install . --config Release
```

### Method 3: Using vcpkg (Advanced)

For dependency management with vcpkg:

```powershell
# Install vcpkg if not already installed
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat

# Install LLVM
.\vcpkg install llvm:x64-windows

# Build with vcpkg
cd ..\xc8plusplus
mkdir build_vcpkg
cd build_vcpkg
cmake -G "Visual Studio 17 2022" -DCMAKE_TOOLCHAIN_FILE=..\..\vcpkg\scripts\buildsystems\vcpkg.cmake ..
cmake --build . --config Release
```

## Verifying the Build

After building, test the native transpiler:

```powershell
# Test the standalone executable
.\build_libtooling\bin\xc8transpiler_tool.exe --version
.\build_libtooling\bin\xc8transpiler_tool.exe --check-llvm

# Test the C API
.\build_libtooling\bin\test_c_api.exe

# Test Python integration
python test_native_integration.py
```

## Installing the Python Package

After building the native backend, install the Python package:

```powershell
# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Using the Native Transpiler

### From Command Line

```bash
# Basic usage
xc8plusplus transpile input.cpp output.c

# With target device
xc8plusplus transpile input.cpp --target PIC18F4620

# Batch transpilation
xc8plusplus batch ./examples/arduino-multi --target PIC16F876A

# Force Python backend (for comparison)
xc8plusplus --python-backend transpile input.cpp

# Check system status
xc8plusplus check
xc8plusplus info
```

### From Python

```python
from xc8plusplus import XC8Transpiler

# Create transpiler (automatically uses native backend if available)
transpiler = XC8Transpiler(
    target_device="PIC16F876A",
    enable_optimization=True,
    generate_xc8_pragmas=True
)

# Check which backend is being used
backend_info = transpiler.get_backend_info()
print(f"Using: {backend_info['description']}")

# Transpile from string
cpp_code = """
class Led {
public:
    void turnOn();
    void turnOff();
private:
    bool state;
};
"""

result = transpiler.transpile_string(cpp_code, "led.cpp")
if result.success:
    print("Generated C code:")
    print(result.generated_c_code)
else:
    print(f"Error: {result.error_message}")

# Transpile from file
result = transpiler.transpile_file("input.cpp", "output.c")
```

### Direct C API Usage

If you want to use the C API directly:

```c
#include "c_api/XC8TranspilerCAPI.h"

int main() {
    // Create transpiler
    XC8Transpiler_t transpiler = xc8_transpiler_create(NULL);
    
    // Transpile code
    XC8TranspilerResult_t result = {0};
    int status = xc8_transpiler_transpile_string(
        transpiler, 
        "class Test { public: void method(); };",
        "test.cpp",
        &result
    );
    
    if (result.success) {
        printf("Generated C code:\n%s\n", result.generated_c_code);
    } else {
        printf("Error: %s\n", result.error_message);
    }
    
    // Cleanup
    xc8_transpiler_result_free(&result);
    xc8_transpiler_destroy(transpiler);
    
    return 0;
}
```

## Troubleshooting

### Common Build Issues

1. **CMake can't find LLVM**
   ```
   Solution: Set LLVM_DIR environment variable
   set LLVM_DIR=C:\Program Files\LLVM\lib\cmake\llvm
   ```

2. **Clang headers not found**
   ```
   Solution: Install LLVM development package
   Windows: Download from LLVM releases page
   Linux: sudo apt-get install libclang-dev
   ```

3. **Visual Studio version mismatch**
   ```
   Solution: Use correct generator
   cmake -G "Visual Studio 16 2019" ..  # For VS 2019
   cmake -G "Visual Studio 17 2022" ..  # For VS 2022
   ```

4. **Python module import error**
   ```
   Solution: Ensure shared library is in PATH
   Windows: Add build_libtooling\lib to PATH
   Linux: Add to LD_LIBRARY_PATH
   ```

### Testing the Installation

Create a test file `test.cpp`:

```cpp
#include "device_config.h"

class Led {
public:
    Led(int pin) : pin_(pin), state_(false) {}
    void turnOn() { state_ = true; }
    void turnOff() { state_ = false; }
    bool isOn() const { return state_; }

private:
    int pin_;
    bool state_;
};

int main() {
    Led led(13);
    led.turnOn();
    return 0;
}
```

Test transpilation:

```bash
# Using CLI
xc8plusplus transpile test.cpp test.c

# Using Python
python -c "
from xc8plusplus import XC8Transpiler
t = XC8Transpiler()
print('Backend:', t.get_backend_info()['backend'])
result = t.transpile_file('test.cpp', 'test.c')
print('Success:', result.success)
"
```

## Performance Comparison

The native backend provides significant advantages:

| Feature | Native C++ | Python Fallback |
|---------|------------|-----------------|
| Speed | ~10x faster | Baseline |
| Memory | Lower usage | Higher usage |
| Accuracy | Full semantic analysis | Basic AST parsing |
| Type Safety | Complete | Limited |
| Error Detection | Comprehensive | Basic |
| XC8 Optimization | Advanced | Basic |

## Development

### Building for Development

```powershell
# Debug build with tests
.\build-scripts\build_native.ps1 -BuildType Debug -Test

# Install development tools
pip install -e ".[dev]"

# Run pre-commit hooks
pre-commit install
```

### Adding New Features

1. Modify C++ source files in `cpp/src/`
2. Update headers in `cpp/include/`
3. Add tests in `cpp/tests/`
4. Rebuild: `.\build-scripts\build_native.ps1 -Clean`
5. Test: `python test_native_integration.py`

## Next Steps

1. **Try the examples**: Start with `examples/arduino-multi/`
2. **Read the documentation**: Check `docs/` directory
3. **Contribute**: See CONTRIBUTING.md for guidelines
4. **Report issues**: Use GitHub Issues for bugs/features

## Support

- **Documentation**: See `docs/` directory
- **Examples**: Check `examples/` directory  
- **Issues**: GitHub Issues page
- **Discussions**: GitHub Discussions

The native transpiler provides professional-grade C++ to C transpilation using LLVM LibTooling semantic analysis. It's the recommended backend for production use.
