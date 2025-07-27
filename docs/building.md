# Building xc8plusplus

!!! warning "Development Status"
    This project is currently in active development. APIs may change between versions.

!!! info "AI-Generated Content Notice"
    A significant portion of this project's content (including code, documentation, and examples) has been generated using AI assistance. Please review all code and documentation carefully before use in production environments. We recommend thorough testing and validation of any AI-generated components.

!!! note "Unofficial Project"
    This is an unofficial, community-driven project and is not affiliated with, endorsed by, or supported by Microchip Technology Inc. The XC8 compiler and PIC microcontrollers are products of Microchip Technology Inc.

## Prerequisites

- **Python 3.8+** with pip
- **Clang/LLVM** (for AST analysis)  
- **XC8 compiler v3.00+** (for target compilation)
- **Git** (for source code)

## Quick Installation

### Production Installation
```bash
git clone https://github.com/s-celles/xc8plusplus.git
cd xc8plusplus
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/s-celles/xc8plusplus.git
cd xc8plusplus
pip install -e ".[dev]"
```

## Development Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/s-celles/xc8plusplus.git
cd xc8plusplus
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate
```

### 3. Install Development Dependencies
```bash
pip install -e ".[dev]"
```

This installs:
- **Core dependencies**: `typer[all]`, `rich`
- **Test dependencies**: `pytest`, `pytest-cov`
- **Code quality**: `black`, `isort`, `flake8`, `mypy`
- **Documentation**: `mkdocs`, `mkdocs-material`

### 4. Verify Installation
```bash
# Test CLI
xc8plusplus version
xc8plusplus demo

# Test Python API
python -c "from xc8plusplus import XC8Transpiler; print('✅ Import successful')"

# Run tests
pytest tests/ -v
```

## Package Structure

### Python Package Layout
```
xc8plusplus/
├── src/xc8plusplus/          # Main package (src-layout)
│   ├── __init__.py           # Package exports
│   ├── __main__.py           # Module execution support
│   ├── cli.py                # Typer-based CLI
│   ├── transpiler.py         # Core XC8Transpiler class
│   └── architecture_demo.py  # Demo functionality
├── tests/                    # Comprehensive test suite
│   ├── test_transpiler.py    # Core functionality tests
│   ├── test_cli.py           # CLI interface tests
│   ├── test_integration.py   # End-to-end tests
│   └── conftest.py           # Pytest configuration
├── examples/                 # Usage examples
│   ├── demo.py               # Interactive demo
│   └── USAGE.md              # Usage documentation
├── docs/                     # Documentation
├── pyproject.toml            # Modern packaging configuration
└── README.md                 # Project overview
```

### Modern Python Packaging

The project uses **modern Python packaging** standards:
- ✅ **src-layout** for clean package organization
- ✅ **pyproject.toml** for build configuration  
- ✅ **hatchling** as build backend
- ✅ **Entry points** for CLI commands
- ✅ **Optional dependencies** for development tools

## Testing

### Running Tests

The project includes a comprehensive test suite with **13/13 tests passing**.

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src/xc8plusplus --cov-report=html

# Run specific test modules
pytest tests/test_transpiler.py -v      # Core functionality
pytest tests/test_cli.py -v             # CLI interface  
pytest tests/test_integration.py -v     # End-to-end tests
```

### Test Categories

| Test Module | Purpose | Coverage |
|-------------|---------|----------|
| `test_transpiler.py` | Core XC8Transpiler functionality | Type mapping, AST analysis, class detection |
| `test_cli.py` | Command-line interface testing | CLI commands, argument parsing, error handling |
| `test_integration.py` | End-to-end workflow validation | Full transpilation process, file handling |

### Validation with Real Hardware

Tests include validation against:
- ✅ **PIC12F675** - Basic transpilation
- ✅ **PIC16F84A** - Method transformation
- ✅ **PIC16F18877** - Complex features
- ✅ **XC8 v3.00** - Real compiler integration

## Development Workflow

### Code Quality Tools

```bash
# Format code
black src/ tests/

# Sort imports  
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/xc8plusplus/

# Run all quality checks
pre-commit run --all-files
```

### Building Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

### Creating Releases

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI (when ready)
twine upload dist/*
```

## Architecture Overview

### Source-to-Source Translation Approach

The project uses **semantic AST analysis** instead of string manipulation:

1. **Clang AST Analysis** - Parse C++ with compiler-grade understanding
2. **Semantic Extraction** - Extract classes, methods, fields with full type info
3. **C Code Generation** - Transform to memory-efficient C structures
4. **XC8 Compilation** - Compile generated C code to PIC firmware

### Why This Architecture?

**XC8 Technical Reality:**
- ✅ Uses Clang 18.1.8 frontend (can parse C++)
- ❌ PIC backend lacks C++ support (crashes on C++ codegen)
- ✅ Source-to-source is the only viable approach

**Benefits:**
- 🧠 **Semantic understanding** vs text manipulation
- 🎯 **XC8 optimization** for 8-bit constraints
- 🔬 **Validated approach** with real hardware
- 🚀 **Professional quality** Python implementation

### Supported C++ → C Transformations

| C++ Feature | C Transformation | Status |
|-------------|------------------|---------|
| Classes | C structs + functions | ✅ Working |
| Member functions | Functions with `self` parameter | ✅ Working |
| Member variables | Struct fields | ✅ Working |
| Constructors | `_init()` functions | ✅ Working |
| Destructors | `_cleanup()` functions | ✅ Working |
| Basic types | XC8-compatible types | ✅ Working |
| Namespaces | Prefix-based naming | 🔄 Planned |
| Inheritance | Struct composition | 🔄 Planned |

## Troubleshooting

### Common Issues

#### 1. Clang Not Found
```bash
# Error: Clang analysis failed
# Solution: Install Clang/LLVM or ensure XC8 is installed
```

#### 2. Import Errors
```bash
# Error: Import "xc8plusplus" could not be resolved
# Solution: Install in development mode
pip install -e .
```

#### 3. Test Failures on Windows
```bash
# Error: PermissionError on temporary files
# Solution: Tests handle Windows file locking automatically
pytest tests/ -v  # Should pass on Windows
```

#### 4. CLI Command Not Found
```bash
# Error: 'xc8plusplus' is not recognized
# Solution: Reinstall package or use module execution
pip install -e . --force-reinstall
# Or use: python -m xc8plusplus
```

### Getting Help

1. **Check Documentation**: [docs/](../docs/)
2. **Review Examples**: [examples/](../examples/)
3. **Run Tests**: `pytest tests/ -v`
4. **Check Issues**: [GitHub Issues](https://github.com/s-celles/xc8plusplus/issues)

## Contributing

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create development environment: `pip install -e ".[dev]"`
4. Create feature branch: `git checkout -b feature/your-feature`
5. Make changes with tests
6. Ensure tests pass: `pytest tests/ -v`
7. Submit pull request

### Code Standards
- ✅ **Python 3.8+** compatibility
- ✅ **Type hints** for all functions
- ✅ **Docstrings** for public APIs
- ✅ **Tests** for new functionality
- ✅ **Black** formatting
- ✅ **Documentation** updates

---

**Ready to start developing? Run `pytest tests/ -v` to ensure everything works!**
