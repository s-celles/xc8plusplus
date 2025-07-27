// Advanced C++ Features Test: Templates, Operator Overloading, and Complex Patterns
// Tests advanced C++ features suitable for 8-bit PIC microcontrollers
// Focus on features that can be efficiently translated to C

#include <stdint.h>

// =============================================================================
// Test 1: Simple Function Templates (Compile-time Specialization)
// =============================================================================

// Template function for maximum (should generate multiple C functions)
template<typename T>
T getMax(T a, T b) {
    return (a > b) ? a : b;
}

// Template specializations that the transpiler should handle
extern "C" int test_function_templates() {
    // These should generate separate C functions: getMax_int, getMax_float, getMax_uint8_t
    int maxInt = getMax<int>(10, 20);
    float maxFloat = getMax<float>(3.14f, 2.71f);
    uint8_t maxByte = getMax<uint8_t>(100, 150);
    
    return maxInt + (int)maxFloat + maxByte; // Return sum for verification
}

// =============================================================================
// Test 2: Simple Class Templates
// =============================================================================

// Template class for a generic buffer
template<typename T, uint8_t SIZE>
class Buffer {
private:
    T data[SIZE];
    uint8_t count;
    
public:
    Buffer() : count(0) {
        // Initialize all elements to default value
        for (uint8_t i = 0; i < SIZE; i++) {
            data[i] = T();
        }
    }
    
    bool add(T value) {
        if (count < SIZE) {
            data[count] = value;
            count++;
            return true;
        }
        return false;
    }
    
    T get(uint8_t index) const {
        if (index < count) {
            return data[index];
        }
        return T(); // Default value
    }
    
    uint8_t size() const {
        return count;
    }
    
    void clear() {
        count = 0;
    }
};

extern "C" int test_class_templates() {
    // Should generate: Buffer_int_8, Buffer_float_4, etc.
    Buffer<int, 8> intBuffer;
    Buffer<float, 4> floatBuffer;
    Buffer<uint8_t, 16> byteBuffer;
    
    // Test operations
    intBuffer.add(42);
    intBuffer.add(100);
    
    floatBuffer.add(3.14f);
    floatBuffer.add(2.71f);
    
    byteBuffer.add(255);
    byteBuffer.add(128);
    byteBuffer.add(64);
    
    // Return combined results
    return intBuffer.get(0) + (int)floatBuffer.get(1) + byteBuffer.size();
}

// =============================================================================
// Test 3: Operator Overloading
// =============================================================================

// Simple Point class with operator overloading
class Point {
private:
    int16_t x, y;
    
public:
    Point(int16_t xPos = 0, int16_t yPos = 0) : x(xPos), y(yPos) {}
    
    // Getters
    int16_t getX() const { return x; }
    int16_t getY() const { return y; }
    
    // Setters
    void setX(int16_t xPos) { x = xPos; }
    void setY(int16_t yPos) { y = yPos; }
    
    // Addition operator (should become Point_add function)
    Point operator+(const Point& other) const {
        return Point(x + other.x, y + other.y);
    }
    
    // Subtraction operator
    Point operator-(const Point& other) const {
        return Point(x - other.x, y - other.y);
    }
    
    // Equality operator
    bool operator==(const Point& other) const {
        return (x == other.x) && (y == other.y);
    }
    
    // Assignment operator
    Point& operator=(const Point& other) {
        if (this != &other) {
            x = other.x;
            y = other.y;
        }
        return *this;
    }
    
    // Compound assignment
    Point& operator+=(const Point& other) {
        x += other.x;
        y += other.y;
        return *this;
    }
};

extern "C" int test_operator_overloading() {
    Point p1(10, 20);
    Point p2(30, 40);
    
    // Test addition operator
    Point p3 = p1 + p2; // Should become Point_add(&p1, &p2)
    
    // Test subtraction
    Point p4 = p2 - p1; // Should become Point_subtract(&p2, &p1)
    
    // Test compound assignment
    p1 += p2; // Should become Point_compound_add(&p1, &p2)
    
    // Test equality
    bool equal = (p1 == p2); // Should become Point_equals(&p1, &p2)
    
    return p3.getX() + p3.getY() + (equal ? 1 : 0);
}

// =============================================================================
// Test 4: Function Overloading with Different Parameter Types
// =============================================================================

class MathUtils {
public:
    // Overloaded static-like methods (all should become separate C functions)
    static int add(int a, int b) {
        return a + b;
    }
    
    static float add(float a, float b) {
        return a + b;
    }
    
    static int add(int a, int b, int c) {
        return a + b + c;
    }
    
    static uint8_t add(uint8_t a, uint8_t b) {
        return a + b; // Handle overflow naturally
    }
    
    // Overloaded methods with different semantics
    static int multiply(int a, int b) {
        return a * b;
    }
    
    static float multiply(float a, float b) {
        return a * b;
    }
    
    // Mixed parameter types
    static float scale(int value, float factor) {
        return (float)value * factor;
    }
    
    static int scale(float value, int factor) {
        return (int)(value * (float)factor);
    }
};

extern "C" int test_function_overloading() {
    // Should generate: MathUtils_add_int_int, MathUtils_add_float_float, etc.
    int result1 = MathUtils::add(10, 20);
    float result2 = MathUtils::add(3.14f, 2.86f);
    int result3 = MathUtils::add(1, 2, 3);
    uint8_t result4 = MathUtils::add((uint8_t)100, (uint8_t)50);
    
    int product = MathUtils::multiply(5, 6);
    float scaled1 = MathUtils::scale(10, 1.5f);
    int scaled2 = MathUtils::scale(7.5f, 3);
    
    return result1 + (int)result2 + result3 + result4 + product + (int)scaled1 + scaled2;
}

// =============================================================================
// Test 5: Namespace-like Functionality (Using Classes as Namespaces)
// =============================================================================

class GPIO {
public:
    // Pin manipulation functions
    static void setPin(uint8_t pin, bool value) {
        // Would generate actual GPIO code for XC8
        // For testing, just store the operation
    }
    
    static bool readPin(uint8_t pin) {
        // Would read actual GPIO for XC8
        return (pin % 2) == 0; // Dummy implementation
    }
    
    static void togglePin(uint8_t pin) {
        // Would toggle actual GPIO for XC8
    }
};

class ADC {
public:
    static uint16_t read(uint8_t channel) {
        // Would read actual ADC for XC8
        return (uint16_t)(channel * 100); // Dummy implementation
    }
    
    static void setReference(uint8_t ref) {
        // Would set ADC reference for XC8
    }
};

class PWM {
public:
    static void setDutyCycle(uint8_t channel, uint8_t duty) {
        // Would set PWM duty cycle for XC8
    }
    
    static void enable(uint8_t channel) {
        // Would enable PWM channel for XC8
    }
    
    static void disable(uint8_t channel) {
        // Would disable PWM channel for XC8
    }
};

extern "C" int test_namespace_like_classes() {
    // Should generate: GPIO_setPin, GPIO_readPin, ADC_read, PWM_setDutyCycle, etc.
    GPIO::setPin(2, true);
    bool pinState = GPIO::readPin(2);
    
    uint16_t adcValue = ADC::read(3);
    
    PWM::setDutyCycle(1, 128);
    PWM::enable(1);
    
    return (int)adcValue + (pinState ? 1 : 0);
}

// =============================================================================
// Test 6: Complex Constructor and Destructor Patterns
// =============================================================================

class ResourceManager {
private:
    uint8_t* buffer;
    uint8_t size;
    bool allocated;
    
public:
    // Constructor with resource allocation
    ResourceManager(uint8_t bufferSize) : size(bufferSize), allocated(false) {
        // In real implementation, would allocate from static pool
        // For 8-bit PICs, avoid dynamic allocation
        buffer = nullptr; // Simplified for testing
        allocated = true;
    }
    
    // Copy constructor (should be converted to copy function)
    ResourceManager(const ResourceManager& other) : size(other.size), allocated(false) {
        if (other.allocated) {
            // Copy implementation
            buffer = nullptr; // Simplified
            allocated = true;
        }
    }
    
    // Destructor (should become cleanup function)
    ~ResourceManager() {
        if (allocated && buffer != nullptr) {
            // Would free from static pool
            buffer = nullptr;
            allocated = false;
        }
    }
    
    // Assignment operator
    ResourceManager& operator=(const ResourceManager& other) {
        if (this != &other) {
            // Cleanup current
            if (allocated && buffer != nullptr) {
                buffer = nullptr;
            }
            
            // Copy from other
            size = other.size;
            if (other.allocated) {
                allocated = true;
            }
        }
        return *this;
    }
    
    bool isAllocated() const {
        return allocated;
    }
    
    uint8_t getSize() const {
        return size;
    }
};

extern "C" int test_resource_management() {
    ResourceManager rm1(64);
    ResourceManager rm2(32);
    
    // Test copy constructor
    ResourceManager rm3(rm1);
    
    // Test assignment
    rm2 = rm1;
    
    return rm1.getSize() + rm2.getSize() + rm3.getSize() + 
           (rm1.isAllocated() ? 1 : 0) + (rm2.isAllocated() ? 1 : 0) + (rm3.isAllocated() ? 1 : 0);
}

// =============================================================================
// Test 7: Const Correctness and References
// =============================================================================

class DataContainer {
private:
    int16_t data[4];
    uint8_t count;
    
public:
    DataContainer() : count(0) {
        for (uint8_t i = 0; i < 4; i++) {
            data[i] = 0;
        }
    }
    
    // Const method
    const int16_t& getValue(uint8_t index) const {
        static int16_t defaultValue = 0;
        if (index < count) {
            return data[index];
        }
        return defaultValue;
    }
    
    // Non-const method
    int16_t& getValue(uint8_t index) {
        static int16_t defaultValue = 0;
        if (index < count) {
            return data[index];
        }
        return defaultValue;
    }
    
    void addValue(const int16_t& value) {
        if (count < 4) {
            data[count] = value;
            count++;
        }
    }
    
    uint8_t getCount() const {
        return count;
    }
    
    // Method taking const reference
    void processData(const DataContainer& other) {
        for (uint8_t i = 0; i < other.getCount() && count < 4; i++) {
            addValue(other.getValue(i));
        }
    }
};

extern "C" int test_const_correctness() {
    DataContainer container1;
    container1.addValue(10);
    container1.addValue(20);
    
    const DataContainer container2 = container1;
    
    // Test const method access
    int16_t value = container2.getValue(0);
    
    // Test reference parameters
    DataContainer container3;
    container3.processData(container1);
    
    return value + container3.getCount();
}

// =============================================================================
// Test 8: Static Members and Methods
// =============================================================================

class Counter {
private:
    static uint16_t globalCount;
    int16_t instanceValue;
    
public:
    Counter(int16_t value) : instanceValue(value) {
        globalCount++;
    }
    
    ~Counter() {
        if (globalCount > 0) {
            globalCount--;
        }
    }
    
    static uint16_t getGlobalCount() {
        return globalCount;
    }
    
    static void resetGlobalCount() {
        globalCount = 0;
    }
    
    int16_t getInstanceValue() const {
        return instanceValue;
    }
    
    void setInstanceValue(int16_t value) {
        instanceValue = value;
    }
    
    // Static method accessing static data
    static bool hasInstances() {
        return globalCount > 0;
    }
};

// Static member definition (should become global variable in C)
uint16_t Counter::globalCount = 0;

extern "C" int test_static_members() {
    Counter::resetGlobalCount();
    
    Counter c1(100);
    Counter c2(200);
    
    uint16_t count1 = Counter::getGlobalCount(); // Should be 2
    
    uint16_t count2;
    {
        Counter c3(300);
        count2 = Counter::getGlobalCount(); // Should be 3
    }
    // c3 destroyed here
    
    uint16_t count3 = Counter::getGlobalCount(); // Should be 2 again
    bool hasInst = Counter::hasInstances();
    
    return count1 + count2 + count3 + (hasInst ? 1 : 0) + c1.getInstanceValue() + c2.getInstanceValue();
}

// =============================================================================
// Integration Test: Complex Real-World Example
// =============================================================================

// Simulate a complete sensor system with multiple advanced features
template<uint8_t MAX_SENSORS>
class SensorSystem {
private:
    struct SensorData {
        uint8_t id;
        float value;
        bool active;
        
        SensorData() : id(0), value(0.0f), active(false) {}
        SensorData(uint8_t sensorId) : id(sensorId), value(0.0f), active(false) {}
    };
    
    SensorData sensors[MAX_SENSORS];
    uint8_t sensorCount;
    static uint16_t totalReadings;
    
public:
    SensorSystem() : sensorCount(0) {}
    
    bool addSensor(uint8_t id) {
        if (sensorCount < MAX_SENSORS) {
            sensors[sensorCount] = SensorData(id);
            sensorCount++;
            return true;
        }
        return false;
    }
    
    bool updateSensor(uint8_t id, float value) {
        for (uint8_t i = 0; i < sensorCount; i++) {
            if (sensors[i].id == id) {
                sensors[i].value = value;
                sensors[i].active = true;
                totalReadings++;
                return true;
            }
        }
        return false;
    }
    
    float getSensorValue(uint8_t id) const {
        for (uint8_t i = 0; i < sensorCount; i++) {
            if (sensors[i].id == id && sensors[i].active) {
                return sensors[i].value;
            }
        }
        return 0.0f;
    }
    
    uint8_t getActiveSensorCount() const {
        uint8_t count = 0;
        for (uint8_t i = 0; i < sensorCount; i++) {
            if (sensors[i].active) {
                count++;
            }
        }
        return count;
    }
    
    static uint16_t getTotalReadings() {
        return totalReadings;
    }
    
    // Operator overloading for combining systems
    SensorSystem operator+(const SensorSystem& other) const {
        SensorSystem combined;
        
        // Add sensors from this system
        for (uint8_t i = 0; i < sensorCount && combined.sensorCount < MAX_SENSORS; i++) {
            combined.sensors[combined.sensorCount] = sensors[i];
            combined.sensorCount++;
        }
        
        // Add sensors from other system
        for (uint8_t i = 0; i < other.sensorCount && combined.sensorCount < MAX_SENSORS; i++) {
            combined.sensors[combined.sensorCount] = other.sensors[i];
            combined.sensorCount++;
        }
        
        return combined;
    }
};

template<uint8_t MAX_SENSORS>
uint16_t SensorSystem<MAX_SENSORS>::totalReadings = 0;

extern "C" int test_complex_system() {
    SensorSystem<8> system1;
    SensorSystem<8> system2;
    
    // Add sensors
    system1.addSensor(1);
    system1.addSensor(2);
    system1.updateSensor(1, 23.5f);
    system1.updateSensor(2, 45.2f);
    
    system2.addSensor(3);
    system2.addSensor(4);
    system2.updateSensor(3, 12.1f);
    system2.updateSensor(4, 67.8f);
    
    // Test operator overloading
    SensorSystem<8> combined = system1 + system2;
    
    uint8_t activeCount = combined.getActiveSensorCount();
    uint16_t totalReadings = SensorSystem<8>::getTotalReadings();
    
    return (int)(system1.getSensorValue(1) + system2.getSensorValue(3)) + activeCount + totalReadings;
}
