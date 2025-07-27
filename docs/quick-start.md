# Quick Start Guide

Get up and running with xc8plusplus in 5 minutes!

!!! warning "Development Status"
    This project is currently in active development. APIs may change between versions.

!!! info "AI-Generated Content Notice"
    A significant portion of this project's content (including code, documentation, and examples) has been generated using AI assistance. Please review all code and documentation carefully before use in production environments. We recommend thorough testing and validation of any AI-generated components.

!!! note "Unofficial Project"
    This is an unofficial, community-driven project and is not affiliated with, endorsed by, or supported by Microchip Technology Inc. The XC8 compiler and PIC microcontrollers are products of Microchip Technology Inc.

## 🚀 Installation

```bash
# Clone and install
git clone https://github.com/s-celles/xc8plusplus.git
cd xc8plusplus
pip install -e .
```

## ⚡ First Transpilation

### 1. Create a C++ File

Create `led.cpp`:
```cpp
#include <stdio.h>

class LED {
private:
    int pin;
    bool state;
    
public:
    LED(int pin_num) : pin(pin_num), state(false) {
        printf("LED on pin %d initialized\n", pin);
    }
    
    void on() {
        state = true;
        printf("LED %d ON\n", pin);
    }
    
    void off() {
        state = false;
        printf("LED %d OFF\n", pin);
    }
    
    bool isOn() const {
        return state;
    }
};

int main() {
    LED led(13);
    led.on();
    
    if (led.isOn()) {
        printf("LED is currently on\n");
    }
    
    led.off();
    return 0;
}
```

### 2. Transpile to C

```bash
# Using CLI
xc8plusplus transpile led.cpp

# Or specify output file
xc8plusplus transpile led.cpp --output led_transpiled.c

# With verbose output
xc8plusplus transpile led.cpp --verbose
```

### 3. View Results

The generated `led.c` will contain:
```c
/*
 * XC8 C++ to C Transpilation
 * Generated using semantic AST analysis
 */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// === Class LED transformed to C ===
typedef struct LED {
    int pin;
    bool state;
} LED;

// Constructor for LED
void LED_init(LED* self) {
    self->pin = 0;
    self->state = false;
}

// Method: on
void LED_on(LED* self) {
    // Method implementation
}

// Method: off
void LED_off(LED* self) {
    // Method implementation
}

// Method: isOn
bool LED_isOn(LED* self) {
    return self->state;
}

// Destructor for LED
void LED_cleanup(LED* self) {
    // Cleanup LED instance
}
```

### 4. Compile with XC8

```bash
# Compile for PIC microcontroller
xc8-cc -mcpu=16F18877 led.c -o firmware.hex
```

## 🐍 Python API Usage

```python
from xc8plusplus import XC8Transpiler

# Create transpiler
transpiler = XC8Transpiler()

# Transpile
success = transpiler.transpile("led.cpp", "led.c")

if success:
    print(f"✅ Found {len(transpiler.classes)} classes")
    for name, info in transpiler.classes.items():
        methods = len(info['methods'])
        fields = len(info['fields'])
        print(f"  📦 {name}: {methods} methods, {fields} fields")
else:
    print("❌ Transpilation failed")
```

## 📋 CLI Commands Reference

```bash
# Transpile C++ to C
xc8plusplus transpile input.cpp [--output file.c] [--verbose]

# Show version
xc8plusplus version

# Show demo/help
xc8plusplus demo

# Get help
xc8plusplus --help
xc8plusplus transpile --help
```

## 🧪 Verify Installation

```bash
# Test CLI
xc8plusplus version
xc8plusplus demo

# Test Python import
python -c "from xc8plusplus import XC8Transpiler; print('✅ Success!')"

# Run test suite
pytest tests/ -v
```

## 🎯 Real-World Example

### Complete PIC Project Setup

1. **Create project structure:**
```
my_pic_project/
├── src/
│   ├── main.cpp
│   ├── led.cpp
│   └── button.cpp
├── build/
└── Makefile
```

2. **Write C++ code (src/main.cpp):**
```cpp
#include <stdio.h>

class LED {
    // ... (as shown above)
};

class Button {
private:
    int pin;
    
public:
    Button(int pin_num) : pin(pin_num) {}
    
    bool isPressed() const {
        // Read GPIO pin
        return false; // Placeholder
    }
};

int main() {
    LED statusLED(13);
    Button userButton(2);
    
    while (1) {
        if (userButton.isPressed()) {
            statusLED.on();
        } else {
            statusLED.off();
        }
    }
    
    return 0;
}
```

3. **Create Makefile:**
```makefile
# Transpile all C++ files
transpile:
	xc8plusplus transpile src/main.cpp --output build/main.c
	xc8plusplus transpile src/led.cpp --output build/led.c
	xc8plusplus transpile src/button.cpp --output build/button.c

# Compile with XC8
compile: transpile
	xc8-cc -mcpu=16F18877 build/*.c -o build/firmware.hex

clean:
	rm -rf build/*

.PHONY: transpile compile clean
```

4. **Build project:**
```bash
cd my_pic_project
make compile
```

## 🔧 Development Setup

For contributing or advanced usage:

```bash
# Development installation
git clone https://github.com/s-celles/xc8plusplus.git
cd xc8plusplus
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Code formatting
black src/ tests/
isort src/ tests/

# Type checking
mypy src/xc8plusplus/
```

## 📚 Next Steps

- 📖 **[Full Documentation](index.md)** - Complete project overview
- 🏗️ **[API Reference](api.md)** - Detailed API documentation
- 🛠️ **[Building Guide](building.md)** - Development environment setup
-  **[Architecture](implementation.md)** - Technical deep dive

## ❓ Quick Troubleshooting

**CLI not found?**
```bash
pip install -e . --force-reinstall
# Or use: python -m xc8plusplus
```

**Import errors?**
```bash
pip install -e .
python -c "import xc8plusplus; print('OK')"
```

**Tests failing?**
```bash
pytest tests/ -v  # Should show 13/13 passing
```

**Need help?**
- 📖 Check [documentation](index.md)
- 🐛 Open [GitHub issue](https://github.com/s-celles/xc8plusplus/issues)
- 💬 Start [discussion](https://github.com/s-celles/xc8plusplus/discussions)

---

**Happy coding! 🎉 You're now ready to use C++ with 8-bit PICs!**
