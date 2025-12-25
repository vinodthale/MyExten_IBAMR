# Quick Reference: Where to Find Force Calculation Code

## File Locations in Your Repository

All files are under: `/home/user/MyExten_IBAMR/IBAMR-0.18.0/`

### Main Force Calculation Class

**Header File:**
```
include/ibamr/IBHydrodynamicForceEvaluator.h
```

**Implementation:**
```
src/IB/IBHydrodynamicForceEvaluator.cpp
```

---

## Critical Code Sections

### 1. File Name Creation

**File:** `src/IB/IBHydrodynamicForceEvaluator.cpp`

**Lines 224-242:**
```cpp
// Set up the streams for printing drag and torque
if (IBTK_MPI::getRank() == 0)
{
    const std::string strct_id_str = std::to_string(strct_id);

    if (from_restart)
    {
        force_obj.drag_CV_stream = new std::ofstream("Drag_CV_strct_id_" + strct_id_str, std::fstream::app);
        force_obj.torque_CV_stream = new std::ofstream("Torque_CV_strct_id_" + strct_id_str, std::fstream::app);
        (force_obj.drag_CV_stream)->precision(10);
        (force_obj.torque_CV_stream)->precision(10);
    }
    else
    {
        force_obj.drag_CV_stream = new std::ofstream("Drag_CV_strct_id_" + strct_id_str, std::fstream::out);
        force_obj.torque_CV_stream = new std::ofstream("Torque_CV_strct_id_" + strct_id_str, std::fstream::out);
        (force_obj.drag_CV_stream)->precision(10);
        (force_obj.torque_CV_stream)->precision(10);
    }
}
```

**What this means:**
- `Drag_CV_strct_id_0` → Drag forces using Control Volume method for structure 0
- `Torque_CV_strct_id_0` → Torques using Control Volume method for structure 0
- Files created in `registerStructure()` function
- Precision set to 10 significant digits

---

### 2. Volume Momentum Integral

**File:** `src/IB/IBHydrodynamicForceEvaluator.cpp`

**Lines 500-618:**
```cpp
// Compute the momentum integral:= (rho * u * dv)
fobj.P_box_new.setZero();

// Loop over control volume
for (int ln = finest_ln; ln >= coarsest_ln; --ln)
{
    Pointer<PatchLevel<NDIM> > level = patch_hierarchy->getPatchLevel(ln);
    Box<NDIM> integration_box(...);

    for (PatchLevel<NDIM>::Iterator p(level); p; p++)
    {
        Pointer<Patch<NDIM> > patch = level->getPatch(p());

        for (int axis = 0; axis < NDIM; ++axis)
        {
            for (Box<NDIM>::Iterator b(SideGeometry<NDIM>::toSideBox(trim_box, axis)); b; b++)
            {
                const double& u_axis = (*u_data)(side_idx);
                const double& vol = (*vol_sc_data)(side_idx);

                // Careful handling of boundary volumes
                dV = (boundary condition) ? 0.5 * vol : vol;

                // Accumulate momentum
                fobj.P_box_new(axis) += d_rho * u_axis * dV;

                // Also compute angular momentum
                fobj.L_box_new += d_rho * r_vec.cross(u_vec) * dV;
            }
        }
    }
}
```

**Physics:** Computes ∫∫∫_CV ρ **u** dV (total momentum in control volume)

---

### 3. Surface Stress Integral - Pressure

**Lines 662-696:**
```cpp
// Integrate over boundary boxes
Pointer<CellData<NDIM, double> > p_data = patch->getPatchData(d_p_idx);
Pointer<SideData<NDIM, double> > u_data = patch->getPatchData(d_u_idx);

for (int axis = 0; axis < NDIM; ++axis)
{
    for (int upperlower = 0; upperlower <= 1; ++upperlower)
    {
        // Get boundary face
        const Box<NDIM>& side_box = bdry_boxes[axis][upperlower];

        // Normal vector (outward from CV)
        IBTK::Vector3d n = IBTK::Vector3d::Zero();
        n(axis) = upperlower ? 1 : -1;

        for (Box<NDIM>::Iterator b(trim_box); b; b++)
        {
            const CellIndex<NDIM>& cell_idx = *b;
            CellIndex<NDIM> cell_nbr_idx = cell_idx;
            cell_nbr_idx(axis) += n(axis);

            SideIndex<NDIM> bdry_idx(...);
            const double& dA = (*face_sc_data)(bdry_idx);

            // Average pressure on face
            IBTK::Vector3d pn = 0.5 * n * ((*p_data)(cell_idx) + (*p_data)(cell_nbr_idx));

            // Pressure force := -p n · dA
            trac += -pn * dA;

            // Pressure torque := r × (-p n) · dA
            torque_trac += r_vec.cross(-pn) * dA;
```

**Physics:** Computes ∫∫_∂CV (-**p I**) · **n** dA (pressure force on CV boundary)

---

### 4. Surface Stress Integral - Momentum Flux

**Lines 698-717:**
```cpp
            // Momentum force := -ρ(u·n)u · dA
            IBTK::Vector3d u = IBTK::Vector3d::Zero();
            for (int d = 0; d < NDIM; ++d)
            {
                if (d == axis)
                {
                    u(d) = (*u_data)(bdry_idx);
                }
                else
                {
                    // Average velocity components
                    u(d) = 0.25 * ((*u_data)(SideIndex<NDIM>(cell_idx, d, SideIndex<NDIM>::Lower)) +
                                   (*u_data)(SideIndex<NDIM>(cell_idx, d, SideIndex<NDIM>::Upper)) +
                                   (*u_data)(SideIndex<NDIM>(cell_nbr_idx, d, SideIndex<NDIM>::Lower)) +
                                   (*u_data)(SideIndex<NDIM>(cell_nbr_idx, d, SideIndex<NDIM>::Upper)));
                }
            }
            trac += -d_rho * n.dot(u) * u * dA;

            // Momentum torque := -ρ(u·n) (r × u) · dA
            torque_trac += -n.dot(u) * d_rho * r_vec.cross(u) * dA;
```

**Physics:** Computes ∫∫_∂CV -ρ(**u**·**n**)**u** dA (convective momentum flux)

---

### 5. Surface Stress Integral - Viscous Stress

**Lines 719-769:**
```cpp
            // Viscous traction force := n · μ(∇u + ∇u^T) · dA
            IBTK::Vector3d viscous_force = IBTK::Vector3d::Zero();
            for (int d = 0; d < NDIM; ++d)
            {
                if (d == axis)
                {
                    // Normal component: 2μ ∂u_axis/∂x_axis
                    viscous_force(axis) =
                        n(axis) * (2.0 * d_mu) / (2.0 * patch_dx[axis]) *
                        ((*u_data)(SideIndex<NDIM>(cell_nbr_idx, axis, ...)) -
                         (*u_data)(SideIndex<NDIM>(cell_idx, axis, ...)));
                }
                else
                {
                    // Tangential components: μ(∂u_axis/∂x_d + ∂u_d/∂x_axis)
                    CellIndex<NDIM> offset(0);
                    offset(d) = 1;

                    viscous_force(d) =
                        d_mu / (2.0 * patch_dx[d]) *
                            ((*u_data)(SideIndex<NDIM>(cell_idx + offset, axis, ...)) -
                             (*u_data)(SideIndex<NDIM>(cell_idx - offset, axis, ...)))
                        +
                        d_mu * n(axis) / (2.0 * patch_dx[axis]) *
                            ((*u_data)(SideIndex<NDIM>(cell_nbr_idx, d, ...)) +
                             (*u_data)(SideIndex<NDIM>(cell_nbr_idx + offset, d, ...)) -
                             (*u_data)(SideIndex<NDIM>(cell_idx, d, ...)) -
                             (*u_data)(SideIndex<NDIM>(cell_idx + offset, d, ...)));
                }
            }
            IBTK::Vector3d n_dot_T = n(axis) * viscous_force;

            trac += n_dot_T * dA;

            // Viscous torque := r × (n · μ(∇u + ∇u^T)) · dA
            torque_trac += r_vec.cross(n_dot_T) * dA;
```

**Physics:** Computes ∫∫_∂CV μ(**∇u** + **∇u**^T) · **n** dA (viscous stress force)

This is the full strain-rate tensor:
```
τ_ij = μ(∂u_i/∂x_j + ∂u_j/∂x_i)
```

---

### 6. Reynolds Transport Theorem Application

**Lines 778-783:**
```cpp
        // Compute hydrodynamic force on the body:
        // F = -∂/∂t(∫∫∫_CV ρu dV) + ∂/∂t(P_body) + ∫∫_∂CV T·n dA

        fobj.F_new = -(fobj.P_box_new - fobj.P_box_current) / dt    // -dP_CV/dt
                   + (fobj.P_new - fobj.P_current) / dt              // +dP_body/dt
                   + trac;                                            // +surface stresses

        // Compute hydrodynamic torque on the body:
        // T = -∂/∂t(∫∫∫_CV ρ(r×u) dV) + ∂/∂t(L_body) + ∫∫_∂CV (r×T)·n dA

        fobj.T_new = -(fobj.L_box_new - fobj.L_box_current) / dt
                   + (fobj.L_new - fobj.L_current) / dt
                   + torque_trac;
```

**Physics:** Direct application of Reynolds Transport Theorem:

**d/dt(∫∫∫_CV ρ**u** dV) = d/dt(P_body) - ∫∫_∂CV **T**·**n** dA**

Rearranged to solve for force:

**F = -d/dt(∫∫∫_CV ρ**u** dV) + d/dt(P_body) + ∫∫_∂CV **T**·**n** dA**

---

### 7. Writing to Files

**Lines 790-820:**
```cpp
void IBHydrodynamicForceEvaluator::postprocessIntegrateData(double current_time, double new_time)
{
    for (auto& hydro_obj : d_hydro_objs)
    {
        IBHydrodynamicForceObject& force_obj = hydro_obj.second;

        // Output drag and torque to stream
        if (IBTK_MPI::getRank() == 0)
        {
            // Write: time  Fx  Fy  Fz
            *force_obj.drag_CV_stream << new_time << '\t'
                                      << force_obj.F_new(0) << '\t'
                                      << force_obj.F_new(1) << '\t'
                                      << force_obj.F_new(2) << std::endl;

            // Write: time  Tx  Ty  Tz
            *force_obj.torque_CV_stream << new_time << '\t'
                                        << force_obj.T_new(0) << '\t'
                                        << force_obj.T_new(1) << '\t'
                                        << force_obj.T_new(2) << std::endl;
        }

        // Update current state for next timestep
        d_current_time = new_time;
        force_obj.box_u_current = force_obj.box_u_new;
        force_obj.box_X_lower_current = force_obj.box_X_lower_new;
        force_obj.box_X_upper_current = force_obj.box_X_upper_new;
        force_obj.box_vol_current = force_obj.box_vol_new;
        force_obj.F_current = force_obj.F_new;
        force_obj.T_current = force_obj.T_new;
        force_obj.P_current = force_obj.P_new;
        force_obj.L_current = force_obj.L_new;
        force_obj.P_box_current = force_obj.P_box_new;
        force_obj.L_box_current = force_obj.L_box_new;
    }
}
```

**What happens:**
1. Only MPI rank 0 writes to files (avoid duplicates in parallel runs)
2. Write format: `time \t Fx \t Fy \t Fz`
3. Update all "current" values ← "new" values for next timestep
4. Files remain open for efficient writing (closed when program exits)

---

## How to Read the Source Code Yourself

### Step 1: Open the header file
```bash
cd /home/user/MyExten_IBAMR/IBAMR-0.18.0
less include/ibamr/IBHydrodynamicForceEvaluator.h
```

Look for:
- Class documentation (lines 78-96)
- Public interface methods (lines 100-301)
- Data structure `IBHydrodynamicForceObject` (lines 118-154)

### Step 2: Open the implementation
```bash
less src/IB/IBHydrodynamicForceEvaluator.cpp
```

Key functions to read:
- `registerStructure()` - lines 115-247 (sets up CV and creates files)
- `computeLaggedMomentumIntegral()` - lines 312-456 (old momentum)
- `computeHydrodynamicForce()` - lines 477-788 (main calculation)
- `postprocessIntegrateData()` - lines 790-820 (writes to files)

### Step 3: Search for specific code
```bash
# Find where file names are created
grep -n "Drag_CV_strct_id_" src/IB/IBHydrodynamicForceEvaluator.cpp

# Find where forces are computed
grep -n "F_new.*=" src/IB/IBHydrodynamicForceEvaluator.cpp

# Find Reynolds Transport Theorem application
grep -n "P_box_new.*P_box_current" src/IB/IBHydrodynamicForceEvaluator.cpp
```

---

## Mathematical Summary

The force you see in `Drag_CV_strct_id_0` is computed as:

```
F_body = -d/dt(∫∫∫_CV ρu dV) + d/dt(P_body) + ∫∫_∂CV T·n dA

where:

  T·n = (-p I + μ(∇u + ∇u^T)) · n
      = -p n + μ(∇u + ∇u^T) · n

Components:
  1. -p n                    → Pressure force (lines 690-696)
  2. μ(∇u + ∇u^T) · n       → Viscous force (lines 719-769)
  3. -ρ(u·n)u               → Momentum flux (lines 698-717)
```

All terms are explicitly computed in the code!

---

## Verification Commands

### Check that files exist:
```bash
ls -lh Drag_CV_strct_id_* Torque_CV_strct_id_*
```

### View file contents:
```bash
head -20 Drag_CV_strct_id_0
```

### Run verification script:
```bash
cd /path/to/simulation/output
python3 /home/user/MyExten_IBAMR/docs/verify_force_files.py
```

### Search source code:
```bash
cd /home/user/MyExten_IBAMR/IBAMR-0.18.0
grep -r "Drag_CV_strct_id" src/
grep -r "Reynolds" include/
```

---

## References

### Source Code
- **This repository**: `/home/user/MyExten_IBAMR/IBAMR-0.18.0/`
- **GitHub**: https://github.com/IBAMR/IBAMR

### Papers
1. **Noca (1997)**: "On the evaluation of time-dependent fluid-dynamic forces on bluff bodies"
   - Caltech PhD thesis
   - Derives the moving control volume formulation

2. **Nangia et al. (2017)**: "A moving control volume approach to computing hydrodynamic forces and torques on immersed bodies"
   - J. Computational Physics, Vol 347, pp 437-462
   - Describes the exact method IBAMR uses

3. **Griffith & Patankar (2020)**: "Immersed Methods for Fluid-Structure Interaction"
   - Annual Review of Fluid Mechanics, Vol 52, pp 421-448
   - Overview of IB methods and force calculations

---

## Summary

**Question**: Where does `Drag_CV_strct_id_0` come from?

**Answer**:
- Created at line 237 of `IBHydrodynamicForceEvaluator.cpp`
- Forces computed using Reynolds Transport Theorem (lines 778-783)
- Includes pressure (690-696), viscous (719-769), and momentum flux (698-717)
- Written to file at lines 800-801
- Contains **exact hydrodynamic forces** from Navier-Stokes solution!

**You can verify every single line of this physics in the source code!**
