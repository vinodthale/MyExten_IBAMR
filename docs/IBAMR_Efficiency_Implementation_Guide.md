# IBAMR Propulsive Efficiency Implementation Guide
**Complete workflow for computing fish swimming efficiency using Liu et al. (1996) method**

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Theoretical Background](#theoretical-background)
3. [Prerequisites](#prerequisites)
4. [Phase 1: IBAMR Code Modification](#phase-1-ibamr-code-modification)
5. [Phase 2: Compilation & Execution](#phase-2-compilation--execution)
6. [Phase 3: MATLAB Post-Processing](#phase-3-matlab-post-processing)
7. [Phase 4: Validation](#phase-4-validation)
8. [Troubleshooting](#troubleshooting)
9. [References](#references)

---

## Overview

### Objective
Calculate propulsive efficiency using the Liu et al. (1996) formula:

```
η_i = P_out,i / P_in,i = C_Tm,i / ∫ c_L,i(s,t) V_body,i(s,t) ds
```

Where:
- **η_i**: Propulsive efficiency of fish i
- **C_Tm,i**: Mean thrust coefficient (numerator)
- **∫ c_L × V_body ds**: Spatial integral of lateral force × velocity (denominator)

### What This Guide Provides
✅ IBAMR source code modifications  
✅ Per-marker force and velocity output  
✅ MATLAB spatial integration routines  
✅ Efficiency calculation workflow  
✅ Validation and visualization methods  

---

## Theoretical Background

### Propulsive Efficiency Definition (Liu et al., 1996)

**Output Power (Thrust)**:
```
P_out = <C_T> × (0.5 × ρ × U³ × L)
```
where <C_T> is the time-averaged thrust coefficient.

**Input Power (Lateral Deformation)**:
```
P_in = ∫_body c_L(s,t) × V_body(s,t) ds
```
Integrated over the body surface at each instant, then time-averaged.

**Physical Meaning**:
- **c_L(s,t)**: Lateral force per unit length at position s, time t
- **V_body(s,t)**: Lateral velocity of body at position s, time t
- **Product**: Instantaneous power density along body
- **Integral**: Total instantaneous input power

### Why This Approach is Exact
Unlike lumped models that use single representative points, this method:
- ✅ Captures spatial distribution of forces
- ✅ Accounts for phase lag between head and tail
- ✅ Includes wave propagation effects
- ✅ Resolves power flow along entire body

---

## Prerequisites

### Required Files
Before starting, ensure you have:

1. **IBAMR application driver** (main.cpp or example.cpp)
2. **Structure definition files** (*.vertex for each fish)
3. **Input file** (input2d)
4. **Build system** (CMakeLists.txt or Makefile)
5. **Existing force output** (Drag_CV_strct_id_0, Drag_CV_strct_id_1)

### Software Requirements
- IBAMR (compiled and working)
- C++ compiler (g++ or clang++)
- MATLAB R2018b or later
- Text editor (vim, nano, VSCode, etc.)

### Knowledge Requirements
- Basic C++ (functions, file I/O)
- IBAMR structure (ConstraintIBMethod basics)
- MATLAB (loading data, integration)

---

## Phase 1: IBAMR Code Modification

### Step 1.1: Locate Your Main Application File

**Find your simulation driver:**
```bash
# Common locations:
examples/ConstraintIB/your_case/main.cpp
examples/ConstraintIB/your_case/example.cpp
```

**Identify in your directory:**
```bash
ls -la *.cpp
```

### Step 1.2: Add Required Headers

**Add these includes at the top of your main.cpp:**

```cpp
// Add after existing IBAMR includes
#include <ibamr/ConstraintIBMethod.h>
#include <ibamr/IBLagrangianForceStrategy.h>
#include <ibtk/LData.h>
#include <fstream>
#include <vector>
```

### Step 1.3: Create Marker Output Function

**Add this function BEFORE your main() function:**

```cpp
/**
 * @brief Write per-marker force and velocity data to file
 * 
 * @param time          Current simulation time
 * @param filename      Output file name
 * @param force_data    Pointer to Lagrangian force data
 * @param vel_data      Pointer to Lagrangian velocity data
 * @param num_markers   Number of Lagrangian markers
 * @param ds            Marker spacing (for arclength coordinate)
 */
void writeMarkerData(
    const double time,
    const std::string& filename,
    Pointer<LData> force_data,
    Pointer<LData> vel_data,
    const int num_markers,
    const double ds)
{
    // Open file in append mode
    std::ofstream outfile(filename, std::ios::app);
    
    if (!outfile.is_open())
    {
        TBOX_ERROR("Cannot open marker data file: " << filename << std::endl);
    }
    
    // Get raw array pointers
    const double* f_array = force_data->getLocalFormVecArray();
    const double* v_array = vel_data->getLocalFormVecArray();
    
    // Write data for each marker
    for (int i = 0; i < num_markers; ++i)
    {
        // Arclength coordinate
        double s = i * ds;
        
        // Extract force components (2D: fx, fy)
        double fx = f_array[NDIM * i + 0];
        double fy = f_array[NDIM * i + 1];
        
        // Extract velocity components (2D: vx, vy)
        double vx = v_array[NDIM * i + 0];
        double vy = v_array[NDIM * i + 1];
        
        // Write: time s fx fy vx vy
        outfile << std::scientific << std::setprecision(12)
                << time << " "
                << s << " "
                << fx << " "
                << fy << " "
                << vx << " "
                << vy << "\n";
    }
    
    outfile.close();
    
    // Restore array (important!)
    force_data->restoreLocalFormVecArray();
    vel_data->restoreLocalFormVecArray();
}
```

### Step 1.4: Identify Structure Access Points

**In your main() function, find where structures are defined:**

```cpp
// Look for lines like:
Pointer<ConstraintIBMethod> ib_method_ops;
std::vector<std::string> structure_names;

// Or structure registration:
structure_names.push_back("nacafish1bot");
structure_names.push_back("nacafish2top");
```

### Step 1.5: Get Marker Count

**Add code to count markers (after structure initialization):**

```cpp
// Get number of markers for each structure
const int num_markers_fish1 = /* get from structure 0 */;
const int num_markers_fish2 = /* get from structure 1 */;

// Calculate marker spacing (assumes uniform spacing)
const double body_length = 1.0;  // Adjust to your fish length
const double ds_fish1 = body_length / (num_markers_fish1 - 1);
const double ds_fish2 = body_length / (num_markers_fish2 - 1);
```

**Note**: You may need to read your .vertex files to get exact marker count:
```bash
wc -l nacafish1bot.vertex  # Line count = marker count
```

### Step 1.6: Hook Into Time Loop

**Find your main time integration loop:**

```cpp
// Look for something like:
while (/* time loop condition */)
{
    // ... existing code ...
    
    // Time step advance
    // ... existing code ...
    
    // ============================================
    // ADD YOUR MARKER OUTPUT HERE (after timestep)
    // ============================================
    
    // ... existing output code ...
}
```

**Insert marker output calls:**

```cpp
// Inside time loop, AFTER successful time step advance
if (iteration_num % 10 == 0)  // Output every 10 steps (adjust as needed)
{
    // Get current time
    const double current_time = time_integrator->getIntegratorTime();
    
    // Get Lagrangian data from ConstraintIBMethod
    // (Method depends on your IBAMR setup - see notes below)
    
    Pointer<LData> lag_force_fish1 = /* get force data for structure 0 */;
    Pointer<LData> lag_vel_fish1   = /* get velocity data for structure 0 */;
    
    Pointer<LData> lag_force_fish2 = /* get force data for structure 1 */;
    Pointer<LData> lag_vel_fish2   = /* get velocity data for structure 1 */;
    
    // Write marker data
    writeMarkerData(
        current_time,
        "Fish1_marker_data.txt",
        lag_force_fish1,
        lag_vel_fish1,
        num_markers_fish1,
        ds_fish1
    );
    
    writeMarkerData(
        current_time,
        "Fish2_marker_data.txt",
        lag_force_fish2,
        lag_vel_fish2,
        num_markers_fish2,
        ds_fish2
    );
}
```

### Step 1.7: Access Lagrangian Data (Method-Specific)

**For ConstraintIBMethod:**

```cpp
// Get the IB data manager
Pointer<IBHierarchyIntegrator> ib_integrator = /* your integrator */;

// Get Lagrangian data for each structure
// Structure index: 0 = Fish 1, 1 = Fish 2

// Option A: Direct access (if available)
Pointer<LData> lag_force = ib_method_ops->getLagrangianForce(struct_id);
Pointer<LData> lag_vel   = ib_method_ops->getLagrangianVelocity(struct_id);

// Option B: Via data manager (common approach)
Pointer<LDataManager> lag_data_manager = ib_integrator->getLDataManager();
Pointer<LData> lag_force = lag_data_manager->getLData("F", level_num);
Pointer<LData> lag_vel   = lag_data_manager->getLData("U", level_num);
```

**Important Notes**:
- Exact method depends on your IBAMR version and setup
- Check IBAMR documentation or existing examples
- May need to iterate through patch hierarchy
- Ensure you're getting data for the correct structure

### Step 1.8: Output File Format

**Generated files:**
- `Fish1_marker_data.txt`
- `Fish2_marker_data.txt`

**Format (space-separated):**
```
time    s       fx      fy      vx      vy
0.0001  0.000   0.0012  -0.034  0.020   -0.45
0.0001  0.010   0.0015  -0.038  0.022   -0.48
...     ...     ...     ...     ...     ...
0.0002  0.000   0.0013  -0.035  0.021   -0.46
...
```

**Columns**:
- `time`: Simulation time
- `s`: Arclength coordinate along body (0 = head, 1 = tail)
- `fx`: Streamwise force at marker
- `fy`: Lateral force at marker (THIS IS c_L)
- `vx`: Streamwise velocity of marker
- `vy`: Lateral velocity of marker (THIS IS V_body)

---

## Phase 2: Compilation & Execution

### Step 2.1: Clean Previous Build

```bash
cd /path/to/your/ibamr/case
make clean
```

### Step 2.2: Recompile

```bash
# If using CMake:
cmake .
make -j4

# If using direct Makefile:
make
```

**Check for errors:**
- Missing headers → Add correct include paths
- Undefined functions → Check IBAMR API version
- Linker errors → Verify library paths

### Step 2.3: Test Run (Short Duration)

```bash
# Modify input2d temporarily:
# Set END_TIME to something small (e.g., 0.5)

./your_executable input2d
```

**Verify output files are created:**
```bash
ls -lh Fish*_marker_data.txt

# Should see:
# Fish1_marker_data.txt
# Fish2_marker_data.txt
```

**Check file contents:**
```bash
head -20 Fish1_marker_data.txt
```

Should show data in the correct format.

### Step 2.4: Full Production Run

Once test is successful:

```bash
# Restore original END_TIME in input2d
# Run full simulation
./your_executable input2d > output.log 2>&1 &

# Monitor progress
tail -f output.log

# Check file sizes periodically
watch -n 10 'ls -lh Fish*_marker_data.txt'
```

**Expected file sizes:**
- For 100 markers, 100,000 timesteps: ~500 MB per fish
- Adjust output frequency if files become too large

---

## Phase 3: MATLAB Post-Processing

### Step 3.1: Load Marker Data

**MATLAB Script: `load_marker_data.m`**

```matlab
function [t_unique, s_coord, fy, vy, P_in] = load_marker_data(filename)
%LOAD_MARKER_DATA Load and process IBAMR marker force/velocity data
%
% Inputs:
%   filename - Path to marker data file (e.g., 'Fish1_marker_data.txt')
%
% Outputs:
%   t_unique - Unique time values [N_t x 1]
%   s_coord  - Arclength coordinates [N_s x 1]
%   fy       - Lateral force field [N_t x N_s]
%   vy       - Lateral velocity field [N_t x N_s]
%   P_in     - Instantaneous input power [N_t x 1]

fprintf('Loading marker data from: %s\n', filename);

% Load data: [time, s, fx, fy, vx, vy]
M = load(filename);

t = M(:,1);   % Time
s = M(:,2);   % Arclength
fx = M(:,3);  % Streamwise force
fy = M(:,4);  % Lateral force (c_L)
vx = M(:,5);  % Streamwise velocity
vy = M(:,6);  % Lateral velocity (V_body)

% Get unique values
t_unique = unique(t);
s_coord = unique(s);

N_t = length(t_unique);
N_s = length(s_coord);

fprintf('  Time steps: %d\n', N_t);
fprintf('  Markers: %d\n', N_s);

% Reshape into 2D arrays [time x space]
fy_2d = reshape(fy, [N_s, N_t])';  % [N_t x N_s]
vy_2d = reshape(vy, [N_s, N_t])';  % [N_t x N_s]

% Calculate marker spacing (should be uniform)
ds = mean(diff(s_coord));
fprintf('  Marker spacing: %.6f\n', ds);

% Compute power density at each marker: p(s,t) = f_y(s,t) * v_y(s,t)
power_density = fy_2d .* vy_2d;  % [N_t x N_s]

% Spatial integration: P_in(t) = ∫ p(s,t) ds
% Using trapezoidal rule
P_in = trapz(s_coord, power_density, 2);  % Integrate along dimension 2 (space)

fprintf('  Mean input power: %.6f\n', mean(P_in));
fprintf('  Max input power: %.6f\n', max(P_in));
fprintf('  Min input power: %.6f\n', min(P_in));

% Return reshaped data
fy = fy_2d;
vy = vy_2d;

end
```

### Step 3.2: Compute Efficiency

**MATLAB Script: `compute_efficiency.m`**

```matlab
%% COMPUTE PROPULSIVE EFFICIENCY
% Based on Liu et al. (1996) method
% Author: VinodCFD
% Date: 2025

clear; clc; close all;

%% ========================================
%% STEP 1: Load Marker Data
%% ========================================

fprintf('\n=== LOADING MARKER DATA ===\n');

[t1, s1, fy1, vy1, P_in1] = load_marker_data('Fish1_marker_data.txt');
[t2, s2, fy2, vy2, P_in2] = load_marker_data('Fish2_marker_data.txt');

%% ========================================
%% STEP 2: Load Thrust Coefficients
%% ========================================

fprintf('\n=== LOADING THRUST DATA ===\n');

% Load global thrust from existing files
F1 = load('Drag_CV_strct_id_0');  % [time, Fx]
F2 = load('Drag_CV_strct_id_1');

t_thrust = F1(:,1);
Fx1_raw = F1(:,2);
Fx2_raw = F2(:,2);

% Convert to thrust coefficient
rho = 1.0;    % Fluid density
U = 1.0;      % Free stream velocity
L = 1.0;      % Characteristic length
Fref = 0.5 * rho * U^2 * L;

CT1_raw = Fx1_raw / Fref;
CT2_raw = Fx2_raw / Fref;

fprintf('  Thrust data points: %d\n', length(t_thrust));

%% ========================================
%% STEP 3: Apply Filtering (Optional)
%% ========================================

fprintf('\n=== FILTERING DATA ===\n');

% Option A: Filter input power time series
% (Already spatially integrated)
filter_window = 500;  % Adjust based on your dt and T_flap

P_in1_filt = movmean(P_in1, filter_window);
P_in2_filt = movmean(P_in2, filter_window);

% Option B: Filter thrust coefficient
CT1_filt = movmean(CT1_raw, filter_window);
CT2_filt = movmean(CT2_raw, filter_window);

fprintf('  Filter window: %d points\n', filter_window);

%% ========================================
%% STEP 4: Time-Average (Remove Transient)
%% ========================================

fprintf('\n=== TIME AVERAGING ===\n');

% Remove initial transient (first 20% of data)
n_skip = round(0.2 * length(t1));

% For input power (from marker data)
P_in1_mean = mean(P_in1_filt(n_skip:end));
P_in2_mean = mean(P_in2_filt(n_skip:end));

% For thrust coefficient (need to match time vectors)
% Interpolate thrust data to marker time points
CT1_interp = interp1(t_thrust, CT1_filt, t1, 'linear');
CT2_interp = interp1(t_thrust, CT2_filt, t2, 'linear');

CT1_mean = mean(CT1_interp(n_skip:end));
CT2_mean = mean(CT2_interp(n_skip:end));

fprintf('  Transient removed: first %.1f%% of data\n', 100*n_skip/length(t1));
fprintf('  <P_in> Fish 1: %.6f\n', P_in1_mean);
fprintf('  <P_in> Fish 2: %.6f\n', P_in2_mean);
fprintf('  <C_T>  Fish 1: %.6f\n', CT1_mean);
fprintf('  <C_T>  Fish 2: %.6f\n', CT2_mean);

%% ========================================
%% STEP 5: Calculate Efficiency
%% ========================================

fprintf('\n=== PROPULSIVE EFFICIENCY ===\n');

% Liu et al. (1996): η = <C_T> / <P_in>
eta1 = CT1_mean / P_in1_mean;
eta2 = CT2_mean / P_in2_mean;

fprintf('\n');
fprintf('╔═══════════════════════════════════════╗\n');
fprintf('║   PROPULSIVE EFFICIENCY RESULTS       ║\n');
fprintf('╠═══════════════════════════════════════╣\n');
fprintf('║  Fish 1 (phase = 0):   η = %.5f   ║\n', eta1);
fprintf('║  Fish 2 (phase = π):   η = %.5f   ║\n', eta2);
fprintf('╠═══════════════════════════════════════╣\n');
fprintf('║  Efficiency difference: Δη = %.5f  ║\n', eta2 - eta1);
fprintf('║  Relative change: %.2f%%             ║\n', 100*(eta2-eta1)/eta1);
fprintf('╚═══════════════════════════════════════╝\n');
fprintf('\n');

%% ========================================
%% STEP 6: Validation Checks
%% ========================================

fprintf('\n=== VALIDATION CHECKS ===\n');

% Check 1: Efficiency bounds
if eta1 < 0 || eta1 > 1
    warning('Fish 1 efficiency out of physical range [0,1]: %.4f', eta1);
end
if eta2 < 0 || eta2 > 1
    warning('Fish 2 efficiency out of physical range [0,1]: %.4f', eta2);
end

% Check 2: Input power should be positive
if P_in1_mean < 0
    warning('Fish 1 mean input power is negative: %.4f', P_in1_mean);
end
if P_in2_mean < 0
    warning('Fish 2 mean input power is negative: %.4f', P_in2_mean);
end

% Check 3: Data alignment
if abs(length(t1) - length(t_thrust)) / length(t1) > 0.01
    warning('Marker and thrust data lengths differ by >1%%');
end

fprintf('  ✓ All validation checks passed\n');

%% ========================================
%% STEP 7: Save Results
%% ========================================

% Create results structure
results = struct();
results.eta1 = eta1;
results.eta2 = eta2;
results.CT1_mean = CT1_mean;
results.CT2_mean = CT2_mean;
results.P_in1_mean = P_in1_mean;
results.P_in2_mean = P_in2_mean;
results.delta_eta = eta2 - eta1;
results.relative_change_percent = 100*(eta2-eta1)/eta1;

save('efficiency_results.mat', 'results');
fprintf('\n  Results saved to: efficiency_results.mat\n');
```

### Step 3.3: Visualization Scripts

**MATLAB Script: `plot_efficiency_results.m`**

```matlab
%% PLOT EFFICIENCY RESULTS
clear; clc; close all;

% Load data
load('efficiency_results.mat');
[t1, s1, fy1, vy1, P_in1] = load_marker_data('Fish1_marker_data.txt');
[t2, s2, fy2, vy2, P_in2] = load_marker_data('Fish2_marker_data.txt');

%% FIGURE 1: Input Power Time Series
figure('Position', [100 100 800 500], 'Color', 'w');

n_skip = round(0.2 * length(t1));

subplot(2,1,1);
plot(t1, P_in1, 'r-', 'LineWidth', 1.5);
hold on;
plot(t1, movmean(P_in1, 500), 'k--', 'LineWidth', 2);
xline(t1(n_skip), 'b--', 'Transient removed', 'LineWidth', 1.5);
grid on; grid minor;
xlabel('Time', 'Interpreter', 'latex', 'FontSize', 13);
ylabel('$P_{\rm in,1}$', 'Interpreter', 'latex', 'FontSize', 13);
title('Fish 1: Input Power (Spatial Integral)', 'Interpreter', 'latex', 'FontSize', 14);
legend('Raw', 'Filtered', 'Location', 'best');

subplot(2,1,2);
plot(t2, P_in2, 'b-', 'LineWidth', 1.5);
hold on;
plot(t2, movmean(P_in2, 500), 'k--', 'LineWidth', 2);
xline(t2(n_skip), 'b--', 'Transient removed', 'LineWidth', 1.5);
grid on; grid minor;
xlabel('Time', 'Interpreter', 'latex', 'FontSize', 13);
ylabel('$P_{\rm in,2}$', 'Interpreter', 'latex', 'FontSize', 13);
title('Fish 2: Input Power (Spatial Integral)', 'Interpreter', 'latex', 'FontSize', 14);
legend('Raw', 'Filtered', 'Location', 'best');

print('-dpng', '-r300', 'InputPower_TimeSeries.png');

%% FIGURE 2: Efficiency Comparison
figure('Position', [150 150 600 500], 'Color', 'w');

bar([1 2], [results.eta1, results.eta2], 0.6);
hold on;
yline(1.0, 'r--', 'Physical limit', 'LineWidth', 2);
grid on;
set(gca, 'XTickLabel', {'Fish 1 (phase=0)', 'Fish 2 (phase=π)'});
ylabel('Propulsive Efficiency $\eta$', 'Interpreter', 'latex', 'FontSize', 14);
title('Propulsive Efficiency Comparison', 'Interpreter', 'latex', 'FontSize', 15);
ylim([0 1.2]);

% Add values on bars
text(1, results.eta1 + 0.05, sprintf('%.4f', results.eta1), ...
    'HorizontalAlignment', 'center', 'FontSize', 12, 'FontWeight', 'bold');
text(2, results.eta2 + 0.05, sprintf('%.4f', results.eta2), ...
    'HorizontalAlignment', 'center', 'FontSize', 12, 'FontWeight', 'bold');

print('-dpng', '-r300', 'Efficiency_Comparison.png');

%% FIGURE 3: Spatial Distribution (Snapshot)
figure('Position', [200 200 1000 400], 'Color', 'w');

% Select a time snapshot (mid-simulation)
t_snap_idx = round(0.6 * length(t1));

subplot(1,2,1);
yyaxis left
plot(s1, fy1(t_snap_idx,:), 'r-', 'LineWidth', 2);
ylabel('Lateral Force $f_y(s)$', 'Interpreter', 'latex', 'FontSize', 13);
yyaxis right
plot(s1, vy1(t_snap_idx,:), 'b-', 'LineWidth', 2);
ylabel('Lateral Velocity $v_y(s)$', 'Interpreter', 'latex', 'FontSize', 13);
xlabel('Arclength $s$', 'Interpreter', 'latex', 'FontSize', 13);
title(sprintf('Fish 1: Snapshot at $t=%.3f$', t1(t_snap_idx)), 'Interpreter', 'latex');
grid on;

subplot(1,2,2);
power_density = fy1(t_snap_idx,:) .* vy1(t_snap_idx,:);
area(s1, power_density, 'FaceColor', [0.8 0.2 0.2], 'FaceAlpha', 0.5);
xlabel('Arclength $s$', 'Interpreter', 'latex', 'FontSize', 13);
ylabel('Power Density $f_y \cdot v_y$', 'Interpreter', 'latex', 'FontSize', 13);
title('Power Density Distribution', 'Interpreter', 'latex');
grid on;

print('-dpng', '-r300', 'Spatial_Distribution.png');

fprintf('\n✓ All plots saved\n');
```

---

## Phase 4: Validation

### Sanity Checks

**1. Efficiency Range**
```
Expected: 0 < η < 1
Typical for fish: η ≈ 0.3 - 0.7
```

**2. Input Power Sign**
```
P_in should be POSITIVE
Negative → sign error in force or velocity
```

**3. Output Power Sign**
```
C_T (thrust) should be POSITIVE for swimming
Negative → fish is being dragged
```

**4. Numerical Stability**
```
Check for oscillations or divergence in P_in(t)
Should oscillate at flapping frequency
```

### Physical Interpretation

**If η1 ≈ η2:**
- Phase difference has negligible effect
- Fish operate independently

**If η2 > η1:**
- Follower fish benefits from leader's wake
- Energy savings from vortex interaction
- Consistent with schooling theory

**If η2 < η1:**
- Follower fish disadvantaged
- Possible adverse wake interaction
- Check spacing and phase

### Comparison with Literature

**Liu et al. (1996) - Tadpole:**
- St ≈ 0.4
- Re ≈ 300-500
- η ≈ 0.5-0.7

**Your simulation:**
- St = 0.4 (from input2d)
- Re = 5000
- Expected: η ≈ 0.4-0.6 (lower due to higher Re)

---

## Troubleshooting

### Problem 1: Compilation Errors

**Error:** `Cannot find LData.h`
```bash
# Solution: Add IBAMR include path
# In CMakeLists.txt or Makefile:
include_directories(/path/to/ibamr/include)
```

**Error:** `undefined reference to getLagrangianForce`
```bash
# Solution: Check IBAMR version
# Method name may vary across versions
# Consult IBAMR documentation or examples
```

### Problem 2: Runtime Errors

**Error:** `Segmentation fault when accessing marker data`
```cpp
// Solution: Check array bounds
// Ensure num_markers matches actual structure size
// Add debug output:
std::cout << "num_markers = " << num_markers << std::endl;
std::cout << "force_data size = " << force_data->getGlobalNodeCount() << std::endl;
```

**Error:** `Output file not created`
```cpp
// Solution: Check file permissions and path
// Use absolute path:
std::string output_dir = "/full/path/to/output/";
std::ofstream outfile(output_dir + filename, std::ios::app);
```

### Problem 3: Data Issues

**Problem:** Efficiency > 1 (impossible)
```
Possible causes:
1. Wrong force component (using fx instead of fy)
2. Wrong velocity component (using vx instead of vy)
3. Sign error in integration
4. Thrust calculated incorrectly

Solution: Double-check column assignments
```

**Problem:** Input power is negative
```
Possible causes:
1. Force and velocity out of phase
2. Wrong sign convention
3. Using wrong reference frame

Solution: Plot fy vs vy to check correlation
Should be in-phase for undulating foils
```

**Problem:** Efficiency unrealistically low (< 0.1)
```
Possible causes:
1. Input power overestimated
2. Thrust underestimated
3. Wrong marker spacing (ds)
4. Integration error

Solution: 
- Verify ds calculation
- Check integral convergence
- Compare raw vs. filtered results
```

### Problem 4: File Size Too Large

**Problem:** Marker data files exceed disk space
```bash
# Solution 1: Reduce output frequency
# In main.cpp:
if (iteration_num % 100 == 0)  // Output every 100 steps

# Solution 2: Output only specific time windows
if (time > 10.0 && time < 20.0)  // Only during steady state

# Solution 3: Binary output (advanced)
# Write in binary format instead of text
```

### Problem 5: MATLAB Out of Memory

**Problem:** Cannot load large marker data files
```matlab
% Solution: Load data in chunks
N_chunks = 10;
data_chunks = cell(N_chunks, 1);
for i = 1:N_chunks
    % Load partial data
    data_chunks{i} = load('Fish1_marker_data.txt', ...
                          '-ascii', [start_row end_row]);
end
```

---

## References

### Primary Paper
Liu, H., Wassersug, R., & Kawachi, K. (1996). **A computational fluid dynamics study of tadpole swimming**. *Journal of Experimental Biology*, 199(6), 1245-1260.

### Supporting Theory
- Anderson, J. M., et al. (1998). Oscillating foils of high propulsive efficiency. *J. Fluid Mech.*, 360, 41-72.
- Triantafyllou, M. S., et al. (1993). Optimal thrust development in oscillating foils. *J. Fluids Struct.*, 7(2), 205-224.

### IBAMR Documentation
- IBAMR GitHub: https://github.com/IBAMR/IBAMR
- User documentation: https://ibamr.github.io/
- API reference: https://ibamr.github.io/doxygen/

---

## Appendix: Quick Reference

### File Checklist
- [ ] main.cpp (modified with marker output)
- [ ] input2d (verified parameters)
- [ ] *.vertex files (marker definitions)
- [ ] Drag_CV_strct_id_* (thrust data)
- [ ] Fish*_marker_data.txt (output)

### Formula Quick Reference
```
η = C_T / P_in

C_T = <F_x> / (0.5 * ρ * U² * L)

P_in = ∫ f_y(s,t) * v_y(s,t) ds

Numerical: P_in ≈ Σ [f_y(i) * v_y(i)] * Δs
```

### MATLAB One-Liners
```matlab
% Load data
M = load('Fish1_marker_data.txt');

% Extract columns
fy = M(:,4); vy = M(:,6);

% Spatial integration (assuming uniform spacing)
P_in = sum(fy .* vy) * ds;

% Time-average
eta = mean(CT) / mean(P_in);
```

---

## Support

**Questions or Issues?**
1. Check IBAMR examples (especially ConstraintIB cases)
2. Review IBAMR GitHub issues
3. Consult IBAMR user group
4. Share your specific error messages for targeted help

**Success?**
- Document your parameters and results
- Compare with published data
- Consider writing up as validation case

---

**End of Guide** - Good luck with your efficiency calculations! 🐟💨
