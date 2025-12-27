%% ---------------------------------------------------------------------
%% Two Tethered Wavy Hydrofoils — Side-by-Side (SIMPLIFIED)
%% PAPER: Fig. 3(a) — Mesh independence study
%%
%% Physical parameters:
%%   Re = 5000, St = 0.4, A_max = 0.1, lambda = 2
%%   phi/pi = 1 (ANTI-PHASE motion), G = 0.3L, D = 0.5L
%% ---------------------------------------------------------------------

clear; clc;

%% Grid Parameters
MAX_LEVELS = 3;
REF_RATIO  = 4;
N = 256;

finest   = MAX_LEVELS - 1;
ref_mult = REF_RATIO^finest;

Lx = 16; 
Ly = 8;

Nx = 2*N*ref_mult;
Ny = N*ref_mult;

dx = Lx/Nx;
dy = Ly/Ny;

fprintf('Grid: %d x %d cells\n', Nx, Ny);
fprintf('Grid spacing: dx = dy = %.6f\n\n', dx);

%% Geometry Parameters
L = 1.0;
angleRotation = 0;
R = [cos(angleRotation) -sin(angleRotation);
     sin(angleRotation)  cos(angleRotation)];

BodyNx = ceil(L/dx);
NumMatPoints = 0;

%% Kinematics Parameters (from paper)
A_max  = 0.1;
lambda = 2.0;
St     = 0.4;
f      = St/(2*A_max);
phi1   = 0.0;      % Bottom fish phase
phi2   = pi;       % Top fish phase (anti-phase)
tstar  = 0.0;      % Initial time snapshot
tmax   = 0.12*L;   % NACA0012 thickness

%% Generate Hydrofoil Coordinates
Coord1 = cell(BodyNx,2);   % Bottom fish (phi = 0)
Coord2 = cell(BodyNx,2);   % Top fish (phi = pi)

for i = 1:BodyNx
    x  = (i-1)*dx;
    xi = min(max(x/L,0),1);   % Normalized coordinate
    
    % Traveling wave amplitude envelope
    a_x = A_max * xi;
    omega = St/(2*A_max);
    
    % Lateral displacement for each fish
    y1 = a_x * sin(2*pi*(xi/lambda - omega*tstar) + phi1);
    y2 = a_x * sin(2*pi*(xi/lambda - omega*tstar) + phi2);
    
    % NACA0012 thickness distribution
    thickness = 0.2969*sqrt(xi) - 0.1260*xi - 0.3516*xi^2 ...
              + 0.2843*xi^3 - 0.1015*xi^4;
    
    height = max((tmax/0.2)*thickness, 0);
    Nh = ceil(height/dy);
    
    xu1=[]; xd1=[]; yu1=[]; yd1=[];
    xu2=[]; xd2=[]; yu2=[]; yd2=[];
    
    for j = 1:Nh
        P1 = R*[x; y1];
        P2 = R*[x; y2];
        
        xu1(j) = P1(1); 
        xd1(j) = P1(1);
        yu1(j) = P1(2) + (j-1)*dy;
        yd1(j) = P1(2) - j*dy;
        
        xu2(j) = P2(1); 
        xd2(j) = P2(1);
        yu2(j) = P2(2) + (j-1)*dy;
        yd2(j) = P2(2) - j*dy;
        
        NumMatPoints = NumMatPoints + 2;
    end
    
    Coord1{i,1} = [xu1 xd1];
    Coord1{i,2} = [yu1 yd1];
    
    Coord2{i,1} = [xu2 xd2];
    Coord2{i,2} = [yu2 yd2];
end

%% Position Fish in Domain
G = 0.3;   % Vertical spacing
D = 0.5;   % Streamwise spacing

fish_X_center = 5.0;
fish_Y_center = 4.0;

x_nose_1 = fish_X_center;
y_nose_1 = fish_Y_center - G*0.5;

x_nose_2 = fish_X_center + D;
y_nose_2 = y_nose_1 + G;

Coord_fish1 = Coord1;
Coord_fish2 = Coord2;

for i = 1:BodyNx
    Coord_fish1{i,1} = Coord1{i,1} + x_nose_1;
    Coord_fish1{i,2} = Coord1{i,2} + y_nose_1;
    
    Coord_fish2{i,1} = Coord2{i,1} + x_nose_2;
    Coord_fish2{i,2} = Coord2{i,2} + y_nose_2;
end

%% Write Vertex Files
fid1 = fopen('nacafish1bot.vertex','w');
fprintf(fid1,'%d\n', NumMatPoints);
for i = 1:BodyNx
    n_pts = length(Coord_fish1{i,1});
    for j = 1:n_pts
        fprintf(fid1,'%.16f %.16f\n', Coord_fish1{i,1}(j), Coord_fish1{i,2}(j));
    end
end
fclose(fid1);

fid2 = fopen('nacafish2top.vertex','w');
fprintf(fid2,'%d\n', NumMatPoints);
for i = 1:BodyNx
    n_pts = length(Coord_fish2{i,1});
    for j = 1:n_pts
        fprintf(fid2,'%.16f %.16f\n', Coord_fish2{i,1}(j), Coord_fish2{i,2}(j));
    end
end
fclose(fid2);

fprintf('Vertex files written:\n');
fprintf('  nacafish1bot.vertex: %d points\n', NumMatPoints);
fprintf('  nacafish2top.vertex: %d points\n\n', NumMatPoints);

%% Visualization
figure('Position',[100 100 1200 700]); 
hold on;

for i = 1:BodyNx
    plot(Coord_fish1{i,1}, Coord_fish1{i,2}, 'r.', 'MarkerSize', 4);
    plot(Coord_fish2{i,1}, Coord_fish2{i,2}, 'b.', 'MarkerSize', 4);
end

% Centerlines
plot([x_nose_1 x_nose_1+1], [y_nose_1 y_nose_1], 'r-', 'LineWidth', 2);
plot([x_nose_2 x_nose_2+1], [y_nose_2 y_nose_2], 'b-', 'LineWidth', 2);

% Nose markers
plot(x_nose_1, y_nose_1, 'ro', 'MarkerSize', 10, 'MarkerFaceColor', 'r');
plot(x_nose_2, y_nose_2, 'bo', 'MarkerSize', 10, 'MarkerFaceColor', 'b');

% Spacing annotations
quiver(x_nose_1-0.3, y_nose_1, 0, G, 0, 'k', 'LineWidth', 2, 'MaxHeadSize', 0.6);
text(x_nose_1-0.45, y_nose_1+G/2, 'G', 'FontWeight', 'bold', 'FontSize', 12);

quiver(x_nose_1, y_nose_1-0.3, D, 0, 0, 'k', 'LineWidth', 2, 'MaxHeadSize', 0.6);
text(x_nose_1+D/2, y_nose_1-0.45, 'D', 'FontWeight', 'bold', 'FontSize', 12);

% Domain boundary
rectangle('Position', [0 0 Lx Ly], 'EdgeColor', 'k', 'LineWidth', 2);

title('Two Tethered Hydrofoils (Anti-Phase)', 'FontWeight', 'bold', 'FontSize', 14);
xlabel('x/C'); 
ylabel('y/C');
axis equal; 
grid on;
xlim([3 8]); 
ylim([2.8 5.2]);
legend({'Fish 1 (Bottom)', 'Fish 2 (Top)'}, 'Location', 'northeast');

%% Summary
fprintf('Configuration:\n');
fprintf('  Fish 1 (bottom): (%.1f, %.2f)\n', x_nose_1, y_nose_1);
fprintf('  Fish 2 (top):    (%.2f, %.2f)\n', x_nose_2, y_nose_2);
fprintf('  G = %.1f, D = %.1f\n\n', G, D);

fprintf('Kinematics:\n');
fprintf('  A_max = %.2f, lambda = %.1f, St = %.1f\n', A_max, lambda, St);
fprintf('  Phase shift = %.2f rad (anti-phase)\n\n', phi2-phi1);

fprintf('IBAMR Deformation Functions:\n\n');
fprintf('Fish 1 (Bottom, phi=0):\n');
fprintf('  body_shape_equation = "(0.1*X_0)*sin(PI*X_0 - 4*PI*T)"\n');
fprintf('  deformation_velocity_function_0 = "(-1.2566370614359172*X_0*cos(PI*X_0 - 4*PI*T))*N_0"\n');
fprintf('  deformation_velocity_function_1 = "(-1.2566370614359172*X_0*cos(PI*X_0 - 4*PI*T))*N_1"\n\n');

fprintf('Fish 2 (Top, phi=PI):\n');
fprintf('  body_shape_equation = "(0.1*X_0)*sin(PI*X_0 - 4*PI*T + PI)"\n');
fprintf('  deformation_velocity_function_0 = "(-1.2566370614359172*X_0*cos(PI*X_0 - 4*PI*T + PI))*N_0"\n');
fprintf('  deformation_velocity_function_1 = "(-1.2566370614359172*X_0*cos(PI*X_0 - 4*PI*T + PI))*N_1"\n');

fprintf('--------------------------------------------------\n');
fprintf('IBAMR KINEMATICS (PI HARD-CODED)\n');
fprintf('--------------------------------------------------\n\n');

fprintf('Fish 1 (Bottom, phi = 0):\n');
fprintf('  body_shape_equation = "(0.1*X_0)*sin(3.141592653589793*X_0 - 12.566370614359172*T)"\n');
fprintf('  deformation_velocity_function_0 = "(-1.2566370614359172*X_0*cos(3.141592653589793*X_0 - 12.566370614359172*T))*N_0"\n');
fprintf('  deformation_velocity_function_1 = "(-1.2566370614359172*X_0*cos(3.141592653589793*X_0 - 12.566370614359172*T))*N_1"\n\n');

fprintf('Fish 2 (Top, phi = PI):\n');
fprintf('  body_shape_equation = "(0.1*X_0)*sin(3.141592653589793*X_0 - 12.566370614359172*T + 3.141592653589793)"\n');
fprintf('  deformation_velocity_function_0 = "(-1.2566370614359172*X_0*cos(3.141592653589793*X_0 - 12.566370614359172*T + 3.141592653589793))*N_0"\n');
fprintf('  deformation_velocity_function_1 = "(-1.2566370614359172*X_0*cos(3.141592653589793*X_0 - 12.566370614359172*T + 3.141592653589793))*N_1"\n');
