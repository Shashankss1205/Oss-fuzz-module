#!/usr/bin/env python3
"""
OSS-Fuzz API Example - Curl Fuzzing

This example demonstrates how to use the OSS-Fuzz API to:
1. Get information about the curl project
2. Retrieve coverage data
3. Download the corpus
4. Run a local fuzzing job
"""

import os
import sys
import logging
import datetime
from pathlib import Path

# Add parent directory to path if running directly
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ossfuzz_module.project_info import list_projects, get_project_details, get_fuzz_targets
from ossfuzz_module.historical_results import get_coverage, get_coverage_report, download_corpus
from ossfuzz_module.custom_fuzzing import setup_local_fuzzing, run_local_fuzzing, analyze_fuzzing_results

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("curl_fuzzing_example")

# Project configuration
PROJECT_NAME = "curl"
FUZZ_TARGET = "curl_fuzzer"
DURATION_MINUTES = 2

def main():
    """
    Main function demonstrating the OSS-Fuzz API workflow for the curl project.
    """
    logger.info(f"Starting OSS-Fuzz API example for {PROJECT_NAME}")
    
    # Check if curl is in the list of available projects
    projects = list_projects()
    if PROJECT_NAME not in projects:
        logger.error(f"Project {PROJECT_NAME} not found in OSS-Fuzz.")
        logger.info(f"Available projects: {', '.join(projects[:5])}...")
        sys.exit(1)
    
    # Step 1: Get project details
    logger.info(f"Getting project details for {PROJECT_NAME}")
    project_details = get_project_details(PROJECT_NAME)
    logger.info(f"Project details: {project_details}")
    
    # Step 2: Check for available fuzz targets
    logger.info(f"Getting fuzz targets for {PROJECT_NAME}")
    targets_info = get_fuzz_targets(PROJECT_NAME)
    logger.info(f"Available targets: {targets_info.get('fuzz_targets', [])}")
    
    # Confirm the fuzz target exists or use the first available one
    available_targets = targets_info.get('fuzz_targets', [])
    if not available_targets:
        logger.error(f"No fuzz targets found for {PROJECT_NAME}")
        sys.exit(1)
        
    target_to_use = FUZZ_TARGET
    if FUZZ_TARGET not in available_targets:
        target_to_use = available_targets[0]
        logger.warning(f"Specified target {FUZZ_TARGET} not found, using {target_to_use} instead")
    
    # Step 3: Get coverage information
    logger.info(f"Getting coverage information for {PROJECT_NAME}")
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=30)
    
    try:
        coverage = get_coverage(
            PROJECT_NAME,
            start_date=start_date,
            end_date=end_date
        )
        logger.info(f"Overall coverage: {coverage.get('overall_coverage', 'N/A')}%")
        logger.info(f"Line coverage: {coverage.get('line_coverage', 'N/A')}%")
        logger.info(f"Function coverage: {coverage.get('function_coverage', 'N/A')}%")
    except Exception as e:
        logger.warning(f"Warning: Could not get coverage information: {e}")
    
    # Step 4: Get coverage report URL
    try:
        report = get_coverage_report(PROJECT_NAME)
        logger.info(f"Coverage report available at: {report.get('report_url', 'N/A')}")
    except Exception as e:
        logger.warning(f"Warning: Could not get coverage report: {e}")
    
    # Step 5: Download corpus
    corpus_dir = os.path.join(os.getcwd(), f"{PROJECT_NAME}_corpus")
    logger.info(f"Downloading corpus for {target_to_use} to {corpus_dir}")
    
    try:
        corpus_result = download_corpus(PROJECT_NAME, target_to_use, corpus_dir)
        logger.info(f"Corpus downloaded: {corpus_result.get('files_created', 0)} files")
    except Exception as e:
        logger.warning(f"Warning: Could not download corpus: {e}")
        # Create the directory anyway for the next steps
        os.makedirs(corpus_dir, exist_ok=True)
    
    # Step 6: Set up local fuzzing
    logger.info(f"Setting up local fuzzing for {PROJECT_NAME} with target {target_to_use}")
    fuzzing_dir = os.path.join(os.getcwd(), f"{PROJECT_NAME}_fuzzing")
    
    try:
        setup_result = setup_local_fuzzing(
            PROJECT_NAME,
            fuzz_target=target_to_use,
            output_dir=fuzzing_dir
        )
        
        if not setup_result.get('success', False):
            logger.error(f"Failed to set up local fuzzing: {setup_result.get('error', 'Unknown error')}")
            sys.exit(1)
            
        logger.info(f"Local fuzzing setup successful")
        logger.info(f"Fuzz target path: {setup_result.get('fuzz_target_path')}")
        
        # Step 7: Run local fuzzing (optional, ask user first)
        run_fuzzing = input(f"Do you want to run {target_to_use} for {DURATION_MINUTES} minutes? (y/n): ")
        
        if run_fuzzing.lower() == 'y':
            logger.info(f"Running local fuzzing for {DURATION_MINUTES} minutes")
            output_dir = os.path.join(os.getcwd(), f"{PROJECT_NAME}_fuzzing_output")
            
            fuzzing_result = run_local_fuzzing(
                PROJECT_NAME,
                fuzz_target=setup_result.get('fuzz_target_path'),
                corpus_dir=corpus_dir,
                duration=DURATION_MINUTES * 60,  # Convert to seconds
                output_dir=output_dir
            )
            
            logger.info(f"Fuzzing completed with {fuzzing_result.get('executions', 0)} executions")
            logger.info(f"Crashes found: {fuzzing_result.get('crashes', 0)}")
            
            # Step 8: Analyze results
            analysis = analyze_fuzzing_results(output_dir)
            logger.info(f"Analysis results: {analysis}")
            
    except Exception as e:
        logger.error(f"Error during fuzzing setup/execution: {e}")
        sys.exit(1)
    
    logger.info("OSS-Fuzz API example completed successfully")

if __name__ == "__main__":
    main() 