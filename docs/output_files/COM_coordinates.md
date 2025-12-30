# <basename>_COM_coordinates_struct_no_N

## File Overview

**Filename pattern:** `Eel2d_COM_coordinates_struct_no_0`, `Foil_COM_coordinates_struct_no_1`, ...
**Created by:** `ConstraintIBMethod` kinematics output
**Size:** ~1-2 MB for typical simulation
**Format:** Tab-separated values (TSV)
**Alternate name:** Sometimes called `COMcoords_strct_id_N.curve`

## Purpose

This file contains the **center of mass (COM) coordinates** of the immersed structure over time. It tracks the position of the structure's centroid in the computational domain.

## File Format

### Column Structure

| Column | Name | Units | Description |
|--------|------|-------|-------------|
| 1 | `time` | seconds | Simulation time |
| 2 | `X_com` | meters (or non-dim) | x-coordinate of center of mass |
| 3 | `Y_com` | meters (or non-dim) | y-coordinate of center of mass |
| 4 | `Z_com` | meters (or non-dim) | z-coordinate of center of mass |

### Example Data - FREE SWIMMING

```
# time       X_com       Y_com       Z_com
0.000000    0.000000    0.000000    0.000000
1.000000    0.523456    0.001234    0.000000
2.000000    1.098765    0.002345    0.000000
3.000000    1.712345    0.001456    0.000000
5.000000    3.045678    0.000987    0.000000
```

### Example Data - TETHERED

```
# time       X_com       Y_com       Z_com
0.000000    0.500000    0.300000    0.000000
1.000000    0.500000    0.300000    0.000000
2.000000    0.500000    0.300000    0.000000
3.000000    0.500000    0.300000    0.000000
5.000000    0.500000    0.300000    0.000000
```

## Physical Interpretation

### Definition of Center of Mass

For a discrete Lagrangian structure with markers:

```
X_com = (1/M) * Σ(m_i * x_i)
Y_com = (1/M) * Σ(m_i * y_i)
Z_com = (1/M) * Σ(m_i * z_i)
```

Where:
- `M`: Total mass of structure
- `m_i`: Mass of marker i
- `(x_i, y_i, z_i)`: Position of marker i

### For FREE SWIMMING Bodies

**Coordinates change with time:**
- **X_com increases**: Body moving forward (positive x-direction)
- **X_com decreases**: Body moving backward (negative x-direction)
- **Y_com oscillates**: Lateral motion or drift
- **Z_com changes**: Vertical motion (3D only)

**Typical behavior:**
```
t = 0s:    X_com = 0.0     (starting position)
t = 5s:    X_com = 2.5     (accelerating)
t = 10s:   X_com = 5.2     (steady swimming)
```

**Swimming speed:**
```
U_swim = dX_com/dt
```

### For TETHERED Bodies

**Coordinates remain constant:**
- **All components constant**: Body position is fixed
- **Body deforms** around this fixed center point
- **No translation**: Despite swimming motion

**Typical values:**
```
All times:  X_com = constant
            Y_com = constant
            Z_com = constant (0 for 2D)
```

## Data Analysis Examples

### Compute Swimming Trajectory (Free Swimming)

```python
import numpy as np
import matplotlib.pyplot as plt

# Load COM data
data = np.loadtxt('Eel2d_COM_coordinates_struct_no_0')
time = data[:, 0]
X_com = data[:, 1]
Y_com = data[:, 2]

# Plot trajectory
plt.figure(figsize=(12, 6))

# Trajectory in space
plt.subplot(1, 2, 1)
plt.plot(X_com, Y_com, 'b-', linewidth=2)
plt.plot(X_com[0], Y_com[0], 'go', markersize=10, label='Start')
plt.plot(X_com[-1], Y_com[-1], 'ro', markersize=10, label='End')
plt.xlabel('X (m)')
plt.ylabel('Y (m)')
plt.title('Swimming Trajectory')
plt.axis('equal')
plt.legend()
plt.grid(True)

# Position vs time
plt.subplot(1, 2, 2)
plt.plot(time, X_com, 'b-', label='X_com')
plt.plot(time, Y_com, 'r-', label='Y_com')
plt.xlabel('Time (s)')
plt.ylabel('Position (m)')
plt.title('COM Position vs Time')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('com_trajectory.png', dpi=300)
```

### Compute Swimming Speed

```python
# Compute velocity from position
dt = time[1] - time[0]
Vx_com = np.gradient(X_com, dt)
Vy_com = np.gradient(Y_com, dt)

# Swimming speed (magnitude)
V_swim = np.sqrt(Vx_com**2 + Vy_com**2)

# Steady-state swimming speed
steady_start = 5.0
mask = time > steady_start
V_steady = np.mean(V_swim[mask])
V_std = np.std(V_swim[mask])

print(f"Steady swimming speed: {V_steady:.6f} m/s")
print(f"Speed variation: {V_std:.6f} m/s")

# Plot
plt.figure(figsize=(10, 6))
plt.plot(time, V_swim, 'b-', linewidth=0.5)
plt.axhline(y=V_steady, color='r', linestyle='--',
            label=f'Mean = {V_steady:.4f} m/s')
plt.xlabel('Time (s)')
plt.ylabel('Swimming Speed (m/s)')
plt.title('Instantaneous Swimming Speed')
plt.legend()
plt.grid(True)
plt.savefig('swimming_speed.png', dpi=300)
```

### Compute Total Distance Traveled

```python
# Distance traveled
distance_x = X_com[-1] - X_com[0]
distance_y = Y_com[-1] - Y_com[0]
total_distance = np.sqrt(distance_x**2 + distance_y**2)

# Path length (actual swimming path)
dx = np.diff(X_com)
dy = np.diff(Y_com)
ds = np.sqrt(dx**2 + dy**2)
path_length = np.sum(ds)

print(f"Straight-line distance: {total_distance:.4f} m")
print(f"Actual path length: {path_length:.4f} m")
print(f"Path efficiency: {total_distance/path_length*100:.2f}%")

# Cost of transport
body_length = 0.1  # meters
body_lengths_traveled = total_distance / body_length
print(f"Distance: {body_lengths_traveled:.2f} body lengths")
```

### Check if Body is Tethered

```python
# Check if position is constant (tethered)
X_range = np.max(X_com) - np.min(X_com)
Y_range = np.max(Y_com) - np.min(Y_com)

tolerance = 1e-6  # meters

if X_range < tolerance and Y_range < tolerance:
    print("Body is TETHERED (position fixed)")
    print(f"  X_com = {np.mean(X_com):.6f} ± {X_range:.2e}")
    print(f"  Y_com = {np.mean(Y_com):.6f} ± {Y_range:.2e}")
else:
    print("Body is FREE SWIMMING (position varies)")
    print(f"  X_com range: {X_range:.6f} m")
    print(f"  Y_com range: {Y_range:.6f} m")
```

### Lateral Drift Analysis

```python
# Compute lateral drift (deviation from straight line)
# Fit linear trend to Y_com
from scipy import stats

# Skip transient
mask = time > steady_start
slope, intercept, r_value, p_value, std_err = stats.linregress(
    X_com[mask], Y_com[mask])

# Drift angle
drift_angle = np.arctan(slope) * 180 / np.pi
print(f"Lateral drift angle: {drift_angle:.4f} degrees")

if abs(drift_angle) < 1.0:
    print("Swimming is straight (minimal drift)")
else:
    print("Swimming has lateral drift")

# Plot trajectory with fit
plt.figure(figsize=(10, 6))
plt.plot(X_com, Y_com, 'b-', linewidth=2, label='Actual path')
X_fit = X_com[mask]
Y_fit = slope * X_fit + intercept
plt.plot(X_fit, Y_fit, 'r--', linewidth=2,
         label=f'Trend (angle={drift_angle:.2f}°)')
plt.xlabel('X (m)')
plt.ylabel('Y (m)')
plt.title('Swimming Path with Linear Fit')
plt.legend()
plt.axis('equal')
plt.grid(True)
plt.savefig('lateral_drift.png', dpi=300)
```

## Relationship to Other Files

### Translational Velocity

The COM velocity should match the translational velocity output:

```python
# Load translational velocity
vel_data = np.loadtxt('Eel2d_Trans_vel_struct_no_0')
time_vel = vel_data[:, 0]
Vx_direct = vel_data[:, 1]
Vy_direct = vel_data[:, 2]

# Compute from COM
Vx_from_com = np.gradient(X_com, dt)
Vy_from_com = np.gradient(Y_com, dt)

# Verify they match
error_x = np.max(np.abs(Vx_direct - Vx_from_com))
error_y = np.max(np.abs(Vy_direct - Vy_from_com))

print(f"Velocity error (x): {error_x:.2e}")
print(f"Velocity error (y): {error_y:.2e}")

# Should be very small (< 1e-10)
```

### Domain Boundaries

Check if body reaches domain boundaries:

```python
# Assuming domain is [0, L_x] × [0, L_y]
L_x = 10.0  # Domain length
L_y = 5.0   # Domain height

# Check boundaries
if np.any(X_com < 0.1) or np.any(X_com > L_x - 0.1):
    print("WARNING: Body near x-boundary!")
if np.any(Y_com < 0.1) or np.any(Y_com > L_y - 0.1):
    print("WARNING: Body near y-boundary!")

# Plot domain with trajectory
plt.figure(figsize=(12, 6))
plt.plot(X_com, Y_com, 'b-', linewidth=2)
plt.xlim([0, L_x])
plt.ylim([0, L_y])
plt.xlabel('X (m)')
plt.ylabel('Y (m)')
plt.title('Trajectory in Domain')
plt.grid(True)
plt.savefig('trajectory_in_domain.png', dpi=300)
```

## Input File Configuration

### To enable this output:

```
ConstraintIBMethod {
    PrintOutput {
        output_com_coords = TRUE
        output_interval = 1  // Every timestep
    }
}
```

### For free swimming:

```
ConstraintIBKinematics {
    calculate_translational_momentum = 1,1,0
    // Body can translate in x-y plane
}
```

### For tethered:

```
ConstraintIBKinematics {
    calculate_translational_momentum = 0,0,0
    // Body position is fixed
}
```

## Initial Position Setup

Set the initial COM position in the structure definition:

```
// In .vertex file or kinematics specification
center_of_mass = 0.5, 0.3, 0.0  // Initial (X,Y,Z)
```

## Troubleshooting

### Problem: COM is drifting unexpectedly

**Possible causes:**
1. Asymmetric swimming motion
2. External forces or flow
3. Numerical drift

**Solutions:**
- Check swimming kinematics symmetry
- Verify boundary conditions
- Check for numerical issues (reduce timestep)

### Problem: COM coordinates are NaN or Inf

**Possible causes:**
1. Numerical instability
2. Structure collapsing
3. Timestep too large

**Solutions:**
- Reduce timestep
- Check structural stiffness
- Verify mesh quality

### Problem: Body leaving domain

**Solution:**
```
// Use periodic boundary conditions or larger domain
Main {
    domain_boxes = [0.0, 0.0], [20.0, 10.0]  // Larger domain
}
```

## Physical Units

Ensure consistent units throughout:

```python
# Example: Convert to body lengths
body_length = 0.1  # m
X_com_BL = X_com / body_length
Y_com_BL = Y_com / body_length

# Non-dimensional time
swimming_frequency = 1.0  # Hz
time_nd = time * swimming_frequency
```

## See Also

- [Trans_vel_struct.md](./Trans_vel_struct.md) - Translational velocity
- [Drag_CV_strct_id.md](./Drag_CV_strct_id.md) - Forces causing motion
- [Rot_vel_struct.md](./Rot_vel_struct.md) - Rotational velocity

---

**Last updated:** 2025-12-30
**IBAMR version:** 0.18.0
