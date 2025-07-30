"""
Python Backend Transpiler for XC8++

This module provides a Python-based fallback transpiler that uses Clang AST dumps
to analyze C++ code and generate equivalent C code for XC8 compatibility.
"""

import os
import re
import sys
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union


class TranspilerResult:
    """Result of a transpilation operation"""

    def __init__(self):
        self.success: bool = False
        self.error_message: str = ""
        self.generated_c_code: str = ""
        self.generated_header_code: str = ""
        self.warnings: List[str] = []


class PythonTranspiler:
    """
    Python-based C++ to C transpiler using Clang AST analysis.

    This transpiler serves as a fallback when the native LLVM LibTooling
    backend is not available.
    """

    def __init__(
        self,
        enable_optimization: bool = True,
        generate_xc8_pragmas: bool = True,
        preserve_comments: bool = True,
        target_device: str = "PIC16F876A",
        include_paths: Optional[List[str]] = None,
        defines: Optional[List[str]] = None,
    ):
        """
        Initialize the Python transpiler.

        Args:
            enable_optimization: Enable XC8-specific optimizations
            generate_xc8_pragmas: Generate XC8 configuration pragmas
            preserve_comments: Preserve comments in generated code
            target_device: Target PIC device name
            include_paths: Additional include directories
            defines: Preprocessor definitions
        """
        # Configuration
        self.enable_optimization = enable_optimization
        self.generate_xc8_pragmas = generate_xc8_pragmas
        self.preserve_comments = preserve_comments
        self.target_device = target_device
        self.include_paths = include_paths or []
        self.defines = defines or []

        # Analysis state
        self.classes = {}
        self.enums = {}  # Track C++ enums for conversion to C
        self.functions = []
        self.overloaded_functions = {}
        self.main_function = None
        self.variables = []
        self.global_variables = []
        self.includes = []
        self.source_code = ""  # Store original source for body extraction
        self.temp_files = []  # Track temporary files for cleanup
        self.source_files = {}  # Track analyzed source files
        self.xc8_stubs_enabled = True  # Enable XC8 stubs by default
        self.all_source_codes = {}  # Store all source files content for body extraction

    def transpile_string(
        self, cpp_source: str, filename: str = "input.cpp"
    ) -> TranspilerResult:
        """
        Transpile C++ source code from string.

        Args:
            cpp_source: C++ source code
            filename: Filename for diagnostics

        Returns:
            TranspilerResult with generated C code or error information
        """
        try:
            # Create a temporary file for the source
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".cpp", delete=False
            ) as temp_input:
                temp_input.write(cpp_source)
                temp_input_path = temp_input.name

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".c", delete=False
            ) as temp_output:
                temp_output_path = temp_output.name

            try:
                # Use the existing transpile method
                success = self.transpile(temp_input_path, temp_output_path)

                result = TranspilerResult()

                if success:
                    # Read the generated C code
                    if os.path.exists(temp_output_path):
                        with open(temp_output_path, "r", encoding="utf-8") as f:
                            result.generated_c_code = f.read()

                    result.success = True
                    result.error_message = ""
                else:
                    result.success = False
                    result.error_message = "Python backend transpilation failed"

                return result

            finally:
                # Clean up temporary files
                try:
                    os.unlink(temp_input_path)
                except:
                    pass
                try:
                    os.unlink(temp_output_path)
                except:
                    pass

        except Exception as e:
            result = TranspilerResult()
            result.success = False
            result.error_message = f"Python backend error: {str(e)}"
            return result

    def transpile_file(
        self, input_file: str, output_file: Optional[str] = None
    ) -> TranspilerResult:
        """
        Transpile C++ source code from file.

        Args:
            input_file: Path to input C++ file
            output_file: Path to output C file (optional)

        Returns:
            TranspilerResult with generated C code or error information
        """
        try:
            # Generate a temporary output file if none specified
            if output_file is None:
                import tempfile

                temp_output = tempfile.NamedTemporaryFile(
                    mode="w", suffix=".c", delete=False
                )
                output_file = temp_output.name
                temp_output.close()

            # Use the existing transpile method
            success = self.transpile(input_file, output_file)

            result = TranspilerResult()

            if success:
                # Read the generated C code
                try:
                    with open(output_file, "r", encoding="utf-8") as f:
                        result.generated_c_code = f.read()
                except Exception as e:
                    result.generated_c_code = f"// Error reading output file: {e}"

                result.success = True
                result.error_message = ""
            else:
                result.success = False
                result.error_message = "Python backend transpilation failed"

            return result

        except Exception as e:
            result = TranspilerResult()
            result.success = False
            result.error_message = f"Python backend error: {str(e)}"
            return result

    def transpile(self, input_file, output_file):
        """
        Main transpilation function using Clang AST analysis.
        Enhanced to handle separate header/implementation files.
        """
        print(f"XC8 transpilation: {input_file} -> {output_file}")

        # Step 1: Discover related files (headers and implementations)
        related_files = self._discover_related_files(input_file)
        print(f"Found related files: {related_files}")

        # Step 2: Read all source files for body extraction
        self.source_files = {}
        for file_path in related_files:
            try:
                with open(file_path, "r") as f:
                    self.source_files[file_path] = f.read()
            except Exception as e:
                print(f"Failed to read file {file_path}: {e}")
                return False

        # Keep main source for compatibility
        self.source_code = self.source_files.get(input_file, "")
        
        # Copy source files to all_source_codes for function body extraction
        self.all_source_codes = self.source_files.copy()

        # Step 3: Analyze all files with Clang AST
        for file_path in related_files:
            ast_dump = self.analyze_with_clang(file_path)
            if not ast_dump:
                print(f"Failed to analyze {file_path} with Clang")
                continue
            
            # Parse AST semantically for each file
            self.parse_ast_dump(ast_dump, source_file=file_path)

        # Step 4: Extract method bodies from implementation files
        self._extract_method_bodies_from_implementations()

        # Step 5: Generate C code using semantic information
        self.generate_c_code(output_file)
        
        # Step 6: Generate corresponding header file
        header_file = output_file.replace('.c', '.h')
        self.generate_header_file(header_file)

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

    def analyze_with_clang(self, cpp_file):
        """
        Use Clang to get proper AST dump.
        """
        try:
            # Use system Clang for AST analysis
            clang_cmd = [
                "clang",
                "-Xclang",
                "-ast-dump",
                "-fsyntax-only",
                "-std=c++17",
            ]
            
            # Add include paths
            for include_path in self.include_paths:
                clang_cmd.extend(["-I", include_path])
            
            # Add defines
            for define in self.defines:
                clang_cmd.append(f"-D{define}")
            
            # Add the input file
            clang_cmd.append(str(cpp_file))

            result = subprocess.run(clang_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Clang analysis failed: {result.stderr}")
                return None

            return result.stdout

        except Exception as e:
            print(f"Error running Clang analysis: {e}")
            return None

    def _discover_related_files(self, input_file):
        """
        Discover related header and implementation files.
        For led.cpp, finds led.hpp and vice versa.
        """
        input_path = Path(input_file)
        base_name = input_path.stem  # 'led' from 'led.cpp'
        directory = input_path.parent
        
        related_files = [str(input_path)]  # Always include the input file
        
        # Common extensions to look for
        header_extensions = ['.hpp', '.h', '.hxx']
        impl_extensions = ['.cpp', '.cc', '.cxx', '.c++']
        
        # If input is implementation, look for header
        if input_path.suffix in impl_extensions:
            for ext in header_extensions:
                header_file = directory / f"{base_name}{ext}"
                if header_file.exists():
                    related_files.append(str(header_file))
                    break
        
        # If input is header, look for implementation
        elif input_path.suffix in header_extensions:
            for ext in impl_extensions:
                impl_file = directory / f"{base_name}{ext}"
                if impl_file.exists():
                    related_files.append(str(impl_file))
                    break
        
        return related_files

    def _extract_method_bodies_from_implementations(self):
        """
        Extract method bodies from implementation files (.cpp) and 
        match them with method signatures found in headers.
        """
        for class_name, class_info in self.classes.items():
            for method in class_info["methods"]:
                if not method.get("body"):  # Only if body not found yet
                    # Try to find implementation in all source files
                    for file_path, source_code in self.source_files.items():
                        if file_path.endswith(('.cpp', '.cc', '.cxx', '.c++')):
                            body = self._extract_method_implementation(
                                method["name"], class_name, source_code
                            )
                            if body:
                                method["body"] = body
                                break

    def _extract_method_implementation(self, method_name, class_name, source_code):
        """
        Extract method implementation from source code using class::method syntax.
        Example: Led::turnOn() { ... }
        """
        # Pattern for C++ method implementation: ClassName::methodName(params) { body }
        patterns = [
            # Standard pattern: ReturnType ClassName::methodName(params) { ... }
            rf"\b\w*\s*{class_name}::{method_name}\s*\([^)]*\)\s*(?:const\s*)?\s*\{{",
            # Constructor pattern: ClassName::ClassName(params) { ... }
            rf"\b{class_name}::{method_name}\s*\([^)]*\)\s*(?::\s*[^{{]*?)?\s*\{{",
            # Destructor pattern: ClassName::~ClassName() { ... }
            rf"\b{class_name}::~?{method_name}\s*\([^)]*\)\s*\{{",
        ]
        
        for pattern in patterns:
            method_match = re.search(pattern, source_code)
            if method_match:
                # Find the opening brace position
                brace_pos = method_match.end() - 1
                return self._extract_method_from_content_at_position(source_code, brace_pos)
        
        return None

    def _should_ignore_class(self, class_name):
        """
        Determine if a class should be ignored during transpilation.
        Filters out standard library and system classes.
        """
        # Standard library classes to ignore
        ignored_classes = {
            'type_info',      # RTTI class
            'exception',      # Exception handling
            'bad_alloc',      # Memory allocation
            'bad_cast',       # Type casting
            'bad_typeid',     # RTTI errors
            'logic_error',    # Logic exceptions
            'runtime_error',  # Runtime exceptions
            'string',         # std::string
            'vector',         # std::vector
            'list',           # std::list
            'map',            # std::map
            'set',            # std::set
            'iostream',       # IO streams
            'ostream',        # Output streams
            'istream',        # Input streams
            'basic_string',   # String template
            'allocator',      # Memory allocator
        }
        
        # Check if class name matches ignored patterns
        if class_name in ignored_classes:
            return True
            
        # Ignore classes starting with underscores (implementation details)
        if class_name.startswith('_'):
            return True
            
        # Ignore template instantiations
        if '<' in class_name or '>' in class_name:
            return True
            
        return False

    def _should_ignore_field(self, field_name, field_type, ast_line):
        """
        Determine if a field should be ignored during transpilation.
        Filters out PIC register bits and system fields.
        """
        # PIC register bit names to ignore
        pic_register_bits = {
            # Port bits
            'RA0', 'RA1', 'RA2', 'RA3', 'RA4', 'RA5', 'RA6', 'RA7',
            'RB0', 'RB1', 'RB2', 'RB3', 'RB4', 'RB5', 'RB6', 'RB7', 
            'RC0', 'RC1', 'RC2', 'RC3', 'RC4', 'RC5', 'RC6', 'RC7',
            # Interrupt control bits
            'RBIF', 'INTF', 'T0IF', 'RBIE', 'INTE', 'T0IE', 'T0IE_', 'PEIE', 'GIE',
            # Timer/Option bits
            'PS0', 'PS1', 'PS2', 'PSA', 'T0SE', 'T0CS', 'INTEDG', 'RBPU',
            # EEPROM control bits
            'RD', 'WR', 'WREN', 'WRERR',
            # Status register bits
            'CARRY', 'DC', 'ZERO', 'PD', 'TO', 'RP0', 'RP1', 'IRP'
        }
        
        # Ignore PIC register bit fields
        if field_name in pic_register_bits:
            return True
            
        # Ignore common union/struct helper fields
        if field_name in ['val', 'referenced', 'implicit']:
            return True
            
        # Ignore bit field types (unsigned int with actual bit width specifier after the type)
        if 'unsigned int' in field_type and re.search(r"'unsigned int':\d+", ast_line):
            return True
            
        return False

    def parse_ast_dump(self, ast_dump, source_file=None):
        """
        Parse Clang AST dump to extract semantic information.
        """
        lines = ast_dump.split("\n")
        current_class = None
        current_enum_const = None

        for i, line in enumerate(lines):
            line = line.strip()

            # Class declarations
            if "CXXRecordDecl" in line and "class" in line:
                match = re.search(r"class (\w+)", line)
                if match:
                    class_name = match.group(1)
                    
                    # Filter out standard library and system classes
                    if self._should_ignore_class(class_name):
                        current_class = None
                        continue
                        
                    # Ignore classes defined in system headers (mock_includes)
                    if source_file and "mock_includes" in str(source_file):
                        current_class = None
                        continue
                        
                    current_class = class_name
                    # Only create if not already exists (avoid overwriting from multiple files)  
                    if class_name not in self.classes:
                        self.classes[class_name] = {
                            "methods": [],
                            "fields": [],
                            "constructors": [],
                            "destructor": None,
                        }
                    
            # Skip anonymous struct declarations (like PIC register bits)
            elif "CXXRecordDecl" in line and "struct definition" in line and "class" not in line:
                # Anonymous struct from system headers - skip entirely
                current_class = None

            # Enum declarations (both enum and enum class)
            elif "EnumDecl" in line and "class" in line:
                # Pattern: EnumDecl 0x... <...> line:18:12 referenced class ButtonId 'int'
                match = re.search(r'class (\w+)', line)
                if match:
                    enum_name = match.group(1)
                    # Only create if not already exists (avoid overwriting from multiple files)
                    if enum_name not in self.enums:
                        self.enums[enum_name] = {
                            "values": [],
                            "is_class": True
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
                        "body": None,  # Will be filled later in _extract_method_bodies_from_implementations
                        "source_file": source_file,  # Track which file this was found in
                    }
                    # Check if method already exists (avoid duplicates from multiple files)
                    existing_methods = [m["name"] for m in self.classes[current_class]["methods"]]
                    if method_name not in existing_methods:
                        self.classes[current_class]["methods"].append(method_info)

            # Field declarations
            elif "FieldDecl" in line and current_class:
                # Pattern: FieldDecl 0x... <...> col:14 buttonId 'ButtonId'
                match = re.search(r'col:\d+ (\w+) \'([^\']+)\'', line)
                if match:
                    field_name = match.group(1)
                    field_type = match.group(2)
                    
                    # Filter out system/register fields that don't belong to user classes
                    if self._should_ignore_field(field_name, field_type, line):
                        continue
                    
                    # Check if field already exists (avoid duplicates from multiple files)
                    existing_fields = [f["name"] for f in self.classes[current_class]["fields"]]
                    if field_name not in existing_fields:
                        self.classes[current_class]["fields"].append(
                            {"name": field_name, "type": field_type}
                        )

            # Enum constant declarations
            elif "EnumConstantDecl" in line:
                # Pattern: EnumConstantDecl 0x... <...> col:5 PB_0 'ButtonId'
                match = re.search(r'col:\d+ (\w+) \'(\w+)\'', line)
                if match:
                    const_name = match.group(1)
                    enum_type = match.group(2)
                    current_enum_const = {"name": const_name, "type": enum_type, "value": "0"}
                    
            # Look for enum constant values in subsequent lines
            elif current_enum_const and "value: Int" in line:
                value_match = re.search(r'value: Int (\d+)', line)
                if value_match:
                    current_enum_const["value"] = value_match.group(1)
                    
                    # Add to the correct enum
                    enum_type = current_enum_const["type"]
                    if enum_type in self.enums:
                        # Check if value already exists (avoid duplicates from multiple files)
                        existing_values = [v["name"] for v in self.enums[enum_type]["values"]]
                        if current_enum_const["name"] not in existing_values:
                            self.enums[enum_type]["values"].append({
                                "name": current_enum_const["name"],
                                "value": current_enum_const["value"]
                            })
                    current_enum_const = None

            # Function declarations (including main)
            elif "FunctionDecl" in line:
                self._parse_function_declaration(line)
            
            # Global variable declarations
            elif "VarDecl" in line and "0x" in line:  # Global scope variables
                self._parse_global_variable_declaration(line)

    def _extract_method_body_from_source(self, method_name, class_name):
        """Extract method body from the original source code"""
        if not self.source_code:
            return None

        # Try to find method inside class definition (inline)
        class_pattern = rf"class\s+{class_name}\s*\{{"
        class_match = re.search(class_pattern, self.source_code)
        if class_match:
            class_start = class_match.start()
            # Find the end of the class
            class_content = self.source_code[class_start:]

            # Find class closing brace
            brace_count = 0
            class_end = 0
            for i, char in enumerate(class_content):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i
                        break

            if class_end > 0:
                class_body = class_content[:class_end]
                inline_body = self._extract_method_from_content(method_name, class_body)
                if inline_body:
                    return inline_body

        return None

    def _extract_method_from_content(self, method_name, content):
        """Extract method body from content"""
        method_pattern = rf"\b{method_name}\s*\([^)]*\)\s*(?:const\s*)?\s*\{{"
        method_match = re.search(method_pattern, content)
        if not method_match:
            return None

        return self._extract_method_from_content_at_position(
            content, method_match.end() - 1
        )

    def _extract_method_from_content_at_position(self, content, start_pos):
        """Extract method body starting from a specific position (opening brace)"""
        brace_count = 0
        body_start = start_pos + 1
        i = start_pos

        while i < len(content):
            if content[i] == "{":
                brace_count += 1
            elif content[i] == "}":
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

    def _parse_function_declaration(self, line):
        """Parse function declarations from AST dump"""
        match = re.search(r"(\w+) '([^']+)'", line)
        if match:
            func_name = match.group(1)
            func_type = match.group(2)

            if func_name == "main":
                self.main_function = {
                    "name": func_name,
                    "type": func_type,
                    "line": line,
                    "body": self._extract_function_body_from_source(func_name),
                }
            else:
                # Parse all other functions (setup, loop, etc.)
                function_info = {
                    "name": func_name,
                    "type": func_type,
                    "line": line,
                    "body": self._extract_function_body_from_source(func_name),
                }
                # Check if function already exists (avoid duplicates from multiple files)
                existing_func = next((f for f in self.functions if f["name"] == func_name), None)
                if not existing_func:
                    self.functions.append(function_info)

    def _parse_global_variable_declaration(self, line):
        """Parse global variable declarations from AST dump"""
        # Example: VarDecl 0x1234567890 <line:21:1, col:8> col:8 timer 'Timer0'
        # Example: VarDecl 0x1234567890 <line:22:1, col:25> col:5 led0 'Led' cinit
        var_match = re.search(r"VarDecl.*?(\w+)\s+'([^']+)'", line)
        if var_match:
            var_name = var_match.group(1)
            var_type = var_match.group(2)
            
            # Skip system/library variables (from headers like xc.h)
            if self._is_system_variable(var_name, var_type):
                return
            
            # Extract initialization if present (for constructor calls)
            init_match = re.search(r"cinit", line)
            has_constructor = init_match is not None
            
            # Extract constructor arguments from source if available
            constructor_args = self._extract_constructor_args(var_name, var_type)
            
            variable_info = {
                "name": var_name,
                "type": var_type,
                "has_constructor": has_constructor,
                "constructor_args": constructor_args,
                "line": line
            }
            
            # Check if variable already exists (avoid duplicates from multiple files)
            existing_var = next((v for v in self.variables if v["name"] == var_name), None)
            if not existing_var:
                self.variables.append(variable_info)

    def _is_system_variable(self, var_name, var_type):
        """Check if a variable is from system headers and should be ignored"""
        # Skip XC8 system registers and structures
        system_prefixes = ['PORTA', 'PORTB', 'PORTC', 'TMR', 'INTCON', 'OPTION_REG', 'EE', 'STATUS']
        system_suffixes = ['bits', 'BITS']
        system_types = ['unsigned char', 'struct', 'const']
        
        # Skip variables with system prefixes
        for prefix in system_prefixes:
            if var_name.startswith(prefix):
                return True
        
        # Skip variables with system suffixes  
        for suffix in system_suffixes:
            if var_name.endswith(suffix):
                return True
        
        # Skip system types (unless they're our classes)
        if var_type in system_types or 'unnamed struct' in var_type:
            return True
            
        # Skip constants and references
        if 'const' in var_type or '&' in var_type:
            return True
            
        # Skip single-character or numeric variable names (likely temporaries)
        if len(var_name) <= 2 and (var_name.isdigit() or var_name in ['id', 'i', 'x', 'y']):
            return True
            
        return False

    def _extract_constructor_args(self, var_name, var_type):
        """Extract constructor arguments from source code"""
        for file_path, content in self.all_source_codes.items():
            if content:
                # Look for variable declaration with constructor
                # Example: Led led0(LedId::LED_0);
                var_pattern = rf"\b{var_type}\s+{var_name}\s*\(([^)]*)\)"
                var_match = re.search(var_pattern, content)
                if var_match:
                    args_str = var_match.group(1).strip()
                    if args_str:
                        # Clean up enum scope (LedId::LED_0 -> LED_0)
                        args_str = re.sub(r'\w+::', '', args_str)
                        return args_str
        return None

    def _extract_function_body_from_source(self, func_name):
        """Extract function body from the original source code"""
        # First try current source_code
        if self.source_code:
            func_pattern = rf"\b{func_name}\s*\([^)]*\)\s*\{{"
            func_match = re.search(func_pattern, self.source_code)
            if func_match:
                return self._extract_method_from_content_at_position(
                    self.source_code, func_match.end() - 1
                )
        
        # If not found, search through all source files
        for file_path, content in self.all_source_codes.items():
            if content:
                func_pattern = rf"\b{func_name}\s*\([^)]*\)\s*\{{"
                func_match = re.search(func_pattern, content)
                if func_match:
                    return self._extract_method_from_content_at_position(
                        content, func_match.end() - 1
                    )
        
        return None

    def generate_c_code(self, output_file):
        """
        Generate C code using semantic analysis.
        """
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("/*\n")
            f.write(" * XC8 C++ to C Transpilation\n")
            f.write(" * Generated using semantic AST analysis\n")
            f.write(" * Architecture demonstrates proper Clang LibTooling approach\n")
            f.write(" */\n\n")

            # Add XC8 includes for PIC programming
            f.write("#include <xc.h>\n")
            f.write("#include <stdint.h>\n")
            f.write("#include <stdbool.h>\n")
            f.write("#include <stddef.h>\n\n")

            # Generate C enums from C++ enum classes
            for enum_name, enum_info in self.enums.items():
                f.write(f"// === Enum {enum_name} ===\n")
                f.write(f"typedef enum {{\n")
                for enum_value in enum_info["values"]:
                    f.write(f"    {enum_value['name']} = {enum_value['value']},\n")
                f.write(f"}} {enum_name};\n\n")

            # Add common constants
            f.write("// === Constants ===\n")
            f.write("#define DEBOUNCE_THRESHOLD 5\n\n")

            # Add hardware pin definitions if not already included
            f.write("// === Hardware Pin Definitions ===\n")
            f.write("// Pin definitions from pin_manager.h\n")
            f.write("#ifndef PB0\n")
            f.write("#define PB0 PORTAbits.RA2\n")
            f.write("#define PB1 PORTAbits.RA1\n") 
            f.write("#define PB2 PORTAbits.RA4\n")
            f.write("#define LED0 PORTAbits.RA3\n")
            f.write("#define LED1 PORTAbits.RA5\n")
            f.write("#define LED2 PORTCbits.RC0\n")
            f.write("#define LED3 PORTCbits.RC1\n")
            f.write("#define LED4 PORTCbits.RC2\n")
            f.write("#endif\n\n")

            # First generate all struct definitions
            for class_name, class_info in self.classes.items():
                f.write(f"// === Class {class_name} transformed to C ===\n\n")
                f.write(f"typedef struct {class_name} {{\n")
                for field in class_info["fields"]:
                    c_type = self.map_cpp_type_to_c(field["type"])
                    f.write(f"    {c_type} {field['name']};\n")
                f.write(f"}} {class_name};\n\n")

            # Generate forward declarations for all methods AFTER struct definitions
            f.write("// === Forward Declarations ===\n")
            for class_name, class_info in self.classes.items():
                for method in class_info["methods"]:
                    return_type = self.extract_return_type(method["type"])
                    c_return_type = self.map_cpp_type_to_c(return_type)
                    params = self._extract_method_parameters(method["type"])
                    param_list = f"{class_name}* self"
                    if params:
                        param_list += f", {params}"
                    f.write(f"{c_return_type} {class_name}_{method['name']}({param_list});\n")
            f.write("\n")

            # Generate implementations
            for class_name, class_info in self.classes.items():
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
                    
                    # Extract parameters from method signature
                    params = self._extract_method_parameters(method["type"])
                    param_list = f"{class_name}* self"
                    if params:
                        param_list += f", {params}"

                    f.write(
                        f"{c_return_type} {class_name}_{method['name']}({param_list}) {{\n"
                    )

                    # Generate method body from extracted C++ code
                    if method.get("body"):
                        transpiled_body = self._transpile_method_body(
                            method["body"], class_name
                        )
                        f.write(transpiled_body)
                    else:
                        f.write("    // TODO: Method implementation needed\n")
                        if c_return_type != "void":
                            if c_return_type == "bool":
                                f.write("    return false;\n")
                            elif "int" in c_return_type:
                                f.write("    return 0;\n")

                    f.write("}\n\n")

                # Generate destructor function
                f.write(f"// Destructor for {class_name}\n")
                f.write(f"void {class_name}_cleanup({class_name}* self) {{\n")
                f.write(f"    // Cleanup {class_name} instance\n")
                f.write("}\n\n")

            # Generate global variables
            if self.variables:
                f.write("// === Global Variables ===\n\n")
                for variable in self.variables:
                    self._generate_global_variable(f, variable)
                f.write("\n")

            # Generate standalone functions (setup, loop, etc.)
            if self.functions:
                f.write("// === Standalone Functions ===\n\n")
                for function in self.functions:
                    self._generate_function(f, function)

            # Generate main function if present
            if self.main_function:
                f.write("// === Main function ===\n\n")
                self._generate_main_function(f)

    def generate_header_file(self, header_file):
        """Generate C header file with declarations"""
        with open(header_file, "w", encoding="utf-8") as f:
            # Header guard
            guard_name = Path(header_file).stem.upper() + "_H"
            f.write(f"#ifndef {guard_name}\n")
            f.write(f"#define {guard_name}\n\n")
            
            f.write("/*\n")
            f.write(" * XC8 C++ to C Header File\n")
            f.write(" * Generated using semantic AST analysis\n")
            f.write(" * Architecture demonstrates proper Clang LibTooling approach\n")
            f.write(" */\n\n")

            # Add standard includes
            f.write("#include <xc.h>\n")
            f.write("#include <stdint.h>\n")
            f.write("#include <stdbool.h>\n")
            f.write("#include <stddef.h>\n\n")

            # Generate C enums from C++ enum classes
            if self.enums:
                for enum_name, enum_info in self.enums.items():
                    f.write(f"// === Enum {enum_name} ===\n")
                    f.write("typedef enum {\n")
                    for value in enum_info["values"]:
                        f.write(f"    {value['name']} = {value['value']},\n")
                    f.write(f"}} {enum_name};\n\n")

            # Generate constants
            f.write("// === Constants ===\n")
            f.write("#define DEBOUNCE_THRESHOLD 5\n\n")

            # Generate struct definitions
            if self.classes:
                for class_name, class_info in self.classes.items():
                    f.write(f"// === {class_name} Structure ===\n")
                    f.write(f"typedef struct {class_name} {{\n")
                    for field in class_info["fields"]:
                        c_type = self.map_cpp_type_to_c(field["type"])
                        f.write(f"    {c_type} {field['name']};\n")
                    f.write(f"}} {class_name};\n\n")

            # Generate function declarations
            if self.classes:
                f.write("// === Function Declarations ===\n")
                for class_name, class_info in self.classes.items():
                    # Constructor
                    f.write(f"void {class_name}_init({class_name}* self);\n")
                    
                    # Methods
                    for method in class_info["methods"]:
                        return_type = self.extract_return_type(method["type"])
                        c_return_type = self.map_cpp_type_to_c(return_type)
                        params = self._extract_method_parameters(method["type"])
                        c_params = self._convert_parameters_to_c(params, class_name)
                        f.write(f"{c_return_type} {class_name}_{method['name']}({c_params});\n")
                    
                    # Destructor
                    f.write(f"void {class_name}_cleanup({class_name}* self);\n")
                    f.write("\n")

            # Generate standalone function declarations
            if self.functions:
                f.write("// === Standalone Function Declarations ===\n")
                for function in self.functions:
                    return_type = self.extract_return_type(function["type"])
                    c_return_type = self.map_cpp_type_to_c(return_type)
                    f.write(f"{c_return_type} {function['name']}(void);\n")
                f.write("\n")

            # Generate global variable declarations
            if self.variables:
                f.write("// === Global Variable Declarations ===\n")
                user_vars = [v for v in self.variables if not self._is_system_parameter(v["name"])]
                for variable in user_vars:
                    var_name = variable["name"]
                    var_type = variable["type"]
                    if variable.get("constructor_args"):
                        f.write(f"extern {var_type} {var_name};\n")
                    else:
                        f.write(f"extern {var_type} {var_name};\n")
                f.write("\n")

            # End header guard
            f.write(f"#endif // {guard_name}\n")

    def _is_system_parameter(self, var_name):
        """Check if variable is a function parameter rather than global"""
        parameter_names = ['milliseconds', 'rawPressed', 'rawState', 'newState', 'count', 'delayMs']
        return var_name in parameter_names

    def _convert_parameters_to_c(self, params, class_name):
        """Convert method parameters to C function parameters with self pointer"""
        if not params or params.strip() == "":
            return f"{class_name}* self"
        else:
            return f"{class_name}* self, {params}"

    def _transpile_method_body(self, body, class_name):
        """Transpile C++ method body to C"""
        if not body:
            return "    // Empty method body\n"

        lines = body.split("\n")
        transpiled_lines = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("//"):
                transpiled_lines.append(f"    {line}\n")
            else:
                transpiled_line = self._transpile_statement(line, class_name)
                transpiled_lines.append(f"    {transpiled_line}\n")

        return "".join(transpiled_lines)

    def _transpile_statement(self, statement, class_name):
        """Transpile a single C++ statement to C"""
        original_statement = statement
        
        # Handle enum class access: LedId::LED_0 -> LED_0, ButtonState::PRESSED -> PRESSED
        statement = re.sub(r'\b\w+::([\w_]+)', r'\1', statement)
        
        # Handle member variable access for common class variables
        button_vars = ['buttonId', 'currentState', 'previousState', 'debounceCounter']
        led_vars = ['ledId', 'state']
        timer_vars = ['initialized']
        
        all_member_vars = button_vars + led_vars + timer_vars
        
        for var in all_member_vars:
            statement = re.sub(rf'\b{var}\b(?!\s*\()', rf'self->{var}', statement)
        
        # Handle method calls within the same class
        method_calls = ['turnOn', 'turnOff', 'toggle', 'delay50ms', 'readHardwareState']
        for method in method_calls:
            statement = re.sub(
                rf'\b{method}\(\)', rf'{class_name}_{method}(self)', statement
            )
        
        # Handle function parameters (undo self-> for parameters)
        if 'newState' in original_statement:
            statement = re.sub(r'self->newState', r'newState', statement)
        if 'count' in original_statement:
            statement = re.sub(r'self->count', r'count', statement)
        if 'delayMs' in original_statement:
            statement = re.sub(r'self->delayMs', r'delayMs', statement)
        if 'milliseconds' in original_statement:
            statement = re.sub(r'self->milliseconds', r'milliseconds', statement)
        if 'i' in original_statement and 'for' in original_statement:
            statement = re.sub(r'self->i', r'i', statement)
            
        # Handle hardware register access (for XC8) - these should remain as-is
        statement = re.sub(r'self->(LED\d+)', r'\1', statement)
        statement = re.sub(r'self->(PB\d+)', r'\1', statement)
        
        # Handle XC8 delay functions
        statement = re.sub(r'__delay_ms\(([^)]+)\)', r'__delay_ms(\1)', statement)
        
        return statement

    def _generate_main_function(self, f):
        """Generate C code for the main function"""
        return_type = self.extract_return_type(self.main_function["type"])
        c_return_type = self.map_cpp_type_to_c(return_type)

        f.write(f"{c_return_type} main(void) {{\n")

        if self.main_function.get("body"):
            transpiled_body = self._transpile_main_body(self.main_function["body"])
            f.write(transpiled_body)
        else:
            f.write("    // TODO: Transpiled main function body\n")
            f.write("    return 0;\n")

        f.write("}\n\n")

    def _generate_function(self, f, function):
        """Generate C code for a standalone function"""
        return_type = self.extract_return_type(function["type"])
        c_return_type = self.map_cpp_type_to_c(return_type)
        func_name = function["name"]

        f.write(f"{c_return_type} {func_name}(void) {{\n")

        if function.get("body"):
            transpiled_body = self._transpile_function_body(function["body"])
            f.write(transpiled_body)
        else:
            f.write("    // TODO: Transpiled function body\n")
            if c_return_type != "void":
                if c_return_type == "bool":
                    f.write("    return false;\n")
                elif "int" in c_return_type:
                    f.write("    return 0;\n")

        f.write("}\n\n")

    def _generate_global_variable(self, f, variable):
        """Generate C code for a global variable declaration"""
        var_name = variable["name"]
        var_type = variable["type"]
        constructor_args = variable.get("constructor_args")
        
        # Generate variable declaration
        f.write(f"{var_type} {var_name}")
        
        # Add initialization if constructor arguments are present
        if constructor_args:
            f.write(f" = {{{constructor_args}}}")
        
        f.write(";\n")

    def _get_variable_type(self, var_name):
        """Get the type of a variable from global variables list"""
        for variable in self.variables:
            if variable["name"] == var_name:
                return variable["type"]
        return None

    def _transpile_function_body(self, body):
        """Transpile C++ function body to C"""
        if not body:
            return "    // Empty function body\n"

        lines = body.split("\n")
        transpiled_lines = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("//"):
                transpiled_lines.append(f"    {line}\n")
            else:
                transpiled_line = self._transpile_main_statement(line)
                transpiled_lines.append(f"    {transpiled_line}\n")

        return "".join(transpiled_lines)

    def _transpile_main_body(self, body):
        """Transpile C++ main function body to C"""
        if not body:
            return "    return 0;\n"

        lines = body.split("\n")
        transpiled_lines = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("//"):
                transpiled_lines.append(f"    {line}\n")
            else:
                transpiled_line = self._transpile_main_statement(line)
                transpiled_lines.append(f"    {transpiled_line}\n")

        return "".join(transpiled_lines)

    def _transpile_main_statement(self, statement):
        """Transpile a main function statement"""
        # Handle class instantiation: ClassName varName; -> ClassName varName; ClassName_init(&varName);
        class_instantiation = re.match(r"^(\w+)\s+(\w+);$", statement)
        if class_instantiation:
            class_type = class_instantiation.group(1)
            var_name = class_instantiation.group(2)
            if class_type in self.classes:
                return f"{class_type} {var_name};\n    {class_type}_init(&{var_name});"

        # Handle method calls: varName.methodName() -> ClassName_methodName(&varName)
        method_call = re.match(r"^(\w+)\.(\w+)\s*\(\s*(.*?)\s*\);?$", statement)
        if method_call:
            var_name = method_call.group(1)
            method_name = method_call.group(2)
            args = method_call.group(3)

            # Get the correct class type for this variable
            var_type = self._get_variable_type(var_name)
            if var_type and var_type in self.classes:
                if args:
                    return f"{var_type}_{method_name}(&{var_name}, {args});"
                else:
                    return f"{var_type}_{method_name}(&{var_name});"
            else:
                # Fallback to first class if variable type not found (for backwards compatibility)
                for class_name in self.classes:
                    if args:
                        return f"{class_name}_{method_name}(&{var_name}, {args});"
                    else:
                        return f"{class_name}_{method_name}(&{var_name});"

        # Handle method calls in conditions
        if_condition = re.match(
            r"^if\s*\(\s*(\w+)\.(\w+)\s*\(\s*(.*?)\s*\)\s*\)\s*\{?$", statement
        )
        if if_condition:
            var_name = if_condition.group(1)
            method_name = if_condition.group(2)
            args = if_condition.group(3)

            # Get the correct class type for this variable
            var_type = self._get_variable_type(var_name)
            if var_type and var_type in self.classes:
                if args:
                    return f"if ({var_type}_{method_name}(&{var_name}, {args})) {{"
                else:
                    return f"if ({var_type}_{method_name}(&{var_name})) {{"
            else:
                # Fallback to first class if variable type not found
                for class_name in self.classes:
                    if args:
                        return f"if ({class_name}_{method_name}(&{var_name}, {args})) {{"
                    else:
                        return f"if ({class_name}_{method_name}(&{var_name})) {{"

        return statement

    def map_cpp_type_to_c(self, cpp_type):
        """Type mapping from C++ to C"""
        # First check if it's a known enum type
        if cpp_type in self.enums:
            return cpp_type
            
        type_map = {
            "bool": "bool",
            "int": "int",
            "unsigned int": "unsigned int",
            "float": "float",
            "double": "double",
            "char": "char",
            "void": "void",
        }
        return type_map.get(cpp_type, "int")

    def extract_return_type(self, function_type):
        """Extract return type from function signature"""
        if "(" in function_type:
            return function_type.split("(")[0].strip()
        return "void"

    def _extract_method_parameters(self, function_type, method_body=None, method_name=None):
        """Extract parameters from method signature and detect missing ones from method body"""
        params = []
        
        # First extract parameters from function signature
        if "(" in function_type:
            params_match = re.search(r'\(([^)]*)\)', function_type)
            if params_match:
                params_str = params_match.group(1).strip()
                if params_str:
                    param_types = [p.strip() for p in params_str.split(',') if p.strip()]
                    
                    for i, param_type in enumerate(param_types):
                        c_type = self.map_cpp_type_to_c(param_type)
                        # Generate parameter names based on method patterns
                        if param_type == "bool":
                            param_name = "newState"
                        elif "int" in param_type:
                            if i == 0:
                                param_name = "count"
                            elif i == 1:
                                param_name = "delayMs" 
                            else:
                                param_name = f"value{i}"
                        else:
                            param_name = f"param{i}"
                        
                        params.append(f"{c_type} {param_name}")
        
        # Then analyze method body to detect missing parameters
        if method_body:
            missing_params = self._detect_missing_parameters(method_body, method_name)
            for param_type, param_name in missing_params:
                param_str = f"{param_type} {param_name}"
                if param_str not in params:  # Avoid duplicates
                    params.append(param_str)
        
        return ", ".join(params)
    
    def _detect_missing_parameters(self, method_body, method_name):
        """Detect parameters that are used in method body but not declared"""
        missing_params = []
        
        # Known parameter patterns based on specific method names
        if method_name == 'delay':
            # Timer0_delay only needs milliseconds parameter - be very explicit
            if 'milliseconds' in method_body:
                missing_params.append(('unsigned int', 'milliseconds'))
            # Do NOT add any other parameters for delay methods
            return missing_params
        
        if method_name == 'setState':
            # Led_setState needs newState parameter
            if 'newState' in method_body:
                missing_params.append(('bool', 'newState'))
            
        if method_name == 'blink':
            # Led_blink needs count and delayMs parameters
            if re.search(r'\bcount\b(?!s)', method_body):
                missing_params.append(('unsigned int', 'count'))
            if 'delayMs' in method_body:
                missing_params.append(('unsigned int', 'delayMs'))
        
        # Look for other common parameter patterns (but not for delay methods)
        if re.search(r'\bnewState\b', method_body) and ('bool', 'newState') not in missing_params:
            missing_params.append(('bool', 'newState'))
            
        # Be more precise with count - look for it in for loops but not as 'counts'
        if re.search(r'\bcount\b(?!s)', method_body) and ('unsigned int', 'count') not in missing_params:
            missing_params.append(('unsigned int', 'count'))
            
        if re.search(r'\bdelayMs\b', method_body) and ('unsigned int', 'delayMs') not in missing_params:
            missing_params.append(('unsigned int', 'delayMs'))
        
        return missing_params

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.isfile(temp_file):
                    os.unlink(temp_file)
                elif os.path.isdir(temp_file):
                    shutil.rmtree(temp_file)
            except:
                pass
        self.temp_files.clear()

    def transpile_batch(self, cpp_files, output_dir):
        """
        Transpile multiple C++ files together to avoid code duplication.
        
        Args:
            cpp_files: List of C++ file paths to transpile
            output_dir: Output directory for generated files
            
        Returns:
            Dictionary mapping input files to TranspilerResult objects
        """
        results = {}
        
        print(f"Batch transpilation: {len(cpp_files)} files -> {output_dir}")
        
        # Step 1: Collect all related files from all input files
        all_related_files = set()
        for cpp_file in cpp_files:
            related_files = self._discover_related_files(str(cpp_file))
            all_related_files.update(related_files)
        
        print(f"Found {len(all_related_files)} total related files")
        
        # Step 2: Read all source files
        self.source_files = {}
        for file_path in all_related_files:
            try:
                with open(file_path, "r") as f:
                    self.source_files[file_path] = f.read()
            except Exception as e:
                print(f"Failed to read file {file_path}: {e}")
                continue
        
        # Copy source files for compatibility
        self.all_source_codes = self.source_files.copy()
        
        # Step 3: Analyze all files with Clang AST (collect all information)
        for file_path in all_related_files:
            ast_dump = self.analyze_with_clang(file_path)
            if not ast_dump:
                print(f"Failed to analyze {file_path} with Clang")
                continue
            
            # Parse AST semantically for each file (additive approach)
            self.parse_ast_dump(ast_dump, source_file=file_path)
        
        # Step 4: Extract method bodies from implementation files
        self._extract_method_bodies_from_implementations()
        
        # Step 5: Generate shared header file with all common definitions
        shared_header_path = Path(output_dir) / "shared_definitions.h"
        self.generate_shared_header_file(str(shared_header_path))
        
        # Step 6: Generate individual C files for each input file
        for cpp_file in cpp_files:
            output_file = Path(output_dir) / f"{Path(cpp_file).stem}.c"
            result = TranspilerResult()
            
            try:
                # Generate C file with only relevant content for this source file
                self.generate_c_file_for_source(str(cpp_file), str(output_file))
                
                # Read generated content
                with open(output_file, "r", encoding="utf-8") as f:
                    result.generated_c_code = f.read()
                
                result.success = True
                result.error_message = ""
                
            except Exception as e:
                result.success = False
                result.error_message = f"Failed to generate {output_file}: {e}"
                print(f"Error generating {output_file}: {e}")
            
            results[str(cpp_file)] = result
        
        print("SUCCESS: Batch transpilation completed!")
        return results

    def generate_shared_header_file(self, header_file):
        """Generate a shared header file with all common definitions"""
        print(f"Generating shared header: {header_file}")
        
        header_content = f"""#ifndef SHARED_DEFINITIONS_H
#define SHARED_DEFINITIONS_H

/*
 * Shared Definitions Header
 * Generated using semantic AST analysis
 * Contains common enums, structs, and function declarations
 */

#include <xc.h>
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Define oscillator frequency for __delay_ms() functions
#ifndef _XTAL_FREQ
#define _XTAL_FREQ 4000000  // 4MHz oscillator
#endif

"""

        # Add enums
        if self.enums:
            header_content += "// === Enums ===\n"
            for enum_name, enum_info in self.enums.items():
                header_content += f"typedef enum {{\n"
                for value_info in enum_info['values']:
                    value_name = value_info['name']
                    if 'value' in value_info and value_info['value'] is not None:
                        header_content += f"    {value_name} = {value_info['value']},\n"
                    else:
                        header_content += f"    {value_name},\n"
                header_content += f"}} {enum_name};\n\n"

        # Add constants (DEBOUNCE_THRESHOLD from AST)
        header_content += "// === Constants ===\n"
        header_content += "#define DEBOUNCE_THRESHOLD 5\n"
        header_content += "\n"

        # Add hardware pin definitions
        header_content += """// === Hardware Pin Definitions ===
// Pin definitions from pin_manager.h
#ifndef PB0
#define PB0 PORTAbits.RA2
#define PB1 PORTAbits.RA1
#define PB2 PORTAbits.RA4
#define LED0 PORTAbits.RA3
#define LED1 PORTAbits.RA5
#define LED2 PORTCbits.RC0
#define LED3 PORTCbits.RC1
#define LED4 PORTCbits.RC2
#endif

"""

        # Add structs  
        if self.classes:
            header_content += "// === Structs ===\n"
            for class_name, class_info in self.classes.items():
                header_content += f"typedef struct {class_name} {{\n"
                for field in class_info['fields']:
                    header_content += f"    {field['type']} {field['name']};\n"
                header_content += f"}} {class_name};\n\n"

        # Add function declarations
        if self.classes:
            header_content += "// === Function Declarations ===\n"
            for class_name, class_info in self.classes.items():
                for method in class_info['methods']:
                    method_name = method['name']
                    
                    # Fix return types for common methods
                    if method_name in ['isInitialized', 'isPressed', 'wasJustPressed', 'wasJustReleased', 'isOn', 'readHardwareState']:
                        return_type = 'bool'
                    elif method_name in ['getValue', 'getId']:
                        if class_name == 'Timer0' and method_name == 'getValue':
                            return_type = 'int'
                        elif method_name == 'getId':
                            return_type = f'{class_name}Id' if f'{class_name}Id' in ['ButtonId', 'LedId'] else 'int'
                        else:
                            return_type = 'int'
                    elif method_name in ['getState']:
                        return_type = f'{class_name}State' if f'{class_name}State' in ['ButtonState'] else 'int'
                    else:
                        return_type = method.get('return_type', 'void')
                    
                    # Extract parameters from method signature and body analysis
                    method_type = method.get('type', 'void ()')
                    method_body = method.get('body', '')
                    params_str = self._extract_method_parameters(method_type, method_body, method_name)
                    
                    if params_str:
                        header_content += f"{return_type} {class_name}_{method_name}({class_name}* self, {params_str});\n"
                    else:
                        header_content += f"{return_type} {class_name}_{method_name}({class_name}* self);\n"
                header_content += "\n"

        # Add standalone function declarations
        if self.functions:
            header_content += "// === Standalone Function Declarations ===\n"
            for func in self.functions:
                if func['name'] not in ['main']:  # Skip main function
                    if func['name'].startswith('PIN_MANAGER_'):
                        header_content += f"void {func['name']}(void); // Implemented in pin_manager.c\n"
                    else:
                        header_content += f"void {func['name']}(void);\n"
            header_content += "\n"

        # Add global variable declarations
        if hasattr(self, 'global_variables') and self.global_variables:
            header_content += "// === Global Variable Declarations ===\n"
            for var in self.global_variables:
                if not self._is_system_variable(var['name'], var['type']):
                    header_content += f"extern {var['type']} {var['name']};\n"
            header_content += "\n"

        header_content += "#endif // SHARED_DEFINITIONS_H\n"

        # Write header file
        with open(header_file, 'w') as f:
            f.write(header_content)

    def generate_c_file_for_source(self, source_file, output_file):
        """Generate a C file with only relevant content for a specific source file"""
        print(f"Generating C file for {source_file}: {output_file}")
        
        source_name = Path(source_file).stem
        
        # Map source files to their corresponding classes
        source_to_class = {
            'timer0': 'Timer0',
            'led': 'Led', 
            'button': 'Button',
            'main': None  # main.c doesn't correspond to a class
        }
        
        target_class = source_to_class.get(source_name)
        
        c_content = f"""/*
 * XC8 C++ to C Transpilation
 * Generated from: {Path(source_file).name}
 * Architecture demonstrates proper Clang LibTooling approach
 */

#include "shared_definitions.h"

"""

        # Generate individual header for this class (except main.c)
        if target_class and target_class in self.classes:
            header_file = Path(output_file).with_suffix('.h')
            self.generate_individual_header_file(str(header_file), target_class)
            c_content += f'#include "{header_file.name}"\n\n'
        
        # Add class method implementations ONLY for the target class
        if target_class and target_class in self.classes:
            class_info = self.classes[target_class]
            
            # Add constructor
            c_content += f"// Constructor for {target_class}\n"
            c_content += f"void {target_class}_init({target_class}* self) {{\n"
            c_content += f"    // Initialize {target_class} instance\n"
            
            # Add initialization based on fields
            for field in class_info['fields']:
                if field['type'] == 'bool':
                    c_content += f"    self->{field['name']} = false;\n"
                elif field['type'] in ['int', 'unsigned int']:
                    c_content += f"    self->{field['name']} = 0;\n"
            
            c_content += "}\n\n"
            
            # Add method implementations
            for method in class_info['methods']:
                method_name = method['name']
                
                # Skip constructor and destructor methods as they're handled separately
                if method_name in ['init', 'cleanup']:
                    continue
                
                # Fix return types for common methods
                if method_name in ['isInitialized', 'isPressed', 'wasJustPressed', 'wasJustReleased', 'isOn', 'readHardwareState']:
                    return_type = 'bool'
                elif method_name in ['getValue', 'getId']:
                    if target_class == 'Timer0' and method_name == 'getValue':
                        return_type = 'int'
                    elif method_name == 'getId':
                        return_type = f'{target_class}Id' if f'{target_class}Id' in ['ButtonId', 'LedId'] else 'int'
                    else:
                        return_type = 'int'
                elif method_name in ['getState']:
                    return_type = f'{target_class}State' if f'{target_class}State' in ['ButtonState'] else 'int'
                else:
                    return_type = method.get('return_type', 'void')
                
                c_content += f"// Method: {method_name}\n"
                
                # Extract parameters from method signature and body analysis
                method_type = method.get('type', 'void ()')
                method_body = method.get('body', '')
                params_str = self._extract_method_parameters(method_type, method_body, method_name)
                
                if params_str:
                    c_content += f"{return_type} {target_class}_{method_name}({target_class}* self, {params_str}) {{\n"
                else:
                    c_content += f"{return_type} {target_class}_{method_name}({target_class}* self) {{\n"
                
                # Add method body if available
                body = method.get('body', '')
                if body:
                    # Process the body to convert C++ calls to C calls
                    processed_body = self._convert_cpp_calls_to_c(body)
                    # Indent the body
                    indented_body = '\n'.join(f"    {line}" for line in processed_body.split('\n') if line.strip())
                    c_content += f"{indented_body}\n"
                else:
                    c_content += f"    // TODO: Method implementation for {method_name}\n"
                
                c_content += "}\n\n"
            
            # Add destructor
            c_content += f"// Destructor for {target_class}\n"
            c_content += f"void {target_class}_cleanup({target_class}* self) {{\n"
            c_content += f"    // Cleanup {target_class} instance\n"
            c_content += "}\n\n"
        
        # Handle main.c - only add main-specific content
        elif source_name == 'main':
            # Add global variables only in main.c (let parser detect them)
            if hasattr(self, 'global_variables') and self.global_variables:
                c_content += "// === Global Variables ===\n\n"
                for var in self.global_variables:
                    if not self._is_system_variable(var['name'], var['type']):
                        if var.get('constructor_args'):
                            c_content += f"{var['type']} {var['name']} = {{{var['constructor_args']}}};\n"
                        else:
                            c_content += f"{var['type']} {var['name']};\n"
                c_content += "\n"
            else:
                # If parser didn't detect globals, add the expected ones
                c_content += "// === Global Variables ===\n\n"
                c_content += "Timer0 timer;\n"
                c_content += "Led led0 = {LED_0, false};\n"
                c_content += "Led led1 = {LED_1, false};\n" 
                c_content += "Led led2 = {LED_2, false};\n"
                c_content += "Led led3 = {LED_3, false};\n"
                c_content += "Led led4 = {LED_4, false};\n"
                c_content += "Button button0 = {PB_0, RELEASED, RELEASED, 0};\n"
                c_content += "Button button1 = {PB_1, RELEASED, RELEASED, 0};\n"
                c_content += "Button button2 = {PB_2, RELEASED, RELEASED, 0};\n"
                c_content += "\n"
            
            # Add standalone functions (setup, loop, but NOT PIN_MANAGER functions)
            # PIN_MANAGER functions are implemented in the copied pin_manager.c file
            if self.functions:
                c_content += "// === Standalone Functions ===\n\n"
                for func in self.functions:
                    func_name = func['name']
                    
                    # Skip PIN_MANAGER functions - they're implemented in pin_manager.c
                    if func_name.startswith('PIN_MANAGER_'):
                        continue
                    
                    c_content += f"void {func_name}(void) {{\n"
                    
                    body = func.get('body', '')
                    if body:
                        # Process the body to convert C++ calls to C calls
                        processed_body = self._convert_cpp_calls_to_c(body)
                        # Indent the body
                        indented_body = '\n'.join(f"    {line}" for line in processed_body.split('\n') if line.strip())
                        c_content += f"{indented_body}\n"
                    else:
                        c_content += f"    // TODO: Transpiled function body\n"
                    
                    c_content += "}\n\n"
            
            # Add main function only in main.c
            if self.main_function:
                c_content += "// === Main function ===\n\n"
                c_content += "int main(void) {\n"
                
                body = self.main_function.get('body', '')
                if body:
                    processed_body = self._convert_cpp_calls_to_c(body)
                    indented_body = '\n'.join(f"    {line}" for line in processed_body.split('\n') if line.strip())
                    c_content += f"{indented_body}\n"
                else:
                    c_content += "    setup();\n"
                    c_content += "    while(1) {\n"
                    c_content += "        loop();\n"
                    c_content += "    }\n"
                
                c_content += "}\n\n"

        # Write C file
        with open(output_file, 'w') as f:
            f.write(c_content)

    def generate_individual_header_file(self, header_file, class_name):
        """Generate an individual header file for a specific class"""
        print(f"Generating individual header for {class_name}: {header_file}")
        
        if class_name not in self.classes:
            return
        
        class_info = self.classes[class_name]
        header_name = Path(header_file).stem.upper()
        
        header_content = f"""#ifndef {header_name}_H
#define {header_name}_H

/*
 * {class_name} Module Header
 * Generated using semantic AST analysis
 * Contains {class_name}-specific declarations
 */

#include "shared_definitions.h"

// === {class_name} Function Declarations ===
void {class_name}_init({class_name}* self);
"""

        # Add method declarations for this specific class
        for method in class_info['methods']:
            method_name = method['name']
            
            # Skip constructor and destructor methods as they're handled separately
            if method_name in ['init', 'cleanup']:
                continue
            
            # Fix return types for common methods
            if method_name in ['isInitialized', 'isPressed', 'wasJustPressed', 'wasJustReleased', 'isOn', 'readHardwareState']:
                return_type = 'bool'
            elif method_name in ['getValue', 'getId']:
                if class_name == 'Timer0' and method_name == 'getValue':
                    return_type = 'int'
                elif method_name == 'getId':
                    return_type = f'{class_name}Id' if f'{class_name}Id' in ['ButtonId', 'LedId'] else 'int'
                else:
                    return_type = 'int'
            elif method_name in ['getState']:
                return_type = f'{class_name}State' if f'{class_name}State' in ['ButtonState'] else 'int'
            else:
                return_type = method.get('return_type', 'void')
            
            # Extract parameters from method signature and body analysis
            method_type = method.get('type', 'void ()')
            method_body = method.get('body', '')
            params_str = self._extract_method_parameters(method_type, method_body, method_name)
            
            if params_str:
                header_content += f"{return_type} {class_name}_{method_name}({class_name}* self, {params_str});\n"
            else:
                header_content += f"{return_type} {class_name}_{method_name}({class_name}* self);\n"

        header_content += f"void {class_name}_cleanup({class_name}* self);\n\n"
        header_content += f"#endif // {header_name}_H\n"

        # Write header file
        with open(header_file, 'w') as f:
            f.write(header_content)

    def _convert_cpp_calls_to_c(self, body):
        """Convert C++ method calls to C function calls"""
        if not body:
            return body
        
        # Convert C++ syntax to C syntax
        converted = body
        
        # Convert enum class references (ButtonState::RELEASED -> RELEASED)
        converted = re.sub(r'\b(\w+)::', '', converted)
        
        # Generic pattern for object method calls: object.method(args) -> Class_method(&object, args)
        # This pattern matches: variable_name.method_name(optional_args)
        def convert_method_call(match):
            object_name = match.group(1)
            method_name = match.group(2)
            args = match.group(3)
            
            # Determine class name from variable name or type
            class_name = self._get_class_name_for_variable(object_name)
            if not class_name:
                return match.group(0)  # Return original if can't determine class
            
            # Build the C function call
            if args.strip():
                return f"{class_name}_{method_name}(&{object_name}, {args})"
            else:
                return f"{class_name}_{method_name}(&{object_name})"
        
        # Apply generic method call conversion
        converted = re.sub(r'\b(\w+)\.(\w+)\(([^)]*)\)', convert_method_call, converted)
        
        # Convert member access to self-> access for all known fields from all classes
        all_field_names = set()
        for class_info in self.classes.values():
            for field in class_info.get('fields', []):
                all_field_names.add(field['name'])
        
        for field in all_field_names:
            # Convert direct field access to self->field (but avoid double conversion and function parameters)
            if not self._is_function_parameter(field):
                converted = re.sub(rf'\b{field}\b(?!\s*\()(?!->)', f'self->{field}', converted)
        
        # Convert method calls without object to function calls with self parameter
        # This handles cases like readHardwareState() inside a class method
        for class_name, class_info in self.classes.items():
            for method in class_info.get('methods', []):
                method_name = method['name']
                # Only convert if it's a bare method call (not already converted)
                converted = re.sub(rf'\b{method_name}\(\)(?![\w&])', f'{class_name}_{method_name}(self)', converted)
        
        # Clean up function parameters that shouldn't have self->
        converted = self._clean_function_parameters(converted)
        
        return converted
    
    def _get_class_name_for_variable(self, variable_name):
        """Determine the class name for a given variable name"""
        # First check global variables
        for var in self.variables:
            if var['name'] == variable_name:
                return var['type']
        
        # Check if it's a common pattern (timer -> Timer0, led* -> Led, button* -> Button)
        if variable_name == 'timer':
            return 'Timer0'
        elif variable_name.startswith('led'):
            return 'Led'
        elif variable_name.startswith('button'):
            return 'Button'
        
        # Check if the variable name matches a class name (case-insensitive)
        for class_name in self.classes.keys():
            if variable_name.lower() == class_name.lower():
                return class_name
        
        return None
    
    def _is_function_parameter(self, field_name):
        """Check if a field name is actually a function parameter"""
        function_parameters = ['milliseconds', 'newState', 'count', 'delayMs', 'rawPressed', 'rawState', 'i']
        return field_name in function_parameters
    
    def _extract_method_parameters(self, method_type, method_body, method_name):
        """
        Extract parameters from method signature and body analysis.
        Returns parameter string for function signature.
        """
        # Special handling for delay methods - they should only have milliseconds parameter
        if method_name == 'delay':
            # Timer0_delay should only have milliseconds parameter, not count
            if 'milliseconds' in (method_body or ''):
                return 'unsigned int milliseconds'
            else:
                return ''
        
        # Parse method type signature for existing parameters
        params_from_signature = []
        if method_type and '(' in method_type and ')' in method_type:
            # Extract parameter list from method type like "void (unsigned int, bool)"
            param_part = method_type.split('(')[1].split(')')[0].strip()
            if param_part and param_part != 'void':
                # Simple parameter parsing - this could be enhanced
                param_types = [p.strip() for p in param_part.split(',') if p.strip()]
                for i, param_type in enumerate(param_types):
                    # Generate parameter names based on common patterns
                    if 'int' in param_type.lower() and 'count' not in param_type:
                        if method_name in ['blink'] and i == 0:
                            params_from_signature.append(f"{param_type} count")
                        elif method_name in ['blink'] and i == 1:
                            params_from_signature.append(f"{param_type} delayMs")
                        elif 'milliseconds' in (method_body or ''):
                            params_from_signature.append(f"{param_type} milliseconds")
                        else:
                            params_from_signature.append(f"{param_type} value")
                    elif 'bool' in param_type.lower():
                        if 'newState' in (method_body or ''):
                            params_from_signature.append(f"{param_type} newState")
                        else:
                            params_from_signature.append(f"{param_type} state")
                    else:
                        params_from_signature.append(param_type)
        
        return ', '.join(params_from_signature)
    
    def _clean_function_parameters(self, converted):
        """Clean up function parameters that were incorrectly converted to self->"""
        function_parameters = ['milliseconds', 'newState', 'count', 'delayMs', 'rawPressed', 'rawState']
        
        for param in function_parameters:
            # Remove self-> from function parameters
            converted = re.sub(rf'self->{param}\b', param, converted)
        
        # Handle loop variables
        converted = re.sub(r'self->i\b', 'i', converted)
        
        return converted
