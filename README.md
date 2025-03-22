# OSS-Fuzz API Module

A Python interface for interacting with OSS-Fuzz services and running custom fuzzing jobs.

## Features

- **Project Information**: Get details about OSS-Fuzz projects, including available fuzz targets
- **Historical Results**: Access coverage reports, crash data, and fuzzing metrics
- **Custom Fuzzing**: Set up and run local fuzzing jobs using OSS-Fuzz infrastructure

## Installation

```bash
pip install ossfuzz_module
```

## Examples

### Getting Project Information

```python
from ossfuzz_module.project_info import list_projects, get_project_details, get_fuzz_targets

# List all available projects
projects = list_projects()
print(f"Found {len(projects)} projects in OSS-Fuzz")

# Get details about a specific project
project_details = get_project_details("curl")
print(f"Project: {project_details['name']}")

# Get available fuzz targets
targets = get_fuzz_targets("curl")
print(f"Available fuzz targets: {targets['fuzz_targets']}")
```

### Accessing Historical Results

```python
from ossfuzz_module.historical_results import get_coverage, get_crash_reports
import datetime

# Get coverage information
coverage = get_coverage("curl", 
                       start_date="2023-01-01", 
                       end_date="2023-01-31")
print(f"Overall coverage: {coverage['overall_coverage']}%")

# Get crash reports
crashes = get_crash_reports("curl", 
                          start_date=datetime.datetime(2023, 1, 1),
                          end_date=datetime.datetime(2023, 1, 31))
print(f"Found {crashes['total_crashes']} crashes")
```

### Running Custom Fuzzing

```python
from ossfuzz_module.custom_fuzzing import setup_local_fuzzing, run_local_fuzzing, analyze_fuzzing_results

# Set up the environment for local fuzzing
setup = setup_local_fuzzing("curl", fuzz_target="curl_fuzzer")
print(f"Setup completed: {setup['success']}")

# Run the fuzzer
results = run_local_fuzzing("curl", 
                           fuzz_target=setup['fuzz_target_path'], 
                           duration=300)
print(f"Fuzzing completed with {results['executions']} executions")

# Analyze the results
analysis = analyze_fuzzing_results(results['output_dir'])
print(f"Found {analysis.get('crash_count', 0)} crashes")
```

## Requirements

- Python 3.8+
- `requests`
- `pandas`
- `pyyaml`

## Development

```bash
# Clone the repository
git clone https://github.com/example/ossfuzz_module.git
cd ossfuzz_module

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

Apache License 2.0 