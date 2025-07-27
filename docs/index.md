# xc8plusplus Documentation

Welcome to the xc8plusplus documentation. This project provides C++ to C transpilation for Microchip's XC8 compiler, enabling C++ development for 8-bit PIC microcontrollers.

## Quick Links

- [Getting Started](#getting-started)
- [Architecture](#architecture) 
- [Research](#research)
- [Development](#development)

## Getting Started

### Installation & Usage
- **[Building](building.md)** - How to build and set up xc8plusplus
- **[Implementation](implementation.md)** - Technical architecture and source code overview

### Quick Start
```bash
# Transpile C++ to C
python src/xc8_transpiler.py input.cpp output.c

# Compile with XC8
xc8 output.c
```

## Architecture

### Core Concepts
- **Source-to-Source Translation**: C++ code is parsed with Clang AST and transformed to equivalent C
- **Semantic Analysis**: Uses compiler-grade parsing instead of string manipulation
- **XC8 Compatibility**: Generated C code follows XC8 conventions and memory constraints

### Why This Approach?
- **[Design Decisions](why-python-is-wrong.md)** - Why we use AST analysis instead of string manipulation
- **[XC8 Architecture](xc8-architecture.md)** - Technical analysis of XC8 compiler internals

## Research

### Technical Findings
- **[Research Findings](research-findings.md)** - Project status, achievements, and technical discoveries
- **[Memory Constraints](memory-constraints.md)** - Analysis of 8-bit PIC memory limitations
- **[XC8 Source Research](xc8-source-research.md)** - Investigation of XC8 compiler source code

### Key Discoveries
1. **XC8 uses Clang 18.1.8** as frontend (not GCC)
2. **PIC backend lacks C++ support** - crashes on C++ code generation
3. **Source-to-source translation** is the viable approach
4. **Memory constraints** guide C++ feature selection

## Development

### Current Status
- ✅ **Working transpiler** using Clang AST analysis
- ✅ **Generated C code compiles** with XC8
- ✅ **Semantic transformation** approach proven
- 🔄 **Feature expansion** ongoing

### Supported Features
- Classes → C structs + function pointers
- Member functions → C functions with explicit `this`
- Constructors/Destructors → Init/cleanup functions
- Basic inheritance → Struct composition (planned)

### Contributing
The project uses Apache 2.0 + LLVM Exceptions license (same as Clang) to ensure compatibility with LLVM ecosystem tools.

## File Overview

| File | Purpose |
|------|---------|
| `building.md` | Build instructions and setup |
| `implementation.md` | Technical architecture details |
| `research-findings.md` | Project status and achievements |
| `why-python-is-wrong.md` | Design decision rationale |
| `xc8-architecture.md` | XC8 compiler analysis |
| `memory-constraints.md` | 8-bit PIC memory analysis |
| `xc8-source-research.md` | Source code investigation |
