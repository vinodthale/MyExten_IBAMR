"""
Convergence Plotting Module
============================

Visualization tools for convergence analysis.
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional

plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300


def plot_convergence_rate(resolutions: List[float],
                          errors: List[float],
                          output_path: str,
                          convergence_rate: float,
                          title: str = "Convergence Analysis",
                          error_label: str = "Error",
                          expected_order: Optional[float] = None):
    """
    Plot convergence rate with fitted line.

    Parameters:
    -----------
    resolutions : list of float
        Grid resolutions (h)
    errors : list of float
        Error values
    output_path : str
        Path to save figure
    convergence_rate : float
        Computed convergence rate
    title : str
        Plot title
    error_label : str
        Label for error type
    expected_order : float, optional
        Expected theoretical order
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot data points
    ax.loglog(resolutions, errors, 'bo', markersize=10, label='Computed',
             markeredgecolor='black', markeredgewidth=1.5, alpha=0.8)

    # Plot fitted line
    h = np.array(resolutions)
    # Compute fitted line: e = C * h^p
    log_h = np.log(h)
    log_e = np.log(np.array(errors))
    p = convergence_rate
    C = np.exp(np.mean(log_e - p * log_h))

    h_fit = np.logspace(np.log10(min(h)), np.log10(max(h)), 100)
    e_fit = C * h_fit**p

    ax.loglog(h_fit, e_fit, 'b-', linewidth=2, alpha=0.6,
             label=f'Fitted: order = {p:.2f}')

    # Plot expected order if provided
    if expected_order is not None:
        e_expected = C * h_fit**expected_order
        ax.loglog(h_fit, e_expected, 'r--', linewidth=2, alpha=0.6,
                 label=f'Expected: order = {expected_order:.2f}')

    # Add reference lines
    h_ref = np.array([min(h), max(h)])
    for order, style, alpha in [(1, ':', 0.3), (2, ':', 0.3)]:
        e_ref = errors[0] * (h_ref / h[0])**order
        ax.loglog(h_ref, e_ref, 'k' + style, linewidth=1, alpha=alpha,
                 label=f'Order {order}' if order <= 2 else None)

    ax.set_xlabel('Grid Resolution h', fontweight='bold', fontsize=12)
    ax.set_ylabel(f'{error_label}', fontweight='bold', fontsize=12)
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.legend(loc='best', fontsize=10, frameon=True, shadow=True)
    ax.grid(True, which='both', linestyle='--', alpha=0.3)

    # Add text box with convergence info
    textstr = f'Convergence Rate: {p:.3f}'
    if expected_order is not None:
        deviation = abs(p - expected_order)
        textstr += f'\nExpected: {expected_order:.3f}'
        textstr += f'\nDeviation: {deviation:.3f}'

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
           verticalalignment='top', bbox=props)

    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_eoc_table(eoc_data: List[Dict],
                  output_path: str,
                  title: str = "Experimental Order of Convergence"):
    """
    Visualize EOC table.

    Parameters:
    -----------
    eoc_data : list of dict
        EOC table data from convergence analysis
    output_path : str
        Path to save figure
    title : str
        Plot title
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    levels = [d['level'] for d in eoc_data]
    resolutions = [d['resolution'] for d in eoc_data]
    errors = [d['error'] for d in eoc_data]
    eocs = [d['eoc'] if d['eoc'] is not None else 0 for d in eoc_data]

    # Plot 1: Error vs level
    ax1.semilogy(levels, errors, 'bo-', markersize=8, linewidth=2,
                markeredgecolor='black', markeredgewidth=1.5, alpha=0.8)
    ax1.set_xlabel('Refinement Level', fontweight='bold')
    ax1.set_ylabel('Error', fontweight='bold')
    ax1.set_title('Error Reduction', fontweight='bold')
    ax1.grid(True, which='both', linestyle='--', alpha=0.3)

    # Plot 2: EOC vs level
    eoc_plot = [eoc for eoc in eocs if eoc != 0]
    level_plot = levels[1:len(eoc_plot)+1]

    ax2.plot(level_plot, eoc_plot, 'rs-', markersize=8, linewidth=2,
            markeredgecolor='black', markeredgewidth=1.5, alpha=0.8,
            label='Computed EOC')

    # Add reference lines for orders 1 and 2
    ax2.axhline(y=1.0, color='k', linestyle=':', alpha=0.3, label='1st order')
    ax2.axhline(y=2.0, color='k', linestyle='--', alpha=0.3, label='2nd order')

    ax2.set_xlabel('Refinement Level', fontweight='bold')
    ax2.set_ylabel('EOC (Experimental Order of Convergence)', fontweight='bold')
    ax2.set_title('Convergence Order', fontweight='bold')
    ax2.legend(loc='best')
    ax2.grid(True, linestyle='--', alpha=0.3)

    plt.suptitle(title, fontweight='bold', fontsize=14, y=0.98)
    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_richardson_extrapolation(resolutions: List[float],
                                  solutions: List[float],
                                  extrapolated: float,
                                  output_path: str,
                                  title: str = "Richardson Extrapolation"):
    """
    Visualize Richardson extrapolation.

    Parameters:
    -----------
    resolutions : list of float
        Grid resolutions
    solutions : list of float
        Solutions at each resolution
    extrapolated : float
        Richardson extrapolated value
    output_path : str
        Path to save figure
    title : str
        Plot title
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    # Plot solutions vs 1/N (or h)
    h = np.array(resolutions)
    ax.plot(h, solutions, 'bo-', markersize=10, linewidth=2,
           markeredgecolor='black', markeredgewidth=1.5, alpha=0.8,
           label='Computed Solutions')

    # Plot extrapolated value
    ax.axhline(y=extrapolated, color='r', linestyle='--', linewidth=2,
              alpha=0.7, label=f'Extrapolated: {extrapolated:.6f}')

    # Fit and plot trend line
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(h, solutions)
    h_fit = np.linspace(0, max(h), 100)
    fit_line = slope * h_fit + intercept
    ax.plot(h_fit, fit_line, 'g:', linewidth=1.5, alpha=0.5,
           label=f'Linear fit (R² = {r_value**2:.4f})')

    ax.set_xlabel('Grid Resolution h', fontweight='bold')
    ax.set_ylabel('Solution Value', fontweight='bold')
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.legend(loc='best', frameon=True, shadow=True)
    ax.grid(True, linestyle='--', alpha=0.3)

    # Add text box with extrapolation info
    textstr = f'Extrapolated value: {extrapolated:.6e}\n'
    textstr += f'Finest grid value: {solutions[-1]:.6e}\n'
    textstr += f'Difference: {abs(extrapolated - solutions[-1]):.6e}'

    props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
    ax.text(0.95, 0.05, textstr, transform=ax.transAxes, fontsize=10,
           verticalalignment='bottom', horizontalalignment='right', bbox=props)

    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_multi_convergence(convergence_data: Dict[str, Dict],
                          output_path: str,
                          title: str = "Multi-Test Convergence Comparison"):
    """
    Plot convergence for multiple tests/error types.

    Parameters:
    -----------
    convergence_data : dict
        Dict of {test_name: {'resolutions': [...], 'errors': [...], 'rate': ...}}
    output_path : str
        Path to save figure
    title : str
        Plot title
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    markers = ['o', 's', '^', 'v', 'D', '*', 'p', 'h']
    colors = plt.cm.tab10(np.linspace(0, 1, len(convergence_data)))

    for i, (test_name, data) in enumerate(convergence_data.items()):
        h = data['resolutions']
        e = data['errors']
        rate = data.get('rate', None)

        marker = markers[i % len(markers)]
        color = colors[i]

        label = test_name
        if rate is not None:
            label += f' (p={rate:.2f})'

        ax.loglog(h, e, marker=marker, color=color, linewidth=2,
                 markersize=8, label=label, alpha=0.8,
                 markeredgecolor='black', markeredgewidth=1)

    # Add reference lines
    h_range = [ax.get_xlim()[0], ax.get_xlim()[1]]
    e_ref = ax.get_ylim()[1]

    for order in [1, 2]:
        e_line = [e_ref, e_ref * (h_range[1]/h_range[0])**order]
        ax.loglog(h_range, e_line, 'k:', alpha=0.3, linewidth=1,
                 label=f'Order {order}' if order == 1 else f'Order {order}')

    ax.set_xlabel('Grid Resolution h', fontweight='bold', fontsize=12)
    ax.set_ylabel('Error', fontweight='bold', fontsize=12)
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.legend(loc='best', fontsize=9, ncol=2, frameon=True, shadow=True)
    ax.grid(True, which='both', linestyle='--', alpha=0.3)

    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()
