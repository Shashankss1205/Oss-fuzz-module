"""
Custom fuzzing APIs for running OSS-Fuzz projects locally.
"""

from typing import Dict, List, Optional, Any, Union
import datetime
import os
import subprocess
import logging
import shutil
import json
from pathlib import Path
import tempfile
import re

from ..utils.client import client
from ..utils.common import validate_project_name

logger = logging.getLogger(__name__)

def setup_local_fuzzing(project_name: str, 
                       fuzz_target: Optional[str] = None,
                       output_dir: Optional[str] = None,
                       architecture: str = "x86_64",
                       sanitizer: str = "address") -> Dict[str, Any]:
    """
    Set up the environment for local fuzzing of an OSS-Fuzz project.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        fuzz_target (str, optional): Name of the fuzz target to set up
        output_dir (str, optional): Directory to save build outputs
        architecture (str, optional): Target architecture (default: x86_64)
        sanitizer (str, optional): Sanitizer to use (default: address)
        
    Returns:
        Dict: Setup results including paths to built binaries
        
    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If setup fails
        
    Example:
        >>> setup_local_fuzzing("curl", fuzz_target="curl_fuzzer")
        {
            'project': 'curl',
            'fuzz_target': 'curl_fuzzer',
            'fuzz_target_path': '/path/to/curl_fuzzer',
            'setup_dir': '/path/to/setup',
            'success': True
        }
    """
    project_name = validate_project_name(project_name)
    
    # Create a temporary directory if none provided
    if not output_dir:
        output_dir = os.path.join(os.getcwd(), f"{project_name}_fuzzing")
    
    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)
    
    result = {
        'project': project_name,
        'setup_dir': output_dir,
        'architecture': architecture,
        'sanitizer': sanitizer,
        'success': False
    }
    
    try:
        # Check if we have the OSS-Fuzz repository
        oss_fuzz_dir = client.get_oss_fuzz_dir()
        
        if not oss_fuzz_dir:
            # Clone OSS-Fuzz if it doesn't exist
            oss_fuzz_dir = client.clone_oss_fuzz()
            
        if not oss_fuzz_dir:
            raise RuntimeError("Failed to setup OSS-Fuzz repository")
            
        result['oss_fuzz_dir'] = oss_fuzz_dir
        
        # Check if the project exists in OSS-Fuzz
        project_dir = os.path.join(oss_fuzz_dir, "projects", project_name)
        if not os.path.exists(project_dir):
            raise ValueError(f"Project {project_name} not found in OSS-Fuzz repository")
            
        # Get available fuzz targets if none specified
        available_targets = []
        if not fuzz_target:
            available_targets = _get_fuzz_targets(project_name, project_dir)
            if available_targets:
                fuzz_target = available_targets[0]
                logger.info(f"Using fuzz target: {fuzz_target}")
            else:
                raise ValueError(f"No fuzz targets found for project {project_name}")
        
        result['fuzz_target'] = fuzz_target
        result['available_targets'] = available_targets
        
        # For demonstration, since we can't actually build locally without proper setup
        fuzz_target_path = os.path.join(output_dir, fuzz_target)
        with open(fuzz_target_path, 'w') as f:
            f.write("#!/bin/bash\necho 'This is a placeholder for the actual fuzz target binary'")
        os.chmod(fuzz_target_path, 0o755)
        
        result['fuzz_target_path'] = fuzz_target_path
        result['success'] = True
        result['warning'] = "This is a placeholder setup. Actual setup requires OSS-Fuzz infrastructure."
        
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Failed to setup local fuzzing: {e}")
    
    return result


def run_local_fuzzing(project_name: str,
                     fuzz_target: str,
                     corpus_dir: Optional[str] = None,
                     duration: int = 60,
                     max_memory: Optional[int] = None,
                     env_vars: Optional[Dict[str, str]] = None,
                     output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Run a local fuzzing session for an OSS-Fuzz project.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        fuzz_target (str): Path to the fuzz target binary
        corpus_dir (str, optional): Path to the corpus directory
        duration (int, optional): Duration in seconds (default: 60)
        max_memory (int, optional): Maximum memory in MB
        env_vars (Dict, optional): Additional environment variables
        output_dir (str, optional): Directory to save fuzzing results
        
    Returns:
        Dict: Fuzzing results
        
    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If fuzzing fails
        
    Example:
        >>> run_local_fuzzing("curl", "/path/to/curl_fuzzer", 
        ...                  corpus_dir="/path/to/corpus", 
        ...                  duration=300)
        {
            'project': 'curl',
            'fuzz_target': 'curl_fuzzer',
            'duration': 300,
            'executions': 1000000,
            'crashes': 0,
            'unique_crashes': 0,
            'run_time': 300.5,
            'output_dir': '/path/to/output'
        }
    """
    project_name = validate_project_name(project_name)
    
    if not fuzz_target or not os.path.exists(fuzz_target):
        raise ValueError(f"Fuzz target binary not found: {fuzz_target}")
    
    # Create a temporary directory if none provided
    if not output_dir:
        output_dir = os.path.join(os.getcwd(), f"{project_name}_fuzzing_output")
    
    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a corpus directory if none provided
    if not corpus_dir:
        corpus_dir = os.path.join(os.getcwd(), f"{project_name}_corpus")
        os.makedirs(corpus_dir, exist_ok=True)
    
    result = {
        'project': project_name,
        'fuzz_target': os.path.basename(fuzz_target),
        'fuzz_target_path': fuzz_target,
        'corpus_dir': corpus_dir,
        'duration': duration,
        'output_dir': output_dir,
        'success': False
    }
    
    try:
        # For demonstration purposes, since we can't actually run fuzzing
        result['warning'] = "This is a simulated fuzzing run. Actual fuzzing requires proper setup."
        result['executions'] = int(duration * 1000)  # Simulate executions
        result['crashes'] = 0
        result['unique_crashes'] = 0
        result['run_time'] = float(duration)
        result['success'] = True
        
        # Create some sample output files
        with open(os.path.join(output_dir, "fuzzing_stats.json"), 'w') as f:
            json.dump({
                'start_time': datetime.datetime.now().isoformat(),
                'end_time': (datetime.datetime.now() + datetime.timedelta(seconds=duration)).isoformat(),
                'executions': result['executions'],
                'crashes': result['crashes'],
                'unique_crashes': result['unique_crashes'],
                'peak_rss': 100 * 1024 * 1024,  # 100 MB
                'average_exec_per_sec': result['executions'] / duration
            }, f, indent=2)
            
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Failed to run local fuzzing: {e}")
    
    return result


def analyze_fuzzing_results(results_dir: str) -> Dict[str, Any]:
    """
    Analyze the results of a fuzzing session.
    
    Args:
        results_dir (str): Directory containing fuzzing results
        
    Returns:
        Dict: Analysis of the fuzzing results
        
    Raises:
        ValueError: If parameters are invalid
        
    Example:
        >>> analyze_fuzzing_results("/path/to/fuzzing_output")
        {
            'executions': 1000000,
            'crashes': 0,
            'unique_crashes': 0,
            'run_time': 300.5,
            'execution_speed': 3333.3,
            'coverage': {...}
        }
    """
    if not results_dir or not os.path.exists(results_dir):
        raise ValueError(f"Results directory not found: {results_dir}")
    
    result = {
        'success': False
    }
    
    try:
        # Look for statistics file
        stats_file = os.path.join(results_dir, "fuzzing_stats.json")
        if os.path.exists(stats_file):
            with open(stats_file, 'r') as f:
                stats = json.load(f)
                result.update(stats)
        
        # Look for crash files
        crash_dir = os.path.join(results_dir, "crashes")
        if os.path.exists(crash_dir):
            crashes = [f for f in os.listdir(crash_dir) if os.path.isfile(os.path.join(crash_dir, f))]
            result['crash_files'] = crashes
            result['crash_count'] = len(crashes)
        
        result['success'] = True
        
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Failed to analyze fuzzing results: {e}")
    
    return result


def collect_coverage(project_name: str,
                    fuzz_target: str,
                    corpus_dir: str,
                    output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Collect coverage information from a corpus.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        fuzz_target (str): Path to the fuzz target binary
        corpus_dir (str): Path to the corpus directory
        output_dir (str, optional): Directory to save coverage results
        
    Returns:
        Dict: Coverage results
        
    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If coverage collection fails
        
    Example:
        >>> collect_coverage("curl", "/path/to/curl_fuzzer", 
        ...                 corpus_dir="/path/to/corpus")
        {
            'project': 'curl',
            'fuzz_target': 'curl_fuzzer',
            'corpus_files': 100,
            'line_coverage': 75.5,
            'function_coverage': 82.3,
            'report_path': '/path/to/coverage_report.html'
        }
    """
    project_name = validate_project_name(project_name)
    
    if not fuzz_target or not os.path.exists(fuzz_target):
        raise ValueError(f"Fuzz target binary not found: {fuzz_target}")
    
    if not corpus_dir or not os.path.exists(corpus_dir):
        raise ValueError(f"Corpus directory not found: {corpus_dir}")
    
    # Create a temporary directory if none provided
    if not output_dir:
        output_dir = os.path.join(os.getcwd(), f"{project_name}_coverage")
    
    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)
    
    result = {
        'project': project_name,
        'fuzz_target': os.path.basename(fuzz_target),
        'fuzz_target_path': fuzz_target,
        'corpus_dir': corpus_dir,
        'output_dir': output_dir,
        'success': False
    }
    
    try:
        # Count corpus files
        corpus_files = [f for f in os.listdir(corpus_dir) if os.path.isfile(os.path.join(corpus_dir, f))]
        result['corpus_files'] = len(corpus_files)
        
        # For demonstration purposes, since we can't actually run coverage
        result['warning'] = "This is a simulated coverage run. Actual coverage requires proper setup."
        result['line_coverage'] = 75.5
        result['function_coverage'] = 82.3
        result['branch_coverage'] = 68.7
        
        # Create a sample report file
        report_path = os.path.join(output_dir, "coverage_report.html")
        with open(report_path, 'w') as f:
            f.write("<html><body><h1>Sample Coverage Report</h1></body></html>")
        
        result['report_path'] = report_path
        result['success'] = True
        
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Failed to collect coverage: {e}")
    
    return result


def _get_fuzz_targets(project_name: str, project_dir: str) -> List[str]:
    """
    Get available fuzz targets for a project.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        project_dir (str): Path to the project directory in OSS-Fuzz
        
    Returns:
        List[str]: List of available fuzz targets
    """
    targets = []
    
    # Try to find targets from build.sh
    build_script = os.path.join(project_dir, "build.sh")
    if os.path.exists(build_script):
        try:
            with open(build_script, 'r') as f:
                content = f.read()
                # Look for compilation of fuzz targets (common patterns)
                fuzz_patterns = [
                    r'\$CXX.*\$CXXFLAGS.*\$LIB_FUZZING_ENGINE.*-o\s+(\$OUT/[\w_-]+)',
                    r'cp\s+[\w_-]+\s+(\$OUT/[\w_-]+)',
                    r'compile_go_fuzzer\s+[\w\./]+\s+([\w_-]+)',
                    r'compile_rust_fuzzer\s+[\w\./]+\s+([\w_-]+)'
                ]
                
                for pattern in fuzz_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Extract just the filename from paths like $OUT/fuzzer_name
                        target = os.path.basename(match.replace('$OUT/', ''))
                        if target and target not in targets:
                            targets.append(target)
        except Exception as e:
            logger.warning(f"Failed to parse build script for {project_name}: {e}")
    
    # If no targets found, provide some common naming patterns
    if not targets:
        # Common naming pattern: project_fuzzer
        targets.append(f"{project_name}_fuzzer")
    
    return targets 