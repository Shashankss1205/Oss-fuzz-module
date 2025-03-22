# OSS-Fuzz API Directory Structure

This document explains the structure and purpose of files in the OSS-Fuzz API Python module.

## Root Directory Structure

```
/ossfuzz_api/
├── examples/                # Example scripts demonstrating usage
├── ossfuzz_api/             # Main package source code
├── ossfuzz_api.egg-info/    # Package metadata (generated during installation)
├── README.md                # Project overview and usage instructions
├── setup.py                 # Package installation configuration
├── pyproject.toml           # Project build system requirements
└── test_install.sh          # Shell script to verify installation
```

## Main Package Structure

```
/ossfuzz_api/ossfuzz_api/
├── __init__.py              # Package initialization and exports
├── README.md                # Internal module documentation
├── custom_fuzzing/          # Custom fuzzing API module
├── historical_results/      # Historical results API module
├── project_info/            # Project information API module
└── utils/                   # Utility functions and shared code
```

## Detailed File Descriptions

### Root Directory

- **examples/** - Contains example scripts demonstrating how to use the OSS-Fuzz API:
  - `basic_usage.py` - Shows basic functionality across all modules
  - `curl_fuzzing.py` - Detailed example focused on fuzzing the curl project

- **README.md** - Main documentation explaining the module's features, installation instructions, and usage examples.

- **setup.py** - Defines package metadata, dependencies, and installation configuration for pip. Specifies required packages like `pyyaml`, `google-api-python-client`, etc.

- **pyproject.toml** - Modern Python project configuration defining build system requirements and dependencies.

- **test_install.sh** - Shell script that tests the installation by importing and running basic functions.

### Main Package Modules

#### `ossfuzz_api/ossfuzz_api/__init__.py`

Exports the main API functions, making them directly accessible when importing the package. Defines the package version and public interface.

#### Project Information Module (`project_info/`)

```
/ossfuzz_api/ossfuzz_api/project_info/
├── __init__.py              # Module exports
└── api.py                   # Implementation of project information APIs
```

- **api.py** - Implements:
  - `get_projects()` - Returns list of all OSS-Fuzz projects with optional filtering
  - `get_project_details()` - Returns detailed information about a specific project
  - `get_project_stats()` - Returns statistics for a project (coverage, bugs, etc.)
  - `get_project_builds()` - Returns build status information for a project

#### Historical Results Module (`historical_results/`)

```
/ossfuzz_api/ossfuzz_api/historical_results/
├── __init__.py              # Module exports
└── api.py                   # Implementation of historical results APIs
```

- **api.py** - Implements:
  - `get_coverage()` - Returns coverage data for a project over a specified time period
  - `get_crash_reports()` - Returns crash report data with filtering options
  - `get_coverage_report()` - Returns detailed coverage report for a specific date
  - `download_corpus()` - Downloads fuzzing corpus for a specific project and fuzzer

#### Custom Fuzzing Module (`custom_fuzzing/`)

```
/ossfuzz_api/ossfuzz_api/custom_fuzzing/
├── __init__.py              # Module exports
└── api.py                   # Implementation of custom fuzzing APIs
```

- **api.py** - Implements:
  - `submit_fuzz_job()` - Creates and configures a fuzzing job
  - `get_fuzz_status()` - Checks the status of a running fuzzing job
  - `get_fuzz_results()` - Retrieves results from a completed fuzzing job
  - `cancel_fuzz_job()` - Cancels a running fuzzing job
  - `run_local_fuzzing()` - Executes a fuzzing job locally (blocking)
  - `wait_for_job_completion()` - Waits for a job to complete and returns results

#### Utilities Module (`utils/`)

```
/ossfuzz_api/ossfuzz_api/utils/
├── __init__.py              # Module exports
├── client.py                # Client for interacting with OSS-Fuzz services
└── common.py                # Shared utility functions
```

- **client.py** - Implements the `OSSFuzzClient` class that:
  - Handles interaction with the local OSS-Fuzz repository
  - Provides methods for the real OSS-Fuzz service when credentials are available
  - Manages both local and remote operations transparently

- **common.py** - Contains shared utility functions:
  - `validate_project_name()` - Validates project name format
  - `validate_date_range()` - Validates and normalizes date ranges
  - `format_date()` - Standardizes date formats for API calls

## Usage Flow

1. **Project Discovery**: Use `project_info` module to discover projects and their details
2. **Historical Analysis**: Use `historical_results` module to analyze coverage and crashes
3. **Custom Fuzzing**: Use `custom_fuzzing` module to run your own fuzzing jobs
4. **Local Development**: Works with a local clone of OSS-Fuzz repository
5. **Service Integration**: When GCP credentials are available, interacts with actual OSS-Fuzz infrastructure

## Extension Points

To extend this module, you can:

1. Add new methods to the existing API modules
2. Create new modules for additional functionality
3. Enhance the client implementation in `utils/client.py` to support more OSS-Fuzz service features
4. Add more examples in the `examples/` directory

## Dependencies

The module has several dependencies:
- PyYAML: For parsing project configuration files
- Google API Client: For interacting with Google Cloud services
- Google Cloud Storage: For downloading and uploading artifacts
- Pandas: For data manipulation and formatting
- TQDM: For progress indicators in long-running operations 