// Test C++ file for memory overhead measurement
#include <stdint.h>

class SimpleClass {
    uint8_t value;
public:
    SimpleClass(uint8_t v) : value(v) {}
    void setValue(uint8_t v) { value = v; }
    uint8_t getValue() const { return value; }
};

SimpleClass global_obj(0);

int main() {
    global_obj.setValue(42);
    return 0;
}
