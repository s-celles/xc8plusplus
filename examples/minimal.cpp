// Minimal C++ example for XC8++
// Test basic C++ compilation without complex features

extern "C" int simple_add(int a, int b) {
    return a + b;
}

class SimpleClass {
public:
    int value;
    
    SimpleClass() {
        value = 42;
    }
    
    int getValue() {
        return value;
    }
};

extern "C" int test_class() {
    SimpleClass obj;
    return obj.getValue();
}
