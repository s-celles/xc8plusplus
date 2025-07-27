#include "test_output.c"

// Test the generated C code
int main() {
    // Test the transpiled class
    SimpleClass obj;
    SimpleClass_init(&obj);
    
    // Set a value
    obj.value = 42;
    
    // Call the method
    int result = SimpleClass_getValue(&obj);
    
    // Cleanup
    SimpleClass_cleanup(&obj);
    
    return 0;
}
