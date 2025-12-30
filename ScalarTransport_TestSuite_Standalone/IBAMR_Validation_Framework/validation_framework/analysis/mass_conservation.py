"""
Mass Conservation Analysis Module
==================================

Tools for checking mass conservation in scalar transport simulations.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple


def compute_total_mass(field: np.ndarray,
                      dx: Optional[float] = None,
                      dy: Optional[float] = None,
                      dz: Optional[float] = None) -> float:
    """
    Compute total mass (integral) of scalar field.

    M = ∫C dV

    Parameters:
    -----------
    field : np.ndarray
        Scalar field (concentration)
    dx, dy, dz : float, optional
        Grid spacing in each dimension

    Returns:
    --------
    float : Total mass
    """
    # Compute cell volume
    if dx is not None or dy is not None or dz is not None:
        dV = _compute_volume_element(field.shape, dx, dy, dz)
        return np.sum(field * dV)
    else:
        # No grid spacing provided, return sum
        return np.sum(field)


def check_mass_conservation(fields: List[np.ndarray],
                           dx: Optional[float] = None,
                           dy: Optional[float] = None,
                           dz: Optional[float] = None,
                           tolerance: float = 1e-6) -> Dict:
    """
    Check mass conservation across multiple time steps.

    Parameters:
    -----------
    fields : list of np.ndarray
        List of scalar fields at different times
    dx, dy, dz : float, optional
        Grid spacing
    tolerance : float
        Relative tolerance for conservation check

    Returns:
    --------
    dict : Mass conservation analysis
    """
    if len(fields) == 0:
        return {'error': 'No fields provided'}

    # Compute mass at each time
    masses = [compute_total_mass(f, dx, dy, dz) for f in fields]

    # Reference mass (initial)
    M0 = masses[0]

    # Compute relative changes
    relative_changes = [(M - M0) / M0 if abs(M0) > 1e-14 else (M - M0) for M in masses]
    absolute_changes = [M - M0 for M in masses]

    # Check if conserved
    max_relative_change = max(abs(rc) for rc in relative_changes)
    is_conserved = max_relative_change < tolerance

    results = {
        'is_conserved': is_conserved,
        'initial_mass': M0,
        'final_mass': masses[-1],
        'masses': masses,
        'relative_changes': relative_changes,
        'absolute_changes': absolute_changes,
        'max_relative_change': max_relative_change,
        'max_absolute_change': max(abs(ac) for ac in absolute_changes),
        'mean_mass': np.mean(masses),
        'std_mass': np.std(masses),
        'tolerance': tolerance,
    }

    return results


def compute_mass_error(field: np.ndarray,
                      initial_mass: float,
                      dx: Optional[float] = None,
                      dy: Optional[float] = None,
                      dz: Optional[float] = None) -> float:
    """
    Compute mass conservation error relative to initial mass.

    Parameters:
    -----------
    field : np.ndarray
        Current scalar field
    initial_mass : float
        Initial total mass
    dx, dy, dz : float, optional
        Grid spacing

    Returns:
    --------
    float : Relative mass error
    """
    current_mass = compute_total_mass(field, dx, dy, dz)

    if abs(initial_mass) > 1e-14:
        return (current_mass - initial_mass) / initial_mass
    else:
        return current_mass - initial_mass


def track_mass_over_time(fields: List[np.ndarray],
                         times: List[float],
                         dx: Optional[float] = None,
                         dy: Optional[float] = None,
                         dz: Optional[float] = None) -> Dict:
    """
    Track mass evolution over time.

    Parameters:
    -----------
    fields : list of np.ndarray
        Scalar fields at different times
    times : list of float
        Time values
    dx, dy, dz : float, optional
        Grid spacing

    Returns:
    --------
    dict : Mass tracking results
    """
    assert len(fields) == len(times), "Fields and times must have same length"

    masses = [compute_total_mass(f, dx, dy, dz) for f in fields]

    # Compute mass changes
    M0 = masses[0]
    relative_errors = [(M - M0) / M0 if abs(M0) > 1e-14 else (M - M0) for M in masses]

    # Compute drift rate (linear fit)
    if len(times) > 1:
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(times, relative_errors)
        drift_rate = slope
    else:
        drift_rate = None

    results = {
        'times': times,
        'masses': masses,
        'relative_errors': relative_errors,
        'drift_rate': drift_rate,
        'initial_mass': M0,
        'final_mass': masses[-1],
        'total_drift': relative_errors[-1],
        'max_drift': max(abs(e) for e in relative_errors),
    }

    return results


def compute_flux_balance(field: np.ndarray,
                        source_term: Optional[np.ndarray] = None,
                        dt: float = 1.0,
                        dx: Optional[float] = None,
                        dy: Optional[float] = None,
                        dz: Optional[float] = None) -> Dict:
    """
    Compute flux balance for mass conservation check.

    dM/dt = ∫S dV - ∫(∇·F) dV

    Parameters:
    -----------
    field : np.ndarray
        Scalar field
    source_term : np.ndarray, optional
        Source/sink term
    dt : float
        Time step
    dx, dy, dz : float, optional
        Grid spacing

    Returns:
    --------
    dict : Flux balance analysis
    """
    dV = _compute_volume_element(field.shape, dx, dy, dz)

    # Compute total mass
    total_mass = np.sum(field * dV)

    # Compute source contribution
    if source_term is not None:
        source_integral = np.sum(source_term * dV)
    else:
        source_integral = 0.0

    results = {
        'total_mass': total_mass,
        'source_integral': source_integral,
        'expected_mass_change': source_integral * dt,
    }

    return results


def check_boundary_flux(field: np.ndarray,
                       boundary_type: str = 'periodic') -> Dict:
    """
    Check flux through domain boundaries.

    Parameters:
    -----------
    field : np.ndarray
        Scalar field
    boundary_type : str
        Type of boundary conditions

    Returns:
    --------
    dict : Boundary flux analysis
    """
    ndim = field.ndim

    fluxes = {}

    if ndim >= 1:
        fluxes['x_min'] = np.sum(field[0, ...])
        fluxes['x_max'] = np.sum(field[-1, ...])

    if ndim >= 2:
        fluxes['y_min'] = np.sum(field[:, 0, ...])
        fluxes['y_max'] = np.sum(field[:, -1, ...])

    if ndim >= 3:
        fluxes['z_min'] = np.sum(field[:, :, 0])
        fluxes['z_max'] = np.sum(field[:, :, -1])

    # Check periodicity if applicable
    if boundary_type == 'periodic':
        periodic_checks = {}
        if ndim >= 1:
            periodic_checks['x_periodic'] = np.allclose(field[0, ...], field[-1, ...])
        if ndim >= 2:
            periodic_checks['y_periodic'] = np.allclose(field[:, 0, ...], field[:, -1, ...])
        if ndim >= 3:
            periodic_checks['z_periodic'] = np.allclose(field[:, :, 0], field[:, :, -1])

        fluxes['periodic_checks'] = periodic_checks

    return fluxes


def _compute_volume_element(shape: Tuple[int, ...],
                           dx: Optional[float] = None,
                           dy: Optional[float] = None,
                           dz: Optional[float] = None) -> float:
    """Compute volume element for integration"""
    ndim = len(shape)

    if ndim == 1:
        return dx if dx is not None else 1.0
    elif ndim == 2:
        dx_val = dx if dx is not None else 1.0
        dy_val = dy if dy is not None else 1.0
        return dx_val * dy_val
    elif ndim == 3:
        dx_val = dx if dx is not None else 1.0
        dy_val = dy if dy is not None else 1.0
        dz_val = dz if dz is not None else 1.0
        return dx_val * dy_val * dz_val
    else:
        return 1.0


def analyze_mass_drift(masses: List[float],
                      times: List[float],
                      tolerance: float = 1e-6) -> Dict:
    """
    Analyze mass drift characteristics.

    Parameters:
    -----------
    masses : list of float
        Mass values over time
    times : list of float
        Time values
    tolerance : float
        Acceptable tolerance

    Returns:
    --------
    dict : Drift analysis
    """
    from scipy import stats

    masses = np.array(masses)
    times = np.array(times)

    M0 = masses[0]
    relative_drift = (masses - M0) / M0 if abs(M0) > 1e-14 else (masses - M0)

    # Linear fit
    slope, intercept, r_value, p_value, std_err = stats.linregress(times, relative_drift)

    # Categorize drift
    max_drift = np.max(np.abs(relative_drift))

    if max_drift < tolerance:
        drift_category = 'Excellent'
    elif max_drift < 10 * tolerance:
        drift_category = 'Good'
    elif max_drift < 100 * tolerance:
        drift_category = 'Acceptable'
    else:
        drift_category = 'Poor'

    results = {
        'drift_rate': slope,
        'drift_rate_std': std_err,
        'max_drift': max_drift,
        'final_drift': relative_drift[-1],
        'mean_drift': np.mean(relative_drift),
        'std_drift': np.std(relative_drift),
        'r_squared': r_value ** 2,
        'drift_category': drift_category,
        'is_acceptable': max_drift < tolerance,
    }

    return results
