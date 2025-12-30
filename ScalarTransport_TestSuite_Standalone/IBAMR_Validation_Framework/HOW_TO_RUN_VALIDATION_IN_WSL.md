# How to Run IBAMR Scalar Transport Validation Suite in WSL

This comprehensive guide explains how to compile IBAMR, build the test suite, run all tests, perform analysis, and generate the final compatibility validation report on Windows Subsystem for Linux (WSL).

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setting Up IBAMR](#setting-up-ibamr)
3. [Building the Test Suite](#building-the-test-suite)
4. [Running All Tests](#running-all-tests)
5. [Analyzing Results](#analyzing-results)
6. [Generating the Final Report](#generating-the-final-report)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

---

## Prerequisites

### System Requirements

- **WSL 2** (Ubuntu 20.04 or later recommended)
- **At least 8 GB RAM**
- **20 GB free disk space**
- **4+ CPU cores** (recommended for parallel builds)

### Required Software

Install the following packages in your WSL environment:

```bash
sudo apt update
sudo apt install -y \
    build-essential \
    cmake \
    git \
    gfortran \
    libopenmpi-dev \
    openmpi-bin \
    libhdf5-openmpi-dev \
    libboost-all-dev \
    python3 \
    python3-pip \
    python3-dev
```

### Required Python Packages

```bash
pip3 install numpy scipy matplotlib h5py
```

---

## Setting Up IBAMR

### Option 1: IBAMR Already Installed

If you already have IBAMR 0.18.0 installed, note the installation path:

```bash
export IBAMR_ROOT=/path/to/your/IBAMR-0.18.0
```

Add this to your `~/.bashrc` for persistence.

### Option 2: Building IBAMR from Source

If you need to build IBAMR:

#### Step 1: Install Dependencies

##### SAMRAI

```bash
cd $HOME
wget https://github.com/LLNL/SAMRAI/archive/v-4-1-0.tar.gz
tar -xzf v-4-1-0.tar.gz
cd SAMRAI-v-4-1-0

mkdir build && cd build
cmake .. \
    -DCMAKE_INSTALL_PREFIX=$HOME/local/samrai \
    -DENABLE_HDF5=ON \
    -DHDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/openmpi
make -j$(nproc)
make install
```

##### PETSc (Optional but Recommended)

```bash
cd $HOME
wget https://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-3.18.0.tar.gz
tar -xzf petsc-3.18.0.tar.gz
cd petsc-3.18.0

./configure \
    --prefix=$HOME/local/petsc \
    --with-cc=mpicc \
    --with-cxx=mpicxx \
    --with-fc=mpif90 \
    --with-debugging=0 \
    --with-shared-libraries=1 \
    COPTFLAGS='-O3' \
    CXXOPTFLAGS='-O3' \
    FOPTFLAGS='-O3'

make PETSC_DIR=$HOME/petsc-3.18.0 PETSC_ARCH=arch-linux-c-opt all
make PETSC_DIR=$HOME/petsc-3.18.0 PETSC_ARCH=arch-linux-c-opt install
```

#### Step 2: Build IBAMR

```bash
cd $HOME/MyExten_IBAMR/IBAMR-0.18.0

mkdir build && cd build

cmake .. \
    -DCMAKE_INSTALL_PREFIX=$HOME/local/ibamr \
    -DCMAKE_BUILD_TYPE=Release \
    -DSAMRAI_ROOT=$HOME/local/samrai \
    -DPETSC_ROOT=$HOME/local/petsc \
    -DCMAKE_C_COMPILER=mpicc \
    -DCMAKE_CXX_COMPILER=mpicxx \
    -DCMAKE_Fortran_COMPILER=mpif90

make -j$(nproc)
make install
```

**Set environment variable:**

```bash
export IBAMR_ROOT=$HOME/local/ibamr
```

---

## Building the Test Suite

### Step 1: Navigate to Test Suite Directory

```bash
cd $HOME/MyExten_IBAMR/ScalarTransport_TestSuite_Standalone
```

### Step 2: Create Build Directory

```bash
mkdir -p build
cd build
```

### Step 3: Configure with CMake

Point CMake to your IBAMR installation:

```bash
cmake .. \
    -DIBAMR_ROOT=$IBAMR_ROOT \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_ALL_TESTS=ON
```

**Expected Output:**
```
========================================================
IBAMR Scalar Transport Test Suite - STANDALONE BUILD
========================================================
Build Type:      Release
C++ Standard:    14
C++ Compiler:    /usr/bin/mpicxx

IBAMR Configuration:
  IBAMR Root:    /home/user/local/ibamr
  Include Dirs:  ...
  Library Dir:   /home/user/local/ibamr/lib

Dependencies:
  MPI:           TRUE
  PETSc:         TRUE (if found)
  SAMRAI:        TRUE (if found)

Tests to build:
  ✓ test01_smoke
  ✓ test02_diffusion
  ✓ test03_advection
  ... (all 17 tests)
========================================================
```

### Step 4: Build All Tests

```bash
make -j$(nproc)
```

This will compile all 17 test executables. Compilation time: 10-20 minutes depending on your system.

### Step 5: Verify Build

```bash
ls -1 test*
```

You should see executables like:
```
test01_smoke
test02_diffusion
test03_advection
...
test17_pitch_plunge
```

---

## Running All Tests

### Step 1: Return to Test Suite Root

```bash
cd $HOME/MyExten_IBAMR/ScalarTransport_TestSuite_Standalone
```

### Step 2: Run Test Suite with Automation Script

#### Basic Run (Default Settings)

```bash
python3 run_all_tests.py
```

**Default Configuration:**
- Build directory: `./build`
- Results directory: `./results`
- MPI processes: 4
- Timeout per test: 3600 seconds (1 hour)

#### Custom Configuration

```bash
python3 run_all_tests.py \
    --build-dir ./build \
    --results-dir ./results \
    --mpi-np 8 \
    --timeout 7200 \
    --clean
```

**Options:**
- `--build-dir PATH`: Path to CMake build directory
- `--results-dir PATH`: Where to store results
- `--mpi-np N`: Number of MPI processes
- `--timeout SEC`: Timeout per test in seconds
- `--tests TEST1,TEST2`: Run only specific tests
- `--clean`: Clean results directory before running
- `--dry-run`: Show what would be run without executing

#### Run Specific Tests Only

```bash
python3 run_all_tests.py --tests "Test01_SmokeTest,Test02_Diffusion_Analytic"
```

### Step 3: Monitor Progress

The script will show real-time progress:

```
======================================================================
IBAMR SCALAR TRANSPORT TEST SUITE - AUTOMATED RUNNER
======================================================================
Build directory:   ./build
Results directory: ./results
MPI processes:     4
Timeout:           3600s

Discovering tests...
Found 17 tests:
  • Test01_SmokeTest
  • Test02_Diffusion_Analytic
  ...

Starting test execution...

[1/17]
======================================================================
Running: Test01_SmokeTest
======================================================================
Input file: Test01_SmokeTest/input2d
Executable: build/test01_smoke
MPI processes: 4
Results directory: results/Test01_SmokeTest

Starting test at 14:30:00...

✓ Test PASSED (duration: 125.3s)
...
```

### Step 4: Check Results

After all tests complete, you'll see a summary:

```
======================================================================
TEST EXECUTION SUMMARY
======================================================================
Total tests:  17
Passed:       15
Failed:       2
Errors:       0

Summary saved to: results/test_summary.json
```

---

## Analyzing Results

### Step 1: Run Analysis Script

```bash
python3 analyze_results.py
```

This script will:
1. Scan all test result directories
2. Load HDF5 output files
3. Compute error metrics (L1, L2, L∞)
4. Check mass conservation
5. Calculate convergence rates
6. Generate visualization plots
7. Create individual test summaries

**Expected Output:**
```
======================================================================
IBAMR SCALAR TRANSPORT - RESULTS ANALYSIS
======================================================================
Results directory: ./results
Report output: ./Compatibility_Report.md

Found 17 test result directories

Analyzing Test01_SmokeTest...
  Found 5 HDF5 files
  ✓ Metrics saved to results/Test01_SmokeTest/metrics.json

Analyzing Test02_Diffusion_Analytic...
  Found 10 HDF5 files
  Computing L1, L2, Linf errors...
  ✓ Metrics saved to results/Test02_Diffusion_Analytic/metrics.json
...

======================================================================
Generating compatibility report...
======================================================================
Report generated: Compatibility_Report.md

✓ Analysis complete!
```

### Step 2: Review Individual Test Results

Each test will have:

```
results/Test01_SmokeTest/
├── raw/                        # Raw IBAMR outputs
│   ├── *.h5
│   ├── *.xmf
│   └── viz_IB2d/
├── plots/                      # Generated visualizations
│   ├── error_vs_time.png
│   ├── error_vs_time.pdf
│   ├── field_comparison.png
│   ├── convergence_plot.png
│   └── mass_conservation.png
├── metrics.json                # Computed error metrics
├── summary.md                  # Test-specific summary
└── test_output.log             # Captured stdout/stderr
```

---

## Generating the Final Report

The final `Compatibility_Report.md` is automatically generated by `analyze_results.py`.

### View the Report

```bash
# View in terminal
cat Compatibility_Report.md

# Convert to PDF (requires pandoc)
pandoc Compatibility_Report.md -o Compatibility_Report.pdf

# View in browser (if you have a markdown viewer)
markdown Compatibility_Report.md > report.html
firefox report.html  # or your preferred browser
```

### Report Contents

The report includes:

1. **Executive Summary**
   - Overall pass/fail statistics
   - Assessment of IBAMR compatibility

2. **Test Results Table**
   - Quick overview of all tests
   - Status, errors, convergence rates

3. **Detailed Test Results**
   - Individual test analysis
   - Embedded plots
   - Error logs for failed tests

4. **Error Analysis**
   - L1, L2, L∞ error rankings
   - Statistical analysis

5. **Convergence Analysis**
   - Convergence rate verification
   - Comparison with expected orders

6. **Mass Conservation Analysis**
   - Mass drift over time
   - Conservation quality assessment

7. **Recommendations**
   - Action items for failed tests
   - Suggestions for improvement

8. **Appendix**
   - Metric definitions
   - Directory structure

---

## Troubleshooting

### Common Issues

#### 1. CMake Cannot Find IBAMR

**Error:**
```
CMake Error: IBAMR_ROOT directory does not exist
```

**Solution:**
```bash
export IBAMR_ROOT=/path/to/your/IBAMR-0.18.0
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT
```

#### 2. Linking Errors During Build

**Error:**
```
undefined reference to `SAMRAI::...`
```

**Solution:**
Ensure IBAMR was built with the same MPI compiler:
```bash
which mpicc mpicxx
# Should match what IBAMR was built with
```

#### 3. Test Hangs or Timeouts

**Solution:**
Increase timeout or reduce MPI processes:
```bash
python3 run_all_tests.py --mpi-np 2 --timeout 7200
```

#### 4. HDF5 File Read Errors

**Error:**
```
Unable to open HDF5 file
```

**Solution:**
Check HDF5 parallel support:
```bash
h5cc -showconfig | grep "Parallel HDF5"
# Should show "yes"
```

#### 5. Python Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'h5py'
```

**Solution:**
```bash
pip3 install --user h5py numpy scipy matplotlib
```

---

## Advanced Usage

### Customizing Error Analysis

Edit `analyze_results.py` to add custom analysis:

```python
def analyze_test_results(test_dir: Path):
    # Load your specific output format
    computed = load_scalar_field(test_dir / 'raw' / 'solution.h5', 'C')
    exact = compute_exact_solution(...)  # Your exact solution

    # Compute errors
    errors = compute_all_errors(computed, exact, dx=0.01, dy=0.01)

    # Generate plots
    plot_field_comparison(computed, exact,
                         test_dir / 'plots' / 'comparison.png')

    # Save metrics
    with open(test_dir / 'metrics.json', 'w') as f:
        json.dump(errors, f, indent=2)
```

### Running Tests in Parallel

To run multiple tests simultaneously (requires careful resource management):

```bash
# Run tests in batches
python3 run_all_tests.py --tests "Test01_SmokeTest,Test02_Diffusion_Analytic" &
python3 run_all_tests.py --tests "Test03_Advection_Analytic,Test04_MMS" &
wait
```

### Automated Nightly Testing

Create a cron job:

```bash
crontab -e
```

Add:
```cron
0 2 * * * cd $HOME/MyExten_IBAMR/ScalarTransport_TestSuite_Standalone && \
          python3 run_all_tests.py --clean && \
          python3 analyze_results.py && \
          mail -s "IBAMR Test Results" user@example.com < Compatibility_Report.md
```

### Comparing with Baseline Results

```python
# Save current results as baseline
cp results/test_summary.json results/baseline_summary.json

# Later, compare
import json
with open('results/test_summary.json') as f:
    current = json.load(f)
with open('results/baseline_summary.json') as f:
    baseline = json.load(f)

# Compute regression/improvement
for test in current['results']:
    # Compare metrics...
```

---

## File Structure Reference

After running the complete validation:

```
ScalarTransport_TestSuite_Standalone/
├── build/                          # CMake build directory
│   ├── test01_smoke
│   ├── test02_diffusion
│   └── ...
├── results/                        # Test results
│   ├── Test01_SmokeTest/
│   │   ├── raw/                    # Raw outputs
│   │   ├── plots/                  # Visualizations
│   │   ├── metrics.json            # Computed metrics
│   │   ├── summary.md              # Test summary
│   │   └── test_output.log         # Test log
│   ├── Test02_Diffusion_Analytic/
│   └── ...
├── validation_framework/           # Analysis tools
│   ├── analysis/
│   ├── plotting/
│   └── reporting/
├── run_all_tests.py                # Main test runner
├── analyze_results.py              # Results analyzer
├── Compatibility_Report.md         # Final report
└── HOW_TO_RUN_VALIDATION_IN_WSL.md # This file
```

---

## Quick Reference Commands

```bash
# Full validation workflow
cd $HOME/MyExten_IBAMR/ScalarTransport_TestSuite_Standalone

# 1. Build tests
mkdir -p build && cd build
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT -DBUILD_ALL_TESTS=ON
make -j$(nproc)
cd ..

# 2. Run all tests
python3 run_all_tests.py --clean --mpi-np 4

# 3. Analyze and report
python3 analyze_results.py

# 4. View report
cat Compatibility_Report.md
```

---

## Support and Contact

For issues or questions:

- **Repository Issues:** https://github.com/vinodthale/MyExten_IBAMR/issues
- **IBAMR Documentation:** https://ibamr.github.io
- **IBAMR Community:** https://github.com/ibamr/IBAMR

---

**Last Updated:** 2025-11-19
**Version:** 1.0.0
**Compatible with:** IBAMR 0.18.0
