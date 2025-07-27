# xc8plusplus Tests

This directory contains the test suite for the xc8plusplus transpiler.

## Test Structure

- `test_transpiler.py` - Core transpiler functionality tests
- `test_cli.py` - Command-line interface tests  
- `test_integration.py` - End-to-end integration tests
- `conftest.py` - Pytest configuration and fixtures

## Running Tests

Run all tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=src/xc8plusplus --cov-report=html
```

Run specific test modules:
```bash
pytest tests/test_transpiler.py -v
pytest tests/test_cli.py -v
pytest tests/test_integration.py -v
```

## Test Requirements

- Python 3.8+
- pytest
- pytest-cov (for coverage)
- typer (for CLI testing)

Install test dependencies:
```bash
pip install -e ".[dev]"
```

## Test Coverage

The tests cover:
- ✅ Transpiler initialization and basic functionality
- ✅ Type mapping from C++ to C
- ✅ CLI argument parsing and command execution
- ✅ File handling and error conditions
- ✅ Integration with Clang AST analysis (when available)

## Notes

- Tests handle the case where Clang is not available
- Windows file locking issues are properly handled
- Temporary files are cleaned up properly
- Tests are isolated and don't interfere with each other
