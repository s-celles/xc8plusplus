"""
XC8++ Transpilers Package

This package contains different transpiler backends for converting C++ code to C
for use with the Microchip XC8 compiler.

Available transpilers:
- Native transpiler: LLVM LibTooling-based transpiler (C++)
- Python transpiler: Fallback transpiler using Clang AST dumps
"""

from .unified_transpiler import XC8Transpiler
from .python_backend import PythonTranspiler, TranspilerResult

try:
    from .native_backend import (
        NativeTranspiler,
        TranspilerConfig,
        get_version,
        check_llvm,
    )

    __all__ = [
        "XC8Transpiler",
        "TranspilerResult",
        "NativeTranspiler",
        "TranspilerConfig",
        "PythonTranspiler",
        "get_version",
        "check_llvm",
    ]
except ImportError:
    __all__ = ["XC8Transpiler", "TranspilerResult", "PythonTranspiler"]
