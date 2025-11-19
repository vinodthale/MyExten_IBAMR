# IBAMR Scalar Transport Validation Framework

A comprehensive Python framework for validating IBAMR scalar transport simulations.

## Overview

This framework provides automated tools for:

- **Error Analysis:** L1, L2, L∞ error metrics
- **Convergence Analysis:** Order of accuracy verification
- **Mass Conservation:** Conservation error tracking
- **Field Comparison:** Computed vs exact solution comparison
- **Visualization:** Automated plot generation
- **Reporting:** Comprehensive markdown reports

## Structure

```
validation_framework/
├── analysis/              # Error analysis and metrics
│   ├── error_metrics.py   # L1, L2, Linf calculators
│   ├── field_analysis.py  # Field loading and comparison
│   ├── convergence.py     # Convergence rate analysis
│   └── mass_conservation.py # Mass conservation checking
├── plotting/              # Visualization tools
│   ├── error_plots.py     # Error vs time/resolution
│   ├── field_plots.py     # Field visualization
│   ├── convergence_plots.py # Convergence plots
│   └── comparison_plots.py # Multi-test comparisons
└── reporting/             # Report generation
    └── report_generator.py # Markdown report generator
```

## Quick Start

### Basic Error Analysis

```python
from validation_framework.analysis import compute_all_errors
import numpy as np

# Your computed and exact solutions
computed = np.load('computed_field.npy')
exact = np.load('exact_field.npy')

# Compute all error norms
errors = compute_all_errors(computed, exact, dx=0.01, dy=0.01)

print(f"L1 error:    {errors['L1']:.6e}")
print(f"L2 error:    {errors['L2']:.6e}")
print(f"Linf error:  {errors['Linf']:.6e}")
```

### Convergence Analysis

```python
from validation_framework.analysis import analyze_convergence_series

resolutions = [0.1, 0.05, 0.025, 0.0125]
errors = [1e-2, 2.5e-3, 6.2e-4, 1.5e-4]

results = analyze_convergence_series(errors, resolutions)
print(f"Convergence rate: {results['convergence_rate']:.2f}")
print(f"R²: {results['r_squared']:.4f}")
```

### Generate Plots

```python
from validation_framework.plotting import plot_error_vs_time, plot_convergence_rate

# Error vs time
times = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
errors = {'L1': [...], 'L2': [...], 'Linf': [...]}
plot_error_vs_time(times, errors, 'error_vs_time.png')

# Convergence plot
resolutions = [0.1, 0.05, 0.025]
errors = [1e-2, 2.5e-3, 6.2e-4]
plot_convergence_rate(resolutions, errors, 'convergence.png',
                     convergence_rate=2.0, expected_order=2.0)
```

### Mass Conservation Check

```python
from validation_framework.analysis import check_mass_conservation

# Fields at different time steps
fields = [field_t0, field_t1, field_t2, field_t3]

results = check_mass_conservation(fields, dx=0.01, dy=0.01, tolerance=1e-6)

if results['is_conserved']:
    print("✓ Mass is conserved")
else:
    print(f"✗ Mass error: {results['max_relative_change']:.6e}")
```

## API Reference

### analysis.error_metrics

- `compute_l1_error(computed, exact, dx, dy, dz)` - L1 error norm
- `compute_l2_error(computed, exact, dx, dy, dz)` - L2 error norm
- `compute_linf_error(computed, exact)` - L∞ error norm
- `compute_all_errors(computed, exact, dx, dy, dz)` - All error metrics

### analysis.convergence

- `compute_convergence_rate(errors, resolutions)` - Convergence rate
- `analyze_convergence_series(errors, resolutions)` - Full analysis
- `compute_eoc_table(errors, resolutions)` - EOC table

### analysis.mass_conservation

- `check_mass_conservation(fields, dx, dy, dz, tolerance)` - Check conservation
- `compute_total_mass(field, dx, dy, dz)` - Compute total mass
- `track_mass_over_time(fields, times, dx, dy, dz)` - Track mass evolution

### plotting.error_plots

- `plot_error_vs_time(times, errors, output_path)` - Error timeline
- `plot_error_vs_resolution(resolutions, errors, output_path)` - Error vs h
- `plot_error_comparison(test_names, errors, output_path)` - Bar comparison

### plotting.field_plots

- `plot_scalar_field_2d(field, output_path)` - 2D field visualization
- `plot_scalar_field_contour(field, output_path)` - Contour plot
- `plot_field_difference(field1, field2, output_path)` - Difference field
- `plot_centerline_profile(field, output_path)` - Centerline profile

### plotting.convergence_plots

- `plot_convergence_rate(resolutions, errors, output_path, convergence_rate)`
- `plot_eoc_table(eoc_data, output_path)` - EOC visualization
- `plot_richardson_extrapolation(resolutions, solutions, extrapolated, output_path)`

### reporting

- `generate_compatibility_report(results_dir, output_file)` - Generate full report

## Requirements

```
numpy >= 1.20
scipy >= 1.7
matplotlib >= 3.3
h5py >= 3.0
```

## Installation

The framework is standalone and doesn't require installation. Simply ensure the parent directory is in your Python path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from validation_framework.analysis import *
from validation_framework.plotting import *
```

## Examples

See `../analyze_results.py` for a complete example of using the framework.

## License

Part of MyExten_IBAMR project. See repository root for license information.
