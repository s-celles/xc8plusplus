// Simple inheritance demo for XC8++
#include <stdint.h>

class Device {
protected:
    uint8_t id;
    bool enabled;
    
public:
    Device(uint8_t deviceId) : id(deviceId), enabled(false) {}
    
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

class LED : public Device {
private:
    uint8_t brightness;
    
public:
    LED(uint8_t id) : Device(id), brightness(0) {}
    
    void setBrightness(uint8_t level) {
        brightness = level;
        if (brightness > 0) {
            enable();
        } else {
            disable();
        }
    }
    
    uint8_t getBrightness() const {
        return brightness;
    }
    
    void turnOn() {
        setBrightness(255);
    }
    
    void turnOff() {
        setBrightness(0);
    }
};

extern "C" int test_led_inheritance() {
    LED statusLED(1);
    
    // Test inheritance - using base class methods
    statusLED.enable();
    uint8_t id = statusLED.getId();
    
    // Test derived class methods
    statusLED.turnOn();
    uint8_t brightness = statusLED.getBrightness();
    
    // Test that base class state is affected by derived class
    bool isOn = statusLED.isEnabled();
    
    return id + brightness + (isOn ? 1 : 0);
}
