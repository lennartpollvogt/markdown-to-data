#!/usr/bin/env python3
"""
Test runner script for the update_dependencies module tests.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run the tests for the update_dependencies script."""
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Path to the test file
    test_file = project_root / "tests" / "test_update_dependencies.py"
    
    if not test_file.exists():
        print(f"Error: Test file not found at {test_file}")
        sys.exit(1)
    
    print("Running tests for update_dependencies script...")
    print(f"Test file: {test_file}")
    print("-" * 50)
    
    try:
        # Run pytest on the specific test file
        result = subprocess.run(
            ["python", "-m", "pytest", str(test_file), "-v", "--tb=short"],
            cwd=project_root,
            check=False
        )
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with exit code {result.returncode}")
            sys.exit(result.returncode)
            
    except FileNotFoundError:
        print("Error: pytest not found. Make sure pytest is installed.")
        print("Install with: uv add --dev pytest")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()