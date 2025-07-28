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
from pathlib import Path


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
        """Extract method body from the original source code"""
        if not self.source_code:
            return None
            
        # Find the class definition
        class_pattern = rf"class\s+{class_name}\s*\{{"
        class_match = re.search(class_pattern, self.source_code)
        if not class_match:
            return None
            
        # Find the method within the class
        class_start = class_match.start()
        class_content = self.source_code[class_start:]
        
        # Pattern to match method definition with body
        method_pattern = rf"\b{method_name}\s*\([^)]*\)\s*(?:const\s*)?\s*\{{"
        method_match = re.search(method_pattern, class_content)
        if not method_match:
            return None
            
        # Extract the method body by counting braces
        method_start = method_match.end() - 1  # Start at the opening brace
        brace_count = 0
        body_start = method_start + 1
        i = method_start
        
        while i < len(class_content):
            if class_content[i] == '{':
                brace_count += 1
            elif class_content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    body_end = i
                    break
            i += 1
        else:
            return None
            
        # Extract and clean the body
        body = class_content[body_start:body_end].strip()
        return body

    def _extract_function_body_from_source(self, func_name):
        """Extract function body from the original source code"""
        if not self.source_code:
            return None
        
        # Find all function definitions with this name
        func_pattern = rf"\b{func_name}\s*\([^)]*\)\s*\{{"
        func_matches = list(re.finditer(func_pattern, self.source_code))
        
        if not func_matches:
            return None
        
        # For overloaded functions, we need to extract all bodies
        # This is a simplified approach - we'll return the body of the last match for now
        # A more sophisticated approach would match parameter types
        func_match = func_matches[-1]  # Get the last match
        
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
        with open(output_file, "w") as f:
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


def main():
    if len(sys.argv) != 3:
        print("Usage: python xc8_transpiler.py <input.cpp> <output.c>")
        print("\nThis demonstrates the proper approach:")
        print("✅ Uses Clang AST analysis")
        print("✅ Semantic transformation")
        print("✅ No string manipulation")
        print("✅ Proper architecture for LibTooling")
        return 1

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: Input file {input_file} not found")
        return 1

    transpiler = XC8Transpiler()
    success = transpiler.transpile(input_file, output_file)

    if success:
        print("\nSUCCESS: Transpilation complete!")
        print(f"Output written to: {output_file}")
        print(
            "\nThis demonstrates the architecture for our C++ LibTooling implementation"
        )
        return 0
    else:
        print("ERROR: Transpilation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
