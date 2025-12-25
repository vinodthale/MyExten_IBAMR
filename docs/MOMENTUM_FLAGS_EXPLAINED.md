# Understanding `calculate_translational_momentum` and `calculate_rotational_momentum` Flags

## Quick Answer

**YES**, these flags control which momentum components are calculated for self-propelled (swimming) bodies, but they **DO NOT** affect the hydrodynamic force calculation in `Drag_CV_strct_id_0`.

---

## The Flags in Your Input File

From `input2d` (lines 126-127):
```
calculate_translational_momentum = 1,1,0
calculate_rotational_momentum    = 0,0,1
```

This means:
- **Translational:** Calculate x ✅, Calculate y ✅, DON'T calculate z ❌
- **Rotational:** DON'T calculate x ❌, DON'T calculate y ❌, Calculate z ✅

Since this is a 2D simulation, z-translation is disabled and z-rotation (out-of-plane) is enabled.

---

## What These Flags Actually Control

### Location in Code
**File:** `IBAMR-0.18.0/src/IB/ConstraintIBKinematics.cpp`

**Lines 65-71:**
```cpp
// Get options from database
d_calculate_trans_mom = input_db->getIntegerArray("calculate_translational_momentum");
d_calculate_rot_mom = input_db->getIntegerArray("calculate_rotational_momentum");
for (int i = 0; i < 3; ++i)
{
    if (d_calculate_trans_mom[i]) d_struct_is_self_translating = true;
    if (d_calculate_rot_mom[i]) d_struct_is_self_rotating = true;
}
```

These flags set:
- `d_struct_is_self_translating` - Is the body self-propelled (swimming)?
- `d_struct_is_self_rotating` - Does the body rotate due to self-propulsion?

---

## Purpose: Kinematics Velocity Momentum

These flags control the calculation of **kinematics velocity momentum**, which is the momentum due to the body's **prescribed deformation** (swimming motion), NOT the hydrodynamic forces!

### Where It's Used
**File:** `IBAMR-0.18.0/src/IB/ConstraintIBMethod.cpp`

**Function:** `calculateMomentumOfKinematicsVelocity()` (lines 1240-1380)

### What It Computes

#### 1. Translational Momentum from Deformation Velocity

**Lines 1256-1296:**
```cpp
// Calculate linear momentum
for (int ln = coarsest_ln; ln <= finest_ln; ++ln)
{
    // Sum up deformation velocities at all Lagrangian points
    for (const auto& node_idx : local_nodes)
    {
        for (int d = 0; d < NDIM; ++d)
        {
            U_com_def[d] += def_vel[d][lag_idx - offset];
                            ^^^^^^^^
                            Prescribed swimming velocity!
        }
    }
    d_vel_com_def_new[position_handle][d] += U_com_def[d];
}

// Average over all nodes, but ONLY for enabled directions
for (int d = 0; d < 3; ++d)
{
    if (calculate_trans_mom[d])
        d_vel_com_def_new[position_handle][d] /= total_nodes;
                                                  ^^^^^^^^^^^
                                                  Average velocity
    else
        d_vel_com_def_new[position_handle][d] = 0.0;
                                                 ^^^^
                                                 Zero out disabled directions!
}
```

**Physics:** Computes the **average translational velocity** of the body due to its swimming motion.

#### 2. Rotational Momentum from Deformation Velocity

**Lines 1298-1377:**
```cpp
// Calculate angular momentum
if (struct_param.getStructureIsSelfRotating())
{
    for (int ln = coarsest_ln; ln <= finest_ln; ++ln)
    {
        for (const auto& node_idx : local_nodes)
        {
            // Position vector from center of mass
            double x = X[0] - d_center_of_mass_unshifted_new[position_handle][0];
            double y = X[1] - d_center_of_mass_unshifted_new[position_handle][1];

            // Angular momentum: r × v_def
            R_cross_U_def[2] += (x * def_vel[1][lag_idx] - y * def_vel[0][lag_idx]);
                                      ^^^^^^^^                    ^^^^^^^^
                                      Prescribed swimming velocity!
        }
    }

    // Convert to angular velocity: ω = L / I
    d_omega_com_def_new[position_handle][2] /= d_moment_of_inertia_new[position_handle](2, 2);

    // Zero out disabled directions
    for (int d = 0; d < 3; ++d)
        if (!calculate_rot_mom[d])
            d_omega_com_def_new[position_handle][d] = 0.0;
}
```

**Physics:** Computes the **angular velocity** of the body due to its swimming motion.

---

## Why These Flags Exist: Self-Propulsion

For **self-propelled (swimming) bodies**, the body deforms according to prescribed kinematics:
- Eel swimming: `body_shape_equation` (input2d line 132)
- Deformation velocity: `deformation_velocity_function_0/1` (input2d lines 133-134)

This creates internal forces that propel the body through the fluid.

### The flags control:
1. **Which directions** the body can translate
2. **Which axes** the body can rotate about
3. Whether to **zero out** momentum in disabled directions

---

## Example: Your Eel Simulation

```
calculate_translational_momentum = 1,1,0
calculate_rotational_momentum    = 0,0,1
```

**Your eel can:**
- ✅ Swim in x-direction (forward/backward)
- ✅ Swim in y-direction (up/down)
- ❌ NOT move in z-direction (2D simulation)
- ❌ NOT rotate about x-axis (2D, out-of-plane)
- ❌ NOT rotate about y-axis (2D, out-of-plane)
- ✅ Rotate about z-axis (in-plane rotation - heading direction)

**Effect:**
- Eel can translate freely in 2D plane
- Eel can change its heading (yaw angle)
- All z-components are zeroed out

---

## Connection to Force Calculation

### ⚠️ IMPORTANT: These flags DO NOT affect force calculation!

The hydrodynamic forces in `Drag_CV_strct_id_0` are computed by:
1. `IBHydrodynamicForceEvaluator` (separate class)
2. Reynolds Transport Theorem
3. Control volume integration

**These are INDEPENDENT of the kinematics flags!**

### Where the kinematics momentum IS used:

The kinematics momentum (`d_vel_com_def_new`, `d_omega_com_def_new`) is used to:

1. **Update body velocity** (ConstraintIBMethod.cpp, line 888):
```cpp
if (struct_param.getStructureIsSelfTranslating())
    calculateMomentumOfKinematicsVelocity(struct_no);
```

2. **Provide body momentum to force evaluator**:
The `P_new` and `L_new` passed to `IBHydrodynamicForceEvaluator::updateStructureMomentum()` include contributions from kinematics velocity.

3. **Complete the momentum balance**:
```
Total momentum = Rigid body momentum + Deformation momentum
P_total = m * V_com + ∫ ρ * v_def dV
```

The flags determine which components of `v_def` contribute.

---

## Comparison: With vs Without Flags

### Scenario 1: All flags = 1,1,1 (all enabled)
```cpp
calculate_translational_momentum = 1,1,1
calculate_rotational_momentum    = 1,1,1
```
- Body can translate in all directions due to swimming
- Body can rotate about all axes
- All momentum components calculated

### Scenario 2: Constrained swimming (your case)
```cpp
calculate_translational_momentum = 1,1,0
calculate_rotational_momentum    = 0,0,1
```
- Body can swim in x-y plane only
- Body can only change heading (z-rotation)
- z-translation momentum set to zero
- x/y-rotation momentum set to zero

### Scenario 3: Fixed orientation swimmer
```cpp
calculate_translational_momentum = 1,1,0
calculate_rotational_momentum    = 0,0,0
```
- Body can swim in x-y plane
- Body CANNOT change heading
- Heading is fixed or externally prescribed

---

## Verification

### Check what momentum is being calculated:

Look in your output for files like:
- `Eel2dStr/Eel2d_TranslationalVelocity_*.curve`
- `Eel2dStr/Eel2d_RotationalVelocity_*.curve`

These will show which velocity components are non-zero.

### Debug output:

In the code, you can see when these are used:
```cpp
// Line 1233: Calculate kinematics momentum
if (struct_param.getStructureIsSelfTranslating())
    calculateMomentumOfKinematicsVelocity(struct_no);

// Lines 1590-1601: Set rigid velocity components
if (struct_param.getStructureIsSelfTranslating())
{
    for (int d = 0; d < NDIM; ++d)
    {
        if (calculate_trans_mom[d])
            d_rigid_trans_vel_new[struct_no][d] /= total_nodes;
        else
            d_rigid_trans_vel_new[struct_no][d] = 0.0;  // ZEROED!
    }
}
```

---

## Key Line Numbers Reference

| What | File | Lines |
|------|------|-------|
| Read flags from input | `ConstraintIBKinematics.cpp` | 65-71 |
| Set self-translating/rotating | `ConstraintIBKinematics.cpp` | 69-70 |
| Calculate kinematics momentum | `ConstraintIBMethod.cpp` | 1240-1380 |
| Apply translational flags | `ConstraintIBMethod.cpp` | 1290-1296 |
| Apply rotational flags | `ConstraintIBMethod.cpp` | 1375 |
| Use in velocity calculation | `ConstraintIBMethod.cpp` | 1590-1601 |

---

## Summary

| Flag | Controls | Used For | Affects Force Output? |
|------|----------|----------|----------------------|
| `calculate_translational_momentum` | Which translation directions | Body swimming velocity | ❌ NO (indirectly via P_body) |
| `calculate_rotational_momentum` | Which rotation axes | Body angular velocity | ❌ NO (indirectly via L_body) |

**Bottom Line:**
- These flags control **kinematics** (how the body moves due to swimming)
- They do NOT directly control **dynamics** (forces from the fluid)
- Forces in `Drag_CV_strct_id_0` are still computed correctly!
- The flags only determine which momentum components from swimming are included

**For force calculation, you can trust your data regardless of these flags!**

The flags just tell IBAMR: "When this eel swims, consider its motion in x-y plane and rotation about z only."
