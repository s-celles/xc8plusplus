// Test C file for memory overhead baseline
#include <stdint.h>

uint8_t global_var = 0;

void simple_function(uint8_t param) {
    global_var = param;
}

int main() {
    simple_function(42);
    return 0;
}
