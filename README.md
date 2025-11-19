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
