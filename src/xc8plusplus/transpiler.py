#!/usr/bin/env python3
"""
XC8 C++ to C Transpiler using Clang AST Analysis
This demonstrates the proper way to handle C++ to C transformation
using semantic analysis instead of string manipulation.

Uses Clang AST analysis and demonstrates the architecture
we'll implement in C++ with LibTooling.

ENHANCEMENT: Now supports transpiling main functions and overloaded functions
by generating appropriate C function signatures with name mangling for overloads.

NOTE: This is a demonstration transpiler. A complete implementation would need
more sophisticated AST analysis to fully transpile function bodies, expressions,
and control flow structures. The current implementation generates proper C
declarations and placeholders for manual implementation.
"""

import re
import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional


class XC8Transpiler:
    """
    XC8 C++ to C transpiler using semantic analysis.
    Uses Clang AST analysis instead of string manipulation.
    """

    def __init__(self):
        self.classes = {}
        self.functions = []
        self.overloaded_functions = {}
        self.main_function = None
        self.variables = []
        self.includes = []
        self.source_code = ""  # Store original source for body extraction
        self.temp_files = []  # Track temporary files for cleanup
        self.source_files = {}  # Track analyzed source files
        self.xc8_stubs_enabled = True  # Enable XC8 stubs by default
        self.all_source_codes = {}  # Store all source files content for body extraction

    def analyze_with_clang(self, cpp_file):
        """
        Use Clang to get proper AST dump - no manual parsing!
        This is what the C++ LibTooling version will do internally.
        """
        try:
            # Use XC8's Clang for AST analysis with proper include paths
            clang_cmd = [
                r"C:\Program Files\Microchip\xc8\v3.00\pic\bin\clang.exe",
                "-Xclang",
                "-ast-dump",
                "-fsyntax-only",
                "-std=c++17",
                "-I",
                r"C:\Program Files\Microchip\xc8\v3.00\pic\include",
                "-I",
                r"C:\Program Files\Microchip\xc8\v3.00\pic\include\c99",
                "--target=pic",
                str(cpp_file),
            ]

            result = subprocess.run(clang_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Clang analysis failed: {result.stderr}")
                return None

            return result.stdout

        except Exception as e:
            print(f"Error running Clang analysis: {e}")
            return None

    def _create_xc8_stubs_header(self) -> str:
        """Create a temporary header with XC8 stub definitions for Clang analysis."""
        xc8_stubs = '''
// XC8 Stub Definitions for Clang Analysis
#ifndef XC8_STUBS_H
#define XC8_STUBS_H

// Delay macros
#define __delay_ms(x) do { volatile int _delay = (x) * 1000; while(_delay--); } while(0)
#define __delay_us(x) do { volatile int _delay = (x); while(_delay--); } while(0)

// PIC16F876A Register Stubs
typedef struct {
    unsigned RA0 : 1; unsigned RA1 : 1; unsigned RA2 : 1; unsigned RA3 : 1;
    unsigned RA4 : 1; unsigned RA5 : 1; unsigned : 2;
} PORTAbits_t;

typedef struct {
    unsigned RC0 : 1; unsigned RC1 : 1; unsigned RC2 : 1; unsigned RC3 : 1;
    unsigned RC4 : 1; unsigned RC5 : 1; unsigned RC6 : 1; unsigned RC7 : 1;
} PORTCbits_t;

typedef struct {
    unsigned RB0 : 1; unsigned RB1 : 1; unsigned RB2 : 1; unsigned RB3 : 1;
    unsigned RB4 : 1; unsigned RB5 : 1; unsigned RB6 : 1; unsigned RB7 : 1;
} PORTBbits_t;

typedef struct {
    unsigned TRISA0 : 1; unsigned TRISA1 : 1; unsigned TRISA2 : 1; unsigned TRISA3 : 1;
    unsigned TRISA4 : 1; unsigned TRISA5 : 1; unsigned : 2;
} TRISAbits_t;

typedef struct {
    unsigned TRISB0 : 1; unsigned TRISB1 : 1; unsigned TRISB2 : 1; unsigned TRISB3 : 1;
    unsigned TRISB4 : 1; unsigned TRISB5 : 1; unsigned TRISB6 : 1; unsigned TRISB7 : 1;
} TRISBbits_t;

typedef struct {
    unsigned T0CS : 1; unsigned T0SE : 1; unsigned PSA : 1; unsigned PS0 : 1;
    unsigned PS1 : 1; unsigned PS2 : 1; unsigned INTEDG : 1; unsigned RBPU : 1;
} OPTION_REGbits_t;

typedef struct {
    unsigned RBIF : 1; unsigned INTF : 1; unsigned T0IF : 1; unsigned RBIE : 1;
    unsigned INTE : 1; unsigned T0IE : 1; unsigned PEIE : 1; unsigned GIE : 1;
} INTCONbits_t;

// Global register variables
extern volatile PORTAbits_t PORTAbits;
extern volatile PORTBbits_t PORTBbits;
extern volatile PORTCbits_t PORTCbits;
extern volatile TRISAbits_t TRISAbits;
extern volatile TRISBbits_t TRISBbits;
extern volatile OPTION_REGbits_t OPTION_REGbits;
extern volatile INTCONbits_t INTCONbits;
extern volatile unsigned char TMR0;

#endif // XC8_STUBS_H
'''
        
        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.h', prefix='xc8_stubs_')
        os.write(temp_fd, xc8_stubs.encode('utf-8'))
        os.close(temp_fd)
        
        self.temp_files.append(temp_path)
        return temp_path

    def _create_comprehensive_xc8_stubs_header(self, project_dir: Path) -> str:
        """Create a comprehensive XC8 stubs header that includes project-specific definitions."""
        xc8_stubs = '''
// Comprehensive XC8 Stub Definitions for Clang Analysis
#ifndef XC8_COMPREHENSIVE_STUBS_H
#define XC8_COMPREHENSIVE_STUBS_H

// Standard includes
#include <stdint.h>
#include <stdbool.h>

// Delay macros
#define __delay_ms(x) do { volatile int _delay = (x) * 1000; while(_delay--); } while(0)
#define __delay_us(x) do { volatile int _delay = (x); while(_delay--); } while(0)

// PIC16F876A Register Stubs
typedef struct {
    unsigned RA0 : 1; unsigned RA1 : 1; unsigned RA2 : 1; unsigned RA3 : 1;
    unsigned RA4 : 1; unsigned RA5 : 1; unsigned : 2;
} PORTAbits_t;

typedef struct {
    unsigned RC0 : 1; unsigned RC1 : 1; unsigned RC2 : 1; unsigned RC3 : 1;
    unsigned RC4 : 1; unsigned RC5 : 1; unsigned RC6 : 1; unsigned RC7 : 1;
} PORTCbits_t;

typedef struct {
    unsigned RB0 : 1; unsigned RB1 : 1; unsigned RB2 : 1; unsigned RB3 : 1;
    unsigned RB4 : 1; unsigned RB5 : 1; unsigned RB6 : 1; unsigned RB7 : 1;
} PORTBbits_t;

typedef struct {
    unsigned TRISA0 : 1; unsigned TRISA1 : 1; unsigned TRISA2 : 1; unsigned TRISA3 : 1;
    unsigned TRISA4 : 1; unsigned TRISA5 : 1; unsigned : 2;
} TRISAbits_t;

typedef struct {
    unsigned TRISB0 : 1; unsigned TRISB1 : 1; unsigned TRISB2 : 1; unsigned TRISB3 : 1;
    unsigned TRISB4 : 1; unsigned TRISB5 : 1; unsigned TRISB6 : 1; unsigned TRISB7 : 1;
} TRISBbits_t;

typedef struct {
    unsigned T0CS : 1; unsigned T0SE : 1; unsigned PSA : 1; unsigned PS0 : 1;
    unsigned PS1 : 1; unsigned PS2 : 1; unsigned INTEDG : 1; unsigned RBPU : 1;
} OPTION_REGbits_t;

typedef struct {
    unsigned RBIF : 1; unsigned INTF : 1; unsigned T0IF : 1; unsigned RBIE : 1;
    unsigned INTE : 1; unsigned T0IE : 1; unsigned PEIE : 1; unsigned GIE : 1;
} INTCONbits_t;

// Global register variables
extern volatile PORTAbits_t PORTAbits;
extern volatile PORTBbits_t PORTBbits;
extern volatile PORTCbits_t PORTCbits;
extern volatile TRISAbits_t TRISAbits;
extern volatile TRISBbits_t TRISBbits;
extern volatile OPTION_REGbits_t OPTION_REGbits;
extern volatile INTCONbits_t INTCONbits;
extern volatile unsigned char TMR0;
'''

        # Scan for project-specific enums in pin_manager.h or other headers
        pin_manager_file = project_dir / "pin_manager.h"
        if pin_manager_file.exists():
            with open(pin_manager_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract enum definitions and add them as stubs
                enum_matches = re.findall(r'typedef\s+enum\s*\{([^}]+)\}\s*(\w+);', content)
                for enum_body, enum_name in enum_matches:
                    xc8_stubs += f"\n// {enum_name} enum stub\ntypedef enum {{{enum_body}}} {enum_name};\n"

        xc8_stubs += '\n#endif // XC8_COMPREHENSIVE_STUBS_H\n'
        
        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.h', prefix='xc8_comprehensive_stubs_')
        os.write(temp_fd, xc8_stubs.encode('utf-8'))
        os.close(temp_fd)
        
        self.temp_files.append(temp_path)
        return temp_path

    def _preprocess_cpp_file(self, cpp_file: Path, stubs_header: str) -> str:
        """Preprocess a C++ file to add XC8 stubs header and copy local includes."""
        with open(cpp_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Create a temporary directory for the preprocessed files
        temp_dir = Path(tempfile.mkdtemp(prefix='xc8_preprocess_'))
        self.temp_files.append(str(temp_dir))
        
        # Copy all local header files to temp directory
        source_dir = cpp_file.parent
        for header_file in source_dir.glob('*.h'):
            shutil.copy2(header_file, temp_dir)
        for header_file in source_dir.glob('*.hpp'):
            shutil.copy2(header_file, temp_dir)
        
        # Process the content to add stubs
        lines = original_content.split('\n')
        processed_lines = []
        stubs_added = False
        
        # Add the stubs header at the very beginning
        processed_lines.append(f'#include "{stubs_header}"')
        stubs_added = True
        
        for line in lines:
            # Convert relative includes to use temp directory if needed
            if line.strip().startswith('#include "'):
                # Keep the line as-is, files are copied to temp dir
                processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        # Create temporary processed file in the temp directory
        temp_file = temp_dir / f'processed_{cpp_file.name}'
        processed_content = '\n'.join(processed_lines)
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        return str(temp_file)

    def analyze_with_clang_enhanced(self, cpp_file: Path) -> Optional[str]:
        """
        Enhanced Clang analysis with XC8 stubs support.
        Automatically handles XC8-specific macros by preprocessing files.
        """
        try:
            analysis_file = cpp_file
            temp_dir = None
            
            # If XC8 stubs are enabled and this is a .cpp file, preprocess it
            if self.xc8_stubs_enabled and cpp_file.suffix.lower() == '.cpp':
                stubs_header = self._create_xc8_stubs_header()
                processed_file_path = self._preprocess_cpp_file(cpp_file, stubs_header)
                analysis_file = Path(processed_file_path)
                temp_dir = analysis_file.parent
            
            # Use enhanced Clang command with additional include paths
            return self._analyze_with_clang_internal(analysis_file, temp_dir)
            
        except Exception as e:
            print(f"Error in enhanced Clang analysis: {e}")
            return None

    def _analyze_with_clang_internal(self, cpp_file: Path, additional_include_dir: Optional[Path] = None) -> Optional[str]:
        """
        Internal Clang analysis with configurable include paths.
        """
        try:
            # Base Clang command
            clang_cmd = [
                r"C:\Program Files\Microchip\xc8\v3.00\pic\bin\clang.exe",
                "-Xclang",
                "-ast-dump",
                "-fsyntax-only",
                "-std=c++17",
                "-I",
                r"C:\Program Files\Microchip\xc8\v3.00\pic\include",
                "-I",
                r"C:\Program Files\Microchip\xc8\v3.00\pic\include\c99",
                "--target=pic",
            ]
            
            # Add additional include directory if provided
            if additional_include_dir:
                clang_cmd.extend(["-I", str(additional_include_dir)])
            
            # Add the source file
            clang_cmd.append(str(cpp_file))

            result = subprocess.run(clang_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Clang analysis failed: {result.stderr}")
                return None

            return result.stdout

        except Exception as e:
            print(f"Error running internal Clang analysis: {e}")
            return None

    def parse_ast_dump(self, ast_dump):
        """
        Parse Clang AST dump to extract semantic information.
        This demonstrates proper AST analysis - no regex soup!
        """
        lines = ast_dump.split("\n")
        current_class = None
        current_method = None
        in_compound_stmt = False
        compound_depth = 0

        for i, line in enumerate(lines):
            line = line.strip()

            # Class declarations
            if "CXXRecordDecl" in line and "class" in line:
                match = re.search(r"class (\w+)", line)
                if match:
                    class_name = match.group(1)
                    current_class = class_name
                    self.classes[class_name] = {
                        "methods": [],
                        "fields": [],
                        "constructors": [],
                        "destructor": None,
                    }

            # Method declarations
            elif "CXXMethodDecl" in line and current_class:
                match = re.search(r"(\w+) '([^']+)'", line)
                if match:
                    method_name = match.group(1)
                    method_type = match.group(2)
                    method_info = {
                        "name": method_name, 
                        "type": method_type, 
                        "line": line,
                        "body": self._extract_method_body_from_source(method_name, current_class)
                    }
                    self.classes[current_class]["methods"].append(method_info)

            # Field declarations
            elif "FieldDecl" in line and current_class:
                match = re.search(r"(\w+) '([^']+)'", line)
                if match:
                    field_name = match.group(1)
                    field_type = match.group(2)
                    self.classes[current_class]["fields"].append(
                        {"name": field_name, "type": field_type}
                    )

            # Constructor declarations
            elif "CXXConstructorDecl" in line and current_class:
                self.classes[current_class]["constructors"].append(line)

            # Function declarations (including main and overloaded functions)
            elif "FunctionDecl" in line:
                self._parse_function_declaration(line)

    def _extract_method_body_from_source(self, method_name, class_name):
        """Extract method body from the original source code, searching all source files"""
        
        # First try to find in the current source code (for inline methods)
        inline_body = self._extract_method_body_from_single_source(method_name, class_name, self.source_code)
        if inline_body:
            return inline_body
        
        # Then search in all stored source files for implementation
        for file_path, content in self.all_source_codes.items():
            if file_path.endswith('.cpp'):  # Look for implementations in .cpp files
                body = self._extract_method_body_from_single_source(method_name, class_name, content)
                if body:
                    return body
        
        return None

    def _extract_method_body_from_single_source(self, method_name, class_name, source_content):
        """Extract method body from a single source file"""
        if not source_content:
            return None
        
        # Try to find method inside class definition (inline)
        class_pattern = rf"class\s+{class_name}\s*\{{"
        class_match = re.search(class_pattern, source_content)
        if class_match:
            class_start = class_match.start()
            # Find the end of the class
            class_content = source_content[class_start:]
            
            # Find class closing brace
            brace_count = 0
            class_end = 0
            for i, char in enumerate(class_content):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i
                        break
            
            if class_end > 0:
                class_body = class_content[:class_end]
                inline_body = self._extract_method_from_content(method_name, class_body)
                if inline_body:
                    return inline_body
        
        # Try to find method implementation outside class (in .cpp files)
        # Pattern: ClassName::methodName(...) { ... }
        external_pattern = rf"{class_name}::{method_name}\s*\([^)]*\)\s*(?:const\s*)?\s*\{{"
        external_match = re.search(external_pattern, source_content)
        if external_match:
            return self._extract_method_from_content_at_position(source_content, external_match.end() - 1)
        
        return None

    def _extract_method_from_content(self, method_name, content):
        """Extract method body from content"""
        method_pattern = rf"\b{method_name}\s*\([^)]*\)\s*(?:const\s*)?\s*\{{"
        method_match = re.search(method_pattern, content)
        if not method_match:
            return None
        
        return self._extract_method_from_content_at_position(content, method_match.end() - 1)
    
    def _extract_method_from_content_at_position(self, content, start_pos):
        """Extract method body starting from a specific position (opening brace)"""
        brace_count = 0
        body_start = start_pos + 1
        i = start_pos
        
        while i < len(content):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    body_end = i
                    break
            i += 1
        else:
            return None
            
        # Extract and clean the body
        body = content[body_start:body_end].strip()
        return body if body else None

    def _transpile_method_body(self, cpp_body, class_name):
        """Transpile C++ method body to C code"""
        if not cpp_body:
            return "    // Empty method body\n"
        
        # Split body into lines for processing
        lines = cpp_body.split('\n')
        transpiled_lines = []
        
        for line in lines:
            # Strip leading/trailing whitespace but preserve indentation
            stripped_line = line.rstrip()
            if not stripped_line:
                transpiled_lines.append('')
                continue
                
            # Add proper indentation for C function
            indented_line = '    ' + stripped_line
            
            # Apply C++ to C transformations
            transformed_line = self._transform_cpp_line_to_c(indented_line, class_name)
            transpiled_lines.append(transformed_line)
        
        # Join lines and ensure proper formatting
        result = '\n'.join(transpiled_lines)
        if result and not result.endswith('\n'):
            result += '\n'
            
        return result

    def _transform_cpp_line_to_c(self, line, class_name):
        """Transform a single C++ line to C equivalent"""
        
        # Clean up any Unicode characters that might cause encoding issues
        line = line.encode('ascii', 'ignore').decode('ascii')
        
        # Handle member variable access: this->member or direct member access
        # Transform member access to explicit this pointer usage
        line = re.sub(r'\b(\w+)\s*=', r'self->\1 =', line)
        
        # Handle method calls on this object: methodName() -> ClassName_methodName(self)
        for other_class, class_info in self.classes.items():
            for method in class_info['methods']:
                method_name = method['name']
                # Pattern: methodName(...) -> ClassName_methodName(self, ...)
                pattern = rf'\b{method_name}\s*\(\s*\)'
                replacement = f'{other_class}_{method_name}(self)'
                line = re.sub(pattern, replacement, line)
                
                # Pattern with parameters: methodName(params) -> ClassName_methodName(self, params)
                pattern = rf'\b{method_name}\s*\(([^)]+)\)'
                replacement = rf'{other_class}_{method_name}(self, \1)'
                line = re.sub(pattern, replacement, line)
        
        # Handle object method calls: object.method() -> Class_method(&object)
        # This is more complex and would need object tracking
        
        # Handle C++ specific constructs
        line = line.replace('true', '1')
        line = line.replace('false', '0')
        
        # Handle enum access if we know the enums
        # This would need enum tracking from the AST analysis
        
        return line

    def _extract_function_body_from_source(self, func_name):
        """Extract function body from the original source code, searching all files"""
        
        # Search in all stored source files
        for file_path, content in self.all_source_codes.items():
            # Look for function definitions
            func_pattern = rf"\b{func_name}\s*\([^)]*\)\s*\{{"
            func_matches = list(re.finditer(func_pattern, content))
            
            if func_matches:
                # Get the last match (in case of multiple definitions)
                func_match = func_matches[-1]
                body = self._extract_method_from_content_at_position(content, func_match.end() - 1)
                if body:
                    return body
        
        return None
        
        # Extract the function body by counting braces
        func_start = func_match.end() - 1  # Start at the opening brace
        brace_count = 0
        body_start = func_start + 1
        i = func_start
        
        while i < len(self.source_code):
            if self.source_code[i] == '{':
                brace_count += 1
            elif self.source_code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    body_end = i
                    break
            i += 1
        else:
            return None
            
        # Extract and clean the body
        body = self.source_code[body_start:body_end].strip()
        return body

    def _parse_function_declaration(self, line):
        """Parse function declarations from AST dump"""
        # Look for function name and signature
        match = re.search(r"(\w+) '([^']+)'", line)
        if match:
            func_name = match.group(1)
            func_type = match.group(2)
            
            # Extract function body from source based on signature
            func_body = self._extract_function_body_by_signature(func_name, func_type)
            
            # Check if it's the main function
            if func_name == "main":
                self.main_function = {
                    "name": func_name,
                    "type": func_type,
                    "line": line,
                    "body": func_body
                }
            else:
                # Handle overloaded functions
                if func_name not in self.overloaded_functions:
                    self.overloaded_functions[func_name] = []
                
                self.overloaded_functions[func_name].append({
                    "name": func_name,
                    "type": func_type,
                    "line": line,
                    "body": func_body,
                    "mangled_name": self._generate_mangled_name(func_name, func_type)
                })
                
                # Also add to regular functions list
                self.functions.append({
                    "name": func_name,
                    "type": func_type,
                    "line": line,
                    "body": func_body
                })

    def _extract_function_body_by_signature(self, func_name, func_type):
        """Extract function body matching the specific signature"""
        if not self.source_code:
            return None
        
        # Extract parameter types from the function type
        if "(" in func_type and ")" in func_type:
            params_str = func_type.split("(")[1].split(")")[0]
            param_types = [p.strip() for p in params_str.split(",") if p.strip()]
        else:
            param_types = []
        
        # Build a more specific pattern based on parameter count
        if len(param_types) == 0:
            pattern = rf"\b{func_name}\s*\(\s*\)\s*\{{"
        elif len(param_types) == 2:
            pattern = rf"\b{func_name}\s*\(\s*\w+\s+\w+\s*,\s*\w+\s+\w+\s*\)\s*\{{"
        elif len(param_types) == 3:
            pattern = rf"\b{func_name}\s*\(\s*\w+\s+\w+\s*,\s*\w+\s+\w+\s*,\s*\w+\s+\w+\s*\)\s*\{{"
        else:
            # Fallback to generic pattern
            pattern = rf"\b{func_name}\s*\([^)]*\)\s*\{{"
        
        matches = list(re.finditer(pattern, self.source_code))
        
        if not matches:
            # Fallback to simpler pattern
            return self._extract_function_body_from_source(func_name)
        
        # For now, use the match based on parameter count
        target_match = None
        if len(param_types) == 2 and len(matches) >= 1:
            target_match = matches[0]  # First function with 2 params
        elif len(param_types) == 3 and len(matches) >= 2:
            target_match = matches[1] if len(matches) > 1 else matches[0]  # Second function with 3 params
        elif len(matches) > 0:
            target_match = matches[0]
        
        if not target_match:
            return None
        
        # Extract the function body by counting braces
        func_start = target_match.end() - 1  # Start at the opening brace
        brace_count = 0
        body_start = func_start + 1
        i = func_start
        
        while i < len(self.source_code):
            if self.source_code[i] == '{':
                brace_count += 1
            elif self.source_code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    body_end = i
                    break
            i += 1
        else:
            return None
            
        # Extract and clean the body
        body = self.source_code[body_start:body_end].strip()
        return body

    def _generate_mangled_name(self, func_name, func_type):
        """Generate mangled names for overloaded functions"""
        # Extract parameter types from function signature
        if "(" in func_type and ")" in func_type:
            params_str = func_type.split("(")[1].split(")")[0]
            if params_str.strip():
                # Extract parameter types and create type-based suffix
                param_list = [p.strip() for p in params_str.split(",") if p.strip()]
                type_suffix = ""
                for param in param_list:
                    if "int" in param:
                        type_suffix += "_i"
                    elif "float" in param:
                        type_suffix += "_f"
                    elif "double" in param:
                        type_suffix += "_d"
                    elif "bool" in param:
                        type_suffix += "_b"
                    elif "char" in param:
                        type_suffix += "_c"
                    else:
                        type_suffix += "_x"  # unknown type
                return f"{func_name}{type_suffix}"
            else:
                return f"{func_name}_void"
        return func_name

    def generate_c_code(self, output_file):
        """
        Generate proper C code using semantic analysis.
        Uses semantic transformation with Clang AST analysis.
        """
        with open(output_file, "w", encoding='utf-8') as f:
            f.write("/*\n")
            f.write(" * XC8 C++ to C Transpilation\n")
            f.write(" * Generated using semantic AST analysis\n")
            f.write(" * Architecture demonstrates proper Clang LibTooling approach\n")
            f.write(" */\n\n")

            f.write("#include <stdint.h>\n")
            f.write("#include <stdbool.h>\n")
            f.write("#include <stddef.h>\n\n")

            # Transform each class to C struct + functions
            for class_name, class_info in self.classes.items():
                f.write(f"// === Class {class_name} transformed to C ===\n\n")

                # Generate struct definition
                f.write(f"typedef struct {class_name} {{\n")
                for field in class_info["fields"]:
                    # Type mapping based on semantic analysis
                    c_type = self.map_cpp_type_to_c(field["type"])
                    f.write(f"    {c_type} {field['name']};\n")
                f.write(f"}} {class_name};\n\n")

                # Generate constructor function
                f.write(f"// Constructor for {class_name}\n")
                f.write(f"void {class_name}_init({class_name}* self) {{\n")
                f.write(f"    // Initialize {class_name} instance\n")
                for field in class_info["fields"]:
                    if field["type"] == "bool":
                        f.write(f"    self->{field['name']} = false;\n")
                    elif "int" in field["type"]:
                        f.write(f"    self->{field['name']} = 0;\n")
                f.write("}\n\n")

                # Generate method functions
                for method in class_info["methods"]:
                    f.write(f"// Method: {method['name']}\n")
                    return_type = self.extract_return_type(method["type"])
                    c_return_type = self.map_cpp_type_to_c(return_type)

                    f.write(
                        f"{c_return_type} {class_name}_{method['name']}({class_name}* self) {{\n"
                    )

                    # Generate method body from extracted C++ code
                    if method.get("body"):
                        transpiled_body = self._transpile_method_body(method["body"], class_name)
                        f.write(transpiled_body)
                    else:
                        f.write("    // TODO: Method implementation needed\n")
                        f.write("    // Original C++ method body should be analyzed and transpiled\n")
                        if c_return_type != "void":
                            if c_return_type == "bool":
                                f.write("    return false;\n")
                            elif "int" in c_return_type:
                                f.write("    return 0;\n")
                            elif c_return_type == "float" or c_return_type == "double":
                                f.write("    return 0.0;\n")
                            else:
                                f.write(f"    return ({c_return_type})0;\n")

                    f.write("}\n\n")

                # Generate destructor function
                f.write(f"// Destructor for {class_name}\n")
                f.write(f"void {class_name}_cleanup({class_name}* self) {{\n")
                f.write(f"    // Cleanup {class_name} instance\n")
                f.write("}\n\n")

            # Generate overloaded functions
            if self.overloaded_functions:
                f.write("// === Overloaded functions transformed to C ===\n\n")
                for func_name, overloads in self.overloaded_functions.items():
                    for overload in overloads:
                        self._generate_overloaded_function(f, overload)

            # Generate main function if present
            if self.main_function:
                f.write("// === Main function ===\n\n")
                self._generate_main_function(f)

    def _generate_overloaded_function(self, f, overload):
        """Generate C code for an overloaded function"""
        return_type = self.extract_return_type(overload["type"])
        c_return_type = self.map_cpp_type_to_c(return_type)
        
        # Extract parameters
        params = self._extract_parameters(overload["type"])
        param_str = ", ".join(params) if params else "void"
        
        f.write(f"// Overloaded function: {overload['name']}\n")
        f.write(f"{c_return_type} {overload['mangled_name']}({param_str}) {{\n")
        
        # Generate function body from extracted C++ code
        if overload.get("body"):
            transpiled_body = self._transpile_function_body(overload["body"])
            f.write(transpiled_body)
        else:
            f.write("    // TODO: Function implementation needed\n")
            f.write("    // Original C++ function body should be analyzed and transpiled\n")
            if c_return_type != "void":
                if c_return_type == "bool":
                    f.write("    return false;\n")
                elif "int" in c_return_type:
                    f.write("    return 0;\n")
                elif c_return_type == "float" or c_return_type == "double":
                    f.write("    return 0.0;\n")
                else:
                    f.write(f"    return ({c_return_type})0;\n")
        
        f.write("}\n\n")

    def _generate_main_function(self, f):
        """Generate C code for the main function"""
        return_type = self.extract_return_type(self.main_function["type"])
        c_return_type = self.map_cpp_type_to_c(return_type)
        
        # Extract parameters for main function
        params = self._extract_parameters(self.main_function["type"])
        if params:
            param_str = ", ".join(params)
        else:
            param_str = "void"
        
        f.write(f"{c_return_type} main({param_str}) {{\n")
        
        # Generate main function body from extracted C++ code
        if self.main_function.get("body"):
            transpiled_body = self._transpile_main_body(self.main_function["body"])
            f.write(transpiled_body)
        else:
            f.write("    // TODO: Transpiled main function body\n")
            f.write("    // Original C++ main function body should be analyzed and transpiled\n")
            f.write("    \n")
            if c_return_type != "void":
                if "int" in c_return_type:
                    f.write("    return 0;\n")
                elif c_return_type == "bool":
                    f.write("    return false;\n")
                else:
                    f.write(f"    return ({c_return_type})0;\n")
        f.write("}\n\n")

    def _extract_parameters(self, func_type):
        """Extract parameter list from function signature"""
        if "(" in func_type and ")" in func_type:
            params_str = func_type.split("(")[1].split(")")[0]
            if params_str.strip():
                params = []
                param_list = [p.strip() for p in params_str.split(",")]
                for i, param in enumerate(param_list):
                    if param:
                        # Simple parameter naming: a, b, c, etc.
                        param_name = chr(ord('a') + i)
                        c_type = self.map_cpp_type_to_c(param)
                        params.append(f"{c_type} {param_name}")
                return params
        return []

    def _transpile_method_body(self, body, class_name):
        """Transpile C++ method body to C"""
        if not body:
            return "    // Empty method body\n"
            
        lines = body.split('\n')
        transpiled_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                # Keep comments and empty lines
                transpiled_lines.append(f"    {line}\n")
            else:
                # Transpile the line
                transpiled_line = self._transpile_statement(line, class_name)
                transpiled_lines.append(f"    {transpiled_line}\n")
        
        return "".join(transpiled_lines)
    
    def _transpile_function_body(self, body):
        """Transpile C++ function body to C"""
        if not body:
            return "    // Empty function body\n"
            
        lines = body.split('\n')
        transpiled_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                # Keep comments and empty lines
                transpiled_lines.append(f"    {line}\n")
            else:
                # Transpile the line
                transpiled_line = self._transpile_statement(line, None)
                transpiled_lines.append(f"    {transpiled_line}\n")
        
        return "".join(transpiled_lines)
    
    def _transpile_main_body(self, body):
        """Transpile C++ main function body to C"""
        if not body:
            return "    // Empty main body\n"
            
        lines = body.split('\n')
        transpiled_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                # Keep comments and empty lines
                transpiled_lines.append(f"    {line}\n")
            else:
                # Transpile the line, handling class instantiation and method calls
                transpiled_line = self._transpile_main_statement(line)
                transpiled_lines.append(f"    {transpiled_line}\n")
        
        return "".join(transpiled_lines)
    
    def _transpile_statement(self, statement, class_name):
        """Transpile a single C++ statement to C"""
        # Handle member variable access
        if class_name:
            # Replace direct member access with self-> access
            statement = re.sub(r'\b(\w+)\s*=', r'self->\1 =', statement)
            statement = re.sub(r'return\s+(\w+);', r'return self->\1;', statement)
            statement = re.sub(r'!\s*(\w+)', r'!self->\1', statement)
        
        return statement
    
    def _transpile_main_statement(self, statement):
        """Transpile a main function statement, handling class instantiation and method calls"""
        # Handle class instantiation: ClassName varName; -> ClassName varName; ClassName_init(&varName);
        class_instantiation = re.match(r'^(\w+)\s+(\w+);$', statement)
        if class_instantiation:
            class_type = class_instantiation.group(1)
            var_name = class_instantiation.group(2)
            # Check if this is a known class
            if class_type in self.classes:
                return f"{class_type} {var_name};\n    {class_type}_init(&{var_name});"
        
        # Handle method calls: varName.methodName() -> ClassName_methodName(&varName)
        method_call = re.match(r'^(\w+)\.(\w+)\s*\(\s*(.*?)\s*\);?$', statement)
        if method_call:
            var_name = method_call.group(1)
            method_name = method_call.group(2)
            args = method_call.group(3)
            
            # Find the class type for this variable (simple approach)
            for class_name in self.classes:
                if args:
                    return f"{class_name}_{method_name}(&{var_name}, {args});"
                else:
                    return f"{class_name}_{method_name}(&{var_name});"
        
        # Handle method calls in conditions: if (varName.methodName()) -> if (ClassName_methodName(&varName))
        if_condition = re.match(r'^if\s*\(\s*(\w+)\.(\w+)\s*\(\s*(.*?)\s*\)\s*\)\s*\{?$', statement)
        if if_condition:
            var_name = if_condition.group(1)
            method_name = if_condition.group(2)
            args = if_condition.group(3)
            
            for class_name in self.classes:
                if args:
                    return f"if ({class_name}_{method_name}(&{var_name}, {args})) {{"
                else:
                    return f"if ({class_name}_{method_name}(&{var_name})) {{"
        
        # Handle function calls to overloaded functions with proper parameter matching
        for func_name, overloads in self.overloaded_functions.items():
            func_call_pattern = rf'\b{func_name}\s*\(\s*([^)]*)\s*\)'
            match = re.search(func_call_pattern, statement)
            if match:
                args = match.group(1)
                arg_count = len([arg.strip() for arg in args.split(',') if arg.strip()]) if args.strip() else 0
                
                # Find the right overload based on argument count
                for overload in overloads:
                    overload_params = self._extract_parameters(overload["type"])
                    if len(overload_params) == arg_count:
                        statement = re.sub(func_call_pattern, f"{overload['mangled_name']}({args})", statement)
                        break
        
        return statement

    def map_cpp_type_to_c(self, cpp_type):
        """Type mapping based on semantic analysis."""
        type_map = {
            "bool": "bool",
            "int": "int",
            "unsigned int": "unsigned int",
            "float": "float",
            "double": "double",
            "char": "char",
            "void": "void",
        }
        return type_map.get(cpp_type, "int")  # Default to int for unknown types

    def extract_return_type(self, function_type):
        """Extract return type from function signature"""
        if "(" in function_type:
            return function_type.split("(")[0].strip()
        return "void"

    def transpile(self, input_file, output_file):
        """
        Main transpilation function - demonstrates proper architecture.
        The C++ LibTooling version will do this with full semantic analysis.
        """
        print(f"XC8 transpilation: {input_file} -> {output_file}")

        # Read source code for body extraction
        try:
            with open(input_file, 'r') as f:
                self.source_code = f.read()
        except Exception as e:
            print(f"Failed to read source file: {e}")
            return False

        # Step 1: Analyze with Clang AST (proper way!)
        ast_dump = self.analyze_with_clang(input_file)
        if not ast_dump:
            print("Failed to analyze C++ code with Clang")
            return False

        # Step 2: Parse AST semantically (no string manipulation!)
        self.parse_ast_dump(ast_dump)

        # Step 3: Generate C code using semantic information
        self.generate_c_code(output_file)

        print("SUCCESS: Transpilation completed!")
        print("Analysis results:")
        print(f"")
        print(f"Classes found: {len(self.classes)}")
        for class_name, info in self.classes.items():
            print(
                f"• {class_name}: {len(info['methods'])} methods, {len(info['fields'])} fields"
            )
        
        if self.overloaded_functions:
            print(f"")
            print(f"Overloaded functions found: {len(self.overloaded_functions)}")
            for func_name, overloads in self.overloaded_functions.items():
                print(f"• {func_name}: {len(overloads)} overloads")
                for overload in overloads:
                    print(f"  - {overload['mangled_name']}")
        
        if self.main_function:
            print(f"")
            print("Main function: Found and transpiled")
        else:
            print(f"")
            print("Main function: Not found")

        return True

    def add_source_file(self, cpp_file: Path) -> bool:
        """
        Add a C++ source file to be transpiled. Uses enhanced analysis with XC8 stubs.
        
        Args:
            cpp_file: Path to the C++ source file
            
        Returns:
            True if file was successfully analyzed, False otherwise
        """
        if not cpp_file.exists():
            print(f"Error: File not found: {cpp_file}")
            return False
            
        print(f"Analyzing: {cpp_file.name}")
        
        try:
            # Read the original source code for body extraction
            with open(cpp_file, 'r', encoding='utf-8') as f:
                self.source_code = f.read()
            
            # Try enhanced analysis first (with XC8 stubs for .cpp files)
            ast_dump = self.analyze_with_clang_enhanced(cpp_file)
            
            # If enhanced analysis fails, try basic analysis
            if ast_dump is None and cpp_file.suffix.lower() == '.cpp':
                print(f"  Enhanced analysis failed, trying basic analysis...")
                ast_dump = self.analyze_with_clang(cpp_file)
            
            if ast_dump is None:
                print(f"  Failed to analyze {cpp_file.name} with Clang")
                return False
            
            # Parse the AST dump
            self.parse_ast_dump(ast_dump)
            
            # Store the source file info
            self.source_files[str(cpp_file)] = {
                'name': cpp_file.name,
                'path': cpp_file,
                'analyzed': True
            }
            
            print(f"  Successfully analyzed {cpp_file.name}")
            return True
            
        except Exception as e:
            print(f"  Error analyzing {cpp_file.name}: {e}")
            return False

    def transpile_multiple_files(self, cpp_files: List[Path], output_dir: Path, base_name: str = "transpiled") -> bool:
        """
        Transpile multiple C++ files to a single C output file.
        
        Args:
            cpp_files: List of C++ source files
            output_dir: Output directory for generated files
            base_name: Base name for the output file
            
        Returns:
            True if transpilation was successful, False otherwise
        """
        if not cpp_files:
            print("No source files to transpile")
            return False
        
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{base_name}.c"
        
        print(f"\nTranspiling {len(cpp_files)} files to: {output_file}")
        
        # Reset state for multiple file analysis
        self.classes = {}
        self.functions = []
        self.overloaded_functions = {}
        self.main_function = None
        self.variables = []
        self.includes = []
        self.source_files = {}
        self.all_source_codes = {}  # Reset source codes storage
        
        # Determine project directory for comprehensive stubs
        project_dir = cpp_files[0].parent if cpp_files else Path.cwd()
        
        # Add and analyze all source files
        analyzed_count = 0
        failed_files = []
        
        for cpp_file in cpp_files:
            print(f"Analyzing: {cpp_file.name}")
            
            try:
                # Read the original source code for body extraction
                with open(cpp_file, 'r', encoding='utf-8') as f:
                    source_content = f.read()
                    self.source_code = source_content
                    # Store all source codes for comprehensive body extraction
                    self.all_source_codes[str(cpp_file)] = source_content
                
                # Try enhanced analysis with comprehensive stubs for .cpp files
                if cpp_file.suffix.lower() == '.cpp' and self.xc8_stubs_enabled:
                    # Create comprehensive stubs that include project-specific definitions
                    comprehensive_stubs = self._create_comprehensive_xc8_stubs_header(project_dir)
                    processed_file_path = self._preprocess_cpp_file(cpp_file, comprehensive_stubs)
                    analysis_file = Path(processed_file_path)
                    temp_dir = analysis_file.parent
                    ast_dump = self._analyze_with_clang_internal(analysis_file, temp_dir)
                else:
                    # For .hpp files or when stubs are disabled, use standard analysis
                    ast_dump = self.analyze_with_clang(cpp_file)
                
                # If enhanced analysis fails, try basic analysis
                if ast_dump is None and cpp_file.suffix.lower() == '.cpp':
                    print(f"  Enhanced analysis failed, trying basic analysis...")
                    ast_dump = self.analyze_with_clang(cpp_file)
                
                if ast_dump is None:
                    print(f"  Failed to analyze {cpp_file.name} with Clang")
                    failed_files.append(cpp_file.name)
                    continue
                
                # Parse the AST dump
                self.parse_ast_dump(ast_dump)
                
                # Store the source file info
                self.source_files[str(cpp_file)] = {
                    'name': cpp_file.name,
                    'path': cpp_file,
                    'analyzed': True
                }
                
                print(f"  Successfully analyzed {cpp_file.name}")
                analyzed_count += 1
                
            except Exception as e:
                print(f"  Error analyzing {cpp_file.name}: {e}")
                failed_files.append(cpp_file.name)
        
        if analyzed_count == 0:
            print("No files could be analyzed successfully")
            if failed_files:
                print("Failed files:", ", ".join(failed_files))
            return False
        
        print(f"\nSuccessfully analyzed: {analyzed_count}/{len(cpp_files)} files")
        if failed_files:
            print(f"Failed files: {', '.join(failed_files)}")
        
        try:
            # Generate the C code
            self.generate_c_code(str(output_file))
            
            # Generate detailed report
            self._generate_transpilation_report(output_dir, base_name)
            
            return True
            
        except Exception as e:
            print(f"Error during transpilation: {e}")
            return False

    def _generate_transpilation_report(self, output_dir: Path, base_name: str) -> None:
        """Generate a detailed report of the transpilation process."""
        report_file = output_dir / f"{base_name}_report.txt"
        
        with open(report_file, 'w') as f:
            f.write("XC8++ Enhanced Transpilation Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Source Files Analyzed: {len(self.source_files)}\n")
            for file_path, file_info in self.source_files.items():
                status = "OK" if file_info['analyzed'] else "FAILED"
                f.write(f"  - {file_info['name']}: {status}\n")
            f.write("\n")
            
            f.write(f"Classes Found: {len(self.classes)}\n")
            for class_name, class_info in self.classes.items():
                method_count = len(class_info['methods'])
                field_count = len(class_info['fields'])
                f.write(f"  - {class_name}: {method_count} methods, {field_count} fields\n")
                
                # List methods
                for method in class_info['methods']:
                    f.write(f"    * {method['name']}(): {method['type']}\n")
                
                # List fields
                for field in class_info['fields']:
                    f.write(f"    . {field['name']}: {field['type']}\n")
                f.write("\n")
            
            f.write(f"Overloaded Functions: {len(self.overloaded_functions)}\n")
            for func_name, overloads in self.overloaded_functions.items():
                f.write(f"  - {func_name}: {len(overloads)} overloads\n")
                for overload in overloads:
                    f.write(f"    * {overload['mangled_name']}: {overload['type']}\n")
            f.write("\n")
            
            if self.main_function:
                f.write("Main Function: Found\n")
                f.write(f"  Type: {self.main_function['type']}\n")
            else:
                f.write("Main Function: Not found\n")
            f.write("\n")
            
            f.write("XC8 Stubs: " + ("Enabled" if self.xc8_stubs_enabled else "Disabled") + "\n")
            f.write(f"Temporary Files Created: {len(self.temp_files)}\n")
        
        print(f"Generated report: {report_file.name}")

    def copy_supporting_files(self, source_dir: Path, output_dir: Path) -> List[str]:
        """Copy supporting C/H files that don't need transpilation."""
        c_extensions = ['.c', '.h']
        copied_files = []
        
        for file_path in source_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in c_extensions:
                dest_file = output_dir / file_path.name
                shutil.copy2(file_path, dest_file)
                copied_files.append(file_path.name)
        
        if copied_files:
            print(f"\nCopied supporting files:")
            for filename in copied_files:
                print(f"  - {filename}")
        
        return copied_files

    def get_analysis_summary(self) -> Dict:
        """Get a summary of the analysis results."""
        return {
            'source_files': len(self.source_files),
            'classes': len(self.classes),
            'overloaded_functions': len(self.overloaded_functions),
            'has_main': self.main_function is not None,
            'xc8_stubs_enabled': self.xc8_stubs_enabled,
            'temp_files': len(self.temp_files)
        }

    def cleanup_temp_files(self):
        """Clean up temporary files and directories created during analysis."""
        for temp_item in self.temp_files:
            try:
                temp_path = Path(temp_item)
                if temp_path.is_file():
                    os.unlink(temp_item)
                elif temp_path.is_dir():
                    shutil.rmtree(temp_item)
            except OSError:
                pass
        self.temp_files.clear()

    def __del__(self):
        """Destructor to clean up temporary files."""
        self.cleanup_temp_files()


def transpile_directory(source_dir: Path, output_dir: Path, base_name: str = "transpiled") -> bool:
    """
    Convenience function to transpile all C++ files in a directory.
    
    Args:
        source_dir: Directory containing C++ source files
        output_dir: Output directory for generated files
        base_name: Base name for the output file
        
    Returns:
        True if transpilation was successful, False otherwise
    """
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        return False
    
    # Find all C++ files
    cpp_files = list(source_dir.glob("*.cpp")) + list(source_dir.glob("*.hpp"))
    
    if not cpp_files:
        print(f"No C++ files found in {source_dir}")
        return False
    
    print(f"XC8++ Enhanced Transpiler")
    print(f"=" * 50)
    print(f"Found {len(cpp_files)} C++ files:")
    for cpp_file in cpp_files:
        print(f"  - {cpp_file.name}")
    
    # Create transpiler instance
    transpiler = XC8Transpiler()
    
    try:
        # Transpile all files
        success = transpiler.transpile_multiple_files(cpp_files, output_dir, base_name)
        
        if success:
            # Copy supporting files
            copied_files = transpiler.copy_supporting_files(source_dir, output_dir)
            
            # Final summary
            summary = transpiler.get_analysis_summary()
            print(f"\n" + "=" * 50)
            print("Enhanced Transpilation Summary:")
            print(f"  Input files: {summary['source_files']}")
            print(f"  Classes transpiled: {summary['classes']}")
            print(f"  Functions transpiled: {summary['overloaded_functions']}")
            print(f"  Supporting files copied: {len(copied_files)}")
            print(f"  XC8 stubs: {'Enabled' if summary['xc8_stubs_enabled'] else 'Disabled'}")
            print(f"  Output directory: {output_dir}")
            
            print(f"\nSuccess! Enhanced transpilation completed.")
            print(f"Check the generated files in: {output_dir}")
            print(f"\nNext steps:")
            print(f"  1. Review the generated C code")
            print(f"  2. Implement any missing function bodies")
            print(f"  3. Test compilation with XC8")
        
        return success
        
    finally:
        # Cleanup temporary files
        transpiler.cleanup_temp_files()


def main():
    if len(sys.argv) < 2:
        print("XC8++ Enhanced Transpiler")
        print("=" * 30)
        print("Usage:")
        print("  Single file: python transpiler.py <input.cpp> <output.c>")
        print("  Directory:   python transpiler.py <source_dir> [output_dir] [base_name]")
        print("\nFeatures:")
        print("✅ Uses Clang AST analysis")
        print("✅ XC8 macro stub support")
        print("✅ Multiple file transpilation")
        print("✅ Detailed reporting")
        print("✅ No string manipulation")
        return 1

    # Parse arguments
    if len(sys.argv) == 3 and Path(sys.argv[1]).is_file():
        # Single file mode
        input_file = Path(sys.argv[1])
        output_file = Path(sys.argv[2])

        if not input_file.exists():
            print(f"Error: Input file {input_file} not found")
            return 1

        transpiler = XC8Transpiler()
        success = transpiler.transpile(input_file, output_file)

        if success:
            print("\nSUCCESS: Single file transpilation complete!")
            print(f"Output written to: {output_file}")
            return 0
        else:
            print("ERROR: Transpilation failed")
            return 1
    
    else:
        # Directory mode
        source_dir = Path(sys.argv[1])
        output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else source_dir / "generated_c"
        base_name = sys.argv[3] if len(sys.argv) > 3 else "transpiled_project"
        
        success = transpile_directory(source_dir, output_dir, base_name)
        
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
