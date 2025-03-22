"""
Historical fuzzing results APIs for OSS-Fuzz projects.
"""

from .api import get_coverage, get_crash_reports, get_coverage_report, download_corpus

__all__ = [
    'get_coverage',
    'get_crash_reports',
    'get_coverage_report',
    'download_corpus'
] 