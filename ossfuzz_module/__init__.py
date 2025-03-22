"""
OSS-Fuzz API - Python interface for interacting with OSS-Fuzz services.

This module provides APIs for:
- Getting information about OSS-Fuzz projects
- Retrieving historical fuzzing results
- Running custom fuzzing jobs
"""

from . import project_info
from . import historical_results
from . import custom_fuzzing
from . import utils

__version__ = "0.1.0"

__all__ = [
    'project_info',
    'historical_results',
    'custom_fuzzing',
    'utils'
] 