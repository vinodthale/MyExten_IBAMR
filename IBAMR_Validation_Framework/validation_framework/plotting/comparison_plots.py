"""
Comparison Plotting Module
===========================

Tools for comparing fields and results across tests.
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional

plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300


def plot_field_comparison(computed: np.ndarray,
                          exact: np.ndarray,
                          output_path: str,
                          title: str = "Field Comparison"):
    """
    Side-by-side comparison of computed vs exact fields.

    Parameters:
    -----------
    computed, exact : np.ndarray
        Computed and exact 2D fields
    output_path : str
        Path to save figure
    title : str
        Plot title
    """
    if computed.shape != exact.shape:
        raise ValueError("Fields must have same shape")

    if computed.ndim != 2:
        raise ValueError(f"Fields must be 2D, got {computed.ndim}D")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Find common color scale
    vmin = min(np.min(computed), np.min(exact))
    vmax = max(np.max(computed), np.max(exact))

    # Computed field
    im1 = axes[0].imshow(computed.T, origin='lower', aspect='auto',
                        vmin=vmin, vmax=vmax, cmap='viridis')
    axes[0].set_title('Computed', fontweight='bold')
    plt.colorbar(im1, ax=axes[0])

    # Exact field
    im2 = axes[1].imshow(exact.T, origin='lower', aspect='auto',
                        vmin=vmin, vmax=vmax, cmap='viridis')
    axes[1].set_title('Exact', fontweight='bold')
    plt.colorbar(im2, ax=axes[1])

    # Difference
    diff = np.abs(computed - exact)
    im3 = axes[2].imshow(diff.T, origin='lower', aspect='auto', cmap='hot')
    axes[2].set_title('Absolute Difference', fontweight='bold')
    plt.colorbar(im3, ax=axes[2])

    plt.suptitle(title, fontweight='bold', fontsize=16, y=0.98)
    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_multiple_fields(fields: List[Tuple[np.ndarray, str]],
                        output_path: str,
                        title: str = "Field Comparison",
                        cmap: str = 'viridis',
                        same_scale: bool = True):
    """
    Plot multiple fields for comparison.

    Parameters:
    -----------
    fields : list of (field, label) tuples
        Fields to plot with labels
    output_path : str
        Path to save figure
    title : str
        Overall title
    cmap : str
        Colormap
    same_scale : bool
        Use same color scale for all
    """
    n = len(fields)
    ncols = min(4, n)
    nrows = (n + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(5*ncols, 4*nrows))

    if n == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    if same_scale:
        all_fields = [f[0] for f in fields]
        vmin = min(np.min(f) for f in all_fields)
        vmax = max(np.max(f) for f in all_fields)
    else:
        vmin, vmax = None, None

    for i, (field, label) in enumerate(fields):
        im = axes[i].imshow(field.T, origin='lower', aspect='auto',
                          cmap=cmap, vmin=vmin, vmax=vmax)
        axes[i].set_title(label, fontweight='bold')
        plt.colorbar(im, ax=axes[i])

    # Hide unused axes
    for i in range(n, len(axes)):
        axes[i].axis('off')

    plt.suptitle(title, fontweight='bold', fontsize=16, y=0.995)
    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_heatmap_comparison(data_dict: Dict[str, float],
                           output_path: str,
                           title: str = "Test Results Heatmap",
                           vmin: Optional[float] = None,
                           vmax: Optional[float] = None):
    """
    Create heatmap comparing results across multiple tests/metrics.

    Parameters:
    -----------
    data_dict : dict
        Nested dict {test_name: {metric: value}}
    output_path : str
        Path to save figure
    title : str
        Plot title
    vmin, vmax : float, optional
        Color scale limits
    """
    # Convert to matrix
    test_names = list(data_dict.keys())
    metric_names = list(data_dict[test_names[0]].keys())

    matrix = np.zeros((len(test_names), len(metric_names)))
    for i, test in enumerate(test_names):
        for j, metric in enumerate(metric_names):
            matrix[i, j] = data_dict[test].get(metric, 0)

    fig, ax = plt.subplots(figsize=(12, max(6, len(test_names) * 0.5)))

    im = ax.imshow(matrix, aspect='auto', cmap='RdYlGn_r', vmin=vmin, vmax=vmax)

    # Set ticks and labels
    ax.set_xticks(np.arange(len(metric_names)))
    ax.set_yticks(np.arange(len(test_names)))
    ax.set_xticklabels(metric_names, rotation=45, ha='right')
    ax.set_yticklabels(test_names)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Error Value', fontweight='bold')

    # Add text annotations
    for i in range(len(test_names)):
        for j in range(len(metric_names)):
            text = ax.text(j, i, f'{matrix[i, j]:.2e}',
                          ha="center", va="center", color="black", fontsize=8)

    ax.set_title(title, fontweight='bold', fontsize=14, pad=20)
    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_test_summary(test_results: Dict[str, Dict],
                     output_path: str,
                     title: str = "Test Suite Summary"):
    """
    Create comprehensive summary visualization.

    Parameters:
    -----------
    test_results : dict
        Dict of {test_name: {metric: value}}
    output_path : str
        Path to save figure
    title : str
        Plot title
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    test_names = list(test_results.keys())
    n_tests = len(test_names)

    # Extract common metrics
    l2_errors = [test_results[t].get('L2', 0) for t in test_names]
    linf_errors = [test_results[t].get('Linf', 0) for t in test_names]
    mass_errors = [test_results[t].get('mass_error', 0) for t in test_names]
    convergence_rates = [test_results[t].get('convergence_rate', 0) for t in test_names]

    x = np.arange(n_tests)

    # Plot 1: L2 errors
    axes[0, 0].bar(x, l2_errors, color='steelblue', alpha=0.8, edgecolor='black')
    axes[0, 0].set_ylabel('L2 Error', fontweight='bold')
    axes[0, 0].set_title('L2 Error by Test', fontweight='bold')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    axes[0, 0].set_yscale('log')
    axes[0, 0].grid(True, axis='y', linestyle='--', alpha=0.3)

    # Plot 2: Linf errors
    axes[0, 1].bar(x, linf_errors, color='coral', alpha=0.8, edgecolor='black')
    axes[0, 1].set_ylabel('L∞ Error', fontweight='bold')
    axes[0, 1].set_title('L∞ Error by Test', fontweight='bold')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    axes[0, 1].set_yscale('log')
    axes[0, 1].grid(True, axis='y', linestyle='--', alpha=0.3)

    # Plot 3: Mass conservation
    axes[1, 0].bar(x, np.abs(mass_errors), color='seagreen', alpha=0.8, edgecolor='black')
    axes[1, 0].set_ylabel('|Mass Error|', fontweight='bold')
    axes[1, 0].set_title('Mass Conservation by Test', fontweight='bold')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    axes[1, 0].set_yscale('log')
    axes[1, 0].grid(True, axis='y', linestyle='--', alpha=0.3)

    # Plot 4: Convergence rates
    axes[1, 1].bar(x, convergence_rates, color='purple', alpha=0.8, edgecolor='black')
    axes[1, 1].axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='1st order')
    axes[1, 1].axhline(y=2.0, color='g', linestyle='--', alpha=0.5, label='2nd order')
    axes[1, 1].set_ylabel('Convergence Rate', fontweight='bold')
    axes[1, 1].set_title('Convergence Rate by Test', fontweight='bold')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    axes[1, 1].legend()
    axes[1, 1].grid(True, axis='y', linestyle='--', alpha=0.3)

    plt.suptitle(title, fontweight='bold', fontsize=16, y=0.995)
    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()
