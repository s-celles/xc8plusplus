// Complete C++ example for enhanced translator testing
// Tests method bodies, constructor initialization, and function calls

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
    
    void setValue(int newValue) {
        value = newValue;
    }
};

extern "C" int test_class() {
    SimpleClass obj;
    obj.setValue(100);
    return obj.getValue();
}
