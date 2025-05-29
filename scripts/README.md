# Dependency Update Script

This directory contains utility scripts for the `markdown-to-data` project.

## `update_dependencies.py`

A utility script to check for new versions of dependencies and update them using the `uv` package manager.

### Features

- Checks both main and development dependencies from `pyproject.toml`
- Compares installed versions with latest available versions
- Provides a clear version comparison (current → latest)
- Interactive prompt to select which dependencies to update
- Uses `uv` for faster dependency installation

### Usage

Run the script from the project root:

```bash
python scripts/update_dependencies.py
```

### Commands

- `/Y` - Update all dependencies with new versions available
- `/N` - Cancel and exit without updating
- Space-separated dependency names - Update only specified dependencies

### Requirements

- Python 3.10+
- `uv` package manager installed and available in PATH

### Example Output

```
Checking main dependencies:
- package1: 1.0.0 -> 1.1.0
- package2: 2.0.0 (up to date)

Checking development dependencies:
- pytest: 7.0.0 -> 7.1.0
- rich: 12.0.0 -> 12.1.0

Found updates for the following dependencies:
- package1: 1.0.0 -> 1.1.0
- pytest: 7.0.0 -> 7.1.0
- rich: 12.0.0 -> 12.1.0

Update dependencies? [/Y = all, /N = none, or specify space-separated names]: pytest rich
Updating pytest to 7.1.0...
✅ Successfully updated pytest to 7.1.0
Updating rich to 12.1.0...
✅ Successfully updated rich to 12.1.0
```

## `run_tests.py`

A test runner script for the dependency update functionality.

### Features

- Runs comprehensive unit tests for the `update_dependencies.py` script
- Tests all core functions with mocked external dependencies
- Provides clear pass/fail feedback
- Uses pytest for test execution

### Usage

Run the tests from the project root:

```bash
python scripts/run_tests.py
```

Or run tests directly with pytest:

```bash
uv run python -m pytest tests/test_update_dependencies.py -v
```

### Test Coverage

The test suite covers:

- **TOML parsing**: Loading and parsing `pyproject.toml` files
- **Dependency extraction**: Extracting main and dev dependencies
- **Version checking**: Getting installed and latest versions (mocked)
- **Dependency parsing**: Handling various dependency string formats
- **Update logic**: Testing the update workflow with mocked subprocess calls
- **Error handling**: Network failures, missing packages, subprocess errors
- **Integration tests**: End-to-end workflow testing

### Test Structure

- `TestLoadPyprojectToml`: TOML file loading and parsing
- `TestGetProjectDependencies`: Dependency extraction from project data
- `TestParseDependency`: Parsing various dependency string formats
- `TestGetInstalledVersion`: Getting installed package versions
- `TestGetLatestVersion`: Fetching latest versions from PyPI
- `TestCheckForUpdates`: Update checking logic
- `TestUpdateDependencies`: Dependency update functionality
- `TestIntegration`: End-to-end workflow tests

All external calls (subprocess, HTTP requests) are mocked to ensure fast, reliable tests that don't depend on external services.