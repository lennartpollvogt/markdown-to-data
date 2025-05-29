"""
Comprehensive test suite for the update_dependencies script.
"""

import pytest
import json
import subprocess
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
import sys
import os

# Add the scripts directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from update_dependencies import (
    load_pyproject_toml,
    get_project_dependencies,
    parse_dependency,
    get_installed_version,
    get_latest_version,
    check_for_updates,
    update_dependencies
)


class TestLoadPyprojectToml:
    """Test loading and parsing pyproject.toml files."""
    
    def test_load_valid_toml(self, tmp_path):
        """Test loading a valid pyproject.toml file."""
        toml_content = b"""
[project]
name = "test-project"
dependencies = ["requests>=2.0.0"]

[dependency-groups]
dev = ["pytest>=7.0.0"]
"""
        toml_file = tmp_path / "pyproject.toml"
        toml_file.write_bytes(toml_content)
        
        result = load_pyproject_toml(toml_file)
        
        assert result["project"]["name"] == "test-project"
        assert result["project"]["dependencies"] == ["requests>=2.0.0"]
        assert result["dependency-groups"]["dev"] == ["pytest>=7.0.0"]
    
    def test_load_nonexistent_file(self, tmp_path):
        """Test loading a non-existent file exits with error."""
        nonexistent_file = tmp_path / "nonexistent.toml"
        
        with pytest.raises(SystemExit):
            load_pyproject_toml(nonexistent_file)


class TestGetProjectDependencies:
    """Test extraction of dependencies from pyproject data."""
    
    def test_extract_main_dependencies(self):
        """Test extracting main project dependencies."""
        pyproject_data = {
            "project": {
                "dependencies": ["requests>=2.0.0", "click"]
            }
        }
        
        main_deps, dev_deps = get_project_dependencies(pyproject_data)
        
        assert main_deps == ["requests>=2.0.0", "click"]
        assert dev_deps == {}
    
    def test_extract_dev_dependencies(self):
        """Test extracting development dependencies."""
        pyproject_data = {
            "dependency-groups": {
                "dev": ["pytest>=7.0.0", "black"],
                "test": ["coverage"]
            }
        }
        
        main_deps, dev_deps = get_project_dependencies(pyproject_data)
        
        assert main_deps == []
        assert dev_deps == {
            "dev": ["pytest>=7.0.0", "black"],
            "test": ["coverage"]
        }
    
    def test_extract_mixed_dependencies(self):
        """Test extracting both main and dev dependencies."""
        pyproject_data = {
            "project": {
                "dependencies": ["requests"]
            },
            "dependency-groups": {
                "dev": ["pytest"],
                "empty": []  # Empty groups should be filtered out
            }
        }
        
        main_deps, dev_deps = get_project_dependencies(pyproject_data)
        
        assert main_deps == ["requests"]
        assert dev_deps == {"dev": ["pytest"]}  # Empty group filtered out
    
    def test_extract_no_dependencies(self):
        """Test extracting from empty pyproject data."""
        pyproject_data = {}
        
        main_deps, dev_deps = get_project_dependencies(pyproject_data)
        
        assert main_deps == []
        assert dev_deps == {}


class TestParseDependency:
    """Test parsing of dependency strings."""
    
    def test_parse_simple_name(self):
        """Test parsing a simple package name."""
        name, constraint = parse_dependency("requests")
        assert name == "requests"
        assert constraint is None
    
    def test_parse_version_constraint_gte(self):
        """Test parsing with >= version constraint."""
        name, constraint = parse_dependency("requests>=2.0.0")
        assert name == "requests"
        assert constraint == ">=2.0.0"
    
    def test_parse_version_constraint_eq(self):
        """Test parsing with == version constraint."""
        name, constraint = parse_dependency("requests==2.28.1")
        assert name == "requests"
        assert constraint == "==2.28.1"
    
    def test_parse_with_extras(self):
        """Test parsing package with extras."""
        name, constraint = parse_dependency("requests[security]")
        assert name == "requests"
        assert constraint == "[security]"
    
    def test_parse_complex_dependency(self):
        """Test parsing complex dependency with extras and version."""
        name, constraint = parse_dependency("requests[security]>=2.0.0")
        assert name == "requests[security]"
        assert constraint == ">=2.0.0"
    
    def test_parse_with_whitespace(self):
        """Test parsing with whitespace."""
        name, constraint = parse_dependency("  requests >= 2.0.0  ")
        assert name == "requests"
        assert constraint == ">=2.0.0"


class TestGetInstalledVersion:
    """Test getting installed package versions."""
    
    @patch('subprocess.run')
    def test_get_version_uv_success(self, mock_run):
        """Test successful version retrieval with uv pip show."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Name: requests\nVersion: 2.28.1\nSummary: Python HTTP for Humans."
        )
        
        version = get_installed_version("requests")
        
        assert version == "2.28.1"
        mock_run.assert_called_once_with(
            ["uv", "pip", "show", "requests"],
            capture_output=True,
            text=True,
            check=False
        )
    
    @patch('subprocess.run')
    def test_get_version_fallback_to_pip(self, mock_run):
        """Test fallback to regular pip when uv fails."""
        # First call (uv) fails, second call (pip) succeeds
        mock_run.side_effect = [
            Mock(returncode=1, stdout=""),
            Mock(returncode=0, stdout="Name: requests\nVersion: 2.28.1\n")
        ]
        
        version = get_installed_version("requests")
        
        assert version == "2.28.1"
        assert mock_run.call_count == 2
    
    @patch('subprocess.run')
    def test_get_version_not_installed(self, mock_run):
        """Test when package is not installed."""
        mock_run.return_value = Mock(returncode=1, stdout="")
        
        version = get_installed_version("nonexistent-package")
        
        assert version is None
    
    @patch('subprocess.run')
    def test_get_version_exception(self, mock_run):
        """Test handling of subprocess exceptions."""
        mock_run.side_effect = Exception("Command failed")
        
        version = get_installed_version("requests")
        
        assert version is None


class TestGetLatestVersion:
    """Test getting latest package versions from PyPI."""
    
    @patch('urllib.request.urlopen')
    def test_get_latest_version_success(self, mock_urlopen):
        """Test successful version retrieval from PyPI."""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "info": {"version": "2.31.0"}
        }).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        version = get_latest_version("requests")
        
        assert version == "2.31.0"
        mock_urlopen.assert_called_once()
    
    @patch('urllib.request.urlopen')
    def test_get_latest_version_with_extras(self, mock_urlopen):
        """Test version retrieval for package with extras."""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "info": {"version": "2.31.0"}
        }).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        version = get_latest_version("requests[security]")
        
        assert version == "2.31.0"
        # Should call PyPI API with just the package name
        args, _ = mock_urlopen.call_args
        assert "requests/json" in args[0]
        assert "[security]" not in args[0]
    
    @patch('urllib.request.urlopen')
    def test_get_latest_version_with_constraint(self, mock_urlopen):
        """Test version retrieval for package with version constraint."""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "info": {"version": "2.31.0"}
        }).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        version = get_latest_version("requests>=2.0.0")
        
        assert version == "2.31.0"
    
    @patch('urllib.request.urlopen')
    def test_get_latest_version_http_error(self, mock_urlopen):
        """Test handling of HTTP errors."""
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError(None, 404, "Not Found", None, None)
        
        version = get_latest_version("nonexistent-package")
        
        assert version is None
    
    @patch('urllib.request.urlopen')
    def test_get_latest_version_json_error(self, mock_urlopen):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.read.return_value = b"invalid json"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        version = get_latest_version("requests")
        
        assert version is None


class TestCheckForUpdates:
    """Test the update checking functionality."""
    
    @patch('update_dependencies.get_latest_version')
    @patch('update_dependencies.get_installed_version')
    def test_check_updates_available(self, mock_installed, mock_latest):
        """Test finding updates when newer versions are available."""
        mock_installed.side_effect = lambda pkg: {"requests": "2.28.1", "click": "8.0.0"}.get(pkg)
        mock_latest.side_effect = lambda pkg: {"requests": "2.31.0", "click": "8.1.0"}.get(pkg)
        
        dependencies = ["requests>=2.0.0", "click"]
        updates = check_for_updates(dependencies)
        
        assert len(updates) == 2
        assert updates["requests"]["current"] == "2.28.1"
        assert updates["requests"]["latest"] == "2.31.0"
        assert updates["requests"]["constraint"] == ">=2.0.0"
        assert updates["click"]["current"] == "8.0.0"
        assert updates["click"]["latest"] == "8.1.0"
        assert updates["click"]["constraint"] is None
    
    @patch('update_dependencies.get_latest_version')
    @patch('update_dependencies.get_installed_version')
    def test_check_no_updates(self, mock_installed, mock_latest):
        """Test when all packages are up to date."""
        mock_installed.return_value = "2.31.0"
        mock_latest.return_value = "2.31.0"
        
        dependencies = ["requests"]
        updates = check_for_updates(dependencies)
        
        assert len(updates) == 0
    
    @patch('update_dependencies.get_latest_version')
    @patch('update_dependencies.get_installed_version')
    def test_check_not_installed(self, mock_installed, mock_latest):
        """Test handling of packages that are not installed."""
        mock_installed.return_value = None
        mock_latest.return_value = "2.31.0"
        
        dependencies = ["requests"]
        updates = check_for_updates(dependencies)
        
        assert len(updates) == 0
    
    @patch('update_dependencies.get_latest_version')
    @patch('update_dependencies.get_installed_version')
    def test_check_pypi_failure(self, mock_installed, mock_latest):
        """Test handling of PyPI API failures."""
        mock_installed.return_value = "2.28.1"
        mock_latest.return_value = None
        
        dependencies = ["requests"]
        updates = check_for_updates(dependencies)
        
        assert len(updates) == 0
    
    def test_check_empty_dependencies(self):
        """Test with empty dependency list."""
        updates = check_for_updates([])
        assert len(updates) == 0


class TestUpdateDependencies:
    """Test the dependency update functionality."""
    
    @patch('subprocess.run')
    def test_update_success(self, mock_run):
        """Test successful dependency update."""
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        updates = {
            "requests": {
                "current": "2.28.1",
                "latest": "2.31.0",
                "constraint": ">=2.0.0"
            }
        }
        
        update_dependencies(updates)
        
        mock_run.assert_called_once_with(
            ["uv", "add", "--upgrade", "requests==2.31.0"],
            check=False,
            capture_output=True,
            text=True
        )
    
    @patch('subprocess.run')
    def test_update_fallback_to_pip(self, mock_run):
        """Test fallback to uv pip install when uv add fails."""
        # First call (uv add) fails, second call (uv pip install) succeeds
        mock_run.side_effect = [
            Mock(returncode=1, stderr="uv add failed"),
            Mock(returncode=0, stderr="")
        ]
        
        updates = {
            "requests": {
                "current": "2.28.1",
                "latest": "2.31.0",
                "constraint": None
            }
        }
        
        update_dependencies(updates)
        
        assert mock_run.call_count == 2
        # Check second call used uv pip install
        second_call_args = mock_run.call_args_list[1][0][0]
        assert second_call_args == ["uv", "pip", "install", "--upgrade", "requests==2.31.0"]
    
    @patch('subprocess.run')
    def test_update_complete_failure(self, mock_run):
        """Test when both uv add and uv pip install fail."""
        mock_run.return_value = Mock(returncode=1, stderr="Installation failed")
        
        updates = {
            "requests": {
                "current": "2.28.1",
                "latest": "2.31.0",
                "constraint": None
            }
        }
        
        # Should not raise an exception, just print error messages
        update_dependencies(updates)
        
        assert mock_run.call_count == 2
    
    def test_update_empty_dict(self):
        """Test with empty updates dictionary."""
        # Should not raise an exception
        update_dependencies({})
    
    @patch('subprocess.run')
    def test_update_exception_handling(self, mock_run):
        """Test handling of subprocess exceptions."""
        mock_run.side_effect = Exception("Subprocess failed")
        
        updates = {
            "requests": {
                "current": "2.28.1",
                "latest": "2.31.0",
                "constraint": None
            }
        }
        
        # Should not raise an exception
        update_dependencies(updates)


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_dependency_parsing_integration(self):
        """Test the complete dependency parsing workflow."""
        pyproject_data = {
            "project": {
                "dependencies": ["requests>=2.0.0", "click[colorama]"]
            },
            "dependency-groups": {
                "dev": ["pytest==7.0.0", "black"]
            }
        }
        
        main_deps, dev_deps_groups = get_project_dependencies(pyproject_data)
        
        # Test main dependencies parsing
        for dep in main_deps:
            name, constraint = parse_dependency(dep)
            assert name in ["requests", "click"]
            if name == "requests":
                assert constraint == ">=2.0.0"
            elif name == "click":
                assert constraint == "[colorama]"
        
        # Test dev dependencies parsing
        dev_deps = []
        for deps in dev_deps_groups.values():
            dev_deps.extend(deps)
        
        for dep in dev_deps:
            name, constraint = parse_dependency(dep)
            assert name in ["pytest", "black"]
            if name == "pytest":
                assert constraint == "==7.0.0"


if __name__ == "__main__":
    pytest.main([__file__])