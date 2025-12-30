# <basename>_Trans_vel_struct_no_N

## File Overview

**Filename pattern:** `Eel2d_Trans_vel_struct_no_0`, `Foil_Trans_vel_struct_no_1`, ...
**Created by:** `ConstraintIBMethod` kinematics output
**Size:** ~1-2 MB for typical simulation
**Format:** Tab-separated values (TSV)
**Alternate name:** `TranslationalVelocity_strct_id_N.curve`

## Purpose

This file contains the **translational velocity** of the structure's center of mass. It represents how fast the body is moving through the fluid.

## File Format

### Column Structure

| Column | Name | Units | Description |
|--------|------|-------|-------------|
| 1 | `time` | seconds | Simulation time |
| 2 | `Vx` | m/s (or non-dim) | Velocity in x-direction (streamwise) |
| 3 | `Vy` | m/s (or non-dim) | Velocity in y-direction (lateral) |
| 4 | `Vz` | m/s (or non-dim) | Velocity in z-direction (vertical) |

### Example Data - FREE SWIMMING

```
# time       Vx          Vy          Vz
0.000000    0.000000    0.000000    0.000000
1.000000    0.345678    0.001234    0.000000
2.000000    0.678901   -0.002345    0.000000
3.000000    0.912345    0.000876    0.000000
5.000000    1.034567   -0.000543    0.000000
```

### Example Data - TETHERED

```
# time       Vx          Vy          Vz
0.000000    0.000000    0.000000    0.000000
1.000000    0.000000    0.000000    0.000000
2.000000    0.000000    0.000000    0.000000
3.000000    0.000000    0.000000    0.000000
5.000000    0.000000    0.000000    0.000000
```

## Physical Interpretation

### Velocity Components

- **Vx**: Forward/backward swimming speed (primary direction)
- **Vy**: Lateral velocity (should be small for straight swimming)
- **Vz**: Vertical velocity (3D only, zero for 2D)

### For FREE SWIMMING Bodies

**Velocities evolve with time:**

**Startup phase (t < ~3 periods):**
- Vx increases from 0 (acceleration)
- Body gains momentum
- Swimming motion develops

**Steady swimming (t > ~5 periods):**
- Vx ≈ constant (steady speed)
- Small oscillations around mean
- Vy ≈ 0 (minimal lateral drift)

**Typical trajectory:**
```
t = 0s:    Vx = 0.0     (starting from rest)
t = 2s:    Vx = 0.5     (accelerating)
t = 5s:    Vx = 0.9     (approaching steady state)
t = 10s:   Vx = 1.0     (steady swimming speed)
```

### For TETHERED Bodies

**All velocities are zero:**
- Vx = 0 (no forward motion)
- Vy = 0 (no lateral motion)
- Vz = 0 (no vertical motion)

**Why?**
- Translational momentum flags = 0
- Body deforms but doesn't translate
- Position is held fixed

## Relationship to Forces

### Newton's Second Law

For free swimming:
```
M * dV/dt = F_hydro + F_internal

Where:
- M: Body mass
- V: Velocity vector (Vx, Vy, Vz)
- F_hydro: Hydrodynamic force (from Drag_CV file)
- F_internal: Internal swimming forces
```

At steady swimming:
```
dV/dt ≈ 0  →  F_hydro ≈ 0
```

Thrust balances drag!

## Data Analysis Examples

### Compute Steady Swimming Speed

```python
import numpy as np
import matplotlib.pyplot as plt

# Load velocity data
data = np.loadtxt('Eel2d_Trans_vel_struct_no_0')
time = data[:, 0]
Vx = data[:, 1]
Vy = data[:, 2]

# Skip transient
steady_start = 5.0  # seconds
mask = time > steady_start

# Compute mean velocity
Vx_mean = np.mean(Vx[mask])
Vy_mean = np.mean(Vy[mask])
V_magnitude = np.sqrt(Vx_mean**2 + Vy_mean**2)

print(f"Steady swimming speed:")
print(f"  Vx: {Vx_mean:.6f} m/s")
print(f"  Vy: {Vy_mean:.6f} m/s")
print(f"  |V|: {V_magnitude:.6f} m/s")

# Oscillation amplitude
Vx_std = np.std(Vx[mask])
print(f"  Vx oscillation: ± {Vx_std:.6f} m/s")

# Non-dimensional swimming speed
body_length = 0.1  # m
swimming_freq = 1.0  # Hz
U_nd = Vx_mean / (body_length * swimming_freq)
print(f"Non-dimensional speed: {U_nd:.4f} L/cycle")
```

### Plot Velocity vs Time

```python
fig, axes = plt.subplots(2, 1, figsize=(10, 8))

# Streamwise velocity
axes[0].plot(time, Vx, 'b-', linewidth=0.5)
axes[0].axhline(y=Vx_mean, color='r', linestyle='--',
                label=f'Mean = {Vx_mean:.4f} m/s')
axes[0].axvline(x=steady_start, color='gray', linestyle=':',
                label='Steady state start')
axes[0].set_ylabel('Vx (m/s)')
axes[0].set_title('Streamwise Velocity')
axes[0].legend()
axes[0].grid(True)

# Lateral velocity
axes[1].plot(time, Vy, 'g-', linewidth=0.5)
axes[1].axhline(y=Vy_mean, color='r', linestyle='--',
                label=f'Mean = {Vy_mean:.4e} m/s')
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Vy (m/s)')
axes[1].set_title('Lateral Velocity')
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig('velocity_history.png', dpi=300)
```

### Compute Acceleration

```python
# Numerical derivative
dt = time[1] - time[0]
ax = np.gradient(Vx, dt)
ay = np.gradient(Vy, dt)

# Plot acceleration
plt.figure(figsize=(10, 6))
plt.plot(time, ax, 'b-', linewidth=0.5, label='ax')
plt.plot(time, ay, 'r-', linewidth=0.5, label='ay')
plt.xlabel('Time (s)')
plt.ylabel('Acceleration (m/s²)')
plt.title('Acceleration vs Time')
plt.legend()
plt.grid(True)
plt.savefig('acceleration.png', dpi=300)

# Peak acceleration
ax_max = np.max(np.abs(ax))
print(f"Peak acceleration: {ax_max:.4f} m/s²")
```

### Verify Newton's Second Law

```python
# Load hydrodynamic force
force_data = np.loadtxt('Drag_CV_strct_id_0')
time_f = force_data[:, 0]
Fx = force_data[:, 1]

# Body mass (from input file)
body_mass = 0.01  # kg

# Compute acceleration from force
# F = M*a  →  a = F/M
ax_from_force = Fx / body_mass

# Compare with numerical derivative
# (Should match for free swimming)
plt.figure(figsize=(10, 6))
plt.plot(time, ax, 'b-', linewidth=1, label='From velocity')
plt.plot(time_f, ax_from_force, 'r--', linewidth=1, label='From force')
plt.xlabel('Time (s)')
plt.ylabel('Acceleration (m/s²)')
plt.title('Acceleration: Velocity vs Force')
plt.legend()
plt.grid(True)
plt.savefig('acceleration_comparison.png', dpi=300)
```

### Compute Strouhal Number

```python
# Strouhal number for oscillatory swimming
# St = f * A / U

# Swimming frequency (from FFT of velocity)
from scipy import signal
fs = 1.0 / dt
f, Pxx = signal.welch(Vx[mask], fs=fs, nperseg=1024)
peak_idx = np.argmax(Pxx)
swimming_freq = f[peak_idx]

# Amplitude of lateral motion (from Vy or body kinematics)
lateral_amplitude = 0.01  # m (from input file)

# Strouhal number
St = swimming_freq * lateral_amplitude / Vx_mean
print(f"Swimming frequency: {swimming_freq:.4f} Hz")
print(f"Strouhal number: {St:.4f}")

# Typical range for efficient swimming: 0.2 < St < 0.4
if 0.2 <= St <= 0.4:
    print("Strouhal number in efficient range!")
else:
    print("Strouhal number outside typical efficient range")
```

### Swimming Efficiency Metrics

```python
# Froude efficiency: η = (U / U_max)
# where U_max is theoretical maximum from kinematics

# Body length and swimming parameters
L = 0.1  # m
f = swimming_freq  # Hz
A = lateral_amplitude  # m

# Wave speed along body
c_wave = L * f  # m/s

# Froude efficiency
eta_froude = Vx_mean / c_wave
print(f"Wave speed: {c_wave:.4f} m/s")
print(f"Froude efficiency: {eta_froude:.4f}")

# Typical values:
# - Fish: 0.7 - 0.9
# - Undulatory swimmers: 0.6 - 0.8
```

### Check for Lateral Drift

```python
# Lateral drift indicates asymmetric swimming
lateral_drift_speed = Vy_mean
drift_angle = np.arctan2(Vy_mean, Vx_mean) * 180 / np.pi

print(f"Lateral drift speed: {lateral_drift_speed:.6f} m/s")
print(f"Drift angle: {drift_angle:.4f} degrees")

# For good straight swimming:
# |drift_angle| < 1 degree
if abs(drift_angle) < 1.0:
    print("Swimming is straight!")
else:
    print("Swimming has lateral drift")
```

## Relationship to Other Files

### Center of Mass Position

Verify velocity is derivative of position:

```python
# Load COM coordinates
com_data = np.loadtxt('Eel2d_COM_coordinates_struct_no_0')
time_com = com_data[:, 0]
X_com = com_data[:, 1]
Y_com = com_data[:, 2]

# Compute velocity from position
Vx_from_pos = np.gradient(X_com, dt)
Vy_from_pos = np.gradient(Y_com, dt)

# Should match Vx, Vy
error_x = np.max(np.abs(Vx - Vx_from_pos))
error_y = np.max(np.abs(Vy - Vy_from_pos))
print(f"Position-velocity consistency error: {max(error_x, error_y):.2e}")
```

### Power Calculation

Velocity appears in power calculation:

```python
# Load power
power_data = np.loadtxt('Eel2d_Power_spent_struct_no_0')
P_trans = power_data[:, 1]

# Power = Force · Velocity
P_from_FV = Fx * Vx  # Simplified, actual calculation more complex

# For free swimming at steady state:
# P_trans should correlate with swimming speed
```

## Input File Configuration

### To enable this output:

```
ConstraintIBMethod {
    PrintOutput {
        output_rig_transvel = TRUE
        output_interval = 1
    }
}
```

### For free swimming:

```
ConstraintIBKinematics {
    calculate_translational_momentum = 1,1,0
    // Vx, Vy will be non-zero
}
```

### For tethered:

```
ConstraintIBKinematics {
    calculate_translational_momentum = 0,0,0
    // Vx = Vy = Vz = 0
}
```

## Troubleshooting

### Problem: Velocity is always zero (free swimming expected)

**Check:**
1. `calculate_translational_momentum = 1,1,0`
2. Swimming kinematics are active
3. Body has correct mass/inertia
4. Simulation has run long enough

### Problem: Velocity doesn't reach steady state

**Possible causes:**
1. Simulation too short (need ~10 swimming periods)
2. Numerical instability
3. Domain too small (body hits boundary)

**Solution:**
```bash
# Check simulation time
tail Eel2d_Trans_vel_struct_no_0
# Should show times >> swimming period
```

### Problem: Velocity is negative

**This is normal!**
- Velocity direction depends on coordinate system
- Negative Vx means swimming in -x direction
- Check initial body orientation

## Physical Units

### Dimensional velocity:
```python
Vx_dimensional = Vx  # m/s
```

### Non-dimensional velocity:
```python
# Option 1: Body lengths per second
Vx_BL_per_s = Vx / body_length

# Option 2: Body lengths per swimming cycle
Vx_BL_per_cycle = Vx / (body_length * swimming_freq)

# Option 3: Fraction of wave speed
Vx_relative = Vx / (body_length * swimming_freq)
```

## See Also

- [COM_coordinates.md](./COM_coordinates.md) - Position (integral of velocity)
- [Drag_CV_strct_id.md](./Drag_CV_strct_id.md) - Forces causing acceleration
- [Rot_vel_struct.md](./Rot_vel_struct.md) - Rotational velocity
- [Power_spent_struct.md](./Power_spent_struct.md) - Power = Force · Velocity

---

**Last updated:** 2025-12-30
**IBAMR version:** 0.18.0
