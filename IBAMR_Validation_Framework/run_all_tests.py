#!/usr/bin/env python3
"""
IBAMR Scalar Transport Test Suite - Automated Test Runner
==========================================================

This script automatically discovers, runs, and organizes output from all
IBAMR scalar transport tests in the test suite.

Usage:
    python3 run_all_tests.py [OPTIONS]

Options:
    --build-dir PATH    Path to CMake build directory (default: ./build)
    --results-dir PATH  Path to results directory (default: ./results)
    --mpi-np N          Number of MPI processes (default: 4)
    --timeout SEC       Timeout per test in seconds (default: 3600)
    --tests TEST1,TEST2 Run only specific tests (default: all)
    --clean             Clean results directory before running
    --dry-run           Show what would be run without executing

Author: Automated Validation Framework
Date: 2025-11-19
"""

import os
import sys
import subprocess
import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime
import re
import glob

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TestDiscovery:
    """Discovers all IBAMR tests in the suite"""

    def __init__(self, suite_dir):
        self.suite_dir = Path(suite_dir)
        self.tests = []

    def discover_tests(self):
        """Find all Test* directories"""
        test_dirs = sorted(self.suite_dir.glob("Test*"))

        for test_dir in test_dirs:
            if not test_dir.is_dir():
                continue

            test_name = test_dir.name

            # Look for main.cpp to confirm it's a test
            main_cpp = test_dir / "main.cpp"
            if not main_cpp.exists():
                print(f"{Colors.WARNING}Warning: {test_name} has no main.cpp{Colors.ENDC}")
                continue

            # Look for input files
            input_files = list(test_dir.glob("input*"))

            test_info = {
                'name': test_name,
                'dir': str(test_dir),
                'executable_name': self._get_executable_name(test_name),
                'input_files': [str(f) for f in input_files],
                'has_2d': any('2d' in f.name for f in input_files),
                'has_3d': any('3d' in f.name for f in input_files),
            }

            self.tests.append(test_info)

        return self.tests

    def _get_executable_name(self, test_name):
        """Map test directory name to executable name"""
        # Based on CMakeLists.txt mapping
        mapping = {
            'Test01_SmokeTest': 'test01_smoke',
            'Test02_Diffusion_Analytic': 'test02_diffusion',
            'Test03_Advection_Analytic': 'test03_advection',
            'Test04_MMS': 'test04_mms',
            'Test05_Discontinuous': 'test05_discontinuous',
            'Test06_MassConservation': 'test06_mass_conservation',
            'Test07_BCs': 'test07_bcs',
            'Test08_SphereSource': 'test08_sphere_source',
            'Test09_HighSc': 'test09_high_sc',
            'Test10_MovingIB': 'test10_moving_ib',
            'Test11_AMR': 'test11_amr',
            'Test12_TimeStep': 'test12_timestep',
            'Test13_LongRun': 'test13_long_run',
            'Test14_Benchmarks': 'test14_benchmarks',
            'Test15_RotatingCylinder': 'test15_rotating_cylinder',
            'Test16_3DSphere': 'test16_3d_sphere',
            'Test17_PitchPlunge': 'test17_pitch_plunge',
        }
        return mapping.get(test_name, test_name.lower())

class TestRunner:
    """Runs individual tests and captures output"""

    def __init__(self, build_dir, results_dir, mpi_np=4, timeout=3600):
        self.build_dir = Path(build_dir)
        self.results_dir = Path(results_dir)
        self.mpi_np = mpi_np
        self.timeout = timeout
        self.results = []

    def run_test(self, test_info, dry_run=False):
        """Run a single test"""
        test_name = test_info['name']
        test_dir = Path(test_info['dir'])
        executable_name = test_info['executable_name']

        print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}Running: {test_name}{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")

        # Find executable
        executable = self.build_dir / executable_name
        if not executable.exists():
            print(f"{Colors.FAIL}✗ Executable not found: {executable}{Colors.ENDC}")
            return {
                'test': test_name,
                'status': 'NOT_BUILT',
                'error': 'Executable not found'
            }

        # Create results directory for this test
        test_results_dir = self.results_dir / test_name
        raw_dir = test_results_dir / 'raw'
        plots_dir = test_results_dir / 'plots'

        if dry_run:
            print(f"{Colors.OKCYAN}[DRY RUN] Would create: {test_results_dir}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}[DRY RUN] Would run: mpirun -np {self.mpi_np} {executable}{Colors.ENDC}")
            return {'test': test_name, 'status': 'DRY_RUN'}

        # Clean and create directories
        if test_results_dir.exists():
            shutil.rmtree(test_results_dir)
        raw_dir.mkdir(parents=True, exist_ok=True)
        plots_dir.mkdir(parents=True, exist_ok=True)

        # Determine which input file to use
        input_file = self._select_input_file(test_info)
        if input_file is None:
            print(f"{Colors.FAIL}✗ No input file found{Colors.ENDC}")
            return {
                'test': test_name,
                'status': 'NO_INPUT',
                'error': 'No input file found'
            }

        print(f"Input file: {input_file}")
        print(f"Executable: {executable}")
        print(f"MPI processes: {self.mpi_np}")
        print(f"Results directory: {test_results_dir}")

        # Build command
        cmd = [
            'mpirun',
            '-np', str(self.mpi_np),
            str(executable),
            str(input_file)
        ]

        # Run test
        start_time = datetime.now()
        print(f"\n{Colors.OKBLUE}Starting test at {start_time.strftime('%H:%M:%S')}...{Colors.ENDC}\n")

        log_file = test_results_dir / 'test_output.log'
        error_file = test_results_dir / 'test_error.log'

        try:
            with open(log_file, 'w') as log_f, open(error_file, 'w') as err_f:
                # Run from test directory
                result = subprocess.run(
                    cmd,
                    cwd=str(test_dir),
                    stdout=log_f,
                    stderr=err_f,
                    timeout=self.timeout
                )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Collect output files
            self._collect_output_files(test_dir, raw_dir)

            # Determine status
            if result.returncode == 0:
                status = 'PASSED'
                print(f"\n{Colors.OKGREEN}✓ Test PASSED (duration: {duration:.1f}s){Colors.ENDC}")
            else:
                status = 'FAILED'
                print(f"\n{Colors.FAIL}✗ Test FAILED (return code: {result.returncode}){Colors.ENDC}")

            test_result = {
                'test': test_name,
                'status': status,
                'duration': duration,
                'return_code': result.returncode,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'log_file': str(log_file),
                'error_file': str(error_file),
                'results_dir': str(test_results_dir),
                'input_file': str(input_file),
                'mpi_np': self.mpi_np
            }

        except subprocess.TimeoutExpired:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            status = 'TIMEOUT'
            print(f"\n{Colors.FAIL}✗ Test TIMEOUT after {duration:.1f}s{Colors.ENDC}")

            test_result = {
                'test': test_name,
                'status': status,
                'duration': duration,
                'error': 'Timeout exceeded',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
            }

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            status = 'ERROR'
            print(f"\n{Colors.FAIL}✗ Test ERROR: {str(e)}{Colors.ENDC}")

            test_result = {
                'test': test_name,
                'status': status,
                'duration': duration,
                'error': str(e),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
            }

        # Save test result
        result_json = test_results_dir / 'test_result.json'
        with open(result_json, 'w') as f:
            json.dump(test_result, f, indent=2)

        self.results.append(test_result)
        return test_result

    def _select_input_file(self, test_info):
        """Select appropriate input file (prefer 2d)"""
        input_files = test_info['input_files']

        if not input_files:
            return None

        # Prefer input2d
        for f in input_files:
            if 'input2d' in f:
                return f

        # Otherwise use first available
        return input_files[0]

    def _collect_output_files(self, test_dir, raw_dir):
        """Collect all output files generated by the test"""
        patterns = ['*.visit', '*.h5', '*.xmf', '*.dat', '*.csv', '*.vtk', 'viz*', 'dumps*']

        for pattern in patterns:
            for file in test_dir.glob(pattern):
                if file.is_file():
                    dest = raw_dir / file.name
                    shutil.copy2(file, dest)

        # Also collect any directories like viz_IB2d, dumps
        for item in test_dir.iterdir():
            if item.is_dir() and (item.name.startswith('viz') or item.name.startswith('dump')):
                dest_dir = raw_dir / item.name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(item, dest_dir)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='IBAMR Scalar Transport Test Suite - Automated Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--build-dir', type=str, default='./build',
                        help='Path to CMake build directory (default: ./build)')
    parser.add_argument('--results-dir', type=str, default='./results',
                        help='Path to results directory (default: ./results)')
    parser.add_argument('--mpi-np', type=int, default=4,
                        help='Number of MPI processes (default: 4)')
    parser.add_argument('--timeout', type=int, default=3600,
                        help='Timeout per test in seconds (default: 3600)')
    parser.add_argument('--tests', type=str,
                        help='Comma-separated list of tests to run (default: all)')
    parser.add_argument('--clean', action='store_true',
                        help='Clean results directory before running')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be run without executing')

    args = parser.parse_args()

    # Print header
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("="*70)
    print("IBAMR SCALAR TRANSPORT TEST SUITE - AUTOMATED RUNNER")
    print("="*70)
    print(f"{Colors.ENDC}")
    print(f"Build directory:   {args.build_dir}")
    print(f"Results directory: {args.results_dir}")
    print(f"MPI processes:     {args.mpi_np}")
    print(f"Timeout:           {args.timeout}s")
    print(f"Dry run:           {args.dry_run}")
    print()

    # Get suite directory
    suite_dir = Path(__file__).parent.absolute()

    # Discover tests
    print(f"{Colors.OKBLUE}Discovering tests...{Colors.ENDC}")
    discovery = TestDiscovery(suite_dir)
    all_tests = discovery.discover_tests()

    print(f"{Colors.OKGREEN}Found {len(all_tests)} tests:{Colors.ENDC}")
    for test in all_tests:
        print(f"  • {test['name']}")

    # Filter tests if requested
    if args.tests:
        test_names = [t.strip() for t in args.tests.split(',')]
        all_tests = [t for t in all_tests if t['name'] in test_names]
        print(f"\n{Colors.WARNING}Filtered to {len(all_tests)} tests{Colors.ENDC}")

    # Clean results directory if requested
    results_dir = Path(args.results_dir)
    if args.clean and results_dir.exists() and not args.dry_run:
        print(f"\n{Colors.WARNING}Cleaning results directory...{Colors.ENDC}")
        shutil.rmtree(results_dir)

    results_dir.mkdir(parents=True, exist_ok=True)

    # Run tests
    runner = TestRunner(args.build_dir, results_dir, args.mpi_np, args.timeout)

    print(f"\n{Colors.BOLD}Starting test execution...{Colors.ENDC}\n")

    for i, test in enumerate(all_tests, 1):
        print(f"\n{Colors.BOLD}[{i}/{len(all_tests)}]{Colors.ENDC}")
        runner.run_test(test, dry_run=args.dry_run)

    # Save summary
    if not args.dry_run:
        summary_file = results_dir / 'test_summary.json'
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(all_tests),
            'results': runner.results,
            'config': {
                'build_dir': args.build_dir,
                'mpi_np': args.mpi_np,
                'timeout': args.timeout,
            }
        }

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        # Print final summary
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("="*70)
        print("TEST EXECUTION SUMMARY")
        print("="*70)
        print(f"{Colors.ENDC}")

        passed = sum(1 for r in runner.results if r['status'] == 'PASSED')
        failed = sum(1 for r in runner.results if r['status'] == 'FAILED')
        errors = sum(1 for r in runner.results if r['status'] not in ['PASSED', 'FAILED'])

        print(f"Total tests:  {len(runner.results)}")
        print(f"{Colors.OKGREEN}Passed:       {passed}{Colors.ENDC}")
        print(f"{Colors.FAIL}Failed:       {failed}{Colors.ENDC}")
        print(f"{Colors.WARNING}Errors:       {errors}{Colors.ENDC}")
        print(f"\nSummary saved to: {summary_file}")
        print()

        # Return appropriate exit code
        if failed > 0 or errors > 0:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == '__main__':
    main()
