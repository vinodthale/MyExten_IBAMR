# <basename>_EULERIAN_MOMENTUM_struct_no_N

## File Overview

**Filename pattern:** `Eel2d_EULERIAN_MOMENTUM_struct_no_0`, `Foil_EULERIAN_MOMENTUM_struct_no_1`, ...
**Created by:** `ConstraintIBMethod` kinematics output
**Size:** ~1-2 MB for typical simulation
**Format:** Tab-separated values (TSV)
**Alternate name:** `EulerianMomentum_strct_id_N.curve`

## Purpose

This file contains the **Eulerian fluid momentum** computed on the fixed Eulerian grid. It represents the total momentum of the fluid in the control volume surrounding the structure.

## File Format

### Column Structure

| Column | Name | Units | Description |
|--------|------|-------|-------------|
| 1 | `time` | seconds | Simulation time |
| 2 | `Px_euler` | kg·m/s (or non-dim) | x-component of Eulerian momentum |
| 3 | `Py_euler` | kg·m/s (or non-dim) | y-component of Eulerian momentum |
| 4 | `Pz_euler` | kg·m/s (or non-dim) | z-component of Eulerian momentum (0 for 2D) |

### Example Data

```
# time       Px_euler    Py_euler    Pz_euler
0.000000    0.000000    0.000000    0.000000
0.100000    0.001234   -0.000123    0.000000
0.200000    0.002456   -0.000234    0.000000
0.300000    0.003678    0.000345    0.000000
1.000000    0.012345   -0.001234    0.000000
```

## Physical Formulation

### Definition

The Eulerian momentum is computed by integrating the velocity field over the Eulerian grid:

```
P⃗_euler = ∫∫∫_Ω ρ u⃗(x⃗,t) dV

Where:
- ρ: Fluid density
- u⃗: Eulerian velocity field
- Ω: Computational domain (or control volume)
- dV: Volume element
```

### Discrete Formulation

On the Eulerian grid:

```
Px_euler = Σ_cells ρ * u * ΔV
Py_euler = Σ_cells ρ * v * ΔV
Pz_euler = Σ_cells ρ * w * ΔV
```

Where the sum is over all grid cells in the control volume.

## Physical Interpretation

### Fluid Momentum vs Total Momentum

**Total momentum** of the system:
```
P⃗_total = P⃗_fluid + P⃗_body
```

**This file contains only:** `P⃗_fluid` (Eulerian component)

**Body momentum** is computed separately from:
```
P⃗_body = M * V⃗_com
```

### Momentum Conservation

For an isolated system (no external forces):
```
dP⃗_total/dt = 0

Therefore:
dP⃗_fluid/dt = -dP⃗_body/dt
```

**Physical meaning:**
- Fluid momentum increases → Body momentum decreases (and vice versa)
- Momentum exchange drives swimming

### For FREE SWIMMING

**Eulerian momentum changes:**
- Wake carries momentum away
- Body accelerates → fluid momentum changes
- Exchange of momentum between fluid and body

**At steady swimming:**
- Periodic oscillations
- Mean may be non-zero (wake momentum)

### For TETHERED

**Eulerian momentum accumulates:**
- Body doesn't move → doesn't gain momentum
- Fluid momentum increases continuously
- Wake carries momentum downstream

## Use in Reynolds Transport Theorem

### Force Calculation

The Eulerian momentum appears in the unsteady force term:

```
F⃗_unsteady = -dP⃗_euler/dt + dP⃗_body/dt

Where:
- dP⃗_euler/dt: Rate of change of fluid momentum (from this file)
- dP⃗_body/dt: Rate of change of body momentum
```

This is the **unsteady component** in the force decomposition.

See: [Drag_CV_strct_id.md](./Drag_CV_strct_id.md) for total force calculation.

## Data Analysis Examples

### Plot Eulerian Momentum

```python
import numpy as np
import matplotlib.pyplot as plt

# Load Eulerian momentum
data = np.loadtxt('Eel2d_EULERIAN_MOMENTUM_struct_no_0')
time = data[:, 0]
Px_euler = data[:, 1]
Py_euler = data[:, 2]

# Magnitude
P_euler_mag = np.sqrt(Px_euler**2 + Py_euler**2)

# Plot components
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

axes[0].plot(time, Px_euler, 'b-', label='Px', linewidth=0.5)
axes[0].plot(time, Py_euler, 'r-', label='Py', linewidth=0.5)
axes[0].set_ylabel('Momentum (kg·m/s)')
axes[0].set_title('Eulerian Momentum Components')
axes[0].legend()
axes[0].grid(True)

axes[1].plot(time, P_euler_mag, 'k-', linewidth=0.5)
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('|P| (kg·m/s)')
axes[1].set_title('Eulerian Momentum Magnitude')
axes[1].grid(True)

plt.tight_layout()
plt.savefig('eulerian_momentum.png', dpi=300)
```

### Compute Rate of Change

```python
# dP/dt is used in force calculation
dt = time[1] - time[0]
dPx_dt = np.gradient(Px_euler, dt)
dPy_dt = np.gradient(Py_euler, dt)

# Plot
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

axes[0].plot(time, dPx_dt, 'b-', linewidth=0.5)
axes[0].set_ylabel('dPx/dt (N)')
axes[0].set_title('Rate of Change of Eulerian Momentum')
axes[0].grid(True)

axes[1].plot(time, dPy_dt, 'r-', linewidth=0.5)
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('dPy/dt (N)')
axes[1].grid(True)

plt.tight_layout()
plt.savefig('momentum_rate.png', dpi=300)

print(f"Mean dPx/dt: {np.mean(dPx_dt):.6e} N")
print(f"Mean dPy/dt: {np.mean(dPy_dt):.6e} N")
```

### Verify Momentum Conservation (Free Swimming)

```python
# For free swimming, check momentum conservation
# P_total = P_euler + P_body = constant (if no external forces)

# Load body velocity
vel_data = np.loadtxt('Eel2d_Trans_vel_struct_no_0')
Vx_body = vel_data[:, 1]
Vy_body = vel_data[:, 2]

# Body mass
M_body = 0.01  # kg

# Body momentum
Px_body = M_body * Vx_body
Py_body = M_body * Vy_body

# Total momentum
Px_total = Px_euler + Px_body
Py_total = Py_euler + Py_body

# Plot
fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

axes[0].plot(time, Px_euler, 'b-', label='Fluid', linewidth=1)
axes[0].plot(time, Px_body, 'r-', label='Body', linewidth=1)
axes[0].set_ylabel('Momentum (kg·m/s)')
axes[0].set_title('Momentum Components (x-direction)')
axes[0].legend()
axes[0].grid(True)

axes[1].plot(time, Px_total, 'k-', linewidth=1)
axes[1].set_ylabel('Total Px (kg·m/s)')
axes[1].set_title('Total Momentum (should be conserved)')
axes[1].grid(True)

# Check conservation
Px_mean = np.mean(Px_total)
Px_std = np.std(Px_total)
axes[2].plot(time, Px_total - Px_mean, 'k-', linewidth=0.5)
axes[2].set_xlabel('Time (s)')
axes[2].set_ylabel('Deviation (kg·m/s)')
axes[2].set_title(f'Momentum Conservation (std = {Px_std:.2e})')
axes[2].grid(True)

plt.tight_layout()
plt.savefig('momentum_conservation.png', dpi=300)

print(f"\nMomentum Conservation Check:")
print(f"  Mean total Px: {Px_mean:.6e} kg·m/s")
print(f"  Std total Px:  {Px_std:.6e} kg·m/s")
print(f"  Variation:     {Px_std/abs(Px_mean)*100:.4f}%")
```

### Analyze Wake Momentum (Tethered)

```python
# For tethered swimming, fluid momentum accumulates
steady_start = 5.0
mask = time > steady_start

# Rate of momentum accumulation
# This equals the thrust force
dPx_dt_mean = np.mean(dPx_dt[mask])

print(f"\nWake Momentum Accumulation (Tethered):")
print(f"  dPx/dt: {dPx_dt_mean:.6e} N")

# This should match the thrust force
force_data = np.loadtxt('Drag_CV_strct_id_0')
Fx = force_data[:, 1]
Fx_mean = np.mean(Fx[mask])

print(f"  Thrust force: {-Fx_mean:.6e} N")
print(f"  Difference: {abs(dPx_dt_mean - (-Fx_mean)):.2e} N")

# They should match for tethered case
```

### Compute Momentum Flux

```python
# Momentum leaving through domain boundaries
# Useful for open domains

# Momentum flux ≈ ρ * u * A
# For 2D: flux per unit span

rho = 1000  # kg/m³
U_inf = 1.0  # m/s
height = 1.0  # m

# Expected momentum flux in wake
flux_expected = rho * U_inf**2 * height

# Actual accumulation rate
flux_actual = dPx_dt_mean

print(f"\nMomentum Flux:")
print(f"  Expected (ρU²H): {flux_expected:.6e} N")
print(f"  Actual: {flux_actual:.6e} N")
```

## Relationship to Force Components

### Unsteady Force

From Reynolds Transport Theorem:

```python
# The unsteady force component uses this momentum

# Load force components (if available)
unsteady_data = np.loadtxt('Unsteady_CV_strct_id_0')
Fx_unsteady = unsteady_data[:, 1]

# Verify relation: F_unsteady = -dP_euler/dt + dP_body/dt
Fx_unsteady_computed = -dPx_dt + M_body * np.gradient(Vx_body, dt)

# Plot comparison
plt.figure(figsize=(10, 6))
plt.plot(time, Fx_unsteady, 'b-', label='From file', linewidth=1)
plt.plot(time, Fx_unsteady_computed, 'r--', label='Computed', linewidth=1)
plt.xlabel('Time (s)')
plt.ylabel('Unsteady Force (N)')
plt.title('Unsteady Force Verification')
plt.legend()
plt.grid(True)
plt.savefig('unsteady_force_verification.png', dpi=300)
```

## Input File Configuration

### To enable this output:

```
ConstraintIBMethod {
    PrintOutput {
        output_eulerian_mom = TRUE
        output_interval = 1
    }
}
```

## Computational Details

### Control Volume

The integration domain for Eulerian momentum:
- May be entire computational domain
- Or a control volume around the structure
- Check IBAMR documentation for specific implementation

### Grid Resolution

The accuracy depends on:
- Eulerian grid spacing
- Control volume size
- Velocity interpolation scheme

## Physical Units

### Dimensional:
```python
Px_dimensional = Px_euler  # kg·m/s
```

### Non-dimensional:
```python
# Using reference momentum
rho_ref = 1000  # kg/m³
U_ref = 1.0  # m/s
L_ref = 0.1  # m
V_ref = L_ref**3  # m³ (for 3D)
A_ref = L_ref**2  # m² (for 2D per unit thickness)

P_ref = rho_ref * U_ref * V_ref
Px_nondim = Px_euler / P_ref
```

## Troubleshooting

### Problem: Eulerian momentum is zero

**Check:**
1. Simulation has started (check time)
2. Flow field exists
3. Output is enabled in input file

### Problem: Momentum grows unbounded (tethered)

**This is NORMAL for tethered swimming!**
- Wake carries momentum downstream
- Fluid momentum accumulates
- Not a conservation violation

### Problem: Momentum not conserved (free swimming)

**Possible causes:**
1. Boundaries not far enough
2. Outflow conditions incorrect
3. Numerical dissipation

**Check:**
- Domain size adequate
- Boundary conditions appropriate

## See Also

- [Drag_CV_strct_id.md](./Drag_CV_strct_id.md) - Total force calculation
- [Trans_vel_struct.md](./Trans_vel_struct.md) - Body velocity (for body momentum)
- [../FORCE_CALCULATION_EXPLAINED.md](../FORCE_CALCULATION_EXPLAINED.md) - Reynolds Transport Theorem

---

**Last updated:** 2025-12-30
**IBAMR version:** 0.18.0
