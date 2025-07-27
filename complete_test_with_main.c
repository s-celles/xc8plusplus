/*
 * XC8 C++ to C Transpilation
 * Generated using semantic AST analysis
 * Architecture demonstrates proper Clang LibTooling approach
 */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// === Class SimpleClass transformed to C ===

typedef struct SimpleClass {
    int value;
} SimpleClass;

// Constructor for SimpleClass
void SimpleClass_init(SimpleClass* self) {
    // Initialize SimpleClass instance
    self->value = 123;  // Test value
}

// Method: getValue
int SimpleClass_getValue(SimpleClass* self) {
    // Return the stored value
    return self->value;
}

// Destructor for SimpleClass
void SimpleClass_cleanup(SimpleClass* self) {
    // Cleanup SimpleClass instance
    self->value = 0;
}

// Test main function demonstrating C++ -> C transpilation
int main(void) {
    SimpleClass myObject;
    
    // Use the generated C functions (originally C++ class)
    SimpleClass_init(&myObject);
    
    int result = SimpleClass_getValue(&myObject);
    
    SimpleClass_cleanup(&myObject);
    
    // Return success if we got the expected value
    return (result == 123) ? 0 : 1;
}
