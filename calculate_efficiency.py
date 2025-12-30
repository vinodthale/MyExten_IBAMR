#!/usr/bin/env python3
"""
Calculate Equations 7 and 8: Force Coefficients and Quasipropulsive Efficiency
Based on hydrofoil hydrodynamics paper

Equation 7: C_T = F_T / (0.5 * ρ * u_p^2 * c)
Equation 8: η_QP = C_Tm / ∫ c_L(s,t) V_body(s,t) dS
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate

# ============================================
# PARAMETERS (Match your IBAMR simulation)
# ============================================

rho = 1.0           # Fluid density
u_p = 1.0           # Free-stream velocity (propulsive velocity)
c = 1.0             # Chord length
F_ref = 0.5 * rho * u_p**2 * c  # Reference force

# Time range for averaging (after transient)
t_start_avg = 5.0   # Start averaging after t = 5.0

# ============================================
# STEP 1: Load Global Force Data
# ============================================

print("Loading force data...")
F_data = np.loadtxt('Drag_CV_strct_id_0')

t_force = F_data[:, 0]
F_x = F_data[:, 1]  # Thrust (streamwise)
F_y = F_data[:, 2]  # Lateral (sideways)

# Calculate force coefficients (Equation 7)
C_T = F_x / F_ref
C_L = F_y / F_ref

# ============================================
# STEP 2: Time-Average Force Coefficients
# ============================================

idx_steady = t_force > t_start_avg

C_Tm = np.mean(C_T[idx_steady])  # Mean thrust coefficient
C_Lm = np.mean(C_L[idx_steady])  # Mean lateral coefficient

print(f"  C_Tm (mean thrust coefficient) = {C_Tm:.6f}")
print(f"  C_Lm (mean lateral coefficient) = {C_Lm:.6f}")

# ============================================
# STEP 3: Load Per-Marker Data
# ============================================

print("\nLoading marker data...")

try:
    M = np.loadtxt('Hydrofoil_marker_data.txt')
except FileNotFoundError:
    print("ERROR: Marker data file not found!")
    print("You need to instrument IBAMR to output per-marker forces/velocities.")
    print("See IBAMR_Efficiency_Implementation_Guide.md")
    exit(1)

t_marker = M[:, 0]
s = M[:, 1]
f_x_marker = M[:, 2]
f_y_marker = M[:, 3]  # Lateral force (f_l)
v_x_marker = M[:, 4]
v_y_marker = M[:, 5]  # Lateral velocity (v_body)

# ============================================
# STEP 4: Reshape and Non-dimensionalize
# ============================================

t_unique = np.unique(t_marker)
s_unique = np.unique(s)

N_t = len(t_unique)
N_s = len(s_unique)

print(f"  Number of time steps: {N_t}")
print(f"  Number of markers: {N_s}")

# Reshape to 2D grids [time × space]
fy_2d = f_y_marker.reshape((N_t, N_s))
vy_2d = v_y_marker.reshape((N_t, N_s))

# Non-dimensionalize
c_L = fy_2d / F_ref        # Force coefficient per unit length
V_body = vy_2d / u_p       # Velocity ratio

# ============================================
# STEP 5: Spatial Integration (Equation 8 Denominator)
# ============================================

print("\nCalculating input power...")

# Power density: p(s,t) = c_L(s,t) × V_body(s,t)
power_density = c_L * V_body

# Integrate over space: P_in(t) = ∫ p(s,t) ds
ds = np.mean(np.diff(s_unique))
P_in = integrate.trapezoid(power_density, s_unique, axis=1)

print(f"  Marker spacing ds = {ds:.6f}")

# ============================================
# STEP 6: Time-Average Input Power
# ============================================

idx_steady_marker = t_unique > t_start_avg
P_in_mean = np.mean(P_in[idx_steady_marker])

print(f"  Mean input power P_in = {P_in_mean:.6f}")

# ============================================
# STEP 7: Calculate Efficiency (Equation 8)
# ============================================

print("\nCalculating quasipropulsive efficiency...")

# For tethered simulation: P_out = C_Tm
# For free-swimming: P_out = C_Ds + C_Tm (where C_Ds is stationary drag)
P_out = C_Tm  # Tethered case

eta_QP = P_out / P_in_mean

# ============================================
# RESULTS DISPLAY
# ============================================

print()
print("╔════════════════════════════════════════════════╗")
print("║     HYDROFOIL PERFORMANCE RESULTS              ║")
print("╠════════════════════════════════════════════════╣")
print("║  EQUATION 7: Force Coefficients                ║")
print(f"║    C_Tm (thrust):      {C_Tm:+.6f}                 ║")
print(f"║    C_Lm (lateral):     {C_Lm:+.6f}                 ║")
print("╠════════════════════════════════════════════════╣")
print("║  EQUATION 8: Quasipropulsive Efficiency        ║")
print(f"║    P_out (numerator):  {P_out:.6f}                  ║")
print(f"║    P_in (denominator): {P_in_mean:.6f}                  ║")
print(f"║    η_QP:               {eta_QP:.6f} ({eta_QP*100:.2f}%)         ║")
print("╚════════════════════════════════════════════════╝")
print()

# ============================================
# VALIDATION CHECKS
# ============================================

if eta_QP < 0 or eta_QP > 1:
    print(f"WARNING: Efficiency out of physical range [0,1]: {eta_QP:.4f}")

if P_in_mean < 0:
    print("WARNING: Input power is negative - check force/velocity signs")

# ============================================
# SAVE RESULTS
# ============================================

results = {
    'C_Tm': C_Tm,
    'C_Lm': C_Lm,
    'P_out': P_out,
    'P_in': P_in_mean,
    'eta_QP': eta_QP,
    'eta_percent': eta_QP * 100
}

np.savez('hydrofoil_efficiency_results.npz', **results)
print("Results saved to: hydrofoil_efficiency_results.npz")

# ============================================
# PLOTTING
# ============================================

fig = plt.figure(figsize=(12, 6))
fig.patch.set_facecolor('white')

# Plot 1: Force coefficients time history
ax1 = plt.subplot(2, 2, 1)
ax1.plot(t_force, C_T, 'b-', linewidth=1.5, label='C_T(t)')
ax1.axhline(C_Tm, color='r', linestyle='--', linewidth=2,
            label=f'Mean = {C_Tm:.4f}')
ax1.axvline(t_start_avg, color='k', linestyle='--', linewidth=1.5,
            label='Avg starts')
ax1.grid(True)
ax1.set_xlabel('Time')
ax1.set_ylabel('$C_T$')
ax1.set_title('Thrust Coefficient (Equation 7)')
ax1.legend()

# Plot 2: Input power time history
ax2 = plt.subplot(2, 2, 2)
ax2.plot(t_unique, P_in, 'r-', linewidth=1.5, label='$P_{in}(t)$')
ax2.axhline(P_in_mean, color='k', linestyle='--', linewidth=2,
            label=f'Mean = {P_in_mean:.4f}')
ax2.axvline(t_start_avg, color='k', linestyle='--', linewidth=1.5,
            label='Avg starts')
ax2.grid(True)
ax2.set_xlabel('Time')
ax2.set_ylabel('$P_{in}$')
ax2.set_title('Input Power (Equation 8 Denominator)')
ax2.legend()

# Plot 3: Efficiency bar chart
ax3 = plt.subplot(2, 2, 3)
ax3.bar([1], [eta_QP], color=[0.2, 0.6, 0.8], width=0.5)
ax3.axhline(1.0, color='r', linestyle='--', linewidth=2, label='Physical limit')
ax3.set_ylim([0, 1.2])
ax3.set_ylabel('$\\eta_{QP}$')
ax3.set_title(f'Quasipropulsive Efficiency = {eta_QP*100:.2f}%')
ax3.set_xticks([1])
ax3.set_xticklabels(['Hydrofoil'])
ax3.grid(True, axis='y')
ax3.legend()

# Plot 4: Power density snapshot
ax4 = plt.subplot(2, 2, 4)
t_snap = int(0.7 * N_t)  # Snapshot at 70% of simulation
ax4.fill_between(s_unique, 0, power_density[t_snap, :], alpha=0.6)
ax4.set_xlabel('Arc length $s$')
ax4.set_ylabel('$c_L \\times V_{body}$')
ax4.set_title(f'Power Density at t = {t_unique[t_snap]:.3f}')
ax4.grid(True)

plt.tight_layout()
plt.savefig('Hydrofoil_Performance_Analysis.png', dpi=300, bbox_inches='tight')
print("\nPlot saved: Hydrofoil_Performance_Analysis.png")
plt.show()
