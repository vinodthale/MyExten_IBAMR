"""
IBAMR Scalar Transport Validation Framework - Analysis Module
==============================================================

This module provides comprehensive error analysis tools for IBAMR
scalar transport simulations.

Main components:
- error_metrics: L1, L2, Linf error calculators
- field_analysis: Scalar field comparison and difference tools
- convergence: Convergence rate calculators
- mass_conservation: Mass conservation checkers
- boundary_conditions: BC error analysis
"""

from .error_metrics import (
    compute_l1_error,
    compute_l2_error,
    compute_linf_error,
    compute_all_errors
)

from .field_analysis import (
    FieldAnalyzer,
    load_scalar_field,
    compute_field_difference,
    compute_field_statistics
)

from .convergence import (
    compute_convergence_rate,
    analyze_convergence_series,
    fit_convergence_order
)

from .mass_conservation import (
    check_mass_conservation,
    compute_mass_error,
    track_mass_over_time
)

__all__ = [
    'compute_l1_error',
    'compute_l2_error',
    'compute_linf_error',
    'compute_all_errors',
    'FieldAnalyzer',
    'load_scalar_field',
    'compute_field_difference',
    'compute_field_statistics',
    'compute_convergence_rate',
    'analyze_convergence_series',
    'fit_convergence_order',
    'check_mass_conservation',
    'compute_mass_error',
    'track_mass_over_time',
]
