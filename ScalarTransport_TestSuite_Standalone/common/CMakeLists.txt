# CMakeLists.txt for common test utilities
# Standalone version - works without CMake config files

cmake_minimum_required(VERSION 3.12)

# Create library for common utilities
add_library(test_utilities STATIC
    src/AnalyticalSolutions.cpp
    src/ErrorCalculator.cpp
    src/TestUtilities.cpp
)

# Set include directories
target_include_directories(test_utilities
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
        ${IBAMR_INCLUDE_DIRS}
)

# Link with MPI (required)
target_link_libraries(test_utilities PUBLIC MPI::MPI_CXX)

# Note: IBAMR and SAMRAI libraries will be linked at the test executable level
# This avoids issues with CMake target dependencies
