# xc8plusplus API Reference

## Overview

The xc8plusplus package provides both CLI and programmatic APIs for C++ to C transpilation targeting Microchip's XC8 compiler.

## Installation

```bash
pip install -e .  # Development installation
```

## CLI Interface

### Commands

#### `xc8plusplus transpile`

Transpile C++ source code to XC8-compatible C.

**Syntax:**
```bash
xc8plusplus transpile INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE` - C++ source file to transpile (required)

**Options:**
- `--output`, `-o` PATH - Output C file path (default: input_file with .c extension)
- `--verbose`, `-v` - Enable verbose output
- `--help` - Show help message

**Examples:**
```bash
# Basic transpilation
xc8plusplus transpile led.cpp

# Specify output file
xc8plusplus transpile led.cpp --output led_transpiled.c

# Verbose output
xc8plusplus transpile led.cpp --verbose
```

#### `xc8plusplus version`

Display version information.

**Syntax:**
```bash
xc8plusplus version
```

**Output:**
```
xc8plusplus version 0.1.0
Author: Sébastien Celles
```

#### `xc8plusplus demo`

Show architecture demonstration and usage examples.

**Syntax:**
```bash
xc8plusplus demo
```

## Python API

### Core Classes

#### `XC8Transpiler`

Main transpiler class for C++ to C conversion using semantic AST analysis.

```python
from xc8plusplus import XC8Transpiler
```

##### Constructor

```python
transpiler = XC8Transpiler()
```

Creates a new transpiler instance with empty analysis state.

##### Attributes

- **`classes`** (`dict`) - Dictionary of discovered C++ classes
  - Key: Class name (`str`)
  - Value: Class information (`dict`) with keys:
    - `'methods'`: List of method information dictionaries
    - `'fields'`: List of field information dictionaries  
    - `'constructors'`: List of constructor AST lines
    - `'destructor'`: Destructor information or `None`

- **`functions`** (`list`) - List of standalone function information
- **`variables`** (`list`) - List of global variable information
- **`includes`** (`list`) - List of include statement information

##### Methods

###### `transpile(input_file, output_file)`

Main transpilation function that converts C++ source to C.

**Parameters:**
- `input_file` (`str` or `Path`) - Path to input C++ file
- `output_file` (`str` or `Path`) - Path to output C file

**Returns:**
- `bool` - `True` if transpilation succeeded, `False` if failed

**Example:**
```python
transpiler = XC8Transpiler()
success = transpiler.transpile("led.cpp", "led.c")

if success:
    print(f"Found {len(transpiler.classes)} classes")
    for name, info in transpiler.classes.items():
        print(f"  {name}: {len(info['methods'])} methods")
else:
    print("Transpilation failed")
```

###### `analyze_with_clang(cpp_file)`

Analyze C++ source file using Clang AST dump.

**Parameters:**
- `cpp_file` (`str` or `Path`) - Path to C++ source file

**Returns:**
- `str` or `None` - AST dump output if successful, `None` if failed

**Example:**
```python
transpiler = XC8Transpiler()
ast_output = transpiler.analyze_with_clang("input.cpp")
if ast_output:
    print("AST analysis successful")
else:
    print("AST analysis failed")
```

###### `parse_ast_dump(ast_dump)`

Parse Clang AST dump to extract semantic information.

**Parameters:**
- `ast_dump` (`str`) - AST dump output from Clang

**Side Effects:**
- Populates `classes`, `functions`, `variables`, and `includes` attributes

**Example:**
```python
transpiler = XC8Transpiler()
ast_dump = transpiler.analyze_with_clang("input.cpp")
if ast_dump:
    transpiler.parse_ast_dump(ast_dump)
    print(f"Discovered {len(transpiler.classes)} classes")
```

###### `generate_c_code(output_file)`

Generate C code from analyzed semantic information.

**Parameters:**
- `output_file` (`str` or `Path`) - Path to output C file

**Side Effects:**
- Writes transpiled C code to output file

**Example:**
```python
transpiler = XC8Transpiler()
# ... perform analysis ...
transpiler.generate_c_code("output.c")
```

###### `map_cpp_type_to_c(cpp_type)`

Map C++ type to equivalent C type for XC8 compatibility.

**Parameters:**
- `cpp_type` (`str`) - C++ type name

**Returns:**
- `str` - Equivalent C type name

**Type Mappings:**
- `bool` → `bool`
- `int` → `int`
- `unsigned int` → `unsigned int`
- `float` → `float`
- `double` → `double`
- `char` → `char`
- `void` → `void`
- Unknown types → `int` (default)

**Example:**
```python
transpiler = XC8Transpiler()
c_type = transpiler.map_cpp_type_to_c("bool")  # Returns "bool"
unknown = transpiler.map_cpp_type_to_c("MyClass")  # Returns "int"
```

###### `extract_return_type(function_type)`

Extract return type from function signature.

**Parameters:**
- `function_type` (`str`) - Function type signature

**Returns:**
- `str` - Return type name

**Example:**
```python
transpiler = XC8Transpiler()
return_type = transpiler.extract_return_type("int (int, bool)")  # Returns "int"
```

### Package Exports

The main package exports the following:

```python
from xc8plusplus import (
    XC8Transpiler,    # Main transpiler class
    __version__,      # Package version string
    __author__        # Package author
)
```

## Data Structures

### Class Information Dictionary

Structure of class information stored in `transpiler.classes[class_name]`:

```python
{
    'methods': [
        {
            'name': 'method_name',      # Method name
            'type': 'return_type (...)', # Function signature
            'line': '...'               # Original AST line
        },
        # ... more methods
    ],
    'fields': [
        {
            'name': 'field_name',       # Field name  
            'type': 'field_type'        # Field type
        },
        # ... more fields
    ],
    'constructors': [
        'AST line for constructor',
        # ... more constructors
    ],
    'destructor': 'AST line for destructor' or None
}
```

## Error Handling

### Common Error Scenarios

1. **Clang Not Available**
   - `analyze_with_clang()` returns `None`
   - `transpile()` returns `False`
   - Error message printed to stdout

2. **Invalid Input File**
   - File doesn't exist or not readable
   - `transpile()` returns `False`

3. **AST Parsing Failure**
   - Malformed C++ code
   - `parse_ast_dump()` may not populate expected data
   - Generated C code may be incomplete

### Best Practices

```python
transpiler = XC8Transpiler()

try:
    success = transpiler.transpile("input.cpp", "output.c")
    
    if success:
        if transpiler.classes:
            print("Successfully transpiled classes:")
            for name, info in transpiler.classes.items():
                print(f"  {name}: {len(info['methods'])} methods")
        else:
            print("No C++ classes found in input")
    else:
        print("Transpilation failed - check input file and Clang availability")
        
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Integration Examples

### Basic Workflow

```python
from xc8plusplus import XC8Transpiler
from pathlib import Path

def transpile_project(src_dir, output_dir):
    """Transpile all C++ files in a directory."""
    transpiler = XC8Transpiler()
    src_path = Path(src_dir)
    out_path = Path(output_dir)
    
    for cpp_file in src_path.glob("*.cpp"):
        c_file = out_path / cpp_file.with_suffix(".c").name
        
        print(f"Transpiling {cpp_file} -> {c_file}")
        success = transpiler.transpile(str(cpp_file), str(c_file))
        
        if success:
            print(f"✅ Success: {len(transpiler.classes)} classes found")
        else:
            print(f"❌ Failed: {cpp_file}")

# Usage
transpile_project("src", "build")
```

### Advanced Analysis

```python
from xc8plusplus import XC8Transpiler

def analyze_cpp_complexity(cpp_file):
    """Analyze C++ code complexity."""
    transpiler = XC8Transpiler()
    
    # Just analyze, don't generate output
    ast_dump = transpiler.analyze_with_clang(cpp_file)
    if not ast_dump:
        return None
        
    transpiler.parse_ast_dump(ast_dump)
    
    complexity = {
        'classes': len(transpiler.classes),
        'total_methods': sum(len(info['methods']) for info in transpiler.classes.values()),
        'total_fields': sum(len(info['fields']) for info in transpiler.classes.values()),
        'class_details': {}
    }
    
    for name, info in transpiler.classes.items():
        complexity['class_details'][name] = {
            'methods': len(info['methods']),
            'fields': len(info['fields']),
            'constructors': len(info['constructors'])
        }
    
    return complexity

# Usage
complexity = analyze_cpp_complexity("complex.cpp")
if complexity:
    print(f"Code complexity: {complexity['total_methods']} methods across {complexity['classes']} classes")
```

## Module Execution

The package can be executed as a module:

```bash
python -m xc8plusplus --help
python -m xc8plusplus transpile input.cpp --output output.c
python -m xc8plusplus version
python -m xc8plusplus demo
```

This is equivalent to using the `xc8plusplus` command directly.

## Version Information

```python
import xc8plusplus

print(f"Version: {xc8plusplus.__version__}")
print(f"Author: {xc8plusplus.__author__}")
```

Current version: **0.1.0**
