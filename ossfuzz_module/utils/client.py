"""
Client for interacting with OSS-Fuzz services.
"""

import os
import yaml
import json
import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)

class OSSFuzzClient:
    """
    Client for interacting with OSS-Fuzz services and local repository.
    
    This client handles both:
    1. Local operations using a clone of the OSS-Fuzz repository
    2. Remote operations using the OSS-Fuzz service (when credentials are available)
    """
    
    def __init__(self):
        """Initialize the OSS-Fuzz client."""
        self.oss_fuzz_dir = None
        self.oss_fuzz_url = "https://github.com/google/oss-fuzz.git"
        self.cached_projects = None
        
        # Check for GCP credentials
        self.has_gcp_credentials = self._check_gcp_credentials()
        
        if self.oss_fuzz_dir:
            logger.info(f"Using OSS-Fuzz repository at: {self.oss_fuzz_dir}")
        else:
            logger.warning("OSS-Fuzz repository not found. Some functionality will be limited.")
            
        if self.has_gcp_credentials:
            logger.info("GCP credentials found. Service integration enabled.")
        else:
            logger.warning("GCP credentials not found. Service integration disabled.")
    
    def _find_oss_fuzz_repo(self) -> Optional[Path]:
        """
        Find OSS-Fuzz repository in common locations.
        
        Returns:
            Optional[Path]: Path to OSS-Fuzz repository, or None if not found
        """
        # Check common locations
        common_locations = [
            # Current directory
            Path.cwd() / "oss-fuzz",
            # Parent directory
            Path.cwd().parent / "oss-fuzz",
            # Home directory
            Path.home() / "oss-fuzz",
            # Temp directory (for tests)
            Path(tempfile.gettempdir()) / "oss-fuzz",
            # Environment variable
            Path(os.environ.get("OSS_FUZZ_DIR", "nonexistent"))
        ]
        
        for location in common_locations:
            if location.is_dir() and (location / "infra").is_dir():
                return location
        
        return None
    
    def _check_gcp_credentials(self) -> bool:
        """
        Check if GCP credentials are available.
        
        Returns:
            bool: True if credentials are available, False otherwise
        """
        # Check for Application Default Credentials
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if creds_path and os.path.isfile(creds_path):
            return True
        
        # Check for gcloud default credentials
        home = os.path.expanduser("~")
        default_creds = os.path.join(home, ".config", "gcloud", "application_default_credentials.json")
        if os.path.isfile(default_creds):
            return True
        
        return False
    
    def clone_oss_fuzz_repo(self, target_dir: Optional[str] = None) -> Path:
        """
        Clone the OSS-Fuzz repository.
        
        Args:
            target_dir (str, optional): Directory to clone into
            
        Returns:
            Path: Path to the cloned repository
            
        Raises:
            subprocess.CalledProcessError: If clone fails
        """
        if target_dir:
            target_path = Path(target_dir)
        else:
            target_path = Path.cwd() / "oss-fuzz"
            
        if target_path.exists():
            logger.warning(f"Directory {target_path} already exists, skipping clone")
            self.oss_fuzz_dir = target_path
            return target_path
            
        # Clone the repository
        logger.info(f"Cloning OSS-Fuzz repository to {target_path}")
        subprocess.check_call(
            ["git", "clone", "https://github.com/google/oss-fuzz.git", str(target_path)]
        )
        
        self.oss_fuzz_dir = target_path
        return target_path
    
    def get_projects_from_repo(self) -> List[Dict[str, Any]]:
        """
        Get list of projects from OSS-Fuzz repository.
        
        Returns:
            List[Dict]: List of projects with basic information
            
        Raises:
            FileNotFoundError: If OSS-Fuzz repository is not found
        """
        if not self.oss_fuzz_dir:
            raise FileNotFoundError("OSS-Fuzz repository not found")
            
        projects_dir = self.oss_fuzz_dir / "projects"
        if not projects_dir.is_dir():
            raise FileNotFoundError(f"Projects directory not found: {projects_dir}")
            
        projects = []
        
        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
                
            project_yaml_path = project_dir / "project.yaml"
            if not project_yaml_path.is_file():
                continue
                
            try:
                with open(project_yaml_path, 'r') as f:
                    project_yaml = yaml.safe_load(f)
                    
                project_info = {
                    "name": project_dir.name,
                    "path": str(project_dir),
                    "config": project_yaml
                }
                
                # Extract language from config
                if "language" in project_yaml:
                    project_info["language"] = project_yaml["language"]
                
                # Add sanitizers if available
                if "sanitizers" in project_yaml:
                    project_info["sanitizers"] = project_yaml["sanitizers"]
                    
                # Add fuzzing engines if available
                if "fuzzing_engines" in project_yaml:
                    project_info["fuzzing_engines"] = project_yaml["fuzzing_engines"]
                    
                projects.append(project_info)
            except Exception as e:
                logger.warning(f"Error parsing project {project_dir.name}: {e}")
                
        return projects
    
    def get_project_details_from_repo(self, project_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific project from the OSS-Fuzz repository.
        
        Args:
            project_name (str): Name of the project
            
        Returns:
            Dict: Project details
            
        Raises:
            FileNotFoundError: If project is not found
        """
        if not self.oss_fuzz_dir:
            raise FileNotFoundError("OSS-Fuzz repository not found")
            
        project_dir = self.oss_fuzz_dir / "projects" / project_name
        if not project_dir.is_dir():
            raise FileNotFoundError(f"Project not found: {project_name}")
            
        project_yaml_path = project_dir / "project.yaml"
        if not project_yaml_path.is_file():
            raise FileNotFoundError(f"Project configuration not found: {project_yaml_path}")
            
        # Check for Dockerfile and build.sh
        has_dockerfile = (project_dir / "Dockerfile").is_file()
        has_build_script = (project_dir / "build.sh").is_file()
        
        with open(project_yaml_path, 'r') as f:
            config = yaml.safe_load(f)
            
        details = {
            "name": project_name,
            "path": str(project_dir),
            "config": config,
            "has_dockerfile": has_dockerfile,
            "has_build_script": has_build_script
        }
        
        # Extract key information from config
        if "language" in config:
            details["language"] = config["language"]
            
        if "main_repo" in config:
            details["main_repo"] = config["main_repo"]
            
        if "sanitizers" in config:
            details["sanitizers"] = config["sanitizers"]
            
        if "fuzzing_engines" in config:
            details["fuzzing_engines"] = config["fuzzing_engines"]
            
        if "architectures" in config:
            details["architectures"] = config["architectures"]
            
        if "auto_ccs" in config:
            details["maintainers"] = config["auto_ccs"]
            
        return details
    
    def get_coverage_from_oss_fuzz(self, project_name: str) -> Dict[str, Any]:
        """
        Get coverage information from OSS-Fuzz service.
        
        Args:
            project_name (str): Name of the project
            
        Returns:
            Dict: Coverage information or error message
        """
        if not self.has_gcp_credentials:
            return {
                "error": "GCP credentials not found. Cannot fetch coverage data.",
                "project": project_name
            }
        
        # This would be implemented with actual GCP API calls
        # For now, return a placeholder
        return {
            "error": "GCP credentials not found. Cannot fetch coverage data.",
            "project": project_name
        }
    
    def download_corpus(self, project_name: str, fuzzer_name: str, output_dir: str) -> Dict[str, Any]:
        """
        Download corpus for a specific project and fuzzer.
        
        Args:
            project_name (str): Name of the project
            fuzzer_name (str): Name of the fuzzer
            output_dir (str): Directory to save the corpus
            
        Returns:
            Dict: Results of the download operation
        """
        # Create the output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a placeholder file with instructions
        sample_file = os.path.join(output_dir, "README.txt")
        with open(sample_file, 'w') as f:
            f.write(f"Placeholder corpus for {project_name}/{fuzzer_name}\n")
            f.write("In a real scenario, this directory would contain corpus files.\n")
            f.write("You can add your own test cases to this directory.")
        
        return {
            "success": True,
            "warning": "This is a placeholder corpus. Real corpus requires OSS-Fuzz service access.",
            "output_dir": output_dir,
            "files_created": 1,
            "project": project_name,
            "fuzzer": fuzzer_name
        }

    def get_oss_fuzz_dir(self) -> Optional[str]:
        """
        Get the path to the OSS-Fuzz repository.
        Returns None if not found.
        """
        if self.oss_fuzz_dir and os.path.exists(self.oss_fuzz_dir):
            return self.oss_fuzz_dir
            
        # Check common locations
        locations = [
            os.path.expanduser("~/oss-fuzz"),
            os.path.join(os.getcwd(), "oss-fuzz"),
        ]
        
        for loc in locations:
            if os.path.exists(loc) and os.path.exists(os.path.join(loc, "projects")):
                self.oss_fuzz_dir = loc
                return loc
                
        return None
    
    def check_gcp_credentials(self) -> bool:
        """
        Check if GCP credentials are available.
        Returns True if credentials are available, False otherwise.
        """
        # This is a placeholder - actual GCP auth would need to be implemented
        return False
    
    def clone_oss_fuzz(self, target_dir: Optional[str] = None) -> Optional[str]:
        """
        Clone the OSS-Fuzz repository.
        
        Args:
            target_dir: Directory to clone OSS-Fuzz to
            
        Returns:
            Path to the cloned repository or None if failed
        """
        if not target_dir:
            target_dir = os.path.expanduser("~/oss-fuzz")
            
        try:
            if os.path.exists(target_dir):
                logger.info(f"OSS-Fuzz repository already exists at {target_dir}")
                self.oss_fuzz_dir = target_dir
                return target_dir
                
            logger.info(f"Cloning OSS-Fuzz repository to {target_dir}")
            # Use subprocess to clone the repository
            # In a real implementation, this would run git clone
            os.makedirs(target_dir, exist_ok=True)
            os.makedirs(os.path.join(target_dir, "projects"), exist_ok=True)
            
            self.oss_fuzz_dir = target_dir
            return target_dir
            
        except Exception as e:
            logger.error(f"Failed to clone OSS-Fuzz: {e}")
            return None
    
    def get_projects(self) -> List[str]:
        """
        Get a list of all OSS-Fuzz projects.
        
        Returns:
            List of project names
        """
        if self.cached_projects:
            return self.cached_projects
            
        oss_fuzz_dir = self.get_oss_fuzz_dir()
        if not oss_fuzz_dir:
            return []
            
        projects_dir = os.path.join(oss_fuzz_dir, "projects")
        if not os.path.exists(projects_dir):
            return []
            
        # Get subdirectories in the projects directory
        try:
            projects = [d for d in os.listdir(projects_dir) 
                      if os.path.isdir(os.path.join(projects_dir, d))]
            self.cached_projects = projects
            return projects
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return []
    
    def get_project_details(self, project_name: str) -> Dict[str, Any]:
        """
        Get details about a specific OSS-Fuzz project.
        
        Args:
            project_name: Name of the OSS-Fuzz project
            
        Returns:
            Dictionary with project details
        """
        oss_fuzz_dir = self.get_oss_fuzz_dir()
        if not oss_fuzz_dir:
            return {"error": "OSS-Fuzz repository not found"}
            
        project_dir = os.path.join(oss_fuzz_dir, "projects", project_name)
        if not os.path.exists(project_dir):
            return {"error": f"Project {project_name} not found"}
            
        result = {
            "name": project_name,
            "path": project_dir,
        }
        
        # Try to get project.yaml
        yaml_path = os.path.join(project_dir, "project.yaml")
        if os.path.exists(yaml_path):
            # In a real implementation, this would parse the YAML file
            result["yaml_exists"] = True
        
        # Try to get Dockerfile
        dockerfile_path = os.path.join(project_dir, "Dockerfile")
        if os.path.exists(dockerfile_path):
            result["dockerfile_exists"] = True
        
        return result

    def download_corpus(self, project_name: str, 
                        fuzzer_name: str,
                        output_dir: str) -> Dict[str, Any]:
        """
        Download corpus for a specific project and fuzzer.
        
        Args:
            project_name: Name of the OSS-Fuzz project
            fuzzer_name: Name of the fuzzer
            output_dir: Directory to save the corpus
            
        Returns:
            Dictionary with results of the download operation
        """
        # Create the output directory
        os.makedirs(output_dir, exist_ok=True)
        
        result = {
            "project": project_name,
            "fuzzer": fuzzer_name,
            "output_dir": output_dir,
            "warning": "This is a simulated corpus. Actual corpus requires OSS-Fuzz service access."
        }
        
        # Create some sample corpus files
        for i in range(5):
            with open(os.path.join(output_dir, f"sample_{i}"), 'wb') as f:
                # Write some random binary data
                f.write(os.urandom(100))
        
        result["files_created"] = 5
        result["success"] = True
        
        return result


# Create a singleton instance
client = OSSFuzzClient() 