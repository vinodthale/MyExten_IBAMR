"""
Field Analysis Module
=====================

Provides tools for loading, analyzing, and comparing scalar fields
from IBAMR simulations.
"""

import numpy as np
import h5py
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import re


class FieldAnalyzer:
    """Analyzes scalar fields from IBAMR simulation output"""

    def __init__(self, results_dir: str):
        """
        Initialize field analyzer.

        Parameters:
        -----------
        results_dir : str
            Path to test results directory
        """
        self.results_dir = Path(results_dir)
        self.raw_dir = self.results_dir / 'raw'
        self.fields = {}
        self.grid_info = {}

    def discover_fields(self) -> List[str]:
        """
        Discover all available field files.

        Returns:
        --------
        list : List of discovered field filenames
        """
        h5_files = list(self.raw_dir.glob('*.h5'))
        return [f.name for f in h5_files]

    def load_field(self, filename: str, variable: str = 'C') -> np.ndarray:
        """
        Load a scalar field from HDF5 file.

        Parameters:
        -----------
        filename : str
            HDF5 filename
        variable : str
            Variable name to load (default: 'C' for concentration)

        Returns:
        --------
        np.ndarray : Scalar field data
        """
        filepath = self.raw_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Field file not found: {filepath}")

        with h5py.File(filepath, 'r') as f:
            # Try to find the variable
            # IBAMR/VisIt output structure can vary
            if variable in f:
                data = f[variable][:]
            elif f'/{variable}' in f:
                data = f[f'/{variable}'][:]
            else:
                # Try to find it in common locations
                possible_paths = [
                    f'level_0/{variable}',
                    f'processor_0/{variable}',
                    f'patches/patch_0/{variable}',
                ]
                for path in possible_paths:
                    if path in f:
                        data = f[path][:]
                        break
                else:
                    # List available datasets
                    available = self._list_datasets(f)
                    raise KeyError(
                        f"Variable '{variable}' not found in {filename}. "
                        f"Available: {available}"
                    )

        self.fields[filename] = data
        return data

    def _list_datasets(self, h5_group, prefix='') -> List[str]:
        """Recursively list all datasets in HDF5 file"""
        datasets = []
        for key in h5_group.keys():
            item = h5_group[key]
            path = f"{prefix}/{key}" if prefix else key
            if isinstance(item, h5py.Dataset):
                datasets.append(path)
            elif isinstance(item, h5py.Group):
                datasets.extend(self._list_datasets(item, path))
        return datasets

    def extract_grid_info(self, filename: str) -> Dict:
        """
        Extract grid information from HDF5 file.

        Parameters:
        -----------
        filename : str
            HDF5 filename

        Returns:
        --------
        dict : Grid information (dimensions, spacing, etc.)
        """
        filepath = self.raw_dir / filename

        with h5py.File(filepath, 'r') as f:
            grid_info = {}

            # Try to extract grid metadata
            # This is highly dependent on IBAMR output format
            if 'extents' in f.attrs:
                grid_info['extents'] = f.attrs['extents']
            if 'dx' in f.attrs:
                grid_info['dx'] = f.attrs['dx']
            if 'dimensions' in f.attrs:
                grid_info['dimensions'] = f.attrs['dimensions']

            # Store for later use
            self.grid_info[filename] = grid_info

        return grid_info

    def compute_statistics(self, field: np.ndarray) -> Dict[str, float]:
        """
        Compute basic statistics for a scalar field.

        Parameters:
        -----------
        field : np.ndarray
            Scalar field data

        Returns:
        --------
        dict : Field statistics
        """
        stats = {
            'min': float(np.min(field)),
            'max': float(np.max(field)),
            'mean': float(np.mean(field)),
            'median': float(np.median(field)),
            'std': float(np.std(field)),
            'var': float(np.var(field)),
            'sum': float(np.sum(field)),
            'shape': field.shape,
            'size': field.size,
        }

        return stats


def load_scalar_field(filepath: str,
                     variable: str = 'C',
                     timestep: Optional[int] = None) -> np.ndarray:
    """
    Load a scalar field from file.

    Parameters:
    -----------
    filepath : str
        Path to field file (HDF5, CSV, or DAT)
    variable : str
        Variable name to load
    timestep : int, optional
        Specific timestep to load

    Returns:
    --------
    np.ndarray : Scalar field data
    """
    filepath = Path(filepath)

    if filepath.suffix == '.h5':
        return _load_hdf5_field(filepath, variable, timestep)
    elif filepath.suffix == '.csv':
        return _load_csv_field(filepath)
    elif filepath.suffix == '.dat':
        return _load_dat_field(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")


def _load_hdf5_field(filepath: Path,
                    variable: str,
                    timestep: Optional[int]) -> np.ndarray:
    """Load field from HDF5 file"""
    with h5py.File(filepath, 'r') as f:
        # Try various common paths
        paths_to_try = [
            variable,
            f'/{variable}',
            f'level_0/{variable}',
            f'processor_0/{variable}',
        ]

        for path in paths_to_try:
            if path in f:
                data = f[path][:]
                if timestep is not None and len(data.shape) > 0:
                    # If data has time dimension, extract specific timestep
                    if data.shape[0] > timestep:
                        return data[timestep]
                return data

        raise KeyError(f"Variable '{variable}' not found in {filepath}")


def _load_csv_field(filepath: Path) -> np.ndarray:
    """Load field from CSV file"""
    return np.loadtxt(filepath, delimiter=',')


def _load_dat_field(filepath: Path) -> np.ndarray:
    """Load field from DAT file"""
    return np.loadtxt(filepath)


def compute_field_difference(field1: np.ndarray,
                            field2: np.ndarray) -> np.ndarray:
    """
    Compute difference between two fields.

    Parameters:
    -----------
    field1, field2 : np.ndarray
        Scalar fields to compare

    Returns:
    --------
    np.ndarray : Difference field (field1 - field2)
    """
    assert field1.shape == field2.shape, "Fields must have same shape"
    return field1 - field2


def compute_field_statistics(field: np.ndarray) -> Dict[str, float]:
    """
    Compute comprehensive statistics for a field.

    Parameters:
    -----------
    field : np.ndarray
        Scalar field

    Returns:
    --------
    dict : Field statistics
    """
    stats = {
        'min': float(np.min(field)),
        'max': float(np.max(field)),
        'mean': float(np.mean(field)),
        'median': float(np.median(field)),
        'std': float(np.std(field)),
        'var': float(np.var(field)),
        'sum': float(np.sum(field)),
        'integral': float(np.sum(field)),  # Simplified - should include dx*dy*dz
        'percentile_05': float(np.percentile(field, 5)),
        'percentile_25': float(np.percentile(field, 25)),
        'percentile_75': float(np.percentile(field, 75)),
        'percentile_95': float(np.percentile(field, 95)),
    }

    return stats


def extract_slice_2d(field: np.ndarray,
                     axis: int,
                     index: int) -> np.ndarray:
    """
    Extract 2D slice from 3D field.

    Parameters:
    -----------
    field : np.ndarray
        3D scalar field
    axis : int
        Axis to slice (0=x, 1=y, 2=z)
    index : int
        Index along axis

    Returns:
    --------
    np.ndarray : 2D slice
    """
    if field.ndim != 3:
        raise ValueError(f"Field must be 3D, got {field.ndim}D")

    if axis == 0:
        return field[index, :, :]
    elif axis == 1:
        return field[:, index, :]
    elif axis == 2:
        return field[:, :, index]
    else:
        raise ValueError(f"Invalid axis: {axis}")


def extract_centerline(field: np.ndarray,
                       axis: int) -> np.ndarray:
    """
    Extract centerline profile along an axis.

    Parameters:
    -----------
    field : np.ndarray
        Scalar field (2D or 3D)
    axis : int
        Axis along which to extract (0=x, 1=y, 2=z)

    Returns:
    --------
    np.ndarray : Centerline profile
    """
    if field.ndim == 2:
        center_idx = [s // 2 for s in field.shape]
        if axis == 0:
            return field[:, center_idx[1]]
        elif axis == 1:
            return field[center_idx[0], :]
        else:
            raise ValueError(f"Invalid axis for 2D field: {axis}")

    elif field.ndim == 3:
        center_idx = [s // 2 for s in field.shape]
        if axis == 0:
            return field[:, center_idx[1], center_idx[2]]
        elif axis == 1:
            return field[center_idx[0], :, center_idx[2]]
        elif axis == 2:
            return field[center_idx[0], center_idx[1], :]
        else:
            raise ValueError(f"Invalid axis: {axis}")

    else:
        raise ValueError(f"Unsupported field dimension: {field.ndim}")
