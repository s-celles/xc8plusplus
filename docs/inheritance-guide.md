# XC8++ Inheritance Usage Guide

## Getting Started with Inheritance in XC8++

This guide shows how to use inheritance and advanced C++ features for 8-bit PIC microcontroller development.

## Basic Inheritance Example

### Step 1: Define a Base Device Class

```cpp
// Base class for all hardware devices
class Device {
protected:
    uint8_t deviceId;
    bool enabled;
    
public:
    Device(uint8_t id) : deviceId(id), enabled(false) {}
    
    void enable() { 
        enabled = true; 
        // Initialize hardware
    }
    
    void disable() { 
        enabled = false; 
        // Shutdown hardware
    }
    
    bool isEnabled() const { 
        return enabled; 
    }
    
    uint8_t getId() const { 
        return deviceId; 
    }
};
```

### Step 2: Create Specialized Derived Classes

```cpp
// Temperature sensor with calibration
class TemperatureSensor : public Device {
private:
    float temperatureOffset;
    float lastReading;
    
public:
    TemperatureSensor(uint8_t id, float offset = 0.0f) 
        : Device(id), temperatureOffset(offset), lastReading(0.0f) {}
    
    void calibrate(float offset) {
        temperatureOffset = offset;
    }
    
    float readTemperature() {
        if (!isEnabled()) return 0.0f;
        
        // Read from ADC (pseudo-code)
        uint16_t adcValue = readADC(getId());
        float rawTemp = (float)adcValue * 0.1f; // Convert to Celsius
        
        lastReading = rawTemp + temperatureOffset;
        return lastReading;
    }
    
    bool isValidReading() const {
        return isEnabled() && (lastReading > -40.0f && lastReading < 85.0f);
    }
};

// PWM-controlled actuator
class ServoMotor : public Device {
private:
    uint8_t currentPosition;
    uint8_t targetPosition;
    uint8_t pwmChannel;
    
public:
    ServoMotor(uint8_t id, uint8_t channel) 
        : Device(id), currentPosition(90), targetPosition(90), pwmChannel(channel) {}
    
    void setPosition(uint8_t degrees) {
        if (!isEnabled()) return;
        
        targetPosition = degrees;
        updatePWM();
    }
    
    void updatePWM() {
        // Convert angle to PWM duty cycle
        uint16_t pulseWidth = 1000 + (targetPosition * 1000) / 180;
        setPWM(pwmChannel, pulseWidth);
        currentPosition = targetPosition;
    }
    
    uint8_t getPosition() const {
        return currentPosition;
    }
    
    bool atTarget() const {
        return currentPosition == targetPosition;
    }
};
```

### Step 3: Use in Main Application

```cpp
extern "C" int main() {
    // Create device instances
    TemperatureSensor tempSensor(1, 2.5f);  // ID=1, offset=2.5°C
    ServoMotor servo(2, 1);                 // ID=2, PWM channel=1
    
    // Initialize devices
    tempSensor.enable();
    servo.enable();
    
    // Main control loop
    while (1) {
        // Read temperature
        float temperature = tempSensor.readTemperature();
        
        if (tempSensor.isValidReading()) {
            // Control servo based on temperature
            if (temperature > 25.0f) {
                servo.setPosition(0);   // Cool position
            } else if (temperature < 20.0f) {
                servo.setPosition(180); // Heat position
            } else {
                servo.setPosition(90);  // Neutral position
            }
        }
        
        delay_ms(100);
    }
    
    return 0;
}
```

## Advanced Pattern: Sensor System with Composition

### Modular Sensor Design

```cpp
// Base sensor interface
class Sensor : public Device {
protected:
    float lastValue;
    
public:
    Sensor(uint8_t id) : Device(id), lastValue(0.0f) {}
    
    virtual float read() = 0;  // Pure virtual for specialized reading
    
    float getValue() const { 
        return lastValue; 
    }
};

// Analog sensor implementation
class AnalogSensor : public Sensor {
private:
    uint8_t adcChannel;
    float scaleFactor;
    
public:
    AnalogSensor(uint8_t id, uint8_t channel, float scale) 
        : Sensor(id), adcChannel(channel), scaleFactor(scale) {}
    
    float read() override {
        if (!isEnabled()) return 0.0f;
        
        uint16_t adcValue = readADC(adcChannel);
        lastValue = (float)adcValue * scaleFactor;
        return lastValue;
    }
};

// Digital sensor implementation  
class DigitalSensor : public Sensor {
private:
    uint8_t pinNumber;
    
public:
    DigitalSensor(uint8_t id, uint8_t pin) 
        : Sensor(id), pinNumber(pin) {}
    
    float read() override {
        if (!isEnabled()) return 0.0f;
        
        bool state = digitalRead(pinNumber);
        lastValue = state ? 1.0f : 0.0f;
        return lastValue;
    }
};
```

### Sensor Array Management

```cpp
template<uint8_t MAX_SENSORS>
class SensorArray {
private:
    Sensor* sensors[MAX_SENSORS];
    uint8_t sensorCount;
    
public:
    SensorArray() : sensorCount(0) {
        for (uint8_t i = 0; i < MAX_SENSORS; i++) {
            sensors[i] = nullptr;
        }
    }
    
    bool addSensor(Sensor* sensor) {
        if (sensorCount < MAX_SENSORS) {
            sensors[sensorCount] = sensor;
            sensorCount++;
            return true;
        }
        return false;
    }
    
    void readAll() {
        for (uint8_t i = 0; i < sensorCount; i++) {
            if (sensors[i] != nullptr) {
                sensors[i]->read();
            }
        }
    }
    
    float getSensorValue(uint8_t index) const {
        if (index < sensorCount && sensors[index] != nullptr) {
            return sensors[index]->getValue();
        }
        return 0.0f;
    }
    
    uint8_t getCount() const { 
        return sensorCount; 
    }
};
```

## Memory-Efficient Patterns for 8-bit PICs

### 1. Prefer Composition Over Deep Inheritance

❌ **Avoid:**
```cpp
class A { uint16_t data[10]; };
class B : public A { uint16_t moreData[10]; };
class C : public B { uint16_t evenMore[10]; };  // 60 bytes!
```

✅ **Prefer:**
```cpp
struct SensorData { uint16_t values[5]; };      // 10 bytes
class Sensor {
    SensorData data;        // Composition
    uint8_t status;         // 1 byte
};  // Total: 11 bytes
```

### 2. Use Static Methods for Utility Functions

```cpp
class MathUtils {
public:
    static uint16_t map(uint16_t value, uint16_t fromLow, uint16_t fromHigh, 
                       uint16_t toLow, uint16_t toHigh) {
        return toLow + (value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow);
    }
    
    static bool inRange(float value, float min, float max) {
        return (value >= min) && (value <= max);
    }
};

// Usage:
uint16_t pwmValue = MathUtils::map(temperature, 0, 100, 0, 1023);
if (MathUtils::inRange(voltage, 3.0f, 3.6f)) {
    // Valid voltage range
}
```

### 3. Template Specialization for Type Safety

```cpp
template<typename T, uint8_t SIZE>
class CircularBuffer {
private:
    T buffer[SIZE];
    uint8_t head, tail, count;
    
public:
    CircularBuffer() : head(0), tail(0), count(0) {}
    
    bool push(const T& item) {
        if (count < SIZE) {
            buffer[head] = item;
            head = (head + 1) % SIZE;
            count++;
            return true;
        }
        return false;
    }
    
    bool pop(T& item) {
        if (count > 0) {
            item = buffer[tail];
            tail = (tail + 1) % SIZE;
            count--;
            return true;
        }
        return false;
    }
    
    uint8_t size() const { return count; }
    bool isEmpty() const { return count == 0; }
    bool isFull() const { return count == SIZE; }
};

// Usage with different types:
CircularBuffer<uint8_t, 16> byteBuffer;      // 19 bytes total
CircularBuffer<float, 8> floatBuffer;        // 35 bytes total
```

## Testing Your Code

### 1. Transpile to C

```bash
python -m xc8plusplus transpile my_sensors.cpp -o my_sensors.c -v
```

### 2. Check Generated Code

The transpiler converts your C++ to memory-efficient C:

```c
// Generated C code
typedef struct TemperatureSensor {
    uint8_t deviceId;
    bool enabled;
    float temperatureOffset;
    float lastReading;
} TemperatureSensor;

void TemperatureSensor_init(TemperatureSensor* self, uint8_t id, float offset);
float TemperatureSensor_readTemperature(TemperatureSensor* self);
bool TemperatureSensor_isValidReading(TemperatureSensor* self);
```

### 3. Compile with XC8

```bash
xc8-cc -mcpu=PIC16F877A my_sensors.c -o my_project.hex
```

## Best Practices

### ✅ **Do:**
- Use inheritance for "is-a" relationships
- Prefer composition for "has-a" relationships  
- Keep inheritance hierarchies shallow (2-3 levels max)
- Use `uint8_t` and `uint16_t` for memory efficiency
- Test memory usage with your target PIC device

### ❌ **Don't:**
- Use virtual functions unless you have >1KB RAM
- Create deep inheritance chains
- Use dynamic allocation (`new`/`delete`)
- Include heavy STL containers
- Ignore memory constraints

## Debugging Tips

1. **Check Memory Usage:**
   ```cpp
   // Add at compile time
   #pragma message("Sizeof TemperatureSensor: " stringify(sizeof(TemperatureSensor)))
   ```

2. **Validate Transpilation:**
   ```bash
   # Check generated C code structure
   grep -n "typedef struct" output.c
   ```

3. **Test on Simulator:**
   - Use MPLAB X IDE simulator
   - Monitor RAM usage
   - Verify timing constraints

This guide provides a foundation for using inheritance effectively in 8-bit PIC microcontroller projects while maintaining the memory efficiency required for embedded systems.
