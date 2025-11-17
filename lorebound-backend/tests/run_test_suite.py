#!/usr/bin/env python3
"""Test runner for the comprehensive test suite."""

import sys
import subprocess
from pathlib import Path


def run_tests(category: str = None, verbose: bool = True, coverage: bool = False):
    """Run tests with optional category filtering."""
    base_dir = Path(__file__).parent.parent
    
    cmd = ["python", "-m", "pytest"]
    
    if category:
        if category == "unit":
            cmd.extend(["-m", "unit"])
        elif category == "integration":
            cmd.extend(["-m", "integration"])
        elif category == "api":
            cmd.extend(["-m", "api"])
        elif category == "service":
            cmd.extend(["-m", "service"])
        elif category == "legacy":
            cmd.extend(["tests/legacy/"])
        else:
            print(f"Unknown category: {category}")
            print("Available categories: unit, integration, api, service, legacy")
            return 1
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    cmd.append("tests/")
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=base_dir)
    return result.returncode


if __name__ == "__main__":
    category = None
    coverage = False
    
    if len(sys.argv) > 1:
        category = sys.argv[1]
    
    if "--coverage" in sys.argv or "-c" in sys.argv:
        coverage = True
    
    exit_code = run_tests(category=category, coverage=coverage)
    sys.exit(exit_code)

