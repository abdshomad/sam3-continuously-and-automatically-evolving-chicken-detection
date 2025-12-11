#!/usr/bin/env -S uv run python
"""
Task ID: 3.1.1
Description: Run Zero-Shot Inference
Created: 2025-12-12

Note: This script should be executed using 'uv run python script.py' to ensure
the virtual environment is used. Dependencies should be declared in pyproject.toml
and installed via 'uv sync' before running this script.
"""

import sys
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Import configuration from config.py
try:
    import config
except ImportError:
    print("Error: config.py not found. Please create config.py with required settings.", file=sys.stderr)
    sys.exit(1)


def check_file_exists(filepath, description):
    """Check if a file exists and print error if not."""
    if not Path(filepath).exists():
        print(f"ERROR: {description} not found: {filepath}", file=sys.stderr)
        return False
    return True


def main():
    """Run zero-shot inference using pre-trained SAM3 checkpoint."""
    print("=" * 50)
    print("Task 3.1.1: Run Zero-Shot Inference")
    print("=" * 50)
    print()

    # Get paths from config
    project_root = Path(__file__).parent.parent
    checkpoint_path = project_root / config.DEFAULT_CHECKPOINT_PATH / "sam3_vit_h.pt"
    val_json_path = project_root / config.DEFAULT_DATA_PATH / "chicken_val.json"
    config_path = project_root / "configs" / "base_eval.yaml"
    sam3_train_script = project_root / "sam3" / "sam3" / "train" / "train.py"

    # Check if checkpoint exists
    if not check_file_exists(checkpoint_path, "Checkpoint"):
        print("Please run task 1.2.5 first to download pre-trained weights.", file=sys.stderr)
        return 1

    # Check if validation JSON exists
    if not check_file_exists(val_json_path, "Validation JSON"):
        print("Please run Phase 2 tasks first to generate chicken_val.json.", file=sys.stderr)
        return 1

    # Check if config file exists
    if not check_file_exists(config_path, "Evaluation config"):
        print(f"ERROR: Evaluation config not found: {config_path}", file=sys.stderr)
        print("The config file should have been created by this script.", file=sys.stderr)
        return 1

    # Check if SAM3 train script exists
    if not check_file_exists(sam3_train_script, "SAM3 train script"):
        print("ERROR: SAM3 submodule not found. Please run task 1.2.1 first.", file=sys.stderr)
        return 1

    print(f"Checkpoint: {checkpoint_path}")
    print(f"Validation JSON: {val_json_path}")
    print(f"Config: {config_path}")
    print()

    # Change to project root directory
    os.chdir(project_root)

    # Build command
    cmd = [
        sys.executable,
        str(sam3_train_script),
        "-c", str(config_path),
        "--use-cluster", "0",
        "--num-gpus", "1"
    ]

    print("Running zero-shot inference...")
    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        # Run the evaluation
        result = subprocess.run(cmd, check=True, cwd=project_root)
        print()
        print("=" * 50)
        print("✓ Zero-shot inference completed successfully")
        print("=" * 50)
        print()
        print(f"Results should be saved in: {project_root / 'results' / 'zero_shot_baseline'}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Zero-shot inference failed with exit code {e.returncode}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nERROR: Zero-shot inference interrupted by user", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
