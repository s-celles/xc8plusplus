// More comprehensive C++ test for Phase 3 translator
// Tests multiple classes, inheritance concepts, and complex scenarios

#include <stdint.h>

// Test 1: Simple function with multiple parameters
extern "C" int calculate_sum(int a, int b, int c) {
    return a + b + c;
}

// Test 2: Function with different parameter types
extern "C" float calculate_average(int count, float total) {
    return total / count;
}

// Test 3: Basic class with multiple constructors (simplified)
class Counter {
public:
    int count;
    int step;
    
    Counter() { 
        count = 0; 
        step = 1; 
    }
    
    int getCount() { 
        return count; 
    }
    
    void increment() { 
        count = count + step; 
    }
    
    void setStep(int newStep) { 
        step = newStep; 
    }
    
    void reset() { 
        count = 0; 
    }
};

// Test 4: Class with different member types
class Sensor {
public:
    uint8_t id;
    float voltage;
    int status;
    
    Sensor() {
        id = 0;
        voltage = 3.3f;
        status = 1;
    }
    
    float readVoltage() {
        return voltage;
    }
    
    void setVoltage(float newVoltage) {
        voltage = newVoltage;
    }
    
    uint8_t getId() {
        return id;
    }
    
    void setId(uint8_t newId) {
        id = newId;
    }
};

// Test 5: Function using multiple classes
extern "C" int test_multiple_classes() {
    Counter counter;
    Sensor sensor;
    
    counter.setStep(5);
    counter.increment();
    counter.increment();
    
    sensor.setId(42);
    sensor.setVoltage(5.0f);
    
    return counter.getCount() + (int)sensor.readVoltage();
}

// Test 6: Function with method chaining simulation
extern "C" int test_method_sequence() {
    Counter c1;
    Counter c2;
    
    c1.setStep(10);
    c1.increment();
    
    c2.setStep(c1.getCount());
    c2.increment();
    c2.increment();
    
    return c2.getCount();
}

// Test 7: Function with conditional logic
extern "C" int test_conditional() {
    Sensor s;
    s.setVoltage(4.5f);
    
    if (s.readVoltage() > 4.0f) {
        s.setId(1);
    } else {
        s.setId(0);
    }
    
    return s.getId();
}
