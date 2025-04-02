"""
Project information APIs for OSS-Fuzz projects.
"""

from typing import Dict, List, Optional, Any, Union
import os
import logging
from datetime import datetime

from ..utils.client import client
from ..utils.common import validate_project_name
from ..models import OSSFuzzProject, FuzzTarget

logger = logging.getLogger(__name__)

def list_projects() -> List[str]:
    """
    Get a list of all projects available in OSS-Fuzz.
    
    Returns:
        List of project names
        
    Example:
        >>> list_projects()
        ['curl', 'ffmpeg', 'openssl', ...]
    """
    projects = client.get_projects_from_repo()
    return [p.name for p in projects]


def get_project_details(project_name: str) -> OSSFuzzProject:
    """
    Get detailed information about a specific project.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        
    Returns:
        OSSFuzzProject: Project details
        
    Raises:
        ValueError: If project name is invalid
        
    Example:
        >>> project = get_project_details("curl")
        >>> print(f"Project: {project.name}, Language: {project.language}")
        Project: curl, Language: c++
    """
    project_name = validate_project_name(project_name)
    return client.get_project_details_from_repo(project_name)


def get_fuzz_targets(project_name: str) -> List[FuzzTarget]:
    """
    Get information about available fuzz targets for a specific project.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        
    Returns:
        List[FuzzTarget]: List of available fuzz targets
        
    Raises:
        ValueError: If project name is invalid
        
    Example:
        >>> targets = get_fuzz_targets("curl")
        >>> print(f"Found {len(targets)} fuzz targets")
        Found 5 fuzz targets
    """
    project_name = validate_project_name(project_name)
    project = get_project_details(project_name)
    return client.get_fuzz_targets(project)


def check_project_exists(project_name: str) -> bool:
    """
    Check if a project exists in OSS-Fuzz.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        
    Returns:
        bool: True if the project exists, False otherwise
        
    Example:
        >>> check_project_exists("curl")
        True
        >>> check_project_exists("nonexistent_project")
        False
    """
    try:
        project_name = validate_project_name(project_name)
        
        # Get list of all projects
        projects = list_projects()
        
        return project_name in projects
        
    except ValueError:
        # If project name is invalid, return False
        return False


def get_projects(language: Optional[str] = None,
                build_system: Optional[str] = None,
                sanitizer: Optional[str] = None,
                fuzzer_engine: Optional[str] = None) -> List[OSSFuzzProject]:
    """
    Get list of OSS-Fuzz projects with optional filtering.
    
    Args:
        language (str, optional): Filter by programming language
        build_system (str, optional): Filter by build system (e.g., cmake, bazel)
        sanitizer (str, optional): Filter by sanitizer (e.g., address, undefined)
        fuzzer_engine (str, optional): Filter by fuzzer engine (e.g., libfuzzer, afl)
        
    Returns:
        List[OSSFuzzProject]: List of projects
        
    Example:
        >>> projects = get_projects(language="c++")
        >>> print(f"Found {len(projects)} C++ projects")
        Found 42 C++ projects
    """
    try:
        # Get all projects from local OSS-Fuzz repo
        projects = client.get_projects_from_repo()
        
        # Apply filters
        if language:
            projects = [p for p in projects if p.language and p.language.lower() == language.lower()]
        
        if sanitizer:
            projects = [p for p in projects if sanitizer in p.sanitizers]
            
        if fuzzer_engine:
            projects = [p for p in projects if fuzzer_engine in p.fuzzing_engines]
        
        # Note: build_system is not directly available in project.yaml
        # We could parse Dockerfile or build.sh to determine this
        
        return projects
    except Exception as e:
        logger.error(f"Error retrieving projects: {e}")
        return []


def get_project_stats(project_name: str) -> Dict[str, Any]:
    """
    Get statistics about a specific OSS-Fuzz project.
    
    Args:
        project_name (str): Name of the project
        
    Returns:
        Dict: Project statistics including coverage, bugs found, etc.
        
    Raises:
        ValueError: If project_name is invalid
    """
    project_name = validate_project_name(project_name)
    
    try:
        # This would be implemented with actual stats from OSS-Fuzz service
        # For now, return a placeholder
        return {
            "warning": "Access to project statistics requires OSS-Fuzz service access",
            "project": project_name,
            "example_url": f"https://oss-fuzz.com/stats/{project_name}",
        }
    except Exception as e:
        logger.error(f"Error retrieving project stats for {project_name}: {e}")
        return {
            "error": str(e),
            "project": project_name,
        }


def get_project_builds(project_name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get information about build status for a specific OSS-Fuzz project.
    
    Args:
        project_name (str): Name of the project
        limit (int, optional): Maximum number of builds to return
        
    Returns:
        List[Dict]: List of build status information
        
    Raises:
        ValueError: If project_name is invalid
    """
    project_name = validate_project_name(project_name)
    
    # This is a placeholder - actual implementation would require GCP access
    return [{
        "warning": "Access to build status requires OSS-Fuzz service access",
        "project": project_name,
        "example_url": f"https://oss-fuzz.com/build-status/{project_name}",
    }]


def _detect_build_system(project_name: str) -> Optional[str]:
    """
    Try to detect build system from project files.
    
    Args:
        project_name (str): Name of the project
        
    Returns:
        Optional[str]: Detected build system or None
    """
    if not client.oss_fuzz_dir:
        return None
        
    project_dir = client.oss_fuzz_dir / "projects" / project_name
    dockerfile_path = project_dir / "Dockerfile"
    
    if not dockerfile_path.exists():
        return None
    
    build_systems = {
        r'cmake': 'cmake',
        r'\.\/configure': 'autoconf',
        r'autogen\.sh': 'autoconf',
        r'\.\/bootstrap': 'autoconf',
        r'meson': 'meson',
        r'ninja': 'ninja',
        r'bazel': 'bazel',
        r'make': 'make',
        r'pip\s+install': 'pip',
        r'setup\.py': 'setuptools',
    }
    
    try:
        with open(dockerfile_path, 'r') as f:
            content = f.read()
            
        for pattern, build_system in build_systems.items():
            if re.search(pattern, content, re.IGNORECASE):
                return build_system
    except Exception as e:
        logger.warning(f"Error detecting build system for {project_name}: {e}")
    
    return None


def _get_fuzz_targets(project_name: str) -> List[str]:
    """
    Try to detect fuzz targets from project files.
    
    Args:
        project_name (str): Name of the project
        
    Returns:
        List[str]: List of detected fuzz targets
    """
    if not client.oss_fuzz_dir:
        return []
        
    project_dir = client.oss_fuzz_dir / "projects" / project_name
    build_sh_path = project_dir / "build.sh"
    
    if not build_sh_path.exists():
        return []
    
    fuzz_targets = []
    
    try:
        with open(build_sh_path, 'r') as f:
            content = f.read()
            
        # Look for compile_*_fuzzer lines
        targets = re.findall(r'compile_\w+_fuzzer\s+\$?\w+\s+(\w+)_fuzzer', content)
        if targets:
            fuzz_targets.extend([f"{t}_fuzzer" for t in targets])
            
        # Also look for lines that build fuzzers directly
        targets = re.findall(r'(\w+_fuzzer)\.\w+', content)
        if targets:
            fuzz_targets.extend(targets)
    except Exception as e:
        logger.warning(f"Error detecting fuzz targets for {project_name}: {e}")
    
    return list(set(fuzz_targets))  # Remove duplicates 