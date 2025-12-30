%% CALCULATE EQUATIONS 7 AND 8: Force Coefficients and Quasipropulsive Efficiency
% Implementation based on the provided documentation
%
% This script calculates:
% - Equation 7: Force coefficients C_T and C_L
% - Equation 8: Quasipropulsive efficiency η_QP
%
% Author: Claude Code
% Date: 2025-12-30
% Reference: CALCULATE_EQUATIONS_7_8.md, EQUATIONS_7_8_QUICK_REFERENCE.md

clear; clc; close all;

%% ============================================
%% STEP 1: PARAMETERS (Match IBAMR simulation)
%% ============================================

fprintf('\n╔════════════════════════════════════════════════╗\n');
fprintf('║  HYDROFOIL EFFICIENCY CALCULATION              ║\n');
fprintf('║  Equations 7 & 8 Implementation                ║\n');
fprintf('╚════════════════════════════════════════════════╝\n\n');

% Simulation parameters (from input2d file)
rho = 1.0;           % Fluid density
u_p = 1.0;           % Free-stream velocity (propulsive velocity)
c = 1.0;             % Chord length
F_ref = 0.5 * rho * u_p^2 * c;  % Reference force

fprintf('Simulation Parameters:\n');
fprintf('  ρ (density):           %.2f\n', rho);
fprintf('  u_p (velocity):        %.2f\n', u_p);
fprintf('  c (chord length):      %.2f\n', c);
fprintf('  F_ref (reference):     %.4f\n\n', F_ref);

% Time range for averaging (remove transient)
t_start_avg = 5.0;   % Start averaging after t = 5.0
fprintf('Time averaging starts at t = %.1f\n\n', t_start_avg);

%% ============================================
%% STEP 2: Load Global Force Data (Equation 7)
%% ============================================

fprintf('═══════════════════════════════════════════════\n');
fprintf('STEP 1: Loading global force data...\n');
fprintf('═══════════════════════════════════════════════\n');

% Check if force file exists
force_file = 'Drag_CV_strct_id_0';
if ~exist(force_file, 'file')
    error('Force file not found: %s\nRun IBAMR simulation first!', force_file);
end

F_data = load(force_file);
t_force = F_data(:,1);  % Time
F_x = F_data(:,2);      % Thrust (streamwise)
F_y = F_data(:,3);      % Lateral (sideways)

fprintf('  ✓ Loaded force data: %s\n', force_file);
fprintf('  ✓ Number of time steps: %d\n', length(t_force));
fprintf('  ✓ Time range: %.4f to %.4f\n', t_force(1), t_force(end));

% Calculate force coefficients (Equation 7)
C_T = F_x / F_ref;
C_L = F_y / F_ref;

fprintf('  ✓ Calculated force coefficients C_T and C_L\n\n');

%% ============================================
%% STEP 3: Time-Average Force Coefficients
%% ============================================

fprintf('═══════════════════════════════════════════════\n');
fprintf('STEP 2: Time-averaging force coefficients...\n');
fprintf('═══════════════════════════════════════════════\n');

idx_steady = (t_force > t_start_avg);

if sum(idx_steady) == 0
    warning('No data after t = %.1f. Using all data.', t_start_avg);
    idx_steady = true(size(t_force));
end

C_Tm = mean(C_T(idx_steady));  % Mean thrust coefficient
C_Lm = mean(C_L(idx_steady));  % Mean lateral coefficient

fprintf('  C_Tm (mean thrust coefficient):    %+.6f\n', C_Tm);
fprintf('  C_Lm (mean lateral coefficient):   %+.6f\n\n', C_Lm);

%% ============================================
%% STEP 4: Load Per-Marker Data (Equation 8)
%% ============================================

fprintf('═══════════════════════════════════════════════\n');
fprintf('STEP 3: Loading per-marker data...\n');
fprintf('═══════════════════════════════════════════════\n');

% Check if marker data file exists
marker_file = 'Hydrofoil_marker_data.txt';
if ~exist(marker_file, 'file')
    error(['Marker data file not found: %s\n\n' ...
           'The IBAMR simulation must be run with the modified code\n' ...
           'that outputs per-marker forces and velocities.\n' ...
           'See IBAMR_Efficiency_Implementation_Guide.md for details.'], marker_file);
end

M = load(marker_file);

t_marker = M(:,1);    % Time
s = M(:,2);           % Arclength coordinate
f_x_marker = M(:,3);  % Streamwise force at marker
f_y_marker = M(:,4);  % Lateral force (f_l)
v_x_marker = M(:,5);  % Streamwise velocity
v_y_marker = M(:,6);  % Lateral velocity (v_body)

fprintf('  ✓ Loaded marker data: %s\n', marker_file);
fprintf('  ✓ Total data points: %d\n', size(M,1));

%% ============================================
%% STEP 5: Reshape and Non-dimensionalize
%% ============================================

fprintf('\n═══════════════════════════════════════════════\n');
fprintf('STEP 4: Reshaping data and non-dimensionalizing...\n');
fprintf('═══════════════════════════════════════════════\n');

t_unique = unique(t_marker);
s_unique = unique(s);

N_t = length(t_unique);
N_s = length(s_unique);

fprintf('  Number of time steps: %d\n', N_t);
fprintf('  Number of markers: %d\n', N_s);

% Reshape to 2D grids [time × space]
fy_2d = reshape(f_y_marker, [N_s, N_t])';
vy_2d = reshape(v_y_marker, [N_s, N_t])';

% Non-dimensionalize
c_L = fy_2d / F_ref;        % Lateral force coefficient per unit length
V_body = vy_2d / u_p;       % Velocity ratio

fprintf('  ✓ Data reshaped to [%d × %d] grids\n', N_t, N_s);
fprintf('  ✓ Non-dimensionalized force and velocity\n\n');

%% ============================================
%% STEP 6: Spatial Integration (Equation 8 Denominator)
%% ============================================

fprintf('═══════════════════════════════════════════════\n');
fprintf('STEP 5: Computing input power (spatial integral)...\n');
fprintf('═══════════════════════════════════════════════\n');

% Power density: p(s,t) = c_L(s,t) × V_body(s,t)
power_density = c_L .* V_body;

% Integrate over space: P_in(t) = ∫ p(s,t) ds
% Using trapezoidal rule
ds = mean(diff(s_unique));
P_in = trapz(s_unique, power_density, 2);  % Integrate along dimension 2 (space)

fprintf('  Marker spacing ds: %.6f\n', ds);
fprintf('  ✓ Spatial integration completed\n\n');

%% ============================================
%% STEP 7: Time-Average Input Power
%% ============================================

fprintf('═══════════════════════════════════════════════\n');
fprintf('STEP 6: Time-averaging input power...\n');
fprintf('═══════════════════════════════════════════════\n');

idx_steady_marker = (t_unique > t_start_avg);

if sum(idx_steady_marker) == 0
    warning('No marker data after t = %.1f. Using all data.', t_start_avg);
    idx_steady_marker = true(size(t_unique));
end

P_in_mean = mean(P_in(idx_steady_marker));

fprintf('  Mean input power P_in: %.6f\n\n', P_in_mean);

%% ============================================
%% STEP 8: Calculate Efficiency (Equation 8)
%% ============================================

fprintf('═══════════════════════════════════════════════\n');
fprintf('STEP 7: Calculating quasipropulsive efficiency...\n');
fprintf('═══════════════════════════════════════════════\n');

% Steady drag coefficient (C_Ds)
% This is the drag on a stationary body at the same Reynolds number
% Options to obtain C_Ds:
%   1. Run separate simulation with stationary body
%   2. Use literature value for NACA0012 at Re=5000
%   3. Set to 0 if neglecting (valid when C_Ds << C_Tm)

C_Ds = 0.0;  % MODIFY THIS: Add your C_Ds value here
             % For NACA0012 at Re=5000, C_Ds ≈ 0.01-0.02

% Output power (Equation 8 numerator)
% Full form: P_out = C_Ds + C_Tm
% Simplified (if C_Ds negligible): P_out = C_Tm
P_out = C_Ds + C_Tm;

% Quasipropulsive efficiency
eta_QP = P_out / P_in_mean;

fprintf('  C_Ds (steady drag):       %.6f\n', C_Ds);
fprintf('  C_Tm (thrust):            %.6f\n', C_Tm);
fprintf('  Numerator (P_out = C_Ds + C_Tm): %.6f\n', P_out);
fprintf('  Denominator (P_in):       %.6f\n', P_in_mean);
fprintf('  η_QP:                     %.6f (%.2f%%)\n\n', eta_QP, eta_QP*100);

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
fprintf('║    C_Ds (steady drag): %.6f                  ║\n', C_Ds);
fprintf('║    C_Tm (thrust):      %.6f                  ║\n', C_Tm);
fprintf('║    P_out = C_Ds+C_Tm:  %.6f                  ║\n', P_out);
fprintf('║    P_in (denominator): %.6f                  ║\n', P_in_mean);
fprintf('║    η_QP:               %.6f (%.2f%%)         ║\n', eta_QP, eta_QP*100);
fprintf('╚════════════════════════════════════════════════╝\n');
fprintf('\n');

%% ============================================
%% VALIDATION CHECKS
%% ============================================

fprintf('═══════════════════════════════════════════════\n');
fprintf('VALIDATION CHECKS\n');
fprintf('═══════════════════════════════════════════════\n');

validation_passed = true;

% Check 1: Efficiency bounds
if eta_QP < 0 || eta_QP > 1
    fprintf('  ⚠ WARNING: Efficiency out of physical range [0,1]: %.4f\n', eta_QP);
    validation_passed = false;
else
    fprintf('  ✓ Efficiency within physical range [0,1]\n');
end

% Check 2: Input power should be positive
if P_in_mean < 0
    fprintf('  ⚠ WARNING: Input power is negative: %.4f\n', P_in_mean);
    fprintf('    Check force/velocity signs in simulation\n');
    validation_passed = false;
else
    fprintf('  ✓ Input power is positive\n');
end

% Check 3: Reasonable efficiency range for hydrofoils
if eta_QP >= 0.3 && eta_QP <= 0.8
    fprintf('  ✓ Efficiency in typical range for oscillating foils\n');
elseif eta_QP < 0.3 && eta_QP > 0
    fprintf('  ⚠ NOTE: Efficiency is low (< 0.3). May indicate:\n');
    fprintf('    - Suboptimal kinematics\n');
    fprintf('    - Low Reynolds number effects\n');
elseif eta_QP > 0.8 && eta_QP < 1
    fprintf('  ⚠ NOTE: Efficiency is very high (> 0.8). Please verify:\n');
    fprintf('    - Force and velocity signs\n');
    fprintf('    - Integration method\n');
end

if validation_passed
    fprintf('\n  ✓ All validation checks passed!\n\n');
else
    fprintf('\n  ⚠ Some validation checks failed. Review results carefully.\n\n');
end

%% ============================================
%% SAVE RESULTS
%% ============================================

fprintf('═══════════════════════════════════════════════\n');
fprintf('SAVING RESULTS\n');
fprintf('═══════════════════════════════════════════════\n');

results = struct();
results.C_Ds = C_Ds;
results.C_Tm = C_Tm;
results.C_Lm = C_Lm;
results.P_out = P_out;
results.P_in = P_in_mean;
results.eta_QP = eta_QP;
results.eta_percent = eta_QP * 100;
results.rho = rho;
results.u_p = u_p;
results.c = c;
results.F_ref = F_ref;

save('hydrofoil_efficiency_results.mat', 'results');
fprintf('  ✓ Results saved to: hydrofoil_efficiency_results.mat\n\n');

%% ============================================
%% PLOTTING
%% ============================================

fprintf('═══════════════════════════════════════════════\n');
fprintf('GENERATING PLOTS\n');
fprintf('═══════════════════════════════════════════════\n');

% Figure 1: Force coefficients time history
figure('Position', [100 100 1200 800], 'Color', 'w');

% Plot 1: Thrust coefficient
subplot(2,2,1);
plot(t_force, C_T, 'b-', 'LineWidth', 1.5);
hold on;
yline(C_Tm, 'r--', sprintf('Mean = %.4f', C_Tm), 'LineWidth', 2);
xline(t_start_avg, 'k--', 'Avg starts', 'LineWidth', 1.5);
grid on;
xlabel('Time', 'Interpreter', 'latex', 'FontSize', 12);
ylabel('$C_T$', 'Interpreter', 'latex', 'FontSize', 12);
title('Thrust Coefficient (Equation 7)', 'Interpreter', 'latex', 'FontSize', 14);
legend('C_T(t)', sprintf('C_{Tm} = %.4f', C_Tm), 'Location', 'best');

% Plot 2: Input power time history
subplot(2,2,2);
plot(t_unique, P_in, 'r-', 'LineWidth', 1.5);
hold on;
yline(P_in_mean, 'k--', sprintf('Mean = %.4f', P_in_mean), 'LineWidth', 2);
xline(t_start_avg, 'k--', 'Avg starts', 'LineWidth', 1.5);
grid on;
xlabel('Time', 'Interpreter', 'latex', 'FontSize', 12);
ylabel('$P_{in}$', 'Interpreter', 'latex', 'FontSize', 12);
title('Input Power (Equation 8 Denominator)', 'Interpreter', 'latex', 'FontSize', 14);

% Plot 3: Efficiency bar chart
subplot(2,2,3);
bar(eta_QP, 'FaceColor', [0.2 0.6 0.8]);
hold on;
yline(1.0, 'r--', 'Physical limit', 'LineWidth', 2);
ylim([0 min(1.2, eta_QP*1.5)]);
ylabel('$\eta_{QP}$', 'Interpreter', 'latex', 'FontSize', 12);
title(sprintf('Quasipropulsive Efficiency = %.2f%%', eta_QP*100), 'Interpreter', 'latex', 'FontSize', 14);
grid on;
set(gca, 'XTick', []);

% Plot 4: Power density snapshot
subplot(2,2,4);
t_snap = round(0.7 * N_t);  % Snapshot at 70% of simulation
area(s_unique, power_density(t_snap,:), 'FaceAlpha', 0.6);
xlabel('Arc length $s$', 'Interpreter', 'latex', 'FontSize', 12);
ylabel('$c_L \times V_{body}$', 'Interpreter', 'latex', 'FontSize', 12);
title(sprintf('Power Density at $t = %.3f$', t_unique(t_snap)), 'Interpreter', 'latex', 'FontSize', 14);
grid on;

print('-dpng', '-r300', 'Hydrofoil_Performance_Analysis.png');
fprintf('  ✓ Plot saved: Hydrofoil_Performance_Analysis.png\n');

% Figure 2: Detailed time series comparison
figure('Position', [150 150 1000 600], 'Color', 'w');

subplot(2,1,1);
plot(t_force, C_T, 'b-', 'LineWidth', 1.5);
hold on;
xline(t_start_avg, 'k--', 'LineWidth', 1.5);
grid on;
xlabel('Time', 'FontSize', 11);
ylabel('C_T', 'FontSize', 11);
title('Thrust Coefficient Time History', 'FontSize', 13);

subplot(2,1,2);
plot(t_unique, P_in, 'r-', 'LineWidth', 1.5);
hold on;
xline(t_start_avg, 'k--', 'LineWidth', 1.5);
grid on;
xlabel('Time', 'FontSize', 11);
ylabel('P_{in}', 'FontSize', 11);
title('Input Power Time History', 'FontSize', 13);

print('-dpng', '-r300', 'Time_Series_Comparison.png');
fprintf('  ✓ Plot saved: Time_Series_Comparison.png\n\n');

fprintf('╔════════════════════════════════════════════════╗\n');
fprintf('║  CALCULATION COMPLETE!                         ║\n');
fprintf('╚════════════════════════════════════════════════╝\n\n');
