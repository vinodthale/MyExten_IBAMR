%% =====================================================================
%% IBAMR NACA0012 Traveling Wavy Foil - Simplified
%% Based on: Dong & Lu (2007) - Single wavy foil
%% FIG. 2. Time-dependent drag and lateral force coefficients during one cycle
%% for flow over a single traveling wavy foil at c=2.0.
%% =====================================================================
clear; clc; close all;

%% =====================================================================
%% SECTION 1: DOMAIN AND GRID (MUST MATCH input2d EXACTLY!)
%% =====================================================================
% These parameters MUST match your input2d file
MAX_LEVELS = 3;      % Number of AMR levels
REF_RATIO  = 4;      % Refinement ratio between levels
N = 256;             % Coarsest grid resolution

Lx = 16.0;           % Domain length
Ly = 8.0;            % Domain height

% Finest grid spacing (calculated automatically)
Nx = 2*N*REF_RATIO^(MAX_LEVELS-1);
Ny = N*REF_RATIO^(MAX_LEVELS-1);
dx = Lx/Nx;
dy = Ly/Ny;

fprintf('Finest mesh: dx = dy = %.8f\n', dx);

%% =====================================================================
%% SECTION 2: FOIL GEOMETRY (USER-DEFINED)
%% =====================================================================
% Modify these to position your foil
L = 1.0;             % Chord length (reference length scale)
x_LE = 5.0;          % Leading edge x-position
y_LE = 4.0;          % Leading edge y-position (centerline)
t_max = 0.12 * L;    % NACA0012 max thickness (12% of chord)

%% =====================================================================
%% SECTION 3: TRAVELING WAVE PARAMETERS (USER-DEFINED)
%% =====================================================================
% Modify these to change swimming kinematics
% Based on Dong & Lu (2007), Figure 2 parameters:

c = 2.0;             % Phase speed (wave propagation speed)
lambda = 1.0;        % Wavelength (spatial period of wave)

% Amplitude envelope coefficients: A(xi) = a0 + a1*xi + a2*xi^2
% where xi = x/L (normalized coordinate from 0 to 1)
a0 = 0.02;           % Constant amplitude term
a1 = -0.0825;        % Linear amplitude term
a2 = 0.1625;         % Quadratic amplitude term

% Computed parameters (do not modify)
k = 2*pi/lambda;     % Wave number
omega = k*c;         % Angular frequency

%% =====================================================================
%% SECTION 4: MESH GENERATION (AUTOMATIC - DO NOT MODIFY)
%% =====================================================================

% Discretization
BodyNx = ceil(L/dx);

% Generate mesh
NumMatPoints = 0;
Coord = cell(BodyNx, 2);

for i = 1:BodyNx
    x = (i-1)*dx;
    xi = x/L;
    
    % Amplitude and midline at t=0
    A_xi = a0 + a1*xi + a2*xi^2;
    y_mid = A_xi * cos(k*x);
    
    % NACA0012 thickness distribution
    thickness = 0.2969*sqrt(xi) - 0.1260*xi - 0.3516*xi^2 ...
              + 0.2843*xi^3 - 0.1015*xi^4;
    height = (t_max/0.2) * thickness;
    
    % Points across thickness
    NumPoints = ceil(height/dy);
    
    xcoord = [];
    ycoord = [];
    
    for j = 1:NumPoints
        % Upper surface
        xcoord(j) = x + x_LE;
        ycoord(j) = y_mid + y_LE + (j-1)*dy;
        
        % Lower surface
        xcoord(NumPoints+j) = x + x_LE;
        ycoord(NumPoints+j) = y_mid + y_LE - j*dy;
        
        NumMatPoints = NumMatPoints + 2;
    end
    
    Coord{i,1} = xcoord;
    Coord{i,2} = ycoord;
end

fprintf('Generated %d material points\n', NumMatPoints);

%% =====================================================================
%% SECTION 5: OUTPUT VERTEX FILE (USER CAN CHANGE FILENAME)
%% =====================================================================
filename = 'nacafish1bot.vertex';  % Change filename if desired

fid = fopen(filename, 'w');
fprintf(fid, '%d\n', NumMatPoints);
for i = 1:BodyNx
    for j = 1:length(Coord{i,1})
        fprintf(fid, '%.10f\t%.10f\n', Coord{i,1}(j), Coord{i,2}(j));
    end
end
fclose(fid);
fprintf('Written: %s\n', filename);

%% =====================================================================
%% SECTION 6: TIMESTEP STABILITY CHECK (AUTOMATIC)
%% =====================================================================
A_max = max(abs(a0 + a1*(0:0.01:1) + a2*(0:0.01:1).^2));
v_max = omega * A_max;
dt_safe = 0.25 * dx / v_max;

fprintf('\nTimestep stability:\n');
fprintf('  Max velocity = %.6f\n', v_max);
fprintf('  Safe DT_MAX <= %.6e\n', dt_safe);

%% =====================================================================
%% SECTION 7: GENERATE input2d STRINGS (COPY TO YOUR input2d FILE)
%% =====================================================================
fprintf('\n=== COPY TO input2d ===\n\n');

amp_str = sprintf('(%.6f + %.6f*X_0 + %.6f*X_0*X_0)', a0, a1, a2);
wave_arg = sprintf('%.6f*X_0 - %.6f*T', k, omega);

fprintf('body_shape_equation = "%s * cos(%s)"\n\n', amp_str, wave_arg);
fprintf('deformation_velocity_function_0 = "%.6f * %s * sin(%s) * N_0"\n\n', omega, amp_str, wave_arg);
fprintf('deformation_velocity_function_1 = "%.6f * %s * sin(%s) * N_1"\n\n', omega, amp_str, wave_arg);

%% =====================================================================
%% SECTION 8: VISUALIZATION (AUTOMATIC)
%% =====================================================================
figure('Position', [100 100 1200 500]);

subplot(1,2,1);
xlim([4.972 6.063])
ylim([3.479 4.587])
hold on;
for i = 1:BodyNx
    plot(Coord{i,1}, Coord{i,2}, 'k.', 'MarkerSize', 1);
end
axis equal; grid on;
xlabel('x'); ylabel('y');
title(sprintf('NACA0012 Mesh (%d pts)', NumMatPoints));

subplot(1,2,2);
xi_plot = 0:0.01:1;
A_plot = a0 + a1*xi_plot + a2*xi_plot.^2;
plot(xi_plot, A_plot, 'b-', 'LineWidth', 2);
grid on;
xlabel('\xi = x/L'); ylabel('Amplitude');
title('Wave Envelope A(\xi)');

fprintf('\n======================\n');