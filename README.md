# MyExten_IBAMR

A fully independent, extended version of the IBAMR framework (IBAMR 0.18.0) combined with custom analysis, study notes, and new modules tailored for advanced immersed boundary method research.

This repository contains:

- **IBAMR-0.18.0**  
  A clean imported version of the IBAMR 0.18.0 solver (no fork, no upstream linkage).
  https://github.com/ibamr/IBAMR 

- **IBAMR-understand-ibamr-code**  
  My structured notes, experiments, and exploratory modifications used while studying the IBAMR codebase.  
  Includes diagrams, simplified examples, and C++ test utilities.

---

## 📌 Project Goals

This project aims to:

1. Build a completely standalone IBAMR environment for custom research and simulation development.
2. Add new numerical methods, force models, and multi-structure interaction features.
3. Perform controlled code exploration without modifying the upstream IBAMR repository.
4. Integrate advanced physics modules such as:
   - Custom force functions  
   - Odor dynamics  
   - Phase change / evaporation  
   - Multi-body fluid–structure coupling  
   - Fish-body flow dynamics (ellipsoid geometry)

---

## 📁 Repository Structure

```
MyExten_IBAMR/
├── IBAMR-0.18.0/                   # Clean IBAMR 0.18.0 import
│   ├── src/                        # Core IBAMR source code
│   ├── ibtk/                       # Immersed Boundary Toolkit
│   ├── examples/                   # Official IBAMR examples
│   ├── tests/                      # Test suites
│   ├── doc/                        # Documentation
│   └── CMakeLists.txt              # Build configuration
│
├── IBAMR-understand-ibamr-code/    # Custom extensions and research
│   ├── vinod/                      # Custom modules and experiments
│   │   ├── src/                    # Extended source code
│   │   ├── include/                # Custom headers
│   │   ├── examples/               # Custom examples & test cases
│   │   ├── docs/                   # Research notes & diagrams
│   │   ├── INTEGRATION_GUIDE.md    # Integration documentation
│   │   └── LIBRARY_README.md       # Library documentation
│   ├── src/                        # Modified IBAMR source
│   ├── ibtk/                       # Modified IBTK
│   ├── examples/                   # Extended examples
│   └── tests/                      # Additional tests
│
├── docs/                           # Force calculation & data analysis documentation
│   ├── 00_DOCUMENTATION_INDEX.md   # Master documentation index
│   ├── DATA_FILES_COMPLETE_GUIDE.md # Column-by-column data file descriptions
│   ├── FORCE_CALCULATION_EXPLAINED.md # Physics of force calculation
│   ├── README_TETHERED_BODY_FORCES.md # Tethered body simulations
│   ├── MOMENTUM_FLAGS_EXPLAINED.md # Configuration flags explained
│   ├── CODE_LOCATIONS_REFERENCE.md # Source code line numbers
│   └── FORCE_CALCULATION_VISUAL_SUMMARY.md # Visual guide
│
└── README.md                       # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **C++ Compiler**: GCC 7+ or Clang 5+ with C++11 support
- **CMake**: Version 3.12 or higher
- **MPI**: OpenMPI or MPICH
- **SAMRAI**: Version 4.1.0 or compatible
- **PETSc**: Version 3.13+ (optional, recommended)
- **HDF5**: For data output
- **Boost**: C++ libraries (optional)

### Build Instructions

#### Option 1: Using CMake (Recommended)

```bash
# Clone the repository
git clone https://github.com/vinodthale/MyExten_IBAMR.git
cd MyExten_IBAMR

# Build IBAMR-0.18.0 (baseline)
cd IBAMR-0.18.0
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/path/to/install
make -j$(nproc)
make install

# Build IBAMR-understand-ibamr-code (extended version)
cd ../../IBAMR-understand-ibamr-code
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/path/to/install
make -j$(nproc)
make install
```

#### Option 2: Using Autotools

```bash
cd IBAMR-0.18.0
./configure --prefix=/path/to/install
make -j$(nproc)
make install
```

---

## 🔧 CI/CD Pipeline

This repository includes automated GitHub Actions CI/CD workflows for continuous integration and testing.

### Automated Build Process

The CI pipeline automatically builds and tests:
- PETSc 3.17.5 (with caching)
- IBSAMRAI2 (custom build with automated fixes)
- IBAMR 0.18.0
- IBAMR Validation Framework
- IBAMR Understanding Code modules
- ScalarTransport Test Suite

### IBSAMRAI2 Build Fix

**Important**: The CI workflow includes an automatic fix for a missing include in IBSAMRAI2's `HDFDatabaseFactory.C` file. This fix:

- Clones fresh IBSAMRAI2 source on every run
- Applies a complete file replacement to add the missing `#include "tbox/HDFDatabase.h"`
- Verifies the fix with full before/after logging
- Uses cache key `final-v1` for optimized builds

**Build Status**: See [GitHub Actions](https://github.com/vinodthale/MyExten_IBAMR/actions)

### Running CI Locally

To trigger the CI workflow:

```bash
# Option 1: Using GitHub CLI
gh workflow run ci-ibamr.yml --ref main

# Option 2: Make an empty commit
git commit --allow-empty -m "Trigger CI"
git push origin main
```

### Cache Management

The CI uses GitHub Actions cache to speed up builds:
- PETSc cache: ~10-15 minutes saved
- IBSAMRAI2 build cache: ~10-20 minutes saved
- IBAMR/test suite caches: ~5-10 minutes saved per component

To clear caches (if needed):
1. Go to: https://github.com/vinodthale/MyExten_IBAMR/actions/caches
2. Delete specific caches or clear all

---

## 🧪 Running Examples

### Basic IBAMR Example

```bash
cd IBAMR-0.18.0/examples/IBLevelSet/ex0
mpirun -np 4 ./main2d input2d
```

### Custom Extended Example

```bash
cd IBAMR-understand-ibamr-code/vinod/examples
# Follow specific example README for build/run instructions
```

---

## 📚 Documentation

### IBAMR Force Calculation & Data Analysis

**Complete documentation for understanding IBAMR force calculations and output files:**

📖 **[START HERE: Documentation Index](docs/00_DOCUMENTATION_INDEX.md)**

**Key Documentation Files:**
- **[Data Files Guide](docs/DATA_FILES_COMPLETE_GUIDE.md)** - Complete column-by-column descriptions for FREE SWIMMING vs TETHERED cases
- **[Force Calculation Physics](docs/FORCE_CALCULATION_EXPLAINED.md)** - How IBAMR computes forces (Reynolds Transport Theorem)
- **[Tethered Body Forces](docs/README_TETHERED_BODY_FORCES.md)** - Thrust measurement on swimming bodies
- **[Momentum Flags Explained](docs/MOMENTUM_FLAGS_EXPLAINED.md)** - What calculate_translational/rotational_momentum do
- **[Code Locations](docs/CODE_LOCATIONS_REFERENCE.md)** - Exact line numbers in IBAMR source
- **[Visual Summary](docs/FORCE_CALCULATION_VISUAL_SUMMARY.md)** - Flowcharts and diagrams
- **[Verification Script](docs/verify_force_files.py)** - Python tool to verify force output files

### IBAMR Official Documentation

- **IBAMR Official Docs**: [ibamr.github.io](https://ibamr.github.io)
- **Custom Integration Guide**: `IBAMR-understand-ibamr-code/vinod/INTEGRATION_GUIDE.md`
- **Library Documentation**: `IBAMR-understand-ibamr-code/vinod/LIBRARY_README.md`
- **API Reference**: Build with Doxygen from `doc/` directories

---

## 🔬 Research Features

This extended version includes:

- **Custom Force Models**: Advanced force computation for fluid-structure interaction
- **Odor Dynamics Module**: Scalar transport with source terms
- **Phase Change Modeling**: Evaporation and multi-phase flows
- **Multi-body Coupling**: Enhanced support for multiple immersed structures
- **Fish Hydrodynamics**: Ellipsoid body geometry with undulatory swimming
- **Analysis Tools**: Post-processing utilities and visualization scripts

See `IBAMR-understand-ibamr-code/vinod/docs/` for detailed module documentation.

---

## 🤝 Contributing

This is a personal research repository. For contributions to upstream IBAMR:
- Visit: [github.com/ibamr/IBAMR](https://github.com/ibamr/IBAMR)
- See: `IBAMR-0.18.0/CONTRIBUTING.md`

---

## 📄 License

- **IBAMR 0.18.0**: Licensed under LGPL-2.1 (see `IBAMR-0.18.0/COPYRIGHT`)
- **Custom Extensions**: Research code, consult author for usage terms

---

## 🙏 Acknowledgments

- **IBAMR Development Team**: For the excellent immersed boundary framework
- **SAMRAI Team** (LLNL): For structured AMR infrastructure
- **PETSc Team** (ANL): For scalable solvers

---

## 📧 Contact

For questions about custom extensions or research collaboration:
- Repository: [github.com/vinodthale/MyExten_IBAMR](https://github.com/vinodthale/MyExten_IBAMR)
- Issues: Use GitHub Issues for bug reports and feature requests

---

## 🔖 Version Information

- **IBAMR Base Version**: 0.18.0
- **Repository Created**: 2025
- **Status**: Active Development
