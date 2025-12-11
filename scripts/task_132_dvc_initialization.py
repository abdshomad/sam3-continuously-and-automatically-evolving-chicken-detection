#!/usr/bin/env python3
"""
Task ID: 1.3.2
Description: DVC Initialization
Created: 2025-12-12
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv is optional

# Import configuration from config.py
try:
    import config
except ImportError:
    print("Error: config.py not found. Please create config.py with required settings.", file=sys.stderr)
    sys.exit(1)

def find_command_in_venv(cmd):
    """Find command in venv, fallback to PATH."""
    venv_dir = project_root / '.venv'
    
    # Check venv bin directory first
    if venv_dir.exists():
        venv_bin = venv_dir / 'bin' / cmd
        venv_scripts = venv_dir / 'Scripts' / f'{cmd}.exe'  # Windows
        if venv_bin.exists():
            return str(venv_bin)
        elif venv_scripts.exists():
            return str(venv_scripts)
    
    # Fallback to PATH
    return cmd

def check_command_exists(cmd):
    """Check if a command exists in PATH or venv."""
    dvc_cmd = find_command_in_venv(cmd)
    try:
        subprocess.run([dvc_cmd, '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_dependencies():
    """Install dependencies using uv sync from pyproject.toml."""
    if not check_command_exists('uv'):
        print("ERROR: uv is not installed or not in PATH", file=sys.stderr)
        print("", file=sys.stderr)
        print("To install uv:", file=sys.stderr)
        print("  curl -LsSf https://astral.sh/uv/install.sh | sh", file=sys.stderr)
        return False
    
    print("Installing dependencies from pyproject.toml using uv sync...")
    print("")
    
    try:
        result = subprocess.run(
            ['uv', 'sync'],
            cwd=str(project_root),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Dependencies installed successfully with uv sync")
            return True
        else:
            print(f"ERROR: uv sync failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return False
    except Exception as e:
        print(f"ERROR: Failed to run uv sync: {e}", file=sys.stderr)
        return False

def is_dvc_initialized():
    """Check if DVC is already initialized in the project."""
    dvc_dir = project_root / '.dvc'
    dvc_config = project_root / '.dvc' / 'config'
    return dvc_dir.exists() and dvc_config.exists()

def main():
    print("=" * 50)
    print("Task 1.3.2: DVC Initialization")
    print("=" * 50)
    print("")
    
    # Check if DVC is already installed
    try:
        import dvc
        dvc_version = getattr(dvc, '__version__', 'installed')
        print(f"✓ dvc is already installed (version: {dvc_version})")
        print("")
    except ImportError:
        print("dvc is not installed. Installing dependencies from pyproject.toml...")
        print("")
        if not install_dependencies():
            print("ERROR: Failed to install dependencies", file=sys.stderr)
            print("", file=sys.stderr)
            print("Please install manually:", file=sys.stderr)
            print("  uv sync", file=sys.stderr)
            print("", file=sys.stderr)
            print("This will install all dependencies including dvc from pyproject.toml", file=sys.stderr)
            return 1
        print("")
    
    # Import dvc (should work now)
    try:
        import dvc
    except ImportError:
        print("ERROR: dvc installation failed or cannot be imported", file=sys.stderr)
        return 1
    
    # Check if DVC is already initialized
    if is_dvc_initialized():
        print("✓ DVC is already initialized in this project")
        print(f"  DVC directory: {project_root / '.dvc'}")
        print("")
        print("DVC configuration:")
        try:
            dvc_cmd = find_command_in_venv('dvc')
            result = subprocess.run(
                [dvc_cmd, 'remote', 'list'],
                cwd=str(project_root),
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                print(result.stdout)
            else:
                print("  No remotes configured yet")
        except Exception:
            pass
        print("")
        print("=" * 50)
        print("✓ DVC Initialization: ALREADY COMPLETE")
        print("=" * 50)
        print("")
        print("Next steps:")
        print("  - Proceed to Task 1.3.3: Configure Remote Storage")
        return 0
    
    # Initialize DVC
    print("Initializing DVC in project root...")
    print(f"  Project root: {project_root}")
    print("")
    
    dvc_cmd = find_command_in_venv('dvc')
    
    try:
        result = subprocess.run(
            [dvc_cmd, 'init'],
            cwd=str(project_root),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ DVC initialized successfully")
            print("")
            
            # Verify initialization
            if is_dvc_initialized():
                print("Verification:")
                print(f"  ✓ .dvc directory created: {project_root / '.dvc'}")
                print(f"  ✓ DVC config file created: {project_root / '.dvc' / 'config'}")
                print("")
            else:
                print("⚠ WARNING: DVC initialization completed but verification failed")
                print("  Please check if .dvc directory and config file exist")
                print("")
        else:
            print(f"ERROR: DVC initialization failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return 1
            
    except FileNotFoundError:
        print("ERROR: dvc command not found", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please ensure dvc is installed:", file=sys.stderr)
        print("  uv sync", file=sys.stderr)
        print("", file=sys.stderr)
        print("Or activate the virtual environment and try again:", file=sys.stderr)
        print("  source .venv/bin/activate", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Failed to initialize DVC: {e}", file=sys.stderr)
        return 1
    
    print("=" * 50)
    print("✓ DVC Initialization: COMPLETED")
    print("=" * 50)
    print("")
    print("DVC has been initialized. The following files were created:")
    print("  - .dvc/ directory (contains DVC configuration)")
    print("  - .dvcignore (similar to .gitignore for DVC)")
    print("")
    print("Next steps:")
    print("  - Configure remote storage (Task 1.3.3)")
    print("  - Add data files to DVC tracking")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
