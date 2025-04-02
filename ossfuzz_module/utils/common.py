"""
Common utility functions for the OSS-Fuzz API.
"""

import datetime
import re
from typing import Dict, Optional, Union

def validate_project_name(project_name: str) -> str:
    """
    Validate and normalize the project name.
    
    Args:
        project_name: Name of the OSS-Fuzz project
        
    Returns:
        Normalized project name
        
    Raises:
        ValueError: If project name is invalid
    """
    if not project_name:
        raise ValueError("Project name cannot be empty")
        
    # Remove leading/trailing whitespace and convert to lowercase
    project_name = project_name.strip().lower()
    
    # Check for invalid characters
    if not re.match(r'^[a-z0-9_-]+$', project_name):
        raise ValueError("Project name can only contain lowercase letters, numbers, underscores, and hyphens")
        
    return project_name


def validate_date_range(start_date: Optional[Union[datetime.datetime, str]] = None,
                        end_date: Optional[Union[datetime.datetime, str]] = None) -> Dict[str, str]:
    """
    Validate and normalize date range parameters.
    
    Args:
        start_date: Start date (datetime object or ISO format string)
        end_date: End date (datetime object or ISO format string)
        
    Returns:
        Dictionary with normalized start_date and end_date as ISO format strings
        
    Raises:
        ValueError: If date range is invalid
    """
    # Default to last 30 days if no dates provided
    if not start_date and not end_date:
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=30)
        
    # If only end_date is provided, set start_date to 30 days before
    if not start_date and end_date:
        if isinstance(end_date, str):
            end_date_obj = datetime.datetime.fromisoformat(end_date)
        else:
            end_date_obj = end_date
            
        start_date = end_date_obj - datetime.timedelta(days=30)
        
    # If only start_date is provided, set end_date to today
    if start_date and not end_date:
        end_date = datetime.datetime.now()
        
    # Convert to datetime objects if strings
    if isinstance(start_date, str):
        try:
            start_date = datetime.datetime.fromisoformat(start_date)
        except ValueError:
            raise ValueError(f"Invalid start_date format: {start_date}. Use ISO format (YYYY-MM-DD).")
            
    if isinstance(end_date, str):
        try:
            end_date = datetime.datetime.fromisoformat(end_date)
        except ValueError:
            raise ValueError(f"Invalid end_date format: {end_date}. Use ISO format (YYYY-MM-DD).")
            
    # Validate date range
    if start_date > end_date:
        raise ValueError("start_date cannot be after end_date")
        
    # Convert to ISO format strings
    return {
        "start_date": start_date.isoformat().split('T')[0],
        "end_date": end_date.isoformat().split('T')[0]
    }


def validate_fuzz_target(fuzz_target: str) -> str:
    """
    Validate the fuzz target name.
    
    Args:
        fuzz_target: Name of the fuzz target
        
    Returns:
        Normalized fuzz target name
        
    Raises:
        ValueError: If fuzz target name is invalid
    """
    if not fuzz_target:
        raise ValueError("Fuzz target name cannot be empty")
        
    # Remove leading/trailing whitespace
    fuzz_target = fuzz_target.strip()
    
    # Check for invalid characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', fuzz_target):
        raise ValueError("Fuzz target name can only contain letters, numbers, underscores, and hyphens")
        
    return fuzz_target


def format_datetime(dt: Union[datetime.datetime, str]) -> str:
    """
    Format a datetime object or string as a consistent string.
    
    Args:
        dt: Datetime object or string
        
    Returns:
        Formatted datetime string
    """
    if isinstance(dt, str):
        try:
            dt = datetime.datetime.fromisoformat(dt)
        except ValueError:
            return dt  # Return as is if we can't parse
            
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_date(date: Union[datetime.datetime, str]) -> str:
    """
    Format a date to ISO format string.
    
    Args:
        date (datetime or str): Date to format
        
    Returns:
        str: Formatted date string
        
    Raises:
        ValueError: If date is invalid
    """
    if isinstance(date, str):
        try:
            date = datetime.datetime.fromisoformat(date)
        except ValueError:
            raise ValueError("Invalid date format. Use ISO format (YYYY-MM-DD)")
    elif not isinstance(date, datetime.datetime):
        raise ValueError("Date must be a datetime object or ISO format string")
        
    return date.isoformat() 