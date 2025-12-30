# IBAMR Scalar Transport Validation Framework

**A comprehensive automated validation system for IBAMR 0.18.0 scalar transport simulations.**

---

## 📋 Quick Start

```bash
# Navigate to your test suite
cd ../ScalarTransport_TestSuite_Standalone

# Set IBAMR installation path
export IBAMR_ROOT=/path/to/your/IBAMR-0.18.0

# Build tests
mkdir -p build && cd build
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT -DBUILD_ALL_TESTS=ON
make -j$(nproc)
cd ..

# Run validation
python3 ../IBAMR_Validation_Framework/run_all_tests.py --clean --mpi-np 4

# Analyze results
python3 ../IBAMR_Validation_Framework/analyze_results.py

# View report
cat Compatibility_Report.md
```

---

## 📁 What's Included

- **`run_all_tests.py`** - Automated test runner for all 17 tests
- **`analyze_results.py`** - Results analyzer and report generator
- **`quick_start.sh`** - One-command workflow automation
- **`validation_framework/`** - Python analysis library
  - `analysis/` - Error metrics, convergence, mass conservation
  - `plotting/` - Publication-quality visualizations
  - `reporting/` - Markdown report generation

---

## 📖 Documentation

1. **`HOW_TO_RUN_VALIDATION_IN_WSL.md`** - Complete step-by-step guide
2. **`VALIDATION_FRAMEWORK_README.md`** - Feature overview
3. **`validation_framework/README.md`** - API reference

---

## 📊 Features

✅ **L1, L2, L∞ Error Analysis** - Quantitative error metrics
✅ **Convergence Verification** - Order of accuracy analysis
✅ **Mass Conservation** - Conservation error tracking
✅ **Publication Plots** - 300 DPI PNG + PDF output
✅ **Comprehensive Reports** - Automated Markdown reports
✅ **17 Test Cases** - Complete test suite coverage

---

## 💻 Requirements

- IBAMR 0.18.0 (pre-installed)
- Python 3.7+ with numpy, scipy, matplotlib, h5py
- MPI (OpenMPI or MPICH)
- CMake 3.12+

---

## 📞 Support

See **`HOW_TO_RUN_VALIDATION_IN_WSL.md`** for detailed instructions and troubleshooting.

---

**Version:** 1.0.0
**Date:** 2025-11-19
**Compatible with:** IBAMR 0.18.0
