"""
Native C++ transpiler backend using LLVM LibTooling
This module provides Python bindings to the C++ XC8 transpiler implementation.
"""

import ctypes
import ctypes.util
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import platform


# Try to find the shared library
def _find_transpiler_library():
    """Find the XC8 transpiler shared library"""

    # Library name based on platform
    if platform.system() == "Windows":
        lib_name = "xc8transpiler_capi.dll"
    elif platform.system() == "Darwin":
        lib_name = "libxc8transpiler_capi.dylib"
    else:
        lib_name = "libxc8transpiler_capi.so"

    # Search paths
    search_paths = [
        # Development build directories
        Path(__file__).parent.parent.parent / "build" / "lib",
        Path(__file__).parent.parent.parent / "build_libtooling" / "lib",
        Path(__file__).parent.parent.parent / "lib",
        # System directories
        Path("/usr/local/lib"),
        Path("/usr/lib"),
        # Current directory
        Path("."),
    ]

    # Add LD_LIBRARY_PATH directories on Unix
    if platform.system() != "Windows":
        ld_library_path = os.environ.get("LD_LIBRARY_PATH", "")
        for path_str in ld_library_path.split(":"):
            if path_str:
                search_paths.append(Path(path_str))

    # Search for the library
    for search_path in search_paths:
        lib_path = search_path / lib_name
        if lib_path.exists():
            return str(lib_path)

    # Try using ctypes.util.find_library as fallback
    lib_path = ctypes.util.find_library("xc8transpiler_capi")
    if lib_path:
        return lib_path

    raise RuntimeError(
        f"Could not find {lib_name}. Please build the C++ transpiler first."
    )


# Load the library
try:
    _lib_path = _find_transpiler_library()
    _lib = ctypes.CDLL(_lib_path)
except Exception as e:
    _lib = None
    _lib_error = str(e)


# Define C structures
class CTranspilerConfig(ctypes.Structure):
    _fields_ = [
        ("enable_optimization", ctypes.c_bool),
        ("generate_xc8_pragmas", ctypes.c_bool),
        ("preserve_comments", ctypes.c_bool),
        ("target_device", ctypes.c_char_p),
        ("include_paths", ctypes.POINTER(ctypes.c_char_p)),
        ("include_paths_count", ctypes.c_size_t),
        ("defines", ctypes.POINTER(ctypes.c_char_p)),
        ("defines_count", ctypes.c_size_t),
    ]


class CTranspilerResult(ctypes.Structure):
    _fields_ = [
        ("success", ctypes.c_bool),
        ("error_message", ctypes.c_char_p),
        ("generated_c_code", ctypes.c_char_p),
        ("generated_header_code", ctypes.c_char_p),
        ("warnings", ctypes.POINTER(ctypes.c_char_p)),
        ("warnings_count", ctypes.c_size_t),
    ]


# Define function signatures if library is available
if _lib:
    # xc8_transpiler_create
    _lib.xc8_transpiler_create.argtypes = [ctypes.POINTER(CTranspilerConfig)]
    _lib.xc8_transpiler_create.restype = ctypes.c_void_p

    # xc8_transpiler_destroy
    _lib.xc8_transpiler_destroy.argtypes = [ctypes.c_void_p]
    _lib.xc8_transpiler_destroy.restype = None

    # xc8_transpiler_transpile_string
    _lib.xc8_transpiler_transpile_string.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(CTranspilerResult),
    ]
    _lib.xc8_transpiler_transpile_string.restype = ctypes.c_int

    # xc8_transpiler_transpile_file
    _lib.xc8_transpiler_transpile_file.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(CTranspilerResult),
    ]
    _lib.xc8_transpiler_transpile_file.restype = ctypes.c_int

    # xc8_transpiler_result_free
    _lib.xc8_transpiler_result_free.argtypes = [ctypes.POINTER(CTranspilerResult)]
    _lib.xc8_transpiler_result_free.restype = None

    # xc8_transpiler_version
    _lib.xc8_transpiler_version.argtypes = []
    _lib.xc8_transpiler_version.restype = ctypes.c_char_p

    # xc8_transpiler_check_llvm
    _lib.xc8_transpiler_check_llvm.argtypes = []
    _lib.xc8_transpiler_check_llvm.restype = ctypes.c_bool


class TranspilerConfig:
    """Configuration for the XC8 transpiler"""

    def __init__(
        self,
        enable_optimization: bool = True,
        generate_xc8_pragmas: bool = True,
        preserve_comments: bool = True,
        target_device: str = "PIC16F876A",
        include_paths: Optional[List[str]] = None,
        defines: Optional[List[str]] = None,
    ):
        self.enable_optimization = enable_optimization
        self.generate_xc8_pragmas = generate_xc8_pragmas
        self.preserve_comments = preserve_comments
        self.target_device = target_device
        self.include_paths = include_paths or []
        self.defines = defines or []


class TranspilerResult:
    """Result of a transpilation operation"""

    def __init__(self):
        self.success = False
        self.error_message = ""
        self.generated_c_code = ""
        self.generated_header_code = ""
        self.warnings = []


class NativeTranspiler:
    """Native C++ transpiler using LLVM LibTooling"""

    def __init__(self, config: Optional[TranspilerConfig] = None):
        if _lib is None:
            raise RuntimeError(f"Native transpiler library not available: {_lib_error}")

        self.config = config or TranspilerConfig()
        self._transpiler_handle = None
        self._create_transpiler()

    def _create_transpiler(self):
        """Create the native transpiler instance"""
        # Convert Python config to C config
        c_config = CTranspilerConfig()
        c_config.enable_optimization = self.config.enable_optimization
        c_config.generate_xc8_pragmas = self.config.generate_xc8_pragmas
        c_config.preserve_comments = self.config.preserve_comments
        c_config.target_device = self.config.target_device.encode("utf-8")

        # Convert include paths
        if self.config.include_paths:
            include_paths_array = (ctypes.c_char_p * len(self.config.include_paths))()
            for i, path in enumerate(self.config.include_paths):
                include_paths_array[i] = path.encode("utf-8")
            c_config.include_paths = include_paths_array
            c_config.include_paths_count = len(self.config.include_paths)
        else:
            c_config.include_paths = None
            c_config.include_paths_count = 0

        # Convert defines
        if self.config.defines:
            defines_array = (ctypes.c_char_p * len(self.config.defines))()
            for i, define in enumerate(self.config.defines):
                defines_array[i] = define.encode("utf-8")
            c_config.defines = defines_array
            c_config.defines_count = len(self.config.defines)
        else:
            c_config.defines = None
            c_config.defines_count = 0

        # Create transpiler
        self._transpiler_handle = _lib.xc8_transpiler_create(ctypes.byref(c_config))
        if not self._transpiler_handle:
            raise RuntimeError("Failed to create native transpiler instance")

    def __del__(self):
        """Destructor to clean up native resources"""
        if hasattr(self, "_transpiler_handle") and self._transpiler_handle:
            _lib.xc8_transpiler_destroy(self._transpiler_handle)

    def transpile_string(
        self, cpp_source: str, filename: str = "input.cpp"
    ) -> TranspilerResult:
        """Transpile C++ source code from string"""
        if not self._transpiler_handle:
            raise RuntimeError("Transpiler instance not available")

        # Prepare C result structure
        c_result = CTranspilerResult()

        # Call native function
        status = _lib.xc8_transpiler_transpile_string(
            self._transpiler_handle,
            cpp_source.encode("utf-8"),
            filename.encode("utf-8"),
            ctypes.byref(c_result),
        )

        # Convert C result to Python result
        result = TranspilerResult()
        result.success = c_result.success

        if c_result.error_message:
            result.error_message = c_result.error_message.decode("utf-8")

        if c_result.generated_c_code:
            result.generated_c_code = c_result.generated_c_code.decode("utf-8")

        if c_result.generated_header_code:
            result.generated_header_code = c_result.generated_header_code.decode(
                "utf-8"
            )

        # Convert warnings
        if c_result.warnings and c_result.warnings_count > 0:
            for i in range(c_result.warnings_count):
                if c_result.warnings[i]:
                    result.warnings.append(c_result.warnings[i].decode("utf-8"))

        # Free C result memory
        _lib.xc8_transpiler_result_free(ctypes.byref(c_result))

        return result

    def transpile_file(
        self, input_file: str, output_file: Optional[str] = None
    ) -> TranspilerResult:
        """Transpile C++ source code from file"""
        if not self._transpiler_handle:
            raise RuntimeError("Transpiler instance not available")

        # Prepare C result structure
        c_result = CTranspilerResult()

        # Prepare output file parameter
        output_file_c = output_file.encode("utf-8") if output_file else None

        # Call native function
        status = _lib.xc8_transpiler_transpile_file(
            self._transpiler_handle,
            input_file.encode("utf-8"),
            output_file_c,
            ctypes.byref(c_result),
        )

        # Convert C result to Python result
        result = TranspilerResult()
        result.success = c_result.success

        if c_result.error_message:
            result.error_message = c_result.error_message.decode("utf-8")

        if c_result.generated_c_code:
            result.generated_c_code = c_result.generated_c_code.decode("utf-8")

        if c_result.generated_header_code:
            result.generated_header_code = c_result.generated_header_code.decode(
                "utf-8"
            )

        # Convert warnings
        if c_result.warnings and c_result.warnings_count > 0:
            for i in range(c_result.warnings_count):
                if c_result.warnings[i]:
                    result.warnings.append(c_result.warnings[i].decode("utf-8"))

        # Free C result memory
        _lib.xc8_transpiler_result_free(ctypes.byref(c_result))

        return result


def get_version() -> str:
    """Get the version of the native transpiler"""
    if _lib is None:
        return "Native transpiler not available"

    version_bytes = _lib.xc8_transpiler_version()
    return version_bytes.decode("utf-8")


def check_llvm() -> bool:
    """Check if LLVM/Clang is available"""
    if _lib is None:
        return False

    return _lib.xc8_transpiler_check_llvm()


def is_available() -> bool:
    """Check if the native transpiler is available"""
    return _lib is not None
