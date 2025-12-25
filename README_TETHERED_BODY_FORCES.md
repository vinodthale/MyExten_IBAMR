# How IBAMR Computes Forces on Tethered Bodies

## Overview: What is a "Tethered" Simulation?

In your research on flow-mediated interactions between swimming fish (NACA0012 hydrofoils with wavy lateral movement), you're simulating a **tethered body** configuration.

### Key Characteristics

**Tethered Body:**
- ❌ Body does NOT translate as a rigid body
- ❌ Body does NOT rotate as a rigid body
- ✅ Body ONLY deforms according to prescribed kinematics
- ✅ Net hydrodynamic force is NOT zero
- ✅ That force represents **propulsive thrust**

**This is like a fish "swimming in place" on a treadmill.**

---

## Physical Setup

### Your Simulation

From your description:
> Two swimming fish with various swimming modes, simplified into two rigid NACA0012 hydrofoils with wavy lateral movement subject to free stream flow

```
                Free stream flow U∞ →
                ═════════════════════════════════
                        ┌─────────┐
                        │ Hydrofoil│  ← Deforming (swimming motion)
                        │ NACA0012 │  ← But position FIXED
                        └─────────┘
                        ↑↑↑↑↑↑↑↑↑
                        Reaction force (thrust)
```

**Physical Interpretation:**
1. **Free stream flow** moves past the hydrofoil at velocity U∞
2. **Hydrofoil deforms** with prescribed wavy motion (swimming kinematics)
3. **Hydrofoil position** remains fixed in space (tethered)
4. **Net force** from fluid on body = **Thrust** (propulsive force)

### Comparison to Free Swimming

| Aspect | Free Swimming | Tethered (Your Case) |
|--------|---------------|---------------------|
| Body translation | ✅ Yes - body moves forward | ❌ No - body held fixed |
| Body rotation | ✅ Yes - body can turn | ❌ No - body orientation fixed |
| Body deformation | ✅ Yes - swimming motion | ✅ Yes - swimming motion |
| Net force | Zero (steady state) | Non-zero (thrust) |
| Interpretation | Self-propelled swimming | Thrust measurement |

---

## How IBAMR Handles This

### 1. Kinematics Setup

In your input file, the kinematics are defined:

```
ConstraintIBKinematics {
    structure_names = "naca0012_fish1"

    # Tethered configuration - NO rigid body motion!
    calculate_translational_momentum = 0,0,0  ← All DISABLED
    calculate_rotational_momentum    = 0,0,0  ← All DISABLED

    # Prescribed deformation (swimming motion)
    deformation_velocity_function_0 = "A*omega*cos(k*X_0 - omega*T)*N_0"
    deformation_velocity_function_1 = "A*omega*cos(k*X_0 - omega*T)*N_1"
}
```

**What this means:**
- `calculate_translational_momentum = 0,0,0` → Body CANNOT translate
- `calculate_rotational_momentum = 0,0,0` → Body CANNOT rotate
- `deformation_velocity_function` → Body CAN deform (swim)

### 2. Force Calculation

**The force is still computed using Reynolds Transport Theorem!**

**File:** `IBAMR-0.18.0/src/IB/IBHydrodynamicForceEvaluator.cpp`

**Lines 778-783:**
```cpp
// Compute hydrodynamic force on the body
fobj.F_new = -(fobj.P_box_new - fobj.P_box_current) / dt    // Fluid momentum change
           + (fobj.P_new - fobj.P_current) / dt              // Body momentum change
           + trac;                                            // Surface stresses
```

**For a tethered body:**
- `fobj.P_new - fobj.P_current ≈ 0` (body momentum doesn't change significantly)
- `fobj.P_box_new - fobj.P_box_current` (fluid momentum changes due to swimming)
- `trac` = pressure + viscous stresses on control volume boundary

**Result:** The computed force equals the thrust produced by the swimming motion!

---

## Physical Interpretation

### What `Drag_CV_strct_id_0` Contains (Tethered Case)

```
time        Fx          Fy          Fz
0.000000   -1.234e-01   2.345e-03   0.000e+00
0.001000   -1.456e-01   3.456e-03   0.000e+00
0.002000   -1.678e-01   4.567e-03   0.000e+00
...
```

**Column meanings:**
- `Fx` = **Thrust** in x-direction (along free stream)
- `Fy` = **Lateral force** in y-direction (perpendicular to stream)
- `Fz` = Force in z-direction (zero for 2D)

**Sign convention:**
- **Negative Fx** = Thrust (opposes free stream)
- **Positive Fx** = Drag (same direction as free stream)

### Force Balance

For a tethered body in free stream:

```
F_thrust + F_drag = F_net (measured)

Where:
  F_thrust = Force from swimming motion (propulsive)
  F_drag   = Drag from free stream
  F_net    = What IBAMR computes in Drag_CV_strct_id_0
```

**Example:**
- Free stream creates drag: +10 N (rightward)
- Swimming creates thrust: -15 N (leftward)
- **Net force = -5 N** (leftward thrust excess)

This is the **propulsive thrust** available for acceleration!

---

## Connection to Your Research

### From Your Description:

> "Flow-mediated interaction between two swimming fish with various swimming modes"

**Setup:**
1. **Two NACA0012 hydrofoils** in free stream
2. **Wavy lateral movement** (prescribed kinematics)
3. **Tethered** (fixed position)
4. **Various swimming modes** (different frequencies, amplitudes, phase differences)

**What IBAMR computes:**
- **Individual thrust** for each hydrofoil
- **Hydrodynamic interaction** between the two
- **Effect of relative position** on thrust
- **Effect of phase difference** on thrust

### Experimental Validation

As you mentioned:
> "This is exactly how thrust is measured in experiments like Akanyeti et al. (2017)"

**Akanyeti et al. (2017) method:**
1. Tether fish model to force transducer
2. Subject to free stream flow in water tunnel
3. Fish executes swimming motion
4. Measure net force on force transducer
5. That force = **thrust production**

**Your IBAMR simulation replicates this exactly!**

---

## Why This Configuration Makes Sense

### 1. Isolates Thrust Production

By preventing translation/rotation, you can:
- ✅ Measure pure thrust from swimming
- ✅ Separate thrust from drag
- ✅ Study efficiency of different swimming modes
- ✅ Analyze hydrodynamic interactions

### 2. Matches Experimental Setup

Real experiments use:
- Force balances or load cells
- Water tunnels with flow
- Tethered robotic fish or real fish
- Same configuration as your simulation!

### 3. Enables Parametric Studies

You can vary:
- Swimming frequency (Strouhal number)
- Amplitude of motion
- Wavelength of undulation
- Phase difference between fish
- Separation distance

And measure the effect on **thrust production** directly!

---

## The Role of Momentum Flags

### Your Configuration

```
calculate_translational_momentum = 0,0,0
calculate_rotational_momentum    = 0,0,0
```

**What this does:**
1. **Prevents** IBAMR from calculating rigid body motion
2. **Zeros out** any momentum from swimming that would cause translation/rotation
3. **Keeps body fixed** in space

**From** `ConstraintIBMethod.cpp` (lines 1290-1296):
```cpp
for (int d = 0; d < 3; ++d)
{
    if (calculate_trans_mom[d])
        d_vel_com_def_new[position_handle][d] /= total_nodes;
    else
        d_vel_com_def_new[position_handle][d] = 0.0;  // ZERO - body stays put!
}
```

**Effect:** Body deforms but doesn't move → **Perfect tethering!**

---

## Force Computation Details

### Control Volume Integration

**Even though the body is tethered, IBAMR uses the same Reynolds Transport Theorem:**

```
F_body = -d/dt(∫∫∫_CV ρu dV) + d/dt(P_body) + ∫∫_∂CV T·n dA
         \_________________/   \___________/   \___________/
         Fluid momentum        Body momentum   Surface stress
         changes due to        (≈0 for         (pressure +
         swimming              tethered)       viscous)
```

**For tethered body:**
- Body momentum change ≈ 0 (body not accelerating)
- **Dominant terms:**
  - Fluid momentum change (due to swimming-induced flow)
  - Surface stresses (pressure and viscous forces)

**Result:** Net force = Thrust from swimming motion!

---

## Validation: What to Check

### 1. Force Time History

**Expected behavior:**
```python
import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt('Drag_CV_strct_id_0')
time = data[:, 0]
Fx = data[:, 1]  # Thrust

plt.plot(time, Fx)
plt.xlabel('Time')
plt.ylabel('Thrust (Fx)')
plt.axhline(y=0, color='k', linestyle='--', label='Zero thrust')
plt.legend()
plt.show()
```

**For swimming fish:**
- Should see **oscillating thrust** (periodic)
- Mean thrust can be positive (drag) or negative (excess thrust)
- Frequency matches swimming frequency

### 2. Thrust Coefficient

Define thrust coefficient:
```
C_T = Fx / (0.5 * ρ * U∞² * A_ref)

Where:
  Fx = Mean thrust (time-averaged)
  ρ = Fluid density
  U∞ = Free stream velocity
  A_ref = Reference area (e.g., projected area)
```

**Compare to literature:**
- Akanyeti et al. (2017)
- Borazjani & Sotiropoulos (2008)
- Your experimental data

### 3. Strouhal Number

```
St = f * A / U∞

Where:
  f = Swimming frequency
  A = Amplitude of tail motion
  U∞ = Free stream velocity
```

**Optimal swimming typically occurs at St ≈ 0.2-0.4**

Check that your thrust is maximized in this range!

---

## Comparison: Free Swimming vs Tethered

### Free Swimming

**Configuration:**
```
calculate_translational_momentum = 1,1,0
calculate_rotational_momentum    = 0,0,1
```

**Result:**
- Body accelerates forward
- Net force → 0 at steady swimming
- `Drag_CV_strct_id_0` shows force during acceleration phase

**Use case:** Studying swimming performance, maneuvering

### Tethered (Your Case)

**Configuration:**
```
calculate_translational_momentum = 0,0,0
calculate_rotational_momentum    = 0,0,0
```

**Result:**
- Body stays fixed
- Net force = thrust production
- `Drag_CV_strct_id_0` shows propulsive force

**Use case:** Thrust measurement, efficiency studies, matching experiments

---

## Code Locations Reference

| What | File | Lines |
|------|------|-------|
| Read momentum flags | `ConstraintIBKinematics.cpp` | 65-71 |
| Zero out translation | `ConstraintIBMethod.cpp` | 1290-1296 |
| Zero out rotation | `ConstraintIBMethod.cpp` | 1375 |
| Compute forces | `IBHydrodynamicForceEvaluator.cpp` | 778-783 |
| Write force files | `IBHydrodynamicForceEvaluator.cpp` | 800-801 |

---

## Example: Two-Fish Interaction Study

### Input File Setup

```
num_structures = 2

ConstraintIBKinematics {

fish1 {
    structure_names = "naca0012_fish1"
    calculate_translational_momentum = 0,0,0  # Tethered
    calculate_rotational_momentum    = 0,0,0  # Fixed orientation

    # Swimming kinematics
    deformation_velocity_function_0 = "A*omega*cos(k*X_0 - omega*T + phi1)*N_0"
    deformation_velocity_function_1 = "A*omega*cos(k*X_0 - omega*T + phi1)*N_1"
}

fish2 {
    structure_names = "naca0012_fish2"
    calculate_translational_momentum = 0,0,0  # Tethered
    calculate_rotational_momentum    = 0,0,0  # Fixed orientation

    # Swimming kinematics (different phase)
    deformation_velocity_function_0 = "A*omega*cos(k*X_0 - omega*T + phi2)*N_0"
    deformation_velocity_function_1 = "A*omega*cos(k*X_0 - omega*T + phi2)*N_1"
}

}
```

### Output Files

```
Drag_CV_strct_id_0  → Thrust on fish 1
Drag_CV_strct_id_1  → Thrust on fish 2
```

### Analysis

**Compare thrust between fish:**
```python
fish1 = np.loadtxt('Drag_CV_strct_id_0')
fish2 = np.loadtxt('Drag_CV_strct_id_1')

T1_mean = np.mean(fish1[:, 1])  # Mean thrust fish 1
T2_mean = np.mean(fish2[:, 1])  # Mean thrust fish 2

print(f"Fish 1 thrust: {T1_mean:.4f}")
print(f"Fish 2 thrust: {T2_mean:.4f}")
print(f"Thrust enhancement: {(T2_mean - T1_mean)/T1_mean * 100:.2f}%")
```

**Study:**
- Effect of separation distance
- Effect of phase difference (phi1 vs phi2)
- In-phase vs anti-phase swimming
- Leader-follower configurations

---

## Summary

### What is Computed

**For a tethered swimming body, `Drag_CV_strct_id_0` contains:**
- ✅ **Thrust** from swimming motion
- ✅ **Drag** from free stream
- ✅ **Net propulsive force**
- ✅ Time-accurate force history

### Why It's Meaningful

1. **Matches experiments** (Akanyeti et al., 2017 and others)
2. **Isolates thrust production** from translation effects
3. **Enables parametric studies** of swimming efficiency
4. **Computes hydrodynamic interactions** between multiple swimmers
5. **Uses rigorous physics** (Reynolds Transport Theorem)

### How to Use It

**For your two-fish interaction study:**
1. Run simulation with different configurations
2. Extract force time histories from `Drag_CV_strct_id_*` files
3. Compute mean thrust and oscillation amplitude
4. Calculate thrust coefficient and efficiency
5. Compare to experimental data
6. Identify optimal swimming modes

---

## References

### Experimental Validation
- **Akanyeti et al. (2017)**: Tethered fish thrust measurements
- Fish subjected to flow in water tunnel
- Force measured on tether
- Exactly your simulation setup!

### IBAMR Implementation
- **Nangia et al. (2017)**: Moving control volume for forces
- Reynolds Transport Theorem
- Validates against experimental data

### Your Configuration
- **Tethered body**: Fixed position, swimming motion only
- **Force output**: Direct thrust measurement
- **Matches**: Experimental thrust measurement protocols

---

## Quick Check: Is This Right?

**Ask yourself:**
1. ✅ Do I want to measure thrust production? → YES
2. ✅ Should the fish stay in place? → YES (tethered)
3. ✅ Is there a free stream flow? → YES
4. ✅ Does the body deform (swim)? → YES

**Then your configuration is CORRECT!**

**Your force data represents:**
- Net propulsive force from swimming
- Thrust available for acceleration
- What you'd measure with a force transducer in an experiment

**Trust your `Drag_CV_strct_id_0` data - it's computing exactly what you need!**

---

## Additional Documentation

See also:
- `FORCE_CALCULATION_EXPLAINED.md` - How forces are computed
- `MOMENTUM_FLAGS_EXPLAINED.md` - What the flags control
- `CODE_LOCATIONS_REFERENCE.md` - Exact line numbers in source

**For tethered body simulations, all the force calculation physics is the same - only the body kinematics constraint (tethering) is different!**
