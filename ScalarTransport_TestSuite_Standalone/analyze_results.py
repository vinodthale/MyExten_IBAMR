#!/usr/bin/env python3
"""
IBAMR Scalar Transport - Results Analysis Script
=================================================

Analyzes test results, computes error metrics, generates plots,
and creates the final validation report.

Usage:
    python3 analyze_results.py [OPTIONS]

Options:
    --results-dir PATH    Path to results directory (default: ./results)
    --report-output PATH  Path to report output (default: ./Compatibility_Report.md)
"""

import sys
import os
import argparse
import json
from pathlib import Path

# Add validation framework to path
sys.path.insert(0, str(Path(__file__).parent))

from validation_framework.analysis import *
from validation_framework.plotting import *
from validation_framework.reporting import generate_compatibility_report


def analyze_test_results(test_dir: Path):
    """
    Analyze results for a single test.

    Parameters:
    -----------
    test_dir : Path
        Path to test results directory
    """
    print(f"\nAnalyzing {test_dir.name}...")

    raw_dir = test_dir / 'raw'
    plots_dir = test_dir / 'plots'
    plots_dir.mkdir(exist_ok=True)

    metrics = {}

    # Example analysis - customize based on actual output
    # This is a template that should be adapted to actual IBAMR output format

    try:
        # Try to find and analyze HDF5 files
        h5_files = list(raw_dir.glob('*.h5'))

        if h5_files:
            print(f"  Found {len(h5_files)} HDF5 files")

            # For demonstration, compute basic statistics
            # In real use, you would:
            # 1. Load computed and exact solutions
            # 2. Compute L1, L2, Linf errors
            # 3. Check mass conservation
            # 4. Analyze convergence if multiple resolutions

            # Placeholder metrics
            metrics = {
                'status': 'analyzed',
                'n_outputs': len(h5_files),
                'test_dir': str(test_dir),
            }

            # Example: if you have exact solution, compute errors
            # computed = load_scalar_field(h5_files[-1], 'C')
            # exact = compute_exact_solution(...)
            # metrics.update(compute_all_errors(computed, exact))

        # Try to find log files and extract information
        log_file = test_dir / 'test_output.log'
        if log_file.exists():
            metrics['has_log'] = True

            # Parse log for useful info
            with open(log_file, 'r') as f:
                log_content = f.read()

                # Example: extract timesteps, convergence info, etc.
                # This depends on IBAMR output format

        # Save metrics
        metrics_file = test_dir / 'metrics.json'
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)

        print(f"  ✓ Metrics saved to {metrics_file}")

        # Generate summary for this test
        generate_test_summary(test_dir)

    except Exception as e:
        print(f"  ✗ Error analyzing {test_dir.name}: {str(e)}")
        metrics = {
            'status': 'error',
            'error_message': str(e)
        }

        metrics_file = test_dir / 'metrics.json'
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)


def generate_test_summary(test_dir: Path):
    """Generate individual test summary"""
    summary_file = test_dir / 'summary.md'

    lines = [
        f"# {test_dir.name} - Test Summary",
        "",
        f"**Test Directory:** `{test_dir}`",
        "",
        "## Test Information",
        ""
    ]

    # Load metrics if available
    metrics_file = test_dir / 'metrics.json'
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)

        lines.append("### Computed Metrics")
        lines.append("")
        for key, value in metrics.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")

    # Link to plots
    plots_dir = test_dir / 'plots'
    if plots_dir.exists():
        plot_files = list(plots_dir.glob('*.png'))
        if plot_files:
            lines.append("## Visualizations")
            lines.append("")
            for plot_file in sorted(plot_files):
                rel_path = os.path.relpath(plot_file, test_dir)
                lines.append(f"![{plot_file.stem}]({rel_path})")
                lines.append("")

    # Raw output files
    raw_dir = test_dir / 'raw'
    if raw_dir.exists():
        lines.append("## Raw Output Files")
        lines.append("")
        for item in sorted(raw_dir.iterdir()):
            lines.append(f"- `{item.name}`")
        lines.append("")

    with open(summary_file, 'w') as f:
        f.write('\n'.join(lines))


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Analyze IBAMR test results and generate report'
    )

    parser.add_argument('--results-dir', type=str, default='./results',
                       help='Path to results directory')
    parser.add_argument('--report-output', type=str, default='./Compatibility_Report.md',
                       help='Path to report output file')

    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    report_output = Path(args.report_output)

    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        sys.exit(1)

    print("="*70)
    print("IBAMR SCALAR TRANSPORT - RESULTS ANALYSIS")
    print("="*70)
    print(f"Results directory: {results_dir}")
    print(f"Report output: {report_output}")
    print()

    # Find all test result directories
    test_dirs = sorted([d for d in results_dir.iterdir()
                       if d.is_dir() and d.name.startswith('Test')])

    print(f"Found {len(test_dirs)} test result directories")

    # Analyze each test
    for test_dir in test_dirs:
        analyze_test_results(test_dir)

    print("\n" + "="*70)
    print("Generating compatibility report...")
    print("="*70)

    # Generate comprehensive report
    generate_compatibility_report(str(results_dir), str(report_output))

    print("\n✓ Analysis complete!")
    print(f"\nReport saved to: {report_output}")


if __name__ == '__main__':
    main()
