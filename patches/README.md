# IBSAMRAI2 Patches

This directory contains patches applied to the IBSAMRAI2 dependency during the build process.

## ibsamrai2-hdfdatabase-include.patch

**Issue**: Missing include in `HDFDatabaseFactory.C` causing compilation error:
```
error: 'HDFDatabase' was not declared in this scope
```

**Fix**: Adds `#include "tbox/HDFDatabase.h"` to the source file.

**Applied**: During CI build after cloning IBSAMRAI2 from upstream.

This patch is necessary because the upstream IBSAMRAI2 repository is missing a required header include, which causes compilation failures with modern GCC compilers (tested on Ubuntu 22.04 with GCC 11).
