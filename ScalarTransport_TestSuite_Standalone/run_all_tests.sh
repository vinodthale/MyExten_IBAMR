#!/bin/bash

################################################################################
# run_all_tests.sh
#
# Standalone Test Runner for IBAMR Scalar Transport Test Suite
#
# This script:
#   1. Configures and builds all tests using CMake
#   2. Runs each test executable
#   3. Captures output to test_results/
#   4. Generates a PASS/FAIL summary
#
# Usage:
#   ./run_all_tests.sh [options]
#
# Options:
#   --tier1          Build and run only Tier 1 tests (1-6)
#   --tier2          Build and run only Tier 2 tests (7-10)
#   --tier3          Build and run only Tier 3 tests (11-14)
#   --literature     Build and run only Literature tests (15-17)
#   --all            Build and run all tests (default)
#   --rebuild        Force clean rebuild
#   --help           Show this help message
#
# Environment Variables:
#   IBAMR_ROOT       Path to IBAMR installation (required if not in ../IBAMR-0.18.0)
#   BUILD_DIR        Build directory (default: build)
#   NUM_PROCS        Number of MPI processes for parallel tests (default: 1)
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default settings
BUILD_DIR="${BUILD_DIR:-build}"
NUM_PROCS="${NUM_PROCS:-1}"
RESULTS_DIR="test_results"
CMAKE_OPTIONS=""
REBUILD=0
TEST_MODE="all"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

################################################################################
# Parse command line arguments
################################################################################

while [[ $# -gt 0 ]]; do
    case $1 in
        --tier1)
            CMAKE_OPTIONS="-DBUILD_TIER1_ONLY=ON"
            TEST_MODE="tier1"
            shift
            ;;
        --tier2)
            CMAKE_OPTIONS="-DBUILD_TIER2_ONLY=ON"
            TEST_MODE="tier2"
            shift
            ;;
        --tier3)
            CMAKE_OPTIONS="-DBUILD_TIER3_ONLY=ON"
            TEST_MODE="tier3"
            shift
            ;;
        --literature)
            CMAKE_OPTIONS="-DBUILD_LITERATURE_ONLY=ON"
            TEST_MODE="literature"
            shift
            ;;
        --all)
            CMAKE_OPTIONS="-DBUILD_ALL_TESTS=ON"
            TEST_MODE="all"
            shift
            ;;
        --rebuild)
            REBUILD=1
            shift
            ;;
        --help)
            head -n 30 "$0" | grep "^#" | sed 's/^# //g' | sed 's/^#//g'
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

################################################################################
# Print banner
################################################################################

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}  IBAMR Scalar Transport Test Suite${NC}"
echo -e "${BLUE}  Standalone Test Runner${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""
echo -e "Test Mode:       ${GREEN}${TEST_MODE}${NC}"
echo -e "Build Directory: ${BUILD_DIR}"
echo -e "Results Directory: ${RESULTS_DIR}"
echo -e "MPI Processes:   ${NUM_PROCS}"
echo ""

################################################################################
# Check IBAMR_ROOT
################################################################################

if [[ -z "$IBAMR_ROOT" ]]; then
    # Try default location
    DEFAULT_IBAMR="../IBAMR-0.18.0"
    if [[ -d "$DEFAULT_IBAMR" ]]; then
        export IBAMR_ROOT="$(cd "$DEFAULT_IBAMR" && pwd)"
        echo -e "${YELLOW}IBAMR_ROOT not set, using default: ${IBAMR_ROOT}${NC}"
    else
        echo -e "${RED}ERROR: IBAMR_ROOT not set and default location not found${NC}"
        echo "Please set IBAMR_ROOT to your IBAMR installation:"
        echo "  export IBAMR_ROOT=/path/to/ibamr"
        exit 1
    fi
else
    echo -e "IBAMR_ROOT:      ${IBAMR_ROOT}"
fi

if [[ ! -d "$IBAMR_ROOT" ]]; then
    echo -e "${RED}ERROR: IBAMR_ROOT directory does not exist: ${IBAMR_ROOT}${NC}"
    exit 1
fi

echo ""

################################################################################
# Setup build directory
################################################################################

if [[ $REBUILD -eq 1 ]] && [[ -d "$BUILD_DIR" ]]; then
    echo -e "${YELLOW}Cleaning build directory...${NC}"
    rm -rf "$BUILD_DIR"
fi

mkdir -p "$BUILD_DIR"
mkdir -p "$RESULTS_DIR"

################################################################################
# Configure with CMake
################################################################################

echo -e "${BLUE}Configuring tests with CMake...${NC}"
cd "$BUILD_DIR"

cmake .. \
    -DIBAMR_ROOT="$IBAMR_ROOT" \
    -DCMAKE_BUILD_TYPE=Release \
    $CMAKE_OPTIONS

if [[ $? -ne 0 ]]; then
    echo -e "${RED}CMake configuration failed!${NC}"
    exit 1
fi

echo ""

################################################################################
# Build tests
################################################################################

echo -e "${BLUE}Building tests...${NC}"

# Determine number of cores for parallel build
if command -v nproc &> /dev/null; then
    NCORES=$(nproc)
elif command -v sysctl &> /dev/null; then
    NCORES=$(sysctl -n hw.ncpu)
else
    NCORES=4
fi

make -j${NCORES}

if [[ $? -ne 0 ]]; then
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Build completed successfully!${NC}"
echo ""

################################################################################
# Discover test executables
################################################################################

echo -e "${BLUE}Discovering test executables...${NC}"

# Find all test executables
TEST_EXECUTABLES=($(find . -maxdepth 1 -type f -executable -name "test*" | sort))

if [[ ${#TEST_EXECUTABLES[@]} -eq 0 ]]; then
    echo -e "${RED}No test executables found!${NC}"
    exit 1
fi

echo -e "Found ${#TEST_EXECUTABLES[@]} test(s)"
echo ""

################################################################################
# Run tests
################################################################################

cd "$SCRIPT_DIR"

PASSED=0
FAILED=0
SKIPPED=0
declare -a FAILED_TESTS
declare -a PASSED_TESTS

echo -e "${BLUE}Running tests...${NC}"
echo -e "${BLUE}======================================================${NC}"

for TEST_EXEC in "${TEST_EXECUTABLES[@]}"; do
    # Extract test name (remove ./ prefix)
    TEST_NAME=$(basename "$TEST_EXEC")

    # Map test name to directory
    case "$TEST_NAME" in
        test01_smoke) TEST_DIR="Test01_SmokeTest" ;;
        test02_diffusion) TEST_DIR="Test02_Diffusion_Analytic" ;;
        test03_advection) TEST_DIR="Test03_Advection_Analytic" ;;
        test04_mms) TEST_DIR="Test04_MMS" ;;
        test05_discontinuous) TEST_DIR="Test05_Discontinuous" ;;
        test06_mass_conservation) TEST_DIR="Test06_MassConservation" ;;
        test07_bcs) TEST_DIR="Test07_BCs" ;;
        test08_sphere_source) TEST_DIR="Test08_SphereSource" ;;
        test09_high_sc) TEST_DIR="Test09_HighSc" ;;
        test10_moving_ib) TEST_DIR="Test10_MovingIB" ;;
        test11_amr) TEST_DIR="Test11_AMR" ;;
        test12_timestep) TEST_DIR="Test12_TimeStep" ;;
        test13_long_run) TEST_DIR="Test13_LongRun" ;;
        test14_benchmarks) TEST_DIR="Test14_Benchmarks" ;;
        test15_rotating_cylinder) TEST_DIR="Test15_RotatingCylinder" ;;
        test16_3d_sphere) TEST_DIR="Test16_3DSphere" ;;
        test17_pitch_plunge) TEST_DIR="Test17_PitchPlunge" ;;
        *)
            echo -e "${YELLOW}Unknown test: $TEST_NAME, skipping...${NC}"
            SKIPPED=$((SKIPPED + 1))
            continue
            ;;
    esac

    # Check if test directory and input file exist
    if [[ ! -d "$TEST_DIR" ]]; then
        echo -e "${YELLOW}Test directory not found: $TEST_DIR, skipping...${NC}"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    INPUT_FILE="$TEST_DIR/input2d"
    if [[ ! -f "$INPUT_FILE" ]]; then
        echo -e "${YELLOW}Input file not found: $INPUT_FILE, skipping...${NC}"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    echo ""
    echo -e "${BLUE}Running: ${TEST_NAME}${NC}"
    echo -e "  Directory: ${TEST_DIR}"
    echo -e "  Input:     ${INPUT_FILE}"

    # Create output directory
    OUTPUT_DIR="$RESULTS_DIR/$TEST_NAME"
    mkdir -p "$OUTPUT_DIR"

    # Run test
    cd "$TEST_DIR"

    # Copy input file to output directory
    cp input2d "../$OUTPUT_DIR/"

    # Run the test executable
    START_TIME=$(date +%s)

    if [[ $NUM_PROCS -gt 1 ]]; then
        mpirun -np $NUM_PROCS "../$BUILD_DIR/$TEST_NAME" input2d \
            > "../$OUTPUT_DIR/stdout.log" 2> "../$OUTPUT_DIR/stderr.log"
        TEST_EXIT_CODE=$?
    else
        "../$BUILD_DIR/$TEST_NAME" input2d \
            > "../$OUTPUT_DIR/stdout.log" 2> "../$OUTPUT_DIR/stderr.log"
        TEST_EXIT_CODE=$?
    fi

    END_TIME=$(date +%s)
    ELAPSED=$((END_TIME - START_TIME))

    cd "$SCRIPT_DIR"

    # Check result
    if [[ $TEST_EXIT_CODE -eq 0 ]]; then
        echo -e "  ${GREEN}✓ PASS${NC} (${ELAPSED}s)"
        PASSED=$((PASSED + 1))
        PASSED_TESTS+=("$TEST_NAME")
        echo "PASS" > "$OUTPUT_DIR/result.txt"
    else
        echo -e "  ${RED}✗ FAIL${NC} (exit code: $TEST_EXIT_CODE, ${ELAPSED}s)"
        FAILED=$((FAILED + 1))
        FAILED_TESTS+=("$TEST_NAME")
        echo "FAIL (exit code: $TEST_EXIT_CODE)" > "$OUTPUT_DIR/result.txt"
    fi

    echo "$ELAPSED" > "$OUTPUT_DIR/runtime.txt"
done

################################################################################
# Print Summary
################################################################################

echo ""
echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""
echo -e "Total Tests:  ${#TEST_EXECUTABLES[@]}"
echo -e "${GREEN}Passed:       ${PASSED}${NC}"
echo -e "${RED}Failed:       ${FAILED}${NC}"
if [[ $SKIPPED -gt 0 ]]; then
    echo -e "${YELLOW}Skipped:      ${SKIPPED}${NC}"
fi
echo ""

if [[ $PASSED -gt 0 ]]; then
    echo -e "${GREEN}Passed tests:${NC}"
    for TEST in "${PASSED_TESTS[@]}"; do
        echo -e "  ${GREEN}✓${NC} $TEST"
    done
    echo ""
fi

if [[ $FAILED -gt 0 ]]; then
    echo -e "${RED}Failed tests:${NC}"
    for TEST in "${FAILED_TESTS[@]}"; do
        echo -e "  ${RED}✗${NC} $TEST"
        echo -e "    Output: $RESULTS_DIR/$TEST/"
    done
    echo ""
fi

echo -e "Results saved to: ${RESULTS_DIR}/"
echo -e "${BLUE}======================================================${NC}"

# Write summary file
SUMMARY_FILE="$RESULTS_DIR/summary.txt"
{
    echo "IBAMR Scalar Transport Test Suite - Test Summary"
    echo "================================================"
    echo ""
    echo "Run Date: $(date)"
    echo "Test Mode: $TEST_MODE"
    echo "IBAMR_ROOT: $IBAMR_ROOT"
    echo ""
    echo "Total Tests:  ${#TEST_EXECUTABLES[@]}"
    echo "Passed:       $PASSED"
    echo "Failed:       $FAILED"
    echo "Skipped:      $SKIPPED"
    echo ""

    if [[ $PASSED -gt 0 ]]; then
        echo "Passed Tests:"
        for TEST in "${PASSED_TESTS[@]}"; do
            echo "  ✓ $TEST"
        done
        echo ""
    fi

    if [[ $FAILED -gt 0 ]]; then
        echo "Failed Tests:"
        for TEST in "${FAILED_TESTS[@]}"; do
            echo "  ✗ $TEST"
        done
        echo ""
    fi
} > "$SUMMARY_FILE"

echo -e "Summary written to: ${SUMMARY_FILE}"
echo ""

# Exit with error if any tests failed
if [[ $FAILED -gt 0 ]]; then
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
