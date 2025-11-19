"""
Error Metrics Module
====================

Provides functions to compute L1, L2, and L∞ error norms for
scalar field comparisons.
"""

import numpy as np
from typing import Dict, Tuple, Optional, Union


def compute_l1_error(computed: np.ndarray,
                     exact: np.ndarray,
                     dx: Optional[Union[float, np.ndarray]] = None,
                     dy: Optional[Union[float, np.ndarray]] = None,
                     dz: Optional[Union[float, np.ndarray]] = None) -> float:
    """
    Compute L1 error norm.

    L1 = ∫|u_computed - u_exact| dV / ∫|u_exact| dV

    Parameters:
    -----------
    computed : np.ndarray
        Computed scalar field
    exact : np.ndarray
        Exact/reference scalar field
    dx, dy, dz : float or np.ndarray, optional
        Grid spacing in each dimension

    Returns:
    --------
    float : L1 error norm
    """
    assert computed.shape == exact.shape, "Field shapes must match"

    # Compute absolute difference
    abs_diff = np.abs(computed - exact)
    abs_exact = np.abs(exact)

    # Compute cell volumes
    if dx is not None or dy is not None or dz is not None:
        dV = _compute_cell_volume(computed.shape, dx, dy, dz)
        numerator = np.sum(abs_diff * dV)
        denominator = np.sum(abs_exact * dV)
    else:
        numerator = np.sum(abs_diff)
        denominator = np.sum(abs_exact)

    # Avoid division by zero
    if denominator < 1e-14:
        # If exact solution is zero, return absolute error
        return numerator / computed.size

    return numerator / denominator


def compute_l2_error(computed: np.ndarray,
                     exact: np.ndarray,
                     dx: Optional[Union[float, np.ndarray]] = None,
                     dy: Optional[Union[float, np.ndarray]] = None,
                     dz: Optional[Union[float, np.ndarray]] = None) -> float:
    """
    Compute L2 error norm.

    L2 = sqrt(∫(u_computed - u_exact)² dV) / sqrt(∫u_exact² dV)

    Parameters:
    -----------
    computed : np.ndarray
        Computed scalar field
    exact : np.ndarray
        Exact/reference scalar field
    dx, dy, dz : float or np.ndarray, optional
        Grid spacing in each dimension

    Returns:
    --------
    float : L2 error norm
    """
    assert computed.shape == exact.shape, "Field shapes must match"

    # Compute squared difference
    diff_squared = (computed - exact) ** 2
    exact_squared = exact ** 2

    # Compute cell volumes
    if dx is not None or dy is not None or dz is not None:
        dV = _compute_cell_volume(computed.shape, dx, dy, dz)
        numerator = np.sqrt(np.sum(diff_squared * dV))
        denominator = np.sqrt(np.sum(exact_squared * dV))
    else:
        numerator = np.sqrt(np.sum(diff_squared))
        denominator = np.sqrt(np.sum(exact_squared))

    # Avoid division by zero
    if denominator < 1e-14:
        # If exact solution is zero, return RMS error
        return numerator / np.sqrt(computed.size)

    return numerator / denominator


def compute_linf_error(computed: np.ndarray,
                       exact: np.ndarray) -> float:
    """
    Compute L∞ (maximum) error norm.

    L∞ = max|u_computed - u_exact| / max|u_exact|

    Parameters:
    -----------
    computed : np.ndarray
        Computed scalar field
    exact : np.ndarray
        Exact/reference scalar field

    Returns:
    --------
    float : L∞ error norm
    """
    assert computed.shape == exact.shape, "Field shapes must match"

    max_diff = np.max(np.abs(computed - exact))
    max_exact = np.max(np.abs(exact))

    # Avoid division by zero
    if max_exact < 1e-14:
        return max_diff

    return max_diff / max_exact


def compute_all_errors(computed: np.ndarray,
                       exact: np.ndarray,
                       dx: Optional[Union[float, np.ndarray]] = None,
                       dy: Optional[Union[float, np.ndarray]] = None,
                       dz: Optional[Union[float, np.ndarray]] = None) -> Dict[str, float]:
    """
    Compute all error norms at once.

    Parameters:
    -----------
    computed : np.ndarray
        Computed scalar field
    exact : np.ndarray
        Exact/reference scalar field
    dx, dy, dz : float or np.ndarray, optional
        Grid spacing in each dimension

    Returns:
    --------
    dict : Dictionary containing all error metrics
    """
    errors = {
        'L1': compute_l1_error(computed, exact, dx, dy, dz),
        'L2': compute_l2_error(computed, exact, dx, dy, dz),
        'Linf': compute_linf_error(computed, exact),
        'max_abs_error': np.max(np.abs(computed - exact)),
        'mean_abs_error': np.mean(np.abs(computed - exact)),
        'rms_error': np.sqrt(np.mean((computed - exact) ** 2)),
    }

    return errors


def compute_pointwise_error(computed: np.ndarray,
                            exact: np.ndarray) -> np.ndarray:
    """
    Compute pointwise absolute error.

    Parameters:
    -----------
    computed : np.ndarray
        Computed scalar field
    exact : np.ndarray
        Exact/reference scalar field

    Returns:
    --------
    np.ndarray : Pointwise error field
    """
    return np.abs(computed - exact)


def compute_relative_error(computed: np.ndarray,
                          exact: np.ndarray,
                          epsilon: float = 1e-14) -> np.ndarray:
    """
    Compute pointwise relative error.

    relative_error = |computed - exact| / (|exact| + epsilon)

    Parameters:
    -----------
    computed : np.ndarray
        Computed scalar field
    exact : np.ndarray
        Exact/reference scalar field
    epsilon : float
        Small value to avoid division by zero

    Returns:
    --------
    np.ndarray : Pointwise relative error field
    """
    return np.abs(computed - exact) / (np.abs(exact) + epsilon)


def _compute_cell_volume(shape: Tuple[int, ...],
                        dx: Optional[Union[float, np.ndarray]] = None,
                        dy: Optional[Union[float, np.ndarray]] = None,
                        dz: Optional[Union[float, np.ndarray]] = None) -> np.ndarray:
    """
    Compute cell volumes for integration.

    Parameters:
    -----------
    shape : tuple
        Shape of the field array
    dx, dy, dz : float or np.ndarray, optional
        Grid spacing in each dimension

    Returns:
    --------
    np.ndarray : Cell volume array
    """
    ndim = len(shape)

    if ndim == 1:
        if dx is None:
            dx = 1.0
        if isinstance(dx, (int, float)):
            return np.full(shape, dx)
        else:
            return dx

    elif ndim == 2:
        if dx is None:
            dx = 1.0
        if dy is None:
            dy = 1.0

        if isinstance(dx, (int, float)) and isinstance(dy, (int, float)):
            return np.full(shape, dx * dy)
        else:
            # Handle non-uniform grids
            if isinstance(dx, (int, float)):
                dx_array = np.full(shape[0], dx)
            else:
                dx_array = dx

            if isinstance(dy, (int, float)):
                dy_array = np.full(shape[1], dy)
            else:
                dy_array = dy

            return np.outer(dx_array, dy_array)

    elif ndim == 3:
        if dx is None:
            dx = 1.0
        if dy is None:
            dy = 1.0
        if dz is None:
            dz = 1.0

        if isinstance(dx, (int, float)) and isinstance(dy, (int, float)) and isinstance(dz, (int, float)):
            return np.full(shape, dx * dy * dz)
        else:
            # Handle non-uniform grids (simplified)
            # For full non-uniform 3D grids, this would need more sophisticated handling
            return np.full(shape, float(dx) * float(dy) * float(dz))

    else:
        raise ValueError(f"Unsupported number of dimensions: {ndim}")


def compute_error_statistics(computed: np.ndarray,
                             exact: np.ndarray) -> Dict[str, float]:
    """
    Compute comprehensive error statistics.

    Parameters:
    -----------
    computed : np.ndarray
        Computed scalar field
    exact : np.ndarray
        Exact/reference scalar field

    Returns:
    --------
    dict : Dictionary containing error statistics
    """
    diff = computed - exact
    abs_diff = np.abs(diff)

    stats = {
        'mean_error': np.mean(diff),
        'std_error': np.std(diff),
        'min_error': np.min(diff),
        'max_error': np.max(diff),
        'mean_abs_error': np.mean(abs_diff),
        'median_abs_error': np.median(abs_diff),
        'rms_error': np.sqrt(np.mean(diff ** 2)),
        'max_abs_error': np.max(abs_diff),
        'percentile_95': np.percentile(abs_diff, 95),
        'percentile_99': np.percentile(abs_diff, 99),
    }

    return stats
