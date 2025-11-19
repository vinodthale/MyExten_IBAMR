"""
Error Plotting Module
=====================

Visualization tools for error analysis.
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Set publication-quality defaults
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.figsize'] = (8, 6)


def plot_error_vs_time(times: List[float],
                       errors: Dict[str, List[float]],
                       output_path: str,
                       title: str = "Error vs Time",
                       log_scale: bool = True):
    """
    Plot error metrics vs time.

    Parameters:
    -----------
    times : list of float
        Time values
    errors : dict
        Dictionary with error types as keys, lists of errors as values
        Example: {'L1': [...], 'L2': [...], 'Linf': [...]}
    output_path : str
        Path to save figure
    title : str
        Plot title
    log_scale : bool
        Use log scale for y-axis
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    markers = ['o', 's', '^', 'v', 'D', '*']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

    for i, (error_type, error_values) in enumerate(errors.items()):
        marker = markers[i % len(markers)]
        color = colors[i % len(colors)]
        ax.plot(times, error_values, marker=marker, label=error_type,
                linewidth=2, markersize=6, color=color, alpha=0.8)

    ax.set_xlabel('Time', fontweight='bold')
    ax.set_ylabel('Error', fontweight='bold')
    ax.set_title(title, fontweight='bold', fontsize=14)

    if log_scale:
        ax.set_yscale('log')

    ax.legend(loc='best', frameon=True, shadow=True)
    ax.grid(True, which='both', linestyle='--', alpha=0.3)

    plt.tight_layout()

    # Save as both PNG and PDF
    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_error_vs_resolution(resolutions: List[float],
                             errors: Dict[str, List[float]],
                             output_path: str,
                             title: str = "Error vs Grid Resolution",
                             convergence_rates: Optional[Dict[str, float]] = None):
    """
    Plot error vs grid resolution (convergence plot).

    Parameters:
    -----------
    resolutions : list of float
        Grid resolutions (h = dx)
    errors : dict
        Dictionary with error types as keys
    output_path : str
        Path to save figure
    title : str
        Plot title
    convergence_rates : dict, optional
        Convergence rates to display
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    markers = ['o', 's', '^', 'v', 'D', '*']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

    for i, (error_type, error_values) in enumerate(errors.items()):
        marker = markers[i % len(markers)]
        color = colors[i % len(colors)]

        label = error_type
        if convergence_rates and error_type in convergence_rates:
            rate = convergence_rates[error_type]
            label = f"{error_type} (order ≈ {rate:.2f})"

        ax.loglog(resolutions, error_values, marker=marker, label=label,
                  linewidth=2, markersize=8, color=color, alpha=0.8)

    # Add reference lines for common orders
    h_min, h_max = min(resolutions), max(resolutions)
    e_ref = errors[list(errors.keys())[0]][0]  # Reference error

    # First order reference
    h_ref = np.array([h_min, h_max])
    e_first = e_ref * (h_ref / h_min)
    ax.loglog(h_ref, e_first, 'k--', alpha=0.4, linewidth=1.5, label='1st order')

    # Second order reference
    e_second = e_ref * (h_ref / h_min)**2
    ax.loglog(h_ref, e_second, 'k:', alpha=0.4, linewidth=1.5, label='2nd order')

    ax.set_xlabel('Grid Resolution h', fontweight='bold')
    ax.set_ylabel('Error', fontweight='bold')
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.legend(loc='best', frameon=True, shadow=True)
    ax.grid(True, which='both', linestyle='--', alpha=0.3)

    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_error_comparison(test_names: List[str],
                         errors: List[float],
                         output_path: str,
                         error_type: str = "L2",
                         title: Optional[str] = None):
    """
    Create bar chart comparing errors across multiple tests.

    Parameters:
    -----------
    test_names : list of str
        Names of tests
    errors : list of float
        Error values for each test
    output_path : str
        Path to save figure
    error_type : str
        Type of error being plotted
    title : str, optional
        Plot title
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(test_names))
    bars = ax.bar(x, errors, color='steelblue', alpha=0.8, edgecolor='black', linewidth=1.5)

    # Color code: green for small errors, yellow for medium, red for large
    for i, (bar, error) in enumerate(zip(bars, errors)):
        if error < 1e-4:
            bar.set_color('#2ca02c')  # Green
        elif error < 1e-2:
            bar.set_color('#ff7f0e')  # Orange
        else:
            bar.set_color('#d62728')  # Red

    ax.set_xlabel('Test', fontweight='bold')
    ax.set_ylabel(f'{error_type} Error', fontweight='bold')

    if title is None:
        title = f'{error_type} Error Comparison Across Tests'
    ax.set_title(title, fontweight='bold', fontsize=14)

    ax.set_xticks(x)
    ax.set_xticklabels(test_names, rotation=45, ha='right')
    ax.set_yscale('log')
    ax.grid(True, which='both', axis='y', linestyle='--', alpha=0.3)

    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_error_statistics(error_stats: Dict[str, float],
                         output_path: str,
                         title: str = "Error Statistics"):
    """
    Plot error statistics (mean, max, percentiles, etc.).

    Parameters:
    -----------
    error_stats : dict
        Dictionary of error statistics
    output_path : str
        Path to save figure
    title : str
        Plot title
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Box plot style visualization
    stats_to_plot = {
        'Mean': error_stats.get('mean_abs_error', 0),
        'Median': error_stats.get('median_abs_error', 0),
        'RMS': error_stats.get('rms_error', 0),
        'Max': error_stats.get('max_abs_error', 0),
        '95th %ile': error_stats.get('percentile_95', 0),
    }

    x = np.arange(len(stats_to_plot))
    bars = ax1.bar(x, list(stats_to_plot.values()), color='steelblue', alpha=0.8,
                   edgecolor='black', linewidth=1.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(list(stats_to_plot.keys()))
    ax1.set_ylabel('Error Magnitude', fontweight='bold')
    ax1.set_title('Error Statistics', fontweight='bold')
    ax1.set_yscale('log')
    ax1.grid(True, axis='y', linestyle='--', alpha=0.3)

    # Percentile distribution
    percentiles = [0, 25, 50, 75, 95, 99, 100]
    percentile_values = []

    for p in percentiles:
        key = f'percentile_{p:02d}' if p < 100 else 'max_abs_error'
        if p == 0:
            key = 'min_error'
        if p == 50:
            key = 'median_abs_error'

        percentile_values.append(error_stats.get(key, 0))

    ax2.plot(percentiles, percentile_values, marker='o', linewidth=2,
             markersize=8, color='steelblue', alpha=0.8)
    ax2.set_xlabel('Percentile', fontweight='bold')
    ax2.set_ylabel('Error Value', fontweight='bold')
    ax2.set_title('Error Distribution', fontweight='bold')
    ax2.set_yscale('log')
    ax2.grid(True, linestyle='--', alpha=0.3)

    plt.suptitle(title, fontweight='bold', fontsize=14, y=1.02)
    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_multi_error_timeline(times: List[float],
                              errors_dict: Dict[str, Dict[str, List[float]]],
                              output_path: str,
                              title: str = "Error Evolution"):
    """
    Plot multiple error types for multiple tests on the same timeline.

    Parameters:
    -----------
    times : list of float
        Time values
    errors_dict : dict
        Nested dict: {test_name: {error_type: [values]}}
    output_path : str
        Path to save figure
    title : str
        Plot title
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    error_types = ['L1', 'L2', 'Linf', 'RMS']

    for i, error_type in enumerate(error_types):
        ax = axes[i]

        for test_name, errors in errors_dict.items():
            if error_type in errors:
                ax.plot(times, errors[error_type], marker='o', label=test_name,
                        linewidth=2, markersize=4, alpha=0.8)

        ax.set_xlabel('Time', fontweight='bold')
        ax.set_ylabel(f'{error_type} Error', fontweight='bold')
        ax.set_title(f'{error_type} Error vs Time', fontweight='bold')
        ax.set_yscale('log')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, which='both', linestyle='--', alpha=0.3)

    plt.suptitle(title, fontweight='bold', fontsize=16, y=0.995)
    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()
