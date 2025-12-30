%% =====================================================================
%% IBAMR NACA0012 Traveling Wavy Foil - Lagrangian Mesh Generation
%% =====================================================================
%% Reference: Dong & Lu (2007), Physics of Fluids 19, 057107
%%            "Characteristics of flow over traveling wavy foils in a
%%             side-by-side arrangement"
%%
%% PURPOSE: Generate Lagrangian mesh for SINGLE traveling wavy foil
%%          to reproduce FIG. 2 (Time-dependent drag and lateral force
%%          coefficients during one cycle at c = 2.0)
%%
%% NUMERICAL PARAMETERS FROM FIGURE 2:
%%   - Reynolds number: Re = 5000
%%   - Phase speed: c = 2.0
%%   - Domain size: [-2, 15] × [-4, 4] (from Fig. 2 validation)
%%   - Element number: ~2×10^4 per foil
%%   - Time step: Δt = 0.005
%%   - Foil type: NACA0012 airfoil with traveling wave motion
%% =====================================================================

clear; clc; close all;

%% =====================================================================
%% SECTION 1: COMPUTATIONAL DOMAIN AND GRID PARAMETERS
%% =====================================================================
%% Based on Fig. 2 validation parameters:
%%   - Original domain: x ∈ [-2, 15], y ∈ [-4, 4]
%%   - For IBAMR: We use domain [0, 16] × [0, 8] (shifted)
%%   - Finest mesh: dx = dy ≈ 1.22×10^-4 (from element number ~2×10^4)

MAX_LEVELS = 3;         % Adaptive mesh refinement levels
REF_RATIO  = 4;         % Refinement ratio between levels
N = 256;                % Base grid resolution

Lx = 16.0;              % Domain length in x-direction
Ly = 8.0;               % Domain length in y-direction

Nx = 2*N*REF_RATIO^(MAX_LEVELS-1);  % Total grid points in x
Ny = N*REF_RATIO^(MAX_LEVELS-1);    % Total grid points in y
dx = Lx/Nx;                          % Grid spacing in x
dy = Ly/Ny;                          % Grid spacing in y

fprintf('=== COMPUTATIONAL DOMAIN ===\n');
fprintf('Domain size: [0, %.1f] × [0, %.1f]\n', Lx, Ly);
fprintf('Grid resolution: %d × %d\n', Nx, Ny);
fprintf('Finest mesh: dx = dy = %.8f\n', dx);

%% =====================================================================
%% SECTION 2: FOIL GEOMETRY (NACA0012 Airfoil)
%% =====================================================================
%% NACA0012 airfoil is used as the contour at equilibrium position
%% Reference: Section II.A (Physical problem and mathematical formulation)
%%
%% NACA 4-digit series thickness distribution (correct form):
%%   y_t(x) = 5 t × [0.2969√x - 0.1260x - 0.3516x² + 0.2843x³ - 0.1015x⁴]
%%   where t = maximum thickness ratio (t = 0.12 for NACA0012)
%%
%% (Note: 5t = t / 0.2 only when t = 0.2; here we use the general 5t form.)
%%
%% Foil parameters:
L = 1.0;                % Chord length (nondimensional)
x_LE = 5.0;             % Leading edge x-position in domain
y_LE = 4.0;             % Leading edge y-position (domain center)
t_max = 0.12 * L;       % Maximum thickness (12% of chord)

%% =====================================================================
%% SECTION 3: TRAVELING WAVE PARAMETERS
%% =====================================================================
%% Reference: Equation (3) from Dong & Lu (2007)
%%
%% EQUATION (3) - Midline lateral oscillation:
%%   y_o^i(x,t) = A_m^i(x) × cos[2π(x - c·t) + φ^i] + d^i
%%
%% where:
%%   - A_m^i(x) = amplitude envelope (depends on x)
%%   - c = phase speed (nondimensional)
%%   - φ^i = phase difference (0 for single foil)
%%   - d^i = lateral equilibrium position (0 for centerline)
%%
%% For a SINGLE foil centered at y = 0, Eq. (3) simplifies to:
%%   y_o(x,t) = A_m(x) × cos[2π(x - c·t)]
%%
%% Expanding the argument:
%%   2π(x - c·t) = 2π·x - 2π·c·t
%%
%% In standard wave notation cos(k·x - ω·t), we identify:
%%   k = 2π/λ     (wavenumber)
%%   ω = 2π·c/λ   (angular frequency)
%%   where λ = wavelength (nondimensional, in chord lengths)
%%
%% =====================================================================
%% TRAVELING WAVE PARAMETERS FOR FIG. 2:
%% =====================================================================
c = 2.0;             % Phase speed (nondimensional) - FROM FIG. 2
lambda = 1.0;        % Wavelength λ* (equals chord length L = 1.0)

% Derived wave parameters
k     = 2*pi / lambda;        % Wavenumber: k = 2π/λ = 6.2832
omega = 2*pi*c / lambda;      % Angular frequency: ω = 2π·c/λ = 12.5664

fprintf('\n=== TRAVELING WAVE PARAMETERS (Eq. 3) ===\n');
fprintf('Phase speed c = %.4f\n', c);
fprintf('Wavelength λ = %.4f\n', lambda);
fprintf('Wavenumber k = 2π/λ = %.4f\n', k);
fprintf('Angular frequency ω = 2π·c/λ = %.4f\n', omega);


%% =====================================================================
%% EQUATION (4) - Amplitude envelope A_m(x):
%%   A_m(x) = C_0 + C_1·x + C_2·x²
%%
%% Boundary conditions from steadily swimming saithe (Videler, 1993):
%%   A_m(0)   = 0.02  (leading edge amplitude)
%%   A_m(0.2) = 0.01  (minimum amplitude at 20% chord)
%%   A_m(1.0) = 0.10  (trailing edge amplitude)
%%
%% Solving the 3×3 linear system gives:
%%   C_0 =  0.0200
%%   C_1 = -0.0825
%%   C_2 =  0.1625
%% =====================================================================
a0 = 0.02;           % Coefficient C_0
a1 = -0.0825;        % Coefficient C_1
a2 = 0.1625;         % Coefficient C_2

fprintf('\n=== AMPLITUDE ENVELOPE (Eq. 4) ===\n');
fprintf('A_m(x) = C_0 + C_1·x + C_2·x²\n');
fprintf('C_0 = %.4f\n', a0);
fprintf('C_1 = %.4f\n', a1);
fprintf('C_2 = %.4f\n', a2);
fprintf('\nBoundary conditions verification:\n');
fprintf('  A_m(0.0) = %.4f (expected: 0.0200)\n', a0);
fprintf('  A_m(0.2) = %.4f (expected: 0.0100)\n', a0 + a1*0.2 + a2*0.2^2);
fprintf('  A_m(1.0) = %.4f (expected: 0.1000)\n', a0 + a1*1.0 + a2*1.0^2);


%% =====================================================================
%% SECTION 4: LAGRANGIAN MESH GENERATION
%% =====================================================================
%% Generate material points on NACA0012 airfoil with traveling wave motion
%%
%% ALGORITHM:
%%   1. Discretize chord into BodyNx points along x-direction
%%   2. At each x-location:
%%      a) Compute normalized coordinate ξ = x/L ∈ [0,1]
%%      b) Compute amplitude A_m(ξ) using Eq. (4)
%%      c) Compute midline position y_mid = A_m(ξ)·cos(k·ξ) using Eq. (3)
%%      d) Compute NACA0012 thickness distribution
%%      e) Generate material points along thickness direction
%%
%% NACA0012 Thickness Formula:
%%   y_t(ξ) = (t/0.2) × [0.2969√ξ - 0.1260ξ - 0.3516ξ² + 0.2843ξ³ - 0.1015ξ⁴]
%% =====================================================================

BodyNx = ceil(L/dx);        % Number of points along chord
NumMatPoints = 0;            % Total material point counter
Coord = cell(BodyNx,2);      % Storage for coordinates

fprintf('\n=== LAGRANGIAN MESH GENERATION ===\n');
fprintf('Number of chordwise points: %d\n', BodyNx);

for i = 1:BodyNx
    % Current chordwise position
    x  = (i-1)*dx;           % Dimensional position [0, L]
    xi = x/L;                % Normalized position ξ ∈ [0,1]

    % ─────────────────────────────────────────────────────────────────
    % EQUATION (4): Amplitude envelope A_m(ξ) = C_0 + C_1·ξ + C_2·ξ²
    % ─────────────────────────────────────────────────────────────────
    A_xi  = a0 + a1*xi + a2*xi^2;

    % ─────────────────────────────────────────────────────────────────
    % EQUATION (3): Midline position y_mid = A_m(ξ)·cos(k·ξ)
    %               (evaluated at t=0 for initial mesh)
    % ─────────────────────────────────────────────────────────────────
    y_mid = A_xi * cos(k*xi);

    % ─────────────────────────────────────────────────────────────────
    % NACA0012 thickness distribution
    % ─────────────────────────────────────────────────────────────────
    thickness = 0.2969*sqrt(xi) - 0.1260*xi - 0.3516*xi^2 + ...
                0.2843*xi^3 - 0.1015*xi^4;
    height = (t_max/0.2) * thickness;  % Scale by maximum thickness

    % Generate points along thickness direction (normal to midline)
    NumPoints = ceil(height/dy);
    xcoord = [];
    ycoord = [];

    for j = 1:NumPoints
        % Upper surface points
        xcoord(j) = x + x_LE;
        ycoord(j) = y_mid + y_LE + (j-1)*dy;

        % Lower surface points
        xcoord(NumPoints+j) = x + x_LE;
        ycoord(NumPoints+j) = y_mid + y_LE - j*dy;

        NumMatPoints = NumMatPoints + 2;
    end

    Coord{i,1} = xcoord;
    Coord{i,2} = ycoord;
end

fprintf('Total material points generated: %d\n', NumMatPoints);
fprintf('(Target: ~2×10^4 from Fig. 2 validation)\n');

%% =====================================================================
%% SECTION 5: WRITE VERTEX FILE FOR IBAMR
%% =====================================================================
%% Write Lagrangian mesh to .vertex file format for IBAMR
%%
%% FILE FORMAT:
%%   Line 1: Total number of material points
%%   Line 2-end: x-coordinate  y-coordinate (tab-separated)
%%
%% This file will be read by IBAMR to initialize the immersed boundary
%% =====================================================================

filename = 'nacafish1bot.vertex';
fid = fopen(filename,'w');
fprintf(fid,'%d\n',NumMatPoints);  % Write total number of points

for i = 1:BodyNx
    for j = 1:length(Coord{i,1})
        fprintf(fid,'%.10f\t%.10f\n',Coord{i,1}(j),Coord{i,2}(j));
    end
end
fclose(fid);

fprintf('\n=== VERTEX FILE WRITTEN ===\n');
fprintf('Filename: %s\n', filename);
fprintf('Format: IBAMR .vertex format\n');

%% =====================================================================
%% SECTION 6: TIMESTEP STABILITY ANALYSIS
%% =====================================================================
%% Compute safe timestep for IBAMR simulation based on CFL condition
%%
%% MAXIMUM VELOCITY CALCULATION:
%%   The velocity of material points comes from the traveling wave motion:
%%
%%   dy/dt = ∂[A_m(x)·cos(k·x - ω·t)]/∂t = ω·A_m(x)·sin(k·x - ω·t)
%%
%%   Maximum velocity: v_max = ω·max[A_m(x)]
%%
%%   where ω = 2π·c/λ = 12.5664 (from Eq. 3)
%%
%% CFL CONDITION:
%%   For stability: Δt ≤ Δx / v_max
%%   Safe timestep: Δt_safe = 0.25 × Δx / v_max
%%
%% FROM FIG. 2 VALIDATION: Δt = 0.005
%% =====================================================================

xi_test = 0:0.01:1;
A_max = max(abs(a0 + a1*xi_test + a2*xi_test.^2));  % Maximum amplitude
v_max = omega * A_max;                               % Maximum velocity
dt_safe = 0.25 * dx / v_max;                        % Safe timestep

fprintf('\n=== TIMESTEP STABILITY ANALYSIS ===\n');
fprintf('Maximum amplitude A_max = %.6f\n', A_max);
fprintf('Angular frequency ω = %.6f\n', omega);
fprintf('Maximum velocity v_max = ω·A_max = %.6f\n', v_max);
fprintf('Grid spacing dx = %.8f\n', dx);
fprintf('Safe timestep Δt_safe ≤ %.6e\n', dt_safe);
fprintf('\nFig. 2 uses Δt = 0.005\n');

%% =====================================================================
%% SECTION 7: GENERATE IBAMR input2d CONFIGURATION STRINGS
%% =====================================================================
%% Generate the exact mathematical expressions to be copied into the
%% IBAMR input2d configuration file
%%
%% IBAMR VARIABLES:
%%   X_0 = normalized x-coordinate (ξ = x/L)
%%   T   = time
%%   N_0 = x-component of surface normal vector
%%   N_1 = y-component of surface normal vector
%%
%% BODY SHAPE EQUATION (from Eq. 3 & 4):
%%   y(x,t) = A_m(x)·cos(k·x - ω·t)
%%   where A_m(x) = C_0 + C_1·x + C_2·x²
%%
%% DEFORMATION VELOCITY (time derivative of Eq. 3):
%%   v(x,t) = ∂y/∂t = ω·A_m(x)·sin(k·x - ω·t)·N
%%   where N = (N_0, N_1) is the surface normal vector
%% =====================================================================

fprintf('\n═══════════════════════════════════════════════════════\n');
fprintf('   COPY THESE LINES TO IBAMR input2d FILE\n');
fprintf('═══════════════════════════════════════════════════════\n\n');

amp_str  = sprintf('(%.6f + %.6f*X_0 + %.6f*X_0*X_0)', a0, a1, a2);
wave_arg = sprintf('%.6f*X_0 - %.6f*T', k, omega);

fprintf('// ─── Body Shape (Eq. 3 & 4) ───\n');
fprintf('body_shape_equation = "%s * cos(%s)"\n\n', amp_str, wave_arg);

fprintf('// ─── Deformation Velocity (∂y/∂t from Eq. 3) ───\n');
fprintf('deformation_velocity_function_0 = "%.6f * %s * sin(%s) * N_0"\n\n', omega, amp_str, wave_arg);
fprintf('deformation_velocity_function_1 = "%.6f * %s * sin(%s) * N_1"\n\n', omega, amp_str, wave_arg);

fprintf('═══════════════════════════════════════════════════════\n\n');

%% =====================================================================
%% SECTION 8: VISUALIZATION
%% =====================================================================
%% Plot the generated Lagrangian mesh and amplitude envelope to verify
%% they match Fig. 1(b) from Dong & Lu (2007)
%% =====================================================================

figure('Position',[100 100 1200 500]);

% ─────────────────────────────────────────────────────────────────────
% LEFT PANEL: Lagrangian mesh visualization
% ─────────────────────────────────────────────────────────────────────
subplot(1,2,1);
hold on;
for i = 1:BodyNx
    plot(Coord{i,1}, Coord{i,2}, 'k.', 'MarkerSize',1);
end
axis equal; grid on;
xlabel('x', 'FontSize',12);
ylabel('y', 'FontSize',12);
title(sprintf('Lagrangian Mesh: NACA0012 + Traveling Wave\n(%d material points)', NumMatPoints), 'FontSize',12);
legend(sprintf('c = %.1f, Re = 5000', c), 'Location', 'best');

% ─────────────────────────────────────────────────────────────────────
% RIGHT PANEL: Amplitude envelope A_m(ξ) - Compare with Fig. 1(b)
% ─────────────────────────────────────────────────────────────────────
subplot(1,2,2);
plot(xi_test, a0 + a1*xi_test + a2*xi_test.^2, 'b-', 'LineWidth',2);
hold on;
plot([0, 0.2, 1.0], [0.02, 0.01, 0.10], 'ro', 'MarkerSize',8, 'LineWidth',2);
grid on;
xlabel('\xi = x/L', 'FontSize',12);
ylabel('Amplitude A_m(\xi)', 'FontSize',12);
title('Amplitude Envelope (Eq. 4) - Compare with Fig. 1(b)', 'FontSize',12);
legend('A_m(\xi) = C_0 + C_1\xi + C_2\xi^2', 'Boundary conditions', 'Location', 'best');
ylim([0 0.12]);

fprintf('\n═══════════════════════════════════════════════════════\n');
fprintf('   SETUP COMPLETE - Ready for IBAMR Simulation\n');
fprintf('═══════════════════════════════════════════════════════\n');
fprintf('\nREFERENCE:\n');
fprintf('  Dong & Lu (2007), Physics of Fluids 19, 057107\n');
fprintf('  Figure 2: c = 2.0, Re = 5000\n');
fprintf('\n═══════════════════════════════════════════════════════\n\n');
