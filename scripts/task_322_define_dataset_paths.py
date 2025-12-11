#!/usr/bin/env -S uv run python
"""
Task ID: 3.2.2
Description: Define Dataset Paths
Created: 2025-01-15

Note: This script should be executed using 'uv run python script.py' to ensure
the virtual environment is used. Dependencies should be declared in pyproject.toml
and installed via 'uv sync' before running this script.
"""

import sys
import yaml
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


def update_dataset_paths(config_path, train_json, val_json, img_dir):
    """Update dataset paths in the configuration file."""
    
    # Load existing config
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        print("Please run task 3.2.1 first to create the config file.", file=sys.stderr)
        return False
    
    print(f"Loading configuration from: {config_path}")
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
    except Exception as e:
        print(f"ERROR: Failed to load config file: {e}", file=sys.stderr)
        return False
    
    # Update dataset paths in chicken_dataset section
    if 'chicken_dataset' not in config_data:
        print("WARNING: 'chicken_dataset' section not found in config. Creating it...", file=sys.stderr)
        config_data['chicken_dataset'] = {}
    
    # Update paths
    config_data['chicken_dataset']['train_json'] = train_json
    config_data['chicken_dataset']['val_json'] = val_json
    config_data['chicken_dataset']['img_dir'] = img_dir
    
    # Also update paths in trainer.data sections if they exist
    if 'trainer' in config_data and 'data' in config_data['trainer']:
        # Update train dataset
        if 'train' in config_data['trainer']['data']:
            train_data = config_data['trainer']['data']['train']
            if 'dataset' in train_data:
                train_data['dataset']['img_folder'] = f"${{chicken_dataset.img_dir}}"
                train_data['dataset']['ann_file'] = f"${{chicken_dataset.train_json}}"
        
        # Update val dataset
        if 'val' in config_data['trainer']['data']:
            val_data = config_data['trainer']['data']['val']
            if 'dataset' in val_data:
                val_data['dataset']['img_folder'] = f"${{chicken_dataset.img_dir}}"
                val_data['dataset']['ann_file'] = f"${{chicken_dataset.val_json}}"
    
    # Update meters/val/chicken/cgf1/pred_file_evaluators if they exist
    if 'trainer' in config_data and 'meters' in config_data['trainer']:
        if 'val' in config_data['trainer']['meters']:
            if 'chicken' in config_data['trainer']['meters']['val']:
                if 'cgf1' in config_data['trainer']['meters']['val']['chicken']:
                    cgf1_config = config_data['trainer']['meters']['val']['chicken']['cgf1']
                    if 'pred_file_evaluators' in cgf1_config:
                        for evaluator in cgf1_config['pred_file_evaluators']:
                            if 'gt_path' in evaluator:
                                evaluator['gt_path'] = f"${{chicken_dataset.val_json}}"
    
    # Write updated config back to file
    print(f"Updating configuration file: {config_path}")
    try:
        # Use yaml.dump with proper formatting
        yaml_str = yaml.dump(config_data, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)
        
        # Fix the package header if it exists
        if not yaml_str.startswith("# @package"):
            # Try to preserve original header
            with open(config_path, 'r') as f:
                original_lines = f.readlines()
                header_lines = [line for line in original_lines[:5] if line.strip().startswith('#') or line.strip().startswith('defaults:')]
                if header_lines:
                    header = ''.join(header_lines)
                    if not header.strip().endswith('\n'):
                        header += '\n'
                    yaml_str = header + '\n' + yaml_str
        
        with open(config_path, 'w') as f:
            f.write(yaml_str)
        
        print("✓ Configuration file updated successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to write config file: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def verify_paths(train_json, val_json, img_dir):
    """Verify that the dataset paths exist."""
    errors = []
    warnings = []
    
    # Check train JSON
    train_path = project_root / train_json
    if not train_path.exists():
        errors.append(f"Training JSON not found: {train_path}")
    else:
        print(f"✓ Found training JSON: {train_path}")
    
    # Check val JSON
    val_path = project_root / val_json
    if not val_path.exists():
        errors.append(f"Validation JSON not found: {val_path}")
    else:
        print(f"✓ Found validation JSON: {val_path}")
    
    # Check image directory
    img_path = project_root / img_dir
    if not img_path.exists():
        errors.append(f"Image directory not found: {img_path}")
    else:
        print(f"✓ Found image directory: {img_path}")
        # Count images as a sanity check
        image_files = list(img_path.rglob("*.jpg")) + list(img_path.rglob("*.jpeg")) + list(img_path.rglob("*.png"))
        if image_files:
            print(f"  Found {len(image_files)} image files")
        else:
            warnings.append(f"No image files found in {img_path}")
    
    return errors, warnings


def main():
    """Update dataset paths in the SAM3 chicken fine-tuning configuration."""
    print("=" * 70)
    print("Task 3.2.2: Define Dataset Paths")
    print("=" * 70)
    print()
    
    # Get paths from config
    config_path = project_root / "configs" / "sam3_chicken_finetune.yaml"
    
    # Dataset paths to set
    train_json = "data/chicken_train.json"
    val_json = "data/chicken_val.json"
    img_dir = "data/images"
    
    print(f"Dataset paths to configure:")
    print(f"  train_json: {train_json}")
    print(f"  val_json: {val_json}")
    print(f"  img_dir: {img_dir}")
    print()
    
    # Verify paths exist
    print("Verifying dataset paths exist...")
    errors, warnings = verify_paths(train_json, val_json, img_dir)
    print()
    
    if errors:
        print("WARNINGS (paths not found):")
        for error in errors:
            print(f"  - {error}")
        print()
        print("The config will be updated anyway, but ensure paths exist before training.")
        print()
    
    if warnings:
        print("Additional warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    # Update config file regardless of path existence (paths might be relative or in different location)
    success = update_dataset_paths(config_path, train_json, val_json, img_dir)
    
    if success:
        print()
        print("✓ Dataset paths configured successfully")
        print()
        print("Next steps:")
        print("  - Task 3.2.3: Set prompt mode configuration")
        print("  - Task 3.2.4: Configure hardware optimization settings")
        print("  - Task 3.3.1: Configure learning rate schedule")
        print("  - Task 3.3.2: Engineer loss weights (especially focal_loss_weight)")
        print("  - Task 3.3.3: Freeze backbone")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
