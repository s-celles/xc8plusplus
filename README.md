# xc8plusplus 🔧

**Professional C++ to C transpiler for Microchip's XC8 compiler**

Enables modern C++ development for 8-bit PIC microcontrollers using semantic AST analysis.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: Apache 2.0 + LLVM](https://img.shields.io/badge/License-Apache%202.0%20+%20LLVM-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-13%2F13%20passing-brightgreen.svg)](tests/)

> [!WARNING]  
> **Development Status**: This project is currently in active development. APIs may change between versions.

> [!NOTE]  
> **AI-Generated Content**: A significant portion of this project's content (including code, documentation, and examples) has been generated using AI assistance. Please review all code and documentation carefully before use in production environments.

> [!IMPORTANT]  
> **Unofficial Project**: This is an unofficial, community-driven project and is not affiliated with, endorsed by, or supported by Microchip Technology Inc. The XC8 compiler and PIC microcontrollers are products of Microchip Technology Inc.

## Quick Start

```bash
# Install
git clone https://github.com/s-celles/xc8plusplus.git
cd xc8plusplus
pip install -e .

# Use CLI
xc8plusplus transpile input.cpp --output output.c
xc8plusplus version

# Use Python API
python -c "from xc8plusplus import XC8Transpiler; print('Ready!')"

# Run tests
pytest tests/ -v
```

## Key Features

- 🧠 **Semantic AST Analysis** - Uses Clang for compiler-grade C++ understanding
- 🎯 **XC8 Optimized** - Memory-efficient C code for 8-bit microcontrollers
- 🚀 **Modern CLI** - Rich terminal interface with Typer and Rich
- 📦 **Python Library** - Modern packaging with both CLI and programmatic APIs
- 🔬 **Battle Tested** - Validated with XC8 v3.00 on multiple PIC targets

## Documentation

� **Complete documentation**: https://s-celles.github.io/xc8plusplus

- [Quick Start Guide](docs/quick-start.md) - Get up and running in 5 minutes
- [API Reference](docs/api.md) - Complete CLI and Python API documentation
- [Building Guide](docs/building.md) - Development environment setup
- [Architecture](docs/implementation.md) - Technical deep dive

## Example

**Input C++:**
```cpp
class LED {
private:
    int pin;
    bool state;
public:
    LED(int pin_num) : pin(pin_num), state(false) {}
    void on() { state = true; }
    bool isOn() const { return state; }
};
```

**Generated C:**
```c
typedef struct LED {
    int pin;
    bool state;
} LED;

void LED_init(LED* self) { /* ... */ }
void LED_on(LED* self) { /* ... */ }
bool LED_isOn(LED* self) { return self->state; }
```

**Compile:**
```bash
xc8-cc -mcpu=16F18877 output.c -o firmware.hex
```

## License

Apache License v2.0 with LLVM Exceptions (same as Clang/LLVM)

---

**Made with ❤️ for the embedded C++ community**
