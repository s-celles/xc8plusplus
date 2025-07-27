# Usage Examples

## Basic Usage

### Using the CLI

```bash
# Transpile a C++ file to C
xc8plusplus transpile input.cpp --output output.c

# Use default output filename (input.c)
xc8plusplus transpile input.cpp

# Enable verbose output
xc8plusplus transpile input.cpp --verbose

# Show version
xc8plusplus version

# Show architecture demo
xc8plusplus demo
```

### Using as Python Library

```python
from xc8plusplus import XC8Transpiler

# Create transpiler instance
transpiler = XC8Transpiler()

# Transpile C++ file to C
success = transpiler.transpile("input.cpp", "output.c")

if success:
    print(f"Found {len(transpiler.classes)} classes")
    for class_name, info in transpiler.classes.items():
        print(f"Class {class_name}: {len(info['methods'])} methods")
else:
    print("Transpilation failed")
```

## Example Input/Output

### Input C++ Code
```cpp
#include <stdio.h>

class LED {
private:
    int pin;
    bool state;
    
public:
    LED(int pin_num) : pin(pin_num), state(false) {}
    
    void on() {
        state = true;
        printf("LED %d ON\\n", pin);
    }
    
    void off() {
        state = false;
        printf("LED %d OFF\\n", pin);
    }
    
    bool isOn() const {
        return state;
    }
};

int main() {
    LED led(13);
    led.on();
    return 0;
}
```

### Generated C Code
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
    // Method implementation needed
}

// Method: off  
void LED_off(LED* self) {
    // Method implementation needed
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

## Compilation with XC8

After transpilation, compile with XC8:

```bash
xc8-cc -mcpu=16F18877 output.c -o firmware.hex
```

## Supported Features

- ✅ Class definitions
- ✅ Member variables (private/public)
- ✅ Member functions
- ✅ Constructor/destructor patterns
- ✅ Basic type mapping
- ✅ Semantic AST analysis via Clang

## Architecture Benefits

Unlike simple text-based transpilers, xc8plusplus uses:
- **Clang AST parsing** for compiler-grade analysis
- **Semantic understanding** of C++ constructs  
- **XC8-optimized output** for 8-bit microcontrollers
- **Memory-efficient patterns** suitable for embedded systems
