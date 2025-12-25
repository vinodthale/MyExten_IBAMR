# Propulsive Power and Efficiency Calculations in IBAMR

## Table of Contents
1. [Overview](#overview)
2. [Theoretical Background](#theoretical-background)
3. [Leader/Follower Foil Configuration](#leaderfollower-foil-configuration)
4. [Power Calculation Methods](#power-calculation-methods)
5. [Efficiency Calculation](#efficiency-calculation)
6. [Implementation in IBAMR](#implementation-in-ibamr)
7. [Complete Workflow](#complete-workflow)
8. [Data Files and Output](#data-files-and-output)
9. [MATLAB/Python Post-Processing](#matlabpython-post-processing)
10. [References](#references)

---

## Overview

This document explains how to compute **propulsive efficiency** for swimming bodies (fish, hydrofoils, etc.) in IBAMR simulations, based on the methodology of Liu et al. (1996).

The propulsive efficiency η quantifies how effectively a swimmer converts mechanical power (input power from body deformation) into useful thrust (output power).

### Key Equation

The propulsive efficiency of foil *i* is defined as:

```
η_i = P_out,i / P_in,i = C_Tm,i / ∫ c_L,i(s,t) V_body,i(s,t) ds
```

Where:
- **P_out,i**: Output power (thrust power)
- **P_in,i**: Input power (deformation power)
- **C_Tm,i**: Mean thrust coefficient (time-averaged)
- **c_L,i(s,t)**: Local lateral force coefficient per unit length
- **V_body,i(s,t)**: Local lateral velocity of the body
- **s**: Arc length coordinate along the body
- **i**: Foil index (1 = leader, 2 = follower)

---

## Theoretical Background

### Physical Interpretation

#### Output Power (P_out)

**Definition:** Power transferred to the fluid in the streamwise direction (thrust power)

**Physical meaning:**
- Rate of work done by the thrust force on the fluid
- Useful mechanical power that propels the body forward
- Negative thrust = drag (resists motion)
- Positive thrust = propulsion (drives motion forward)

**Calculation:**
```
P_out = <F_x> × U_swim
```

Where:
- `<F_x>`: Time-averaged thrust force (streamwise direction)
- `U_swim`: Swimming speed (or free-stream velocity for tethered bodies)

**Non-dimensionalized:**
```
P_out* = C_T × U*
C_T = F_x / (0.5 × ρ × U² × L)  [Thrust coefficient]
```

#### Input Power (P_in)

**Definition:** Power required to laterally deform the body

**Physical meaning:**
- Rate of work done by internal forces/muscles to move the body sideways
- Energy input required to create the swimming motion
- Computed as integral of force × velocity over the entire body surface

**Calculation:**
```
P_in = ∫_body f_y(s,t) × v_y(s,t) ds
```

Where:
- `f_y(s,t)`: Local lateral (y-direction) force per unit length at position s and time t
- `v_y(s,t)`: Local lateral velocity at position s and time t
- Integration is performed over the entire body arc length

**Non-dimensionalized:**
```
P_in* = ∫ c_L,i(s,t) × V_body,i(s,t) ds

Where:
  c_L,i(s,t) = f_y(s,t) / (0.5 × ρ × U² × L)  [Force coefficient density]
  V_body,i(s,t) = v_y(s,t) / U                 [Velocity ratio]
```

### Why This Definition Makes Sense

1. **Energy Conservation**: All mechanical energy put into lateral deformation eventually becomes:
   - Useful thrust (propulsion) → P_out
   - Wasted in vortices and drag → P_lost

2. **Efficiency Definition**:
   ```
   η = P_out / P_in = (Useful power) / (Total power input)
   ```

3. **For Undulatory Swimmers**:
   - High efficiency → Most lateral motion converts to forward thrust
   - Low efficiency → Much energy wasted in lateral forces and vortices

---

## Leader/Follower Foil Configuration

### Foil Indexing Convention

In tandem swimming simulations (e.g., two-fish schooling, cascaded hydrofoils):

- **i = 1**: Leader foil (upstream position)
- **i = 2**: Follower foil (downstream position, swimming in leader's wake)

### Configuration Example

```
      Free stream flow →

      ┌─────────┐         ┌─────────┐
      │ Foil 1  │         │ Foil 2  │
      │ Leader  │ ------> │Follower │
      │  (i=1)  │   Gap   │  (i=2)  │
      └─────────┘         └─────────┘

      x = 0.0             x = d_x
```

### Hydrodynamic Interaction Effects

**Leader (i=1):**
- Swims in undisturbed flow
- Creates vortex wake
- Standard propulsive efficiency

**Follower (i=2):**
- Swims in leader's wake
- Experiences:
  - Velocity variations from vortices
  - Pressure gradients
  - Potential energy savings OR penalties
- Efficiency can be higher or lower depending on:
  - Phase relationship between leader and follower
  - Spacing (streamwise gap d_x, lateral offset d_y)
  - Swimming frequency and amplitude

---

## Power Calculation Methods

### Method 1: Direct Force Integration (Control Volume Method)

**Used for:** Output power P_out

**Implementation in IBAMR:**
IBAMR computes hydrodynamic forces using the control volume method (see [`FORCE_CALCULATION_EXPLAINED.md`](./FORCE_CALCULATION_EXPLAINED.md)).

**Files created:**
- `Drag_CV_strct_id_0` → Forces on structure 0 (leader, i=1)
- `Drag_CV_strct_id_1` → Forces on structure 1 (follower, i=2)

**File format:**
```
time        F_x           F_y           F_z
0.0000      0.0000        0.0000        0.0000
0.0001     -0.0123        0.0456        0.0000
0.0002     -0.0234        0.0567        0.0000
...
```

**Thrust coefficient:**
```
C_T,i(t) = F_x,i(t) / (0.5 × ρ × U² × L)
```

**Output power:**
```
P_out,i = <C_T,i> × U
```
Where `<C_T,i>` is the time-averaged thrust coefficient in steady swimming.

---

### Method 2: Lagrangian Marker Integration

**Used for:** Input power P_in

**Concept:**
Integrate the product of force and velocity at each Lagrangian marker point on the body surface.

**Mathematical formulation:**
```
P_in,i(t) = Σ_markers f_y,k(t) × v_y,k(t) × Δs_k

Where:
  k: Marker index
  f_y,k(t): Lateral force at marker k
  v_y,k(t): Lateral velocity at marker k
  Δs_k: Arc length element (spacing between markers)
```

**Non-dimensional form:**
```
P_in,i*(t) = Σ_markers c_L,i,k(t) × V_body,i,k(t) × Δs*_k
```

---

## Efficiency Calculation

### Time-Averaged Efficiency

**Formula:**
```
η_i = <P_out,i> / <P_in,i> = <C_T,i> / <∫ c_L,i V_body,i ds>
```

**Procedure:**

1. **Compute instantaneous powers** for each time step:
   ```
   P_out,i(t) = C_T,i(t) × U
   P_in,i(t) = Σ_k c_L,i,k(t) × V_body,i,k(t) × Δs_k
   ```

2. **Time-average over steady swimming period** (after transients decay):
   ```
   <P_out,i> = (1/T) ∫_{t0}^{t0+T} P_out,i(t) dt
   <P_in,i> = (1/T) ∫_{t0}^{t0+T} P_in,i(t) dt
   ```

   Where T is the period of one swimming cycle (or multiple cycles).

3. **Compute efficiency:**
   ```
   η_i = <P_out,i> / <P_in,i>
   ```

### Cycle-Averaged Efficiency

Alternatively, compute efficiency for each swimming cycle and average:

```
η_i = (1/N) Σ_{cycle=1}^N [<P_out,i>_cycle / <P_in,i>_cycle]
```

---

## Implementation in IBAMR

### Current Status

IBAMR **does not natively output per-marker force and velocity data** required for input power calculation. This must be instrumented manually.

### Required Modifications

#### Step 1: Instrument IBAMR Source Code

**File to modify:** `src/IB/ConstraintIBMethod.cpp` (or your application's main loop)

**Objective:** Extract per-marker data after each time step

**What to extract:**
1. **Lagrangian forces** (`F_lag`): Force on each marker
2. **Lagrangian velocities** (`V_lag`): Velocity of each marker
3. **Arc length coordinates** (`s`): Position along body (0 to 1)

**Key data structures in IBAMR:**
```cpp
// Access Lagrangian data for structure i
Pointer<LData> F_data;  // Force data
Pointer<LData> U_data;  // Velocity data

// Get local array pointers
const double* F = F_data->getLocalFormVecArray();
const double* U = U_data->getLocalFormVecArray();

// For 2D:
int num_markers = F_data->getLocalNodeCount();
for (int k = 0; k < num_markers; ++k) {
    double fx = F[NDIM*k + 0];  // X-component
    double fy = F[NDIM*k + 1];  // Y-component
    double vx = U[NDIM*k + 0];
    double vy = U[NDIM*k + 1];

    // Compute local power contribution
    double p_local = fy * vy;  // Lateral force × lateral velocity
}
```

#### Step 2: Write Marker Data to File

**Suggested file format:** `Power_markers_struct_id_i.txt`

```
# time    s      fx        fy        vx        vy        p_local
0.0000   0.00   0.0000   0.0000    0.0000    0.0000    0.0000
0.0000   0.01   0.0012   0.0234    0.0010    0.0123    0.0029
0.0000   0.02   0.0015   0.0345    0.0012    0.0156    0.0054
...
0.0001   0.00   0.0001   0.0245    0.0011    0.0134    0.0033
...
```

**Code snippet (pseudocode):**
```cpp
std::ofstream file("Power_markers_struct_id_" + std::to_string(struct_id) + ".txt", std::ios::app);

for (int k = 0; k < num_markers; ++k) {
    double s = s_coordinate[k];
    double fx = F[NDIM*k + 0];
    double fy = F[NDIM*k + 1];
    double vx = U[NDIM*k + 0];
    double vy = U[NDIM*k + 1];
    double p_local = fy * vy;

    file << current_time << " " << s << " "
         << fx << " " << fy << " "
         << vx << " " << vy << " "
         << p_local << "\n";
}
file.close();
```

---

## Complete Workflow

### Simulation Setup

#### Input File Configuration (input2d)

For **two foils in tandem**:

```
ConstraintIBKinematics {
    eel2d_1 {  // Leader (i=1)
        structure_names = "eel2d_1"
        structure_levels = MAX_LEVELS - 1
        calculate_translational_momentum = 0,0,0  // Tethered
        calculate_rotational_momentum = 0,0,0

        // Swimming kinematics (lateral deformation)
        deformation_velocity_function_0 = "..."
        deformation_velocity_function_1 = "..."
    }

    eel2d_2 {  // Follower (i=2)
        structure_names = "eel2d_2"
        structure_levels = MAX_LEVELS - 1
        calculate_translational_momentum = 0,0,0  // Tethered
        calculate_rotational_momentum = 0,0,0

        // Swimming kinematics (can be in-phase or out-of-phase)
        deformation_velocity_function_0 = "..."
        deformation_velocity_function_1 = "..."
    }
}
```

**Why tethered (momentum flags = 0)?**
- Bodies deform (swim) but don't translate
- Simulates experimental thrust measurement setup
- Output forces directly represent propulsive thrust
- See [`README_TETHERED_BODY_FORCES.md`](./README_TETHERED_BODY_FORCES.md)

#### Geometry Files

```
eel2d_1.vertex  → Leader foil geometry
eel2d_2.vertex  → Follower foil geometry
```

### Running the Simulation

```bash
# Compile (if source code was modified)
cd IBAMR-0.18.0/examples/your_simulation
mkdir build && cd build
cmake ..
make -j4

# Run simulation
mpirun -np 8 ./main2d ../input2d
```

### Output Files Generated

**Force files (standard IBAMR output):**
```
Drag_CV_strct_id_0  → Thrust on leader (i=1)
Drag_CV_strct_id_1  → Thrust on follower (i=2)
Torque_CV_strct_id_0
Torque_CV_strct_id_1
```

**Marker data files (requires instrumentation):**
```
Power_markers_struct_id_0.txt  → Per-marker forces/velocities for leader
Power_markers_struct_id_1.txt  → Per-marker forces/velocities for follower
```

**Kinematics files (in Eel2dStr/ directory):**
```
Eel2d_Trans_vel_struct_no_0   → Translational velocity
Eel2d_Power_spent_struct_no_0 → Power (if available)
```

---

## MATLAB/Python Post-Processing

### MATLAB Script: Compute Efficiency

```matlab
%% Load force data (thrust)
F1 = load('Drag_CV_strct_id_0');  % Leader
F2 = load('Drag_CV_strct_id_1');  % Follower

t = F1(:,1);      % Time
Fx1 = F1(:,2);    % Thrust force, leader
Fx2 = F2(:,2);    % Thrust force, follower

%% Non-dimensionalize
rho = 1.0;        % Fluid density
U = 1.0;          % Free stream velocity (or swimming speed)
L = 1.0;          % Foil length
F_ref = 0.5 * rho * U^2 * L;

CT1 = Fx1 / F_ref;  % Thrust coefficient, leader
CT2 = Fx2 / F_ref;  % Thrust coefficient, follower

%% Load marker data
M1 = load('Power_markers_struct_id_0.txt');
M2 = load('Power_markers_struct_id_1.txt');

% Columns: [time, s, fx, fy, vx, vy, p_local]
t_marker = M1(:,1);
s1 = M1(:,2);
fy1 = M1(:,4);
vy1 = M1(:,6);

t_marker2 = M2(:,1);
s2 = M2(:,2);
fy2 = M2(:,4);
vy2 = M2(:,6);

%% Compute input power for each time step
times = unique(t_marker);
Pin1 = zeros(size(times));
Pin2 = zeros(size(times));

% Marker spacing (assuming uniform)
ds1 = mean(diff(unique(s1)));
ds2 = mean(diff(unique(s2)));

for k = 1:length(times)
    % Get markers at this time
    idx1 = (t_marker == times(k));
    idx2 = (t_marker2 == times(k));

    % Integrate: P_in = Σ f_y * v_y * ds
    Pin1(k) = sum(fy1(idx1) .* vy1(idx1)) * ds1;
    Pin2(k) = sum(fy2(idx2) .* vy2(idx2)) * ds2;
end

% Non-dimensionalize
Pin1_star = Pin1 / (F_ref * U);
Pin2_star = Pin2 / (F_ref * U);

%% Output power
% Interpolate thrust to marker time steps
CT1_interp = interp1(t, CT1, times, 'linear');
CT2_interp = interp1(t, CT2, times, 'linear');

Pout1 = CT1_interp * U;
Pout2 = CT2_interp * U;

%% Time-average (steady swimming regime)
% Assume steady state after t > 5.0 (adjust based on your simulation)
idx_steady = (times > 5.0);

Pout1_mean = mean(Pout1(idx_steady));
Pout2_mean = mean(Pout2(idx_steady));

Pin1_mean = mean(Pin1_star(idx_steady));
Pin2_mean = mean(Pin2_star(idx_steady));

%% Compute efficiency
eta1 = Pout1_mean / Pin1_mean;
eta2 = Pout2_mean / Pin2_mean;

fprintf('Propulsive Efficiency:\n');
fprintf('  Leader   (i=1): η = %.4f (%.2f%%)\n', eta1, eta1*100);
fprintf('  Follower (i=2): η = %.4f (%.2f%%)\n', eta2, eta2*100);

%% Plot results
figure;
subplot(3,1,1);
plot(times, CT1_interp, 'b-', times, CT2_interp, 'r-');
xlabel('Time'); ylabel('C_T');
legend('Leader', 'Follower');
title('Thrust Coefficient');

subplot(3,1,2);
plot(times, Pin1_star, 'b-', times, Pin2_star, 'r-');
xlabel('Time'); ylabel('P_{in}^*');
legend('Leader', 'Follower');
title('Input Power (Deformation)');

subplot(3,1,3);
plot(times, Pout1, 'b-', times, Pout2, 'r-');
xlabel('Time'); ylabel('P_{out}^*');
legend('Leader', 'Follower');
title('Output Power (Thrust)');
```

### Python Script: Compute Efficiency

```python
import numpy as np
import matplotlib.pyplot as plt

# Load force data
F1 = np.loadtxt('Drag_CV_strct_id_0')
F2 = np.loadtxt('Drag_CV_strct_id_1')

t = F1[:, 0]
Fx1 = F1[:, 1]  # Thrust, leader
Fx2 = F2[:, 1]  # Thrust, follower

# Non-dimensionalize
rho, U, L = 1.0, 1.0, 1.0
F_ref = 0.5 * rho * U**2 * L

CT1 = Fx1 / F_ref
CT2 = Fx2 / F_ref

# Load marker data
M1 = np.loadtxt('Power_markers_struct_id_0.txt')
M2 = np.loadtxt('Power_markers_struct_id_1.txt')

# Extract columns
t_marker = M1[:, 0]
s1 = M1[:, 1]
fy1 = M1[:, 3]
vy1 = M1[:, 5]

t_marker2 = M2[:, 0]
s2 = M2[:, 1]
fy2 = M2[:, 3]
vy2 = M2[:, 5]

# Compute input power
times = np.unique(t_marker)
Pin1 = np.zeros(len(times))
Pin2 = np.zeros(len(times))

ds1 = np.mean(np.diff(np.unique(s1)))
ds2 = np.mean(np.diff(np.unique(s2)))

for i, time in enumerate(times):
    idx1 = (t_marker == time)
    idx2 = (t_marker2 == time)

    Pin1[i] = np.sum(fy1[idx1] * vy1[idx1]) * ds1
    Pin2[i] = np.sum(fy2[idx2] * vy2[idx2]) * ds2

# Non-dimensionalize
Pin1_star = Pin1 / (F_ref * U)
Pin2_star = Pin2 / (F_ref * U)

# Interpolate thrust
CT1_interp = np.interp(times, t, CT1)
CT2_interp = np.interp(times, t, CT2)

Pout1 = CT1_interp * U
Pout2 = CT2_interp * U

# Time-average (steady swimming)
idx_steady = times > 5.0

eta1 = np.mean(Pout1[idx_steady]) / np.mean(Pin1_star[idx_steady])
eta2 = np.mean(Pout2[idx_steady]) / np.mean(Pin2_star[idx_steady])

print(f"Propulsive Efficiency:")
print(f"  Leader   (i=1): η = {eta1:.4f} ({eta1*100:.2f}%)")
print(f"  Follower (i=2): η = {eta2:.4f} ({eta2*100:.2f}%)")

# Plot
fig, axes = plt.subplots(3, 1, figsize=(10, 8))

axes[0].plot(times, CT1_interp, 'b-', label='Leader')
axes[0].plot(times, CT2_interp, 'r-', label='Follower')
axes[0].set_ylabel('$C_T$')
axes[0].set_title('Thrust Coefficient')
axes[0].legend()
axes[0].grid(True)

axes[1].plot(times, Pin1_star, 'b-', label='Leader')
axes[1].plot(times, Pin2_star, 'r-', label='Follower')
axes[1].set_ylabel('$P_{in}^*$')
axes[1].set_title('Input Power (Deformation)')
axes[1].legend()
axes[1].grid(True)

axes[2].plot(times, Pout1, 'b-', label='Leader')
axes[2].plot(times, Pout2, 'r-', label='Follower')
axes[2].set_ylabel('$P_{out}^*$')
axes[2].set_xlabel('Time')
axes[2].set_title('Output Power (Thrust)')
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.savefig('efficiency_analysis.png', dpi=300)
plt.show()
```

---

## Data Files and Output

### Force Data Structure

**File:** `Drag_CV_strct_id_i`

| Column | Name | Description |
|--------|------|-------------|
| 1 | time | Simulation time (s) |
| 2 | F_x | Streamwise force (thrust, dimensionless) |
| 3 | F_y | Lateral force (dimensionless) |
| 4 | F_z | Spanwise force (2D: always 0) |

**Sign convention:**
- Positive F_x = thrust (propulsion)
- Negative F_x = drag (resistance)

### Marker Data Structure (After Instrumentation)

**File:** `Power_markers_struct_id_i.txt`

| Column | Name | Description |
|--------|------|-------------|
| 1 | time | Simulation time |
| 2 | s | Arc length coordinate (0 to 1) |
| 3 | f_x | Streamwise force at marker |
| 4 | f_y | Lateral force at marker |
| 5 | v_x | Streamwise velocity at marker |
| 6 | v_y | Lateral velocity at marker |
| 7 | p_local | Local power = f_y × v_y |

### Accessing Existing IBAMR Data

**If marker data is not available**, you can still estimate input power using:

**File:** `Eel2d_Power_spent_struct_no_i`

This file (if generated) contains power expenditure computed by IBAMR. Check columns 2-4 for power in X, Y, Z directions.

---

## Summary of Calculations

### For Each Foil (i = 1 or 2):

1. **Thrust coefficient:**
   ```
   C_T,i(t) = F_x,i(t) / (0.5 × ρ × U² × L)
   ```

2. **Output power:**
   ```
   P_out,i = <C_T,i> × U
   ```

3. **Input power:**
   ```
   P_in,i(t) = Σ_markers c_L,i,k(t) × V_body,i,k(t) × Δs_k
   ```

   Where:
   ```
   c_L,i,k = f_y,k / (0.5 × ρ × U² × L)
   V_body,i,k = v_y,k / U
   ```

4. **Propulsive efficiency:**
   ```
   η_i = <P_out,i> / <P_in,i>
   ```

### Expected Results

**Typical efficiency ranges:**
- Anguilliform swimmers (eels): η ≈ 0.7–0.9 (70–90%)
- Carangiform swimmers (mackerel): η ≈ 0.8–0.95
- Foils with optimal kinematics: η ≈ 0.6–0.85

**Leader vs Follower:**
- Leader: Baseline efficiency
- Follower: Efficiency can be higher (vortex energy recovery) or lower (wake interference) depending on spacing and phase

---

## References

### Key Papers

1. **Liu, H., Wassersug, R. J., & Kawachi, K. (1996)**
   "A computational fluid dynamics study of tadpole swimming"
   *Journal of Experimental Biology*, 199(6), 1245-1260.
   - **Defines propulsive efficiency equation used in this document**

2. **Borazjani, I., & Sotiropoulos, F. (2008)**
   "Numerical investigation of the hydrodynamics of carangiform swimming in the transitional and inertial flow regimes"
   *Journal of Experimental Biology*, 211(10), 1541-1558.
   - Swimming kinematics and efficiency analysis

3. **Tytell, E. D., & Lauder, G. V. (2004)**
   "The hydrodynamics of eel swimming: I. Wake structure"
   *Journal of Experimental Biology*, 207(11), 1825-1841.
   - Experimental efficiency measurements

4. **Nangia, N., Johansen, H., Patankar, N. A., & Bhalla, A. P. S. (2017)**
   "A moving control volume approach to computing hydrodynamic forces and torques on immersed bodies"
   *Journal of Computational Physics*, 347, 437-462.
   - IBAMR force calculation method

5. **Bhalla, A. P. S., Bale, R., Griffith, B. E., & Patankar, N. A. (2013)**
   "A unified mathematical framework and an adaptive numerical method for fluid–structure interaction with rigid, deforming, and elastic bodies"
   *Journal of Computational Physics*, 250, 446-476.
   - IBAMR ConstraintIB method for swimming bodies

### IBAMR Documentation

- **GitHub:** https://github.com/IBAMR/IBAMR
- **Website:** https://ibamr.github.io
- **User Guide:** https://ibamr.github.io/docs

### Related Documentation in This Repository

- [`FORCE_CALCULATION_EXPLAINED.md`](./FORCE_CALCULATION_EXPLAINED.md) - Physics of force computation
- [`README_TETHERED_BODY_FORCES.md`](./README_TETHERED_BODY_FORCES.md) - Tethered vs free swimming
- [`MOMENTUM_FLAGS_EXPLAINED.md`](./MOMENTUM_FLAGS_EXPLAINED.md) - Configuration flags
- [`DATA_FILES_COMPLETE_GUIDE.md`](./DATA_FILES_COMPLETE_GUIDE.md) - Output file formats
- [`CODE_LOCATIONS_REFERENCE.md`](./CODE_LOCATIONS_REFERENCE.md) - Source code locations

---

## Appendix: Alternative Method (Without Marker Data)

If you cannot instrument IBAMR to output per-marker data, you can estimate input power using:

### Simplified Model

Assume sinusoidal lateral motion:

```
y(s,t) = A(s) sin(k×s - ω×t)
```

Then lateral velocity:

```
v_y(s,t) = ∂y/∂t = -ω × A(s) cos(k×s - ω×t)
```

And lateral force (from resistive force theory):

```
f_y(s,t) ≈ C_n × ρ × v_y² × sign(v_y)
```

Where C_n is the normal force coefficient.

**Input power estimate:**

```
P_in ≈ ∫_0^L C_n × ρ × v_y³ ds
```

**Limitations:**
- Assumes resistive force model (valid only at low Re)
- Ignores added mass and unsteady effects
- Less accurate than direct Lagrangian integration

**When to use:**
- Quick order-of-magnitude estimates
- Validation of IBAMR modifications
- Preliminary design studies

---

**Document Version:** 1.0
**Last Updated:** 2025-12-25
**Author:** Documentation generated for IBAMR efficiency analysis
**Contact:** See main repository README for support

---

**End of Document**
