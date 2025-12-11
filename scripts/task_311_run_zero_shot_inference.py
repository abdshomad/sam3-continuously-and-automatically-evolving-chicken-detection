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
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Suppress pkg_resources deprecation warning from SAM3
warnings.filterwarnings('ignore', category=UserWarning, message='.*pkg_resources.*')

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

    # Get paths from config (project_root already set above)
    checkpoint_dir = project_root / config.DEFAULT_CHECKPOINT_PATH
    
    # Try to find checkpoint file (could be sam3_vit_h.pt, sam3.pt, or other variants)
    checkpoint_path = None
    possible_checkpoint_names = ["sam3_vit_h.pt", "sam3.pt", "sam3_vit_l.pt", "sam3_vit_b.pt"]
    for name in possible_checkpoint_names:
        candidate = checkpoint_dir / name
        if candidate.exists():
            checkpoint_path = candidate
            break
    
    if checkpoint_path is None:
        print(f"ERROR: No checkpoint found in {checkpoint_dir}", file=sys.stderr)
        print(f"Looked for: {', '.join(possible_checkpoint_names)}", file=sys.stderr)
        print("Please run task 1.2.5 first to download pre-trained weights.", file=sys.stderr)
        return 1
    
    val_json_path = project_root / config.DEFAULT_DATA_PATH / "chicken_val.json"
    config_path = project_root / "configs" / "base_eval.yaml"
    sam3_train_script = project_root / "sam3" / "sam3" / "train" / "train.py"

    # Check if checkpoint exists (already checked above, but verify)
    if not checkpoint_path.exists():
        print(f"ERROR: Checkpoint not found: {checkpoint_path}", file=sys.stderr)
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

    # Change to SAM3 directory for Hydra config resolution
    # Hydra expects configs relative to the sam3 package
    sam3_dir = project_root / "sam3"
    if not sam3_dir.exists():
        print(f"ERROR: SAM3 directory not found: {sam3_dir}", file=sys.stderr)
        return 1
    
    # Ensure config exists in sam3 configs directory with absolute paths
    import shutil
    import yaml
    sam3_config_dir = sam3_dir / "sam3" / "train" / "configs"
    sam3_config_dir.mkdir(parents=True, exist_ok=True)
    config_name = "chicken_base_eval.yaml"
    sam3_config_path = sam3_config_dir / config_name
    
    # Read and update config with absolute paths (preserving YAML structure)
    try:
        # Read as text to preserve interpolation syntax
        with open(config_path, 'r') as f:
            config_text = f.read()
        
        # Replace path values while preserving YAML structure
        # Use string replacement to maintain interpolation references
        config_text = config_text.replace(
            'checkpoint_path: checkpoints/sam3.pt',
            f'checkpoint_path: {checkpoint_path}'
        )
        config_text = config_text.replace(
            'experiment_log_dir: results/zero_shot_baseline',
            f'experiment_log_dir: {project_root / "results" / "zero_shot_baseline"}'
        )
        config_text = config_text.replace(
            'coco_gt: data/chicken_val.json',
            f'coco_gt: {val_json_path}'
        )
        # Image path should be the data directory root since file_name in JSON is relative
        config_text = config_text.replace(
            'img_path: data',
            f'img_path: {project_root / config.DEFAULT_DATA_PATH}'
        )
        config_text = config_text.replace(
            'bpe_path: sam3/sam3/assets/bpe_simple_vocab_16e6.txt.gz',
            f'bpe_path: {sam3_dir / "sam3" / "assets" / "bpe_simple_vocab_16e6.txt.gz"}'
        )
        
        # Also update launcher.experiment_log_dir interpolation
        config_text = config_text.replace(
            'experiment_log_dir: ${paths.experiment_log_dir}',
            f'experiment_log_dir: {project_root / "results" / "zero_shot_baseline"}'
        )
        
        # Write updated config to sam3 configs directory
        with open(sam3_config_path, 'w') as f:
            f.write(config_text)
        print(f"Updated config with absolute paths: {sam3_config_path}")
    except Exception as e:
        print(f"ERROR: Could not update config with absolute paths: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    # Change to sam3 directory so Hydra can resolve configs
    original_cwd = os.getcwd()
    original_pythonpath = os.environ.get("PYTHONPATH", "")
    os.chdir(sam3_dir)
    
    # Set PYTHONPATH to include sam3 directory for Hydra config resolution
    os.environ["PYTHONPATH"] = f"{sam3_dir}:{original_pythonpath}" if original_pythonpath else str(sam3_dir)
    
    # Set environment variables for config path resolution
    os.environ["PROJECT_ROOT"] = str(project_root)
    os.environ["SAM3_ROOT"] = str(sam3_dir)
    
    # Suppress pkg_resources deprecation warnings from SAM3
    pythonwarnings = os.environ.get("PYTHONWARNINGS", "")
    if pythonwarnings:
        os.environ["PYTHONWARNINGS"] = f"{pythonwarnings},ignore::UserWarning:sam3.model_builder"
    else:
        os.environ["PYTHONWARNINGS"] = "ignore::UserWarning:sam3.model_builder"
    
    # Use relative path from sam3 directory
    config_arg = f"configs/{config_name}"
    
    # Build command (paths are already in the config file)
    cmd = [
        sys.executable,
        "sam3/train/train.py",
        "-c", config_arg,
        "--use-cluster", "0",
        "--num-gpus", "1"
    ]

    print("Running zero-shot inference...")
    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        # Run the evaluation
        result = subprocess.run(cmd, check=True, cwd=str(sam3_dir))
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
    finally:
        # Restore original directory and PYTHONPATH
        os.chdir(original_cwd)
        if original_pythonpath:
            os.environ["PYTHONPATH"] = original_pythonpath
        elif "PYTHONPATH" in os.environ:
            del os.environ["PYTHONPATH"]


if __name__ == "__main__":
    sys.exit(main())
