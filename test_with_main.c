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
    self->value = 42;  // Set a test value
}

// Method: getValue
int SimpleClass_getValue(SimpleClass* self) {
    // Return the value
    return self->value;
}

// Destructor for SimpleClass
void SimpleClass_cleanup(SimpleClass* self) {
    // Cleanup SimpleClass instance
    self->value = 0;
}

// Simple test main function
int main(void) {
    SimpleClass obj;
    
    // Test constructor
    SimpleClass_init(&obj);
    
    // Test method
    int value = SimpleClass_getValue(&obj);
    
    // Test destructor
    SimpleClass_cleanup(&obj);
    
    return value == 42 ? 0 : 1;  // Return 0 if test passes
}
