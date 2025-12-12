#!/usr/bin/env -S uv run python
"""
Task ID: 4.3.2
Description: Register Artifacts
Created: 2025-01-15

Upon training completion, tag the best checkpoint (best.pt) in the Model Registry
(or WandB Artifacts) with the DVC Commit Hash used for training.

Note: This script should be executed using 'uv run python script.py' to ensure
the virtual environment is used. Dependencies (wandb, python-dotenv) should be
declared in pyproject.toml and installed via 'uv sync' before running this script.
"""

import sys
import os
import subprocess
import json
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


def find_best_checkpoint(checkpoint_dir):
    """Find the best checkpoint file."""
    checkpoint_path = Path(checkpoint_dir)
    
    # Common checkpoint file names
    possible_names = [
        'best.pt',
        'checkpoint_best.pt',
        'best_model.pt',
        'model_best.pt',
    ]
    
    # Check for exact matches
    for name in possible_names:
        candidate = checkpoint_path / name
        if candidate.exists():
            return candidate
    
    # Check for checkpoint files in subdirectories (experiment log dirs)
    for subdir in checkpoint_path.iterdir():
        if subdir.is_dir():
            checkpoints_subdir = subdir / 'checkpoints'
            if checkpoints_subdir.exists():
                for name in possible_names:
                    candidate = checkpoints_subdir / name
                    if candidate.exists():
                        return candidate
    
    # If no best checkpoint found, look for any .pt file
    pt_files = list(checkpoint_path.glob('**/*.pt'))
    if pt_files:
        # Return the most recently modified one
        return max(pt_files, key=lambda p: p.stat().st_mtime)
    
    return None


def register_wandb_artifact(checkpoint_path, commit_hash, hash_type):
    """Register checkpoint as WandB artifact."""
    if not config.USE_WANDB:
        print("WandB is disabled in configuration (USE_WANDB=False)")
        print("Skipping WandB artifact registration.")
        return False
    
    try:
        import wandb
    except ImportError:
        print("WARNING: wandb not available, skipping WandB artifact registration", file=sys.stderr)
        return False
    
    wandb_api_key = os.getenv('WANDB_API_KEY')
    if not wandb_api_key:
        print("WARNING: WandB enabled but WANDB_API_KEY not found in .env", file=sys.stderr)
        print("Skipping WandB artifact registration.")
        return False
    
    try:
        # Initialize wandb if not already initialized
        if wandb.run is None:
            wandb.init(
                project=config.WANDB_PROJECT_NAME,
                name="register-artifacts",
                job_type="artifact-registration",
                tags=["checkpoint", "model-registry"]
            )
        
        # Create artifact name with version
        artifact_name = f"chicken-detection-model"
        
        # Create artifact
        artifact = wandb.Artifact(
            name=artifact_name,
            type="model",
            description=f"Best checkpoint for chicken detection model. Registered with {hash_type} commit hash."
        )
        
        # Add checkpoint file to artifact
        artifact.add_file(str(checkpoint_path), name=checkpoint_path.name)
        
        # Add metadata
        metadata = {
            'checkpoint_path': str(checkpoint_path),
            'commit_hash': commit_hash,
            'hash_type': hash_type,
            'timestamp': datetime.now().isoformat(),
            'project_name': config.PROJECT_NAME,
        }
        artifact.metadata = metadata
        
        # Log artifact
        wandb.log_artifact(artifact)
        
        print(f"✓ Checkpoint registered as WandB artifact: {artifact_name}")
        print(f"  Commit hash ({hash_type}): {commit_hash[:8]}...")
        print(f"  Checkpoint: {checkpoint_path}")
        
        # Finish wandb run
        wandb.finish()
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to register WandB artifact: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def main():
    """Register best checkpoint as WandB artifact with DVC/git commit hash."""
    print("=" * 50)
    print("Task 4.3.2: Register Artifacts")
    print("=" * 50)
    print()
    
    # Get checkpoint directory
    checkpoint_dir = project_root / config.DEFAULT_CHECKPOINT_PATH
    
    if not checkpoint_dir.exists():
        print(f"ERROR: Checkpoint directory not found: {checkpoint_dir}", file=sys.stderr)
        print("Please ensure training has been completed and checkpoints are saved.", file=sys.stderr)
        return 1
    
    # Find best checkpoint
    checkpoint_path = find_best_checkpoint(checkpoint_dir)
    
    if checkpoint_path is None:
        print(f"WARNING: No checkpoint file found in {checkpoint_dir}", file=sys.stderr)
        print("Please ensure training has been completed and checkpoints are saved.", file=sys.stderr)
        print()
        print("Searched for:")
        print("  - best.pt")
        print("  - checkpoint_best.pt")
        print("  - best_model.pt")
        print("  - model_best.pt")
        print("  - Any .pt files in checkpoint directory")
        return 1
    
    print(f"Found checkpoint: {checkpoint_path}")
    print()
    
    # Get commit hash (DVC or git)
    commit_hash, hash_type = get_dvc_commit_hash()
    
    if commit_hash is None:
        print("WARNING: Could not determine commit hash (DVC or git)", file=sys.stderr)
        print("Artifact will be registered without commit hash metadata.", file=sys.stderr)
        commit_hash = "unknown"
        hash_type = "unknown"
    else:
        print(f"Using {hash_type} commit hash: {commit_hash[:8]}...")
        print()
    
    # Register WandB artifact
    success = register_wandb_artifact(checkpoint_path, commit_hash, hash_type)
    
    if success:
        print()
        print("=" * 50)
        print("✓ Artifact registration completed successfully")
        print("=" * 50)
        return 0
    else:
        print()
        print("=" * 50)
        print("⚠ Artifact registration skipped or failed")
        print("=" * 50)
        print("Checkpoint found but not registered to WandB.")
        print("This may be normal if WandB is disabled or not configured.")
        return 0  # Return 0 because checkpoint was found, registration is optional


if __name__ == "__main__":
    sys.exit(main())
