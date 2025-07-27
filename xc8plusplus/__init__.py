"""
xc8plusplus - C++ to C transpiler for Microchip XC8 compiler.

This package provides tools for transpiling C++ code to C code compatible
with the XC8 compiler for 8-bit PIC microcontrollers.
"""

__version__ = "0.1.0"
__author__ = "Sébastien Celles"
__email__ = "s.celles@gmail.com"

from .transpiler import XC8Transpiler
from .cli import main

__all__ = ["XC8Transpiler", "main"]
