# IBSAMRAI2 Patches for GCC 11+ Compatibility

This directory contains patches required to build IBSAMRAI2 with GCC 11 and later versions on Ubuntu 22.04.

## Background

GCC 11 introduced stricter type checking and changed the default C++ standard to gnu++17. This causes compilation failures in IBSAMRAI2, which was written for older compilers.

## Patches

### ibsamrai2-gcc11-hdfdatabasefactory.patch

**Issue**: Invalid conversion from `HDFDatabase*` to `Database*` when initializing `Pointer<Database>`

**Error Message**:
```
error: invalid conversion from 'SAMRAI::tbox::HDFDatabase*' to 'SAMRAI::tbox::Database*' [-fpermissive]
```

**Fix**:
1. Adds explicit include of `HDFDatabase.h` to ensure the full type definition is available
2. Adds explicit `static_cast<Database*>` when creating `Pointer<Database>` from `HDFDatabase*`

This ensures the compiler sees the complete inheritance hierarchy and accepts the upcast.

## Application

These patches are automatically applied during CI builds in `.github/workflows/ci-ibamr.yml` before building IBSAMRAI2.

## Testing

To test the patches locally:

```bash
# Clone IBSAMRAI2
git clone https://github.com/IBAMR/IBSAMRAI2.git /tmp/IBSAMRAI2-src
cd /tmp/IBSAMRAI2-src

# Apply patch
patch -p1 < /path/to/MyExten_IBAMR/patches/ibsamrai2-gcc11-hdfdatabasefactory.patch

# Build with GCC 11+
export CXX=mpicxx
export CC=mpicc
export CXXFLAGS="-fpermissive"
./configure --prefix=/tmp/IBSAMRAI2-install
make -j$(nproc)
```

## Notes

- The `-fpermissive` flag is still needed for other implicit conversions throughout the codebase
- These patches should be contributed upstream to IBSAMRAI2 for broader benefit
- If IBSAMRAI2 is updated, these patches may need adjustment
