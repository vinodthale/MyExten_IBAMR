# Torque_CV_strct_id_N

## File Overview

**Filename pattern:** `Torque_CV_strct_id_0`, `Torque_CV_strct_id_1`, ...
**Created by:** `CustomIBHydrodynamicForceEvaluator::postprocessIntegrateData()`
**Code location:** `CustomIBHydrodynamicForceEvaluator.cpp` lines 866-867
**Size:** ~2-3 MB for typical simulation
**Format:** Tab-separated values (TSV)

## Purpose

This file contains the **total hydrodynamic torque** (moment) on an immersed structure computed using the Reynolds Transport Theorem approach.

## Physical Formulation

### Torque Calculation

The total torque about the center of mass is computed from:

```
T⃗_total = -(L⃗_box_new - L⃗_box_current)/dt + (L⃗_new - L⃗_current)/dt + T⃗_trac
```

Where:
- **L_box**: Angular momentum of fluid in control volume
- **L**: Angular momentum of body
- **T_trac**: Torque from surface tractions (pressure + viscous)
- **dt**: Timestep

## Code Implementation

```cpp
// From CustomIBHydrodynamicForceEvaluator.cpp line 866-867
*force_obj.torque_CV_stream << new_time << '\t'
                            << force_obj.T_new(0) << '\t'
                            << force_obj.T_new(1) << '\t'
                            << force_obj.T_new(2) << std::endl;

// Where T_new is computed at line 847:
fobj.T_new = -(fobj.L_box_new - fobj.L_box_current) / dt
           + (fobj.L_new - fobj.L_current) / dt
           + torque_trac;
```

## File Format

### Column Structure

| Column | Name | Units | Description |
|--------|------|-------|-------------|
| 1 | `time` | seconds | Simulation time |
| 2 | `Tx` | N·m (or non-dim) | Torque about x-axis (0 for 2D) |
| 3 | `Ty` | N·m (or non-dim) | Torque about y-axis (0 for 2D) |
| 4 | `Tz` | N·m (or non-dim) | Torque about z-axis (in-plane for 2D) |

### Example Data

```
# time       Tx          Ty          Tz
0.000000    0.000000    0.000000    0.000000
0.000100    0.000000    0.000000   -0.001234
0.000200    0.000000    0.000000   -0.002345
0.000300    0.000000    0.000000   -0.003456
```

## Physical Interpretation

### For 2D Simulations

- **Tx, Ty**: Always zero (no out-of-plane motion)
- **Tz**: In-plane rotational moment

### For TETHERED Bodies (momentum flags = 0,0,0)

**Tz** represents **rotational moment** from swimming motion:
- **For symmetric swimming**: Mean Tz ≈ 0 (no net turning tendency)
- **For asymmetric swimming**: Non-zero mean indicates turning tendency
- **Oscillations**: Due to periodic body deformation

**Physical meaning:**
- Moment that would cause rotation if body were free
- Indicates swimming symmetry
- Small for streamlined symmetric motion

### For FREE SWIMMING Bodies (with rotation enabled)

**Tz** represents **hydrodynamic moment** causing rotation:
- Used for maneuvering and turning
- **During turning**: Non-zero Tz causes angular acceleration
- **Straight swimming**: Mean Tz ≈ 0
- **Unsteady**: Oscillates with swimming frequency

## Sign Convention

- **Positive Tz**: Counter-clockwise rotation (CCW) when viewed from +z axis
- **Negative Tz**: Clockwise rotation (CW) when viewed from +z axis

## Non-Dimensionalization

Convert to torque coefficient:

```python
# Torque coefficient
C_M = Tz / (0.5 * rho * U_inf**2 * chord**2)
```

Where:
- `rho`: Fluid density
- `U_inf`: Reference velocity
- `chord`: Characteristic length

## Data Analysis Examples

### Compute Mean Torque

```python
import numpy as np

# Load data
data = np.loadtxt('Torque_CV_strct_id_0')
time = data[:, 0]
Tz = data[:, 3]  # In-plane torque for 2D

# Skip transient phase
steady_start = 5.0
mask = time > steady_start

# Compute statistics
Tz_mean = np.mean(Tz[mask])
Tz_std = np.std(Tz[mask])
Tz_max = np.max(Tz[mask])
Tz_min = np.min(Tz[mask])

print(f"Mean torque: {Tz_mean:.6e}")
print(f"Std deviation: {Tz_std:.6e}")
print(f"Peak-to-peak: {Tz_max - Tz_min:.6e}")

# Check symmetry
if abs(Tz_mean) < 0.01 * Tz_std:
    print("Swimming is symmetric (mean torque ≈ 0)")
else:
    print(f"Swimming is asymmetric (mean torque = {Tz_mean:.6e})")
```

### Plot Torque History

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(time, Tz, 'b-', linewidth=0.5)
plt.axhline(y=Tz_mean, color='r', linestyle='--', label=f'Mean = {Tz_mean:.4e}')
plt.xlabel('Time (s)')
plt.ylabel('Tz (N·m)')
plt.title('Hydrodynamic Torque (In-Plane)')
plt.legend()
plt.grid(True)
plt.savefig('torque_history.png', dpi=300)
```

### Check Turning Tendency

```python
# For free swimming simulations
# Compare torque with angular velocity

# Load rotational velocity
vel_data = np.loadtxt('Eel2dStr/Eel2d_RotationalVelocity_strct_id_0.curve')
time_vel = vel_data[:, 0]
omega_z = vel_data[:, 3]

# Compute angular acceleration
dt = time_vel[1] - time_vel[0]
alpha_z = np.gradient(omega_z, dt)

# Plot torque vs angular acceleration
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

axes[0].plot(time, Tz, 'b-', label='Torque Tz')
axes[0].set_ylabel('Torque (N·m)')
axes[0].legend()
axes[0].grid(True)

axes[1].plot(time_vel, alpha_z, 'r-', label='Angular accel.')
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('α_z (rad/s²)')
axes[1].legend()
axes[1].grid(True)

plt.savefig('torque_vs_acceleration.png', dpi=300)
```

## Relationship to Angular Momentum

The torque equation comes from conservation of angular momentum:

```
dL_total/dt = T_external

Where:
L_total = L_fluid + L_body
T_external = Torque from surface tractions
```

For tethered bodies:
- `dL_body/dt = 0` (no rotation)
- Torque balances change in fluid angular momentum

For free swimming:
- `dL_body/dt ≠ 0` (body can rotate)
- Torque drives angular acceleration

## Troubleshooting

### Problem: Torque is always zero

**For 2D simulations:**
- Tx and Ty should always be zero (expected)
- If Tz is also zero, check:
  - Swimming motion is active
  - Body is deforming
  - Flow has developed

**Solutions:**
```bash
# Check swimming kinematics
grep "deformation_velocity" input2d

# Verify structure is moving
# Check visualization files
```

### Problem: Large unexpected torque

**Possible causes:**
1. Asymmetric swimming motion
2. Body not centered properly
3. External forces/moments applied
4. Numerical issues

**Solutions:**
- Check body geometry symmetry
- Verify center of mass location
- Check for external constraints

### Problem: Torque doesn't match angular acceleration

**For free swimming:**

Expected relationship:
```
Tz = I * α_z
```

Where:
- `I`: Moment of inertia (from MOI file)
- `α_z`: Angular acceleration

**Verification:**
```python
# Load moment of inertia
moi_data = np.loadtxt('Eel2dStr/Eel2d_MomentInertia_strct_id_0.curve')
Izz = moi_data[:, 4]  # Moment about z-axis

# Compute angular acceleration from torque
alpha_computed = Tz / Izz[mask]

# Should match numerical derivative of omega_z
```

## Input File Configuration

### To enable this file:

```
IBHydrodynamicForceEvaluator {
    // Automatically created with force files
}
```

### For tethered (no rotation):

```
ConstraintIBKinematics {
    calculate_rotational_momentum = 0,0,0
}
```

### For free swimming (with rotation):

```
ConstraintIBKinematics {
    calculate_rotational_momentum = 0,0,1  // Rotation about z-axis
}
```

## Moment of Inertia

The moment of inertia appears in the torque calculation. See related file:
- [MOI_struct.md](./MOI_struct.md) - Moment of inertia output

For a uniform density body:
```
I = ∫∫∫ ρ r² dV
```

## Key References

1. **Nangia et al. (2017)**: Moving control volume forces and torques, *J. Comp. Phys.*
2. **Borazjani & Sotiropoulos (2008)**: Swimming simulations with self-propulsion

## See Also

- [Drag_CV_strct_id.md](./Drag_CV_strct_id.md) - Force output
- [MOI_struct.md](./MOI_struct.md) - Moment of inertia
- [Rot_vel_struct.md](./Rot_vel_struct.md) - Rotational velocity

---

**Last updated:** 2025-12-30
**IBAMR version:** 0.18.0
