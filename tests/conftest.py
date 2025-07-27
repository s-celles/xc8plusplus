"""Pytest configuration for xc8plusplus tests."""

import pytest
import sys
from pathlib import Path

# Add the src directory to the Python path so we can import xc8plusplus
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))


@pytest.fixture
def sample_cpp_code():
    """Sample C++ code for testing."""
    return """
#include <iostream>

class TestClass {
private:
    int value;
    
public:
    TestClass() : value(0) {}
    
    TestClass(int v) : value(v) {}
    
    int getValue() const {
        return value;
    }
    
    void setValue(int v) {
        value = v;
    }
    
    void printValue() const {
        std::cout << "Value: " << value << std::endl;
    }
};

int main() {
    TestClass obj(42);
    obj.printValue();
    
    TestClass obj2;
    obj2.setValue(100);
    obj2.printValue();
    
    return 0;
}
"""


@pytest.fixture
def simple_cpp_code():
    """Simple C++ code for basic testing."""
    return """
#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}
"""
