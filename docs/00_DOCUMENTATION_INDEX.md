# IBAMR Force Calculation - Complete Documentation Index

## Quick Navigation

This directory contains comprehensive documentation explaining how IBAMR computes hydrodynamic forces and how to interpret the output files.

---

## 📚 Main Documentation Files

### 1. **START HERE**: General Force Calculation

**File:** [`README_FORCE_CALCULATION.md`](./README_FORCE_CALCULATION.md)

**What it covers:**
- Overview of all documentation
- Quick start guide
- How to verify force files
- Key takeaways

**Read this first!**

---

### 2. Force Calculation Physics

**File:** [`FORCE_CALCULATION_EXPLAINED.md`](./FORCE_CALCULATION_EXPLAINED.md)

**What it covers:**
- Where `Drag_CV_strct_id_0` files are created (line 237)
- Reynolds Transport Theorem explanation
- All three force components:
  - Pressure forces
  - Viscous forces
  - Momentum flux
- Why you can trust the forces
- Complete physics derivation

**Read this for:** Understanding the physics behind force calculation

---

### 3. Visual Guide

**File:** [`FORCE_CALCULATION_VISUAL_SUMMARY.md`](./FORCE_CALCULATION_VISUAL_SUMMARY.md)

**What it covers:**
- Flowcharts and diagrams
- Timeline of force computation
- Stress tensor breakdown
- File format explanation
- Verification methods

**Read this for:** Visual understanding with diagrams

---

### 4. Code Reference

**File:** [`CODE_LOCATIONS_REFERENCE.md`](./CODE_LOCATIONS_REFERENCE.md)

**What it covers:**
- Exact line numbers for every operation
- Code snippets with explanations
- Search commands to find code yourself
- Mathematical formulas matched to code

**Read this for:** Finding specific code in IBAMR source

---

### 5. Momentum Calculation Flags

**File:** [`MOMENTUM_FLAGS_EXPLAINED.md`](./MOMENTUM_FLAGS_EXPLAINED.md)

**What it covers:**
- What `calculate_translational_momentum` does
- What `calculate_rotational_momentum` does
- Which directions are calculated
- Connection to self-propulsion
- Effect on force calculation (spoiler: none directly!)

**Read this for:** Understanding the input file flags like:
```
calculate_translational_momentum = 1,1,0
calculate_rotational_momentum    = 0,0,1
```

---

### 6. **NEW!** Tethered Body Forces

**File:** [`README_TETHERED_BODY_FORCES.md`](./README_TETHERED_BODY_FORCES.md)

**What it covers:**
- What "tethered" means (body deforms but doesn't move)
- How it differs from free swimming
- Your specific use case: NACA0012 hydrofoils in free stream
- Connection to experimental thrust measurements
- Two-fish interaction studies
- Force interpretation: net propulsive thrust

**Read this for:** Understanding thrust measurements on swimming bodies

---

### 7. **NEW!** Power and Efficiency Calculations

**File:** [`POWER_AND_EFFICIENCY_CALCULATIONS.md`](./POWER_AND_EFFICIENCY_CALCULATIONS.md)

**What it covers:**
- Propulsive efficiency equation (Liu et al., 1996)
- Input power vs output power definitions
- Leader/follower foil indexing (i=1, i=2)
- How to compute ∫ c_L V_body ds integral
- Complete workflow for efficiency calculation
- MATLAB and Python post-processing scripts
- IBAMR code instrumentation guide
- Per-marker force and velocity extraction

**Read this for:** Computing propulsive efficiency η = P_out / P_in for swimming bodies

**Key equations:**
```
η_i = P_out,i / P_in,i = C_Tm,i / ∫ c_L,i(s,t) V_body,i(s,t) ds
```

---

## 🎯 Use Case Guide

### I want to understand...

#### "Where do the force files come from?"
→ Read: [`FORCE_CALCULATION_EXPLAINED.md`](./FORCE_CALCULATION_EXPLAINED.md)
→ See: Line 237 in `IBHydrodynamicForceEvaluator.cpp`

#### "What physics is being computed?"
→ Read: [`FORCE_CALCULATION_EXPLAINED.md`](./FORCE_CALCULATION_EXPLAINED.md)
→ Key concept: Reynolds Transport Theorem

#### "What do those momentum flags do?"
→ Read: [`MOMENTUM_FLAGS_EXPLAINED.md`](./MOMENTUM_FLAGS_EXPLAINED.md)
→ Short answer: Control swimming direction, NOT force calculation

#### "How do I measure thrust on a swimming fish?"
→ Read: [`README_TETHERED_BODY_FORCES.md`](./README_TETHERED_BODY_FORCES.md)
→ Configuration: All momentum flags = 0 (tethered)

#### "Where exactly is this in the code?"
→ Read: [`CODE_LOCATIONS_REFERENCE.md`](./CODE_LOCATIONS_REFERENCE.md)
→ Has all line numbers and code snippets

#### "I'm a visual learner"
→ Read: [`FORCE_CALCULATION_VISUAL_SUMMARY.md`](./FORCE_CALCULATION_VISUAL_SUMMARY.md)
→ Has flowcharts and diagrams

#### "How do I compute propulsive efficiency?"
→ Read: [`POWER_AND_EFFICIENCY_CALCULATIONS.md`](./POWER_AND_EFFICIENCY_CALCULATIONS.md)
→ Complete workflow from simulation to efficiency calculation

#### "What is input power vs output power?"
→ Read: [`POWER_AND_EFFICIENCY_CALCULATIONS.md`](./POWER_AND_EFFICIENCY_CALCULATIONS.md)
→ Section 2: Theoretical Background

#### "How do I extract per-marker force and velocity data?"
→ Read: [`POWER_AND_EFFICIENCY_CALCULATIONS.md`](./POWER_AND_EFFICIENCY_CALCULATIONS.md)
→ Section 6: Implementation in IBAMR

---

## 🔬 Research Use Cases

### Free Swimming Fish

**Configuration:**
```
calculate_translational_momentum = 1,1,0
calculate_rotational_momentum    = 0,0,1
```

**What this does:**
- Fish can swim and turn
- Force output shows transient forces during acceleration
- At steady swimming, net force → 0

**Documentation:** [`MOMENTUM_FLAGS_EXPLAINED.md`](./MOMENTUM_FLAGS_EXPLAINED.md)

---

### Propulsive Efficiency Analysis

**Configuration:**
```
calculate_translational_momentum = 0,0,0  (tethered for thrust measurement)
calculate_rotational_momentum    = 0,0,0
```

**What this does:**
- Body deforms (swims) but stays in place
- Enables accurate thrust measurement
- Compute input power from marker forces/velocities
- Compute output power from thrust
- Calculate efficiency η = P_out / P_in

**Documentation:** [`POWER_AND_EFFICIENCY_CALCULATIONS.md`](./POWER_AND_EFFICIENCY_CALCULATIONS.md)

**Your use case:**
- Leader/follower foils (i=1, i=2)
- Compare efficiency of foils in tandem
- Analyze hydrodynamic interaction effects
- Quantify energy savings or penalties

---

### Tethered Swimming (Thrust Measurement)

**Configuration:**
```
calculate_translational_momentum = 0,0,0
calculate_rotational_momentum    = 0,0,0
```

**What this does:**
- Fish deforms (swims) but stays in place
- Force output = net thrust production
- Matches experimental force balance measurements

**Documentation:** [`README_TETHERED_BODY_FORCES.md`](./README_TETHERED_BODY_FORCES.md)

**Your use case:**
- Two NACA0012 hydrofoils
- Wavy lateral movement
- Free stream flow
- Measuring hydrodynamic interaction

---

### Flow Past Stationary Body

**Configuration:**
```
# No deformation, no momentum calculation
```

**What this does:**
- Body is completely rigid
- Force output = drag and lift
- Standard flow past cylinder/airfoil

**Documentation:** [`FORCE_CALCULATION_EXPLAINED.md`](./FORCE_CALCULATION_EXPLAINED.md)

---

## 🛠️ Tools and Scripts

### Force File Verification

**File:** [`verify_force_files.py`](./verify_force_files.py)

**What it does:**
- Checks file format
- Computes statistics
- Creates plots
- Verifies steady state

**How to use:**
```bash
cd /path/to/simulation/output
python3 /home/user/MyExten_IBAMR/docs/verify_force_files.py
```

---

## 📊 File Format Reference

### Force Output Files

**Files created:**
- `Drag_CV_strct_id_0` - Force on structure 0
- `Torque_CV_strct_id_0` - Torque on structure 0
- `Drag_CV_strct_id_1` - Force on structure 1 (if multiple structures)
- etc.

**Format:**
```
time        Fx          Fy          Fz
0.000000    0.0000000   0.0000000   0.0000000
0.001000    0.1234567   0.0123456   0.0012345
...
```

**Naming convention:**
- `Drag` = Force (not torque)
- `CV` = Control Volume method
- `strct_id_N` = Structure ID number

**See:** [`FORCE_CALCULATION_EXPLAINED.md`](./FORCE_CALCULATION_EXPLAINED.md) for details

---

## 🔑 Key Code Locations

Quick reference to important source files:

### Force Calculation Class
- **Header:** `IBAMR-0.18.0/include/ibamr/IBHydrodynamicForceEvaluator.h`
- **Implementation:** `IBAMR-0.18.0/src/IB/IBHydrodynamicForceEvaluator.cpp`

### Key Functions
| Function | Lines | Purpose |
|----------|-------|---------|
| `registerStructure()` | 115-247 | Creates force output files |
| `computeLaggedMomentumIntegral()` | 312-456 | Old momentum |
| `computeHydrodynamicForce()` | 477-788 | Main force calculation |
| `postprocessIntegrateData()` | 790-820 | Writes to files |

### Critical Lines
| Line | What Happens |
|------|--------------|
| 237 | File name created: `"Drag_CV_strct_id_" + strct_id_str` |
| 690-696 | Pressure force computed |
| 698-717 | Momentum flux computed |
| 719-769 | Viscous force computed |
| 778-783 | Reynolds Transport Theorem applied |
| 800-801 | Force written to file |

**See:** [`CODE_LOCATIONS_REFERENCE.md`](./CODE_LOCATIONS_REFERENCE.md) for complete listing

---

## 📖 Reading Order

### Beginner Path

1. Start: [`README_FORCE_CALCULATION.md`](./README_FORCE_CALCULATION.md)
2. Visual: [`FORCE_CALCULATION_VISUAL_SUMMARY.md`](./FORCE_CALCULATION_VISUAL_SUMMARY.md)
3. Your case: [`README_TETHERED_BODY_FORCES.md`](./README_TETHERED_BODY_FORCES.md)
4. Verify: Run `verify_force_files.py`

### Advanced Path

1. Physics: [`FORCE_CALCULATION_EXPLAINED.md`](./FORCE_CALCULATION_EXPLAINED.md)
2. Flags: [`MOMENTUM_FLAGS_EXPLAINED.md`](./MOMENTUM_FLAGS_EXPLAINED.md)
3. Code: [`CODE_LOCATIONS_REFERENCE.md`](./CODE_LOCATIONS_REFERENCE.md)
4. Source: Read `IBHydrodynamicForceEvaluator.cpp` directly

### Research Path (Your Use Case)

1. **Must read:** [`README_TETHERED_BODY_FORCES.md`](./README_TETHERED_BODY_FORCES.md)
2. Understand physics: [`FORCE_CALCULATION_EXPLAINED.md`](./FORCE_CALCULATION_EXPLAINED.md)
3. Configure flags: [`MOMENTUM_FLAGS_EXPLAINED.md`](./MOMENTUM_FLAGS_EXPLAINED.md)
4. Verify data: Run `verify_force_files.py`

---

## ❓ FAQ

### Q: Can I trust the force data?
**A:** YES! See [`FORCE_CALCULATION_EXPLAINED.md`](./FORCE_CALCULATION_EXPLAINED.md) for proof.

### Q: What do the momentum flags do?
**A:** See [`MOMENTUM_FLAGS_EXPLAINED.md`](./MOMENTUM_FLAGS_EXPLAINED.md)
**Short answer:** Control swimming direction, NOT force calculation directly.

### Q: How do I measure thrust?
**A:** See [`README_TETHERED_BODY_FORCES.md`](./README_TETHERED_BODY_FORCES.md)
**Short answer:** Set all momentum flags to 0 (tethered configuration).

### Q: Where is the file name created?
**A:** Line 237 of `IBHydrodynamicForceEvaluator.cpp`
**See:** [`CODE_LOCATIONS_REFERENCE.md`](./CODE_LOCATIONS_REFERENCE.md)

### Q: What physics is computed?
**A:** Reynolds Transport Theorem with control volume integration
**See:** [`FORCE_CALCULATION_EXPLAINED.md`](./FORCE_CALCULATION_EXPLAINED.md)

### Q: How does tethering work?
**A:** Body deforms but momentum flags prevent translation/rotation
**See:** [`README_TETHERED_BODY_FORCES.md`](./README_TETHERED_BODY_FORCES.md)

---

## 📝 Summary Table

| Topic | Best File to Read | Key Insight |
|-------|-------------------|-------------|
| Force physics | `FORCE_CALCULATION_EXPLAINED.md` | Reynolds Transport Theorem |
| Code locations | `CODE_LOCATIONS_REFERENCE.md` | Line 237, 778-783 |
| Visual guide | `FORCE_CALCULATION_VISUAL_SUMMARY.md` | Flowcharts and diagrams |
| Momentum flags | `MOMENTUM_FLAGS_EXPLAINED.md` | Control swimming, not forces |
| Tethered thrust | `README_TETHERED_BODY_FORCES.md` | All flags = 0 |
| Quick start | `README_FORCE_CALCULATION.md` | Overview and verification |
| Power & efficiency | `POWER_AND_EFFICIENCY_CALCULATIONS.md` | η = P_out / P_in |
| Leader/follower | `POWER_AND_EFFICIENCY_CALCULATIONS.md` | Multi-body interactions |

---

## 🎓 Educational Value

These documents explain:
- ✅ Fundamental fluid mechanics (Reynolds Transport Theorem)
- ✅ Computational fluid dynamics (control volume methods)
- ✅ Immersed boundary methods (IB force calculation)
- ✅ Fish swimming hydrodynamics (thrust production)
- ✅ Experimental validation (tethered body measurements)
- ✅ Propulsive efficiency theory (Liu et al., 1996)
- ✅ Power calculations (input vs output power)
- ✅ Multi-body hydrodynamic interactions (leader/follower)

**Use these as teaching materials or references for your research papers!**

---

## 🔗 External References

### IBAMR Source Code
- GitHub: https://github.com/IBAMR/IBAMR
- Your installation: `/home/user/MyExten_IBAMR/IBAMR-0.18.0/`

### Key Papers
1. **Nangia et al. (2017)**: Moving control volume forces (J. Comp. Phys.)
2. **Noca (1997)**: Reynolds Transport Theorem for forces (Caltech thesis)
3. **Akanyeti et al. (2017)**: Experimental thrust measurements
4. **Borazjani & Sotiropoulos (2008)**: Swimming fish simulations

---

## 📧 Questions?

If you have questions:
1. Check the relevant documentation file
2. Search the source code using the line numbers provided
3. Run the verification script to check your data
4. Compare your results to the physics explained

**All the answers are in this documentation!**

---

## 🏁 Final Checklist

Before running your simulation, make sure you:
- [x] Understand what `Drag_CV_strct_id_0` contains
- [x] Know which momentum flags to use
- [x] Understand tethered vs free swimming
- [x] Can verify your force data
- [x] Know where to find code if needed

**You're ready to do great research!**

---

**Last updated:** 2025-12-25
**Total documentation:** 7 comprehensive guides + 1 verification script
**Total lines documented:** ~3,000+ lines of explanation
**Source code coverage:** Complete force calculation and efficiency analysis pipeline

**Happy researching! 🐟🌊**
