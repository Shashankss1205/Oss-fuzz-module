#!/usr/bin/env python3
"""
Basic usage examples for OSS-Fuzz API.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add parent directory to path to import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ossfuzz_api import (
    get_projects,
    get_project_details,
    get_coverage,
    get_crash_reports,
    submit_fuzz_job,
    get_fuzz_status,
    get_fuzz_results,
    run_local_fuzzing
)


def example_project_info():
    """Example of retrieving project information."""
    print("\n=== Project Information Examples ===\n")
    
    # Get all projects
    projects = get_projects()
    print(f"OSS-Fuzz is currently fuzzing {len(projects)} projects")
    
    # Get projects filtered by language
    cpp_projects = get_projects(language="c++")
    print(f"There are {len(cpp_projects)} C++ projects")
    
    # Get details for a specific project (using curl as an example)
    try:
        project_name = "curl" if not projects else projects[0]["name"]
        details = get_project_details(project_name)
        
        print(f"\nDetails for project {project_name}:")
        print(f"  Language: {details.get('config', {}).get('language', 'unknown')}")
        print(f"  Has Dockerfile: {details.get('has_dockerfile', False)}")
        print(f"  Has build script: {details.get('has_build_script', False)}")
        
        # Print build system if available
        if "build_system" in details:
            print(f"  Build system: {details['build_system']}")
        
        # Print detected fuzz targets if available
        if "fuzz_targets" in details and details["fuzz_targets"]:
            print(f"  Detected fuzz targets: {', '.join(details['fuzz_targets'])}")
    except Exception as e:
        print(f"Error getting project details: {e}")


def example_historical_results():
    """Example of retrieving historical fuzzing results."""
    print("\n=== Historical Results Examples ===\n")
    
    # Use curl as example (it's guaranteed to be in OSS-Fuzz)
    project_name = "curl"
    
    # Set date range for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"Note: Without OSS-Fuzz access, these examples will return placeholder data.")
    
    # Get coverage data
    try:
        coverage = get_coverage(
            project_name=project_name,
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"\nCoverage information for {project_name}:")
        if "warning" in coverage:
            print(f"  Warning: {coverage['warning']}")
        if "example_url" in coverage:
            print(f"  Coverage report URL: {coverage['example_url']}")
        
        print(f"  Overall coverage: {coverage.get('overall_coverage', 0)}%")
        
        # Show sample daily data if available
        if "daily_coverage" in coverage and coverage["daily_coverage"]:
            sample_day = coverage["daily_coverage"][0]
            print(f"  Sample day ({sample_day['date']}): {sample_day.get('overall_coverage', 0)}% coverage")
    except Exception as e:
        print(f"Error getting coverage: {e}")
    
    # Get crash reports
    try:
        crashes = get_crash_reports(
            project_name=project_name,
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"\nCrash information for {project_name}:")
        if "warning" in crashes:
            print(f"  Warning: {crashes['warning']}")
        print(f"  Total crashes: {crashes.get('total_crashes', 0)}")
        print(f"  Unique crashes: {crashes.get('unique_crashes', 0)}")
    except Exception as e:
        print(f"Error getting crash reports: {e}")


def example_custom_fuzzing():
    """Example of submitting and monitoring custom fuzzing jobs."""
    print("\n=== Custom Fuzzing Examples ===\n")
    
    # Use curl as example project and a common fuzzer
    project_name = "curl"
    fuzz_target = "curl_fuzzer"
    
    try:
        # Get project details to check if it exists
        project_details = get_project_details(project_name)
        
        # Submit a fuzzing job (which will return instructions for local execution)
        job = submit_fuzz_job(
            project_name=project_name,
            fuzz_target=fuzz_target,
            duration_hours=1,
            cpu_resources=2,
            memory_mb=2048
        )
        
        print(f"\nFuzzing job information:")
        print(f"  Job ID: {job.get('job_id', 'unknown')}")
        print(f"  Status: {job.get('status', 'unknown')}")
        
        if "note" in job:
            print(f"  Note: {job['note']}")
        
        if "local_command" in job:
            print(f"\nTo run this fuzzer locally, use:")
            print(f"  {job['local_command']}")
        
        # Note: In a real application, you might want to actually run the fuzzer
        # but for this example we'll just print the command
        print("\nFor a short test run, you could use:")
        print(f"  run_local_fuzzing('{project_name}', '{fuzz_target}', duration_minutes=1)")
    except FileNotFoundError:
        print(f"Project {project_name} not found in OSS-Fuzz. Try running with a different project.")
    except Exception as e:
        print(f"Error in custom fuzzing example: {e}")


def main():
    """Run all examples."""
    print("OSS-Fuzz API Examples\n")
    print("Note: This module works with a local clone of the OSS-Fuzz repository.")
    print("      Some features require actual OSS-Fuzz service access and will return placeholder data.")
    
    try:
        example_project_info()
        example_historical_results()
        example_custom_fuzzing()
    except Exception as e:
        print(f"Error: {e}")
        
    print("\nExamples completed.")


if __name__ == "__main__":
    main() 