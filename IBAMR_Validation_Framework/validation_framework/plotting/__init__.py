"""
IBAMR Scalar Transport Validation Framework - Plotting Module
==============================================================

Comprehensive visualization tools for validation results.

Main components:
- error_plots: Error vs time/resolution plots
- field_plots: Scalar field visualization (slices, contours)
- convergence_plots: Convergence log-log plots
- comparison_plots: Side-by-side field comparisons
"""

from .error_plots import (
    plot_error_vs_time,
    plot_error_vs_resolution,
    plot_error_comparison,
    plot_error_statistics
)

from .field_plots import (
    plot_scalar_field_2d,
    plot_scalar_field_contour,
    plot_field_slice,
    plot_field_difference,
    plot_centerline_profile
)

from .convergence_plots import (
    plot_convergence_rate,
    plot_eoc_table,
    plot_richardson_extrapolation
)

from .comparison_plots import (
    plot_field_comparison,
    plot_multiple_fields,
    plot_heatmap_comparison
)

__all__ = [
    'plot_error_vs_time',
    'plot_error_vs_resolution',
    'plot_error_comparison',
    'plot_error_statistics',
    'plot_scalar_field_2d',
    'plot_scalar_field_contour',
    'plot_field_slice',
    'plot_field_difference',
    'plot_centerline_profile',
    'plot_convergence_rate',
    'plot_eoc_table',
    'plot_richardson_extrapolation',
    'plot_field_comparison',
    'plot_multiple_fields',
    'plot_heatmap_comparison',
]
