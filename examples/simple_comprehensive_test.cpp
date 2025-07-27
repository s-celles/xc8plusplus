// Simplified comprehensive test for Phase 3 translator
// Focuses on core features without complex control flow

// Test 1: Functions with multiple parameters
extern "C" int add_three(int a, int b, int c) {
    return a + b + c;
}

extern "C" float divide_numbers(float numerator, float denominator) {
    return numerator / denominator;
}

// Test 2: Simple class with multiple members
class Calculator {
public:
    int result;
    int memory;
    
    Calculator() {
        result = 0;
        memory = 0;
    }
    
    void add(int value) {
        result = result + value;
    }
    
    void subtract(int value) {
        result = result - value;
    }
    
    void store() {
        memory = result;
    }
    
    void recall() {
        result = memory;
    }
    
    int getResult() {
        return result;
    }
};

// Test 3: Class with different data types
class Sensor {
public:
    float voltage;
    int status;
    
    Sensor() {
        voltage = 3.3f;
        status = 1;
    }
    
    void setVoltage(float v) {
        voltage = v;
    }
    
    float getVoltage() {
        return voltage;
    }
    
    void setStatus(int s) {
        status = s;
    }
    
    int getStatus() {
        return status;
    }
};

// Test 4: Function using multiple class instances
extern "C" int test_calculator() {
    Calculator calc;
    calc.add(10);
    calc.add(5);
    calc.subtract(3);
    return calc.getResult();
}

// Test 5: Function with multiple objects
extern "C" int test_multiple_objects() {
    Calculator calc1;
    Calculator calc2;
    Sensor sensor;
    
    calc1.add(20);
    calc1.store();
    
    calc2.add(30);
    sensor.setVoltage(5.0f);
    
    return calc1.getResult() + calc2.getResult();
}
