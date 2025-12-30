# How to Use the IBAMR Efficiency Implementation

## 📖 Overview

This implementation calculates **Equation 7** (force coefficients) and **Equation 8** (quasipropulsive efficiency) for hydrofoil simulations in IBAMR.

### What This Calculates

**Equation 7 - Force Coefficients:**
```
C_T = F_T / (0.5 × ρ × u_p² × c)  [Thrust coefficient]
C_L = F_L / (0.5 × ρ × u_p² × c)  [Lateral force coefficient]
```

**Equation 8 - Quasipropulsive Efficiency (Tethered):**
```
η_QP = C_Tm / ∫ c_L(s,t) × V_body(s,t) dS
```

Where:
- **C_Tm** = Time-averaged thrust coefficient
- **c_L(s,t)** = Lateral force coefficient at position s, time t
- **V_body(s,t)** = Lateral velocity at position s, time t
- **ρ** = Fluid density
- **u_p** = Propulsive (free-stream) velocity
- **c** = Chord length

---

## 🚀 Quick Start Guide

### **Step 1: Compile the Modified Code**

```bash
cd IBAMR_Efficiency_Implementation

# Build using CMake
cmake .
make

# OR use the provided build script
./build_and_debug.sh
```

**What happens:** The modified `example.cpp` is compiled with the new `write_marker_data()` function that exports per-marker forces and velocities during simulation.

**Verify compilation:**
```bash
ls -lh example
# Should show the compiled executable
```

---

### **Step 2: Run the IBAMR Simulation**

```bash
./example input2d
```

**What happens:**
- The simulation runs with your hydrofoil configuration
- Every 10 iterations, per-marker data is written to file
- Progress is displayed in the terminal

**Output files generated:**
- `Drag_CV_strct_id_0` - Global forces (already existed)
- `Hydrofoil_marker_data.txt` - Per-marker forces/velocities (NEW!)

**Monitoring the simulation:**
```bash
# Check if marker data is being written
tail -20 Hydrofoil_marker_data.txt

# Monitor file size growth
watch -n 5 'ls -lh Hydrofoil_marker_data.txt'
```

**Typical runtime:**
- For END_TIME = 10.0: ~30 minutes to several hours (depends on your system)
- The simulation must complete successfully before proceeding to Step 3

---

### **Step 3: Calculate Efficiency in MATLAB**

```matlab
% Open MATLAB and navigate to the directory
cd /path/to/IBAMR_Efficiency_Implementation

% Run the efficiency calculation script
calculate_efficiency
```

**What the script does:**
1. ✅ Loads global force data from `Drag_CV_strct_id_0`
2. ✅ Loads per-marker data from `Hydrofoil_marker_data.txt`
3. ✅ Calculates Equation 7: Force coefficients C_T and C_L
4. ✅ Performs spatial integration for input power
5. ✅ Calculates Equation 8: Quasipropulsive efficiency η_QP
6. ✅ Runs validation checks
7. ✅ Generates visualizations
8. ✅ Saves results to `hydrofoil_efficiency_results.mat`

**Processing time:** Usually < 1 minute for typical datasets

---

## 📊 Understanding the Results

### Console Output

You'll see detailed output sections:

```
╔════════════════════════════════════════════════╗
║     HYDROFOIL PERFORMANCE RESULTS              ║
╠════════════════════════════════════════════════╣
║  EQUATION 7: Force Coefficients                ║
║    C_Tm (thrust):      +0.XXXXXX               ║
║    C_Lm (lateral):     +0.XXXXXX               ║
╠════════════════════════════════════════════════╣
║  EQUATION 8: Quasipropulsive Efficiency        ║
║    P_out (numerator):  0.XXXXXX                ║
║    P_in (denominator): 0.XXXXXX                ║
║    η_QP:               0.XXXXXX (XX.XX%)       ║
╚════════════════════════════════════════════════╝
```

### Expected Values (NACA0012, Re=5000, St≈0.4)

| Parameter | Expected Range | Physical Meaning |
|-----------|---------------|------------------|
| **C_Tm** | 0.01 to 0.10 | Positive = thrust generation |
| **P_in** | 0.05 to 0.20 | Power required to move foil |
| **η_QP** | 0.40 to 0.60 | 40-60% efficiency |

### Generated Files

After running `calculate_efficiency.m`:

1. **`hydrofoil_efficiency_results.mat`**
   - MATLAB structure with all results
   - Can be loaded later: `load('hydrofoil_efficiency_results.mat')`

2. **`Hydrofoil_Performance_Analysis.png`** (4-panel figure)
   - Top-left: Thrust coefficient C_T(t) with time-averaged mean
   - Top-right: Input power P_in(t) with time-averaged mean
   - Bottom-left: Efficiency bar chart with physical limit
   - Bottom-right: Power density distribution snapshot

3. **`Time_Series_Comparison.png`**
   - Detailed time series of C_T and P_in
   - Shows transient region vs. steady-state region

---

## 🔧 Configuration & Customization

### Adjust Marker Output Frequency

Edit `example.cpp` (around line 614):
```cpp
const int marker_output_interval = 10;  // Change this number
```

**Recommendations:**
- **10** = Good balance (default)
- **1** = Every iteration - WARNING: Very large files!
- **50** = Less frequent - Smaller files, may miss dynamics
- **100** = Minimal output - For long simulations

**File size estimates:**
- Interval = 10, 10,000 timesteps: ~500 MB
- Interval = 100, 10,000 timesteps: ~50 MB

### Modify Simulation Parameters

Edit `input2d` file:
```bash
Re  = 5000.0           # Reynolds number
END_TIME = 10.0        # Simulation duration (increase for more data)
DT_MAX = 0.00010       # Maximum time step
```

**For better results:**
- Increase `END_TIME` to 20.0 or 30.0 for longer steady-state
- Ensure simulation reaches periodic steady state

### Adjust Time Averaging in MATLAB

Edit `calculate_efficiency.m` (around line 30):
```matlab
t_start_avg = 5.0;   % Time to start averaging (skip transient)
```

**How to choose:**
- Look at force plots - when do they become periodic?
- Typical: Set to 50% of END_TIME or when forces oscillate regularly
- Too early = Includes transient (wrong results)
- Too late = Not enough data for good average

---

## 📁 Data File Formats

### Input File: `Drag_CV_strct_id_0`
```
time        F_x         F_y         F_z
0.0000      0.1234     -0.0567      0.0000
0.0001      0.1256     -0.0589      0.0000
...
```
- Automatically generated by IBAMR's `IBHydrodynamicForceEvaluator`
- Column 2 (F_x) = Streamwise force (thrust)
- Column 3 (F_y) = Lateral force

### Output File: `Hydrofoil_marker_data.txt`
```
time    s       fx      fy      vx      vy
0.0001  0.000   0.0012  -0.034  0.020   -0.45
0.0001  0.010   0.0015  -0.038  0.022   -0.48
0.0001  0.020   0.0018  -0.042  0.024   -0.50
...
```

**Columns explained:**
- `time` - Simulation time
- `s` - Arc length along hydrofoil (0 = leading edge, 1 = trailing edge)
- `fx` - Streamwise force at this marker
- `fy` - Lateral force at this marker (**used for c_L in Equation 8**)
- `vx` - Streamwise velocity of marker
- `vy` - Lateral velocity of marker (**used for V_body in Equation 8**)

**Data structure:**
- Each time step has N_markers rows (one per marker)
- For 22,051 markers and 1,000 time steps = 22,051,000 rows

---

## ⚠️ Troubleshooting

### Problem 1: "Marker data file not found"

**Error message in MATLAB:**
```
Error: Marker data file not found: Hydrofoil_marker_data.txt
```

**Cause:** Modified code wasn't compiled or simulation didn't run successfully

**Solution:**
```bash
# Step 1: Verify you're in the right directory
pwd
# Should show: .../IBAMR_Efficiency_Implementation

# Step 2: Recompile from scratch
make clean
cmake .
make

# Step 3: Verify executable exists
ls -lh example

# Step 4: Run simulation again
./example input2d

# Step 5: Check if file was created
ls -lh Hydrofoil_marker_data.txt
```

---

### Problem 2: Efficiency > 1.0 or < 0.0

**Error message:**
```
⚠ WARNING: Efficiency out of physical range [0,1]: X.XXXX
```

**Cause:** Wrong force/velocity components or sign errors

**Solution:**
1. **Check MATLAB script uses lateral components:**
   ```matlab
   % In calculate_efficiency.m, verify:
   f_y_marker = M(:,4);  % Column 4 = fy (lateral force)
   v_y_marker = M(:,6);  % Column 6 = vy (lateral velocity)
   ```

2. **Verify force directions in C++ code:**
   - In `write_marker_data()`, ensure:
   ```cpp
   double fy = F_array[NDIM * lag_idx + 1];  // Index 1 = lateral
   double vy = U_array[NDIM * lag_idx + 1];  // Index 1 = lateral
   ```

3. **Check simulation hasn't diverged:**
   ```bash
   # Look for NaN or Inf values
   grep -i "nan\|inf" Hydrofoil_marker_data.txt
   ```

---

### Problem 3: MATLAB crashes with "Out of Memory"

**Error message:**
```
Error: Out of memory
```

**Cause:** Too much marker data (too frequent output)

**Solution Option 1 - Reduce output frequency:**
```cpp
// In example.cpp, change from:
const int marker_output_interval = 10;
// To:
const int marker_output_interval = 100;
```

**Solution Option 2 - Process in chunks (Advanced):**
```matlab
% Load first 100,000 rows only
M = load('Hydrofoil_marker_data.txt', '-ascii', 1, 100000);
```

**Solution Option 3 - Increase MATLAB memory:**
```matlab
% Check current memory
memory

% Increase Java heap space in MATLAB preferences
% Preferences > General > Java Heap Memory
```

---

### Problem 4: Very low efficiency (< 0.1)

**Possible causes:**
1. Simulation hasn't reached steady state
2. Incorrect marker spacing calculation
3. Wrong reference values (ρ, u_p, c)
4. Time averaging started too early

**Solution:**

**Check 1 - Plot forces to verify steady state:**
```matlab
F_data = load('Drag_CV_strct_id_0');
plot(F_data(:,1), F_data(:,2))
xlabel('Time')
ylabel('Thrust Force')
% Should see periodic oscillations after transient
```

**Check 2 - Verify parameters match:**
```matlab
% In calculate_efficiency.m:
rho = 1.0;    % Must match input2d
u_p = 1.0;    % Must match input2d
c = 1.0;      % Must match geometry
```

**Check 3 - Increase simulation time:**
```bash
# In input2d, change:
END_TIME = 20.0  # or higher
```

**Check 4 - Adjust time averaging:**
```matlab
% In calculate_efficiency.m:
t_start_avg = 10.0;  % Increase if transient is long
```

---

### Problem 5: Compilation errors

**Error: "undefined reference to write_marker_data"**

**Solution:**
```bash
# Make sure you modified example.cpp correctly
grep -n "write_marker_data" example.cpp
# Should show both declaration and implementation

# Clean and rebuild
make clean
cmake .
make
```

**Error: "LData.h: No such file or directory"**

**Solution:**
```bash
# IBAMR include paths not set correctly
# Check CMakeLists.txt has correct IBAMR path
```

---

## 🎯 Physics Validation

### Automatic Checks

The MATLAB script performs these validations:

✅ **Check 1:** Efficiency in range [0, 1]
- Physical law: Can't create more energy than you put in
- If failed: Sign error or wrong components

✅ **Check 2:** Input power is positive
- Physical law: Work must be done to move the foil
- If failed: Force and velocity out of phase (check signs)

✅ **Check 3:** Efficiency in typical range [0.3, 0.8]
- Empirical: Oscillating foils typically in this range
- If outside: Not necessarily wrong, but verify carefully

### Physical Interpretation

| η_QP Range | Interpretation | Action |
|-----------|----------------|--------|
| **0.8 - 1.0** | Excellent efficiency (rare) | Verify results carefully |
| **0.5 - 0.8** | Good performance | Typical for optimized foils |
| **0.3 - 0.5** | Moderate performance | Typical for basic kinematics |
| **0.1 - 0.3** | Poor performance | Most power wasted in vortices |
| **< 0.1** | Very inefficient | Check for errors |

### Comparison with Literature

**For NACA0012-type foils:**

| Study | Re | St | η_QP |
|-------|----|----|------|
| Anderson et al. (1998) | 1100-40000 | 0.2-0.4 | 0.50-0.70 |
| Liu et al. (1996) | 300-500 | 0.4 | 0.50-0.70 |
| Your simulation | 5000 | 0.4 | **0.40-0.60** |

**Strouhal number calculation:**
```
St = f × A / U
```
Where f = flapping frequency, A = amplitude, U = velocity

---

## 📚 Reference Documentation

### In This Repository

In the `/docs/` directory:
- **`CALCULATE_EQUATIONS_7_8.md`** - Detailed step-by-step calculation guide
- **`EQUATIONS_7_8_QUICK_REFERENCE.md`** - Quick reference card
- **`IBAMR_Efficiency_Implementation_Guide.md`** - Complete implementation guide

### Key Literature References

1. **Liu, H., Wassersug, R., & Kawachi, K. (1996)**
   - "A computational fluid dynamics study of tadpole swimming"
   - *Journal of Experimental Biology*, 199(6), 1245-1260
   - Original efficiency formula

2. **Anderson, J. M., et al. (1998)**
   - "Oscillating foils of high propulsive efficiency"
   - *Journal of Fluid Mechanics*, 360, 41-72
   - Benchmark efficiency data

3. **Triantafyllou, M. S., et al. (1993)**
   - "Optimal thrust development in oscillating foils"
   - *Journal of Fluids and Structures*, 7(2), 205-224
   - Theoretical background

---

## 💡 Tips for Best Results

### 1. Run Longer Simulations
```bash
# In input2d:
END_TIME = 20.0  # or even 30.0
```
- Ensures full development of periodic steady state
- Provides more data for time averaging
- Reduces uncertainty in mean values

### 2. Start Averaging Late
```matlab
% In calculate_efficiency.m:
t_start_avg = 10.0;  # At least 50% of END_TIME
```
- Completely excludes transient startup
- Look at force plots to identify when oscillations are regular

### 3. Check Force Directions
- **Positive C_T** = Thrust (swimming forward) ✅
- **Negative C_T** = Drag (being pushed backward) ❌
- If C_T is negative, check your kinematics

### 4. Compare with Literature
- Find papers with similar Re and St numbers
- Your efficiency should be in the same ballpark
- Large differences suggest checking implementation

### 5. Save Your Results
```matlab
% Results are automatically saved, but you can also:
save('my_analysis_v1.mat', 'results', 'C_T', 'P_in', 't_force')
```

### 6. Document Your Parameters
Create a log file:
```bash
echo "Simulation: $(date)" > simulation_log.txt
echo "Re = 5000" >> simulation_log.txt
echo "END_TIME = 10.0" >> simulation_log.txt
echo "Efficiency = $eta_QP" >> simulation_log.txt
```

---

## 🔬 Advanced Usage

### Analyzing Multiple Structures

If you have multiple fish/foils (currently commented out in example.cpp):

```cpp
// Uncomment in example.cpp for Fish 2:
write_marker_data(loop_time,
                 "Fish2_marker_data.txt",
                 ib_method_ops->getLDataManager(),
                 finest_level,
                 1,  // struct_id = 1 for second fish
                 num_markers_1,
                 ds_1);
```

Then run `calculate_efficiency.m` separately for each file.

### Batch Processing Multiple Simulations

Create a batch script:
```bash
#!/bin/bash
for Re in 1000 2000 5000 10000; do
    sed -i "s/Re  = .*/Re  = $Re/" input2d
    ./example input2d
    mv Hydrofoil_marker_data.txt data_Re${Re}.txt
done
```

### Custom Analysis

Load results in MATLAB for custom plots:
```matlab
load('hydrofoil_efficiency_results.mat')

% Access saved data
efficiency = results.eta_QP
thrust_coef = results.C_Tm

% Create custom plot
figure;
plot(your_parameter, efficiency, 'o-')
xlabel('Your Parameter')
ylabel('Efficiency η_{QP}')
```

---

## 📞 Getting Help

### If You Encounter Issues

1. **Check this README first** - Most common issues are covered
2. **Review the documentation** in `/docs/` directory
3. **Check IBAMR examples** - Especially ConstraintIB examples
4. **Verify file paths** - Use absolute paths if needed
5. **Check IBAMR installation** - Ensure IBAMR compiled correctly

### Debugging Checklist

- [ ] Modified code compiled successfully (`make` completed without errors)
- [ ] Executable exists (`ls -lh example` shows file)
- [ ] Simulation ran to completion (reached END_TIME)
- [ ] Both data files exist (`Drag_CV_strct_id_0` and `Hydrofoil_marker_data.txt`)
- [ ] Data files are not empty (`wc -l *.txt`)
- [ ] No NaN or Inf values in data (`grep -i nan *.txt`)
- [ ] MATLAB can find the files (use absolute paths if needed)
- [ ] Parameters match between `input2d` and MATLAB script

---

## 🎓 Understanding the Theory

### Why Equation 7?

Force coefficients normalize forces by dynamic pressure:
```
Dynamic pressure = 0.5 × ρ × u²
Reference area = chord length × span (span=1 for 2D)
```

This makes results **dimensionless** and **comparable** across:
- Different Reynolds numbers
- Different fluid densities
- Different foil sizes

### Why Equation 8?

Quasipropulsive efficiency measures:
```
η_QP = Useful thrust power / Input power from body motion
```

**Numerator (P_out):** Power available for propulsion
- For tethered: P_out = C_Tm (mean thrust × velocity)
- For free-swimming: P_out = (C_Ds + C_Tm) × u_p

**Denominator (P_in):** Power required to move the body
- Integral of lateral force × lateral velocity
- Accounts for power in creating vortices
- Higher when motion is inefficient

**Physical meaning:**
- η_QP = 1.0 → Perfect: All input power becomes thrust
- η_QP = 0.5 → Half of input power becomes thrust
- η_QP = 0.0 → No thrust generated (all power wasted)

---

## ✅ Success Criteria

You know the implementation is working when:

1. ✅ Simulation completes without errors
2. ✅ `Hydrofoil_marker_data.txt` file exists and grows during simulation
3. ✅ MATLAB script runs without errors
4. ✅ Efficiency is in range [0, 1]
5. ✅ Efficiency is reasonable (0.3 - 0.8 for typical cases)
6. ✅ C_T is positive (thrust, not drag)
7. ✅ P_in is positive (power required)
8. ✅ Plots show periodic oscillations after transient
9. ✅ Results are reproducible (same input → same output)
10. ✅ Results align with literature for similar conditions

---

## 📝 Citation

If you use this implementation in your research, please cite:

```
@software{ibamr_efficiency_implementation,
  title={IBAMR Hydrofoil Efficiency Implementation: Equations 7 and 8},
  author={},
  year={2025},
  url={https://github.com/vinodthale/MyExten_IBAMR/tree/main/IBAMR_Efficiency_Implementation}
}
```

And cite the original efficiency formulation:
```
@article{liu1996tadpole,
  title={A computational fluid dynamics study of tadpole swimming},
  author={Liu, H and Wassersug, RJ and Kawachi, K},
  journal={Journal of Experimental Biology},
  volume={199},
  number={6},
  pages={1245--1260},
  year={1996}
}
```

---

## 📄 License

This implementation follows the IBAMR license (3-clause BSD). See the main IBAMR repository for details.

---

**Last Updated:** 2025-12-30
**Version:** 1.0
**Branch:** `claude/implement-equations-7-8-y6vue`

---

**Ready to start? Go to [Step 1: Compile the Modified Code](#step-1-compile-the-modified-code)** ⬆️
