#!/bin/bash
# Quick Start Script for IBAMR Scalar Transport Validation
#
# This script automates the complete validation workflow:
# 1. Build the test suite
# 2. Run all tests
# 3. Analyze results
# 4. Generate report

set -e  # Exit on error

echo "======================================================================="
echo "IBAMR SCALAR TRANSPORT VALIDATION - QUICK START"
echo "======================================================================="
echo ""

# Configuration
IBAMR_ROOT=${IBAMR_ROOT:-"../IBAMR-0.18.0"}
BUILD_DIR="build"
RESULTS_DIR="results"
MPI_NP=${MPI_NP:-4}
BUILD_JOBS=${BUILD_JOBS:-$(nproc)}

# Check if IBAMR_ROOT exists
if [ ! -d "$IBAMR_ROOT" ]; then
    echo "ERROR: IBAMR_ROOT directory not found: $IBAMR_ROOT"
    echo "Please set IBAMR_ROOT environment variable or edit this script."
    exit 1
fi

echo "Configuration:"
echo "  IBAMR_ROOT:  $IBAMR_ROOT"
echo "  BUILD_DIR:   $BUILD_DIR"
echo "  RESULTS_DIR: $RESULTS_DIR"
echo "  MPI_NP:      $MPI_NP"
echo "  BUILD_JOBS:  $BUILD_JOBS"
echo ""

# Step 1: Build
echo "======================================================================="
echo "STEP 1: Building Test Suite"
echo "======================================================================="
echo ""

if [ ! -d "$BUILD_DIR" ]; then
    mkdir -p "$BUILD_DIR"
fi

cd "$BUILD_DIR"

echo "Running CMake..."
cmake .. \
    -DIBAMR_ROOT="$IBAMR_ROOT" \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_ALL_TESTS=ON

echo ""
echo "Compiling tests..."
make -j"$BUILD_JOBS"

echo ""
echo "✓ Build complete!"
echo ""

cd ..

# Step 2: Run Tests
echo "======================================================================="
echo "STEP 2: Running All Tests"
echo "======================================================================="
echo ""

python3 run_all_tests.py \
    --build-dir "$BUILD_DIR" \
    --results-dir "$RESULTS_DIR" \
    --mpi-np "$MPI_NP" \
    --clean

echo ""
echo "✓ Test execution complete!"
echo ""

# Step 3: Analyze
echo "======================================================================="
echo "STEP 3: Analyzing Results"
echo "======================================================================="
echo ""

python3 analyze_results.py \
    --results-dir "$RESULTS_DIR" \
    --report-output "Compatibility_Report.md"

echo ""
echo "✓ Analysis complete!"
echo ""

# Summary
echo "======================================================================="
echo "VALIDATION COMPLETE!"
echo "======================================================================="
echo ""
echo "Results saved to: $RESULTS_DIR/"
echo "Report saved to:  Compatibility_Report.md"
echo ""
echo "To view the report:"
echo "  cat Compatibility_Report.md"
echo ""
echo "To convert to PDF (requires pandoc):"
echo "  pandoc Compatibility_Report.md -o Compatibility_Report.pdf"
echo ""
