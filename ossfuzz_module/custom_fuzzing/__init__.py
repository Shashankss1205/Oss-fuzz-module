"""
Custom fuzzing APIs for OSS-Fuzz projects.
"""

from .api import (
    setup_local_fuzzing,
    run_local_fuzzing,
    analyze_fuzzing_results,
    collect_coverage
)

__all__ = [
    'setup_local_fuzzing',
    'run_local_fuzzing',
    'analyze_fuzzing_results',
    'collect_coverage'
] 