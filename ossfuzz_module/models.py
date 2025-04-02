"""
Data models for OSS-Fuzz module.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

@dataclass
class OSSFuzzProject:
    """Represents an OSS-Fuzz project."""
    name: str
    path: Path
    language: Optional[str] = None
    main_repo: Optional[str] = None
    sanitizers: List[str] = None
    fuzzing_engines: List[str] = None
    architectures: List[str] = None
    maintainers: List[str] = None
    has_dockerfile: bool = False
    has_build_script: bool = False
    config: Dict[str, Any] = None

    def __post_init__(self):
        if self.sanitizers is None:
            self.sanitizers = []
        if self.fuzzing_engines is None:
            self.fuzzing_engines = []
        if self.architectures is None:
            self.architectures = []
        if self.maintainers is None:
            self.maintainers = []
        if self.config is None:
            self.config = {}

@dataclass
class FuzzTarget:
    """Represents a fuzz target in an OSS-Fuzz project."""
    name: str
    project: OSSFuzzProject
    build_script: Optional[Path] = None
    source_files: List[Path] = None
    dependencies: List[str] = None
    environment_vars: Dict[str, str] = None

    def __post_init__(self):
        if self.source_files is None:
            self.source_files = []
        if self.dependencies is None:
            self.dependencies = []
        if self.environment_vars is None:
            self.environment_vars = {}

@dataclass
class FuzzingExecution:
    """Represents a fuzzing execution session."""
    project: OSSFuzzProject
    target: FuzzTarget
    start_time: datetime
    end_time: Optional[datetime] = None
    corpus_dir: Optional[Path] = None
    output_dir: Optional[Path] = None
    duration: Optional[int] = None
    max_memory: Optional[int] = None
    executions: int = 0
    crashes: int = 0
    unique_crashes: int = 0
    coverage: float = 0.0
    environment_vars: Dict[str, str] = None
    status: str = "running"

    def __post_init__(self):
        if self.environment_vars is None:
            self.environment_vars = {}
        if self.end_time is None:
            self.end_time = datetime.now()
        if self.duration is None:
            self.duration = int((self.end_time - self.start_time).total_seconds())

@dataclass
class CoverageReport:
    """Represents a coverage report for a project."""
    project: OSSFuzzProject
    date: datetime
    line_coverage: float
    function_coverage: float
    overall_coverage: float
    covered_lines: List[int] = None
    covered_functions: List[str] = None
    uncovered_lines: List[int] = None
    uncovered_functions: List[str] = None

    def __post_init__(self):
        if self.covered_lines is None:
            self.covered_lines = []
        if self.covered_functions is None:
            self.covered_functions = []
        if self.uncovered_lines is None:
            self.uncovered_lines = []
        if self.uncovered_functions is None:
            self.uncovered_functions = [] 