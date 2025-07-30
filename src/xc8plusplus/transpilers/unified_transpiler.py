"""
XC8++ Unified Transpiler

This module provides a unified interface for transpiler backends that convert 
C++ code to C for XC8 compatibility. Users can explicitly choose between 
native (LLVM LibTooling) and python (Clang AST) backends.
"""

import warnings
from pathlib import Path
from typing import Dict, List, Optional, Union

# Import transpiler backends
try:
    from .native_backend import (
        NativeTranspiler,
        TranspilerConfig,
        get_version,
        check_llvm,
    )

    NATIVE_AVAILABLE = True
except ImportError:
    NATIVE_AVAILABLE = False

from .python_backend import PythonTranspiler, TranspilerResult


class XC8Transpiler:
    """
    XC8 C++ to C transpiler with both native (LLVM LibTooling) and Python backends.

    Available backends:
    1. Native C++ backend using LLVM LibTooling (default)
    2. Python backend using Clang AST dumps
    
    Users must explicitly specify which backend to use via the 'backend' parameter.
    """

    def __init__(
        self,
        backend: str = "native",
        enable_optimization: bool = True,
        generate_xc8_pragmas: bool = True,
        preserve_comments: bool = True,
        target_device: str = "PIC16F876A",
        include_paths: Optional[List[str]] = None,
        defines: Optional[List[str]] = None,
    ):
        """
        Initialize the XC8 transpiler.

        Args:
            backend: Backend to use ('native' or 'python')
            enable_optimization: Enable XC8-specific optimizations
            generate_xc8_pragmas: Generate XC8 configuration pragmas
            preserve_comments: Preserve comments in generated code
            target_device: Target PIC device name
            include_paths: Additional include directories
            defines: Preprocessor definitions
        """
        # Validate backend selection
        if backend not in ["native", "python"]:
            raise ValueError(
                f"Invalid backend '{backend}'. Must be 'native' or 'python'"
            )

        # Check if requested backend is available
        if backend == "native" and not NATIVE_AVAILABLE:
            raise RuntimeError(
                f"Native backend requested but not available. Please build the native transpiler or use --backend python"
            )

        self.backend = backend

        # Configuration
        self.enable_optimization = enable_optimization
        self.generate_xc8_pragmas = generate_xc8_pragmas
        self.preserve_comments = preserve_comments
        self.target_device = target_device
        self.include_paths = include_paths or []
        self.defines = defines or []

        # Backend instances
        self._native_transpiler = None
        self._python_transpiler = None

        # Initialize the requested backend
        self._initialize_backend()

    def _initialize_backend(self):
        """Initialize the requested transpiler backend"""
        if self.backend == "native":
            config = TranspilerConfig(
                enable_optimization=self.enable_optimization,
                generate_xc8_pragmas=self.generate_xc8_pragmas,
                preserve_comments=self.preserve_comments,
                target_device=self.target_device,
                include_paths=self.include_paths,
                defines=self.defines,
            )
            self._native_transpiler = NativeTranspiler(config)
            print("🚀 Using native C++ transpiler with LLVM LibTooling")

        elif self.backend == "python":
            self._python_transpiler = PythonTranspiler(
                enable_optimization=self.enable_optimization,
                generate_xc8_pragmas=self.generate_xc8_pragmas,
                preserve_comments=self.preserve_comments,
                target_device=self.target_device,
                include_paths=self.include_paths,
                defines=self.defines,
            )
            print("Using Python backend with Clang AST analysis")

    def get_backend_info(self) -> Dict[str, Union[str, bool]]:
        """Get information about the active backend"""
        if self.backend == "native":
            return {
                "backend": "native",
                "description": "C++ backend using LLVM LibTooling",
                "version": get_version(),
                "llvm_available": check_llvm(),
                "features": [
                    "semantic_analysis",
                    "type_safety",
                    "optimization",
                    "full_ast",
                ],
            }
        else:
            return {
                "backend": "python",
                "description": "Python backend using Clang AST dumps",
                "version": "1.0.0",
                "llvm_available": False,
                "features": ["ast_parsing", "basic_transpilation"],
            }

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
        if self.backend == "native":
            return self._transpile_string_native(cpp_source, filename)
        else:
            return self._python_transpiler.transpile_string(cpp_source, filename)

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
        if self.backend == "native":
            return self._transpile_file_native(input_file, output_file)
        else:
            return self._python_transpiler.transpile_file(input_file, output_file)

    def transpile_batch(self, cpp_files, output_dir):
        """
        Transpile multiple C++ files together to avoid code duplication.
        
        Args:
            cpp_files: List of C++ file paths to transpile
            output_dir: Output directory for generated files
            
        Returns:
            Dictionary mapping input files to TranspilerResult objects
        """
        if self.backend == "native":
            # For now, native backend falls back to individual transpilation
            # This could be enhanced to support batch processing
            results = {}
            for cpp_file in cpp_files:
                output_file = Path(output_dir) / f"{Path(cpp_file).stem}.c"
                result = self.transpile_file(str(cpp_file), str(output_file))
                results[str(cpp_file)] = result
            return results
        else:
            return self._python_transpiler.transpile_batch(cpp_files, output_dir)

    def _transpile_string_native(
        self, cpp_source: str, filename: str
    ) -> TranspilerResult:
        """Transpile using native C++ backend"""
        try:
            native_result = self._native_transpiler.transpile_string(
                cpp_source, filename
            )

            # Convert native result to our result format
            result = TranspilerResult()
            result.success = native_result.success
            result.error_message = native_result.error_message
            result.generated_c_code = native_result.generated_c_code
            result.generated_header_code = native_result.generated_header_code
            result.warnings = native_result.warnings

            return result

        except Exception as e:
            result = TranspilerResult()
            result.success = False
            result.error_message = f"Native transpiler error: {str(e)}"
            return result

    def _transpile_file_native(
        self, input_file: str, output_file: Optional[str]
    ) -> TranspilerResult:
        """Transpile file using native C++ backend"""
        try:
            native_result = self._native_transpiler.transpile_file(
                input_file, output_file
            )

            # Convert native result to our result format
            result = TranspilerResult()
            result.success = native_result.success
            result.error_message = native_result.error_message
            result.generated_c_code = native_result.generated_c_code
            result.generated_header_code = native_result.generated_header_code
            result.warnings = native_result.warnings

            return result

        except Exception as e:
            result = TranspilerResult()
            result.success = False
            result.error_message = f"Native transpiler error: {str(e)}"
            return result


def get_native_version() -> str:
    """Get the version of the native transpiler backend"""
    if NATIVE_AVAILABLE:
        try:
            return get_version()
        except:
            return "unknown"
    return "not available"


def check_llvm() -> bool:
    """Check if LLVM is available for the native backend"""
    if NATIVE_AVAILABLE:
        try:
            return check_llvm()
        except:
            return False
    return False
