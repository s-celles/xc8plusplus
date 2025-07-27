# Building XC8++ from Source

## Prerequisites

- Clang (for AST analysis)
- XC8 compiler (for testing output)
- Python 3.x (for current implementation)
- CMake (for future C++ implementation)

## Current Implementation

The current implementation uses a source-to-source translation approach:

1. **Parse C++**: Use XC8's built-in Clang for AST analysis
2. **Translate**: Convert C++ constructs to equivalent C
3. **Compile**: Use standard XC8 for generated C code

## Building the Python Transpiler

```bash
# Clone the repository
git clone <repository-url>
cd xc8plusplus

# Install dependencies (if needed)
pip install -r requirements.txt

# Test the transpiler
python src/xc8_transpiler.py examples/test.cpp output.c
```

## Future C++ Implementation

The future LibTooling-based implementation will require:

```bash
# Build the C++ implementation
mkdir build && cd build
cmake ../src
make

# Use the C++ transpiler
./xc8-transpiler input.cpp output.c
```

## Architecture Notes

### Why Source-to-Source Translation?

XC8 uses Clang 18.1.8 as its frontend, which can parse C++ correctly. However, the PIC target backend lacks C++ code generation support and crashes when attempting to generate code for C++ constructs.

This limitation requires a source-to-source translation approach rather than direct C++ compilation.

### Supported Transformations

- Classes → C structs + function pointers
- Member functions → C functions with explicit `this` parameter  
- Constructors/Destructors → Initialization/cleanup functions
- Basic inheritance → Struct composition
- Namespaces → Prefix-based naming
