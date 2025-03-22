"""
Historical fuzzing results APIs for OSS-Fuzz projects.
"""

from typing import Dict, List, Optional, Any, Union
import datetime
import os
import logging
import pandas as pd
from pathlib import Path
import random

from ..utils.client import client
from ..utils.common import validate_project_name, validate_date_range

logger = logging.getLogger(__name__)

def get_coverage(project_name: str,
                start_date: Optional[Union[datetime.datetime, str]] = None,
                end_date: Optional[Union[datetime.datetime, str]] = None,
                fuzzer: Optional[str] = None,
                format: str = "json") -> Union[Dict[str, Any], pd.DataFrame]:
    """
    Get coverage reports for a specific project and date range.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        start_date: Start date for coverage reports (optional)
        end_date: End date for coverage reports (optional)
        fuzzer (str, optional): Filter by specific fuzzer
        format (str, optional): Return format, 'json' or 'dataframe'
        
    Returns:
        Union[Dict, pd.DataFrame]: Coverage data in requested format
        
    Raises:
        ValueError: If parameters are invalid
        
    Note:
        Without OSS-Fuzz service access, this will return a placeholder message.
        
    Example:
        >>> get_coverage("curl", 
        ...             start_date="2023-01-01", 
        ...             end_date="2023-01-31")
        {
            'overall_coverage': 76.5,
            'line_coverage': 82.1,
            'function_coverage': 89.3,
            'daily_coverage': [...],
            'fuzzers': {...}
        }
    """
    project_name = validate_project_name(project_name)
    date_range = validate_date_range(start_date, end_date)
    
    # Get coverage information from OSS-Fuzz
    coverage_info = client.get_coverage_from_oss_fuzz(project_name)
    
    # Add placeholder data for demonstration
    placeholder_data = {
        'overall_coverage': 0,
        'line_coverage': 0,
        'function_coverage': 0,
        'daily_coverage': []
    }
    
    # Generate sample daily coverage data
    start = datetime.datetime.fromisoformat(date_range["start_date"])
    end = datetime.datetime.fromisoformat(date_range["end_date"])
    delta = end - start
    
    if delta.days > 0:
        # Generate random coverage data for demonstration
        for i in range(delta.days + 1):
            day = start + datetime.timedelta(days=i)
            placeholder_data['daily_coverage'].append({
                'date': day.strftime("%Y-%m-%d"),
                'line_coverage': random.uniform(60, 85),
                'function_coverage': random.uniform(70, 95),
                'overall_coverage': random.uniform(65, 80)
            })
    
    result = {**coverage_info, **placeholder_data}
    
    if format.lower() == "dataframe" and "daily_coverage" in result:
        # Convert daily coverage to DataFrame
        df = pd.DataFrame(result["daily_coverage"])
        
        # Convert date strings to datetime objects
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            
        return df
        
    return result


def get_crash_reports(project_name: str,
                     start_date: Optional[Union[datetime.datetime, str]] = None,
                     end_date: Optional[Union[datetime.datetime, str]] = None,
                     fuzzer: Optional[str] = None,
                     status: Optional[str] = None,
                     format: str = "json") -> Union[Dict[str, Any], pd.DataFrame]:
    """
    Get crash reports for a specific project and date range.
    
    Args:
        project_name (str): Name of the OSS-Fuzz project
        start_date: Start date for crash reports (optional)
        end_date: End date for crash reports (optional)
        fuzzer (str, optional): Filter by specific fuzzer
        status (str, optional): Filter by status (e.g., "new", "fixed", "verified")
        format (str, optional): Return format, 'json' or 'dataframe'
        
    Returns:
        Union[Dict, pd.DataFrame]: Crash reports data in requested format
        
    Raises:
        ValueError: If parameters are invalid
        
    Note:
        Without OSS-Fuzz service access, this will return a placeholder message.
        
    Example:
        >>> get_crash_reports("curl", 
        ...                  start_date="2023-01-01", 
        ...                  end_date="2023-01-31")
        {
            'total_crashes': 5,
            'unique_crashes': 3,
            'crashes': [
                {
                    'id': 'crash-12345',
                    'fuzzer': 'url_fuzzer',
                    'date': '2023-01-15',
                    'type': 'heap-buffer-overflow',
                    'status': 'verified',
                    ...
                },
                ...
            ]
        }
    """
    project_name = validate_project_name(project_name)
    date_range = validate_date_range(start_date, end_date)
    
    # Add placeholder data for demonstration
    placeholder_data = {
        'total_crashes': 0,
        'unique_crashes': 0,
        'crashes': [],
        'warning': 'Access to real crash data requires OSS-Fuzz service access',
        'project': project_name,
    }
    
    if format.lower() == "dataframe":
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=[
            'id', 'fuzzer', 'date', 'type', 'status', 'fixed', 'summary'
        ])
        
    return placeholder_data


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