"""
IBAMR Validation Framework - Reporting Module
==============================================

Generate comprehensive validation reports.
"""

from .report_generator import (
    CompatibilityReportGenerator,
    generate_compatibility_report
)

__all__ = [
    'CompatibilityReportGenerator',
    'generate_compatibility_report',
]
