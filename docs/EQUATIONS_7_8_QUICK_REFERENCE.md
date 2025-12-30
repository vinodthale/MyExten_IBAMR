# Equations 7 & 8 - Quick Reference Card

## Visual Summary

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  EQUATION 7: Force Coefficients                            │
│  ═══════════════════════════                               │
│                                                             │
│      C_T = F_T / (½ρu_p²c)    [Thrust coefficient]        │
│      C_L = F_L / (½ρu_p²c)    [Lateral coefficient]       │
│                                                             │
│  Where:                                                     │
│    • F_T = Thrust force (from Drag_CV_strct_id file)      │
│    • F_L = Lateral force                                   │
│    • ρ = 1.0 (fluid density)                               │
│    • u_p = 1.0 (free-stream velocity)                      │
│    • c = 1.0 (chord length)                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  EQUATION 8: Quasipropulsive Efficiency                    │
│  ════════════════════════════════════                      │
│                                                             │
│      η_QP = P_out / P_in                                   │
│                                                             │
│  Expanded:                                                  │
│                                                             │
│          (F_Ds + F_Tm)u_p                                  │
│  η_QP = ─────────────────────                             │
│         ∫ f_l(s,t) v_body(s,t) dS                         │
│                                                             │
│  In coefficient form:                                       │
│                                                             │
│         C_Ds + C_Tm                                         │
│  η_QP = ──────────────────────                            │
│         ∫ c_L(s,t) V_body(s,t) ds                         │
│                                                             │
│  For TETHERED simulation (simpler):                        │
│                                                             │
│              C_Tm                                           │
│  η_QP = ──────────────────────                            │
│         ∫ c_L(s,t) V_body(s,t) ds                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## What Each Variable Means

### Physical Variables (Equation 7)

| Symbol | Name | What it is | Where to get it |
|--------|------|------------|----------------|
| F_T | Thrust force | Net forward push | `Drag_CV_strct_id_0` column 2 |
| F_L | Lateral force | Net sideways push | `Drag_CV_strct_id_0` column 3 |
| ρ | Density | Fluid density | From input2d (usually 1.0) |
| u_p | Propulsive velocity | Swimming/towing speed | = u_∞ for tethered (usually 1.0) |
| c | Chord length | Foil length | From geometry file (usually 1.0) |
| C_T | Thrust coefficient | Dimensionless thrust | Calculate: F_T/(0.5ρu_p²c) |
| C_L | Lateral coefficient | Dimensionless lateral force | Calculate: F_L/(0.5ρu_p²c) |

### Efficiency Variables (Equation 8)

| Symbol | Name | What it is | Where to get it |
|--------|------|------------|----------------|
| η_QP | Quasipropulsive efficiency | How efficient the swimming is | **This is what you calculate!** |
| P_out | Output power | Useful thrust power | = C_Tm for tethered |
| P_in | Input power | Power to move the body | ∫ c_L × V_body ds |
| F_Ds | Stationary drag | Drag when not moving | From literature or separate sim |
| F_Tm | Mean thrust | Time-averaged thrust | Average of C_T after transient |
| C_Tm | Mean thrust coef. | Time-averaged C_T | mean(C_T) for t > 5.0 |
| f_l(s,t) | Local lateral force | Force at point s, time t | **Need marker data** |
| v_body(s,t) | Local lateral velocity | Velocity at point s, time t | **Need marker data** |
| c_L(s,t) | Force coefficient | f_l/(0.5ρu_p²c) | Calculate from marker data |
| V_body(s,t) | Velocity ratio | v_body/u_p | Calculate from marker data |

## Step-by-Step Calculation

### ✅ STEP 1: Calculate C_T (Easy - you already have this!)

```
From your IBAMR output file: Drag_CV_strct_id_0

C_T = Column_2 / (0.5 × 1.0 × 1.0² × 1.0)
    = Column_2 / 0.5
    = 2 × Column_2
```

### ✅ STEP 2: Calculate C_Tm (Time average)

```
C_Tm = mean(C_T) for times after t = 5.0

In MATLAB:
  idx = (time > 5.0);
  C_Tm = mean(C_T(idx));

In Python:
  idx = time > 5.0
  C_Tm = np.mean(C_T[idx])
```

### ⚠️ STEP 3: Calculate P_in (Needs marker data!)

```
This is the HARD part - requires per-marker forces and velocities

P_in(t) = ∫ [f_y(s,t) × v_y(s,t)] ds
          ─────────────────────────
          (0.5 × ρ × u_p³ × c)

Numerical approximation:
  P_in(t) ≈ Σ [f_y(i,t) × v_y(i,t)] × Δs
            i=1 to N_markers

Then time-average:
  P_in_mean = mean(P_in(t)) for t > 5.0
```

### ✅ STEP 4: Calculate efficiency

```
For TETHERED simulation:
  η_QP = C_Tm / P_in_mean

For FREE-SWIMMING:
  η_QP = (C_Ds + C_Tm) / P_in_mean
  where C_Ds ≈ 0.05 for NACA0012 (get from literature)
```

## The Challenge: Getting Marker Data

### What you have now ✅
- Global forces: `Drag_CV_strct_id_0`
- Contains total F_x and F_y
- Enough for Equation 7

### What you need for Equation 8 ⚠️
- Per-marker forces: f_y at each point along the foil
- Per-marker velocities: v_y at each point along the foil
- At each time step

### How to get it
**Option 1: Modify IBAMR source code** (recommended)
- See `IBAMR_Efficiency_Implementation_Guide.md`
- Add code to output marker data
- Recompile IBAMR
- Run simulation
- Get file: `Hydrofoil_marker_data.txt`

**Option 2: Use analytical approximation** (less accurate)
- Assume sinusoidal motion: v_y(s,t) = A(s)ω cos(ks - ωt)
- Approximate f_y from resistive force theory
- See literature (Liu et al. 1996)

## Typical Values

### Expected Efficiency Range
```
η_QP = 0.0      → No thrust generated (all power wasted)
η_QP = 0.3-0.5  → Typical for basic oscillating foils
η_QP = 0.6-0.8  → Optimized oscillating foils
η_QP = 1.0      → Perfect (impossible in real world)
```

### For Your Simulation (St ≈ 0.4, Re = 5000)
```
Expected: η_QP ≈ 0.4 - 0.6
```

If you get values outside this range, check:
- Sign of forces (should use f_y not f_x for lateral)
- Sign of velocities (should use v_y not v_x)
- Integration direction
- Time averaging range

## Quick Validation Checklist

- [ ] C_T is POSITIVE (thrust, not drag)
- [ ] C_Tm is stable after transient (t > 5.0)
- [ ] P_in is POSITIVE (always requires energy input)
- [ ] P_in oscillates at flapping frequency
- [ ] 0 < η_QP < 1 (physical bounds)
- [ ] η_QP ≈ 0.4-0.6 (reasonable for your Re and St)

## Files You Need

```
Input files (from IBAMR):
├── Drag_CV_strct_id_0           ← Global forces (you have this)
└── Hydrofoil_marker_data.txt    ← Per-marker data (need to create)

Analysis scripts (provided):
├── calculate_efficiency.py      ← Python calculator
└── docs/CALCULATE_EQUATIONS_7_8.md  ← MATLAB calculator

Documentation:
├── EQUATIONS_7_8_QUICK_REFERENCE.md  ← This file
├── POWER_AND_EFFICIENCY_CALCULATIONS.md
└── IBAMR_Efficiency_Implementation_Guide.md
```

## Common Mistakes

### ❌ Mistake 1: Using wrong force component
```
WRONG: P_in = ∫ f_x × v_x ds  (streamwise)
RIGHT: P_in = ∫ f_y × v_y ds  (lateral/sideways)
```

### ❌ Mistake 2: Wrong denominator units
```
WRONG: F_ref = ρ × u_p² × c
RIGHT: F_ref = 0.5 × ρ × u_p² × c  (note the 0.5!)
```

### ❌ Mistake 3: Not removing transient
```
WRONG: mean(C_T[all_time])
RIGHT: mean(C_T[time > 5.0])
```

### ❌ Mistake 4: Using instantaneous instead of time-averaged
```
WRONG: η_QP = C_T(t_final) / P_in(t_final)
RIGHT: η_QP = mean(C_T) / mean(P_in)  for t > 5.0
```

## Need Help?

1. **For understanding equations**: Read this file + `CALCULATE_EQUATIONS_7_8.md`
2. **For getting marker data**: See `IBAMR_Efficiency_Implementation_Guide.md`
3. **For calculation code**: Use `calculate_efficiency.py` or MATLAB script
4. **For theory**: See `POWER_AND_EFFICIENCY_CALCULATIONS.md`

---

**Remember**: The key challenge is getting the **per-marker data** for the integral in Equation 8. Everything else is straightforward arithmetic!
