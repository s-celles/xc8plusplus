# Professional C++ to C Transpiler using Clang C API
# This is the PROFESSIONAL approach - no more Python soup!

cmake_minimum_required(VERSION 3.16)
project(xc8_professional_transpiler C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Windows-specific LLVM paths for C API
if(WIN32)
    set(LLVM_ROOT "C:/Program Files/LLVM")
    set(LLVM_INCLUDE_DIRS "${LLVM_ROOT}/include")
    set(LLVM_LIBRARY_DIRS "${LLVM_ROOT}/lib")
    
    # Find libclang library
    find_library(LIBCLANG_LIBRARY
        NAMES clang libclang
        PATHS "${LLVM_LIBRARY_DIRS}"
        NO_DEFAULT_PATH
    )
    
    if(NOT LIBCLANG_LIBRARY)
        message(FATAL_ERROR "libclang not found in ${LLVM_LIBRARY_DIRS}")
    endif()
else()
    # For non-Windows systems, try standard package finding
    find_package(LLVM REQUIRED CONFIG)
    find_package(Clang REQUIRED CONFIG)
endif()

# Include directories
include_directories(${LLVM_INCLUDE_DIRS})
if(WIN32)
    link_directories(${LLVM_LIBRARY_DIRS})
endif()

# Professional transpiler executable
add_executable(xc8_transpiler professional_transpiler_c.c)

# Link with Clang C API
if(WIN32)
    target_link_libraries(xc8_transpiler ${LIBCLANG_LIBRARY})
else()
    target_link_libraries(xc8_transpiler clang)
endif()

# Compiler-specific flags
if(MSVC)
    target_compile_options(xc8_transpiler PRIVATE /W3)
else()
    target_compile_options(xc8_transpiler PRIVATE -Wall -Wextra)
endif()

# Installation
install(TARGETS xc8_transpiler
    RUNTIME DESTINATION bin
)

# Print configuration summary
message(STATUS "=== Professional XC8++ Transpiler Configuration ===")
message(STATUS "LLVM Include Dir: ${LLVM_INCLUDE_DIRS}")
if(WIN32)
    message(STATUS "LLVM Library Dir: ${LLVM_LIBRARY_DIRS}")
    message(STATUS "LibClang Library: ${LIBCLANG_LIBRARY}")
endif()
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "===================================================")

# Create test target
add_custom_target(test_transpiler
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/xc8_transpiler 
            ${CMAKE_CURRENT_SOURCE_DIR}/../autotests/00-helloworld/main.cpp
            ${CMAKE_CURRENT_BINARY_DIR}/test_output.c
    DEPENDS xc8_transpiler
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Testing professional transpiler on hello world example"
)
