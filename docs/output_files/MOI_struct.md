# <basename>_MOI_struct_no_N

## File Overview

**Filename pattern:** `Eel2d_MOI_struct_no_0`, `Foil_MOI_struct_no_1`, ...
**Created by:** `ConstraintIBMethod` kinematics output
**Size:** ~1-2 MB for typical simulation
**Format:** Tab-separated values (TSV)
**Alternate name:** `MomentInertia_strct_id_N.curve`

## Purpose

This file contains the **moment of inertia tensor** components of the structure. The moment of inertia describes how the mass is distributed relative to the center of mass, which determines the body's resistance to rotation.

## File Format

### Column Structure

| Column | Name | Units | Description |
|--------|------|-------|-------------|
| 1 | `time` | seconds | Simulation time |
| 2 | `Ixx` | kg·m² (or non-dim) | Moment of inertia about x-axis |
| 3 | `Iyy` | kg·m² (or non-dim) | Moment of inertia about y-axis |
| 4 | `Izz` | kg·m² (or non-dim) | Moment of inertia about z-axis |
| 5 | `Ixy` | kg·m² (or non-dim) | Product of inertia (xy) |
| 6 | `Ixz` | kg·m² (or non-dim) | Product of inertia (xz) |
| 7 | `Iyz` | kg·m² (or non-dim) | Product of inertia (yz) |

### Example Data - RIGID BODY

```
# time       Ixx         Iyy         Izz         Ixy         Ixz         Iyz
0.000000    0.000100    0.000100    0.000200    0.000000    0.000000    0.000000
1.000000    0.000100    0.000100    0.000200    0.000000    0.000000    0.000000
2.000000    0.000100    0.000100    0.000200    0.000000    0.000000    0.000000
```

### Example Data - DEFORMABLE BODY

```
# time       Ixx         Iyy         Izz         Ixy         Ixz         Iyz
0.000000    0.000100    0.000100    0.000200    0.000000    0.000000    0.000000
1.000000    0.000098    0.000102    0.000201   -0.000001    0.000000    0.000000
2.000000    0.000102    0.000098    0.000199    0.000001    0.000000    0.000000
3.000000    0.000099    0.000101    0.000200    0.000000    0.000000    0.000000
```

## Physical Formulation

### Inertia Tensor

The moment of inertia tensor is a 3×3 symmetric matrix:

```
I = | Ixx  Ixy  Ixz |
    | Ixy  Iyy  Iyz |
    | Ixz  Iyz  Izz |
```

### Diagonal Terms (Moments of Inertia)

For a discrete Lagrangian structure:

```
Ixx = Σ m_i (y_i² + z_i²)
Iyy = Σ m_i (x_i² + z_i²)
Izz = Σ m_i (x_i² + y_i²)
```

Where:
- `m_i`: Mass of marker i
- `(x_i, y_i, z_i)`: Position relative to center of mass

### Off-Diagonal Terms (Products of Inertia)

```
Ixy = -Σ m_i (x_i * y_i)
Ixz = -Σ m_i (x_i * z_i)
Iyz = -Σ m_i (y_i * z_i)
```

### For 2D Simulations

- **Ixx, Iyy**: About out-of-plane axes (can vary slightly)
- **Izz**: In-plane rotation (important for turning)
- **Ixy**: Coupling between x and y (≈ 0 for symmetric bodies)
- **Ixz, Iyz**: Zero (no z-variation in 2D)

## Physical Interpretation

### Rigid Body

**All components constant:**
- Mass distribution doesn't change
- Inertia tensor constant
- Simple rotational dynamics

### Deformable Body (Swimming)

**Components vary with time:**
- Body deforms during swimming
- Mass distribution changes
- Inertia oscillates with swimming cycle

**For symmetric swimming:**
- Izz oscillates periodically
- Ixy ≈ 0 (symmetry)
- Mean values approximately constant

## Rotational Dynamics

### Angular Momentum

```
L⃗ = I · ω⃗

For 2D (rotation about z):
L_z = Izz * ω_z
```

### Rotational Equation of Motion

```
T⃗ = dL⃗/dt = I · α⃗ + dI/dt · ω⃗

Where:
- T⃗: Torque
- α⃗: Angular acceleration
- I: Moment of inertia
- ω⃗: Angular velocity
```

**For rigid body (dI/dt = 0):**
```
T_z = Izz * α_z
```

**For deformable body:**
```
T_z = Izz * α_z + dIzz/dt * ω_z
```

## Data Analysis Examples

### Check if Body is Rigid

```python
import numpy as np
import matplotlib.pyplot as plt

# Load MOI data
data = np.loadtxt('Eel2d_MOI_struct_no_0')
time = data[:, 0]
Ixx = data[:, 1]
Iyy = data[:, 2]
Izz = data[:, 3]
Ixy = data[:, 4]

# Check variation
Izz_range = np.max(Izz) - np.min(Izz)
Izz_mean = np.mean(Izz)
variation = Izz_range / Izz_mean * 100

print(f"Izz mean: {Izz_mean:.6e} kg·m²")
print(f"Izz range: {Izz_range:.6e} kg·m²")
print(f"Variation: {variation:.4f}%")

if variation < 0.1:
    print("Body is approximately RIGID")
else:
    print("Body is DEFORMABLE")
```

### Plot Moment of Inertia

```python
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Diagonal terms
axes[0].plot(time, Ixx, 'r-', label='Ixx', linewidth=1)
axes[0].plot(time, Iyy, 'g-', label='Iyy', linewidth=1)
axes[0].plot(time, Izz, 'b-', label='Izz', linewidth=1)
axes[0].set_ylabel('Moment of Inertia (kg·m²)')
axes[0].set_title('Diagonal Terms')
axes[0].legend()
axes[0].grid(True)

# Off-diagonal terms
axes[1].plot(time, Ixy, 'k-', label='Ixy', linewidth=1)
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Product of Inertia (kg·m²)')
axes[1].set_title('Off-Diagonal Terms')
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig('moment_of_inertia.png', dpi=300)
```

### Compute Angular Momentum

```python
# Load angular velocity
vel_data = np.loadtxt('Eel2d_Rot_vel_struct_no_0')
omega_z = vel_data[:, 3]

# Angular momentum
L_z = Izz * omega_z

# Plot
plt.figure(figsize=(10, 6))
plt.plot(time, L_z, 'b-', linewidth=0.5)
plt.xlabel('Time (s)')
plt.ylabel('Angular Momentum L_z (kg·m²/s)')
plt.title('Angular Momentum = I·ω')
plt.grid(True)
plt.savefig('angular_momentum.png', dpi=300)

print(f"Angular momentum range: {np.max(L_z) - np.min(L_z):.6e}")
```

### Verify Torque-Angular Acceleration Relation

```python
# Load torque
torque_data = np.loadtxt('Torque_CV_strct_id_0')
T_z = torque_data[:, 3]

# Compute angular acceleration
dt = time[1] - time[0]
alpha_z = np.gradient(omega_z, dt)

# Expected torque from T = I*α (rigid body approx)
T_expected_rigid = Izz * alpha_z

# Actual relation for deformable body:
# T = I*α + dI/dt * ω
dIzz_dt = np.gradient(Izz, dt)
T_expected_deform = Izz * alpha_z + dIzz_dt * omega_z

# Plot comparison
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

axes[0].plot(time, T_z, 'b-', label='Actual torque', linewidth=1)
axes[0].plot(time, T_expected_rigid, 'r--', label='I*α (rigid)', linewidth=1)
axes[0].plot(time, T_expected_deform, 'g:', label='I*α + dI/dt*ω', linewidth=1)
axes[0].set_ylabel('Torque (N·m)')
axes[0].set_title('Torque Verification')
axes[0].legend()
axes[0].grid(True)

# Error
error_rigid = np.abs(T_z - T_expected_rigid)
error_deform = np.abs(T_z - T_expected_deform)
axes[1].semilogy(time, error_rigid, 'r-', label='Error (rigid)', linewidth=1)
axes[1].semilogy(time, error_deform, 'g-', label='Error (deform)', linewidth=1)
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Error (N·m)')
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig('torque_verification.png', dpi=300)

print(f"Mean error (rigid): {np.mean(error_rigid):.6e}")
print(f"Mean error (deformable): {np.mean(error_deform):.6e}")
```

### Analyze Deformation Effects

```python
# For deformable body, analyze Izz oscillations
steady_start = 5.0
mask = time > steady_start

Izz_steady = Izz[mask]
time_steady = time[mask]

# Statistics
Izz_mean_steady = np.mean(Izz_steady)
Izz_std_steady = np.std(Izz_steady)
Izz_max = np.max(Izz_steady)
Izz_min = np.min(Izz_steady)

print(f"\nMoment of Inertia Statistics (steady state):")
print(f"  Mean: {Izz_mean_steady:.6e} kg·m²")
print(f"  Std:  {Izz_std_steady:.6e} kg·m²")
print(f"  Max:  {Izz_max:.6e} kg·m²")
print(f"  Min:  {Izz_min:.6e} kg·m²")
print(f"  Amplitude: {(Izz_max - Izz_min)/2:.6e} kg·m²")
print(f"  Variation: {Izz_std_steady/Izz_mean_steady*100:.4f}%")

# Frequency of oscillation
from scipy import signal
fs = 1.0 / dt
f, Pxx = signal.welch(Izz_steady - Izz_mean_steady, fs=fs, nperseg=1024)
peak_idx = np.argmax(Pxx)
f_Izz = f[peak_idx]

print(f"  Oscillation frequency: {f_Izz:.4f} Hz")
print(f"  (Should match swimming frequency)")
```

### Compute Radius of Gyration

```python
# Radius of gyration: k = sqrt(I/M)
# where M is total mass

# Body mass (from input file or compute from markers)
body_mass = 0.01  # kg

# Radius of gyration about z-axis
k_z = np.sqrt(Izz / body_mass)

print(f"\nRadius of Gyration:")
print(f"  k_z: {np.mean(k_z[mask]):.6f} m")

# For a uniform rod of length L: k = L/sqrt(12)
# For a uniform disk of radius R: k = R/sqrt(2)
body_length = 0.1  # m
k_rod = body_length / np.sqrt(12)
print(f"  Comparison to uniform rod: k_rod = {k_rod:.6f} m")
```

### Check Symmetry

```python
# For symmetric body, products of inertia should be small
Ixy_mean = np.mean(np.abs(Ixy[mask]))
Izz_mean_val = np.mean(Izz[mask])

# Normalized product of inertia
Ixy_normalized = Ixy_mean / Izz_mean_val

print(f"\nSymmetry Check:")
print(f"  |Ixy|: {Ixy_mean:.6e} kg·m²")
print(f"  Izz:  {Izz_mean_val:.6e} kg·m²")
print(f"  |Ixy|/Izz: {Ixy_normalized:.6f}")

if Ixy_normalized < 0.01:
    print("Body is SYMMETRIC (Ixy ≈ 0)")
else:
    print("Body is ASYMMETRIC (Ixy ≠ 0)")
```

## Input File Configuration

### To enable this output:

```
ConstraintIBMethod {
    PrintOutput {
        output_moment_inertia = TRUE
        output_interval = 1
    }
}
```

### Body Mass Distribution

The moment of inertia is computed from Lagrangian marker masses:

```
// In structure definition
uniform_density = true
rho_solid = 1000.0  // kg/m³
```

## Typical Values

### For 2D Swimming Body

**Eel/Fish (length L = 0.1 m, mass M = 0.01 kg):**
```
Izz ≈ M * L² / 12 ≈ 8.3 × 10⁻⁶ kg·m²
```

**NACA Foil (chord C = 0.05 m, mass M = 0.005 kg):**
```
Izz ≈ M * C² / 12 ≈ 1.0 × 10⁻⁶ kg·m²
```

## Troubleshooting

### Problem: MOI is zero or very small

**Check:**
1. Body mass is defined
2. Density is reasonable
3. Lagrangian markers have mass

### Problem: MOI is unrealistically large

**Possible causes:**
1. Mass distribution incorrect
2. Units mismatch
3. Geometry issue

### Problem: MOI varies wildly

**For deformable body:**
- Some variation is expected
- Should be periodic
- Check structural stiffness

## See Also

- [Rot_vel_struct.md](./Rot_vel_struct.md) - Angular velocity (L = I·ω)
- [Torque_CV_strct_id.md](./Torque_CV_strct_id.md) - Torque (T = I·α)
- [COM_coordinates.md](./COM_coordinates.md) - Center of mass

---

**Last updated:** 2025-12-30
**IBAMR version:** 0.18.0
