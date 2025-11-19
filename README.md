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

