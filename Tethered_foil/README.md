# Tethered Foil Simulation

## Overview

This directory contains IBAMR simulations of tethered NACA0012 hydrofoils undergoing wavy undulation in a fluid flow. The configuration mimics slowly swimming fish and is used to study hydrodynamic interactions and force generation in tandem foil arrangements.

## Physical Configuration

### Geometry
- **Hydrofoil Profile**: NACA0012
- **Configuration**: Two hydrofoils in tandem (leader and follower)
- **Mounting**: Tethered (fixed in streamwise direction, free to oscillate laterally)

### Kinematics

The lateral displacement of each NACA0012 hydrofoil centerline is prescribed by wavy undulation:

**Leader Foil (i = 1):**
```
ΔY₁* = A_max X₁* sin[2π(X₁*/λ - St/(2A_max) t*)]
```

**Follower Foil (i = 2):**
```
ΔY₂* = A_max X₂* sin[2π(X₂*/λ - St/(2A_max) t*) + φ]
```

Where:
- `ΔY* = ΔY/C`: Lateral displacement normalized by chord length `C`
- `X* = X/C`: Streamwise position normalized by chord length
- `t* = tu_∞/C`: Non-dimensional time
- `T = 2A_max/St`: Wavy undulation period
- `t*/T = t*St/(2A_max)`: Phase within the undulation cycle
- `φ`: Phase difference between leader and follower foils

## Simulation Parameters

### Flow Conditions

| Parameter | Symbol | Value | Description |
|-----------|--------|-------|-------------|
| **Reynolds Number** | `Re` | 5000 | `Re = u_∞C/ν` |
| **Strouhal Number** | `St` | 0.4 | `St = fA/u_∞` |
| **Maximum Amplitude** | `A_max` | ≈ 0.1 | Normalized by chord length |

These parameters are representative of **slowly swimming fish**, which typically operate at:
- Moderate Reynolds numbers (O(10³-10⁴))
- Strouhal number `St ≈ 0.4` (efficient swimming regime)
- Small amplitude oscillations `A_max ≈ 0.1C`

### Biological Relevance

The selected parameters match the swimming regime of:
- Small to medium-sized fish (length 10-50 cm)
- Cruising speed (not burst swimming)
- Efficient propulsion with minimal energy expenditure

## Force Calculation Method

### Control Volume Approach

Forces on each hydrofoil are computed using the **Reynolds Transport Theorem** applied to a control volume surrounding the foil, following:

> **Nangia, N., Patankar, N. A., & Bhalla, A. P. S.** (2017). "A moving control volume approach to computing hydrodynamic forces and torques on immersed bodies." *Journal of Computational Physics*, 347, 437-462.

The total hydrodynamic force is decomposed as:

```
F_total = F_pressure + F_viscous + F_momentum + F_unsteady
```

Where:
- **F_pressure**: Pressure traction on control volume surface
- **F_viscous**: Viscous stress on control volume surface
- **F_momentum**: Momentum flux across control volume boundary
- **F_unsteady**: Time rate of change of momentum (fluid + body)

### Output Files

For each structure (foil) with ID `i`, the following force files are generated:

| File | Description | Format |
|------|-------------|--------|
| `Drag_CV_strct_id_i` | Total hydrodynamic force | `time Fx Fy Fz` |
| `Torque_CV_strct_id_i` | Total hydrodynamic torque | `time Tx Ty Tz` |
| `Pressure_CV_strct_id_i` | Pressure force component | `time Fx Fy Fz` |
| `Viscous_CV_strct_id_i` | Viscous force component | `time Fx Fy Fz` |
| `Momentum_CV_strct_id_i` | Momentum flux component | `time Fx Fy Fz` |
| `Unsteady_CV_strct_id_i` | Unsteady force component | `time Fx Fy Fz` |

### Force Conservation Check

The force decomposition should satisfy (to machine precision):

```matlab
F_total = F_pressure + F_viscous + F_momentum + F_unsteady
```

Verification script (MATLAB):
```matlab
% Load all force components
[t, Fx_total, Fy_total, Fz_total] = textread('Drag_CV_strct_id_0', '%f %f %f %f');
[~, Fx_p, Fy_p, Fz_p] = textread('Pressure_CV_strct_id_0', '%f %f %f %f');
[~, Fx_v, Fy_v, Fz_v] = textread('Viscous_CV_strct_id_0', '%f %f %f %f');
[~, Fx_m, Fy_m, Fz_m] = textread('Momentum_CV_strct_id_0', '%f %f %f %f');
[~, Fx_u, Fy_u, Fz_u] = textread('Unsteady_CV_strct_id_0', '%f %f %f %f');

% Verify conservation
err_x = Fx_total - (Fx_p + Fx_v + Fx_m + Fx_u);
err_y = Fy_total - (Fy_p + Fy_v + Fy_m + Fy_u);
err_z = Fz_total - (Fz_p + Fz_v + Fz_m + Fz_u);

max_error = max([max(abs(err_x)), max(abs(err_y)), max(abs(err_z))]);
fprintf('Maximum force decomposition error: %.3e\n', max_error);
% Should be ~1e-14 (machine precision)
```

## Non-dimensional Force Coefficients

### Drag and Lift Coefficients

```
C_D = F_x / (0.5 ρ u_∞² C L)
C_L = F_y / (0.5 ρ u_∞² C L)
```

Where:
- `F_x, F_y`: Streamwise and lateral forces
- `ρ`: Fluid density
- `u_∞`: Freestream velocity
- `C`: Chord length
- `L`: Spanwise length (= 1 for 2D simulations)

### Time-averaged and Instantaneous Forces

For oscillatory swimming:
- **Mean thrust**: `<C_D>` averaged over multiple periods
- **Lateral force amplitude**: `C_L_max - C_L_min`
- **Propulsive efficiency**: `η = <C_T> / <C_P>` (thrust/power)

## Physical Insights

### Vortex Wake Interactions

The tethered foil configuration allows study of:
1. **Leading-edge vortex (LEV)** formation and shedding
2. **Trailing-edge vortex (TEV)** dynamics
3. **Wake-foil interactions** (especially for follower foil)
4. **Phase synchronization** effects with phase difference `φ`

### Expected Flow Regimes

At `Re = 5000` and `St = 0.4`:
- **Transitional flow**: Between laminar and fully turbulent
- **Kármán vortex street**: May form if amplitude is small
- **Reverse Kármán street**: Expected for efficient propulsion (`St ~ 0.4`)
- **Thrust production**: Net positive thrust for `St > 0.2`

## Numerical Methods

### Immersed Boundary Method

IBAMR uses:
- **Penalty IB method** or **Constraint IB method**
- **Lagrangian markers**: Represent foil surface
- **Eulerian grid**: Fluid domain discretization
- **Staggered grid**: Pressure-velocity coupling

### Time Integration

- **Explicit scheme**: For IB forces and kinematics
- **Implicit scheme**: For fluid velocity and pressure
- **CFL condition**: `Δt < CΔx/u_max`

## References

1. **Nangia, N., Patankar, N. A., & Bhalla, A. P. S.** (2017). "A moving control volume approach to computing hydrodynamic forces and torques on immersed bodies." *Journal of Computational Physics*, 347, 437-462.

2. **Triantafyllou, M. S., Triantafyllou, G. S., & Yue, D. K. P.** (2000). "Hydrodynamics of fishlike swimming." *Annual Review of Fluid Mechanics*, 32(1), 33-53.

3. **Anderson, J. M., Streitlien, K., Barrett, D. S., & Triantafyllou, M. S.** (1998). "Oscillating foils of high propulsive efficiency." *Journal of Fluid Mechanics*, 360, 41-72.

4. **Dong, H., Mittal, R., & Najjar, F. M.** (2006). "Wake topology and hydrodynamic performance of low-aspect-ratio flapping foils." *Journal of Fluid Mechanics*, 566, 309-343.

## Getting Started

### Prerequisites

- IBAMR library (version 0.18.0 or later with force separation)
- SAMRAI library
- PETSc library
- MPI compiler (mpicc, mpicxx)

### Building

```bash
cd Tethered_foil
mkdir build && cd build
cmake ..
make -j4
```

### Running

```bash
# Single processor
./main2d input2d

# Parallel (4 processors)
mpirun -np 4 ./main2d input2d
```

### Post-processing

Analyze forces using MATLAB, Python, or VisIt:

```python
import numpy as np
import matplotlib.pyplot as plt

# Load force data
t, Fx, Fy, Fz = np.loadtxt('Drag_CV_strct_id_0', unpack=True)

# Compute force coefficients
rho = 1.0
U_inf = 1.0
C = 1.0
L = 1.0
q = 0.5 * rho * U_inf**2 * C * L

C_D = Fx / q
C_L = Fy / q

# Plot
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(t, C_D, 'b-', label='$C_D$')
plt.xlabel('Time')
plt.ylabel('Drag Coefficient')
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(t, C_L, 'r-', label='$C_L$')
plt.xlabel('Time')
plt.ylabel('Lift Coefficient')
plt.grid(True)

plt.tight_layout()
plt.savefig('force_coefficients.png', dpi=300)
```

## Directory Structure

```
Tethered_foil/
├── README.md                    # This file
├── CMakeLists.txt              # Build configuration
├── input2d                      # IBAMR input file
├── example.cpp                  # Main simulation code
├── IBTetheredFoilKinematics.h  # Kinematics class header
├── IBTetheredFoilKinematics.cpp # Kinematics implementation
├── naca0012.vertex             # Foil geometry file
└── analysis/                    # Post-processing scripts
    ├── compute_forces.m        # MATLAB force analysis
    ├── plot_vorticity.py       # Python flow visualization
    └── verify_conservation.m   # Force conservation check
```

## Expected Results

### Force Characteristics

For a single tethered foil at `Re = 5000`, `St = 0.4`, `A_max = 0.1`:

- **Mean drag coefficient**: `<C_D> ≈ -0.05` to `-0.15` (thrust)
- **Lift coefficient amplitude**: `C_L_max ≈ 1.0` to `2.0`
- **Strouhal scaling**: Thrust increases with `St` for `St < 0.4`

### Validation Targets

Compare against:
- Experimental data (if available)
- Published numerical simulations
- Scaling laws (thrust vs Strouhal number)

## Troubleshooting

### Common Issues

1. **Force decomposition doesn't sum to total**:
   - Ensure `Unsteady_CV_strct_id_X` file exists
   - Check that all four components are loaded

2. **Simulation diverges**:
   - Reduce time step size
   - Refine mesh near foil
   - Check CFL condition

3. **Large unsteady forces**:
   - Expected during initial transients
   - Allow several periods for flow to develop
   - Extract forces after startup phase

## Contact

For questions or issues related to this simulation:
- Open an issue on GitHub: https://github.com/vinodthale/MyExten_IBAMR/issues
- Reference the IBAMR documentation: https://ibamr.github.io/

---

**Last Updated**: December 2024
**IBAMR Version**: 0.18.0 (with force separation)
