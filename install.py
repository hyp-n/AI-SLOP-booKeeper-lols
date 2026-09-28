#!/usr/bin/env python3
"""
booKeeper — cross-platform one-liner installer.
Works on Windows, macOS, and Linux.

Usage:
  curl -fsSL https://raw.githubusercontent.com/yourrepo/booKeeper/main/install.py | python3
  or: python3 install.py
"""

import os
import sys
import subprocess
import platform
import shutil
import json

def run(cmd, cwd=None, shell=False):
    """Run a command and stream output."""
    print(f"  > {cmd}")
    result = subprocess.run(cmd, cwd=cwd, shell=shell)
    if result.returncode != 0:
        print(f"  ERROR: Command failed with exit code {result.returncode}")
        sys.exit(1)

def check_command(name):
    """Check if a command exists, return its path or None."""
    return shutil.which(name)

def main():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(repo_dir)

    print("===============================================")
    print("  booKeeper — Installation")
    print("===============================================")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Dir: {repo_dir}")
    print()

    # --- 1. Check dependencies ---
    print("[1/5] Checking dependencies...")

    python = check_command("python3") or check_command("python")
    if not python:
        print("  ERROR: python3 is required but not installed.")
        print("  Install it from https://www.python.org/downloads/")
        sys.exit(1)

    node = check_command("node")
    if not node:
        print("  ERROR: node is required but not installed.")
        print("  Install it from https://nodejs.org/")
        sys.exit(1)

    npm = check_command("npm")
    if not npm:
        print("  ERROR: npm is required but not installed.")
        sys.exit(1)

    # Check MongoDB
    mongo = check_command("mongod") or check_command("mongo")
    if not mongo:
        print("  WARNING: MongoDB not found in PATH.")
        print("  You'll need MongoDB running locally or a MongoDB Atlas URI.")
        print("  Local install: https://www.mongodb.com/try/download/community")
        print("  Atlas (cloud): https://www.mongodb.com/atlas")
    else:
        print(f"  mongodb: {mongo}")

    print(f"  python: {python}")
    print(f"  node:   {node}")
    print(f"  npm:    {npm}")
    print()

    # --- 2. Install Python dependencies ---
    print("[2/5] Installing Python dependencies...")
    run([python, "-m", "pip", "install", "-r", "backend/requirements.txt"])
    print()

    # --- 3. Install & build frontend ---
    print("[3/5] Installing frontend dependencies...")
    run([npm, "install"], cwd="frontend")
    print()

    print("[4/5] Building frontend...")
    run([npm, "run", "build"], cwd="frontend")
    print()

    # --- 5. Done ---
    print("===============================================")
    print("  Installation complete!")
    print("===============================================")
    print()
    print("  IMPORTANT: Start MongoDB before running the app!")
    print("  macOS:  brew services start mongodb-community")
    print("  Linux:  sudo systemctl start mongod")
    print("  Windows: net start MongoDB")
    print("  Or set MONGODB_URI in backend/.env to a MongoDB Atlas URI")
    print()
    print("  Start the app:")
    print(f"    cd backend && {python} run.py")
    print()
    print("  Then open: http://localhost:5000")
    print()
    print("  For development (hot-reload):")
    print(f"    Terminal 1: cd backend && {python} run.py")
    print(f"    Terminal 2: cd frontend && {npm} run dev")
    print("    Open: http://localhost:5173")
    print()

if __name__ == "__main__":
    main()
