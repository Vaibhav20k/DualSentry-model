#!/usr/bin/env python3
"""
DualSentry Automated Test Suite Runner.
Executes all Python, Go, and Frontend verification test suites.
"""
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def run_command(cmd, cwd, description):
    print(f"\n========================================================")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"Directory: {cwd}")
    print(f"========================================================")
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if result.returncode != 0:
        print(f"\n[FAILED] {description} exited with code {result.returncode}")
        return False
    print(f"[PASSED] {description}")
    return True


def main():
    success = True

    # 1. Python ML Engine tests
    success = success and run_command(
        f'"{sys.executable}" -m pytest -v',
        cwd=ROOT_DIR / "ml-anomaly-engine",
        description="Python ML Anomaly Engine Unit & Integration Tests"
    )

    # 2. Go Ingestion Gateway tests
    success = success and run_command(
        "go test -v ./...",
        cwd=ROOT_DIR / "ingestion-gateway",
        description="Go Ingestion Gateway Tests"
    )

    # 3. Go Transaction Simulator tests
    success = success and run_command(
        "go test -v ./...",
        cwd=ROOT_DIR / "transaction-simulator",
        description="Go Transaction Simulator Tests"
    )

    # 4. Frontend Dashboard Build & Typecheck
    success = success and run_command(
        "npm run build",
        cwd=ROOT_DIR / "fraud-dashboard",
        description="Frontend TypeScript & Vite Production Build"
    )

    if success:
        print("\n[SUCCESS] ALL DUALSENTRY TEST SUITES PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n[ERROR] SOME TESTS FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()
