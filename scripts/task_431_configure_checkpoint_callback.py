#!/usr/bin/env python3
"""
Task ID: 4.3.1
Description: Configure Checkpoint Callback
Created: 2025-01-15

This script ensures the Hydra config saves top-k checkpoints based on validation loss:
- checkpoint.monitor: "val_loss"
- checkpoint.save_top_k: 3

Note: This script should be executed using the wrapper shell script (task_431_configure_checkpoint_callback.sh)
which handles virtual environment setup via uv. Dependencies (pyyaml, python-dotenv) should be
declared in pyproject.toml and installed via 'uv sync'.
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

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


def find_config_file() -> Optional[Path]:
    """
    Find the SAM3 chicken fine-tuning config file.
    Checks common locations: configs/sam3_chicken_finetune.yaml
    """
    possible_paths = [
        project_root / "configs" / "sam3_chicken_finetune.yaml",
        project_root / "sam3" / "sam3" / "train" / "configs" / "sam3_chicken_finetune.yaml",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """Load YAML config file."""
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        print("ERROR: PyYAML is not installed", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please install dependencies:", file=sys.stderr)
        print("  uv sync", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load config file: {e}", file=sys.stderr)
        sys.exit(1)


def save_yaml_config(config_path: Path, config_data: Dict[str, Any]) -> None:
    """Save YAML config file with proper formatting."""
    try:
        import yaml
        # Use default_flow_style=False for better readability
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    except Exception as e:
        print(f"ERROR: Failed to save config file: {e}", file=sys.stderr)
        sys.exit(1)


def update_checkpoint_config(config_data: Dict[str, Any], monitor: str = "val_loss", save_top_k: int = 3) -> bool:
    """
    Update checkpoint configuration in the config data.
    Returns True if changes were made, False otherwise.
    """
    # Navigate to trainer.checkpoint section
    if 'trainer' not in config_data:
        config_data['trainer'] = {}
    
    if 'checkpoint' not in config_data['trainer']:
        config_data['trainer']['checkpoint'] = {}
    
    checkpoint_config = config_data['trainer']['checkpoint']
    changes_made = False
    
    # Update monitor
    if checkpoint_config.get('monitor') != monitor:
        checkpoint_config['monitor'] = monitor
        changes_made = True
    
    # Update save_top_k
    if checkpoint_config.get('save_top_k') != save_top_k:
        checkpoint_config['save_top_k'] = save_top_k
        changes_made = True
    
    return changes_made


def main():
    print("=" * 50)
    print("Task 4.3.1: Configure Checkpoint Callback")
    print("=" * 50)
    print("")
    
    # Find config file
    config_path = find_config_file()
    if not config_path:
        print("ERROR: Could not find sam3_chicken_finetune.yaml config file", file=sys.stderr)
        print("", file=sys.stderr)
        print("Searched in:")
        print("  - configs/sam3_chicken_finetune.yaml")
        print("  - sam3/sam3/train/configs/sam3_chicken_finetune.yaml")
        print("", file=sys.stderr)
        print("Please ensure the config file exists or create it first.")
        return 1
    
    print(f"Found config file: {config_path}")
    print("")
    
    # Load config
    print("Loading configuration...")
    config_data = load_yaml_config(config_path)
    print("✓ Configuration loaded")
    print("")
    
    # Check current checkpoint settings
    current_monitor = None
    current_save_top_k = None
    
    if 'trainer' in config_data and 'checkpoint' in config_data['trainer']:
        checkpoint_config = config_data['trainer']['checkpoint']
        current_monitor = checkpoint_config.get('monitor')
        current_save_top_k = checkpoint_config.get('save_top_k')
    
    print("Current checkpoint configuration:")
    print(f"  monitor: {current_monitor}")
    print(f"  save_top_k: {current_save_top_k}")
    print("")
    
    # Update checkpoint configuration
    print("Updating checkpoint configuration...")
    print("  Setting monitor: 'val_loss'")
    print("  Setting save_top_k: 3")
    print("")
    
    changes_made = update_checkpoint_config(config_data, monitor="val_loss", save_top_k=3)
    
    if not changes_made:
        print("✓ Checkpoint configuration is already correct")
        print("  No changes needed.")
    else:
        # Save config
        print("Saving updated configuration...")
        save_yaml_config(config_path, config_data)
        print("✓ Configuration saved")
        print("")
        
        # Verify the changes
        print("Verifying changes...")
        updated_config = load_yaml_config(config_path)
        if 'trainer' in updated_config and 'checkpoint' in updated_config['trainer']:
            checkpoint_config = updated_config['trainer']['checkpoint']
            new_monitor = checkpoint_config.get('monitor')
            new_save_top_k = checkpoint_config.get('save_top_k')
            
            print(f"  monitor: {new_monitor}")
            print(f"  save_top_k: {new_save_top_k}")
            print("")
            
            if new_monitor == "val_loss" and new_save_top_k == 3:
                print("✓ Checkpoint configuration verified successfully")
            else:
                print("⚠ WARNING: Configuration may not have been updated correctly", file=sys.stderr)
                return 1
    
    print("")
    print("=" * 50)
    print("Checkpoint Configuration Summary:")
    print("=" * 50)
    print("")
    print("The checkpoint callback is now configured to:")
    print("  - Monitor: 'val_loss' (validation loss)")
    print("  - Save top-k: 3 (saves the 3 best checkpoints based on validation loss)")
    print("")
    print("This ensures that:")
    print("  - The best-performing model versions are saved")
    print("  - Progress is preserved even if later epochs overfit")
    print("  - You can compare different checkpoint versions")
    print("")
    print("=" * 50)
    print("✓ Checkpoint Callback Configuration: COMPLETED")
    print("=" * 50)
    print("")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
