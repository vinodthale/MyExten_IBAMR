# Hydrofoil Efficiency Implementation (Equations 7 & 8)

This directory contains the implementation of **Equation 7** (force coefficients) and **Equation 8** (quasipropulsive efficiency) for IBAMR hydrofoil simulations.

## Overview

The implementation calculates:

**Equation 7 - Force Coefficients:**
```
C_T = F_T / (0.5 × ρ × u_p² × c)
C_L = F_L / (0.5 × ρ × u_p² × c)
```

**Equation 8 - Quasipropulsive Efficiency (Tethered):**
```
η_QP = C_Tm / ∫ c_L(s,t) × V_body(s,t) dS
```

## Files Modified

### 1. `example.cpp`
**Modifications:**
- Added `write_marker_data()` function to output per-marker forces and velocities
- Added marker data output in main time loop (every 10 iterations)
- Added necessary includes: `<fstream>`, `<iomanip>`

**Key Changes:**
```cpp
// New function prototype (line ~57)
void write_marker_data(const double time, const std::string& filename, ...);

// Function implementation (line ~677)
void write_marker_data(...) { ... }

// Call in time loop (line ~614)
if (iteration_num % marker_output_interval == 0 || last_step) {
    write_marker_data(...);
}
```

### 2. `calculate_efficiency.m`
**New MATLAB script** that:
- Loads global force data from `Drag_CV_strct_id_0`
- Loads per-marker data from `Hydrofoil_marker_data.txt`
- Calculates force coefficients (Equation 7)
- Performs spatial integration for input power
- Calculates quasipropulsive efficiency (Equation 8)
- Provides validation checks and visualizations

## Usage Instructions

### Step 1: Compile Modified Code
```bash
cd /path/to/IBAMR_Efficiency_Implementation
cmake .
make
```

### Step 2: Run IBAMR Simulation
```bash
./example input2d
```

**Output files generated:**
- `Drag_CV_strct_id_0` - Global forces (already existed)
- `Hydrofoil_marker_data.txt` - Per-marker forces and velocities (NEW)

### Step 3: Calculate Efficiency
```matlab
% In MATLAB:
cd /path/to/IBAMR_Efficiency_Implementation
calculate_efficiency
```

**MATLAB outputs:**
- Console display with detailed results
- `hydrofoil_efficiency_results.mat` - Saved results structure
- `Hydrofoil_Performance_Analysis.png` - 4-panel visualization
- `Time_Series_Comparison.png` - Time history plots

## Expected Results

### Typical Values
For the NACA0012 hydrofoil at Re = 5000, St ≈ 0.4:
- **C_Tm**: +0.01 to +0.10 (positive thrust)
- **P_in**: 0.05 to 0.20 (positive input power)
- **η_QP**: 0.40 to 0.60 (40-60% efficiency)

### Validation Checks
The MATLAB script automatically checks:
- ✓ Efficiency in range [0, 1]
- ✓ Input power is positive
- ✓ Efficiency in typical range for oscillating foils (0.3 - 0.8)

## Output File Format

### `Hydrofoil_marker_data.txt`
```
time    s       fx      fy      vx      vy
0.0001  0.000   0.0012  -0.034  0.020   -0.45
0.0001  0.010   0.0015  -0.038  0.022   -0.48
...
```

**Columns:**
- `time`: Simulation time
- `s`: Arc length along hydrofoil (0 = leading edge)
- `fx`: Streamwise force at marker
- `fy`: Lateral force at marker (used for c_L)
- `vx`: Streamwise velocity
- `vy`: Lateral velocity (used for V_body)

## Simulation Parameters

From `input2d`:
- **ρ (density)**: 1.0
- **u_p (velocity)**: 1.0 (free-stream velocity)
- **c (chord length)**: 1.0
- **Re (Reynolds number)**: 5000
- **Simulation time**: 0 to 10.0

## Troubleshooting

### Problem: Marker data file not created
**Solution:**
- Check that the modified `example.cpp` was compiled
- Verify simulation ran successfully
- Check file permissions in output directory

### Problem: Efficiency > 1 or < 0
**Possible causes:**
- Wrong force component (using fx instead of fy)
- Wrong velocity component (using vx instead of vy)
- Sign error in integration

**Solution:** Check that the MATLAB script uses `fy` (lateral) and `vy` (lateral), NOT fx and vx.

### Problem: MATLAB "File not found" error
**Solution:**
- Ensure IBAMR simulation completed successfully
- Check current directory in MATLAB
- Verify file names match exactly

## Theory Background

### Equation 7: Force Coefficients
Non-dimensionalizes the thrust and lateral forces using dynamic pressure:
```
F_ref = 0.5 × ρ × u_p² × c
C_T = F_T / F_ref  (thrust coefficient)
C_L = F_L / F_ref  (lateral force coefficient)
```

### Equation 8: Quasipropulsive Efficiency
Measures how efficiently the hydrofoil converts input power (from lateral motion) into useful thrust:
```
η_QP = P_out / P_in

Where:
  P_out = C_Tm (for tethered simulation)
  P_in = ∫ c_L(s,t) × V_body(s,t) dS
```

**Physical Meaning:**
- **η_QP ≈ 1**: Nearly perfect efficiency
- **η_QP ≈ 0.5**: Typical for oscillating foils
- **η_QP < 0.3**: Inefficient (most power wasted)

## References

1. **Documentation:**
   - `/docs/CALCULATE_EQUATIONS_7_8.md` - Detailed calculation guide
   - `/docs/EQUATIONS_7_8_QUICK_REFERENCE.md` - Quick reference
   - `/docs/IBAMR_Efficiency_Implementation_Guide.md` - Full implementation guide

2. **Literature:**
   - Liu et al. (1996) - Tadpole swimming efficiency
   - Anderson et al. (1998) - Oscillating foils
   - Triantafyllou et al. (1993) - Optimal thrust development

## Contact

For questions or issues:
1. Check documentation in `/docs/` directory
2. Review IBAMR examples for ConstraintIB method
3. Consult IBAMR GitHub issues

---

**Last Updated:** 2025-12-30
**Branch:** `claude/implement-equations-7-8-y6vue`
