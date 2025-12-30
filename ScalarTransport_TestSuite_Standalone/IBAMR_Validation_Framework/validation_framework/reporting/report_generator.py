"""
Report Generation Module
========================

Generates comprehensive validation reports in Markdown format.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import os


class CompatibilityReportGenerator:
    """Generates comprehensive compatibility validation reports"""

    def __init__(self, results_dir: str, output_file: str = "Compatibility_Report.md"):
        """
        Initialize report generator.

        Parameters:
        -----------
        results_dir : str
            Path to results directory
        output_file : str
            Path to output markdown file
        """
        self.results_dir = Path(results_dir)
        self.output_file = Path(output_file)
        self.test_results = {}
        self.summary_stats = {}

    def collect_results(self):
        """Collect all test results from results directory"""
        test_dirs = sorted([d for d in self.results_dir.iterdir() if d.is_dir() and d.name.startswith('Test')])

        for test_dir in test_dirs:
            test_name = test_dir.name

            # Load test result JSON
            result_file = test_dir / 'test_result.json'
            metrics_file = test_dir / 'metrics.json'

            result_data = {}
            if result_file.exists():
                with open(result_file, 'r') as f:
                    result_data = json.load(f)

            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    metrics_data = json.load(f)
                    result_data['metrics'] = metrics_data

            self.test_results[test_name] = result_data

    def generate_report(self):
        """Generate complete compatibility report"""
        report_lines = []

        # Header
        report_lines.extend(self._generate_header())

        # Executive Summary
        report_lines.extend(self._generate_executive_summary())

        # Test Results Table
        report_lines.extend(self._generate_results_table())

        # Detailed Test Results
        report_lines.extend(self._generate_detailed_results())

        # Error Analysis
        report_lines.extend(self._generate_error_analysis())

        # Convergence Analysis
        report_lines.extend(self._generate_convergence_analysis())

        # Mass Conservation Analysis
        report_lines.extend(self._generate_mass_conservation_analysis())

        # Recommendations
        report_lines.extend(self._generate_recommendations())

        # Appendix
        report_lines.extend(self._generate_appendix())

        # Write report
        with open(self.output_file, 'w') as f:
            f.write('\n'.join(report_lines))

        print(f"Report generated: {self.output_file}")

    def _generate_header(self) -> List[str]:
        """Generate report header"""
        return [
            "# IBAMR Scalar Transport Test Suite",
            "## Compatibility Validation Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"**IBAMR Version:** 0.18.0",
            f"**Test Suite:** ScalarTransport_TestSuite_Standalone",
            f"**Total Tests:** {len(self.test_results)}",
            "",
            "---",
            ""
        ]

    def _generate_executive_summary(self) -> List[str]:
        """Generate executive summary"""
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results.values() if r.get('status') == 'PASSED')
        failed = sum(1 for r in self.test_results.values() if r.get('status') == 'FAILED')
        errors = total_tests - passed - failed

        lines = [
            "## Executive Summary",
            "",
            f"This report presents a comprehensive validation of the IBAMR 0.18.0 Scalar Transport "
            f"Test Suite. The validation includes quantitative error analysis, convergence studies, "
            f"and mass conservation verification.",
            "",
            "### Overall Results",
            "",
            f"- **Total Tests:** {total_tests}",
            f"- **Passed:** {passed} ({100*passed/total_tests:.1f}%)" if total_tests > 0 else "- **Passed:** 0 (0%)",
            f"- **Failed:** {failed} ({100*failed/total_tests:.1f}%)" if total_tests > 0 else "- **Failed:** 0 (0%)",
            f"- **Errors:** {errors} ({100*errors/total_tests:.1f}%)" if total_tests > 0 else "- **Errors:** 0 (0%)",
            "",
        ]

        # Overall assessment
        if failed == 0 and errors == 0:
            assessment = "✅ **EXCELLENT** - All tests passed successfully."
        elif failed <= total_tests * 0.1:
            assessment = "⚠️ **GOOD** - Most tests passed with minor issues."
        else:
            assessment = "❌ **NEEDS ATTENTION** - Significant test failures detected."

        lines.extend([
            f"**Assessment:** {assessment}",
            "",
            "---",
            ""
        ])

        return lines

    def _generate_results_table(self) -> List[str]:
        """Generate summary results table"""
        lines = [
            "## Test Results Summary",
            "",
            "| Test | Status | Duration | L2 Error | L∞ Error | Mass Error | Convergence Rate |",
            "|------|--------|----------|----------|----------|------------|------------------|"
        ]

        for test_name in sorted(self.test_results.keys()):
            result = self.test_results[test_name]
            status = result.get('status', 'UNKNOWN')
            duration = result.get('duration', 0)

            # Get metrics if available
            metrics = result.get('metrics', {})
            l2_error = metrics.get('L2', 'N/A')
            linf_error = metrics.get('Linf', 'N/A')
            mass_error = metrics.get('mass_error', 'N/A')
            conv_rate = metrics.get('convergence_rate', 'N/A')

            # Format values
            if isinstance(l2_error, (int, float)):
                l2_str = f"{l2_error:.2e}"
            else:
                l2_str = str(l2_error)

            if isinstance(linf_error, (int, float)):
                linf_str = f"{linf_error:.2e}"
            else:
                linf_str = str(linf_error)

            if isinstance(mass_error, (int, float)):
                mass_str = f"{mass_error:.2e}"
            else:
                mass_str = str(mass_error)

            if isinstance(conv_rate, (int, float)):
                conv_str = f"{conv_rate:.2f}"
            else:
                conv_str = str(conv_rate)

            # Status emoji
            status_emoji = {
                'PASSED': '✅',
                'FAILED': '❌',
                'TIMEOUT': '⏱️',
                'ERROR': '⚠️',
                'NOT_BUILT': '🔨'
            }.get(status, '❓')

            lines.append(
                f"| {test_name} | {status_emoji} {status} | {duration:.1f}s | {l2_str} | {linf_str} | {mass_str} | {conv_str} |"
            )

        lines.extend(["", "---", ""])
        return lines

    def _generate_detailed_results(self) -> List[str]:
        """Generate detailed results for each test"""
        lines = [
            "## Detailed Test Results",
            ""
        ]

        for test_name in sorted(self.test_results.keys()):
            result = self.test_results[test_name]
            metrics = result.get('metrics', {})

            lines.extend([
                f"### {test_name}",
                ""
            ])

            # Test info
            status = result.get('status', 'UNKNOWN')
            lines.append(f"**Status:** {status}")

            if status == 'PASSED':
                lines.append("")

                # Error metrics
                if metrics:
                    lines.append("#### Error Metrics")
                    lines.append("")
                    for metric, value in metrics.items():
                        if isinstance(value, (int, float)):
                            lines.append(f"- **{metric}:** {value:.6e}")
                        else:
                            lines.append(f"- **{metric}:** {value}")
                    lines.append("")

                # Plots
                plots_dir = self.results_dir / test_name / 'plots'
                if plots_dir.exists():
                    plot_files = list(plots_dir.glob('*.png'))
                    if plot_files:
                        lines.append("#### Visualizations")
                        lines.append("")
                        for plot_file in sorted(plot_files):
                            rel_path = os.path.relpath(plot_file, self.output_file.parent)
                            plot_name = plot_file.stem.replace('_', ' ').title()
                            lines.append(f"![{plot_name}]({rel_path})")
                            lines.append("")

            elif status == 'FAILED':
                lines.append("")
                error_file = self.results_dir / test_name / 'test_error.log'
                if error_file.exists():
                    lines.append("**Error Log:**")
                    lines.append("```")
                    with open(error_file, 'r') as f:
                        error_lines = f.readlines()[:20]  # First 20 lines
                        lines.extend([line.rstrip() for line in error_lines])
                    lines.append("```")
                    lines.append("")

            lines.append("---")
            lines.append("")

        return lines

    def _generate_error_analysis(self) -> List[str]:
        """Generate error analysis section"""
        lines = [
            "## Error Analysis",
            "",
            "This section analyzes error metrics across all tests.",
            ""
        ]

        # Collect error metrics
        l2_errors = []
        linf_errors = []

        for test_name, result in self.test_results.items():
            metrics = result.get('metrics', {})
            if 'L2' in metrics and isinstance(metrics['L2'], (int, float)):
                l2_errors.append((test_name, metrics['L2']))
            if 'Linf' in metrics and isinstance(metrics['Linf'], (int, float)):
                linf_errors.append((test_name, metrics['Linf']))

        if l2_errors:
            lines.append("### L2 Error Rankings")
            lines.append("")
            lines.append("| Rank | Test | L2 Error |")
            lines.append("|------|------|----------|")

            sorted_l2 = sorted(l2_errors, key=lambda x: x[1])
            for i, (test, error) in enumerate(sorted_l2, 1):
                lines.append(f"| {i} | {test} | {error:.6e} |")

            lines.append("")

        if linf_errors:
            lines.append("### L∞ Error Rankings")
            lines.append("")
            lines.append("| Rank | Test | L∞ Error |")
            lines.append("|------|------|----------|")

            sorted_linf = sorted(linf_errors, key=lambda x: x[1])
            for i, (test, error) in enumerate(sorted_linf, 1):
                lines.append(f"| {i} | {test} | {error:.6e} |")

            lines.append("")

        lines.extend(["---", ""])
        return lines

    def _generate_convergence_analysis(self) -> List[str]:
        """Generate convergence analysis section"""
        lines = [
            "## Convergence Analysis",
            "",
            "Analysis of convergence rates for applicable tests.",
            "",
            "| Test | Convergence Rate | Expected | Status |",
            "|------|------------------|----------|--------|"
        ]

        for test_name, result in sorted(self.test_results.items()):
            metrics = result.get('metrics', {})
            if 'convergence_rate' in metrics:
                rate = metrics['convergence_rate']
                expected = metrics.get('expected_order', 'N/A')

                if isinstance(rate, (int, float)):
                    if rate >= 1.8:
                        status = "✅ 2nd order"
                    elif rate >= 0.8:
                        status = "✅ 1st order"
                    elif rate >= 0.5:
                        status = "⚠️ Sub-linear"
                    else:
                        status = "❌ Poor"

                    lines.append(f"| {test_name} | {rate:.3f} | {expected} | {status} |")

        lines.extend(["", "---", ""])
        return lines

    def _generate_mass_conservation_analysis(self) -> List[str]:
        """Generate mass conservation analysis"""
        lines = [
            "## Mass Conservation Analysis",
            "",
            "Verification of mass conservation for all tests.",
            "",
            "| Test | Initial Mass | Final Mass | Relative Error | Status |",
            "|------|--------------|------------|----------------|--------|"
        ]

        for test_name, result in sorted(self.test_results.items()):
            metrics = result.get('metrics', {})
            if 'initial_mass' in metrics and 'final_mass' in metrics:
                M0 = metrics['initial_mass']
                Mf = metrics['final_mass']
                rel_error = abs(Mf - M0) / M0 if M0 != 0 else abs(Mf - M0)

                if rel_error < 1e-6:
                    status = "✅ Excellent"
                elif rel_error < 1e-4:
                    status = "✅ Good"
                elif rel_error < 1e-2:
                    status = "⚠️ Acceptable"
                else:
                    status = "❌ Poor"

                lines.append(f"| {test_name} | {M0:.6e} | {Mf:.6e} | {rel_error:.6e} | {status} |")

        lines.extend(["", "---", ""])
        return lines

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on results"""
        lines = [
            "## Recommendations",
            ""
        ]

        failed_tests = [name for name, result in self.test_results.items()
                       if result.get('status') == 'FAILED']

        if not failed_tests:
            lines.append("✅ All tests passed successfully. No immediate action required.")
        else:
            lines.append("### Failed Tests")
            lines.append("")
            lines.append("The following tests failed and require investigation:")
            lines.append("")
            for test in failed_tests:
                lines.append(f"- **{test}**")
            lines.append("")

        lines.extend(["---", ""])
        return lines

    def _generate_appendix(self) -> List[str]:
        """Generate appendix with additional information"""
        lines = [
            "## Appendix",
            "",
            "### Test Suite Structure",
            "",
            "```",
            "ScalarTransport_TestSuite_Standalone/",
            "├── results/",
        ]

        for test_name in sorted(self.test_results.keys()):
            lines.extend([
                f"│   ├── {test_name}/",
                "│   │   ├── raw/",
                "│   │   ├── plots/",
                "│   │   ├── metrics.json",
                "│   │   └── summary.md",
            ])

        lines.extend([
            "└── Compatibility_Report.md",
            "```",
            "",
            "### Metric Definitions",
            "",
            "- **L1 Error:** $L_1 = \\frac{\\int |u_{computed} - u_{exact}| dV}{\\int |u_{exact}| dV}$",
            "- **L2 Error:** $L_2 = \\frac{\\sqrt{\\int (u_{computed} - u_{exact})^2 dV}}{\\sqrt{\\int u_{exact}^2 dV}}$",
            "- **L∞ Error:** $L_\\infty = \\frac{\\max |u_{computed} - u_{exact}|}{\\max |u_{exact}|}$",
            "- **Mass Error:** $\\frac{|M_{final} - M_{initial}|}{M_{initial}}$",
            "- **Convergence Rate:** Slope of $\\log(error)$ vs $\\log(h)$",
            "",
            "---",
            "",
            "**End of Report**"
        ])

        return lines


def generate_compatibility_report(results_dir: str,
                                  output_file: str = "Compatibility_Report.md"):
    """
    Generate compatibility validation report.

    Parameters:
    -----------
    results_dir : str
        Path to results directory
    output_file : str
        Output markdown file path
    """
    generator = CompatibilityReportGenerator(results_dir, output_file)
    generator.collect_results()
    generator.generate_report()
