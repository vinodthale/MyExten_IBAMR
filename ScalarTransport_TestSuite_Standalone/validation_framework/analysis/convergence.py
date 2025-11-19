"""
Convergence Analysis Module
============================

Tools for computing and analyzing convergence rates.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from scipy import stats


def compute_convergence_rate(errors: List[float],
                             resolutions: List[float]) -> float:
    """
    Compute convergence rate from error vs resolution data.

    Assumes power law: error = C * h^p
    where p is the convergence order.

    Parameters:
    -----------
    errors : list of float
        Error values at different resolutions
    resolutions : list of float
        Grid resolutions (h = dx)

    Returns:
    --------
    float : Convergence rate (order of accuracy)
    """
    assert len(errors) == len(resolutions), "Arrays must have same length"
    assert len(errors) >= 2, "Need at least 2 data points"

    # Convert to numpy arrays and take log
    log_h = np.log(np.array(resolutions))
    log_e = np.log(np.array(errors))

    # Linear regression: log(e) = log(C) + p*log(h)
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_h, log_e)

    return slope


def analyze_convergence_series(errors: List[float],
                               resolutions: List[float]) -> Dict:
    """
    Perform comprehensive convergence analysis.

    Parameters:
    -----------
    errors : list of float
        Error values at different resolutions
    resolutions : list of float
        Grid resolutions (h = dx)

    Returns:
    --------
    dict : Convergence analysis results
    """
    assert len(errors) == len(resolutions), "Arrays must have same length"

    if len(errors) < 2:
        return {
            'convergence_rate': None,
            'error': 'Insufficient data points'
        }

    # Compute overall convergence rate
    log_h = np.log(np.array(resolutions))
    log_e = np.log(np.array(errors))

    slope, intercept, r_value, p_value, std_err = stats.linregress(log_h, log_e)

    # Compute pairwise convergence rates
    pairwise_rates = []
    for i in range(len(errors) - 1):
        rate = np.log(errors[i+1] / errors[i]) / np.log(resolutions[i+1] / resolutions[i])
        pairwise_rates.append(rate)

    results = {
        'convergence_rate': slope,
        'convergence_rate_std': std_err,
        'r_squared': r_value ** 2,
        'p_value': p_value,
        'pairwise_rates': pairwise_rates,
        'mean_pairwise_rate': np.mean(pairwise_rates),
        'std_pairwise_rate': np.std(pairwise_rates),
        'fit_constant': np.exp(intercept),
        'resolutions': resolutions,
        'errors': errors,
    }

    return results


def fit_convergence_order(errors: List[float],
                          resolutions: List[float],
                          expected_order: Optional[float] = None) -> Dict:
    """
    Fit convergence order and compare with expected.

    Parameters:
    -----------
    errors : list of float
        Error values
    resolutions : list of float
        Grid resolutions
    expected_order : float, optional
        Expected convergence order for comparison

    Returns:
    --------
    dict : Fitting results and comparison
    """
    results = analyze_convergence_series(errors, resolutions)

    if expected_order is not None:
        observed = results['convergence_rate']
        deviation = abs(observed - expected_order)
        relative_deviation = deviation / abs(expected_order) if expected_order != 0 else deviation

        results['expected_order'] = expected_order
        results['observed_order'] = observed
        results['deviation'] = deviation
        results['relative_deviation'] = relative_deviation
        results['within_tolerance'] = relative_deviation < 0.2  # 20% tolerance

    return results


def compute_richardson_extrapolation(f_fine: float,
                                     f_coarse: float,
                                     refinement_ratio: float,
                                     order: float) -> float:
    """
    Compute Richardson extrapolation estimate.

    f_exact ≈ (r^p * f_fine - f_coarse) / (r^p - 1)

    Parameters:
    -----------
    f_fine : float
        Solution on fine grid
    f_coarse : float
        Solution on coarse grid
    refinement_ratio : float
        Grid refinement ratio (h_coarse / h_fine)
    order : float
        Order of accuracy

    Returns:
    --------
    float : Extrapolated estimate
    """
    r_p = refinement_ratio ** order
    return (r_p * f_fine - f_coarse) / (r_p - 1)


def estimate_discretization_error(f_fine: float,
                                  f_medium: float,
                                  f_coarse: float,
                                  refinement_ratio: float = 2.0) -> Dict:
    """
    Estimate discretization error using three grid levels.

    Uses Grid Convergence Index (GCI) method.

    Parameters:
    -----------
    f_fine, f_medium, f_coarse : float
        Solutions on three successive grids
    refinement_ratio : float
        Grid refinement ratio between levels

    Returns:
    --------
    dict : Error estimates and convergence metrics
    """
    # Compute apparent order of accuracy
    epsilon_32 = f_coarse - f_medium
    epsilon_21 = f_medium - f_fine

    if abs(epsilon_21) < 1e-14 or abs(epsilon_32) < 1e-14:
        return {
            'apparent_order': None,
            'error': 'Solutions are identical, cannot estimate order'
        }

    # Use ln to handle cases where ratio might be negative
    r = refinement_ratio
    s = np.sign(epsilon_32 / epsilon_21)
    p = np.log(abs(epsilon_32 / epsilon_21)) / np.log(r)

    # Grid Convergence Index
    factor_safety = 1.25  # Safety factor
    GCI_fine = factor_safety * abs(epsilon_21) / (r**p - 1)

    results = {
        'apparent_order': p,
        'GCI_fine': GCI_fine,
        'extrapolated_value': f_fine + epsilon_21 / (r**p - 1),
        'relative_error_estimate': GCI_fine / abs(f_fine) if abs(f_fine) > 1e-14 else GCI_fine,
        'asymptotic_range': abs(GCI_fine / f_fine) < 0.05 if abs(f_fine) > 1e-14 else False,
    }

    return results


def compute_eoc_table(errors: List[float],
                     resolutions: List[float]) -> List[Dict]:
    """
    Compute Experimental Order of Convergence (EOC) table.

    Parameters:
    -----------
    errors : list of float
        Error values
    resolutions : list of float
        Grid resolutions

    Returns:
    --------
    list of dict : EOC table entries
    """
    table = []

    for i in range(len(errors)):
        entry = {
            'level': i,
            'resolution': resolutions[i],
            'error': errors[i],
        }

        if i > 0:
            h_ratio = resolutions[i] / resolutions[i-1]
            e_ratio = errors[i] / errors[i-1]
            eoc = np.log(e_ratio) / np.log(h_ratio)
            entry['eoc'] = eoc
            entry['reduction_factor'] = e_ratio
        else:
            entry['eoc'] = None
            entry['reduction_factor'] = None

        table.append(entry)

    return table


def assess_convergence_quality(convergence_rate: float,
                               r_squared: float,
                               expected_order: Optional[float] = None) -> Dict:
    """
    Assess quality of convergence.

    Parameters:
    -----------
    convergence_rate : float
        Observed convergence rate
    r_squared : float
        R² value from linear fit
    expected_order : float, optional
        Expected theoretical order

    Returns:
    --------
    dict : Quality assessment
    """
    assessment = {
        'convergence_rate': convergence_rate,
        'r_squared': r_squared,
    }

    # Assess fit quality
    if r_squared > 0.99:
        assessment['fit_quality'] = 'Excellent'
    elif r_squared > 0.95:
        assessment['fit_quality'] = 'Good'
    elif r_squared > 0.90:
        assessment['fit_quality'] = 'Fair'
    else:
        assessment['fit_quality'] = 'Poor'

    # Assess convergence
    if convergence_rate > 0.5:
        assessment['is_converging'] = True
        if convergence_rate >= 1.8:
            assessment['convergence_quality'] = 'Second-order or better'
        elif convergence_rate >= 0.8:
            assessment['convergence_quality'] = 'First-order'
        else:
            assessment['convergence_quality'] = 'Sub-linear'
    else:
        assessment['is_converging'] = False
        assessment['convergence_quality'] = 'Not converging'

    # Compare with expected if provided
    if expected_order is not None:
        deviation = abs(convergence_rate - expected_order)
        relative_dev = deviation / abs(expected_order) if expected_order != 0 else deviation

        assessment['expected_order'] = expected_order
        assessment['deviation'] = deviation
        assessment['relative_deviation'] = relative_dev

        if relative_dev < 0.1:
            assessment['matches_expected'] = 'Excellent'
        elif relative_dev < 0.2:
            assessment['matches_expected'] = 'Good'
        elif relative_dev < 0.3:
            assessment['matches_expected'] = 'Fair'
        else:
            assessment['matches_expected'] = 'Poor'

    return assessment
