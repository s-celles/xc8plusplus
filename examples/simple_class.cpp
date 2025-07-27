// Simple C++ class example for XC8++
// Demonstrates basic C++ features that work with 8-bit PICs

class Led {
private:
    bool state;
    
public:
    Led() : state(false) {
        // Constructor - initialize LED as off
    }
    
    void turnOn() {
        state = true;
        // In real implementation, would set GPIO pin high
    }
    
    void turnOff() {
        state = false;
        // In real implementation, would set GPIO pin low
    }
    
    void toggle() {
        state = !state;
        // In real implementation, would toggle GPIO pin
    }
    
    bool isOn() const {
        return state;
    }
};

// Simple function overloading example
int add(int a, int b) {
    return a + b;
}

int add(int a, int b, int c) {
    return a + b + c;
}

// Main function using C++ features
extern "C" int main() {
    Led statusLed;
    
    // Test basic class functionality
    statusLed.turnOn();
    
    if (statusLed.isOn()) {
        statusLed.toggle();
    }
    
    // Test function overloading
    int result1 = add(5, 10);
    int result2 = add(1, 2, 3);
    
    return result1 + result2; // Should return 21
}
