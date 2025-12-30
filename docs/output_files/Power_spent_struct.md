# <basename>_Power_spent_struct_no_N

## File Overview

**Filename pattern:** `Eel2d_Power_spent_struct_no_0`, `Foil_Power_spent_struct_no_1`, ...
**Created by:** `ConstraintIBMethod` kinematics output
**Size:** ~1-2 MB for typical simulation
**Format:** Tab-separated values (TSV)
**Alternate name:** `Power_strct_id_N.curve`

## Purpose

This file contains the **mechanical power** expenditure of the swimming body. It represents the rate at which the body does work on the surrounding fluid.

## File Format

### Column Structure

| Column | Name | Units | Description |
|--------|------|-------|-------------|
| 1 | `time` | seconds | Simulation time |
| 2 | `P_trans` | Watts (or non-dim) | Translational power |
| 3 | `P_rot` | Watts (or non-dim) | Rotational power |
| 4 | `P_total` | Watts (or non-dim) | Total power = P_trans + P_rot |

### Example Data - FREE SWIMMING

```
# time       P_trans     P_rot       P_total
0.000000    0.000000    0.000000    0.000000
1.000000    0.012345   -0.000123    0.012222
2.000000    0.023456    0.000234    0.023690
3.000000    0.018901   -0.000089    0.018812
5.000000    0.020123    0.000045    0.020168
```

### Example Data - TETHERED

```
# time       P_trans     P_rot       P_total
0.000000    0.000000    0.000000    0.000000
1.000000    0.034567    0.000000    0.034567
2.000000    0.045678    0.000000    0.045678
3.000000    0.038901    0.000000    0.038901
5.000000    0.041234    0.000000    0.041234
```

## Physical Formulation

### Power Components

**Translational Power:**
```
P_trans = F⃗_hydro · V⃗_com

Where:
- F⃗_hydro: Hydrodynamic force on body
- V⃗_com: Velocity of center of mass
```

**Rotational Power:**
```
P_rot = T⃗ · ω⃗

Where:
- T⃗: Torque on body
- ω⃗: Angular velocity
```

**Total Power:**
```
P_total = P_trans + P_rot
```

## Physical Interpretation

### Sign Convention

- **Positive P**: Body does work on fluid (energy output)
- **Negative P**: Fluid does work on body (energy input)

### For FREE SWIMMING

**Power represents:**
- Energy exchange between body and fluid
- **P_trans**: Work done by hydrodynamic forces
- **P_rot**: Work done by hydrodynamic torques (usually small)

**During acceleration:**
- P_total can be positive or negative
- Body converting internal energy to kinetic energy

**At steady swimming:**
- Mean P_trans ≈ 0 (force ≈ 0)
- Oscillates with swimming frequency

### For TETHERED (Thrust Measurement)

**Power represents:**
- **INPUT POWER**: Energy cost of swimming
- Work done by internal muscles/actuators
- Power to deform the body

**This is NOT the hydrodynamic power!**

For tethered case:
```
P_input = ∫ f⃗_internal · v⃗_local ds

Where:
- f⃗_internal: Internal forces from swimming
- v⃗_local: Local velocity of body surface
```

See [POWER_AND_EFFICIENCY_CALCULATIONS.md](../POWER_AND_EFFICIENCY_CALCULATIONS.md) for detailed power analysis.

## Propulsive Efficiency

### For Tethered Swimming

The propulsive efficiency is:

```
η = P_output / P_input

Where:
- P_output = -F_thrust * U_∞  (useful work)
- P_input = P_total  (from this file)
```

**Typical values:**
- Fish: η = 0.7 - 0.9
- Undulatory swimmers: η = 0.6 - 0.8
- Poor swimmers: η < 0.5

## Data Analysis Examples

### Compute Mean Power

```python
import numpy as np
import matplotlib.pyplot as plt

# Load power data
data = np.loadtxt('Eel2d_Power_spent_struct_no_0')
time = data[:, 0]
P_trans = data[:, 1]
P_rot = data[:, 2]
P_total = data[:, 3]

# Skip transient
steady_start = 5.0
mask = time > steady_start

# Statistics
P_trans_mean = np.mean(P_trans[mask])
P_total_mean = np.mean(P_total[mask])
P_trans_std = np.std(P_trans[mask])

print(f"Mean translational power: {P_trans_mean:.6e} W")
print(f"Mean total power: {P_total_mean:.6e} W")
print(f"Power oscillation: ± {P_trans_std:.6e} W")

# For tethered: this is input power
if P_total_mean > 0:
    print("Body is doing work on fluid (swimming)")
```

### Plot Power History

```python
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Translational power
axes[0].plot(time, P_trans, 'b-', linewidth=0.5)
axes[0].axhline(y=P_trans_mean, color='r', linestyle='--',
                label=f'Mean = {P_trans_mean:.4e} W')
axes[0].axhline(y=0, color='k', linestyle=':')
axes[0].set_ylabel('P_trans (W)')
axes[0].set_title('Translational Power')
axes[0].legend()
axes[0].grid(True)

# Total power
axes[1].plot(time, P_total, 'g-', linewidth=0.5)
axes[1].axhline(y=P_total_mean, color='r', linestyle='--',
                label=f'Mean = {P_total_mean:.4e} W')
axes[1].axhline(y=0, color='k', linestyle=':')
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('P_total (W)')
axes[1].set_title('Total Power')
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig('power_history.png', dpi=300)
```

### Compute Propulsive Efficiency (Tethered)

```python
# Load thrust force
force_data = np.loadtxt('Drag_CV_strct_id_0')
Fx = force_data[:, 1]

# Freestream velocity (from input file)
U_inf = 1.0  # m/s

# Output power (thrust * velocity)
# Note: Fx is negative for thrust, so -Fx is positive
P_output = -Fx * U_inf

# Input power (from this file)
P_input = P_total

# Efficiency
eta = P_output / P_input

# Mean efficiency (steady state)
eta_mean = np.mean(eta[mask])
eta_std = np.std(eta[mask])

print(f"\nPropulsive Efficiency:")
print(f"  Mean: {eta_mean:.4f} ({eta_mean*100:.2f}%)")
print(f"  Std:  {eta_std:.4f}")

# Plot
plt.figure(figsize=(10, 6))
plt.plot(time, eta, 'b-', linewidth=0.5)
plt.axhline(y=eta_mean, color='r', linestyle='--',
            label=f'Mean η = {eta_mean:.4f}')
plt.xlabel('Time (s)')
plt.ylabel('Efficiency η')
plt.title('Propulsive Efficiency = P_out / P_in')
plt.legend()
plt.grid(True)
plt.ylim([0, 1.2])
plt.savefig('propulsive_efficiency.png', dpi=300)
```

### Compute Energy Expenditure

```python
# Total energy spent during simulation
dt = time[1] - time[0]
E_total = np.trapz(P_total, time)  # Joules

print(f"\nEnergy Expenditure:")
print(f"  Total energy: {E_total:.6f} J")

# Energy per swimming cycle
swimming_freq = 1.0  # Hz
T_cycle = 1.0 / swimming_freq
E_per_cycle = P_total_mean * T_cycle
print(f"  Energy per cycle: {E_per_cycle:.6e} J/cycle")

# Energy per unit distance (cost of transport)
# For free swimming:
vel_data = np.loadtxt('Eel2d_Trans_vel_struct_no_0')
Vx = vel_data[:, 1]
V_mean = np.mean(Vx[mask])
distance = V_mean * (time[-1] - steady_start)

COT = E_total / distance  # J/m
print(f"  Cost of transport: {COT:.6e} J/m")
```

### Power Spectrum Analysis

```python
from scipy import signal

# Compute power spectral density
fs = 1.0 / dt
f, Pxx = signal.welch(P_trans[mask], fs=fs, nperseg=1024)

# Find dominant frequency
peak_idx = np.argmax(Pxx)
f_dominant = f[peak_idx]

print(f"\nPower Spectrum:")
print(f"  Dominant frequency: {f_dominant:.4f} Hz")
print(f"  Expected (swimming freq): {swimming_freq:.4f} Hz")

# Plot spectrum
plt.figure(figsize=(10, 6))
plt.semilogy(f, Pxx)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power Spectral Density')
plt.title('Power Spectrum')
plt.grid(True)
plt.savefig('power_spectrum.png', dpi=300)
```

### Verify Power Calculation

```python
# Power should equal Force · Velocity
force_data = np.loadtxt('Drag_CV_strct_id_0')
vel_data = np.loadtxt('Eel2d_Trans_vel_struct_no_0')

Fx = force_data[:, 1]
Fy = force_data[:, 2]
Vx = vel_data[:, 1]
Vy = vel_data[:, 2]

# Compute power from F·V
P_from_FV = Fx * Vx + Fy * Vy

# Compare with P_trans
# NOTE: For tethered, these won't match!
# P_trans from file is internal power
# P_from_FV is hydrodynamic power

plt.figure(figsize=(10, 6))
plt.plot(time, P_trans, 'b-', label='P_trans (from file)', linewidth=1)
plt.plot(time, P_from_FV, 'r--', label='F·V (computed)', linewidth=1)
plt.xlabel('Time (s)')
plt.ylabel('Power (W)')
plt.title('Power Comparison')
plt.legend()
plt.grid(True)
plt.savefig('power_comparison.png', dpi=300)

# For free swimming, they should match
# For tethered, they differ!
```

### Non-Dimensional Power Coefficient

```python
# Power coefficient
rho = 1000  # kg/m³
U_inf = 1.0  # m/s
chord = 0.1  # m

C_P = P_total_mean / (rho * U_inf**3 * chord**2)
print(f"\nPower coefficient C_P: {C_P:.6f}")
```

## Input File Configuration

### To enable this output:

```
ConstraintIBMethod {
    PrintOutput {
        output_power = TRUE
        output_interval = 1
    }
}
```

### For computing efficiency (tethered):

This power output is essential for efficiency calculations.
See [POWER_AND_EFFICIENCY_CALCULATIONS.md](../POWER_AND_EFFICIENCY_CALCULATIONS.md)

## Important Notes

### Tethered vs Free Swimming

**TETHERED:**
- `P_total` = Input power (energy cost)
- Used to compute efficiency: η = P_out / P_in
- Always positive (swimming requires energy)

**FREE SWIMMING:**
- `P_total` = F·V (hydrodynamic power)
- Can be positive or negative
- Mean ≈ 0 at steady state

## Troubleshooting

### Problem: Power is negative

**For tethered swimming:**
- Should always be positive
- If negative, check:
  - Force directions
  - Velocity signs
  - Swimming kinematics

**For free swimming:**
- Negative is possible
- Fluid doing work on body

### Problem: Power is too high

**Check:**
1. Units (dimensional vs non-dimensional)
2. Swimming amplitude not too large
3. Stiffness parameters reasonable

### Problem: Power oscillates wildly

**Possible causes:**
1. Numerical instability
2. Timestep too large
3. Deformation too violent

**Solutions:**
- Reduce dt
- Check structural parameters
- Smooth kinematics

## Related Files

### Required for Efficiency Calculation

```python
# Load all necessary files
P_input = P_total  # From this file
F_thrust = -Fx  # From Drag_CV_strct_id_0
U_inf = 1.0  # From input file

# Efficiency
eta = (F_thrust * U_inf) / P_input
```

See:
- [Drag_CV_strct_id.md](./Drag_CV_strct_id.md) - Force for output power
- [Trans_vel_struct.md](./Trans_vel_struct.md) - Velocity
- [../POWER_AND_EFFICIENCY_CALCULATIONS.md](../POWER_AND_EFFICIENCY_CALCULATIONS.md) - Complete guide

## Key References

1. **Liu et al. (1996)**: "A computational fluid dynamics study of tadpole swimming", *J. Exp. Biol.*
2. **Borazjani & Sotiropoulos (2008)**: "Numerical investigation of the hydrodynamics of carangiform swimming", *J. Exp. Biol.*

## See Also

- [Drag_CV_strct_id.md](./Drag_CV_strct_id.md) - Forces
- [Trans_vel_struct.md](./Trans_vel_struct.md) - Velocities
- [POWER_AND_EFFICIENCY_CALCULATIONS.md](../POWER_AND_EFFICIENCY_CALCULATIONS.md) - Detailed efficiency guide

---

**Last updated:** 2025-12-30
**IBAMR version:** 0.18.0
