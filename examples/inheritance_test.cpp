// Advanced C++ Features Test: Inheritance and Polymorphism for XC8++
// Tests inheritance patterns suitable for 8-bit PIC microcontrollers
// Focus on simple inheritance that can be translated to C struct composition

#include <stdint.h>

// =============================================================================
// Test 1: Simple Single Inheritance
// =============================================================================

// Base class for all devices
class Device {
protected:
    uint8_t id;
    bool enabled;
    
public:
    Device(uint8_t deviceId) : id(deviceId), enabled(false) {
        // Base constructor
    }
    
    void enable() {
        enabled = true;
    }
    
    void disable() {
        enabled = false;
    }
    
    bool isEnabled() const {
        return enabled;
    }
    
    uint8_t getId() const {
        return id;
    }
};

// Derived class for sensors
class Sensor : public Device {
private:
    float lastReading;
    
public:
    Sensor(uint8_t sensorId) : Device(sensorId), lastReading(0.0f) {
        // Derived constructor
    }
    
    void setReading(float value) {
        lastReading = value;
    }
    
    float getReading() const {
        return lastReading;
    }
    
    // Method that uses base class functionality
    float getEnabledReading() {
        if (isEnabled()) {
            return lastReading;
        }
        return 0.0f;
    }
};

// =============================================================================
// Test 2: Multiple Derived Classes from Same Base
// =============================================================================

// Another derived class for actuators
class Actuator : public Device {
private:
    uint8_t position;
    uint8_t targetPosition;
    
public:
    Actuator(uint8_t actuatorId) : Device(actuatorId), position(0), targetPosition(0) {
        // Actuator constructor
    }
    
    void setTarget(uint8_t target) {
        targetPosition = target;
    }
    
    void moveToTarget() {
        if (isEnabled()) {
            position = targetPosition;
        }
    }
    
    uint8_t getPosition() const {
        return position;
    }
    
    bool atTarget() const {
        return position == targetPosition;
    }
};

// =============================================================================
// Test 3: Two-level Inheritance Hierarchy
// =============================================================================

// Specialized temperature sensor
class TemperatureSensor : public Sensor {
private:
    float temperatureOffset;
    
public:
    TemperatureSensor(uint8_t sensorId, float offset) 
        : Sensor(sensorId), temperatureOffset(offset) {
        // Two-level inheritance constructor
    }
    
    void calibrate(float offset) {
        temperatureOffset = offset;
    }
    
    float getCalibratedTemperature() {
        return getReading() + temperatureOffset;
    }
    
    // Method using multiple inheritance levels
    bool isValidReading() {
        return isEnabled() && (getReading() > -50.0f && getReading() < 150.0f);
    }
};

// =============================================================================
// Test 4: Virtual-like Behavior (Without Virtual Keywords)
// =============================================================================

// Base class for processors with different processing methods
class DataProcessor {
protected:
    uint8_t processorType;
    
public:
    DataProcessor(uint8_t type) : processorType(type) {}
    
    // Non-virtual method that derived classes will "override"
    float process(float input) {
        return input; // Default: pass-through
    }
    
    uint8_t getType() const {
        return processorType;
    }
};

// Derived processor with specific processing
class FilterProcessor : public DataProcessor {
private:
    float filterCoeff;
    float lastOutput;
    
public:
    FilterProcessor(float coeff) : DataProcessor(1), filterCoeff(coeff), lastOutput(0.0f) {}
    
    // "Override" the process method (static dispatch)
    float process(float input) {
        lastOutput = (filterCoeff * input) + ((1.0f - filterCoeff) * lastOutput);
        return lastOutput;
    }
    
    void reset() {
        lastOutput = 0.0f;
    }
};

// =============================================================================
// Test 5: Composition Pattern (Alternative to Multiple Inheritance)
// =============================================================================

// Since multiple inheritance is complex, use composition
class SmartSensor {
private:
    Sensor sensor;
    DataProcessor* processor;
    
public:
    SmartSensor(uint8_t id, DataProcessor* proc) : sensor(id), processor(proc) {}
    
    void enable() {
        sensor.enable();
    }
    
    void setRawReading(float value) {
        sensor.setReading(value);
    }
    
    float getProcessedReading() {
        if (sensor.isEnabled() && processor != nullptr) {
            return processor->process(sensor.getReading());
        }
        return 0.0f;
    }
    
    uint8_t getId() const {
        return sensor.getId();
    }
};

// =============================================================================
// Test Functions for Inheritance Features
// =============================================================================

extern "C" int test_simple_inheritance() {
    Sensor tempSensor(1);
    tempSensor.enable();
    tempSensor.setReading(23.5f);
    
    // Test base class methods through derived object
    if (tempSensor.isEnabled() && tempSensor.getId() == 1) {
        return (int)(tempSensor.getEnabledReading() * 10); // Return 235
    }
    
    return 0;
}

extern "C" int test_multiple_derived_classes() {
    Sensor sensor(1);
    Actuator actuator(2);
    
    // Enable both devices
    sensor.enable();
    actuator.enable();
    
    // Set values
    sensor.setReading(42.0f);
    actuator.setTarget(75);
    actuator.moveToTarget();
    
    // Test that both work correctly
    return (int)(sensor.getReading()) + actuator.getPosition(); // Return 117
}

extern "C" int test_two_level_inheritance() {
    TemperatureSensor tempSensor(3, 2.5f);
    tempSensor.enable();
    tempSensor.setReading(20.0f);
    
    // Test methods from all levels of inheritance
    if (tempSensor.isValidReading()) {
        return (int)(tempSensor.getCalibratedTemperature() * 10); // Return 225
    }
    
    return 0;
}

extern "C" int test_polymorphic_behavior() {
    FilterProcessor filter(0.8f);
    
    // Process multiple values through the filter
    float result1 = filter.process(10.0f);
    float result2 = filter.process(20.0f);
    float result3 = filter.process(15.0f);
    
    return (int)(result3 * 10); // Return filtered result
}

extern "C" int test_composition_pattern() {
    FilterProcessor filter(0.5f);
    SmartSensor smartSensor(4, &filter);
    
    smartSensor.enable();
    smartSensor.setRawReading(100.0f);
    
    float processed1 = smartSensor.getProcessedReading();
    smartSensor.setRawReading(200.0f);
    float processed2 = smartSensor.getProcessedReading();
    
    return (int)(processed2); // Return processed reading
}

extern "C" int test_inheritance_memory_efficiency() {
    // Test that inheritance doesn't add excessive memory overhead
    Device device(1);
    Sensor sensor(2);
    TemperatureSensor tempSensor(3, 1.0f);
    
    // All should have compact memory layout
    device.enable();
    sensor.enable();
    sensor.setReading(50.0f);
    tempSensor.enable();
    tempSensor.setReading(25.0f);
    
    // Return sum of IDs to verify all objects work
    return device.getId() + sensor.getId() + tempSensor.getId(); // Return 6
}

// =============================================================================
// Test 6: Advanced Feature - Method Overloading in Inheritance
// =============================================================================

class AdvancedSensor : public Sensor {
public:
    AdvancedSensor(uint8_t id) : Sensor(id) {}
    
    // Overloaded methods for different data types
    void setReading(int value) {
        Sensor::setReading((float)value);
    }
    
    void setReading(float value) {
        Sensor::setReading(value);
    }
    
    void setReading(uint8_t value) {
        Sensor::setReading((float)value);
    }
};

extern "C" int test_overloading_with_inheritance() {
    AdvancedSensor sensor(5);
    sensor.enable();
    
    // Test different overloaded methods
    sensor.setReading(42);        // int version
    float result1 = sensor.getReading();
    
    sensor.setReading(3.14f);     // float version
    float result2 = sensor.getReading();
    
    sensor.setReading((uint8_t)100); // uint8_t version
    float result3 = sensor.getReading();
    
    return (int)(result1 + result2 + result3); // Return sum
}

// =============================================================================
// Test 7: Constructor Chaining and Member Initialization
// =============================================================================

class ComplexDevice : public Device {
private:
    uint16_t serialNumber;
    float calibrationFactor;
    
public:
    // Constructor with member initialization list
    ComplexDevice(uint8_t id, uint16_t serial, float calibration) 
        : Device(id), serialNumber(serial), calibrationFactor(calibration) {
        // Test proper constructor chaining
    }
    
    uint16_t getSerial() const {
        return serialNumber;
    }
    
    float getCalibration() const {
        return calibrationFactor;
    }
    
    // Method using multiple inherited and own members
    float getAdjustedId() const {
        return (float)getId() * calibrationFactor;
    }
};

extern "C" int test_constructor_chaining() {
    ComplexDevice device(7, 12345, 1.5f);
    device.enable();
    
    // Test that all constructors executed properly
    uint8_t id = device.getId();
    uint16_t serial = device.getSerial();
    float adjusted = device.getAdjustedId();
    
    // Verify values
    if (id == 7 && serial == 12345 && device.isEnabled()) {
        return (int)(adjusted * 10); // Return 105 (7 * 1.5 * 10)
    }
    
    return 0;
}
