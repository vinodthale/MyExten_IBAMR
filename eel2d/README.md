# 2D Free-Swimming Eel Simulation

This directory contains code for simulating free-swimming eel locomotion in 2D using the Immersed Boundary Method (IB) with constraint-based kinematics.

## Overview

The eel2d simulation demonstrates fluid-structure interaction for a deformable swimming body. The eel propels itself through an incompressible viscous fluid by generating traveling waves along its body axis. The implementation uses IBAMR (Immersed Boundary Adaptive Mesh Refinement) framework to solve the coupled fluid-structure problem.

## Reference

This example is based on the following publication:

> Bhalla et al. "A unified mathematical framework and an adaptive numerical method for fluid-structure interaction with rigid, deforming, and elastic bodies." *J Comput Phys*, 250:446-476 (2013).

## Files

### Source Code
- **IBEELKinematics.h/cpp** - Implements the deformational kinematics for the 2D eel
  - Calculates deformation velocity and updated shape
  - Provides routines for straight swimming and maneuvering modes
  - Supports food tracking scenarios

- **example.cpp** - Main simulation driver
  - Sets up the fluid-structure interaction problem
  - Configures Navier-Stokes solver and IB method
  - Evaluates hydrodynamic forces and torques
  - Manages control volume for free-swimming

### Configuration
- **input2d** - Simulation parameters including:
  - Reynolds number (Re = 5609)
  - Grid refinement settings
  - Solver parameters
  - Boundary conditions
  - Eel kinematics parameters (body shape equations, deformation velocities)

### Geometry
- **eel2d.vertex** - Vertex coordinates defining the eel body geometry

### Analysis
- **eel2d_straightswimmer.m** - MATLAB script for post-processing or analysis

### Build System
- **CMakeLists.txt** - CMake build configuration
- **Makefile.am** - Automake configuration
- **Makefile.in** - Makefile template

## Key Features

- **Free-swimming dynamics**: The eel is not fixed in space but free to move based on hydrodynamic forces
- **Deformable body kinematics**: Traveling wave motion along the body axis
- **Adaptive mesh refinement**: Efficiently resolves flow features around the swimming body
- **Hydrodynamic force evaluation**: Computes drag, lift, and torque on the eel
- **Maneuvering capability**: Optional curved swimming paths and food tracking behaviors
- **Moving control volume**: Tracks the eel as it swims through the domain

## Simulation Parameters

Key parameters from input2d:
- Reynolds number: 5609
- Grid levels: 3 with refinement ratio of 4
- CFL number: 0.3
- Body deformation: Sinusoidal traveling wave with wavelength and amplitude specified in body shape equation

## Usage

Compile and run the simulation using IBAMR build system. Refer to IBAMR documentation for installation and compilation instructions.

```bash
# After building with CMake or Automake
./example input2d
```

## Output

The simulation produces:
- Visualization files (VisIt/Silo format) showing velocity, pressure, and vorticity fields
- Time history of hydrodynamic forces and torques
- Eel position and velocity data
- Structure momentum calculations

## License

This code is part of IBAMR and is distributed under the 3-clause BSD license.
Copyright (c) 2014-2025 by the IBAMR developers.
