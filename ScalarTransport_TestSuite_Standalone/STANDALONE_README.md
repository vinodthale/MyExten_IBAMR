# IBAMR Scalar Transport Test Suite - Standalone Version

This is a **standalone**, independent test suite extracted from IBAMR 0.18.0 examples. It contains comprehensive verification and validation tests for scalar transport in IBAMR.

## Overview

This test suite has been extracted from:
```
IBAMR-0.18.0/examples/vinod/examples/Four_fish_school/IBAMR_CPP_Tests
```

It is now **completely independent** and can be built and run against any IBAMR 0.18.0 installation without modifying the original IBAMR source code.

## Test Categories

The test suite contains **17 tests** organized into 4 tiers:

### Tier 1: Fundamental Tests (1-6)
- **Test01_SmokeTest** - Basic functionality check
- **Test02_Diffusion_Analytic** - Diffusion with analytical validation
- **Test03_Advection_Analytic** - Advection with analytical validation
- **Test04_MMS** - Method of Manufactured Solutions
- **Test05_Discontinuous** - Discontinuous initial conditions
- **Test06_MassConservation** - Mass conservation verification

### Tier 2: Intermediate Tests (7-10)
- **Test07_BCs** - Boundary condition tests
- **Test08_SphereSource** - Point source with sphere
- **Test09_HighSc** - High Schmidt number flows
- **Test10_MovingIB** - Moving immersed boundaries

### Tier 3: Advanced Tests (11-14)
- **Test11_AMR** - Adaptive mesh refinement
- **Test12_TimeStep** - Time-stepping schemes
- **Test13_LongRun** - Long-time integration
- **Test14_Benchmarks** - Performance benchmarks

### Literature Validation Tests (15-17)
- **Test15_RotatingCylinder** - Rotating cylinder (literature comparison)
- **Test16_3DSphere** - 3D sphere test
- **Test17_PitchPlunge** - Pitching and plunging motion

## Directory Structure

```
ScalarTransport_TestSuite_Standalone/
├── CMakeLists.txt              # Main CMake build configuration
├── run_all_tests.sh            # Automated test runner script
├── STANDALONE_README.md        # This file
├── README.md                   # Original test suite documentation
├── BUILD_STATUS.md             # Build and test status
├── FINAL_REPORT.md             # Final validation report
├── QUICK_START.md              # Quick start guide
├── common/                     # Shared utilities
│   ├── CMakeLists.txt
│   ├── include/                # Common headers
│   │   ├── AnalyticalSolutions.h
│   │   ├── ErrorCalculator.h
│   │   └── TestUtilities.h
│   └── src/                    # Common implementations
│       ├── AnalyticalSolutions.cpp
│       ├── ErrorCalculator.cpp
│       └── TestUtilities.cpp
├── Test01_SmokeTest/           # Individual test directories
│   ├── main.cpp
│   ├── input2d
│   └── README.md
├── Test02_Diffusion_Analytic/
│   └── ...
├── ...
└── Test17_PitchPlunge/
```

## Prerequisites

### Required:
- **IBAMR 0.18.0** - Built and installed
- **CMake** ≥ 3.12
- **C++ Compiler** with C++14 support (g++, clang++)
- **MPI** (OpenMPI, MPICH, or equivalent)
- **PETSc** (same version used to build IBAMR)
- **SAMRAI** (included with IBAMR)

### Optional:
- **HDF5** (for visualization output)
- **Silo** (for visualization output)

## Build Instructions

### Step 1: Set IBAMR_ROOT

Point to your IBAMR installation:

```bash
export IBAMR_ROOT=/path/to/IBAMR-0.18.0
```

If IBAMR is located at `../IBAMR-0.18.0` relative to this directory, the build system will find it automatically.

### Step 2: Create Build Directory

```bash
mkdir build
cd build
```

### Step 3: Configure with CMake

#### Build all tests (default):
```bash
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT
```

#### Build only specific test tiers:
```bash
# Only Tier 1 tests (1-6)
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT -DBUILD_TIER1_ONLY=ON

# Only Tier 2 tests (7-10)
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT -DBUILD_TIER2_ONLY=ON

# Only Tier 3 tests (11-14)
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT -DBUILD_TIER3_ONLY=ON

# Only Literature Validation tests (15-17)
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT -DBUILD_LITERATURE_ONLY=ON
```

### Step 4: Build

```bash
make -j4  # Use 4 cores for parallel build
```

### Step 5: Verify Build

You should see executables like:
```
test01_smoke
test02_diffusion
test03_advection
...
```

## Running Tests

### Manual Execution

Each test can be run individually:

```bash
# From the test's directory
cd ../Test01_SmokeTest
../build/test01_smoke input2d

# Or from the build directory
cd build
./test01_smoke ../Test01_SmokeTest/input2d
```

For parallel execution with MPI:
```bash
mpirun -np 4 ../build/test01_smoke input2d
```

### Automated Test Runner

The easiest way to run all tests:

```bash
./run_all_tests.sh
```

This script will:
1. Configure and build all tests
2. Run each test executable
3. Capture output to `test_results/`
4. Generate a PASS/FAIL summary

#### Options:
```bash
# Run only Tier 1 tests
./run_all_tests.sh --tier1

# Run only Tier 2 tests
./run_all_tests.sh --tier2

# Run only Tier 3 tests
./run_all_tests.sh --tier3

# Run only Literature Validation tests
./run_all_tests.sh --literature

# Run all tests (default)
./run_all_tests.sh --all

# Force clean rebuild
./run_all_tests.sh --rebuild

# Run with MPI (set NUM_PROCS)
NUM_PROCS=4 ./run_all_tests.sh
```

### Using CTest

If you prefer CTest:

```bash
cd build
ctest -j4  # Run tests in parallel with 4 cores
ctest -V   # Verbose output
```

## Test Results

After running `run_all_tests.sh`, results are saved to:

```
test_results/
├── summary.txt                 # Overall summary
├── test01_smoke/
│   ├── stdout.log             # Standard output
│   ├── stderr.log             # Error output
│   ├── result.txt             # PASS or FAIL
│   ├── runtime.txt            # Execution time
│   └── input2d                # Copy of input file
├── test02_diffusion/
│   └── ...
└── ...
```

## Troubleshooting

### CMake can't find IBAMR

**Solution:** Set `IBAMR_ROOT` explicitly:
```bash
cmake .. -DIBAMR_ROOT=/full/path/to/IBAMR-0.18.0
```

### Linking errors

**Problem:** Missing IBAMR libraries

**Solution:** Ensure IBAMR is fully built. Check that these directories exist:
```
$IBAMR_ROOT/lib/
$IBAMR_ROOT/build/lib/
```

If IBAMR was built in a different location, you may need to update the library paths in `CMakeLists.txt`.

### MPI errors

**Problem:** MPI not found or incompatible version

**Solution:** Ensure you're using the same MPI that IBAMR was built with:
```bash
# Check MPI version
mpirun --version

# Specify MPI explicitly
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT -DMPI_ROOT=/path/to/mpi
```

### Test execution fails

**Problem:** Test runs but fails with runtime errors

**Solution:**
1. Check `test_results/<test_name>/stderr.log` for error messages
2. Ensure all required libraries are in your library path:
   ```bash
   export LD_LIBRARY_PATH=$IBAMR_ROOT/lib:$LD_LIBRARY_PATH
   ```
3. Verify input files are present in each test directory

## Key Features

### Independence
- ✅ **No modification to IBAMR source** - All tests are in a separate directory
- ✅ **Self-contained** - Includes all necessary utilities and headers
- ✅ **Portable** - Can be moved to any location

### Flexibility
- ✅ **Selective building** - Build only the tests you need
- ✅ **Configurable** - CMake options for different build configurations
- ✅ **Parallel execution** - MPI support for faster test runs

### Comprehensive Testing
- ✅ **17 different tests** covering all aspects of scalar transport
- ✅ **Analytical validation** - Comparison with exact solutions
- ✅ **Literature validation** - Comparison with published results
- ✅ **Automated reporting** - PASS/FAIL summary with timing

## Development

### Adding a New Test

1. Create a new directory `Test18_NewTest/`
2. Add `main.cpp` and `input2d` files
3. Update `CMakeLists.txt`:
   ```cmake
   elseif(TEST STREQUAL "test18_newtest")
       add_ibamr_test(${TEST} Test18_NewTest)
   ```
4. Add to appropriate tier list
5. Update `run_all_tests.sh` mapping

### Modifying Common Utilities

Edit files in `common/src/` and `common/include/`. All tests will automatically use the updated utilities.

## References

For detailed information about each test, see:
- `README.md` - Original test suite documentation
- `BUILD_STATUS.md` - Individual test build status
- `FINAL_REPORT.md` - Comprehensive validation results
- Each test's `README.md` - Test-specific documentation

## License

This test suite follows the same license as IBAMR 0.18.0.

## Support

For issues specific to this standalone build system:
1. Check the troubleshooting section above
2. Review the CMake configuration output
3. Check build logs in `build/`

For issues with the tests themselves:
1. See the original documentation in `README.md`
2. Check individual test READMEs
3. Review `FINAL_REPORT.md` for expected behavior

## Version Information

- **Test Suite Version:** 1.0.0
- **Extracted from:** IBAMR 0.18.0
- **Target IBAMR Version:** 0.18.0
- **CMake Minimum Version:** 3.12
- **C++ Standard:** C++14

---

**Last Updated:** 2025-11-19
**Extracted by:** Automated extraction script
