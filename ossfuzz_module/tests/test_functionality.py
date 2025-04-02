"""
Test script for OSS-Fuzz module functionality.
"""

import os
import sys
import unittest
import tempfile
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import ossfuzz_module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ossfuzz_module.project_info.api import (
    list_projects,
    get_project_details,
    get_fuzz_targets,
    check_project_exists,
    get_projects
)
from ossfuzz_module.custom_fuzzing.api import (
    setup_local_fuzzing,
    run_local_fuzzing,
    analyze_fuzzing_results,
    collect_coverage
)
from ossfuzz_module.historical_results.api import (
    get_coverage,
    get_crash_reports,
    get_coverage_report,
    download_corpus
)
from ossfuzz_module.models import OSSFuzzProject, FuzzTarget, FuzzingExecution, CoverageReport
from ossfuzz_module.utils.client import client

class TestOSSFuzzFunctionality(unittest.TestCase):
    """Test suite for OSS-Fuzz module functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Create temporary directory for test outputs
        cls.test_dir = Path(tempfile.mkdtemp())
        print(f"\nTest directory: {cls.test_dir}")
        
        # Clone OSS-Fuzz repository
        cls.oss_fuzz_dir = cls.test_dir / "oss-fuzz"
        print("\nCloning OSS-Fuzz repository...")
        try:
            subprocess.run(
                ["git", "clone", "https://github.com/google/oss-fuzz.git", str(cls.oss_fuzz_dir)],
                check=True,
                capture_output=True
            )
            # Set environment variable for OSS-Fuzz directory
            os.environ["OSS_FUZZ_DIR"] = str(cls.oss_fuzz_dir)
            print("OSS-Fuzz repository cloned successfully")
            
            # Reinitialize client with new environment variable
            client.oss_fuzz_dir = str(cls.oss_fuzz_dir)
            
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to clone OSS-Fuzz repository: {e}")
            print("Some tests may be skipped")
        
        # Use curl as a test project
        cls.test_project = "curl"
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up each test."""
        if not os.environ.get("OSS_FUZZ_DIR"):
            self.skipTest("OSS-Fuzz repository not available")
    
    def test_project_info(self):
        """Test project information functionality."""
        print("\nTesting project information...")
        
        # Test listing projects
        projects = list_projects()
        self.assertIsInstance(projects, list)
        self.assertTrue(len(projects) > 0)
        print(f"Found {len(projects)} projects")
        
        # Test getting project details
        project = get_project_details(self.test_project)
        self.assertIsInstance(project, OSSFuzzProject)
        self.assertEqual(project.name, self.test_project)
        print(f"Project details: {project.name} ({project.language})")
        
        # Test checking project existence
        exists = check_project_exists(self.test_project)
        self.assertTrue(exists)
        exists = check_project_exists("nonexistent_project")
        self.assertFalse(exists)
        
        # Test getting fuzz targets
        targets = get_fuzz_targets(self.test_project)
        self.assertIsInstance(targets, list)
        self.assertTrue(len(targets) > 0)
        self.assertIsInstance(targets[0], FuzzTarget)
        print(f"Found {len(targets)} fuzz targets")
        
        # Test filtering projects
        cpp_projects = get_projects(language="c++")
        self.assertIsInstance(cpp_projects, list)
        print(f"Found {len(cpp_projects)} C++ projects")
    
    def test_custom_fuzzing(self):
        """Test custom fuzzing functionality."""
        print("\nTesting custom fuzzing...")
        
        # Create necessary directories
        corpus_dir = self.test_dir / "corpus"
        corpus_dir.mkdir(parents=True, exist_ok=True)
        
        # Test setting up fuzzing environment
        execution = setup_local_fuzzing(
            self.test_project,
            output_dir=str(self.test_dir / "fuzzing_setup")
        )
        self.assertIsInstance(execution, FuzzingExecution)
        self.assertEqual(execution.project.name, self.test_project)
        print(f"Setup completed: {execution.status}")
        
        # Test running fuzzing
        execution = run_local_fuzzing(
            self.test_project,
            fuzz_target="curl_fuzzer",
            corpus_dir=str(corpus_dir),
            duration=5,
            output_dir=str(self.test_dir / "fuzzing_output")
        )
        self.assertIsInstance(execution, FuzzingExecution)
        self.assertEqual(execution.status, "completed")
        print(f"Fuzzing completed: {execution.executions} executions")
        
        # Test analyzing results
        results = analyze_fuzzing_results(str(self.test_dir / "fuzzing_output"))
        self.assertIsInstance(results, dict)
        self.assertTrue(results.get('success', False))
        print(f"Analysis complete: {results.get('executions', 0)} executions")
        
        # Test collecting coverage
        coverage = collect_coverage(
            self.test_project,
            fuzz_target=str(self.test_dir / "fuzzing_output" / "curl_fuzzer"),
            corpus_dir=str(corpus_dir),
            output_dir=str(self.test_dir / "coverage")
        )
        self.assertIsInstance(coverage, dict)
        self.assertTrue(coverage.get('success', False))
        print(f"Coverage collected: {coverage.get('line_coverage', 0)}% line coverage")
    
    def test_historical_results(self):
        """Test historical results functionality."""
        print("\nTesting historical results...")
        
        # Test getting coverage
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        coverage = get_coverage(
            self.test_project,
            start_date=start_date,
            end_date=end_date
        )
        self.assertIsInstance(coverage, CoverageReport)
        print(f"Coverage: {coverage.overall_coverage}%")
        
        # Test getting crash reports
        crashes = get_crash_reports(
            self.test_project,
            start_date=start_date,
            end_date=end_date
        )
        self.assertIsInstance(crashes, dict)
        print(f"Crashes: {crashes.get('total_crashes', 0)} total")
        
        # Test getting coverage report
        report = get_coverage_report(
            self.test_project,
            report_date=end_date,
            download_path=str(self.test_dir / "coverage_report")
        )
        self.assertIsInstance(report, dict)
        print(f"Report URL: {report.get('report_url', 'N/A')}")
        
        # Test downloading corpus
        corpus = download_corpus(
            self.test_project,
            fuzzer_name="curl_fuzzer",
            output_dir=str(self.test_dir / "corpus")
        )
        self.assertIsInstance(corpus, dict)
        self.assertTrue(corpus.get('success', False))
        print(f"Corpus downloaded: {corpus.get('files_created', 0)} files")

if __name__ == '__main__':
    unittest.main(verbosity=2) 