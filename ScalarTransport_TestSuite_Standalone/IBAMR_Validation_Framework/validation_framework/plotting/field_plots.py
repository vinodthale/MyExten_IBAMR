"""
Field Plotting Module
=====================

Visualization tools for scalar field data.
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List
import matplotlib.colors as mcolors

plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300


def plot_scalar_field_2d(field: np.ndarray,
                         output_path: str,
                         title: str = "Scalar Field",
                         xlabel: str = "X",
                         ylabel: str = "Y",
                         colorbar_label: str = "Value",
                         vmin: Optional[float] = None,
                         vmax: Optional[float] = None,
                         cmap: str = 'viridis'):
    """
    Plot 2D scalar field as colormap.

    Parameters:
    -----------
    field : np.ndarray
        2D scalar field
    output_path : str
        Path to save figure
    title : str
        Plot title
    xlabel, ylabel : str
        Axis labels
    colorbar_label : str
        Colorbar label
    vmin, vmax : float, optional
        Color scale limits
    cmap : str
        Colormap name
    """
    if field.ndim != 2:
        raise ValueError(f"Field must be 2D, got {field.ndim}D")

    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(field.T, origin='lower', aspect='auto',
                   cmap=cmap, vmin=vmin, vmax=vmax,
                   interpolation='bilinear')

    ax.set_xlabel(xlabel, fontweight='bold')
    ax.set_ylabel(ylabel, fontweight='bold')
    ax.set_title(title, fontweight='bold', fontsize=14)

    cbar = plt.colorbar(im, ax=ax, label=colorbar_label)
    cbar.ax.set_ylabel(colorbar_label, fontweight='bold')

    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_scalar_field_contour(field: np.ndarray,
                              output_path: str,
                              title: str = "Scalar Field Contours",
                              xlabel: str = "X",
                              ylabel: str = "Y",
                              num_levels: int = 20,
                              filled: bool = True,
                              cmap: str = 'viridis'):
    """
    Plot 2D scalar field as contours.

    Parameters:
    -----------
    field : np.ndarray
        2D scalar field
    output_path : str
        Path to save figure
    title : str
        Plot title
    xlabel, ylabel : str
        Axis labels
    num_levels : int
        Number of contour levels
    filled : bool
        Use filled contours
    cmap : str
        Colormap name
    """
    if field.ndim != 2:
        raise ValueError(f"Field must be 2D, got {field.ndim}D")

    fig, ax = plt.subplots(figsize=(10, 8))

    ny, nx = field.shape
    x = np.arange(nx)
    y = np.arange(ny)
    X, Y = np.meshgrid(x, y)

    if filled:
        cs = ax.contourf(X, Y, field, levels=num_levels, cmap=cmap)
        # Add contour lines
        ax.contour(X, Y, field, levels=num_levels, colors='k',
                  linewidths=0.5, alpha=0.3)
    else:
        cs = ax.contour(X, Y, field, levels=num_levels, cmap=cmap)
        ax.clabel(cs, inline=True, fontsize=8)

    ax.set_xlabel(xlabel, fontweight='bold')
    ax.set_ylabel(ylabel, fontweight='bold')
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.set_aspect('equal')

    cbar = plt.colorbar(cs, ax=ax)
    cbar.ax.set_ylabel('Field Value', fontweight='bold')

    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_field_slice(field: np.ndarray,
                    output_path: str,
                    axis: int = 2,
                    slice_index: Optional[int] = None,
                    title: str = "Field Slice",
                    cmap: str = 'viridis'):
    """
    Plot slice of 3D field.

    Parameters:
    -----------
    field : np.ndarray
        3D scalar field
    output_path : str
        Path to save figure
    axis : int
        Axis perpendicular to slice (0=x, 1=y, 2=z)
    slice_index : int, optional
        Index of slice (default: middle)
    title : str
        Plot title
    cmap : str
        Colormap name
    """
    if field.ndim != 3:
        raise ValueError(f"Field must be 3D, got {field.ndim}D")

    if slice_index is None:
        slice_index = field.shape[axis] // 2

    # Extract slice
    if axis == 0:
        slice_data = field[slice_index, :, :]
        xlabel, ylabel = "Y", "Z"
    elif axis == 1:
        slice_data = field[:, slice_index, :]
        xlabel, ylabel = "X", "Z"
    elif axis == 2:
        slice_data = field[:, :, slice_index]
        xlabel, ylabel = "X", "Y"
    else:
        raise ValueError(f"Invalid axis: {axis}")

    plot_scalar_field_2d(slice_data, output_path,
                        title=f"{title} (axis={axis}, index={slice_index})",
                        xlabel=xlabel, ylabel=ylabel, cmap=cmap)


def plot_field_difference(field1: np.ndarray,
                         field2: np.ndarray,
                         output_path: str,
                         title: str = "Field Difference",
                         xlabel: str = "X",
                         ylabel: str = "Y",
                         log_scale: bool = False,
                         cmap: str = 'RdBu_r'):
    """
    Plot difference between two fields.

    Parameters:
    -----------
    field1, field2 : np.ndarray
        Scalar fields to compare
    output_path : str
        Path to save figure
    title : str
        Plot title
    xlabel, ylabel : str
        Axis labels
    log_scale : bool
        Use log scale for difference
    cmap : str
        Colormap (diverging recommended)
    """
    if field1.shape != field2.shape:
        raise ValueError("Fields must have same shape")

    if field1.ndim != 2:
        raise ValueError(f"Fields must be 2D, got {field1.ndim}D")

    diff = field1 - field2

    if log_scale:
        diff_plot = np.log10(np.abs(diff) + 1e-14)
        colorbar_label = "log₁₀|Difference|"
    else:
        diff_plot = diff
        colorbar_label = "Difference"

    # Make symmetric color scale for non-log
    if not log_scale:
        vmax = np.max(np.abs(diff))
        vmin = -vmax
    else:
        vmin, vmax = None, None

    plot_scalar_field_2d(diff_plot, output_path, title=title,
                        xlabel=xlabel, ylabel=ylabel,
                        colorbar_label=colorbar_label,
                        vmin=vmin, vmax=vmax, cmap=cmap)


def plot_centerline_profile(field: np.ndarray,
                           output_path: str,
                           axis: int = 0,
                           title: str = "Centerline Profile",
                           exact: Optional[np.ndarray] = None):
    """
    Plot centerline profile of field.

    Parameters:
    -----------
    field : np.ndarray
        Scalar field (2D or 3D)
    output_path : str
        Path to save figure
    axis : int
        Axis along which to extract profile
    title : str
        Plot title
    exact : np.ndarray, optional
        Exact solution for comparison
    """
    # Extract centerline
    if field.ndim == 2:
        center_idx = [s // 2 for s in field.shape]
        if axis == 0:
            profile = field[:, center_idx[1]]
            xlabel = "X"
        else:
            profile = field[center_idx[0], :]
            xlabel = "Y"

    elif field.ndim == 3:
        center_idx = [s // 2 for s in field.shape]
        if axis == 0:
            profile = field[:, center_idx[1], center_idx[2]]
            xlabel = "X"
        elif axis == 1:
            profile = field[center_idx[0], :, center_idx[2]]
            xlabel = "Y"
        else:
            profile = field[center_idx[0], center_idx[1], :]
            xlabel = "Z"
    else:
        raise ValueError(f"Unsupported field dimension: {field.ndim}")

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(profile))
    ax.plot(x, profile, 'b-', linewidth=2, label='Computed', marker='o',
            markersize=4, alpha=0.8)

    if exact is not None:
        ax.plot(x, exact, 'r--', linewidth=2, label='Exact', alpha=0.8)

        # Also plot error
        ax2 = ax.twinx()
        error = np.abs(profile - exact)
        ax2.plot(x, error, 'g:', linewidth=1.5, label='|Error|', alpha=0.6)
        ax2.set_ylabel('Absolute Error', fontweight='bold', color='g')
        ax2.tick_params(axis='y', labelcolor='g')
        ax2.set_yscale('log')

    ax.set_xlabel(xlabel, fontweight='bold')
    ax.set_ylabel('Field Value', fontweight='bold')
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.legend(loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.3)

    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_field_heatmap(field: np.ndarray,
                      output_path: str,
                      title: str = "Field Heatmap",
                      cmap: str = 'hot',
                      annotate: bool = False):
    """
    Plot field as heatmap with optional annotations.

    Parameters:
    -----------
    field : np.ndarray
        2D scalar field
    output_path : str
        Path to save figure
    title : str
        Plot title
    cmap : str
        Colormap name
    annotate : bool
        Annotate cells with values
    """
    if field.ndim != 2:
        raise ValueError(f"Field must be 2D, got {field.ndim}D")

    fig, ax = plt.subplots(figsize=(12, 10))

    im = ax.imshow(field.T, origin='lower', aspect='auto',
                   cmap=cmap, interpolation='nearest')

    if annotate and field.size < 400:  # Only annotate for small grids
        for i in range(field.shape[0]):
            for j in range(field.shape[1]):
                text = ax.text(i, j, f'{field[i, j]:.2e}',
                             ha="center", va="center", color="w", fontsize=6)

    ax.set_title(title, fontweight='bold', fontsize=14)
    cbar = plt.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Field Value', fontweight='bold')

    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()


def plot_field_comparison_grid(fields: List[Tuple[np.ndarray, str]],
                               output_path: str,
                               title: str = "Field Comparison",
                               cmap: str = 'viridis',
                               share_scale: bool = True):
    """
    Plot multiple fields in a grid for comparison.

    Parameters:
    -----------
    fields : list of (np.ndarray, str)
        List of (field, label) tuples
    output_path : str
        Path to save figure
    title : str
        Overall title
    cmap : str
        Colormap name
    share_scale : bool
        Use same color scale for all fields
    """
    n_fields = len(fields)
    ncols = min(3, n_fields)
    nrows = (n_fields + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(6*ncols, 5*nrows))

    if n_fields == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    if share_scale:
        vmin = min(np.min(f[0]) for f in fields)
        vmax = max(np.max(f[0]) for f in fields)
    else:
        vmin, vmax = None, None

    for i, (field, label) in enumerate(fields):
        im = axes[i].imshow(field.T, origin='lower', aspect='auto',
                          cmap=cmap, vmin=vmin, vmax=vmax, interpolation='bilinear')
        axes[i].set_title(label, fontweight='bold')
        plt.colorbar(im, ax=axes[i])

    # Hide unused subplots
    for i in range(n_fields, len(axes)):
        axes[i].axis('off')

    plt.suptitle(title, fontweight='bold', fontsize=16, y=0.995)
    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix('.png'), bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close()
