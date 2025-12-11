#!/usr/bin/env -S uv run python
"""
Task ID: 3.3.3
Description: Freeze Backbone
Created: 2025-01-15

This script updates the SAM3 chicken finetune configuration to freeze the vision backbone.
Freezing the backbone limits gradients to the Mask Decoder and Presence Head, saving VRAM
and training time while preserving general visual knowledge.

The freezing is implemented by setting the learning rate for the vision backbone to 0,
which effectively prevents parameter updates during training.

Note: This script should be executed using 'uv run python script.py' to ensure
the virtual environment is used. Dependencies (pyyaml) should be declared in
pyproject.toml and installed via 'uv sync' before running this script.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """Load YAML configuration file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML file: {e}", file=sys.stderr)
        sys.exit(1)


def save_yaml_config(config: Dict[str, Any], config_path: Path) -> None:
    """Save YAML configuration file."""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    except Exception as e:
        print(f"Error: Failed to save YAML file: {e}", file=sys.stderr)
        sys.exit(1)


def freeze_backbone(config: Dict[str, Any]) -> bool:
    """
    Freeze the vision backbone by setting its learning rate to 0.
    
    Returns:
        True if changes were made, False otherwise
    """
    changes_made = False
    
    # Navigate to the scratch configuration
    if 'scratch' not in config:
        print("Error: 'scratch' section not found in configuration", file=sys.stderr)
        return False
    
    scratch_config = config['scratch']
    
    # Set lr_vision_backbone to 0 to freeze the backbone
    if 'lr_vision_backbone' in scratch_config:
        old_value = scratch_config['lr_vision_backbone']
        # Check if it's already 0 or a formula that evaluates to 0
        if old_value != 0 and old_value != '${times:0,${scratch.lr_scale}}':
            scratch_config['lr_vision_backbone'] = 0
            print(f"Updated lr_vision_backbone: {old_value} -> 0 (frozen)")
            changes_made = True
        else:
            print(f"lr_vision_backbone already set to 0 (backbone is frozen)")
    else:
        # Add lr_vision_backbone if it doesn't exist
        scratch_config['lr_vision_backbone'] = 0
        print("Added lr_vision_backbone: 0 (frozen)")
        changes_made = True
    
    # Also update the optimizer scheduler to ensure backbone params get 0 LR
    # Check if optim section exists
    if 'trainer' in config and 'optim' in config['trainer']:
        optim_config = config['trainer']['optim']
        if 'options' in optim_config and 'lr' in optim_config['options']:
            lr_schedulers = optim_config['options']['lr']
            # Find the scheduler for vision backbone
            for scheduler in lr_schedulers:
                if 'param_names' in scheduler:
                    param_names = scheduler['param_names']
                    if isinstance(param_names, list) and any('backbone.vision_backbone' in str(p) for p in param_names):
                        if 'base_lr' in scheduler:
                            old_lr = scheduler['base_lr']
                            if old_lr != 0:
                                scheduler['base_lr'] = 0
                                print(f"Updated optimizer scheduler base_lr for vision_backbone: {old_lr} -> 0")
                                changes_made = True
                            else:
                                print("Optimizer scheduler for vision_backbone already set to 0")
    
    return changes_made


def main():
    """Main function to freeze backbone in configuration."""
    # Get project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    config_path = project_root / 'configs' / 'sam3_chicken_finetune.yaml'
    
    print(f"Loading configuration from: {config_path}")
    config = load_yaml_config(config_path)
    
    print("Freezing vision backbone...")
    changes_made = freeze_backbone(config)
    
    if changes_made:
        print("Saving updated configuration...")
        save_yaml_config(config, config_path)
        print(f"Successfully froze vision backbone in {config_path}")
        print("")
        print("Note: The vision backbone is now frozen (lr=0). Only the Mask Decoder")
        print("and Presence Head will be updated during training.")
        return 0
    else:
        print("No changes were made to the configuration.")
        print("The backbone may already be frozen.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
