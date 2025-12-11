#!/usr/bin/env python3
"""
Task ID: 2.1.1
Description: Directory Structure Setup
Created: 2025-01-27

This script organizes data into the required directory structure:
- raw_data/images/chicken/
- raw_data/images/not_chicken/
- raw_data/labels/ (matching filenames)
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import configuration from config.py
try:
    import config
except ImportError:
    print("Error: config.py not found. Please create config.py with required settings.", file=sys.stderr)
    sys.exit(1)

def create_directory_structure():
    """Create the required directory structure for raw data."""
    
    # Define base data path (use config if available, otherwise default)
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    base_path = project_root / base_data_path
    
    # Define required directories
    directories = [
        base_path / 'raw_data' / 'images' / 'chicken',
        base_path / 'raw_data' / 'images' / 'not_chicken',
        base_path / 'raw_data' / 'labels',
    ]
    
    created_dirs = []
    existing_dirs = []
    
    print("Creating directory structure...")
    print(f"Base data path: {base_path}")
    print("")
    
    for directory in directories:
        try:
            # Create directory and parents if they don't exist
            directory.mkdir(parents=True, exist_ok=True)
            
            if directory.exists():
                # Check if it was just created or already existed
                # We can't easily tell, but we'll assume if it's empty it was just created
                if any(directory.iterdir()):
                    existing_dirs.append(directory)
                    print(f"  ✓ {directory.relative_to(project_root)} (already exists)")
                else:
                    created_dirs.append(directory)
                    print(f"  ✓ {directory.relative_to(project_root)} (created)")
            else:
                print(f"  ✗ Failed to create: {directory.relative_to(project_root)}", file=sys.stderr)
                
        except PermissionError:
            print(f"  ✗ Permission denied: {directory.relative_to(project_root)}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"  ✗ Error creating {directory.relative_to(project_root)}: {e}", file=sys.stderr)
            return False
    
    print("")
    return True, created_dirs, existing_dirs

def verify_directory_structure():
    """Verify that all required directories exist."""
    
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    base_path = project_root / base_data_path
    
    required_dirs = [
        base_path / 'raw_data' / 'images' / 'chicken',
        base_path / 'raw_data' / 'images' / 'not_chicken',
        base_path / 'raw_data' / 'labels',
    ]
    
    all_exist = True
    missing_dirs = []
    
    print("Verifying directory structure...")
    print("")
    
    for directory in required_dirs:
        if directory.exists() and directory.is_dir():
            print(f"  ✓ {directory.relative_to(project_root)}")
        else:
            print(f"  ✗ Missing: {directory.relative_to(project_root)}", file=sys.stderr)
            missing_dirs.append(directory)
            all_exist = False
    
    print("")
    return all_exist, missing_dirs

def main():
    print("=" * 50)
    print("Task 2.1.1: Directory Structure Setup")
    print("=" * 50)
    print("")
    
    # Create directory structure
    success, created_dirs, existing_dirs = create_directory_structure()
    
    if not success:
        print("ERROR: Failed to create some directories", file=sys.stderr)
        return 1
    
    # Verify structure
    all_exist, missing_dirs = verify_directory_structure()
    
    if not all_exist:
        print("ERROR: Some required directories are missing", file=sys.stderr)
        return 1
    
    # Summary
    print("=" * 50)
    print("✓ Directory Structure Setup: COMPLETED")
    print("=" * 50)
    print("")
    print("Directory structure created successfully:")
    print("")
    
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    base_path = project_root / base_data_path
    
    print(f"  {base_path.relative_to(project_root)}/")
    print(f"    raw_data/")
    print(f"      images/")
    print(f"        chicken/       (for chicken images)")
    print(f"        not_chicken/   (for negative sample images)")
    print(f"      labels/          (for annotation files matching image filenames)")
    print("")
    print("Next steps:")
    print("  - Place chicken images in: raw_data/images/chicken/")
    print("  - Place negative samples in: raw_data/images/not_chicken/")
    print("  - Place annotation files in: raw_data/labels/")
    print("  - Ensure annotation filenames match image filenames (with appropriate extension)")
    print("")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
