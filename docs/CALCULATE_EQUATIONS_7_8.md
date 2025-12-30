# Calculating Equations 7 and 8: Force Coefficients and Quasipropulsive Efficiency

## Quick Summary

**Equation 7** - Force coefficients (dimensionless forces):
```
C_T = F_T / (0.5 × ρ × u_p² × c)
C_L = F_L / (0.5 × ρ × u_p² × c)
```

**Equation 8** - Quasipropulsive efficiency:
```
η_QP = (C_Ds + C_Tm) / ∫ c_L(s,t) V_body(s,t) dS
```

---

## Step-by-Step Calculation Guide

### **STEP 1: Calculate Force Coefficients (Equation 7)**

#### From IBAMR Output Files

Your IBAMR simulation generates force files:
- `Drag_CV_strct_id_0` - Forces on hydrofoil

**File format:**
```
time        F_x         F_y         F_z
0.0000      0.1234     -0.0567      0.0000
0.0001      0.1256     -0.0589      0.0000
...
```

#### MATLAB Code for Equation 7:

```matlab
%% CALCULATE FORCE COEFFICIENTS (Equation 7)

% Load force data
F_data = load('Drag_CV_strct_id_0');
time = F_data(:,1);
F_x = F_data(:,2);  % Thrust force (streamwise)
F_y = F_data(:,3);  % Lateral force (sideways)

% Simulation parameters (match your input2d file)
rho = 1.0;           % Fluid density
u_p = 1.0;           % Free-stream velocity (propulsive velocity)
c = 1.0;             % Chord length (characteristic length)

% Reference force for non-dimensionalization
F_ref = 0.5 * rho * u_p^2 * c;

% Calculate coefficients
C_T = F_x / F_ref;   % Thrust coefficient
C_L = F_y / F_ref;   % Lateral force coefficient

% Time-averaged values (after transient, e.g., t > 5.0)
idx_steady = (time > 5.0);
C_Tm = mean(C_T(idx_steady));  % Mean thrust coefficient
C_Lm = mean(C_L(idx_steady));  % Mean lateral coefficient

fprintf('Mean Thrust Coefficient C_Tm = %.6f\n', C_Tm);
fprintf('Mean Lateral Coefficient C_Lm = %.6f\n', C_Lm);
```

---

### **STEP 2: Calculate Input Power (Denominator of Equation 8)**

This requires **per-marker force and velocity data** along the hydrofoil surface.

#### Required Data

You need to output from IBAMR:
- **f_l(s,t)** = Lateral force at each marker position s and time t
- **v_body(s,t)** = Lateral velocity at each marker position s and time t

#### MATLAB Code for Spatial Integration:

```matlab
%% CALCULATE INPUT POWER - Equation 8 Denominator
% P_in = ∫ c_L(s,t) × V_body(s,t) dS

% Load per-marker data (must be instrumented in IBAMR)
% Format: [time, s, fx, fy, vx, vy]
M = load('Hydrofoil_marker_data.txt');

t = M(:,1);      % Time
s = M(:,2);      % Arc length coordinate along foil
f_x = M(:,3);    % Streamwise force at marker
f_y = M(:,4);    % Lateral force at marker (this is f_l)
v_x = M(:,5);    % Streamwise velocity
v_y = M(:,6);    % Lateral velocity (this is v_body)

% Get unique time and space points
t_unique = unique(t);
s_unique = unique(s);

N_t = length(t_unique);
N_s = length(s_unique);

% Reshape into 2D arrays [time × space]
fy_2d = reshape(f_y, [N_s, N_t])';  % [N_t × N_s]
vy_2d = reshape(v_y, [N_s, N_t])';  % [N_t × N_s]

% Non-dimensionalize
c_L = fy_2d / F_ref;           % Lateral force coefficient
V_body = vy_2d / u_p;          % Lateral velocity ratio

% Power density at each point: p(s,t) = c_L(s,t) × V_body(s,t)
power_density = c_L .* V_body;  % [N_t × N_s]

% Spatial integration for each time step: P_in(t) = ∫ p(s,t) ds
% Using trapezoidal rule
ds = mean(diff(s_unique));  % Marker spacing
P_in = trapz(s_unique, power_density, 2);  % Integrate along space dimension

% Time-average input power (after transient)
idx_steady = (t_unique > 5.0);
P_in_mean = mean(P_in(idx_steady));

fprintf('Mean Input Power (dimensionless) = %.6f\n', P_in_mean);
```

---

### **STEP 3: Calculate Quasipropulsive Efficiency (Equation 8)**

#### For Tethered Simulation:

```matlab
%% CALCULATE QUASIPROPULSIVE EFFICIENCY (Equation 8)

% Output power (numerator)
% For tethered simulation: P_out = C_Tm
P_out = C_Tm;

% Input power (denominator)
% Already calculated from spatial integration
P_in = P_in_mean;

% Quasipropulsive efficiency
eta_QP = P_out / P_in;

fprintf('\n');
fprintf('╔════════════════════════════════════════╗\n');
fprintf('║  QUASIPROPULSIVE EFFICIENCY RESULTS    ║\n');
fprintf('╠════════════════════════════════════════╣\n');
fprintf('║  C_Tm (thrust coefficient):  %.6f  ║\n', C_Tm);
fprintf('║  P_in (input power):         %.6f  ║\n', P_in);
fprintf('║  η_QP (efficiency):          %.6f  ║\n', eta_QP);
fprintf('║  Efficiency (percent):       %.2f%%    ║\n', eta_QP*100);
fprintf('╚════════════════════════════════════════╝\n');
```

#### For Free-Swimming Simulation:

If your hydrofoil can translate (not tethered), you need the drag coefficient **C_Ds** of a stationary NACA00XX foil:

```matlab
% From literature or separate simulation:
C_Ds = 0.05;  % Example: drag coefficient of stationary NACA0012 at same Re

% Output power for free-swimming
P_out = C_Ds + C_Tm;

% Efficiency
eta_QP = P_out / P_in;
```

---

## Complete MATLAB Script

Here's a complete script combining all steps:

```matlab
%% CALCULATE EQUATIONS 7 AND 8
% Hydrofoil Performance Analysis
% Based on your research paper equations

clear; clc; close all;

%% ============================================
%% PARAMETERS (Match your IBAMR simulation)
%% ============================================

rho = 1.0;           % Fluid density
u_p = 1.0;           % Free-stream velocity (propulsive velocity)
c = 1.0;             % Chord length
F_ref = 0.5 * rho * u_p^2 * c;  % Reference force

% Time range for averaging (after transient)
t_start_avg = 5.0;   % Start averaging after t = 5.0

%% ============================================
%% STEP 1: Load Global Force Data
%% ============================================

fprintf('Loading force data...\n');
F_data = load('Drag_CV_strct_id_0');

t_force = F_data(:,1);
F_x = F_data(:,2);  % Thrust (streamwise)
F_y = F_data(:,3);  % Lateral (sideways)

% Calculate force coefficients (Equation 7)
C_T = F_x / F_ref;
C_L = F_y / F_ref;

%% ============================================
%% STEP 2: Time-Average Force Coefficients
%% ============================================

idx_steady = (t_force > t_start_avg);

C_Tm = mean(C_T(idx_steady));  % Mean thrust coefficient
C_Lm = mean(C_L(idx_steady));  % Mean lateral coefficient

fprintf('  C_Tm (mean thrust coefficient) = %.6f\n', C_Tm);
fprintf('  C_Lm (mean lateral coefficient) = %.6f\n', C_Lm);

%% ============================================
%% STEP 3: Load Per-Marker Data
%% ============================================

fprintf('\nLoading marker data...\n');

% Check if marker data file exists
if ~exist('Hydrofoil_marker_data.txt', 'file')
    error(['Marker data file not found!\n' ...
           'You need to instrument IBAMR to output per-marker forces/velocities.\n' ...
           'See IBAMR_Efficiency_Implementation_Guide.md']);
end

M = load('Hydrofoil_marker_data.txt');

t_marker = M(:,1);
s = M(:,2);
f_x_marker = M(:,3);
f_y_marker = M(:,4);  % Lateral force (f_l)
v_x_marker = M(:,5);
v_y_marker = M(:,6);  % Lateral velocity (v_body)

%% ============================================
%% STEP 4: Reshape and Non-dimensionalize
%% ============================================

t_unique = unique(t_marker);
s_unique = unique(s);

N_t = length(t_unique);
N_s = length(s_unique);

fprintf('  Number of time steps: %d\n', N_t);
fprintf('  Number of markers: %d\n', N_s);

% Reshape to 2D grids
fy_2d = reshape(f_y_marker, [N_s, N_t])';
vy_2d = reshape(v_y_marker, [N_s, N_t])';

% Non-dimensionalize
c_L = fy_2d / F_ref;        % Force coefficient per unit length
V_body = vy_2d / u_p;       % Velocity ratio

%% ============================================
%% STEP 5: Spatial Integration (Equation 8 Denominator)
%% ============================================

fprintf('\nCalculating input power...\n');

% Power density: p(s,t) = c_L(s,t) × V_body(s,t)
power_density = c_L .* V_body;

% Integrate over space: P_in(t) = ∫ p(s,t) ds
ds = mean(diff(s_unique));
P_in = trapz(s_unique, power_density, 2);

fprintf('  Marker spacing ds = %.6f\n', ds);

%% ============================================
%% STEP 6: Time-Average Input Power
%% ============================================

idx_steady_marker = (t_unique > t_start_avg);
P_in_mean = mean(P_in(idx_steady_marker));

fprintf('  Mean input power P_in = %.6f\n', P_in_mean);

%% ============================================
%% STEP 7: Calculate Efficiency (Equation 8)
%% ============================================

fprintf('\nCalculating quasipropulsive efficiency...\n');

% For tethered simulation: P_out = C_Tm
% For free-swimming: P_out = C_Ds + C_Tm (where C_Ds is stationary drag)
P_out = C_Tm;  % Tethered case

eta_QP = P_out / P_in_mean;

%% ============================================
%% RESULTS DISPLAY
%% ============================================

fprintf('\n');
fprintf('╔════════════════════════════════════════════════╗\n');
fprintf('║     HYDROFOIL PERFORMANCE RESULTS              ║\n');
fprintf('╠════════════════════════════════════════════════╣\n');
fprintf('║  EQUATION 7: Force Coefficients                ║\n');
fprintf('║    C_Tm (thrust):      %+.6f                 ║\n', C_Tm);
fprintf('║    C_Lm (lateral):     %+.6f                 ║\n', C_Lm);
fprintf('╠════════════════════════════════════════════════╣\n');
fprintf('║  EQUATION 8: Quasipropulsive Efficiency        ║\n');
fprintf('║    P_out (numerator):  %.6f                  ║\n', P_out);
fprintf('║    P_in (denominator): %.6f                  ║\n', P_in_mean);
fprintf('║    η_QP:               %.6f (%.2f%%)         ║\n', eta_QP, eta_QP*100);
fprintf('╚════════════════════════════════════════════════╝\n');
fprintf('\n');

%% ============================================
%% VALIDATION CHECKS
%% ============================================

if eta_QP < 0 || eta_QP > 1
    warning('Efficiency out of physical range [0,1]: %.4f', eta_QP);
end

if P_in_mean < 0
    warning('Input power is negative - check force/velocity signs');
end

%% ============================================
%% SAVE RESULTS
%% ============================================

results = struct();
results.C_Tm = C_Tm;
results.C_Lm = C_Lm;
results.P_out = P_out;
results.P_in = P_in_mean;
results.eta_QP = eta_QP;
results.eta_percent = eta_QP * 100;

save('hydrofoil_efficiency_results.mat', 'results');
fprintf('Results saved to: hydrofoil_efficiency_results.mat\n');

%% ============================================
%% PLOTTING
%% ============================================

figure('Position', [100 100 1200 600], 'Color', 'w');

% Plot 1: Force coefficients time history
subplot(2,2,1);
plot(t_force, C_T, 'b-', 'LineWidth', 1.5);
hold on;
yline(C_Tm, 'r--', sprintf('Mean = %.4f', C_Tm), 'LineWidth', 2);
xline(t_start_avg, 'k--', 'Avg starts', 'LineWidth', 1.5);
grid on;
xlabel('Time');
ylabel('C_T');
title('Thrust Coefficient (Equation 7)');

% Plot 2: Input power time history
subplot(2,2,2);
plot(t_unique, P_in, 'r-', 'LineWidth', 1.5);
hold on;
yline(P_in_mean, 'k--', sprintf('Mean = %.4f', P_in_mean), 'LineWidth', 2);
xline(t_start_avg, 'k--', 'Avg starts', 'LineWidth', 1.5);
grid on;
xlabel('Time');
ylabel('P_{in}');
title('Input Power (Equation 8 Denominator)');

% Plot 3: Efficiency bar chart
subplot(2,2,3);
bar(eta_QP, 'FaceColor', [0.2 0.6 0.8]);
hold on;
yline(1.0, 'r--', 'Physical limit', 'LineWidth', 2);
ylim([0 1.2]);
ylabel('\eta_{QP}');
title(sprintf('Quasipropulsive Efficiency = %.2f%%', eta_QP*100));
grid on;

% Plot 4: Power density snapshot
subplot(2,2,4);
t_snap = round(0.7 * N_t);  % Snapshot at 70% of simulation
area(s_unique, power_density(t_snap,:), 'FaceAlpha', 0.6);
xlabel('Arc length s');
ylabel('c_L \times V_{body}');
title(sprintf('Power Density at t = %.3f', t_unique(t_snap)));
grid on;

print('-dpng', '-r300', 'Hydrofoil_Performance_Analysis.png');
fprintf('\nPlot saved: Hydrofoil_Performance_Analysis.png\n');
```

---

## Key Points to Remember

### For Equation 7:
1. **F_T and F_L** come from your `Drag_CV_strct_id_*` files (columns 2 and 3)
2. Use **time-averaged** values (C_Tm, C_Lm) for efficiency calculation
3. Make sure to **remove transient** period before averaging

### For Equation 8:
1. **Numerator**: Just C_Tm for tethered simulations
2. **Denominator**: Requires spatial integration of f_l × v_body over the foil surface
3. **Critical**: You must output per-marker data from IBAMR (see `IBAMR_Efficiency_Implementation_Guide.md`)

### Physical Interpretation:
- **η_QP near 1.0**: Very efficient - most input power converts to thrust
- **η_QP = 0.5**: Typical for oscillating foils
- **η_QP < 0.3**: Inefficient - most power wasted in vortices

### Expected Values (from literature):
- Optimal oscillating foils: η_QP ≈ 0.6 - 0.8
- Suboptimal kinematics: η_QP ≈ 0.3 - 0.5
- Swimming fish: η_QP ≈ 0.4 - 0.7

---

## Troubleshooting

**Q: I don't have marker data files**
- You need to instrument IBAMR to output per-marker forces/velocities
- See the detailed guide in `IBAMR_Efficiency_Implementation_Guide.md`

**Q: My efficiency is > 1 or < 0**
- Check force/velocity signs
- Verify you're using lateral components (fy and vy, not fx and vx)
- Ensure proper time averaging

**Q: Results don't match literature**
- Verify your Reynolds number and Strouhal number
- Check that u_p = u_∞ for tethered case
- Compare your kinematics with reference papers

---

## References

- **Your paper equations**: Equations 7 & 8 from the hydrofoil paper
- **IBAMR implementation**: See `POWER_AND_EFFICIENCY_CALCULATIONS.md`
- **Theory**: Liu et al. (1996), Anderson et al. (1998)
