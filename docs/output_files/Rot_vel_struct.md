# <basename>_Rot_vel_struct_no_N

## File Overview

**Filename pattern:** `Eel2d_Rot_vel_struct_no_0`, `Foil_Rot_vel_struct_no_1`, ...
**Created by:** `ConstraintIBMethod` kinematics output
**Size:** ~1-2 MB for typical simulation
**Format:** Tab-separated values (TSV)
**Alternate name:** `RotationalVelocity_strct_id_N.curve`

## Purpose

This file contains the **rotational velocity (angular velocity)** of the structure. It represents how fast the body is rotating about each axis.

## File Format

### Column Structure

| Column | Name | Units | Description |
|--------|------|-------|-------------|
| 1 | `time` | seconds | Simulation time |
| 2 | `ωx` | rad/s (or non-dim) | Angular velocity about x-axis |
| 3 | `ωy` | rad/s (or non-dim) | Angular velocity about y-axis |
| 4 | `ωz` | rad/s (or non-dim) | Angular velocity about z-axis (in-plane for 2D) |

### Example Data - FREE SWIMMING (2D)

```
# time       ωx          ωy          ωz
0.000000    0.000000    0.000000    0.000000
1.000000    0.000000    0.000000    0.012345
2.000000    0.000000    0.000000   -0.023456
3.000000    0.000000    0.000000    0.015678
5.000000    0.000000    0.000000   -0.008901
```

### Example Data - TETHERED

```
# time       ωx          ωy          ωz
0.000000    0.000000    0.000000    0.000000
1.000000    0.000000    0.000000    0.000000
2.000000    0.000000    0.000000    0.000000
3.000000    0.000000    0.000000    0.000000
5.000000    0.000000    0.000000    0.000000
```

## Physical Interpretation

### For 2D Simulations

- **ωx = 0**: No rotation about x-axis (always zero in 2D)
- **ωy = 0**: No rotation about y-axis (always zero in 2D)
- **ωz**: In-plane rotation rate (turning)

### Sign Convention

- **Positive ωz**: Counter-clockwise (CCW) rotation when viewed from +z axis
- **Negative ωz**: Clockwise (CW) rotation when viewed from +z axis

### For FREE SWIMMING with Rotation Enabled

**Angular velocity evolves based on torque:**

```
Torque = I * α

Where:
- I: Moment of inertia
- α = dω/dt: Angular acceleration
```

**Typical behavior:**
- **Straight swimming**: ωz ≈ 0 (minimal rotation)
- **Turning maneuvers**: ωz ≠ 0 (body rotates)
- **Oscillations**: Small periodic variations due to swimming

### For TETHERED Bodies

**All angular velocities are zero:**
- No rotation allowed
- Orientation is fixed
- Body deforms but doesn't turn

## Relationship to Orientation

### Angular velocity is derivative of orientation angle:

```
θ(t) = θ₀ + ∫ ωz dt

Where:
- θ: Orientation angle
- θ₀: Initial orientation
```

## Data Analysis Examples

### Compute Turning Rate

```python
import numpy as np
import matplotlib.pyplot as plt

# Load rotational velocity
data = np.loadtxt('Eel2d_Rot_vel_struct_no_0')
time = data[:, 0]
omega_z = data[:, 3]  # In-plane rotation for 2D

# Statistics
steady_start = 5.0
mask = time > steady_start

omega_mean = np.mean(omega_z[mask])
omega_std = np.std(omega_z[mask])
omega_max = np.max(np.abs(omega_z[mask]))

print(f"Mean angular velocity: {omega_mean:.6e} rad/s")
print(f"Std deviation: {omega_std:.6e} rad/s")
print(f"Max |ωz|: {omega_max:.6f} rad/s")

# Convert to degrees/sec
omega_mean_deg = omega_mean * 180 / np.pi
print(f"Mean turning rate: {omega_mean_deg:.6f} deg/s")

# Check if swimming straight
if abs(omega_mean) < 0.01 * omega_std:
    print("Swimming is straight (no net turning)")
else:
    print(f"Body is turning (mean ωz ≠ 0)")
```

### Plot Angular Velocity

```python
plt.figure(figsize=(10, 6))
plt.plot(time, omega_z, 'b-', linewidth=0.5)
plt.axhline(y=omega_mean, color='r', linestyle='--',
            label=f'Mean = {omega_mean:.4e} rad/s')
plt.xlabel('Time (s)')
plt.ylabel('ωz (rad/s)')
plt.title('Angular Velocity (In-Plane Rotation)')
plt.legend()
plt.grid(True)
plt.savefig('angular_velocity.png', dpi=300)
```

### Compute Orientation Angle

```python
# Integrate angular velocity to get orientation
dt = time[1] - time[0]
theta = np.cumsum(omega_z) * dt  # Cumulative integration

# Convert to degrees
theta_deg = theta * 180 / np.pi

# Plot orientation
plt.figure(figsize=(10, 6))
plt.plot(time, theta_deg, 'b-', linewidth=1)
plt.xlabel('Time (s)')
plt.ylabel('Orientation Angle (degrees)')
plt.title('Body Orientation from Angular Velocity')
plt.grid(True)
plt.savefig('orientation_angle.png', dpi=300)

print(f"Total rotation: {theta_deg[-1]:.2f} degrees")
```

### Compute Angular Acceleration

```python
# Numerical derivative
alpha_z = np.gradient(omega_z, dt)

# Plot angular acceleration
plt.figure(figsize=(10, 6))
plt.plot(time, alpha_z, 'r-', linewidth=0.5)
plt.xlabel('Time (s)')
plt.ylabel('αz (rad/s²)')
plt.title('Angular Acceleration')
plt.grid(True)
plt.savefig('angular_acceleration.png', dpi=300)

# Peak angular acceleration
alpha_max = np.max(np.abs(alpha_z))
print(f"Peak angular acceleration: {alpha_max:.4f} rad/s²")
```

### Verify Rotational Dynamics

```python
# Load torque and moment of inertia
torque_data = np.loadtxt('Torque_CV_strct_id_0')
Tz = torque_data[:, 3]

moi_data = np.loadtxt('Eel2d_MOI_struct_no_0')
Izz = moi_data[:, 4]  # Moment of inertia about z-axis

# From Newton's second law for rotation:
# Tz = Izz * αz
alpha_from_torque = Tz / Izz

# Compare with numerical derivative
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

axes[0].plot(time, alpha_z, 'b-', label='From ω (numerical)')
axes[0].plot(time, alpha_from_torque, 'r--', label='From torque/I')
axes[0].set_ylabel('Angular Accel. (rad/s²)')
axes[0].legend()
axes[0].grid(True)
axes[0].set_title('Angular Acceleration Verification')

# Error
error = np.abs(alpha_z - alpha_from_torque)
axes[1].semilogy(time, error, 'k-')
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Error (rad/s²)')
axes[1].grid(True)
axes[1].set_title('Verification Error')

plt.tight_layout()
plt.savefig('rotational_dynamics_verification.png', dpi=300)
```

### Analyze Turning Maneuvers

```python
# Detect turning events (|ωz| > threshold)
threshold = 0.1  # rad/s

turning_mask = np.abs(omega_z) > threshold
turning_times = time[turning_mask]

if len(turning_times) > 0:
    print(f"Turning detected at {len(turning_times)} timesteps")
    print(f"First turn: t = {turning_times[0]:.4f} s")
    print(f"Last turn: t = {turning_times[-1]:.4f} s")

    # Plot with turning regions highlighted
    plt.figure(figsize=(12, 6))
    plt.plot(time, omega_z, 'b-', linewidth=0.5)
    plt.fill_between(time, -threshold, threshold, alpha=0.2,
                     color='green', label='Straight swimming')
    plt.axhline(y=threshold, color='r', linestyle='--')
    plt.axhline(y=-threshold, color='r', linestyle='--')
    plt.xlabel('Time (s)')
    plt.ylabel('ωz (rad/s)')
    plt.title('Angular Velocity with Turning Detection')
    plt.legend()
    plt.grid(True)
    plt.savefig('turning_detection.png', dpi=300)
else:
    print("No significant turning detected")
```

### Compute Turning Radius

```python
# For a body swimming with constant speed V and angular velocity ω,
# the turning radius is: R = V / ω

# Load translational velocity
vel_data = np.loadtxt('Eel2d_Trans_vel_struct_no_0')
Vx = vel_data[:, 1]
Vy = vel_data[:, 2]
V = np.sqrt(Vx**2 + Vy**2)

# Turning radius (avoid division by zero)
omega_z_safe = omega_z.copy()
omega_z_safe[np.abs(omega_z_safe) < 1e-10] = np.nan

R_turn = V / np.abs(omega_z_safe)

# Plot turning radius
plt.figure(figsize=(10, 6))
plt.plot(time, R_turn, 'b-', linewidth=0.5)
plt.xlabel('Time (s)')
plt.ylabel('Turning Radius (m)')
plt.title('Instantaneous Turning Radius')
plt.ylim([0, 50])  # Limit y-axis for visibility
plt.grid(True)
plt.savefig('turning_radius.png', dpi=300)

# Mean turning radius during turns
if np.any(turning_mask):
    R_mean_turn = np.nanmean(R_turn[turning_mask])
    print(f"Mean turning radius: {R_mean_turn:.4f} m")

    # In body lengths
    body_length = 0.1
    R_BL = R_mean_turn / body_length
    print(f"Turning radius: {R_BL:.2f} body lengths")
```

## Relationship to Other Files

### Torque

Angular velocity is driven by torque:

```python
# Torque = I * dω/dt
# See Torque_CV_strct_id.md
```

### Moment of Inertia

Angular momentum: **L = I * ω**

```python
# Load MOI
moi_data = np.loadtxt('Eel2d_MOI_struct_no_0')
Izz = moi_data[:, 4]

# Angular momentum
L_z = Izz * omega_z

# Plot
plt.figure(figsize=(10, 6))
plt.plot(time, L_z, 'b-')
plt.xlabel('Time (s)')
plt.ylabel('Angular Momentum (kg·m²/s)')
plt.title('Angular Momentum = I·ω')
plt.grid(True)
plt.savefig('angular_momentum.png', dpi=300)
```

### COM Coordinates

For turning motion, COM follows curved path:

```python
# Curvature κ = ω / V
kappa = omega_z / V

# Radius of curvature = 1/κ
```

## Input File Configuration

### To enable this output:

```
ConstraintIBMethod {
    PrintOutput {
        output_rig_rotvel = TRUE
        output_interval = 1
    }
}
```

### For free swimming with rotation:

```
ConstraintIBKinematics {
    calculate_rotational_momentum = 0,0,1
    // Can rotate about z-axis (2D in-plane)
}
```

### For tethered (no rotation):

```
ConstraintIBKinematics {
    calculate_rotational_momentum = 0,0,0
    // ωx = ωy = ωz = 0
}
```

## Troubleshooting

### Problem: Angular velocity always zero (free swimming expected)

**Check:**
1. `calculate_rotational_momentum = 0,0,1` (for 2D)
2. Body has correct moment of inertia
3. Torques exist (check Torque_CV file)
4. Simulation time sufficient

### Problem: Unrealistic spinning

**Possible causes:**
1. Moment of inertia too small
2. Large asymmetric forces
3. Numerical instability

**Solutions:**
- Check body mass distribution
- Verify swimming kinematics symmetry
- Reduce timestep

### Problem: ωz doesn't match expected turning

**Verify:**
```python
# Check if orientation changes
# θ_final - θ_initial should equal ∫ωz dt
```

## Physical Units

### Dimensional:
```python
omega_rad_per_s = omega_z  # rad/s
omega_deg_per_s = omega_z * 180 / np.pi  # deg/s
```

### Non-dimensional:
```python
# Angular velocity * characteristic time
omega_nd = omega_z * (1.0 / swimming_freq)

# Reduced angular velocity
omega_reduced = omega_z * chord / U_swim
```

## Swimming Performance Metrics

### Maneuverability Index

```python
# Maximum angular velocity during turn
omega_max_turn = np.max(np.abs(omega_z[turning_mask]))

# Minimum turning radius
R_min = V_steady / omega_max_turn

# Maneuverability: smaller R_min = more maneuverable
print(f"Minimum turning radius: {R_min:.4f} m")
print(f"                      : {R_min/body_length:.2f} BL")
```

## See Also

- [Torque_CV_strct_id.md](./Torque_CV_strct_id.md) - Torque causing rotation
- [MOI_struct.md](./MOI_struct.md) - Moment of inertia
- [Trans_vel_struct.md](./Trans_vel_struct.md) - Translational velocity
- [COM_coordinates.md](./COM_coordinates.md) - Position tracking

---

**Last updated:** 2025-12-30
**IBAMR version:** 0.18.0
