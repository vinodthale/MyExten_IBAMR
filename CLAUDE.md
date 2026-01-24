# CLAUDE.md - AI Assistant Guide for MyExten_IBAMR

**Last Updated:** 2026-01-24
**Repository:** MyExten_IBAMR
**Purpose:** Extended IBAMR framework for fluid-structure interaction research

---

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Codebase Structure](#codebase-structure)
3. [Development Environment](#development-environment)
4. [Build Systems](#build-systems)
5. [Testing Framework](#testing-framework)
6. [Key Conventions](#key-conventions)
7. [Common Workflows](#common-workflows)
8. [Documentation Resources](#documentation-resources)
9. [AI Assistant Guidelines](#ai-assistant-guidelines)

---

## Repository Overview

### Purpose

MyExten_IBAMR is a research-focused extension of the IBAMR (Immersed Boundary Adaptive Mesh Refinement) framework for simulating fluid-structure interaction, particularly focused on:

- Multi-body swimming dynamics
- Scalar transport (odor plume dispersion)
- Hydrodynamic force analysis
- Propulsive efficiency calculations

### Key Features

- **Baseline IBAMR 0.18.0**: Clean reference implementation
- **Custom Extensions**: Advanced research modules for multi-body simulations
- **Comprehensive Testing**: 17 validation tests for scalar transport
- **Force Calculation Documentation**: Detailed physics and code analysis
- **CI/CD Pipeline**: Automated builds with GitHub Actions

### Repository Statistics

- **Total Size:** ~400 MB
- **Source Files:** 1,708 C++ files, 1,720 headers
- **Languages:** C++ (primary), MATLAB, Python, Shell
- **Documentation:** 243 markdown files
- **Tests:** 17 comprehensive validation tests + 628 baseline configs

---

## Codebase Structure

### Top-Level Directory Layout

```
MyExten_IBAMR/
├── IBAMR-0.18.0/                      # Clean IBAMR 0.18.0 baseline (136 MB)
│   ├── src/                           # Core IBAMR source code
│   │   ├── IB/                        # Immersed boundary method
│   │   ├── IBFE/                      # Finite element variant
│   │   ├── adv_diff/                  # Advection-diffusion solvers
│   │   └── navier_stokes/             # Fluid solvers
│   ├── ibtk/                          # Immersed Boundary Toolkit
│   ├── examples/                      # Official IBAMR examples (67 MB)
│   ├── tests/                         # Baseline test suite (628 configs)
│   ├── doc/                           # API documentation
│   └── CMakeLists.txt                 # Master build file (55 KB)
│
├── IBAMR-understand-ibamr-code/       # Custom research extensions (124 MB)
│   ├── vinod/                         # Custom research modules
│   │   ├── include/vinod/             # Custom headers
│   │   │   └── forces/                # MultiStructureForceTracker
│   │   ├── src/                       # Custom implementations
│   │   ├── examples/                  # 10 advanced examples
│   │   │   ├── Four_fish_school/      # Multi-body swimming
│   │   │   ├── EelBAMRvinod/          # Eel kinematics
│   │   │   ├── Naca0012carangiform/   # Airfoil dynamics
│   │   │   └── Zhang_2018/            # Literature validation
│   │   ├── docs/                      # Research notes
│   │   ├── config/                    # Configuration templates
│   │   ├── cmake/                     # CMake helpers
│   │   ├── scripts/                   # Automation scripts
│   │   ├── LIBRARY_README.md          # Reusable components guide
│   │   └── INTEGRATION_GUIDE.md       # Integration documentation
│   ├── src/, ibtk/, examples/, tests/ # Modified IBAMR copies
│   └── CMakeLists.txt                 # Custom build configuration
│
├── ScalarTransport_TestSuite_Standalone/  # Validation framework (691 KB)
│   ├── Test01_SmokeTest/              # Basic functionality
│   ├── Test02_Diffusion_Analytic/     # Diffusion validation
│   ├── Test03_Advection_Analytic/     # Advection validation
│   ├── Test04_MMS/                    # Manufactured solutions
│   ├── Test05_Discontinuous/          # Stability test
│   ├── Test06_MassConservation/       # Conservation properties
│   ├── Test07_BCs/                    # Boundary conditions
│   ├── Test08_SphereSource/           # Lei et al. validation
│   ├── Test09_HighSc/                 # High Schmidt number
│   ├── Test10_MovingIB/               # Moving boundaries
│   ├── Test11_AMR/                    # Adaptive refinement
│   ├── Test12_TimeStep/               # Time stepping
│   ├── Test13_LongRun/                # Long-term stability
│   ├── Test14_Benchmarks/             # Literature comparison
│   ├── Test15_RotatingCylinder/       # Yan & Zu 2008
│   ├── Test16_3DSphere/               # Richter & Nikrityuk 2012
│   ├── Test17_PitchPlunge/            # Lei et al. 2021 full case
│   └── IBAMR_Validation_Framework/    # Python analysis tools
│       └── validation_framework/      # Analysis modules
│
├── docs/                              # Force calculation documentation (319 KB)
│   ├── 00_DOCUMENTATION_INDEX.md      # Master documentation index
│   ├── DATA_FILES_COMPLETE_GUIDE.md   # Output file format reference (34 KB)
│   ├── FORCE_CALCULATION_EXPLAINED.md # Reynolds Transport Theorem derivation
│   ├── CODE_LOCATIONS_REFERENCE.md    # Source code line numbers
│   ├── MOMENTUM_FLAGS_EXPLAINED.md    # Configuration flags guide
│   ├── README_TETHERED_BODY_FORCES.md # Thrust measurement guide
│   ├── POWER_AND_EFFICIENCY_CALCULATIONS.md # Efficiency analysis (26 KB)
│   ├── FORCE_CALCULATION_VISUAL_SUMMARY.md  # Diagrams and flowcharts
│   ├── verify_force_files.py         # Python validation script (5.9 KB)
│   └── output_files/                  # Individual file documentation
│
├── eel2d/                             # 2D eel swimming example (164 KB)
│   ├── IBEELKinematics.h/cpp          # Custom kinematics implementation
│   ├── eel2d.vertex                   # Geometry file
│   ├── input2d                        # Simulation parameters
│   └── README.md                      # Example documentation
│
├── patches/                           # Dependency patches
├── .github/workflows/ci-ibamr.yml     # CI/CD pipeline (218 lines)
├── DATA_FILE_DESCRIPTIONS.txt         # Data structure documentation (16 KB)
├── README.md                          # Main project documentation (8.9 KB)
└── CLAUDE.md                          # This file
```

### Key Source Files

**Core IBAMR Components:**
- `IBAMR-0.18.0/src/IB/IBMethod.cpp` (84 KB) - Main IB method implementation
- `IBAMR-0.18.0/src/IB/IBFEMethod.cpp` (150 KB) - Finite element IB variant
- `IBAMR-0.18.0/src/IB/IBHydrodynamicForceEvaluator.cpp` (66 KB) - Force computation
- `IBAMR-0.18.0/src/navier_stokes/INSStaggeredHierarchyIntegrator.cpp` (126 KB) - NS solver

**Custom Extensions:**
- `IBAMR-understand-ibamr-code/vinod/include/vinod/forces/MultiStructureForceTracker.h` - Multi-body force tracking
- `IBAMR-understand-ibamr-code/vinod/src/CustomForceFunction.h/cpp` - Custom force application
- `eel2d/IBEELKinematics.h/cpp` - Eel swimming kinematics

---

## Development Environment

### Prerequisites

**Required Dependencies:**
- **C++ Compiler:** GCC 7+ or Clang 5+ with C++17 support
- **CMake:** Version 3.15.0 or higher
- **MPI:** OpenMPI or MPICH
- **PETSc:** Version 3.17.5 (built with hypre, metis, superlu)
- **SAMRAI:** IBSAMRAI2 (custom build with HDF5 bug fix)
- **HDF5:** For data I/O
- **LAPACK/BLAS:** Linear algebra libraries

**Optional Dependencies:**
- **Boost:** C++ libraries
- **Eigen3:** Linear algebra templates
- **VisIt/ParaView:** Visualization
- **Python 3:** For analysis tools (numpy, scipy, matplotlib, pandas)
- **MATLAB:** For geometry generation scripts

### Environment Variables

```bash
# Required
export PETSC_DIR=/path/to/petsc
export PETSC_ARCH=arch-linux-c-opt
export SAMRAI2_INSTALL=/path/to/IBSAMRAI2-install
export IBAMR_ROOT=/path/to/ibamr/install

# Optional (if not in standard locations)
export HDF5_ROOT=/path/to/hdf5
export BOOST_ROOT=/path/to/boost
export EIGEN3_ROOT=/path/to/eigen3
```

### C++ Standard

- **Required:** C++17
- **Declared in CMake:** `set(CMAKE_CXX_STANDARD 17)`
- **CMake enforcement:** `set(CMAKE_CXX_STANDARD_REQUIRED ON)`

---

## Build Systems

### CMake (Primary Build System)

**Configuration Files:**
- Root: `/home/user/MyExten_IBAMR/IBAMR-0.18.0/CMakeLists.txt` (55 KB)
- 293+ CMakeLists.txt files throughout repository

**Minimum CMake Version:** 3.15.0

**Build Instructions:**

```bash
# Build baseline IBAMR 0.18.0
cd IBAMR-0.18.0
mkdir build && cd build
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/path/to/install \
  -DPETSC_DIR=$PETSC_DIR \
  -DPETSC_ARCH=$PETSC_ARCH
make -j$(nproc)
make install

# Build custom extensions
cd ../../IBAMR-understand-ibamr-code
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/path/to/install
make -j$(nproc)
make install

# Build validation framework
cd ../../ScalarTransport_TestSuite_Standalone
mkdir build && cd build
cmake ..
make -j$(nproc)
```

**Key CMake Options:**
- `CMAKE_BUILD_TYPE`: Release, Debug, RelWithDebInfo
- `BUILD_EXAMPLES`: ON/OFF (default: ON)
- `IBAMR_ENABLE_TESTING`: ON/OFF (default: ON)
- `CMAKE_CXX_STANDARD`: 17 (mandatory)

### Autotools (Legacy Build System)

**Configuration Files:**
- `configure.ac` (14 KB)
- `configure` (1.5 MB generated script)
- 122 Makefile.am files

**Build Instructions:**

```bash
cd IBAMR-0.18.0
./configure --prefix=/path/to/install
make -j$(nproc)
make install
```

### CI/CD Build Pipeline

**File:** `.github/workflows/ci-ibamr.yml` (218 lines)

**Trigger Conditions:**
- Push to main branch
- Pull requests to main branch

**Build Sequence:**
1. Install system dependencies (25 packages)
2. Cache/build PETSc 3.17.5 (~10-15 min saved with cache)
3. Clone IBSAMRAI2 and apply HDFDatabase.h bug fix
4. Build SAMRAI2 with HDF5 support (~10-20 min saved with cache)
5. Build IBAMR 0.18.0
6. Build Validation Framework
7. Build custom extensions
8. Build test suite
9. Verify MPI functionality
10. Upload build artifacts

**Total Runtime:** ~90 minutes (with caching optimization)

**Critical Bug Fix:**
The CI automatically patches IBSAMRAI2's `HDFDatabaseFactory.C` to add missing `#include "tbox/HDFDatabase.h"` header.

**Cache Management:**
- Cache keys: `petsc-src-3.17.5`, `petsc-build-3.17.5`, `ibsamrai2-v8`
- Clear caches at: https://github.com/vinodthale/MyExten_IBAMR/actions/caches

---

## Testing Framework

### Test Organization

**Three Test Tiers:**

1. **Baseline IBAMR Tests:** `/home/user/MyExten_IBAMR/IBAMR-0.18.0/tests/`
   - 25 test categories
   - 628 input configuration files
   - Coverage: IB, IBFE, CIB, level set, advection-diffusion, Navier-Stokes

2. **Scalar Transport Validation Suite:** `/home/user/MyExten_IBAMR/ScalarTransport_TestSuite_Standalone/`
   - 17 comprehensive validation tests
   - C++ with Python orchestration
   - Automated test discovery and execution

3. **Custom Example Tests:** Embedded in example directories
   - Four_fish_school IBAMR_CPP_Tests
   - Individual example validation

### Validation Test Suite

**Test Categories:**

**Tier 1: Basic Verification (Tests 1-6)**
| Test | Purpose | Pass Criteria |
|------|---------|---------------|
| Test01_SmokeTest | Infrastructure check | No crashes, no NaNs |
| Test02_Diffusion_Analytic | Gaussian diffusion | L2 convergence rate ≈ 2.0 |
| Test03_Advection_Analytic | Profile advection | L2 error < tolerance |
| Test04_MMS | Manufactured solutions | Convergence rate ≈ 2.0 |
| Test05_Discontinuous | Top-hat stability | No oscillations/negatives |
| Test06_MassConservation | Mass budget | Relative drift < 1e-10 |

**Tier 2: Physical Validation (Tests 7-10)**
| Test | Purpose | Pass Criteria |
|------|---------|---------------|
| Test07_BCs | Boundary conditions | BC error ≤ 1e-6 |
| Test08_SphereSource | Lei et al. comparison | Match ±10% |
| Test09_HighSc | High Schmidt (Sc=100-1000) | Stable, physical |
| Test10_MovingIB | IB-scalar coupling | No instabilities |

**Tier 3: Production Validation (Tests 11-14)**
| Test | Purpose | Pass Criteria |
|------|---------|---------------|
| Test11_AMR | Refinement artifacts | Consistent results |
| Test12_TimeStep | Temporal convergence | Convergence rate ≈ 2.0 |
| Test13_LongRun | Long-term stability | No drift (T=100+) |
| Test14_Benchmarks | Literature comparison | Match Lei/Kamran data |

**Tier 4: Literature Validation (Tests 15-17)**
| Test | Reference | Pass Criteria |
|------|-----------|---------------|
| Test15_RotatingCylinder | Yan & Zu 2008 | Streamlines match Figure 2 |
| Test16_3DSphere | Richter & Nikrityuk 2012 | Nu within ±15% |
| Test17_PitchPlunge | Lei et al. 2021 full case | PDF shape, vortex street |

### Running Tests

**Individual Test:**
```bash
cd ScalarTransport_TestSuite_Standalone/Test01_SmokeTest
mkdir build && cd build
cmake ..
make
./test01_smoke ../input2d
```

**All Tests (Sequential):**
```bash
cd ScalarTransport_TestSuite_Standalone
./run_all_tests.sh
```

**With MPI:**
```bash
mpirun -np 4 ./test01_smoke input2d
```

**Python Test Runner:**
```bash
cd ScalarTransport_TestSuite_Standalone/IBAMR_Validation_Framework
python3 run_all_tests.py --num-procs 4
python3 analyze_results.py
```

### Test Output

Each test produces:
- Console output with real-time progress
- VTK files (VisIt/ParaView compatible)
- HDF5 checkpoint files
- Error metrics (L2/Linf norms)
- Pass/fail verdict

**Typical Output Structure:**
```
Test01_SmokeTest/
├── viz_test01/              # Visualization data
├── restart_test01/          # Restart files
├── test01_output.log        # Simulation log
└── test01_results.txt       # Error metrics
```

---

## Key Conventions

### Code Style

**C++ Conventions:**
- **Style guide:** Follow IBAMR conventions
- **Indentation:** Run `make indent` (uses scripts in `IBAMR-0.18.0/scripts/formatting/`)
- **Formatting tools:** clang-format, indent
- **Header guards:** `#ifndef INCLUDED_ClassName`, `#define INCLUDED_ClassName`
- **Namespaces:** IBAMR, IBTK, SAMRAI, custom namespace VINOD
- **Smart pointers:** SAMRAI `Pointer<T>` for memory management

**File Naming:**
- Headers: `.h` (C++ headers)
- Implementation: `.cpp`
- Input files: `.input`, `.input2d`, `.input3d`
- Geometry: `.vertex`, `.spring`, `.beam`
- MATLAB: `.m`
- Python: `.py`

### Naming Conventions

**Classes:**
- PascalCase: `IBMethod`, `MultiStructureForceTracker`, `INSStaggeredHierarchyIntegrator`

**Functions/Methods:**
- camelCase: `computeHydrodynamicForce()`, `registerStructure()`, `updateControlVolume()`

**Variables:**
- Snake_case for members: `d_num_structures`, `d_force_evaluators`
- camelCase for locals: `patchHierarchy`, `velocityIdx`

**Constants:**
- ALL_CAPS: `NDIM`, `MAX_LEVELS`

**File Prefixes:**
- `IB`: Immersed Boundary classes
- `INS`: Incompressible Navier-Stokes
- `Adv`: Advection
- `Diff`: Diffusion

### Input File Conventions

**Format:** Key-value pairs

**Common Parameters:**
```
// Grid parameters
L                    = 1.0              // Domain size
MAX_LEVELS           = 3                // AMR levels
REF_RATIO            = 4                // Refinement ratio
N                    = 64               // Base grid resolution

// Physical parameters
MU                   = 0.001            // Dynamic viscosity
RHO                  = 1.0              // Fluid density
KAPPA                = 0.001            // Diffusivity

// Time stepping
START_TIME           = 0.0
END_TIME             = 1.0
MAX_INTEGRATOR_STEPS = 10000
CFL_MAX              = 0.3

// IB parameters
MFAC                 = 2.0              // Marker spacing factor
DX                   = L/N              // Grid spacing
```

**Naming Patterns:**
- Database names: `InitHydroForceBox_0`, `IBStandardInitializer`
- Structure IDs: `_0`, `_1`, `_2` suffix
- Output prefixes: `Drag_CV_strct_id_`, `Torque_CV_strct_id_`

### Git Workflow

**Branch Naming:**
- Feature branches: `claude/feature-description-<session-id>`
- Current development: `claude/claude-md-mks9mqrob3ompk70-5na1h`

**Commit Messages:**
- Concise (1-2 sentences)
- Focus on "why" rather than "what"
- Reference issue/PR numbers when applicable

**Git Operations:**
```bash
# ALWAYS use -u flag for push
git push -u origin <branch-name>

# Branch must start with 'claude/' and end with session ID
# Otherwise push fails with 403 error

# Fetch specific branches
git fetch origin <branch-name>

# Pull with explicit branch
git pull origin <branch-name>
```

---

## Common Workflows

### 1. Adding a New Multi-Body Simulation

**Use MultiStructureForceTracker for cleaner code:**

```cpp
#include "vinod/forces/MultiStructureForceTracker.h"

// In main.cpp
Pointer<VINOD::MultiStructureForceTracker> force_tracker =
    new VINOD::MultiStructureForceTracker("force_tracker", rho, mu, start_time);

// Register from input database
force_tracker->registerStructuresFromDatabase(
    input_db, "InitHydroForceBox", num_structures, patch_hierarchy);

// Set torque origins
std::vector<std::vector<double>> structure_COM = ib_method->getCurrentStructureCOM();
force_tracker->setTorqueOriginsFromCOM(structure_COM);

// In time-stepping loop
force_tracker->updateAllControlVolumes(COM_velocities, dt, patch_hierarchy, DX);
force_tracker->computeAllForces(u_idx, p_idx, patch_hierarchy, dt,
                                velocity_bc, pressure_bc);
```

**Input file configuration:**
```
// For N structures, add N control volume configs
InitHydroForceBox_0 {
    lower = -0.5, -0.5
    upper =  0.5,  0.5
}

InitHydroForceBox_1 {
    lower = 0.5, -0.5
    upper = 1.5,  0.5
}
// ... up to N-1
```

**Benefits:**
- Eliminates 200+ lines of duplicated code
- Automatic validation of input configurations
- Scales easily to any number of structures

### 2. Understanding Force Output Files

**Force files are created at:** `IBHydrodynamicForceEvaluator.cpp:237`

**File naming pattern:**
```
Drag_CV_strct_id_0      # Force on structure 0
Torque_CV_strct_id_0    # Torque on structure 0
Drag_CV_strct_id_1      # Force on structure 1 (if multiple)
```

**File format (4 columns):**
```
time        Fx          Fy          Fz
0.000000    0.0000000   0.0000000   0.0000000
0.001000    0.1234567   0.0123456   0.0012345
```

**Verification:**
```bash
cd /path/to/simulation/output
python3 /home/user/MyExten_IBAMR/docs/verify_force_files.py
```

**Documentation:** See `/home/user/MyExten_IBAMR/docs/00_DOCUMENTATION_INDEX.md`

### 3. Configuring Swimming Simulations

**Free Swimming (Fish can move):**
```
calculate_translational_momentum = 1,1,0    // Can swim in x,y
calculate_rotational_momentum    = 0,0,1    // Can rotate around z
```

**Tethered (Thrust Measurement):**
```
calculate_translational_momentum = 0,0,0    // Cannot translate
calculate_rotational_momentum    = 0,0,0    // Cannot rotate
```
- Body deforms (swims) but stays in place
- Force output = net thrust production
- Matches experimental force balance measurements

**Documentation:**
- `/home/user/MyExten_IBAMR/docs/MOMENTUM_FLAGS_EXPLAINED.md`
- `/home/user/MyExten_IBAMR/docs/README_TETHERED_BODY_FORCES.md`

### 4. Computing Propulsive Efficiency

**Efficiency equation (Liu et al., 1996):**
```
η = P_out / P_in = C_Tm / ∫ c_L(s,t) V_body(s,t) ds
```

**Steps:**
1. Run simulation in tethered mode
2. Extract thrust from `Drag_CV_strct_id_N` files
3. Compute output power: `P_out = Thrust × U_∞`
4. Extract per-marker forces and velocities from IBAMR
5. Compute input power: `P_in = ∫ F_marker · V_marker`
6. Calculate efficiency: `η = P_out / P_in`

**Documentation:** `/home/user/MyExten_IBAMR/docs/POWER_AND_EFFICIENCY_CALCULATIONS.md`

### 5. Running Validation Tests

**Quick start:**
```bash
cd ScalarTransport_TestSuite_Standalone/Test01_SmokeTest
mkdir build && cd build
cmake ..
make
./test01_smoke ../input2d
```

**Expected output:**
```
Test01_SmokeTest
=================
Running basic infrastructure check...
[timestep progress...]
Final check: No NaNs detected
Final check: No negative concentrations
TEST PASSED ✓
```

**Python analysis:**
```bash
cd ../IBAMR_Validation_Framework
python3 run_all_tests.py
python3 analyze_results.py
```

### 6. Visualizing Results

**With VisIt:**
```bash
visit viz_<name>/dumps.visit
```

**With ParaView:**
```bash
paraview viz_<name>/*.vtu
```

**Output files:**
- Velocity field: `visit*.*.vtk`
- Pressure field: `visit*.*.vtk`
- Scalar concentration: `visit*.*.vtk`
- Lagrangian markers: `lag_data.*.vtu`

### 7. Creating New Examples

**Template structure:**
```
new_example/
├── main.cpp                 # Main application
├── input2d                  # 2D parameters
├── input3d                  # 3D parameters (if needed)
├── CMakeLists.txt           # Build configuration
├── README.md                # Documentation
├── geometry.vertex          # IB geometry
└── analyze_results.m        # MATLAB analysis (optional)
```

**Minimal CMakeLists.txt:**
```cmake
cmake_minimum_required(VERSION 3.15)
project(new_example)

find_package(IBAMR REQUIRED)

add_executable(main2d main.cpp)
target_link_libraries(main2d PRIVATE IBAMR::IBAMR)
```

**Reference examples:**
- Simple: `/home/user/MyExten_IBAMR/IBAMR-understand-ibamr-code/vinod/examples/simple-cmake/`
- Advanced: `/home/user/MyExten_IBAMR/eel2d/`

---

## Documentation Resources

### Primary Documentation

**Force Calculation Physics:**
- **Index:** `/home/user/MyExten_IBAMR/docs/00_DOCUMENTATION_INDEX.md`
- **Physics:** `/home/user/MyExten_IBAMR/docs/FORCE_CALCULATION_EXPLAINED.md`
  - Reynolds Transport Theorem derivation
  - Control volume method explanation
  - Pressure, viscous, and momentum flux components
- **Code:** `/home/user/MyExten_IBAMR/docs/CODE_LOCATIONS_REFERENCE.md`
  - Exact line numbers in source
  - Code snippets with explanations
- **Visual:** `/home/user/MyExten_IBAMR/docs/FORCE_CALCULATION_VISUAL_SUMMARY.md`
  - Flowcharts and diagrams
  - Timeline of computation

**Output Files:**
- **Master guide:** `/home/user/MyExten_IBAMR/docs/DATA_FILES_COMPLETE_GUIDE.md` (34 KB)
- **Individual files:** `/home/user/MyExten_IBAMR/docs/output_files/`
  - `Drag_CV_strct_id.md` - Hydrodynamic force
  - `Torque_CV_strct_id.md` - Hydrodynamic torque
  - `COM_coordinates.md` - Center of mass position
  - `Trans_vel_struct.md` - Translational velocity
  - `Rot_vel_struct.md` - Rotational velocity
  - `Power_spent_struct.md` - Mechanical power
  - `EULERIAN_MOMENTUM.md` - Fluid momentum
  - And more...

**Custom Library:**
- `/home/user/MyExten_IBAMR/IBAMR-understand-ibamr-code/vinod/LIBRARY_README.md`
  - MultiStructureForceTracker API
  - CustomForceFunction usage
  - Integration examples

**Validation Framework:**
- `/home/user/MyExten_IBAMR/ScalarTransport_TestSuite_Standalone/README.md`
- `/home/user/MyExten_IBAMR/ScalarTransport_TestSuite_Standalone/IBAMR_Validation_Framework/VALIDATION_FRAMEWORK_README.md`

**Project Overview:**
- `/home/user/MyExten_IBAMR/README.md` - Main repository documentation
- Build status, CI/CD, quick start, dependencies

### IBAMR Official Resources

- **Website:** https://ibamr.github.io/
- **Documentation:** https://ibamr.github.io/docs/
- **API Reference:** https://ibamr.github.io/api/
- **GitHub:** https://github.com/IBAMR/IBAMR
- **User Group:** ibamr-users@googlegroups.com

### Key Papers

1. **Griffith et al. (2007)**: IBAMR method paper
   - J. Comp. Phys. 223:10-49
2. **Nangia et al. (2017)**: Moving control volume forces
   - J. Comp. Phys.
3. **Lei et al. (2021)**: Odor plume navigation
   - Tests 8, 14, 15-17 reference
4. **Yan & Zu (2008)**: Rotating cylinder validation
   - Test 15 reference
5. **Richter & Nikrityuk (2012)**: 3D sphere/cube
   - Test 16 reference

### File Location Quick Reference

| Documentation | Absolute Path |
|--------------|---------------|
| Force calculation index | `/home/user/MyExten_IBAMR/docs/00_DOCUMENTATION_INDEX.md` |
| Data file guide | `/home/user/MyExten_IBAMR/docs/DATA_FILES_COMPLETE_GUIDE.md` |
| Force physics | `/home/user/MyExten_IBAMR/docs/FORCE_CALCULATION_EXPLAINED.md` |
| Code locations | `/home/user/MyExten_IBAMR/docs/CODE_LOCATIONS_REFERENCE.md` |
| Momentum flags | `/home/user/MyExten_IBAMR/docs/MOMENTUM_FLAGS_EXPLAINED.md` |
| Tethered forces | `/home/user/MyExten_IBAMR/docs/README_TETHERED_BODY_FORCES.md` |
| Efficiency | `/home/user/MyExten_IBAMR/docs/POWER_AND_EFFICIENCY_CALCULATIONS.md` |
| Verification script | `/home/user/MyExten_IBAMR/docs/verify_force_files.py` |
| Library README | `/home/user/MyExten_IBAMR/IBAMR-understand-ibamr-code/vinod/LIBRARY_README.md` |
| CI workflow | `/home/user/MyExten_IBAMR/.github/workflows/ci-ibamr.yml` |

---

## AI Assistant Guidelines

### Understanding the Repository

**When asked about repository structure:**
- Reference this CLAUDE.md file
- Point to specific directory paths
- Explain the three-tier organization: baseline → custom → validation

**When asked about force calculations:**
- Start with `/home/user/MyExten_IBAMR/docs/00_DOCUMENTATION_INDEX.md`
- Reference Reynolds Transport Theorem
- Point to code at line 237, 778-783 in `IBHydrodynamicForceEvaluator.cpp`

**When asked about output files:**
- Reference `/home/user/MyExten_IBAMR/docs/DATA_FILES_COMPLETE_GUIDE.md`
- Explain 4-column format: time, Fx, Fy, Fz
- Suggest verification script: `docs/verify_force_files.py`

### Making Code Changes

**Before modifying code:**
1. Read relevant source files using Read tool
2. Check existing documentation in `docs/`
3. Review related examples in `examples/`
4. Understand the physics/algorithm before changing

**When adding new features:**
1. Follow IBAMR naming conventions (see Key Conventions section)
2. Use SAMRAI smart pointers (`Pointer<T>`)
3. Add comprehensive error checking
4. Document in comments and README files
5. Add validation test if significant

**When fixing bugs:**
1. Identify root cause before patching
2. Check if similar code exists elsewhere
3. Verify fix doesn't break other functionality
4. Add test to prevent regression

### Code Style Enforcement

**Always:**
- Use C++17 features where appropriate
- Follow camelCase for methods, PascalCase for classes
- Use SAMRAI `Pointer<T>` for memory management
- Add Doxygen comments for public methods
- Run `make indent` before committing

**Never:**
- Use raw pointers for SAMRAI objects
- Hardcode paths or magic numbers
- Ignore compiler warnings
- Skip error checking on user inputs

### Testing and Validation

**For new simulations:**
1. Start with simple test case (e.g., Test01_SmokeTest pattern)
2. Verify mass conservation
3. Check for NaN/Inf values
4. Compare to analytical solution when available
5. Validate against literature data

**For modifications to existing code:**
1. Run relevant tests from test suite
2. Verify no regression in force calculations
3. Check CI pipeline passes
4. Document any API changes

### Working with Multi-Body Simulations

**Prefer MultiStructureForceTracker:**
```cpp
// GOOD: Use the library
#include "vinod/forces/MultiStructureForceTracker.h"
Pointer<VINOD::MultiStructureForceTracker> tracker =
    new VINOD::MultiStructureForceTracker(...);
tracker->registerStructuresFromDatabase(...);

// BAD: Manual registration for each structure
for (int i = 0; i < num_structures; ++i) {
    Pointer<IBHydrodynamicForceEvaluator> force_eval = new IBHydrodynamicForceEvaluator(...);
    // ... 50 lines of repetitive setup ...
}
```

**Input file validation:**
- Check all required databases exist
- Validate array sizes match num_structures
- Ensure lower < upper for control volumes

### Documentation

**When creating new examples:**
- Always add README.md with:
  - Purpose and physics
  - Build instructions
  - Run instructions
  - Expected output
  - Parameter descriptions
  - References

**When modifying algorithms:**
- Update relevant documentation in `docs/`
- Add comments explaining physics/mathematics
- Include references to papers

**When adding features:**
- Document in library README
- Add usage examples
- Update this CLAUDE.md if significant

### Common Pitfalls to Avoid

**Build Issues:**
- Don't forget to set PETSC_DIR, PETSC_ARCH, SAMRAI2_INSTALL
- Remember IBSAMRAI2 HDF5 bug fix (CI handles automatically)
- Use correct CMake version (≥3.15)

**Runtime Issues:**
- Check CFL condition (CFL_MAX typically 0.3)
- Verify grid resolution sufficient (MFAC = 2.0 typical)
- Ensure time step small enough for stability

**Physics Issues:**
- Distinguish free swimming vs tethered (momentum flags)
- Understand force = 0 at steady state for free swimming
- Remember control volume must contain structure

**Git Issues:**
- Always use `git push -u origin <branch>`
- Branch must start with `claude/` and end with session ID
- Network failures: retry with exponential backoff (2s, 4s, 8s, 16s)

### Helpful Commands

**Search for code:**
```bash
# Find class definition
grep -r "class IBMethod" IBAMR-0.18.0/include/

# Find function implementation
grep -r "computeHydrodynamicForce" IBAMR-0.18.0/src/

# Find all force evaluator instances
grep -r "IBHydrodynamicForceEvaluator" --include="*.cpp"
```

**Build commands:**
```bash
# Clean rebuild
rm -rf build && mkdir build && cd build
cmake .. && make -j$(nproc)

# Parallel build
make -j8

# Verbose build (debug)
make VERBOSE=1
```

**Run simulations:**
```bash
# Serial
./main2d input2d

# Parallel
mpirun -np 4 ./main2d input2d

# With output redirect
mpirun -np 4 ./main2d input2d > output.log 2>&1
```

### Quick Decision Tree

**User asks about forces:**
→ Point to `/home/user/MyExten_IBAMR/docs/00_DOCUMENTATION_INDEX.md`

**User wants to add multiple swimming bodies:**
→ Recommend `MultiStructureForceTracker` from library

**User needs to validate scalar transport:**
→ Direct to test suite in `ScalarTransport_TestSuite_Standalone/`

**User wants to compute efficiency:**
→ Reference `/home/user/MyExten_IBAMR/docs/POWER_AND_EFFICIENCY_CALCULATIONS.md`

**User has build issues:**
→ Check environment variables, CMake version, dependencies

**User has runtime crashes:**
→ Verify input file format, check CFL condition, examine error logs

**User wants to understand codebase:**
→ Start with README.md, then this CLAUDE.md, then specific docs

### Best Practices Summary

1. **Read before writing**: Always read existing code/docs before modifying
2. **Use the library**: Leverage `MultiStructureForceTracker` for multi-body
3. **Validate thoroughly**: Run tests, check conservation, compare to literature
4. **Document extensively**: Update READMEs, add comments, explain physics
5. **Follow conventions**: Naming, style, file organization
6. **Test incrementally**: Start simple, add complexity gradually
7. **Check CI**: Ensure GitHub Actions passes
8. **Commit properly**: Clear messages, focused changes

---

## Appendix: Critical File Locations

### Force Computation Code

**Class Definition:**
```
/home/user/MyExten_IBAMR/IBAMR-0.18.0/include/ibamr/IBHydrodynamicForceEvaluator.h
```

**Implementation:**
```
/home/user/MyExten_IBAMR/IBAMR-0.18.0/src/IB/IBHydrodynamicForceEvaluator.cpp
```

**Key Lines:**
- Line 237: File name creation `"Drag_CV_strct_id_" + strct_id_str`
- Lines 690-696: Pressure force computation
- Lines 698-717: Momentum flux computation
- Lines 719-769: Viscous force computation
- Lines 778-783: Reynolds Transport Theorem application
- Lines 800-801: Force written to file

### Custom Library Files

**MultiStructureForceTracker:**
```
/home/user/MyExten_IBAMR/IBAMR-understand-ibamr-code/vinod/include/vinod/forces/MultiStructureForceTracker.h
/home/user/MyExten_IBAMR/IBAMR-understand-ibamr-code/vinod/src/forces/MultiStructureForceTracker.cpp
```

**CustomForceFunction:**
```
/home/user/MyExten_IBAMR/IBAMR-understand-ibamr-code/vinod/src/CustomForceFunction.h
/home/user/MyExten_IBAMR/IBAMR-understand-ibamr-code/vinod/src/CustomForceFunction.cpp
```

### Example Simulations

**Eel 2D:**
```
/home/user/MyExten_IBAMR/eel2d/
```

**Four Fish School:**
```
/home/user/MyExten_IBAMR/IBAMR-understand-ibamr-code/vinod/examples/Four_fish_school/
```

**Validation Tests:**
```
/home/user/MyExten_IBAMR/ScalarTransport_TestSuite_Standalone/Test01_SmokeTest/
... through Test17_PitchPlunge/
```

---

**This document is maintained for AI assistants (like Claude) to efficiently navigate and work with the MyExten_IBAMR codebase. Keep it updated as the repository evolves.**

**Last Updated:** 2026-01-24
**Version:** 1.0
**Maintained by:** AI assistant interactions with repository
