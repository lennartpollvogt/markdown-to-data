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