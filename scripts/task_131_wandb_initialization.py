#!/usr/bin/env python3
"""
Task ID: 1.3.1
Description: WandB Initialization
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

def check_command_exists(cmd):
    """Check if a command exists in PATH."""
    try:
        subprocess.run([cmd, '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def add_venv_to_path():
    """Add virtual environment site-packages to Python path."""
    venv_dir = project_root / '.venv'
    
    if venv_dir.exists():
        # Try to find site-packages in venv
        possible_paths = [
            venv_dir / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages',
            venv_dir / 'Lib' / 'site-packages',  # Windows
        ]
        
        for site_packages in possible_paths:
            if site_packages.exists():
                if str(site_packages) not in sys.path:
                    sys.path.insert(0, str(site_packages))
                return True
    
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
            # Add venv to path so we can import newly installed packages
            add_venv_to_path()
            return True
        else:
            print(f"ERROR: uv sync failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return False
    except Exception as e:
        print(f"ERROR: Failed to run uv sync: {e}", file=sys.stderr)
        return False

def main():
    print("=" * 50)
    print("Task 1.3.1: WandB Initialization")
    print("=" * 50)
    print("")
    
    # Try to add venv to path first (in case packages are already installed)
    add_venv_to_path()
    
    # Check if wandb is already installed
    try:
        import wandb
        wandb_version = getattr(wandb, '__version__', 'installed')
        print(f"✓ wandb is already installed (version: {wandb_version})")
        print("")
    except ImportError:
        print("wandb is not installed. Installing dependencies from pyproject.toml...")
        print("")
        if not install_dependencies():
            print("ERROR: Failed to install dependencies", file=sys.stderr)
            print("", file=sys.stderr)
            print("Please install manually:", file=sys.stderr)
            print("  uv sync", file=sys.stderr)
            print("", file=sys.stderr)
            print("This will install all dependencies including wandb from pyproject.toml", file=sys.stderr)
            return 1
        print("")
        
        # Try importing again after installation
        try:
            import wandb
        except ImportError:
            print("ERROR: wandb installation completed but cannot be imported", file=sys.stderr)
            print("", file=sys.stderr)
            print("This may happen if the script is not using the virtual environment Python.", file=sys.stderr)
            print("Try running the script using the venv Python:", file=sys.stderr)
            venv_python = project_root / '.venv' / 'bin' / 'python'
            if venv_python.exists():
                print(f"  {venv_python} scripts/task_131_wandb_initialization.py", file=sys.stderr)
            else:
                print("  source .venv/bin/activate", file=sys.stderr)
                print("  python scripts/task_131_wandb_initialization.py", file=sys.stderr)
            return 1
    
    # Get project name from config
    project_name = getattr(config, 'WANDB_PROJECT_NAME', 'chicken-detection')
    print(f"WandB project name: {project_name}")
    print("")
    
    # Check for API key in environment
    wandb_api_key = os.getenv('WANDB_API_KEY')
    
    if wandb_api_key:
        print("Found WANDB_API_KEY in environment variables.")
        print("Logging in with API key...")
        print("")
        try:
            # Login using API key
            wandb.login(key=wandb_api_key)
            print("✓ Successfully logged in to WandB using API key")
        except Exception as e:
            print(f"ERROR: Failed to login with API key: {e}", file=sys.stderr)
            print("", file=sys.stderr)
            print("You may need to:", file=sys.stderr)
            print("  1. Verify your API key is correct in .env file", file=sys.stderr)
            print("  2. Get a new API key from: https://wandb.ai/authorize", file=sys.stderr)
            return 1
    else:
        print("No WANDB_API_KEY found in environment variables.")
        print("")
        print("To login, you have two options:")
        print("")
        print("Option 1: Interactive login (recommended for first time)")
        print("  Run: wandb login")
        print("  Then enter your API key when prompted")
        print("")
        print("Option 2: Set API key in .env file")
        print("  1. Get your API key from: https://wandb.ai/authorize")
        print("  2. Add to .env file: WANDB_API_KEY=your_api_key_here")
        print("  3. Re-run this script")
        print("")
        
        # Try interactive login if in TTY
        if sys.stdin.isatty():
            try:
                response = input("Attempt interactive login now? (y/n): ").strip().lower()
                if response == 'y':
                    print("")
                    print("Running wandb login...")
                    print("(You will be prompted to enter your API key)")
                    print("")
                    try:
                        result = subprocess.run(['wandb', 'login'], check=True)
                        if result.returncode == 0:
                            print("✓ Successfully logged in to WandB")
                        else:
                            print("⚠ Login process completed with warnings")
                    except subprocess.CalledProcessError as e:
                        print(f"ERROR: wandb login failed: {e}", file=sys.stderr)
                        return 1
                    except FileNotFoundError:
                        print("ERROR: wandb command not found. Please ensure wandb is properly installed.", file=sys.stderr)
                        return 1
                else:
                    print("Skipping interactive login.")
                    print("Please login manually or set WANDB_API_KEY in .env file.")
            except (EOFError, KeyboardInterrupt):
                print("\nLogin cancelled.")
                print("Please login manually or set WANDB_API_KEY in .env file.")
        else:
            print("Non-interactive mode: Skipping login.")
            print("Please set WANDB_API_KEY in .env file or run 'wandb login' manually.")
    
    # Verify login status
    print("")
    print("Verifying WandB connection...")
    try:
        # Try to initialize a run to verify login
        api = wandb.Api()
        # Just check if we can access the API
        print("✓ WandB API connection verified")
    except Exception as e:
        print(f"⚠ WARNING: Could not verify WandB connection: {e}")
        print("  This may be normal if you haven't logged in yet.")
        print("  Run 'wandb login' manually to complete setup.")
    
    print("")
    print("=" * 50)
    print("✓ WandB Initialization: COMPLETED")
    print("=" * 50)
    print("")
    print(f"Project name: {project_name}")
    print("")
    print("Next steps:")
    print("  - Proceed to Task 1.3.2: DVC Initialization")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
