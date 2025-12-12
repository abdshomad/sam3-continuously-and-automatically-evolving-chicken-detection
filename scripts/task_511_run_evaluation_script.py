#!/usr/bin/env -S uv run python
"""
Task ID: 5.1.1
Description: Run Evaluation Script
Created: 2025-01-15

Execute evaluation using the fine-tuned checkpoint:
python sam3/eval/evaluate.py --config configs/eval_chicken.yaml --checkpoint checkpoints/best.pt --json data/chicken_val.json

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


def find_finetuned_checkpoint():
    """Find the fine-tuned checkpoint file."""
    checkpoint_dir = project_root / config.DEFAULT_CHECKPOINT_PATH
    
    # Common checkpoint file names (prioritize best.pt)
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
                return candidate
        
        # Fallback: Look for any .pt file in checkpoint directory
        pt_files = list(checkpoint_dir.glob('*.pt'))
        if pt_files:
            # Return the most recently modified one
            return max(pt_files, key=lambda p: p.stat().st_mtime)
    
    # Check for checkpoint files in subdirectories (experiment log dirs)
    if checkpoint_dir.exists():
        for subdir in checkpoint_dir.iterdir():
            if subdir.is_dir():
                checkpoints_subdir = subdir / 'checkpoints'
                if checkpoints_subdir.exists():
                    for name in possible_names:
                        candidate = checkpoints_subdir / name
                        if candidate.exists():
                            return candidate
    
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
                            return candidate
    
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
                            return candidate
    
    return None


def main():
    """Run evaluation using fine-tuned checkpoint."""
    print("=" * 50)
    print("Task 5.1.1: Run Evaluation Script")
    print("=" * 50)
    print()
    
    # Find fine-tuned checkpoint
    checkpoint_path = find_finetuned_checkpoint()
    
    if checkpoint_path is None:
        print(f"ERROR: No fine-tuned checkpoint found", file=sys.stderr)
        print(f"Searched in:", file=sys.stderr)
        print(f"  - {project_root / config.DEFAULT_CHECKPOINT_PATH}", file=sys.stderr)
        print(f"  - {project_root / 'results'}", file=sys.stderr)
        print(f"  - {project_root / 'sam3_logs'}", file=sys.stderr)
        print()
        print("Please ensure training has been completed and checkpoints are saved.", file=sys.stderr)
        print("Expected checkpoint names: best.pt, checkpoint_best.pt, best_model.pt, model_best.pt", file=sys.stderr)
        return 1
    
    print(f"Found checkpoint: {checkpoint_path}")
    print()
    
    # Get validation JSON path
    val_json_path = project_root / config.DEFAULT_DATA_PATH / "chicken_val.json"
    
    if not check_file_exists(val_json_path, "Validation JSON"):
        print("Please run Phase 2 tasks first to generate chicken_val.json.", file=sys.stderr)
        return 1
    
    # Check if evaluation config exists, otherwise use base_eval.yaml
    eval_config_path = project_root / "configs" / "eval_chicken.yaml"
    if not eval_config_path.exists():
        # Use base_eval.yaml as template
        base_config_path = project_root / "configs" / "base_eval.yaml"
        if not check_file_exists(base_config_path, "Base evaluation config"):
            return 1
        eval_config_path = base_config_path
        print(f"Using base evaluation config: {eval_config_path}")
    else:
        print(f"Using evaluation config: {eval_config_path}")
    
    print()
    
    # Check if SAM3 train script exists
    sam3_train_script = project_root / "sam3" / "sam3" / "train" / "train.py"
    if not check_file_exists(sam3_train_script, "SAM3 train script"):
        print("ERROR: SAM3 submodule not found. Please run task 1.2.1 first.", file=sys.stderr)
        return 1
    
    # Ensure queried_category field exists in JSON (required by SAM3)
    try:
        import json
        with open(val_json_path, 'r') as f:
            data = json.load(f)
        
        # Find chicken category ID
        chicken_cat_id = 1  # default
        if 'categories' in data and len(data['categories']) > 0:
            chicken_cat = next((c for c in data['categories'] if 'chicken' in c.get('name', '').lower()), data['categories'][0])
            chicken_cat_id = chicken_cat.get('id')
        
        # Add queried_category to all images if missing
        updated = 0
        if 'images' in data:
            for img in data['images']:
                if 'queried_category' not in img:
                    img['queried_category'] = str(chicken_cat_id)
                    updated += 1
        
        # Save if updated
        if updated > 0:
            with open(val_json_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Added queried_category={chicken_cat_id} to {updated} images in validation JSON")
            print()
    except Exception as e:
        print(f"WARNING: Could not verify/update queried_category in JSON: {e}", file=sys.stderr)
        print()
    
    # Change to SAM3 directory for Hydra config resolution
    sam3_dir = project_root / "sam3"
    if not sam3_dir.exists():
        print(f"ERROR: SAM3 directory not found: {sam3_dir}", file=sys.stderr)
        return 1
    
    # Ensure config exists in sam3 configs directory with absolute paths
    import shutil
    sam3_config_dir = sam3_dir / "sam3" / "train" / "configs"
    sam3_config_dir.mkdir(parents=True, exist_ok=True)
    config_name = "chicken_finetuned_eval.yaml"
    sam3_config_path = sam3_config_dir / config_name
    
    # Read and update config with absolute paths
    try:
        # Read as text to preserve interpolation syntax
        with open(eval_config_path, 'r') as f:
            config_text = f.read()
        
        # Replace path values while preserving YAML structure
        config_text = config_text.replace(
            'checkpoint_path: checkpoints/sam3.pt',
            f'checkpoint_path: {checkpoint_path}'
        )
        config_text = config_text.replace(
            'experiment_log_dir: results/zero_shot_baseline',
            f'experiment_log_dir: {project_root / "results" / "finetuned_evaluation"}'
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
            f'experiment_log_dir: {project_root / "results" / "finetuned_evaluation"}'
        )
        
        # Write updated config to sam3 configs directory
        with open(sam3_config_path, 'w') as f:
            f.write(config_text)
        print(f"✓ Updated config with absolute paths: {sam3_config_path}")
        print()
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
    
    print("Running evaluation with fine-tuned checkpoint...")
    print(f"Checkpoint: {checkpoint_path}")
    print(f"Validation JSON: {val_json_path}")
    print(f"Config: {sam3_config_path}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        # Run the evaluation
        result = subprocess.run(cmd, check=True, cwd=str(sam3_dir))
        print()
        print("=" * 50)
        print("✓ Evaluation completed successfully")
        print("=" * 50)
        print()
        print(f"Results should be saved in: {project_root / 'results' / 'finetuned_evaluation'}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Evaluation failed with exit code {e.returncode}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nERROR: Evaluation interrupted by user", file=sys.stderr)
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
