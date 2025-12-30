# Drag_CV_strct_id_N

## File Overview

**Filename pattern:** `Drag_CV_strct_id_0`, `Drag_CV_strct_id_1`, ...
**Created by:** `CustomIBHydrodynamicForceEvaluator::postprocessIntegrateData()`
**Code location:** `CustomIBHydrodynamicForceEvaluator.cpp` lines 860-865
**Size:** ~3-4 MB for typical simulation
**Format:** Tab-separated values (TSV)

## Purpose

This file contains the **total hydrodynamic force** on an immersed structure computed using the Reynolds Transport Theorem with a moving control volume (CV) approach.

## Physical Formulation

### Reynolds Transport Theorem

The total force is computed from:

```
F⃗_total = F⃗_pressure + F⃗_viscous + F⃗_momentum + F⃗_unsteady
```

Where:
- **F_pressure**: Pressure traction on CV surface: `∫∫_∂CV (-p n⃗) dA`
- **F_viscous**: Viscous stress on CV surface: `∫∫_∂CV μ(∇u⃗ + ∇u⃗ᵀ)·n⃗ dA`
- **F_momentum**: Momentum flux across CV: `-∫∫_∂CV ρ(u⃗·n⃗)u⃗ dA`
- **F_unsteady**: Rate of change of momentum: `-d/dt∫∫∫_CV ρu⃗ dV + d/dt P⃗_body`

## Code Implementation

```cpp
// From CustomIBHydrodynamicForceEvaluator.cpp line 860-865
*force_obj.drag_CV_stream << new_time << '\t'
                          << force_obj.F_new(0) << '\t'
                          << force_obj.F_new(1) << '\t'
                          << force_obj.F_new(2) << std::endl;

// Where F_new is computed at line 839:
fobj.F_new = trac + fobj.F_unsteady_new;
```

## File Format

### Column Structure

| Column | Name | Units | Description |
|--------|------|-------|-------------|
| 1 | `time` | seconds | Simulation time |
| 2 | `Fx` | N (or non-dim) | Force in x-direction (streamwise) |
| 3 | `Fy` | N (or non-dim) | Force in y-direction (lateral) |
| 4 | `Fz` | N (or non-dim) | Force in z-direction (0 for 2D) |

### Example Data

```
# time       Fx          Fy          Fz
0.000000    0.000000    0.000000    0.000000
0.000100   -0.123456    0.012345    0.000000
0.000200   -0.234567    0.023456    0.000000
0.000300   -0.345678    0.034567    0.000000
```

## Physical Interpretation

### For TETHERED Bodies (momentum flags = 0,0,0)

**Fx** represents **NET PROPULSIVE THRUST**:
- **Negative Fx**: Body produces thrust (pushes fluid backward)
- **Positive Fx**: Body experiences drag (inefficient swimming)
- **Mean Fx < 0**: Efficient swimming/propulsion
- **Oscillations**: Due to periodic swimming motion

**Physical meaning:**
- What you would measure on a force transducer in experiments
- Net thrust production capability
- Directly comparable to wind tunnel/water tunnel measurements

### For FREE SWIMMING Bodies (momentum flags ≠ 0)

**Fx** represents **TRANSIENT HYDRODYNAMIC FORCE**:
- **During acceleration**: Fx < 0 (net thrust accelerates body)
- **At steady swimming**: Mean Fx ≈ 0 (thrust balances drag)
- **Oscillations**: From periodic swimming motion

**Physical meaning:**
- Unbalanced force causing acceleration
- At equilibrium: thrust = drag → Fx = 0
- Used to determine swimming performance

## Sign Convention

- **Positive Fx**: Drag (opposes motion, points backward)
- **Negative Fx**: Thrust (drives motion forward)
- **Positive Fy**: Lateral force (upward in 2D)
- **Negative Fy**: Lateral force (downward in 2D)

## Related Files

This file is the **sum** of component forces:
- **Pressure_CV_strct_id_N**: Pressure contribution
- **Viscous_CV_strct_id_N**: Viscous contribution
- **Momentum_CV_strct_id_N**: Momentum flux contribution
- **Unsteady_CV_strct_id_N**: Unsteady/inertial contribution

**Verification:**
```
Drag_CV = Pressure_CV + Viscous_CV + Momentum_CV + Unsteady_CV
```

## Non-Dimensionalization

Convert to force coefficients:

```python
# Thrust coefficient (for tethered case)
C_T = Fx / (0.5 * rho * U_inf**2 * A_ref)

# Drag coefficient (2D, per unit span)
C_D = Fx / (0.5 * rho * U_inf**2 * chord)

# Lift coefficient
C_L = Fy / (0.5 * rho * U_inf**2 * chord)
```

Where:
- `rho`: Fluid density
- `U_inf`: Reference velocity (freestream or swimming speed)
- `A_ref`: Reference area (chord × span for 3D, chord for 2D)
- `chord`: Characteristic length

## Data Analysis Examples

### Compute Mean Thrust (Tethered)

```python
import numpy as np

# Load data
data = np.loadtxt('Drag_CV_strct_id_0')
time = data[:, 0]
Fx = data[:, 1]
Fy = data[:, 2]

# Skip transient phase
steady_start = 5.0  # seconds
mask = time > steady_start

# Compute statistics
Fx_mean = np.mean(Fx[mask])
Fx_std = np.std(Fx[mask])
Fx_max = np.max(Fx[mask])
Fx_min = np.min(Fx[mask])

print(f"Mean thrust: {Fx_mean:.6f}")
print(f"Std deviation: {Fx_std:.6f}")
print(f"Peak-to-peak: {Fx_max - Fx_min:.6f}")

# Thrust coefficient
rho = 1.0      # kg/m³
U_inf = 1.0    # m/s
chord = 0.1    # m
C_T = Fx_mean / (0.5 * rho * U_inf**2 * chord)
print(f"Thrust coefficient C_T: {C_T:.6f}")
```

### Plot Force Time History

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 1, figsize=(10, 8))

# Streamwise force
axes[0].plot(time, Fx, 'b-', linewidth=0.5)
axes[0].axhline(y=Fx_mean, color='r', linestyle='--', label=f'Mean = {Fx_mean:.4f}')
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Fx (N)')
axes[0].set_title('Streamwise Force (Thrust)')
axes[0].legend()
axes[0].grid(True)

# Lateral force
axes[1].plot(time, Fy, 'g-', linewidth=0.5)
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Fy (N)')
axes[1].set_title('Lateral Force')
axes[1].grid(True)

plt.tight_layout()
plt.savefig('force_history.png', dpi=300)
```

### Frequency Analysis

```python
from scipy import signal

# Compute power spectral density
fs = 1.0 / (time[1] - time[0])  # Sampling frequency
f, Pxx = signal.welch(Fx[mask], fs=fs, nperseg=1024)

# Find dominant frequency
peak_idx = np.argmax(Pxx)
f_dominant = f[peak_idx]

print(f"Dominant frequency: {f_dominant:.4f} Hz")
print(f"Swimming period: {1/f_dominant:.4f} s")

# Plot spectrum
plt.figure(figsize=(10, 6))
plt.semilogy(f, Pxx)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power Spectral Density')
plt.title('Force Spectrum')
plt.grid(True)
plt.savefig('force_spectrum.png', dpi=300)
```

## Troubleshooting

### Problem: All forces are zero

**Possible causes:**
1. Simulation hasn't started yet (check time column)
2. No swimming motion defined (check kinematics)
3. No freestream flow (check boundary conditions)
4. Structure not registered with force evaluator

**Solution:**
```bash
# Check if file has data
wc -l Drag_CV_strct_id_0
# Should show thousands of lines

# Check time range
head -n 5 Drag_CV_strct_id_0
tail -n 5 Drag_CV_strct_id_0
```

### Problem: Forces are extremely large

**Possible causes:**
1. Incorrect non-dimensionalization
2. Timestep too large (numerical instability)
3. Grid too coarse
4. Units mismatch

**Solution:**
- Check reference values in input file
- Reduce timestep: `dt = 0.5 * dx / U_max`
- Refine mesh near body

### Problem: Forces don't match expectations

**Verification steps:**
1. Check force decomposition sums correctly
2. Compare with `<basename>_Drag_strct_id_0.curve`
3. Verify steady-state is reached
4. Check Reynolds number is correct

## Input File Configuration

### To enable this file:

```
IBHydrodynamicForceEvaluator {
    // This is automatically created when you register a structure
    // No special flags needed
}

ConstraintIBMethod {
    // Structure ID determines the file suffix
    structure_names = "eel"  // Creates Drag_CV_strct_id_0
}
```

### For tethered (thrust measurement):

```
ConstraintIBKinematics {
    calculate_translational_momentum = 0,0,0
    calculate_rotational_momentum    = 0,0,0
}
```

### For free swimming:

```
ConstraintIBKinematics {
    calculate_translational_momentum = 1,1,0
    calculate_rotational_momentum    = 0,0,1
}
```

## Key References

1. **Nangia et al. (2017)**: "A moving control volume approach to computing hydrodynamic forces and torques on immersed bodies", *J. Comp. Phys.*
2. **Noca et al. (1997)**: "A comparison of methods for evaluating time-dependent fluid dynamic forces", *Caltech Thesis*

## See Also

- [Torque_CV_strct_id.md](./Torque_CV_strct_id.md) - Torque output
- [Pressure_CV_strct_id.md](./Pressure_CV_strct_id.md) - Pressure component
- [Viscous_CV_strct_id.md](./Viscous_CV_strct_id.md) - Viscous component
- [Momentum_CV_strct_id.md](./Momentum_CV_strct_id.md) - Momentum flux component
- [Unsteady_CV_strct_id.md](./Unsteady_CV_strct_id.md) - Unsteady component

---

**Last updated:** 2025-12-30
**IBAMR version:** 0.18.0
