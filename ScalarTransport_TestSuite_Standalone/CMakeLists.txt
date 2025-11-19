# Standalone CMakeLists.txt for IBAMR C++ Test Suite
# Verification & Validation tests for scalar transport
# Extracted from IBAMR-0.18.0 examples

cmake_minimum_required(VERSION 3.12)
project(IBAMR_Scalar_Transport_Tests_Standalone VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Options for selective test building
option(BUILD_ALL_TESTS "Build all tests (1-17)" ON)
option(BUILD_TIER1_ONLY "Build only Tier 1 tests (1-6)" OFF)
option(BUILD_TIER2_ONLY "Build only Tier 2 tests (7-10)" OFF)
option(BUILD_TIER3_ONLY "Build only Tier 3 tests (11-14)" OFF)
option(BUILD_LITERATURE_ONLY "Build only Literature Validation tests (15-17)" OFF)

# ============================================================================
# Find IBAMR Installation
# ============================================================================

# Set IBAMR_ROOT - user can override via -DIBAMR_ROOT or environment variable
if(NOT DEFINED IBAMR_ROOT)
    if(DEFINED ENV{IBAMR_ROOT})
        set(IBAMR_ROOT $ENV{IBAMR_ROOT})
    else()
        # Default to the IBAMR-0.18.0 in parent directories
        set(IBAMR_ROOT "${CMAKE_SOURCE_DIR}/../IBAMR-0.18.0")
    endif()
endif()

message(STATUS "Looking for IBAMR in: ${IBAMR_ROOT}")

# Verify IBAMR_ROOT exists
if(NOT EXISTS "${IBAMR_ROOT}")
    message(FATAL_ERROR
        "IBAMR_ROOT directory does not exist: ${IBAMR_ROOT}\n"
        "Please set IBAMR_ROOT to your IBAMR installation directory:\n"
        "  cmake -DIBAMR_ROOT=/path/to/ibamr ..\n"
        "or set the environment variable:\n"
        "  export IBAMR_ROOT=/path/to/ibamr")
endif()

# ============================================================================
# Find Required Packages
# ============================================================================

# Find MPI (required)
find_package(MPI REQUIRED)

# Try to find packages via CMake, but make them optional
# as IBAMR might be built without CMake config files
find_package(PETSc QUIET)
find_package(SAMRAI QUIET)

# ============================================================================
# Manual Configuration for IBAMR/SAMRAI/PETSc if needed
# ============================================================================

# Set up include directories
set(IBAMR_INCLUDE_DIRS
    ${IBAMR_ROOT}/include
    ${IBAMR_ROOT}/src
    ${IBAMR_ROOT}/ibtk/include
    ${IBAMR_ROOT}/ibtk/src
)

# For builds where IBAMR was built, check common locations
if(EXISTS "${IBAMR_ROOT}/lib")
    set(IBAMR_LIB_DIR ${IBAMR_ROOT}/lib)
elseif(EXISTS "${IBAMR_ROOT}/build/lib")
    set(IBAMR_LIB_DIR ${IBAMR_ROOT}/build/lib)
else()
    message(WARNING "Could not find IBAMR lib directory. Linking may fail.")
endif()

# Common include directories for numerical libraries
include_directories(
    ${CMAKE_SOURCE_DIR}/common/include
    ${IBAMR_INCLUDE_DIRS}
    ${MPI_CXX_INCLUDE_DIRS}
)

# If PETSc was found via CMake, use it
if(PETSc_FOUND)
    include_directories(${PETSC_INCLUDE_DIRS})
endif()

# If SAMRAI was found via CMake, use it
if(SAMRAI_FOUND)
    include_directories(${SAMRAI_INCLUDE_DIRS})
endif()

# ============================================================================
# Build Common Utilities Library
# ============================================================================

add_subdirectory(common)

# ============================================================================
# Macro to add a test executable
# ============================================================================

macro(add_ibamr_test TEST_NAME TEST_DIR)
    # Create executable
    add_executable(${TEST_NAME} ${TEST_DIR}/main.cpp)

    # Link with common utilities
    target_link_libraries(${TEST_NAME} PRIVATE test_utilities)

    # Link with MPI (always required)
    target_link_libraries(${TEST_NAME} PRIVATE MPI::MPI_CXX)

    # Link with IBAMR libraries if found
    if(EXISTS "${IBAMR_LIB_DIR}")
        target_link_directories(${TEST_NAME} PRIVATE ${IBAMR_LIB_DIR})
        # Note: Library names may vary depending on build configuration
        # Users may need to adjust these for their specific IBAMR build
        target_link_libraries(${TEST_NAME} PRIVATE
            -lIBAMR2d
            -lIBTK2d
        )
    endif()

    # Link with PETSc if found
    if(PETSc_FOUND)
        target_link_libraries(${TEST_NAME} PRIVATE PETSc::PETSc)
    endif()

    # Link with SAMRAI if found
    if(SAMRAI_FOUND)
        target_link_libraries(${TEST_NAME} PRIVATE SAMRAI::SAMRAI)
    endif()

    # Set RPATH for runtime library finding
    set_target_properties(${TEST_NAME} PROPERTIES
        INSTALL_RPATH "${IBAMR_LIB_DIR}"
        BUILD_WITH_INSTALL_RPATH FALSE
        INSTALL_RPATH_USE_LINK_PATH TRUE
    )

    # Add test to CTest
    add_test(NAME ${TEST_NAME}
             COMMAND ${TEST_NAME} ${TEST_DIR}/input2d
             WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/${TEST_DIR})
endmacro()

# ============================================================================
# Define Test Categories
# ============================================================================

set(TIER1_TESTS
    test01_smoke
    test02_diffusion
    test03_advection
    test04_mms
    test05_discontinuous
    test06_mass_conservation
)

set(TIER2_TESTS
    test07_bcs
    test08_sphere_source
    test09_high_sc
    test10_moving_ib
)

set(TIER3_TESTS
    test11_amr
    test12_timestep
    test13_long_run
    test14_benchmarks
)

set(LITERATURE_VALIDATION_TESTS
    test15_rotating_cylinder
    test16_3d_sphere
    test17_pitch_plunge
)

# ============================================================================
# Select which tests to build
# ============================================================================

if(BUILD_TIER1_ONLY)
    set(TESTS_TO_BUILD ${TIER1_TESTS})
    message(STATUS "Building TIER 1 tests only")
elseif(BUILD_TIER2_ONLY)
    set(TESTS_TO_BUILD ${TIER2_TESTS})
    message(STATUS "Building TIER 2 tests only")
elseif(BUILD_TIER3_ONLY)
    set(TESTS_TO_BUILD ${TIER3_TESTS})
    message(STATUS "Building TIER 3 tests only")
elseif(BUILD_LITERATURE_ONLY)
    set(TESTS_TO_BUILD ${LITERATURE_VALIDATION_TESTS})
    message(STATUS "Building Literature Validation tests only")
elseif(BUILD_ALL_TESTS)
    set(TESTS_TO_BUILD ${TIER1_TESTS} ${TIER2_TESTS} ${TIER3_TESTS} ${LITERATURE_VALIDATION_TESTS})
    message(STATUS "Building ALL tests")
else()
    set(TESTS_TO_BUILD ${TIER1_TESTS})
    message(STATUS "Building TIER 1 tests by default")
endif()

# ============================================================================
# Add test executables
# ============================================================================

foreach(TEST ${TESTS_TO_BUILD})
    # Map test name to directory
    if(TEST STREQUAL "test01_smoke")
        add_ibamr_test(${TEST} Test01_SmokeTest)
    elseif(TEST STREQUAL "test02_diffusion")
        add_ibamr_test(${TEST} Test02_Diffusion_Analytic)
    elseif(TEST STREQUAL "test03_advection")
        add_ibamr_test(${TEST} Test03_Advection_Analytic)
    elseif(TEST STREQUAL "test04_mms")
        add_ibamr_test(${TEST} Test04_MMS)
    elseif(TEST STREQUAL "test05_discontinuous")
        add_ibamr_test(${TEST} Test05_Discontinuous)
    elseif(TEST STREQUAL "test06_mass_conservation")
        add_ibamr_test(${TEST} Test06_MassConservation)
    elseif(TEST STREQUAL "test07_bcs")
        add_ibamr_test(${TEST} Test07_BCs)
    elseif(TEST STREQUAL "test08_sphere_source")
        add_ibamr_test(${TEST} Test08_SphereSource)
    elseif(TEST STREQUAL "test09_high_sc")
        add_ibamr_test(${TEST} Test09_HighSc)
    elseif(TEST STREQUAL "test10_moving_ib")
        add_ibamr_test(${TEST} Test10_MovingIB)
    elseif(TEST STREQUAL "test11_amr")
        add_ibamr_test(${TEST} Test11_AMR)
    elseif(TEST STREQUAL "test12_timestep")
        add_ibamr_test(${TEST} Test12_TimeStep)
    elseif(TEST STREQUAL "test13_long_run")
        add_ibamr_test(${TEST} Test13_LongRun)
    elseif(TEST STREQUAL "test14_benchmarks")
        add_ibamr_test(${TEST} Test14_Benchmarks)
    elseif(TEST STREQUAL "test15_rotating_cylinder")
        add_ibamr_test(${TEST} Test15_RotatingCylinder)
    elseif(TEST STREQUAL "test16_3d_sphere")
        add_ibamr_test(${TEST} Test16_3DSphere)
    elseif(TEST STREQUAL "test17_pitch_plunge")
        add_ibamr_test(${TEST} Test17_PitchPlunge)
    endif()
endforeach()

# ============================================================================
# Enable CTest
# ============================================================================

enable_testing()

# ============================================================================
# Print Configuration Summary
# ============================================================================

message(STATUS "========================================================")
message(STATUS "IBAMR Scalar Transport Test Suite - STANDALONE BUILD")
message(STATUS "========================================================")
message(STATUS "Build Type:      ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard:    ${CMAKE_CXX_STANDARD}")
message(STATUS "C++ Compiler:    ${CMAKE_CXX_COMPILER}")
message(STATUS "")
message(STATUS "IBAMR Configuration:")
message(STATUS "  IBAMR Root:    ${IBAMR_ROOT}")
message(STATUS "  Include Dirs:  ${IBAMR_INCLUDE_DIRS}")
if(EXISTS "${IBAMR_LIB_DIR}")
    message(STATUS "  Library Dir:   ${IBAMR_LIB_DIR}")
endif()
message(STATUS "")
message(STATUS "Dependencies:")
message(STATUS "  MPI:           ${MPI_CXX_FOUND}")
message(STATUS "  PETSc:         ${PETSc_FOUND}")
message(STATUS "  SAMRAI:        ${SAMRAI_FOUND}")
message(STATUS "")
message(STATUS "Tests to build (${CMAKE_CURRENT_LIST_LINE}):")
foreach(TEST ${TESTS_TO_BUILD})
    message(STATUS "  ✓ ${TEST}")
endforeach()
message(STATUS "========================================================")
message(STATUS "")
message(STATUS "To build:    make -j4")
message(STATUS "To test:     ctest")
message(STATUS "========================================================")
