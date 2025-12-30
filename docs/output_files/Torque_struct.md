# <basename>_Torque_struct_no_N

## File Overview

**Filename pattern:** `Eel2d_Torque_struct_no_0.curve`, `Foil_Torque_struct_no_1.curve`, ...
**Created by:** `ConstraintIBMethod` (alternative torque calculation)
**Size:** ~2-3 MB for typical simulation
**Format:** Tab-separated values (TSV)
**Note:** `.curve` extension (Lagrangian structure output)

## Purpose

This file contains **hydrodynamic torques computed directly on the Lagrangian structure** (alternative to control volume method). It can be used for **cross-validation** with the control volume torques.

## File Format

### Column Structure

| Column | Name | Units | Description |
|--------|------|-------|-------------|
| 1 | `time` | seconds | Simulation time |
| 2 | `Tx` | N·m (or non-dim) | Torque about x-axis |
| 3 | `Ty` | N·m (or non-dim) | Torque about y-axis |
| 4 | `Tz` | N·m (or non-dim) | Torque about z-axis (in-plane for 2D) |
| 5 | `Tx_alt` | N·m (or non-dim) | Alternative calculation |
| 6 | `Ty_alt` | N·m (or non-dim) | Alternative calculation |
| 7 | `Tz_alt` | N·m (or non-dim) | Alternative calculation |

**Note:** Columns 5-7 may be duplicates or use different computation methods.

### Example Data (2D)

```
# time       Tx          Ty          Tz          Tx_alt      Ty_alt      Tz_alt
0.000000    0.000000    0.000000    0.000000    0.000000    0.000000    0.000000
0.100000    0.000000    0.000000   -0.001234    0.000000    0.000000   -0.001234
0.200000    0.000000    0.000000   -0.002345    0.000000    0.000000   -0.002345
```

## Computation Method

### Lagrangian Torque Calculation

Computed directly from forces on Lagrangian markers:

```
T⃗ = ∫_Γ r⃗ × f⃗(s,t) ds

Where:
- Γ: Lagrangian structure boundary
- r⃗: Position vector from center of mass to point s
- f⃗(s,t): Force density at point s
- ds: Arc length element
```

### For 2D

Only in-plane torque (Tz) is non-zero:

```
Tz = ∫_Γ (rx * fy - ry * fx) ds
```

## Physical Interpretation

### Comparison with Control Volume Torques

**Two methods for computing the same torque:**

1. **This file (Torque_struct):**
   - Direct moment calculation on Lagrangian surface
   - Uses IB force spreading
   - Simpler calculation

2. **Torque_CV_strct_id files:**
   - Control volume angular momentum balance
   - More complex but more rigorous
   - Better physical interpretation

**Both should agree!**

## Data Analysis Examples

### Compare with Control Volume Torques

```python
import numpy as np
import matplotlib.pyplot as plt

# Load both torque calculations
struct_data = np.loadtxt('Eel2d_Torque_struct_no_0.curve')
cv_data = np.loadtxt('Torque_CV_strct_id_0')

time_struct = struct_data[:, 0]
Tz_struct = struct_data[:, 3]  # In-plane for 2D

time_cv = cv_data[:, 0]
Tz_cv = cv_data[:, 3]

# Plot comparison
plt.figure(figsize=(10, 6))
plt.plot(time_struct, Tz_struct, 'b-', label='Structure method',
         linewidth=1, alpha=0.7)
plt.plot(time_cv, Tz_cv, 'r--', label='Control volume',
         linewidth=1, alpha=0.7)
plt.xlabel('Time (s)')
plt.ylabel('Tz (N·m)')
plt.title('Torque Comparison: Structure vs Control Volume')
plt.legend()
plt.grid(True)
plt.savefig('torque_comparison.png', dpi=300)
```

### Quantify Agreement

```python
# Interpolate to same time points
from scipy.interpolate import interp1d

f_Tz_struct = interp1d(time_struct, Tz_struct, kind='linear',
                       fill_value='extrapolate')
Tz_struct_interp = f_Tz_struct(time_cv)

# Compute error
error_z = Tz_struct_interp - Tz_cv

# Statistics (steady state)
steady_start = 5.0
mask = time_cv > steady_start

error_mean = np.mean(error_z[mask])
error_std = np.std(error_z[mask])
error_max = np.max(np.abs(error_z[mask]))

# Relative error
Tz_rms = np.sqrt(np.mean(Tz_cv[mask]**2))
relative_error = error_std / Tz_rms * 100 if Tz_rms > 1e-10 else 0

print(f"Torque Method Comparison:")
print(f"  Tz difference:")
print(f"    Mean:  {error_mean:.6e} N·m")
print(f"    Std:   {error_std:.6e} N·m")
print(f"    Max:   {error_max:.6e} N·m")
if Tz_rms > 1e-10:
    print(f"    Relative: {relative_error:.2f}%")

# Plot error
plt.figure(figsize=(10, 6))
plt.plot(time_cv, error_z, 'k-', linewidth=0.5)
plt.axhline(y=error_mean, color='r', linestyle='--',
            label=f'Mean = {error_mean:.2e}')
plt.xlabel('Time (s)')
plt.ylabel('Error in Tz (N·m)')
plt.title('Difference: Structure - Control Volume')
plt.legend()
plt.grid(True)
plt.savefig('torque_error.png', dpi=300)
```

### Verify Torque-Angular Dynamics

```python
# Load moment of inertia and angular velocity
moi_data = np.loadtxt('Eel2d_MOI_struct_no_0')
vel_data = np.loadtxt('Eel2d_Rot_vel_struct_no_0')

Izz = moi_data[:, 4]
omega_z = vel_data[:, 3]

# Angular acceleration
dt = time_cv[1] - time_cv[0]
alpha_z = np.gradient(omega_z, dt)

# Expected from T = I*α (rigid body)
f_Izz = interp1d(moi_data[:, 0], Izz, kind='linear',
                 fill_value='extrapolate')
Izz_interp = f_Izz(time_cv)

Tz_expected_rigid = Izz_interp * alpha_z

# For deformable body: T = I*α + dI/dt * ω
dIzz_dt = np.gradient(Izz_interp, dt)
Tz_expected_deform = Izz_interp * alpha_z + dIzz_dt * omega_z

# Plot
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

axes[0].plot(time_cv, Tz_cv, 'b-', label='Actual (CV)', linewidth=1)
axes[0].plot(time_cv, Tz_expected_rigid, 'r--',
             label='I*α (rigid)', linewidth=1)
axes[0].plot(time_cv, Tz_expected_deform, 'g:',
             label='I*α + dI/dt*ω', linewidth=1)
axes[0].set_ylabel('Torque (N·m)')
axes[0].set_title('Torque-Angular Dynamics Verification')
axes[0].legend()
axes[0].grid(True)

# Error
error_rigid = np.abs(Tz_cv - Tz_expected_rigid)
error_deform = np.abs(Tz_cv - Tz_expected_deform)
axes[1].semilogy(time_cv, error_rigid, 'r-', label='Error (rigid)', linewidth=0.5)
axes[1].semilogy(time_cv, error_deform, 'g-', label='Error (deform)', linewidth=0.5)
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Error (N·m)')
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig('torque_dynamics_verification.png', dpi=300)
```

### Check Alternative Columns

```python
# Check if columns 5-7 differ from 2-4
Tz_alt = struct_data[:, 6]

diff = np.max(np.abs(Tz_struct - Tz_alt))

print(f"\nAlternative vs Primary Calculation:")
print(f"  Max difference in Tz: {diff:.2e}")

if diff < 1e-10:
    print("  → Columns are identical (duplicate)")
else:
    print("  → Columns are different (alternative method)")
```

### Analyze Torque Statistics

```python
# Compute statistics
steady_start = 5.0
mask = time_struct > steady_start

Tz_mean = np.mean(Tz_struct[mask])
Tz_std = np.std(Tz_struct[mask])
Tz_max = np.max(Tz_struct[mask])
Tz_min = np.min(Tz_struct[mask])

print(f"\nTorque Statistics (Structure Method):")
print(f"  Mean: {Tz_mean:.6e} N·m")
print(f"  Std:  {Tz_std:.6e} N·m")
print(f"  Max:  {Tz_max:.6e} N·m")
print(f"  Min:  {Tz_min:.6e} N·m")
print(f"  Peak-to-peak: {Tz_max - Tz_min:.6e} N·m")

# Check symmetry
if abs(Tz_mean) < 0.01 * Tz_std:
    print("  Swimming is symmetric (mean ≈ 0)")
else:
    print("  Swimming is asymmetric")
```

## When to Use This File

### Use Structure Method When:

1. **Validation**: Cross-check CV results
2. **Lagrangian analysis**: Need torque from IB forces
3. **No CV torques**: CV torques not available

### Prefer Control Volume Method When:

1. **Standard analysis**: More commonly used
2. **Physical clarity**: Better physical interpretation
3. **Consistency**: With force decomposition

## Input File Configuration

### To enable this output:

```
ConstraintIBMethod {
    PrintOutput {
        output_torque = TRUE
        output_interval = 1
    }
}
```

## Troubleshooting

### Problem: Large disagreement with CV torques

**Check:**
1. Control volume setup
2. Lagrangian point distribution
3. Grid resolution
4. Center of mass calculation

### Problem: File not created

**Check:**
1. `output_torque = TRUE` in input file
2. Structure registered properly
3. Output directory exists

### Problem: Torque is noisy

**Solutions:**
- Increase Lagrangian points
- Refine Eulerian grid
- Reduce timestep

## Relationship to Forces

### Torque from force distribution:

```python
# If you have force at each Lagrangian point:
# T = Σ r_i × F_i

# This file integrates this to give total torque
```

## Physical Units

### Dimensional:
```python
Tz_dimensional = Tz_struct  # N·m
```

### Non-dimensional:
```python
# Torque coefficient
C_M = Tz_struct / (0.5 * rho * U_inf**2 * L_ref**2)
```

## Key Differences from CV Method

| Aspect | Structure Method | Control Volume Method |
|--------|------------------|----------------------|
| **Calculation** | Direct r⃗ × f⃗ on Lagrangian surface | Angular momentum balance |
| **Complexity** | Simpler | More complex |
| **Physics** | Force moment | Conservation law |
| **Usage** | Validation | Primary analysis |

## See Also

- [Torque_CV_strct_id.md](./Torque_CV_strct_id.md) - Control volume torques (preferred)
- [Drag_force_struct.md](./Drag_force_struct.md) - Structure forces
- [Rot_vel_struct.md](./Rot_vel_struct.md) - Angular velocity
- [MOI_struct.md](./MOI_struct.md) - Moment of inertia

---

**Last updated:** 2025-12-30
**IBAMR version:** 0.18.0
