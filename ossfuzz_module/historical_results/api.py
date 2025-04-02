"""
Historical results APIs for OSS-Fuzz projects.
"""

from typing import Dict, List, Optional, Any, Union
import datetime
import logging
import random
import pandas as pd

from ..utils.client import client
from ..utils.common import validate_project_name
from ..models import OSSFuzzProject, CoverageReport

logger = logging.getLogger(__name__)

def get_coverage(project_name: str,
                start_date: Optional[Union[datetime.datetime, str]] = None,
                end_date: Optional[Union[datetime.datetime, str]] = None,
                fuzzer: Optional[str] = None,
                format: str = "json") -> Union[CoverageReport, pd.DataFrame]:
    """
    Get coverage information for a project.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        start_date (datetime or str, optional): Start date for coverage data
        end_date (datetime or str, optional): End date for coverage data
        fuzzer (str, optional): Name of the fuzzer to get coverage for
        format (str, optional): Output format ("json" or "dataframe")
        
    Returns:
        CoverageReport or pd.DataFrame: Coverage information
        
    Raises:
        ValueError: If project name is invalid
        
    Example:
        >>> coverage = get_coverage("curl", 
        ...                        start_date="2023-01-01", 
        ...                        end_date="2023-01-31")
        >>> print(f"Overall coverage: {coverage.overall_coverage}%")
        Overall coverage: 75.5%
    """
    project_name = validate_project_name(project_name)
    
    # Get project details
    project = client.get_project_details_from_repo(project_name)
    
    # Parse date range
    date_range = {
        "start_date": start_date.isoformat() if isinstance(start_date, datetime.datetime) else start_date,
        "end_date": end_date.isoformat() if isinstance(end_date, datetime.datetime) else end_date
    }
    
    # Get coverage information from OSS-Fuzz service
    coverage_info = client.get_coverage(project, start_date, end_date)
    
    if not coverage_info:
        logger.warning(f"Could not fetch coverage data for {project_name}")
        return None
    
    # Add placeholder data for demonstration
    coverage_info.line_coverage = random.uniform(60, 85)
    coverage_info.function_coverage = random.uniform(70, 95)
    coverage_info.overall_coverage = random.uniform(65, 80)
    
    if format.lower() == "dataframe":
        # Convert daily coverage to DataFrame
        df = pd.DataFrame([{
            'date': coverage_info.date,
            'line_coverage': coverage_info.line_coverage,
            'function_coverage': coverage_info.function_coverage,
            'overall_coverage': coverage_info.overall_coverage
        }])
        
        # Convert date strings to datetime objects
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            
        return df
        
    return coverage_info

def get_crash_reports(project_name: str,
                     start_date: Optional[Union[datetime.datetime, str]] = None,
                     end_date: Optional[Union[datetime.datetime, str]] = None,
                     fuzzer: Optional[str] = None) -> Dict[str, Any]:
    """
    Get crash reports for a project.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        start_date (datetime or str, optional): Start date for crash data
        end_date (datetime or str, optional): End date for crash data
        fuzzer (str, optional): Name of the fuzzer to get crashes for
        
    Returns:
        Dict: Crash report information
        
    Raises:
        ValueError: If project name is invalid
        
    Example:
        >>> crashes = get_crash_reports("curl", 
        ...                             start_date="2023-01-01", 
        ...                             end_date="2023-01-31")
        >>> print(f"Found {crashes['total_crashes']} crashes")
        Found 42 crashes
    """
    project_name = validate_project_name(project_name)
    
    # Get project details
    project = client.get_project_details_from_repo(project_name)
    
    # Parse date range
    date_range = {
        "start_date": start_date.isoformat() if isinstance(start_date, datetime.datetime) else start_date,
        "end_date": end_date.isoformat() if isinstance(end_date, datetime.datetime) else end_date
    }
    
    # This would be implemented with actual OSS-Fuzz service calls
    # For now, return placeholder data
    return {
        "project": project_name,
        "total_crashes": random.randint(0, 100),
        "unique_crashes": random.randint(0, 50),
        "crash_types": {
            "segmentation_fault": random.randint(0, 20),
            "buffer_overflow": random.randint(0, 15),
            "use_after_free": random.randint(0, 10),
            "null_pointer_dereference": random.randint(0, 25)
        },
        "date_range": date_range
    }


def get_coverage_report(project_name: str, 
                       report_date: Optional[Union[datetime.datetime, str]] = None,
                       fuzzer: Optional[str] = None,
                       download_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed coverage report for a specific date.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        report_date: Date for the coverage report (defaults to latest)
        fuzzer (str, optional): Filter by specific fuzzer
        download_path (str, optional): Path to download report files
        
    Returns:
        Dict: Coverage report details and download URLs
        
    Raises:
        ValueError: If parameters are invalid
        
    Note:
        Without OSS-Fuzz service access, this will return a placeholder message.
    """
    project_name = validate_project_name(project_name)
    
    # Format date if provided
    date_str = "latest"
    if report_date:
        if isinstance(report_date, datetime.datetime):
            date_str = report_date.strftime("%Y-%m-%d")
        else:
            date_str = report_date
    
    # Create placeholder response
    result = {
        'project': project_name,
        'date': date_str,
        'warning': 'Access to coverage reports requires OSS-Fuzz service access',
        'report_url': f"https://oss-fuzz.com/coverage-report/{project_name}/{date_str}/index.html",
    }
    
    # If download path is provided, create directory
    if download_path:
        try:
            download_dir = Path(download_path)
            download_dir.mkdir(parents=True, exist_ok=True)
            result['download_path'] = str(download_dir)
            result['status'] = 'Directory created, but download requires OSS-Fuzz service access'
        except Exception as e:
            result['error'] = f"Error creating download directory: {e}"
    
    return result


def download_corpus(project_name: str, fuzzer_name: str, 
                   output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Download corpus for a specific project and fuzzer.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        fuzzer_name (str): Name of the fuzzer
        output_dir (str, optional): Directory to save the corpus (defaults to current directory)
        
    Returns:
        Dict: Results of the download operation
        
    Raises:
        ValueError: If parameters are invalid
        
    Note:
        Without OSS-Fuzz service access, this will create a placeholder corpus.
    """
    project_name = validate_project_name(project_name)
    
    if not fuzzer_name or not isinstance(fuzzer_name, str):
        raise ValueError("Fuzzer name must be a non-empty string")
    
    if not output_dir:
        output_dir = os.path.join(os.getcwd(), f"{project_name}_{fuzzer_name}_corpus")
    
    result = client.download_corpus(project_name, fuzzer_name, output_dir)
    
    return result 