# IBAMR Scalar Transport Validation Framework

**A comprehensive automated validation system for IBAMR 0.18.0 scalar transport simulations.**

---

## 📋 Quick Start

```bash
# 1. Set your IBAMR installation path
export IBAMR_ROOT=/path/to/your/IBAMR-0.18.0

# 2. Run the complete validation workflow
./quick_start.sh
```

That's it! The framework will:
- ✅ Build all 17 test cases
- ✅ Run tests with MPI
- ✅ Compute error metrics (L1, L2, L∞)
- ✅ Analyze convergence rates
- ✅ Check mass conservation
- ✅ Generate publication-quality plots
- ✅ Create comprehensive report

---

## 📁 What's Included

### Main Scripts
- **`run_all_tests.py`** - Automated test runner for all 17 tests
- **`analyze_results.py`** - Results analyzer and report generator
- **`quick_start.sh`** - One-command full workflow automation

### Documentation
- **`HOW_TO_RUN_VALIDATION_IN_WSL.md`** - Complete step-by-step guide
- **`VALIDATION_FRAMEWORK_README.md`** - Feature overview and examples
- **`validation_framework/README.md`** - API reference

### Analysis Framework (`validation_framework/`)
- **`analysis/error_metrics.py`** - L1, L2, L∞ error calculators
- **`analysis/convergence.py`** - Convergence rate analysis
- **`analysis/mass_conservation.py`** - Mass conservation verification
- **`analysis/field_analysis.py`** - Field loading and comparison

### Plotting Framework (`validation_framework/`)
- **`plotting/error_plots.py`** - Error vs time/resolution plots
- **`plotting/field_plots.py`** - 2D/3D field visualizations
- **`plotting/convergence_plots.py`** - Log-log convergence plots
- **`plotting/comparison_plots.py`** - Multi-test comparisons

### Reporting (`validation_framework/`)
- **`reporting/report_generator.py`** - Markdown report generator

---

## 🚀 Usage

### Step-by-Step Workflow

#### 1. Build Tests
```bash
cd ../ScalarTransport_TestSuite_Standalone
mkdir -p build && cd build
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT -DBUILD_ALL_TESTS=ON
make -j$(nproc)
cd ..
```

#### 2. Run Tests
```bash
python3 ../IBAMR_Validation_Framework/run_all_tests.py \
    --build-dir ./build \
    --results-dir ./results \
    --mpi-np 4 \
    --clean
```

#### 3. Analyze Results
```bash
python3 ../IBAMR_Validation_Framework/analyze_results.py \
    --results-dir ./results \
    --report-output ./Compatibility_Report.md
```

#### 4. View Report
```bash
cat Compatibility_Report.md
```

---

## 📊 What It Computes

### Error Metrics
- **L1 error** - Integral norm: ∫|u_computed - u_exact| dV / ∫|u_exact| dV
- **L2 error** - RMS norm: √(∫(u_computed - u_exact)² dV) / √(∫u_exact² dV)
- **L∞ error** - Maximum norm: max|u_computed - u_exact| / max|u_exact|
- Mean/median absolute error
- Error statistics (percentiles)

### Convergence Analysis
- Convergence rate (order of accuracy)
- Experimental Order of Convergence (EOC)
- Richardson extrapolation
- Grid Convergence Index (GCI)
- R² goodness of fit

### Mass Conservation
- Total mass tracking
- Mass drift rate
- Conservation error
- Temporal evolution

---

## 📈 Generated Outputs

### For Each Test:
```
results/TestXX_Name/
├── raw/                # IBAMR outputs (.h5, .xmf, viz_*)
├── plots/              # Visualizations (PNG + PDF)
│   ├── error_vs_time.*
│   ├── error_vs_resolution.*
│   ├── field_comparison.*
│   ├── convergence.*
│   └── mass_conservation.*
├── metrics.json        # Computed metrics
├── summary.md          # Test-specific summary
└── test_output.log     # Execution log
```

### Overall Report:
- `Compatibility_Report.md` - Comprehensive validation report
- `test_summary.json` - Machine-readable summary

---

## 🧪 Test Suite Coverage

**17 Tests Across 4 Tiers:**

### Tier 1: Basic Validation (6 tests)
1. Test01_SmokeTest
2. Test02_Diffusion_Analytic
3. Test03_Advection_Analytic
4. Test04_MMS
5. Test05_Discontinuous
6. Test06_MassConservation

### Tier 2: Complex Physics (4 tests)
7. Test07_BCs
8. Test08_SphereSource
9. Test09_HighSc
10. Test10_MovingIB

### Tier 3: Advanced Features (4 tests)
11. Test11_AMR
12. Test12_TimeStep
13. Test13_LongRun
14. Test14_Benchmarks

### Tier 4: Literature Validation (3 tests)
15. Test15_RotatingCylinder
16. Test16_3DSphere
17. Test17_PitchPlunge

---

## 💻 Requirements

### System
- Linux/WSL 2 (Ubuntu 20.04+)
- 8+ GB RAM
- 4+ CPU cores (recommended)
- 20 GB free disk space

### Software
- **IBAMR 0.18.0** (pre-installed)
- **CMake** 3.12+
- **MPI** (OpenMPI or MPICH)
- **Python** 3.7+
- **HDF5** with parallel support

### Python Packages
```bash
pip3 install numpy scipy matplotlib h5py
```

---

## 📚 Documentation

### Primary Guides
1. **`HOW_TO_RUN_VALIDATION_IN_WSL.md`** - Start here! Complete tutorial
2. **`VALIDATION_FRAMEWORK_README.md`** - Features and examples
3. **`validation_framework/README.md`** - API reference

### Key Sections in HOW_TO_RUN_VALIDATION_IN_WSL.md
- Prerequisites and dependencies
- IBAMR installation (if needed)
- Building the test suite
- Running tests
- Analyzing results
- Troubleshooting
- Advanced usage

---

## 🎨 Example: Basic Error Analysis

```python
from validation_framework.analysis import compute_all_errors
import numpy as np

# Load fields
computed = np.load('computed_field.npy')
exact = np.load('exact_field.npy')

# Compute errors
errors = compute_all_errors(computed, exact, dx=0.01, dy=0.01)

print(f"L1:   {errors['L1']:.6e}")
print(f"L2:   {errors['L2']:.6e}")
print(f"Linf: {errors['Linf']:.6e}")
```

## 🎨 Example: Convergence Analysis

```python
from validation_framework.analysis import analyze_convergence_series
from validation_framework.plotting import plot_convergence_rate

resolutions = [0.1, 0.05, 0.025, 0.0125]
errors = [1e-2, 2.5e-3, 6.2e-4, 1.5e-4]

# Analyze
results = analyze_convergence_series(errors, resolutions)
print(f"Convergence rate: {results['convergence_rate']:.2f}")

# Plot
plot_convergence_rate(
    resolutions, errors, 'convergence.png',
    convergence_rate=results['convergence_rate'],
    expected_order=2.0
)
```

## 🎨 Example: Mass Conservation

```python
from validation_framework.analysis import check_mass_conservation

# Fields at different timesteps
fields = [field_t0, field_t1, field_t2, field_t3]

results = check_mass_conservation(
    fields, dx=0.01, dy=0.01, tolerance=1e-6
)

if results['is_conserved']:
    print("✓ Mass is conserved")
else:
    print(f"✗ Max drift: {results['max_relative_change']:.6e}")
```

---

## 🛠️ Customization

### Add Custom Analysis

Edit `analyze_results.py`:

```python
def analyze_test_results(test_dir: Path):
    # Load IBAMR output
    computed = load_scalar_field(test_dir / 'raw' / 'solution.h5', 'C')
    exact = your_exact_solution(...)

    # Compute errors
    errors = compute_all_errors(computed, exact, dx=0.01, dy=0.01)

    # Generate plots
    plot_field_comparison(computed, exact,
                         test_dir / 'plots' / 'comparison.png')

    # Save metrics
    with open(test_dir / 'metrics.json', 'w') as f:
        json.dump(errors, f, indent=2)
```

### Add Custom Plots

```python
from validation_framework.plotting import plot_error_vs_time

plot_error_vs_time(
    times, errors,
    output_path='custom_plot.png',
    title='My Custom Analysis',
    log_scale=True
)
```

---

## 🐛 Troubleshooting

### Common Issues

**CMake can't find IBAMR:**
```bash
export IBAMR_ROOT=/path/to/IBAMR-0.18.0
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT
```

**Python module errors:**
```bash
pip3 install --user numpy scipy matplotlib h5py
```

**MPI not found:**
```bash
sudo apt install libopenmpi-dev openmpi-bin
```

**Tests timeout:**
```bash
python3 run_all_tests.py --timeout 7200 --mpi-np 2
```

See `HOW_TO_RUN_VALIDATION_IN_WSL.md` for detailed troubleshooting.

---

## 📖 API Reference

See `validation_framework/README.md` for complete API documentation including:
- All function signatures
- Parameter descriptions
- Return values
- Usage examples

---

## 🤝 Integration with Test Suite

This framework is designed to work with:
```
../ScalarTransport_TestSuite_Standalone/
```

The validation framework lives separately but analyzes tests from the test suite directory.

**Directory Structure:**
```
MyExten_IBAMR/
├── IBAMR_Validation_Framework/    ⬅️ This directory
│   ├── run_all_tests.py
│   ├── analyze_results.py
│   ├── validation_framework/
│   └── documentation...
├── ScalarTransport_TestSuite_Standalone/
│   ├── Test01_SmokeTest/
│   ├── Test02_Diffusion_Analytic/
│   └── ...
└── IBAMR-0.18.0/
```

---

## ✨ Features

✅ **Fully Automated** - One command runs everything
✅ **Quantitative** - L1, L2, L∞ error norms
✅ **Rigorous** - Convergence verification
✅ **Conservative** - Mass conservation checking
✅ **Publication-Ready** - 300 DPI PNG + PDF plots
✅ **Comprehensive** - Detailed Markdown reports
✅ **Extensible** - Easy to customize
✅ **Well-Documented** - 3 complete guides

---

## 📝 License

Part of MyExten_IBAMR project. See repository root for license information.

---

## 📞 Support

- **Documentation:** See guides in this directory
- **Issues:** https://github.com/vinodthale/MyExten_IBAMR/issues
- **IBAMR Docs:** https://ibamr.github.io

---

## 🎯 Next Steps

1. Read `HOW_TO_RUN_VALIDATION_IN_WSL.md`
2. Run `./quick_start.sh`
3. Review generated `Compatibility_Report.md`
4. Customize analysis as needed

---

**Version:** 1.0.0
**Date:** 2025-11-19
**Compatible with:** IBAMR 0.18.0
