# IBAMR Scalar Transport Test Suite - Validation Framework

## Overview

This directory contains a complete, automated validation framework for rigorously testing IBAMR 0.18.0 scalar transport capabilities.

## What's Included

### 1. **Automated Test Runner** (`run_all_tests.py`)
- Discovers and runs all 17 test cases
- Manages MPI execution
- Captures all outputs
- Organizes results systematically

### 2. **Comprehensive Analysis Module** (`validation_framework/analysis/`)
- **Error Metrics:** L1, L2, L∞ norm calculators
- **Field Analysis:** Scalar field loading and comparison tools
- **Convergence:** Order of accuracy verification
- **Mass Conservation:** Mass drift and conservation checkers

### 3. **Advanced Plotting Module** (`validation_framework/plotting/`)
- **Error Plots:** Error vs time, error vs resolution
- **Field Visualization:** 2D/3D field plots, contours, slices
- **Convergence Plots:** Log-log convergence with reference lines
- **Comparison Plots:** Multi-test comparisons, heatmaps

### 4. **Automated Reporting** (`validation_framework/reporting/`)
- Generates comprehensive Markdown reports
- Includes embedded plots
- Pass/fail summaries
- Detailed error analysis
- Convergence verification
- Mass conservation status

### 5. **Complete Documentation**
- **HOW_TO_RUN_VALIDATION_IN_WSL.md:** Step-by-step guide
- **validation_framework/README.md:** API reference
- **This file:** Quick overview

## Quick Start

### Option 1: Automated (Recommended)

```bash
./quick_start.sh
```

This runs the complete workflow automatically.

### Option 2: Step-by-Step

```bash
# 1. Build tests
mkdir -p build && cd build
cmake .. -DIBAMR_ROOT=/path/to/IBAMR-0.18.0 -DBUILD_ALL_TESTS=ON
make -j$(nproc)
cd ..

# 2. Run tests
python3 run_all_tests.py --clean

# 3. Analyze and report
python3 analyze_results.py
```

## Output Structure

```
ScalarTransport_TestSuite_Standalone/
├── results/
│   ├── Test01_SmokeTest/
│   │   ├── raw/              # IBAMR outputs
│   │   ├── plots/            # Visualizations (PNG/PDF)
│   │   ├── metrics.json      # Computed metrics
│   │   ├── summary.md        # Test summary
│   │   └── test_output.log   # Captured output
│   ├── Test02_Diffusion_Analytic/
│   └── ...
└── Compatibility_Report.md   # Final validation report
```

## Features

### Error Metrics Computed
- L1 error (integral norm)
- L2 error (RMS norm)
- L∞ error (maximum norm)
- Mean absolute error
- Pointwise error fields

### Convergence Analysis
- Order of accuracy (p)
- Experimental Order of Convergence (EOC)
- Richardson extrapolation
- Grid Convergence Index (GCI)

### Mass Conservation
- Total mass tracking
- Mass drift rate
- Conservation error
- Flux balance

### Visualization
All plots generated in both PNG (web) and PDF (publication):
- Error vs time
- Error vs grid resolution (log-log)
- Scalar field contours
- Difference fields (computed - exact)
- Centerline profiles
- Convergence plots with reference lines
- Multi-test comparisons
- Heatmaps

## Customization

### Analyze Your Own Test

Edit `analyze_results.py`:

```python
def analyze_test_results(test_dir: Path):
    # Load IBAMR output
    computed = load_scalar_field(test_dir / 'raw' / 'C.h5', variable='C')

    # Your exact solution
    exact = your_exact_solution_function(...)

    # Compute errors
    errors = compute_all_errors(computed, exact, dx=0.01, dy=0.01)

    # Generate plots
    plot_field_comparison(computed, exact,
                         test_dir / 'plots' / 'comparison.png')
    plot_error_vs_time(times, errors,
                      test_dir / 'plots' / 'error_timeline.png')

    # Save metrics
    with open(test_dir / 'metrics.json', 'w') as f:
        json.dump(errors, f, indent=2)
```

### Add Custom Metrics

```python
from validation_framework.analysis import compute_all_errors

# Extend with your metrics
metrics = compute_all_errors(computed, exact, dx, dy)
metrics['your_custom_metric'] = your_calculation(...)
```

### Customize Plots

```python
from validation_framework.plotting import plot_error_vs_time

# Custom styling
plot_error_vs_time(
    times, errors,
    output_path='custom_plot.png',
    title='My Custom Title',
    log_scale=True
)
```

## Test Categories

### Tier 1: Basic Validation (Tests 1-6)
- Smoke test
- Pure diffusion
- Pure advection
- Method of Manufactured Solutions
- Discontinuous initial conditions
- Mass conservation

### Tier 2: Complex Physics (Tests 7-10)
- Boundary conditions
- Sphere source
- High Schmidt number
- Moving immersed boundary

### Tier 3: Advanced Features (Tests 11-14)
- Adaptive Mesh Refinement
- Time-step sensitivity
- Long-time integration
- Benchmarks

### Tier 4: Literature Validation (Tests 15-17)
- Rotating cylinder
- 3D sphere
- Pitch-plunge airfoil

## Requirements

### System
- Linux/WSL with MPI support
- 8+ GB RAM
- 4+ CPU cores (recommended)

### Software
- IBAMR 0.18.0
- CMake 3.12+
- OpenMPI or MPICH
- Python 3.7+

### Python Packages
```bash
pip install numpy scipy matplotlib h5py
```

## Validation Metrics

A test **PASSES** if:
- ✅ Executes without errors
- ✅ L2 error < tolerance (test-specific)
- ✅ Convergence rate matches expected order (±20%)
- ✅ Mass conservation error < 10⁻⁶

A test **FAILS** if:
- ❌ Crashes or times out
- ❌ Error exceeds tolerance
- ❌ Convergence rate significantly off
- ❌ Mass not conserved

## Extending the Framework

### Add New Analysis

Create `validation_framework/analysis/your_analysis.py`:

```python
def your_new_analysis(field, ...):
    """Your analysis function"""
    # Implement your analysis
    return results
```

Update `validation_framework/analysis/__init__.py`:

```python
from .your_analysis import your_new_analysis

__all__ = [..., 'your_new_analysis']
```

### Add New Plots

Create `validation_framework/plotting/your_plots.py`:

```python
def your_custom_plot(data, output_path):
    """Your plotting function"""
    import matplotlib.pyplot as plt
    # Create plot
    plt.savefig(output_path)
    plt.close()
```

## Troubleshooting

See `HOW_TO_RUN_VALIDATION_IN_WSL.md` for detailed troubleshooting.

**Common Quick Fixes:**

```bash
# IBAMR not found
export IBAMR_ROOT=/path/to/IBAMR-0.18.0

# Python module errors
pip3 install --user numpy scipy matplotlib h5py

# MPI errors
sudo apt install libopenmpi-dev openmpi-bin

# Permission errors
chmod +x run_all_tests.py analyze_results.py quick_start.sh
```

## Support

- **Documentation:** See `HOW_TO_RUN_VALIDATION_IN_WSL.md`
- **API Reference:** See `validation_framework/README.md`
- **Issues:** https://github.com/vinodthale/MyExten_IBAMR/issues

## License

Part of MyExten_IBAMR. See repository root for details.

---

**Ready to validate? Run:** `./quick_start.sh`
