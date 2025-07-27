#!/usr/bin/env python3
"""
Example script showing how to use xc8plusplus transpiler.
"""

import tempfile
import os
from pathlib import Path

from xc8plusplus import XC8Transpiler


def main():
    """Demonstrate xc8plusplus transpiler usage."""

    print("🔧 xc8plusplus Transpiler Demo")
    print("=" * 40)

    # Sample C++ code with a simple class
    sample_cpp = """
#include <stdio.h>

class LED {
private:
    int pin;
    bool state;
    
public:
    LED(int pin_num) : pin(pin_num), state(false) {
        printf("LED initialized on pin %d\\n", pin);
    }
    
    void on() {
        state = true;
        printf("LED on pin %d is ON\\n", pin);
    }
    
    void off() {
        state = false;
        printf("LED on pin %d is OFF\\n", pin);
    }
    
    bool isOn() const {
        return state;
    }
};

int main() {
    LED led1(13);
    LED led2(12);
    
    led1.on();
    led2.off();
    
    if (led1.isOn()) {
        printf("LED1 is currently on\\n");
    }
    
    return 0;
}
"""

    print("📝 Sample C++ Code:")
    print(sample_cpp)
    print("\n" + "=" * 40)

    # Create temporary files
    with tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False) as cpp_file:
        cpp_file.write(sample_cpp)
        cpp_file.flush()
        cpp_path = cpp_file.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as c_file:
        c_path = c_file.name

    try:
        # Create transpiler instance
        transpiler = XC8Transpiler()

        print("🔄 Transpiling C++ to C...")
        success = transpiler.transpile(cpp_path, c_path)

        if success:
            print("✅ Transpilation successful!")

            # Show results
            with open(c_path, "r") as f:
                c_code = f.read()

            print(f"\n📊 Analysis Results:")
            print(f"   Classes found: {len(transpiler.classes)}")
            for class_name, info in transpiler.classes.items():
                print(
                    f"   • {class_name}: {len(info['methods'])} methods, {len(info['fields'])} fields"
                )

            print(f"\n📄 Generated C Code:")
            print("-" * 40)
            print(c_code)
            print("-" * 40)

            print(f"\n💡 To compile with XC8:")
            print(f"   xc8-cc -mcpu=16F18877 {Path(c_path).name} -o firmware.hex")

        else:
            print("❌ Transpilation failed")
            print("   Note: This may be expected if Clang is not available")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        # Clean up
        try:
            os.unlink(cpp_path)
            os.unlink(c_path)
        except:
            pass


if __name__ == "__main__":
    main()
