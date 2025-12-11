#!/usr/bin/env python3
"""
Task ID: 1.3.3
Description: Configure Remote Storage
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

def is_dvc_initialized():
    """Check if DVC is already initialized in the project."""
    dvc_dir = project_root / '.dvc'
    dvc_config = project_root / '.dvc' / 'config'
    return dvc_dir.exists() and dvc_config.exists()

def get_remote_storage_url():
    """Get remote storage URL from config or environment."""
    # Try environment variable first
    storage_url = os.getenv('DVC_REMOTE_STORAGE_URL')
    
    # Try config.py
    if not storage_url:
        storage_url = getattr(config, 'DVC_REMOTE_STORAGE_URL', None)
    
    return storage_url

def check_remote_exists(remote_name='storage'):
    """Check if a DVC remote with the given name already exists."""
    try:
        dvc_cmd = find_command_in_venv('dvc')
        result = subprocess.run(
            [dvc_cmd, 'remote', 'list'],
            cwd=str(project_root),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return remote_name in result.stdout
        return False
    except Exception:
        return False

def get_remote_url(remote_name='storage'):
    """Get the URL of an existing remote."""
    try:
        dvc_cmd = find_command_in_venv('dvc')
        result = subprocess.run(
            [dvc_cmd, 'remote', 'get-url', remote_name],
            cwd=str(project_root),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None

def main():
    print("=" * 50)
    print("Task 1.3.3: Configure Remote Storage")
    print("=" * 50)
    print("")
    
    # Check if DVC is initialized
    if not is_dvc_initialized():
        print("ERROR: DVC is not initialized in this project", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please run Task 1.3.2 first to initialize DVC:", file=sys.stderr)
        print("  python3 scripts/task_132_dvc_initialization.py", file=sys.stderr)
        return 1
    
    print("✓ DVC is initialized")
    print("")
    
    # Check if dvc command is available
    if not check_command_exists('dvc'):
        print("ERROR: dvc command not found", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please ensure dvc is installed:", file=sys.stderr)
        print("  uv sync", file=sys.stderr)
        return 1
    
    # Get remote storage URL
    storage_url = get_remote_storage_url()
    remote_name = 'storage'
    
    # Check if remote already exists
    if check_remote_exists(remote_name):
        existing_url = get_remote_url(remote_name)
        print(f"✓ Remote '{remote_name}' already exists")
        print(f"  URL: {existing_url}")
        print("")
        
        # If no storage_url is configured but remote exists, consider it already configured
        if not storage_url:
            print("=" * 50)
            print("✓ Remote Storage Configuration: ALREADY COMPLETE")
            print("=" * 50)
            print("")
            print("Remote storage is already configured.")
            print("Next steps:")
            print("  - Proceed to Phase 2: Data Engineering (ETL) & Schema Transformation")
            return 0
        
        # If storage_url differs from existing, only prompt if explicitly configured
        if existing_url != storage_url:
            print(f"⚠ WARNING: Existing remote URL ({existing_url}) differs from configured URL ({storage_url})")
            print("")
            if sys.stdin.isatty():
                try:
                    response = input(f"Update remote URL to {storage_url}? (y/n): ").strip().lower()
                    if response == 'y':
                        try:
                            dvc_cmd = find_command_in_venv('dvc')
                            result = subprocess.run(
                                [dvc_cmd, 'remote', 'modify', remote_name, 'url', storage_url],
                                cwd=str(project_root),
                                capture_output=True,
                                text=True
                            )
                            if result.returncode == 0:
                                print(f"✓ Remote URL updated to: {storage_url}")
                            else:
                                print(f"ERROR: Failed to update remote URL: {result.stderr}", file=sys.stderr)
                                return 1
                        except Exception as e:
                            print(f"ERROR: Failed to update remote: {e}", file=sys.stderr)
                            return 1
                    else:
                        print("Keeping existing remote URL.")
                        print("=" * 50)
                        print("✓ Remote Storage Configuration: ALREADY COMPLETE")
                        print("=" * 50)
                        return 0
                except (EOFError, KeyboardInterrupt):
                    print("\nUpdate cancelled.")
                    print("Keeping existing remote URL.")
                    print("=" * 50)
                    print("✓ Remote Storage Configuration: ALREADY COMPLETE")
                    print("=" * 50)
                    return 0
            else:
                # Non-interactive mode: keep existing URL
                print("Non-interactive mode: Keeping existing remote URL.")
                print("=" * 50)
                print("✓ Remote Storage Configuration: ALREADY COMPLETE")
                print("=" * 50)
                return 0
        else:
            print("=" * 50)
            print("✓ Remote Storage Configuration: ALREADY COMPLETE")
            print("=" * 50)
            print("")
            print("Next steps:")
            print("  - Proceed to Phase 2: Data Engineering (ETL) & Schema Transformation")
            return 0
    
    # If no storage URL is configured, check if remote already exists
    if not storage_url:
        # If remote already exists, consider it configured
        if check_remote_exists(remote_name):
            existing_url = get_remote_url(remote_name)
            print(f"✓ Remote '{remote_name}' already exists")
            print(f"  URL: {existing_url}")
            print("")
            print("=" * 50)
            print("✓ Remote Storage Configuration: ALREADY COMPLETE")
            print("=" * 50)
            print("")
            print("Remote storage is already configured.")
            print("Next steps:")
            print("  - Proceed to Phase 2: Data Engineering (ETL) & Schema Transformation")
            return 0
        
        # No remote exists and no URL configured, prompt user
        print("No remote storage URL configured.")
        print("")
        print("To configure remote storage, you have two options:")
        print("")
        print("Option 1: Set in .env file (recommended)")
        print("  Add to .env: DVC_REMOTE_STORAGE_URL=s3://bucket-name/chicken-data")
        print("  Or for other backends:")
        print("    - S3: DVC_REMOTE_STORAGE_URL=s3://bucket-name/path")
        print("    - GDrive: DVC_REMOTE_STORAGE_URL=gdrive://folder-id")
        print("    - Local: DVC_REMOTE_STORAGE_URL=/path/to/storage")
        print("")
        print("Option 2: Set in config.py")
        print("  Add to config.py: DVC_REMOTE_STORAGE_URL = 's3://bucket-name/chicken-data'")
        print("")
        
        if sys.stdin.isatty():
            try:
                response = input("Enter remote storage URL now? (y/n): ").strip().lower()
                if response == 'y':
                    storage_url = input("Enter storage URL: ").strip()
                    if not storage_url:
                        print("No URL provided. Skipping remote configuration.")
                        return 0
                else:
                    print("Skipping remote configuration.")
                    print("You can configure it later by:")
                    print("  1. Setting DVC_REMOTE_STORAGE_URL in .env or config.py")
                    print("  2. Re-running this script")
                    print("  3. Or manually: dvc remote add -d storage <url>")
                    return 0
            except (EOFError, KeyboardInterrupt):
                print("\nConfiguration cancelled.")
                return 0
        else:
            print("Non-interactive mode: Skipping remote configuration.")
            print("Please set DVC_REMOTE_STORAGE_URL in .env or config.py and re-run this script.")
            return 0
    
    # Configure remote storage
    print(f"Configuring remote storage '{remote_name}'...")
    print(f"  URL: {storage_url}")
    print("")
    
    try:
        dvc_cmd = find_command_in_venv('dvc')
        # Add remote (or modify if exists)
        if check_remote_exists(remote_name):
            # Modify existing remote
            result = subprocess.run(
                [dvc_cmd, 'remote', 'modify', remote_name, 'url', storage_url],
                cwd=str(project_root),
                capture_output=True,
                text=True
            )
            action = "updated"
        else:
            # Add new remote
            result = subprocess.run(
                [dvc_cmd, 'remote', 'add', '-d', remote_name, storage_url],
                cwd=str(project_root),
                capture_output=True,
                text=True
            )
            action = "added"
        
        if result.returncode == 0:
            print(f"✓ Remote '{remote_name}' {action} successfully")
            print("")
            
            # Verify configuration
            print("Verification:")
            try:
                verify_result = subprocess.run(
                    [dvc_cmd, 'remote', 'list'],
                    cwd=str(project_root),
                    capture_output=True,
                    text=True
                )
                if verify_result.returncode == 0:
                    print(verify_result.stdout)
                
                # Check if it's set as default
                default_result = subprocess.run(
                    [dvc_cmd, 'config', 'core.remote'],
                    cwd=str(project_root),
                    capture_output=True,
                    text=True
                )
                if default_result.returncode == 0 and default_result.stdout.strip() == remote_name:
                    print(f"✓ Remote '{remote_name}' is set as default")
                else:
                    print(f"⚠ WARNING: Remote '{remote_name}' is not set as default")
            except Exception as e:
                print(f"⚠ WARNING: Could not verify remote configuration: {e}")
            
        else:
            print(f"ERROR: Failed to configure remote:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return 1
            
    except FileNotFoundError:
        print("ERROR: dvc command not found", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Failed to configure remote storage: {e}", file=sys.stderr)
        return 1
    
    print("")
    print("=" * 50)
    print("✓ Remote Storage Configuration: COMPLETED")
    print("=" * 50)
    print("")
    print(f"Remote '{remote_name}' configured:")
    print(f"  URL: {storage_url}")
    print("")
    print("Next steps:")
    print("  - Proceed to Phase 2: Data Engineering (ETL) & Schema Transformation")
    print("  - Use 'dvc add <file>' to track files with DVC")
    print("  - Use 'dvc push' to upload tracked files to remote storage")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
