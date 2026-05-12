cmake_minimum_required(VERSION 3.15)
project(devpulse_engine VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and pybind11
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 CONFIG REQUIRED)

# C++ engine shared library
add_library(engine_core STATIC
    src/benchmark.cpp
)

target_include_directories(engine_core PUBLIC include)

# pybind11 Python module
pybind11_add_module(devpulse_engine
    bindings/bindings.cpp
)

target_link_libraries(devpulse_engine PRIVATE engine_core)
target_include_directories(devpulse_engine PRIVATE include)

# Install the module next to the backend
install(TARGETS devpulse_engine
    LIBRARY DESTINATION ${CMAKE_SOURCE_DIR}/../backend/app/engine
)
