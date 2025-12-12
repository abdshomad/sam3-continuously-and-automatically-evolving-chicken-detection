#!/usr/bin/env -S uv run python
"""
Task ID: 4.3.3
Description: Archive Config
Created: 2025-01-15

Save the resolved config.yaml alongside the model weights to ensure the experiment
is reproducible.

Note: This script should be executed using 'uv run python script.py' to ensure
the virtual environment is used. Dependencies (python-dotenv) should be
declared in pyproject.toml and installed via 'uv sync' before running this script.
"""

import sys
import os
import subprocess
import json
import shutil
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Get project root directory
project_root = Path(__file__).parent.parent

# Add project root to Python path to import config
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Import configuration from config.py
try:
    import config
except ImportError:
    print("Error: config.py not found. Please create config.py with required settings.", file=sys.stderr)
    sys.exit(1)


def get_git_commit_hash():
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_dvc_commit_hash():
    """Get DVC commit hash if DVC is initialized, otherwise return git hash."""
    # First try to get DVC commit hash
    try:
        result = subprocess.run(
            ['dvc', 'rev-parse', 'HEAD'],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        dvc_hash = result.stdout.strip()
        if dvc_hash:
            return dvc_hash, 'dvc'
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Fallback to git commit hash
    git_hash = get_git_commit_hash()
    if git_hash:
        return git_hash, 'git'
    
    return None, None


def find_checkpoint_directory():
    """Find the checkpoint directory containing best.pt."""
    checkpoint_dir = project_root / config.DEFAULT_CHECKPOINT_PATH
    
    # Common checkpoint file names
    possible_names = [
        'best.pt',
        'checkpoint_best.pt',
        'best_model.pt',
        'model_best.pt',
    ]
    
    # Check for exact matches in default checkpoint dir
    if checkpoint_dir.exists():
        for name in possible_names:
            candidate = checkpoint_dir / name
            if candidate.exists():
                return checkpoint_dir, candidate
        
        # Fallback: Look for any .pt file in checkpoint directory
        pt_files = list(checkpoint_dir.glob('*.pt'))
        if pt_files:
            # Return the most recently modified one
            checkpoint_file = max(pt_files, key=lambda p: p.stat().st_mtime)
            return checkpoint_dir, checkpoint_file
    
    # Check for checkpoint files in subdirectories (experiment log dirs)
    # SAM3 saves checkpoints in experiment_log_dir/checkpoints/
    if checkpoint_dir.exists():
        for subdir in checkpoint_dir.iterdir():
            if subdir.is_dir():
                checkpoints_subdir = subdir / 'checkpoints'
                if checkpoints_subdir.exists():
                    for name in possible_names:
                        candidate = checkpoints_subdir / name
                        if candidate.exists():
                            return checkpoints_subdir, candidate
    
    # Also check results directories (where SAM3 might save checkpoints)
    results_dir = project_root / 'results'
    if results_dir.exists():
        for subdir in results_dir.iterdir():
            if subdir.is_dir():
                checkpoints_subdir = subdir / 'checkpoints'
                if checkpoints_subdir.exists():
                    for name in possible_names:
                        candidate = checkpoints_subdir / name
                        if candidate.exists():
                            return checkpoints_subdir, candidate
    
    # Check sam3_logs directories (SAM3 default experiment log dir)
    sam3_logs_dir = project_root / 'sam3_logs'
    if sam3_logs_dir.exists():
        for subdir in sam3_logs_dir.iterdir():
            if subdir.is_dir():
                checkpoints_subdir = subdir / 'checkpoints'
                if checkpoints_subdir.exists():
                    for name in possible_names:
                        candidate = checkpoints_subdir / name
                        if candidate.exists():
                            return checkpoints_subdir, candidate
    
    return None, None


def find_config_files(experiment_log_dir):
    """Find config.yaml and config_resolved.yaml files."""
    config_files = {}
    
    # Look for config files in experiment log directory
    if experiment_log_dir and experiment_log_dir.exists():
        config_yaml = experiment_log_dir / 'config.yaml'
        config_resolved_yaml = experiment_log_dir / 'config_resolved.yaml'
        
        if config_yaml.exists():
            config_files['config.yaml'] = config_yaml
        if config_resolved_yaml.exists():
            config_files['config_resolved.yaml'] = config_resolved_yaml
    
    # Also check parent directory (experiment_log_dir might be the parent)
    parent_dir = experiment_log_dir.parent if experiment_log_dir else None
    if parent_dir and parent_dir.exists():
        config_yaml = parent_dir / 'config.yaml'
        config_resolved_yaml = parent_dir / 'config_resolved.yaml'
        
        if config_yaml.exists() and 'config.yaml' not in config_files:
            config_files['config.yaml'] = config_yaml
        if config_resolved_yaml.exists() and 'config_resolved.yaml' not in config_files:
            config_files['config_resolved.yaml'] = config_resolved_yaml
    
    return config_files


def create_manifest(checkpoint_dir, checkpoint_path, config_files, commit_hash, hash_type):
    """Create a manifest file listing all archived files."""
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'checkpoint_path': str(checkpoint_path),
        'checkpoint_dir': str(checkpoint_dir),
        'commit_hash': commit_hash,
        'hash_type': hash_type,
        'config_files': {name: str(path) for name, path in config_files.items()},
        'project_name': config.PROJECT_NAME,
    }
    
    manifest_path = checkpoint_dir / 'config_manifest.json'
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return manifest_path


def main():
    """Archive config files alongside model weights."""
    print("=" * 50)
    print("Task 4.3.3: Archive Config")
    print("=" * 50)
    print()
    
    # Find checkpoint directory
    checkpoint_dir, checkpoint_path = find_checkpoint_directory()
    
    if checkpoint_dir is None or checkpoint_path is None:
        print(f"WARNING: No checkpoint found in {config.DEFAULT_CHECKPOINT_PATH}", file=sys.stderr)
        print("Please ensure training has been completed and checkpoints are saved.", file=sys.stderr)
        print()
        print("Searched in:")
        print(f"  - {project_root / config.DEFAULT_CHECKPOINT_PATH}")
        print(f"  - {project_root / 'results'}")
        print(f"  - {project_root / 'sam3_logs'}")
        return 1
    
    print(f"Found checkpoint: {checkpoint_path}")
    print(f"Checkpoint directory: {checkpoint_dir}")
    print()
    
    # Find experiment log directory (parent of checkpoints subdirectory)
    experiment_log_dir = checkpoint_dir.parent if checkpoint_dir.name == 'checkpoints' else checkpoint_dir
    
    # Find config files
    config_files = find_config_files(experiment_log_dir)
    
    if not config_files:
        print(f"WARNING: No config files found in {experiment_log_dir}", file=sys.stderr)
        print("Config files are typically saved during training in the experiment log directory.", file=sys.stderr)
        print("If training hasn't completed yet, config files may not exist.", file=sys.stderr)
        print()
        print("Searched for:")
        print("  - config.yaml")
        print("  - config_resolved.yaml")
        print()
        print("This is normal if training hasn't been run yet.")
        return 0  # Return 0 because checkpoint was found, config archiving is optional
    
    print(f"Found {len(config_files)} config file(s):")
    for name, path in config_files.items():
        print(f"  - {name}: {path}")
    print()
    
    # Copy config files to checkpoint directory
    copied_files = {}
    for name, source_path in config_files.items():
        dest_path = checkpoint_dir / name
        try:
            shutil.copy2(source_path, dest_path)
            copied_files[name] = str(dest_path)
            print(f"✓ Copied {name} to {dest_path}")
        except Exception as e:
            print(f"ERROR: Failed to copy {name}: {e}", file=sys.stderr)
    
    if not copied_files:
        print("WARNING: No config files were copied", file=sys.stderr)
        return 1
    
    print()
    
    # Get commit hash
    commit_hash, hash_type = get_dvc_commit_hash()
    if commit_hash is None:
        commit_hash = "unknown"
        hash_type = "unknown"
    
    # Create manifest
    manifest_path = create_manifest(
        checkpoint_dir,
        checkpoint_path,
        copied_files,
        commit_hash,
        hash_type
    )
    
    print(f"✓ Created manifest: {manifest_path}")
    print()
    
    print("=" * 50)
    print("✓ Config archiving completed successfully")
    print("=" * 50)
    print()
    print("Archived files:")
    print(f"  - Checkpoint: {checkpoint_path.name}")
    for name in copied_files:
        print(f"  - {name}")
    print(f"  - Manifest: {manifest_path.name}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
