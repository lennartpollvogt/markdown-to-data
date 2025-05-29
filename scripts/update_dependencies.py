#!/usr/bin/env python3
"""
Script to check for new versions of dependencies and update them using 'uv'.
"""

import sys
import subprocess
import json
import urllib.request
import urllib.error
from pathlib import Path
import tomllib
from typing import Dict, List, Tuple, Optional


def load_pyproject_toml(path: Path) -> Dict:
    """Load and parse the pyproject.toml file."""
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        print(f"Error loading pyproject.toml: {e}")
        sys.exit(1)


def get_project_dependencies(pyproject: Dict) -> Tuple[List[str], Dict[str, List[str]]]:
    """Extract dependencies from pyproject.toml."""
    main_deps = pyproject.get("project", {}).get("dependencies", [])

    dev_deps = {}
    for group_name, deps in pyproject.get("dependency-groups", {}).items():
        if deps:
            dev_deps[group_name] = deps

    return main_deps, dev_deps


def get_installed_version(dependency: str) -> Optional[str]:
    """Get the installed version of a dependency."""
    try:
        # First try with uv pip show
        result = subprocess.run(
            ["uv", "pip", "show", dependency],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()

        # If uv pip show fails, try regular pip
        result = subprocess.run(
            ["pip", "show", dependency],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()

        return None
    except Exception:
        return None


def get_latest_version(dependency: str) -> Optional[str]:
    """Get the latest version of a dependency from PyPI."""
    package_name = dependency.split("[")[0].split(">=")[0].split("==")[0].strip()
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get("info", {}).get("version")
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, Exception):
        return None


def parse_dependency(dep: str) -> Tuple[str, Optional[str]]:
    """Parse a dependency string to extract name and version constraint."""
    if '>=' in dep:
        name, version = dep.split('>=', 1)
        return name.strip(), f">={version.strip()}"
    elif '==' in dep:
        name, version = dep.split('==', 1)
        return name.strip(), f"=={version.strip()}"
    elif '[' in dep:
        name = dep.split('[', 1)[0].strip()
        return name, dep[len(name):]
    return dep.strip(), None


def check_for_updates(dependencies: List[str]) -> Dict[str, Dict[str, str]]:
    """Check for updates for the given dependencies."""
    updates = {}

    if not dependencies:
        print("No dependencies found.")
        return updates

    print("Checking for updates...")
    for dep in dependencies:
        name, constraint = parse_dependency(dep)
        print(f"Checking {name}...", end=" ")

        installed_version = get_installed_version(name)
        if not installed_version:
            print("Not installed")
            continue

        latest_version = get_latest_version(name)
        if not latest_version:
            print("Failed to fetch latest version from PyPI")
            continue

        if installed_version != latest_version:
            print(f"{installed_version} -> {latest_version} ⬆️")
            updates[name] = {
                "current": installed_version,
                "latest": latest_version,
                "constraint": constraint
            }
        else:
            print(f"{installed_version} ✅")

    return updates


def update_dependencies(dependencies_to_update: Dict[str, Dict[str, str]]) -> None:
    """Update the specified dependencies using uv."""
    if not dependencies_to_update:
        print("No dependencies to update.")
        return

    print(f"\n🔄 Updating {len(dependencies_to_update)} dependencies...")

    for name, info in dependencies_to_update.items():
        constraint = info.get("constraint", "")

        # For uv add, we want to specify the latest version explicitly
        package_spec = f"{name}=={info['latest']}"

        print(f"📦 Updating {name}: {info['current']} -> {info['latest']}...")

        try:
            # Try uv add first
            result = subprocess.run(
                ["uv", "add", "--upgrade", package_spec],
                check=False,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"  ✅ Successfully updated {name}")
            else:
                # If uv add fails, try uv pip install
                print("  ⚠️  uv add failed, trying uv pip install...")
                result = subprocess.run(
                    ["uv", "pip", "install", "--upgrade", package_spec],
                    check=False,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"  ✅ Successfully updated {name}")
                else:
                    print(f"  ❌ Failed to update {name}")
                    if result.stderr:
                        print(f"     Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"  ❌ Error updating {name}: {e}")


def main():
    # Find the pyproject.toml file
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    pyproject_path = project_root / "pyproject.toml"

    if not pyproject_path.exists():
        print(f"Error: pyproject.toml not found at {pyproject_path}")
        sys.exit(1)

    # Load dependencies from pyproject.toml
    pyproject = load_pyproject_toml(pyproject_path)
    main_deps, dev_deps_groups = get_project_dependencies(pyproject)

    # Flatten dev dependencies
    dev_deps = []
    for deps in dev_deps_groups.values():
        dev_deps.extend(deps)

    # Check for updates
    print("🔍 Checking main dependencies:")
    main_updates = check_for_updates(main_deps) if main_deps else {}

    print("\n🔍 Checking development dependencies:")
    dev_updates = check_for_updates(dev_deps) if dev_deps else {}

    all_updates = {**main_updates, **dev_updates}

    if not all_updates:
        print("\n🎉 All dependencies are up to date!")
        return

    # Prompt for which dependencies to update
    print(f"\n📋 Found updates for {len(all_updates)} dependencies:")
    for name, info in all_updates.items():
        print(f"  • {name}: {info['current']} -> {info['latest']}")

    choice = input("\nUpdate dependencies? [/Y = all, /N = none, or specify space-separated names]: ")

    if choice.strip().upper() == "/N":
        print("Update cancelled.")
        return

    dependencies_to_update = {}

    if choice.strip().upper() == "/Y":
        dependencies_to_update = all_updates
    else:
        # Parse user-specified dependencies
        specified_deps = choice.strip().split()
        for dep in specified_deps:
            if dep in all_updates:
                dependencies_to_update[dep] = all_updates[dep]
            else:
                print(f"Warning: {dep} not found in the list of updatable dependencies.")

    if dependencies_to_update:
        update_dependencies(dependencies_to_update)
    else:
        print("No dependencies selected for update.")


if __name__ == "__main__":
    main()
