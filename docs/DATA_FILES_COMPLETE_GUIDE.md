# IBAMR Output Files: Complete Data Structure Guide

## Overview

This document provides detailed descriptions of ALL output files from IBAMR simulations with immersed swimming bodies (fish, hydrofoils, etc.). **Two configurations** are covered:

1. **FREE SWIMMING** - Body can translate and rotate
2. **TETHERED** - Body deforms but position/orientation is fixed

---

# TABLE OF CONTENTS

1. [Control Volume Force Files](#control-volume-force-files)
2. [Structure-Specific Files (ConstraintIBMethod Output)](#structure-specific-files)
3. [Visualization Files](#visualization-files)
4. [Configuration Differences](#configuration-differences)

---

# CONTROL VOLUME FORCE FILES

These files are created by `CustomIBHydrodynamicForceEvaluator` (or standard `IBHydrodynamicForceEvaluator`) using Reynolds Transport Theorem applied to a moving control volume.

**Location:** Main output directory (where simulation runs)

---

## Mathematical Formulation

### Reynolds Transport Theorem for Forces

The total hydrodynamic force on an immersed body is computed from a control volume (CV) surrounding the body:

**Dimensional Equation:**
```
F⃗ = -d/dt∫∫∫_CV ρu⃗ dV + d/dt P⃗_body + ∫∫_∂CV (-pI + μ(∇u⃗ + ∇u⃗ᵀ))·n⃗ dA - ∫∫_∂CV ρ(u⃗·n⃗)u⃗ dA
```

**Decomposed into 4 components:**

| Component | Symbol | Equation | Physical Meaning |
|-----------|--------|----------|------------------|
| **Unsteady** | `F_unsteady` | `-d/dt∫∫∫_CV ρu⃗ dV + d/dt P⃗_body` | Time rate of change of fluid + body momentum |
| **Pressure** | `F_pressure` | `∫∫_∂CV (-pn⃗) dA` | Pressure traction on CV surface |
| **Viscous** | `F_viscous` | `∫∫_∂CV μ(∇u⃗ + ∇u⃗ᵀ)·n⃗ dA` | Viscous stress on CV surface |
| **Momentum** | `F_momentum` | `-∫∫_∂CV ρ(u⃗·n⃗)u⃗ dA` | Momentum flux across CV boundary |

**Conservation Identity (verified to machine precision):**
```
F_total = F_pressure + F_viscous + F_momentum + F_unsteady
```

### Non-Dimensionalization

All forces can be non-dimensionalized using dynamic pressure:

```
C_F = F / (0.5 ρ U_∞² L_ref A_ref)
```

Where:
- `ρ`: Fluid density (kg/m³)
- `U_∞`: Reference velocity (freestream or swimming speed) (m/s)
- `L_ref`: Reference length (chord, body length) (m)
- `A_ref`: Reference area (projected area or L_ref × span) (m²)

**Example for 2D:**
```
C_D = F_x / (0.5 ρ U_∞² C)    # Drag coefficient
C_L = F_y / (0.5 ρ U_∞² C)    # Lift coefficient
```

Where `C` is chord length and unit span length is assumed.

---

## File: `Drag_CV_strct_id_0`

**Created by:** `CustomIBHydrodynamicForceEvaluator::postprocessIntegrateData()`
**Code location:** `CustomIBHydrodynamicForceEvaluator.cpp` lines 860-865
**Function call:**
```cpp
*force_obj.drag_CV_stream << new_time << '\t'
                          << force_obj.F_new(0) << '\t'
                          << force_obj.F_new(1) << '\t'
                          << force_obj.F_new(2) << std::endl;
```

**Size:** ~3-4 MB for typical simulation
**Format:** Tab-separated values
**Equation computed:** `F_new = F_pressure + F_viscous + F_momentum + F_unsteady`
**Code location for computation:** `CustomIBHydrodynamicForceEvaluator.cpp` line 839

### FREE SWIMMING Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Fx` | N (dimensional) or non-dim | Force in x-direction (streamwise) | Oscillates, mean ≈ 0 at steady swimming |
| 3 | `Fy` | N (dimensional) or non-dim | Force in y-direction (lateral) | Oscillates around 0 |
| 4 | `Fz` | N (dimensional) or non-dim | Force in z-direction (0 for 2D) | 0.0 (2D) |

**Physical meaning:**
- **Fx**: Hydrodynamic force opposing motion (transient during acceleration)
- **Fy**: Lateral forces from swimming oscillations
- **At steady swimming:** Mean Fx ≈ 0 (thrust balances drag)
- **During acceleration:** Net force drives body forward

**Sign convention:**
- Positive Fx = Drag (opposes motion)
- Negative Fx = Net thrust (accelerating forward)

### TETHERED Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Fx` | N (dimensional) or non-dim | **Net thrust** in x-direction | Oscillates, mean = thrust production |
| 3 | `Fy` | N (dimensional) or non-dim | Lateral force | Oscillates around 0 |
| 4 | `Fz` | N (dimensional) or non-dim | Force in z-direction (0 for 2D) | 0.0 (2D) |

**Physical meaning:**
- **Fx**: Net propulsive thrust (what you'd measure on force transducer)
- **Fy**: Lateral forces from swimming oscillations
- **Mean Fx < 0**: Body produces net thrust (typical for efficient swimming)
- **Mean Fx > 0**: Body experiences net drag (inefficient swimming)

**Sign convention:**
- Negative Fx = Thrust (body pushing fluid backward)
- Positive Fx = Drag (fluid pushing body backward)

**Example data:**
```
# time       Fx          Fy          Fz
0.000000    0.000000    0.000000    0.000000
0.000100   -0.123456    0.012345    0.000000
0.000200   -0.234567    0.023456    0.000000
```

---

## File: `Torque_CV_strct_id_0`

**Created by:** `CustomIBHydrodynamicForceEvaluator::postprocessIntegrateData()`
**Code location:** `CustomIBHydrodynamicForceEvaluator.cpp` lines 866-867
**Function call:**
```cpp
*force_obj.torque_CV_stream << new_time << '\t'
                            << force_obj.T_new(0) << '\t'
                            << force_obj.T_new(1) << '\t'
                            << force_obj.T_new(2) << std::endl;
```

**Size:** ~2-3 MB for typical simulation
**Format:** Tab-separated values
**Equation computed:** `T_new = -(L_box_new - L_box_current)/dt + (L_new - L_current)/dt + torque_trac`
**Code location for computation:** `CustomIBHydrodynamicForceEvaluator.cpp` line 847

### FREE SWIMMING Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Tx` | N·m or non-dim | Torque about x-axis (0 for 2D) | 0.0 (2D) |
| 3 | `Ty` | N·m or non-dim | Torque about y-axis (0 for 2D) | 0.0 (2D) |
| 4 | `Tz` | N·m or non-dim | Torque about z-axis (in-plane) | Oscillates for turning |

**Physical meaning:**
- **Tz**: Hydrodynamic moment causing rotation
- Used for maneuvering, turning
- Mean ≈ 0 for straight swimming

### TETHERED Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Tx` | N·m or non-dim | Torque about x-axis (0 for 2D) | 0.0 (2D) |
| 3 | `Ty` | N·m or non-dim | Torque about y-axis (0 for 2D) | 0.0 (2D) |
| 4 | `Tz` | N·m or non-dim | Torque about z-axis | Oscillates, mean ≈ 0 |

**Physical meaning:**
- **Tz**: Rotational moment from swimming (usually small if symmetric)
- For symmetric swimming: mean Tz ≈ 0
- For asymmetric swimming: non-zero mean indicates turning tendency

**Example data:**
```
# time       Tx          Ty          Tz
0.000000    0.000000    0.000000    0.000000
0.000100    0.000000    0.000000   -0.001234
0.000200    0.000000    0.000000   -0.002345
```

---

## File: `Pressure_CV_strct_id_0`

**Created by:** `CustomIBHydrodynamicForceEvaluator::postprocessIntegrateData()`
**Code location:** `CustomIBHydrodynamicForceEvaluator.cpp` lines 870-871
**Function call:**
```cpp
*force_obj.pressure_CV_stream << new_time << '\t'
                              << force_obj.F_pressure_new(0) << '\t'
                              << force_obj.F_pressure_new(1) << '\t'
                              << force_obj.F_pressure_new(2) << std::endl;
```

**Size:** ~3-4 MB for typical simulation
**Format:** Tab-separated values
**Equation computed:** `F_pressure = ∫∫_∂CV (-p n⃗) dA`
**Code location for computation:** `CustomIBHydrodynamicForceEvaluator.cpp` lines 734-736, 835

### Physical Meaning

**Pressure contribution** to total hydrodynamic force:
- Represents pressure traction on the control volume surface (NOT body surface)
- Includes both steady and unsteady pressure effects
- Integrated over the CV boundary surface

**Key implementation:**
```cpp
// Line 734-736: Accumulate pressure force
IBTK::Vector3d pressure_force = -pn * dA;
trac += pressure_force;           // Add to total
trac_pressure += pressure_force;  // Track separately

// Line 835: Store after MPI reduction
fobj.F_pressure_new = trac_pressure;
```

### Both Cases (FREE SWIMMING and TETHERED)

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Fp_x` | N (dimensional) or non-dim | Pressure force in x-direction | Oscillates |
| 3 | `Fp_y` | N (dimensional) or non-dim | Pressure force in y-direction | Oscillates |
| 4 | `Fp_z` | N (dimensional) or non-dim | Pressure force in z-direction | 0.0 (2D) |

**Example data:**
```
# time       Fp_x        Fp_y        Fp_z
0.000000    0.000000    0.000000    0.000000
0.000100   -0.089123    0.008234    0.000000
0.000200   -0.178456    0.016789    0.000000
```

---

## File: `Viscous_CV_strct_id_0`

**Created by:** `CustomIBHydrodynamicForceEvaluator::postprocessIntegrateData()`
**Code location:** `CustomIBHydrodynamicForceEvaluator.cpp` lines 872-873
**Function call:**
```cpp
*force_obj.viscous_CV_stream << new_time << '\t'
                             << force_obj.F_viscous_new(0) << '\t'
                             << force_obj.F_viscous_new(1) << '\t'
                             << force_obj.F_viscous_new(2) << std::endl;
```

**Size:** ~3-4 MB for typical simulation
**Format:** Tab-separated values
**Equation computed:** `F_viscous = ∫∫_∂CV μ(∇u⃗ + ∇u⃗ᵀ)·n⃗ dA`
**Code location for computation:** `CustomIBHydrodynamicForceEvaluator.cpp` lines 811-813, 836

### Physical Meaning

**Viscous stress contribution** to total hydrodynamic force:
- Represents viscous traction on the control volume surface
- Includes both normal and tangential viscous stresses
- Proportional to fluid viscosity μ and velocity gradients

**Key implementation:**
```cpp
// Line 811-813: Accumulate viscous force
IBTK::Vector3d viscous_trac = n_dot_T * dA;
trac += viscous_trac;
trac_viscous += viscous_trac;

// Line 836: Store after MPI reduction
fobj.F_viscous_new = trac_viscous;
```

### Both Cases (FREE SWIMMING and TETHERED)

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Fv_x` | N (dimensional) or non-dim | Viscous force in x-direction | Smaller than pressure |
| 3 | `Fv_y` | N (dimensional) or non-dim | Viscous force in y-direction | Oscillates |
| 4 | `Fv_z` | N (dimensional) or non-dim | Viscous force in z-direction | 0.0 (2D) |

**Scaling:** At moderate Reynolds numbers (Re ~ 1000-10000), viscous forces are typically 10-30% of pressure forces.

**Example data:**
```
# time       Fv_x        Fv_y        Fv_z
0.000000    0.000000    0.000000    0.000000
0.000100   -0.012345    0.001234    0.000000
0.000200   -0.024567    0.002456    0.000000
```

---

## File: `Momentum_CV_strct_id_0`

**Created by:** `CustomIBHydrodynamicForceEvaluator::postprocessIntegrateData()`
**Code location:** `CustomIBHydrodynamicForceEvaluator.cpp` lines 874-875
**Function call:**
```cpp
*force_obj.momentum_CV_stream << new_time << '\t'
                              << force_obj.F_momentum_new(0) << '\t'
                              << force_obj.F_momentum_new(1) << '\t'
                              << force_obj.F_momentum_new(2) << std::endl;
```

**Size:** ~3-4 MB for typical simulation
**Format:** Tab-separated values
**Equation computed:** `F_momentum = -∫∫_∂CV ρ(u⃗·n⃗)u⃗ dA`
**Code location for computation:** `CustomIBHydrodynamicForceEvaluator.cpp` lines 757-759, 837

### Physical Meaning

**Momentum flux contribution** to total hydrodynamic force:
- Represents convective momentum transport across CV boundary
- Captures wake effects and jet formation
- Important for swimming/propulsion analysis

**Key implementation:**
```cpp
// Line 757-759: Accumulate momentum flux
IBTK::Vector3d momentum_force = -d_rho * n.dot(u) * u * dA;
trac += momentum_force;
trac_momentum += momentum_force;

// Line 837: Store after MPI reduction
fobj.F_momentum_new = trac_momentum;
```

### Both Cases (FREE SWIMMING and TETHERED)

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Fm_x` | N (dimensional) or non-dim | Momentum flux in x-direction | Oscillates |
| 3 | `Fm_y` | N (dimensional) or non-dim | Momentum flux in y-direction | Oscillates |
| 4 | `Fm_z` | N (dimensional) or non-dim | Momentum flux in z-direction | 0.0 (2D) |

**Significance:**
- For tethered swimming: captures thrust generation from wake momentum
- For free swimming: represents momentum exchange with surrounding fluid
- Can be negative (fluid flowing into CV) or positive (fluid flowing out)

**Example data:**
```
# time       Fm_x        Fm_y        Fm_z
0.000000    0.000000    0.000000    0.000000
0.000100   -0.022111    0.003001    0.000000
0.000200   -0.044234    0.006123    0.000000
```

---

## File: `Unsteady_CV_strct_id_0`

**Created by:** `CustomIBHydrodynamicForceEvaluator::postprocessIntegrateData()`
**Code location:** `CustomIBHydrodynamicForceEvaluator.cpp` lines 876-877
**Function call:**
```cpp
*force_obj.unsteady_CV_stream << new_time << '\t'
                              << force_obj.F_unsteady_new(0) << '\t'
                              << force_obj.F_unsteady_new(1) << '\t'
                              << force_obj.F_unsteady_new(2) << std::endl;
```

**Size:** ~3-4 MB for typical simulation
**Format:** Tab-separated values
**Equation computed:** `F_unsteady = -d/dt∫∫∫_CV ρu⃗ dV + d/dt P⃗_body`
**Code location for computation:** `CustomIBHydrodynamicForceEvaluator.cpp` line 840

### Physical Meaning

**Unsteady (inertial) contribution** to total hydrodynamic force:
- Time rate of change of fluid momentum in control volume
- Time rate of change of body momentum
- Dominant during acceleration/deceleration
- Small during steady periodic motion

**Key implementation:**
```cpp
// Line 840: Compute unsteady component
fobj.F_unsteady_new = -(fobj.P_box_new - fobj.P_box_current) / dt  // Fluid momentum change
                    + (fobj.P_new - fobj.P_current) / dt;          // Body momentum change
```

Where:
- `P_box_new/current`: Fluid momentum `∫∫∫_CV ρu⃗ dV`
- `P_new/current`: Body momentum `M_body v⃗_body`
- `dt`: Timestep size

### Both Cases (FREE SWIMMING and TETHERED)

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Fu_x` | N (dimensional) or non-dim | Unsteady force in x-direction | Large initially, small later |
| 3 | `Fu_y` | N (dimensional) or non-dim | Unsteady force in y-direction | Oscillates |
| 4 | `Fu_z` | N (dimensional) or non-dim | Unsteady force in z-direction | 0.0 (2D) |

**Behavior:**
- **Startup phase** (t < 2-3 periods): Large as flow develops
- **Periodic steady state**: Small oscillations around mean
- **FREE SWIMMING**: Non-zero during acceleration, near-zero at steady speed
- **TETHERED**: Periodic oscillations at swimming frequency

**Example data:**
```
# time       Fu_x        Fu_y        Fu_z
0.000000    0.000000    0.000000    0.000000
0.000100   -0.000123    0.000011    0.000000
0.000200   -0.000234    0.000022    0.000000
```

---

### Force Conservation Verification

**CRITICAL:** All four components must sum to the total force at every timestep:

```
F_total = F_pressure + F_viscous + F_momentum + F_unsteady
```

**Verification script (Python):**

```python
import numpy as np

# Load all force components
t, Fx_total, Fy_total, Fz_total = np.loadtxt('Drag_CV_strct_id_0', unpack=True)
_, Fx_p, Fy_p, Fz_p = np.loadtxt('Pressure_CV_strct_id_0', unpack=True)
_, Fx_v, Fy_v, Fz_v = np.loadtxt('Viscous_CV_strct_id_0', unpack=True)
_, Fx_m, Fy_m, Fz_m = np.loadtxt('Momentum_CV_strct_id_0', unpack=True)
_, Fx_u, Fy_u, Fz_u = np.loadtxt('Unsteady_CV_strct_id_0', unpack=True)

# Verify conservation (should be ~1e-14 machine precision)
err_x = np.abs(Fx_total - (Fx_p + Fx_v + Fx_m + Fx_u))
err_y = np.abs(Fy_total - (Fy_p + Fy_v + Fy_m + Fy_u))
err_z = np.abs(Fz_total - (Fz_p + Fz_v + Fz_m + Fz_u))

max_error = max([np.max(err_x), np.max(err_y), np.max(err_z)])
print(f'Maximum decomposition error: {max_error:.3e}')
# Expected output: Maximum decomposition error: ~1e-14
```

**If conservation fails:**
- Error > 1e-10: Check that all 4 component files exist
- Missing `Unsteady_CV` file: Common error, verify CustomIBHydrodynamicForceEvaluator has unsteady output
- Large error (> 1e-6): Numerical issue, check timestep size and mesh resolution

---

# STRUCTURE-SPECIFIC FILES

These files are created by `ConstraintIBMethod` for detailed body kinematics.
**Location:** Output directory specified in input file (e.g., `./Eel2dStr/`)

## File: `<basename>_Drag_strct_id_0.curve`

**Example:** `Eel2d_Drag_strct_id_0.curve`
**Created when:** `output_drag = TRUE` in PrintOutput block
**Size:** ~2-4 MB

### FREE SWIMMING Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Fx` | Force units | Drag force in x-direction | Similar to Drag_CV file |
| 3 | `Fy` | Force units | Drag force in y-direction | Oscillates |
| 4 | `Fz` | Force units | Drag force in z-direction | 0.0 (2D) |
| 5 | `Fx_alt` | Force units | Alternative calculation (may be duplicate) | Same as column 2 |
| 6 | `Fy_alt` | Force units | Alternative calculation (may be duplicate) | Same as column 3 |
| 7 | `Fz_alt` | Force units | Alternative calculation (may be duplicate) | 0.0 (2D) |

**Note:** Columns 5-7 may be duplicates or alternative force calculation methods.

### TETHERED Case

**Same column structure as free swimming.**

**Physical meaning:**
- Forces computed directly on immersed structure
- Should match `Drag_CV_strct_id_0` (different calculation method)
- Used for validation and cross-checking

---

## File: `<basename>_Torque_strct_id_0.curve`

**Example:** `Eel2d_Torque_strct_id_0.curve`
**Created when:** `output_torque = TRUE`

### Both Cases (FREE SWIMMING and TETHERED)

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Tx` | Torque units | Torque about x-axis | 0.0 (2D) |
| 3 | `Ty` | Torque units | Torque about y-axis | 0.0 (2D) |
| 4 | `Tz` | Torque units | Torque about z-axis | Oscillates |
| 5 | `Tx_alt` | Torque units | Alternative calculation | 0.0 (2D) |
| 6 | `Ty_alt` | Torque units | Alternative calculation | 0.0 (2D) |
| 7 | `Tz_alt` | Torque units | Alternative calculation | Same as column 4 |

---

## File: `<basename>_Power_strct_id_0.curve`

**Example:** `Eel2d_Power_strct_id_0.curve`
**Created when:** `output_power = TRUE`

### FREE SWIMMING Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `P_trans` | Watts or non-dim | Translational power (F·v) | Varies |
| 3 | `P_rot` | Watts or non-dim | Rotational power (T·ω) | Small for 2D |
| 4 | `P_total` | Watts or non-dim | Total power = P_trans + P_rot | Positive = energy input |

**Physical meaning:**
- **P_trans**: Power from translational motion (F·V_com)
- **P_rot**: Power from rotational motion (T·ω)
- **P_total**: Total mechanical power expenditure
- Positive = fish putting energy into fluid
- Negative = fish extracting energy from fluid

### TETHERED Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `P_trans` | Watts or non-dim | Power from deformation | Oscillates |
| 3 | `P_rot` | Watts or non-dim | Rotational power | ≈ 0 (no rotation) |
| 4 | `P_total` | Watts or non-dim | Total power = internal swimming work | Positive |

**Physical meaning:**
- **P_trans**: Power from internal swimming motion
- **P_rot**: ≈ 0 (body doesn't rotate)
- **P_total**: Energy cost of swimming
- Always positive (swimming requires energy input)

---

## File: `<basename>_TranslationalVelocity_strct_id_0.curve`

**Example:** `Eel2d_TranslationalVelocity_strct_id_0.curve`
**Created when:** `output_rig_transvel = TRUE`

### FREE SWIMMING Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Vx` | m/s or non-dim | Velocity in x-direction | Increases during acceleration |
| 3 | `Vy` | m/s or non-dim | Velocity in y-direction | ≈ 0 for straight swimming |
| 4 | `Vz` | m/s or non-dim | Velocity in z-direction | 0.0 (2D) |

**Physical meaning:**
- **Vx**: Forward swimming speed
- **Vy**: Lateral motion (should be small)
- At steady swimming: Vx = constant
- During acceleration: Vx increases

**Example trajectory:**
```
time=0.0:  Vx=0.0 (starting from rest)
time=5.0:  Vx=0.5 (accelerating)
time=10.0: Vx=1.0 (steady swimming)
```

### TETHERED Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Vx` | m/s or non-dim | Velocity in x-direction | **0.0** (fixed) |
| 3 | `Vy` | m/s or non-dim | Velocity in y-direction | **0.0** (fixed) |
| 4 | `Vz` | m/s or non-dim | Velocity in z-direction | **0.0** (2D) |

**Physical meaning:**
- **All velocities = 0** (body is tethered)
- Body doesn't move despite swimming motion
- This is enforced by momentum flags = 0

**Example data:**
```
# time       Vx          Vy          Vz
0.000000    0.000000    0.000000    0.000000
0.000100    0.000000    0.000000    0.000000
0.000200    0.000000    0.000000    0.000000
(all zeros throughout)
```

---

## File: `<basename>_RotationalVelocity_strct_id_0.curve`

**Example:** `Eel2d_RotationalVelocity_strct_id_0.curve`
**Created when:** `output_rig_rotvel = TRUE`

### FREE SWIMMING Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `ωx` | rad/s or non-dim | Angular velocity about x-axis | 0.0 (2D) |
| 3 | `ωy` | rad/s or non-dim | Angular velocity about y-axis | 0.0 (2D) |
| 4 | `ωz` | rad/s or non-dim | Angular velocity about z-axis | Non-zero for turning |

**Physical meaning:**
- **ωz**: Turning rate (change in heading)
- Positive = counter-clockwise rotation
- Negative = clockwise rotation
- ≈ 0 for straight swimming

### TETHERED Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `ωx` | rad/s or non-dim | Angular velocity about x-axis | 0.0 (2D) |
| 3 | `ωy` | rad/s or non-dim | Angular velocity about y-axis | 0.0 (2D) |
| 4 | `ωz` | rad/s or non-dim | Angular velocity about z-axis | **0.0** (fixed) |

**Physical meaning:**
- **All angular velocities = 0** (body orientation fixed)
- Body doesn't rotate despite swimming motion
- Enforced by rotational momentum flags = 0

---

## File: `<basename>_COMcoords_strct_id_0.curve`

**Example:** `Eel2d_COMcoords_strct_id_0.curve`
**Created when:** `output_com_coords = TRUE`

### FREE SWIMMING Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `X_com` | meters or non-dim | Center of mass x-coordinate | Increases with forward motion |
| 3 | `Y_com` | meters or non-dim | Center of mass y-coordinate | ≈ constant for straight swimming |
| 4 | `Z_com` | meters or non-dim | Center of mass z-coordinate | Constant (2D) |

**Physical meaning:**
- **X_com**: Streamwise position of center of mass
- **Y_com**: Lateral position (should stay near initial value)
- Track body trajectory through domain

**Example trajectory:**
```
time=0.0:  X_com=0.0, Y_com=0.0 (starting position)
time=5.0:  X_com=2.5, Y_com=0.1 (moved forward)
time=10.0: X_com=5.0, Y_com=0.2 (continued forward)
```

### TETHERED Case

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `X_com` | meters or non-dim | Center of mass x-coordinate | **Constant** |
| 3 | `Y_com` | meters or non-dim | Center of mass y-coordinate | **Constant** |
| 4 | `Z_com` | meters or non-dim | Center of mass z-coordinate | **Constant** (2D) |

**Physical meaning:**
- **All coordinates constant** (body position fixed)
- Center of mass stays at initial location
- Body deforms around this fixed point

**Example data:**
```
# time       X_com       Y_com       Z_com
0.000000    0.500000    0.300000    0.000000
0.000100    0.500000    0.300000    0.000000
0.000200    0.500000    0.300000    0.000000
(constant throughout)
```

---

## File: `<basename>_MomentInertia_strct_id_0.curve`

**Example:** `Eel2d_MomentInertia_strct_id_0.curve`
**Created when:** `output_moment_inertia = TRUE`

### Both Cases (FREE SWIMMING and TETHERED)

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Ixx` | kg·m² or non-dim | Moment of inertia about x-axis | Constant or varies slightly |
| 3 | `Iyy` | kg·m² or non-dim | Moment of inertia about y-axis | Constant or varies slightly |
| 4 | `Izz` | kg·m² or non-dim | Moment of inertia about z-axis | Changes with deformation |
| 5 | `Ixy` | kg·m² or non-dim | Product of inertia | ≈ 0 for symmetric bodies |
| 6 | `Ixz` | kg·m² or non-dim | Product of inertia | 0.0 (2D) |
| 7 | `Iyz` | kg·m² or non-dim | Product of inertia | 0.0 (2D) |

**Physical meaning:**
- **Ixx, Iyy, Izz**: Diagonal terms of inertia tensor
- **Ixy, Ixz, Iyz**: Off-diagonal terms (products of inertia)
- Changes as body deforms during swimming
- For rigid body: constant
- For deforming body: varies with swimming cycle

---

## File: `<basename>_EulerianMomentum_strct_id_0.curve`

**Example:** `Eel2d_EulerianMomentum_strct_id_0.curve`
**Created when:** `output_eulerian_mom = TRUE`

### Both Cases (FREE SWIMMING and TETHERED)

| Column | Name | Units | Description | Typical Range |
|--------|------|-------|-------------|---------------|
| 1 | `time` | seconds | Simulation time | 0.0 → end_time |
| 2 | `Px_euler` | Momentum units | Eulerian momentum in x-direction | Varies |
| 3 | `Py_euler` | Momentum units | Eulerian momentum in y-direction | Varies |
| 4 | `Pz_euler` | Momentum units | Eulerian momentum in z-direction | 0.0 (2D) |

**Physical meaning:**
- **Eulerian momentum**: ∫∫∫ ρu dV over Eulerian grid
- Tracks fluid momentum in grid reference frame
- Different from Lagrangian (body) momentum
- Used in Reynolds Transport Theorem

---

# VISUALIZATION FILES

**Location:** Visualization directory (e.g., `viz_eel2d_Str/`)

## Lagrangian Data Files

### File: `lag_data.cycle_NNNNNN.silo`

**Format:** Silo binary format (readable by VisIt)
**Frequency:** Every `viz_dump_interval` cycles
**Size:** ~10-20 MB per file
**Total:** ~1600 snapshots for long simulation

**Contains:**
- Lagrangian marker positions (X, Y, Z)
- Body surface geometry
- Deformation state

**Both Cases:** Same format, but positions differ:
- **Free swimming:** Body moves through domain
- **Tethered:** Body stays at fixed location but deforms

### How to Read:

```python
# Using VisIt or Python bindings
import visit
visit.OpenDatabase("viz_eel2d_Str/dumps.visit")
visit.AddPlot("Mesh", "lag_data")
visit.DrawPlots()
```

---

## Eulerian Data Files

### File: `dumps.cycle_NNNNNN.silo`

**Format:** Silo binary format
**Contains:**
- Velocity field (u, v, w)
- Pressure field (p)
- Vorticity field (ω)
- Divergence of velocity (∇·u)

**Column structure:** Structured grid data

### Typical Fields:

| Field Name | Description | Units |
|------------|-------------|-------|
| `velocity` | Velocity vector (u, v, w) | m/s or non-dim |
| `pressure` | Pressure field | Pa or non-dim |
| `vorticity` | Vorticity (curl of velocity) | 1/s or non-dim |
| `div_u` | Divergence of velocity | 1/s or non-dim |

**Both Cases:** Same format
- **Free swimming:** Wake moves with body
- **Tethered:** Wake emanates from fixed body position

---

# CONFIGURATION DIFFERENCES

## Input File Settings

### FREE SWIMMING

```
ConstraintIBKinematics {
    calculate_translational_momentum = 1,1,0
    calculate_rotational_momentum    = 0,0,1

    # Body can translate in x-y plane
    # Body can rotate about z-axis
}
```

**Result:**
- Body moves through domain
- Velocities in `TranslationalVelocity` are non-zero
- Position in `COMcoords` changes with time
- Forces approach zero at steady swimming

### TETHERED

```
ConstraintIBKinematics {
    calculate_translational_momentum = 0,0,0
    calculate_rotational_momentum    = 0,0,0

    # Body CANNOT translate
    # Body CANNOT rotate
}
```

**Result:**
- Body stays fixed in space
- Velocities in `TranslationalVelocity` = 0
- Position in `COMcoords` = constant
- Forces = net thrust production

---

## File Content Summary Table

| File | FREE SWIMMING | TETHERED | Key Difference |
|------|---------------|----------|----------------|
| `Drag_CV_strct_id_0` | Fx ≈ 0 at steady state | Fx = thrust | Interpretation |
| `TranslationalVelocity` | Vx increases | Vx = 0 | Body motion |
| `RotationalVelocity` | ωz varies | ωz = 0 | Body rotation |
| `COMcoords` | Position changes | Position constant | Body trajectory |
| `Power` | P_trans from motion | P_trans from deformation | Power source |
| Visualization | Body moves | Body fixed | Visual appearance |

---

## Quick Reference

### FREE SWIMMING - Expected Values

```
Time = 0s (start):
  Drag_CV: Fx ≈ 0, Fy ≈ 0
  TransVel: Vx = 0, Vy = 0
  COMcoords: X_com = 0.0, Y_com = 0.0

Time = 5s (accelerating):
  Drag_CV: Fx < 0 (net thrust), Fy oscillates
  TransVel: Vx = 0.5, Vy ≈ 0
  COMcoords: X_com = 2.5, Y_com ≈ 0.0

Time = 10s (steady):
  Drag_CV: Fx ≈ 0 (balanced), Fy oscillates
  TransVel: Vx = 1.0 (constant), Vy ≈ 0
  COMcoords: X_com = 5.0, Y_com ≈ 0.0
```

### TETHERED - Expected Values

```
Time = 0s (start):
  Drag_CV: Fx = 0, Fy = 0
  TransVel: Vx = 0, Vy = 0
  COMcoords: X_com = 0.5, Y_com = 0.3

Time = 5s (swimming):
  Drag_CV: Fx = -0.15 (thrust), Fy oscillates
  TransVel: Vx = 0, Vy = 0
  COMcoords: X_com = 0.5, Y_com = 0.3

Time = 10s (swimming):
  Drag_CV: Fx = -0.15 (thrust), Fy oscillates
  TransVel: Vx = 0, Vy = 0
  COMcoords: X_com = 0.5, Y_com = 0.3
```

---

## Data Analysis Examples

### Compute Mean Thrust (Tethered Case)

```python
import numpy as np

# Load drag data
data = np.loadtxt('Drag_CV_strct_id_0')
time = data[:, 0]
Fx = data[:, 1]

# Skip transient, compute mean
steady_start = 5.0  # seconds
mask = time > steady_start
Fx_mean = np.mean(Fx[mask])
Fx_std = np.std(Fx[mask])

print(f"Mean thrust: {Fx_mean:.4f}")
print(f"Oscillation amplitude: {Fx_std:.4f}")

# Thrust coefficient
rho = 1.0
U_inf = 1.0
A_ref = 0.1
C_T = Fx_mean / (0.5 * rho * U_inf**2 * A_ref)
print(f"Thrust coefficient: {C_T:.4f}")
```

### Compute Swimming Speed (Free Swimming Case)

```python
# Load translational velocity
data = np.loadtxt('Eel2dStr/Eel2d_TranslationalVelocity_strct_id_0.curve')
time = data[:, 0]
Vx = data[:, 1]

# Find steady swimming speed
steady_start = 5.0
mask = time > steady_start
V_steady = np.mean(Vx[mask])

print(f"Steady swimming speed: {V_steady:.4f}")

# Swimming efficiency
data_drag = np.loadtxt('Drag_CV_strct_id_0')
Fx_mean = np.mean(data_drag[mask, 1])
print(f"Drag at steady state: {Fx_mean:.4f} (should be ≈0)")
```

---

## Troubleshooting

### Problem: All forces are zero

**FREE SWIMMING:**
- Check if simulation has run long enough
- Verify swimming kinematics are defined
- Check `deformation_velocity_function`

**TETHERED:**
- Check if swimming motion is active
- Verify free stream velocity U∞ > 0
- Check amplitude of swimming motion

### Problem: Body is not moving (Free Swimming)

**Check:**
1. `calculate_translational_momentum` should be 1,1,0
2. `calculate_rotational_momentum` should be 0,0,1
3. Verify kinematics are defined
4. Check if body mass/inertia are correct

### Problem: Body is moving (Tethered)

**Check:**
1. `calculate_translational_momentum` should be 0,0,0
2. `calculate_rotational_momentum` should be 0,0,0
3. Verify these flags in input file

---

## File Size Reference

Typical file sizes for 10-second simulation:

| File Type | Size | Number | Total |
|-----------|------|--------|-------|
| `Drag_CV_strct_id_0` | 3.9 MB | 1 per structure | ~4 MB |
| `Torque_CV_strct_id_0` | 2.6 MB | 1 per structure | ~3 MB |
| Structure curves | 2-4 MB | 6-8 per structure | ~20 MB |
| Visualization (Silo) | 15 MB | ~1600 snapshots | ~24 GB |

**Total:** ~25-30 GB for complete simulation with visualization

---

## Summary

### Key Differences: FREE SWIMMING vs TETHERED

| Aspect | FREE SWIMMING | TETHERED |
|--------|---------------|----------|
| **Purpose** | Study locomotion | Measure thrust |
| **Body motion** | Translates & rotates | Fixed position |
| **Force meaning** | Transient (→0 steady) | Net thrust |
| **Velocity files** | Non-zero | Zero |
| **Position files** | Changes | Constant |
| **Experimental analog** | Free fish | Force balance |
| **Applications** | Efficiency, maneuver | Thrust production |

**Both cases use the same force calculation physics (Reynolds Transport Theorem)!**

---

**Last updated:** 2025-12-25
**IBAMR version:** 0.18.0
**Documentation:** Complete file structure for swimming simulations
