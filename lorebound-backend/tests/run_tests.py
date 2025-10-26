#!/usr/bin/env python3
"""Test runner script for LoreBound backend tests."""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run LoreBound backend tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--auth", action="store_true", help="Run auth tests only")
    parser.add_argument("--health", action="store_true", help="Run health tests only")
    parser.add_argument("--content", action="store_true", help="Run content tests only")
    parser.add_argument("--endpoints", action="store_true", help="Run endpoint tests only")
    parser.add_argument("--file", type=str, help="Run specific test file")
    parser.add_argument("--test", type=str, help="Run specific test")
    parser.add_argument("--html-cov", action="store_true", help="Generate HTML coverage report")
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["poetry", "run", "pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing"])
        if args.html_cov:
            cmd.append("--cov-report=html")
    
    # Test selection
    if args.fast:
        cmd.extend(["-m", "not slow"])
    elif args.integration:
        cmd.append("tests/test_integration.py")
    elif args.security:
        cmd.extend(["-k", "security"])
    elif args.auth:
        cmd.append("tests/test_auth.py")
    elif args.health:
        cmd.append("tests/test_health.py")
    elif args.content:
        cmd.append("tests/test_content.py")
    elif args.endpoints:
        cmd.append("tests/test_endpoints.py")
    elif args.file:
        cmd.append(f"tests/{args.file}")
    elif args.test:
        cmd.extend(["-k", args.test])
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    
    print("=" * 60)
    print("🧪 Running LoreBound Backend Tests")
    print("=" * 60)
    
    # Run tests
    success = run_command(cmd, cwd=backend_dir)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
        if args.html_cov:
            print("\n📊 HTML coverage report generated in htmlcov/index.html")
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
