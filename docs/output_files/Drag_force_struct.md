# <basename>_Drag_force_struct_no_N

## File Overview

**Filename pattern:** `Eel2d_Drag_force_struct_no_0.curve`, `Foil_Drag_force_struct_no_1.curve`, ...
**Created by:** `ConstraintIBMethod` (alternative force calculation)
**Size:** ~2-4 MB for typical simulation
**Format:** Tab-separated values (TSV)
**Note:** `.curve` extension (Lagrangian structure output)

## Purpose

This file contains **hydrodynamic forces computed directly on the Lagrangian structure** (alternative to control volume method). It can be used for **cross-validation** with the control volume forces.

## File Format

### Column Structure

| Column | Name | Units | Description |
|--------|------|-------|-------------|
| 1 | `time` | seconds | Simulation time |
| 2 | `Fx` | N (or non-dim) | Force in x-direction |
| 3 | `Fy` | N (or non-dim) | Force in y-direction |
| 4 | `Fz` | N (or non-dim) | Force in z-direction (0 for 2D) |
| 5 | `Fx_alt` | N (or non-dim) | Alternative calculation method |
| 6 | `Fy_alt` | N (or non-dim) | Alternative calculation method |
| 7 | `Fz_alt` | N (or non-dim) | Alternative calculation method |

**Note:** Columns 5-7 may be duplicates or use different computation methods.

### Example Data

```
# time       Fx          Fy          Fz          Fx_alt      Fy_alt      Fz_alt
0.000000    0.000000    0.000000    0.000000    0.000000    0.000000    0.000000
0.100000   -0.123456    0.012345    0.000000   -0.123456    0.012345    0.000000
0.200000   -0.234567    0.023456    0.000000   -0.234567    0.023456    0.000000
```

## Computation Method

### Lagrangian Force Calculation

Unlike the control volume method, this computes forces directly from:

```
F⃗ = ∫_Γ f⃗(s,t) ds

Where:
- Γ: Lagrangian structure boundary
- f⃗(s,t): Force density at Lagrangian point s
- ds: Arc length element
```

### IB Method Force

In the Immersed Boundary method, the force density comes from:

```
f⃗ = f⃗_elastic + f⃗_interaction

Where:
- f⃗_elastic: Internal elastic forces (from structure)
- f⃗_interaction: Fluid-structure interaction forces
```

## Physical Interpretation

### Comparison with Control Volume Forces

**Two methods for computing the same force:**

1. **This file (Drag_force_struct):**
   - Direct integration on Lagrangian surface
   - Uses IB force spreading/interpolation
   - May have different numerical error

2. **Drag_CV_strct_id files:**
   - Control volume approach
   - Uses Reynolds Transport Theorem
   - More physically transparent

**Both should give similar results!**

### Expected Differences

Small differences can arise from:
- Numerical discretization
- Interpolation schemes
- Control volume size (for CV method)
- Lagrangian point spacing (for this method)

**Typical agreement:** Within 1-5%

## Data Analysis Examples

### Compare with Control Volume Forces

```python
import numpy as np
import matplotlib.pyplot as plt

# Load both force calculations
struct_data = np.loadtxt('Eel2d_Drag_force_struct_no_0.curve')
cv_data = np.loadtxt('Drag_CV_strct_id_0')

time_struct = struct_data[:, 0]
Fx_struct = struct_data[:, 1]
Fy_struct = struct_data[:, 2]

time_cv = cv_data[:, 0]
Fx_cv = cv_data[:, 1]
Fy_cv = cv_data[:, 2]

# Plot comparison
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# X-component
axes[0].plot(time_struct, Fx_struct, 'b-', label='Structure method',
             linewidth=1, alpha=0.7)
axes[0].plot(time_cv, Fx_cv, 'r--', label='Control volume',
             linewidth=1, alpha=0.7)
axes[0].set_ylabel('Fx (N)')
axes[0].set_title('Force Comparison: Structure vs Control Volume')
axes[0].legend()
axes[0].grid(True)

# Y-component
axes[1].plot(time_struct, Fy_struct, 'b-', label='Structure method',
             linewidth=1, alpha=0.7)
axes[1].plot(time_cv, Fy_cv, 'r--', label='Control volume',
             linewidth=1, alpha=0.7)
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Fy (N)')
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig('force_method_comparison.png', dpi=300)
```

### Quantify Agreement

```python
# Interpolate to same time points
from scipy.interpolate import interp1d

# Use CV times as reference
f_Fx_struct = interp1d(time_struct, Fx_struct, kind='linear',
                       fill_value='extrapolate')
Fx_struct_interp = f_Fx_struct(time_cv)

f_Fy_struct = interp1d(time_struct, Fy_struct, kind='linear',
                       fill_value='extrapolate')
Fy_struct_interp = f_Fy_struct(time_cv)

# Compute errors
error_x = Fx_struct_interp - Fx_cv
error_y = Fy_struct_interp - Fy_cv

# Statistics (skip initial transient)
steady_start = 5.0
mask = time_cv > steady_start

error_x_mean = np.mean(error_x[mask])
error_x_std = np.std(error_x[mask])
error_x_max = np.max(np.abs(error_x[mask]))

error_y_mean = np.mean(error_y[mask])
error_y_std = np.std(error_y[mask])

# Relative error
Fx_rms = np.sqrt(np.mean(Fx_cv[mask]**2))
relative_error_x = error_x_std / Fx_rms * 100

print(f"Force Method Comparison:")
print(f"  Fx difference:")
print(f"    Mean: {error_x_mean:.6e} N")
print(f"    Std:  {error_x_std:.6e} N")
print(f"    Max:  {error_x_max:.6e} N")
print(f"    Relative: {relative_error_x:.2f}%")
print(f"  Fy difference:")
print(f"    Mean: {error_y_mean:.6e} N")
print(f"    Std:  {error_y_std:.6e} N")

if relative_error_x < 5.0:
    print(f"\n✓ Methods agree within {relative_error_x:.2f}% (GOOD)")
else:
    print(f"\n✗ Methods differ by {relative_error_x:.2f}% (CHECK SETUP)")
```

### Plot Error Time Series

```python
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Error
axes[0].plot(time_cv, error_x, 'k-', linewidth=0.5)
axes[0].axhline(y=error_x_mean, color='r', linestyle='--',
                label=f'Mean = {error_x_mean:.2e}')
axes[0].set_ylabel('Error in Fx (N)')
axes[0].set_title('Difference: Structure - Control Volume')
axes[0].legend()
axes[0].grid(True)

axes[1].plot(time_cv, error_y, 'k-', linewidth=0.5)
axes[1].axhline(y=error_y_mean, color='r', linestyle='--',
                label=f'Mean = {error_y_mean:.2e}')
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Error in Fy (N)')
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig('force_error.png', dpi=300)
```

### Check Alternative Columns

```python
# Some implementations provide alternative force calculations
# in columns 5-7

Fx_alt = struct_data[:, 4]
Fy_alt = struct_data[:, 5]

# Check if different from primary calculation
diff_x = np.max(np.abs(Fx_struct - Fx_alt))
diff_y = np.max(np.abs(Fy_struct - Fy_alt))

print(f"\nAlternative vs Primary Calculation:")
print(f"  Max difference in Fx: {diff_x:.2e}")
print(f"  Max difference in Fy: {diff_y:.2e}")

if diff_x < 1e-10:
    print("  → Columns 2 and 5 are identical (duplicate)")
else:
    print("  → Columns 2 and 5 are different (alternative method)")
```

## When to Use This File

### Use Structure Method When:

1. **Validation**: Cross-check control volume results
2. **No CV forces**: Control volume forces not computed
3. **Lagrangian analysis**: Need forces at each Lagrangian point
4. **Surface stress**: Analyzing force distribution on body

### Prefer Control Volume Method When:

1. **Standard analysis**: Most publications use CV method
2. **Physical transparency**: CV method more physically clear
3. **Force decomposition**: Easier to separate components
4. **Well-documented**: Better understood in literature

## Input File Configuration

### To enable this output:

```
ConstraintIBMethod {
    PrintOutput {
        output_drag = TRUE
        output_interval = 1
    }
}
```

### Lagrangian Structure Settings

```
ConstraintIBMethod {
    // Ensure Lagrangian markers are properly distributed
    lag_markers_per_element = 2.0
}
```

## Troubleshooting

### Problem: Large disagreement with CV forces

**Check:**
1. Control volume size (for CV method)
2. Lagrangian point spacing
3. Grid resolution
4. Interpolation kernel width

**Solutions:**
- Refine Eulerian grid
- Increase Lagrangian points
- Adjust CV radius

### Problem: File not created

**Check:**
1. `output_drag = TRUE` in input file
2. Structure is registered
3. Output directory exists

### Problem: Forces are noisy

**Possible causes:**
1. Lagrangian points too sparse
2. Grid too coarse
3. Timestep too large

**Solutions:**
- Increase `lag_markers_per_element`
- Refine mesh
- Reduce dt

## Physical Units

Same as control volume forces:

```python
# Dimensional
Fx_dimensional = Fx_struct  # N

# Non-dimensional force coefficient
C_D = Fx_struct / (0.5 * rho * U_inf**2 * A_ref)
```

## Key Differences from CV Method

| Aspect | Structure Method | Control Volume Method |
|--------|------------------|----------------------|
| **Integration** | Over Lagrangian surface | Over Eulerian CV |
| **Physics** | IB force spreading | Reynolds Transport Theorem |
| **Components** | Not separated | Pressure/viscous/momentum/unsteady |
| **Accuracy** | Depends on IB kernel | Depends on CV size |
| **Usage** | Validation | Primary analysis |

## See Also

- [Drag_CV_strct_id.md](./Drag_CV_strct_id.md) - Control volume forces (preferred)
- [Torque_struct.md](./Torque_struct.md) - Structure torque
- [../FORCE_CALCULATION_EXPLAINED.md](../FORCE_CALCULATION_EXPLAINED.md) - CV method details

---

**Last updated:** 2025-12-30
**IBAMR version:** 0.18.0
