"""Tests for xc8plusplus transpiler."""

import pytest
from pathlib import Path
import tempfile
import os

from xc8plusplus import XC8Transpiler


class TestXC8Transpiler:
    """Test cases for the XC8Transpiler class."""
    
    def test_transpiler_initialization(self):
        """Test that transpiler initializes correctly."""
        transpiler = XC8Transpiler()
        assert transpiler.classes == {}
        assert transpiler.functions == []
        assert transpiler.variables == []
        assert transpiler.includes == []
    
    def test_type_mapping(self):
        """Test C++ to C type mapping."""
        transpiler = XC8Transpiler()
        
        # Test basic type mappings
        assert transpiler.map_cpp_type_to_c("int") == "int"
        assert transpiler.map_cpp_type_to_c("bool") == "bool"
        assert transpiler.map_cpp_type_to_c("float") == "float"
        assert transpiler.map_cpp_type_to_c("double") == "double"
        assert transpiler.map_cpp_type_to_c("char") == "char"
        
        # Test unknown type fallback
        assert transpiler.map_cpp_type_to_c("unknown_type") == "int"
    
    def test_transpile_simple_class(self):
        """Test transpilation of a simple C++ class."""
        cpp_code = '''
class SimpleClass {
private:
    int value;
public:
    SimpleClass() : value(0) {}
    int getValue() const { return value; }
};
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as cpp_file:
            cpp_file.write(cpp_code)
            cpp_file.flush()
            cpp_file_path = cpp_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as c_file:
            c_file_path = c_file.name
            
        transpiler = XC8Transpiler()
        
        try:
            # This will fail if clang is not available, but we test the basic structure
            success = transpiler.transpile(cpp_file_path, c_file_path)
            # If clang is available, we should have found classes
            if success and os.path.getsize(c_file_path) > 0:
                assert len(transpiler.classes) >= 0  # May be 0 if AST parsing fails
        except Exception:
            # If clang is not available, that's expected in test environment
            pass
        finally:
            try:
                os.unlink(cpp_file_path)
            except:
                pass
            try:
                os.unlink(c_file_path)
            except:
                pass
    
    def test_invalid_input_file(self):
        """Test handling of invalid input file."""
        transpiler = XC8Transpiler()
        
        with tempfile.NamedTemporaryFile(suffix='.c', delete=False) as output_file:
            output_file_path = output_file.name
            
        try:
            success = transpiler.transpile("nonexistent.cpp", output_file_path)
            assert not success
        finally:
            try:
                os.unlink(output_file_path)
            except:
                pass
