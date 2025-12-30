#!/bin/bash
# build_and_debug.sh - with timing info

echo "=== Step 1: Building executable ==="
rm -rf build
mkdir build
cd build

# 🔧 FIX 1: force Debug build with symbols
cmake .. -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_FLAGS="-g -O0"
make -j8

if [ ! -f main2d ]; then
    echo "ERROR: Build failed! No main2d created"
    exit 1
fi

echo ""
echo "✓ Build successful!"
echo ""
echo "=== Step 2: Running with debugger ==="

cd ..

# 🔧 FIX 2: robust GDB commands for PETSc/MPI
cat > gdb_commands.txt << 'EOF'
set pagination off
handle SIGSEGV stop print
handle SIGABRT stop print
run
bt full
info locals
thread apply all bt
quit
EOF

# Record start time
START_TIME=$(date +%s)
START_TIME_READABLE=$(date "+%Y-%m-%d %H:%M:%S")

echo "Simulation started at: $START_TIME_READABLE"
echo ""

ulimit -c unlimited

# 🔧 FIX 3: add PETSc memory protection flags
mpirun -np 8 gdb -batch -x gdb_commands.txt \
  --args build/main2d input2d -malloc_debug -malloc_test -on_error_abort \
  2>&1 | tee debug.log

# Record end time
END_TIME=$(date +%s)
END_TIME_READABLE=$(date "+%Y-%m-%d %H:%M:%S")
ELAPSED=$((END_TIME - START_TIME))

# Calculate hours, minutes, seconds
HOURS=$((ELAPSED / 3600))
MINUTES=$(((ELAPSED % 3600) / 60))
SECONDS=$((ELAPSED % 60))

rm -f gdb_commands.txt

echo ""
echo "=========================================="
echo "Simulation ended at: $END_TIME_READABLE"
echo "Total elapsed time: ${HOURS}h ${MINUTES}m ${SECONDS}s"
echo "=========================================="
echo ""

# Check last timestep reached
LAST_TIMESTEP=$(grep -i "timestep #" debug.log | tail -1)
if [ ! -z "$LAST_TIMESTEP" ]; then
    echo "Last timestep: $LAST_TIMESTEP"
fi

# Check if crashed
if grep -q "PETSC ERROR\|Segmentation\|SIGSEGV\|SIGABRT" debug.log; then
    echo "Status: CRASHED"
else
    echo "Status: Completed successfully"
fi

echo ""
echo "Last 40 lines of output:"
echo "=========================================="
tail -40 debug.log
