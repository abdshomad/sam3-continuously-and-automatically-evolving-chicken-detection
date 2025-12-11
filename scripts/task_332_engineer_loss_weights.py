#!/usr/bin/env -S uv run python
"""
Task ID: 3.3.2
Description: Engineer Loss Weights
Created: 2025-01-15

This script updates the SAM3 chicken finetune configuration to engineer loss weights:
- Boost the Focal Loss (presence_loss) to 5.0 to penalize hallucinations
- Set dice_loss_weight to 1.0
- Set iou_loss_weight to 1.0

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


def update_loss_weights(config: Dict[str, Any]) -> bool:
    """
    Update loss weights in the configuration.
    
    Returns:
        True if changes were made, False otherwise
    """
    changes_made = False
    
    # Navigate to the loss configuration (under chicken_dataset)
    if 'chicken_dataset' not in config:
        print("Error: 'chicken_dataset' section not found in configuration", file=sys.stderr)
        return False
    
    chicken_dataset = config['chicken_dataset']
    
    if 'loss' not in chicken_dataset:
        print("Error: 'loss' section not found in chicken_dataset", file=sys.stderr)
        return False
    
    loss_config = chicken_dataset['loss']
    
    # Check for loss_fns_find
    if 'loss_fns_find' not in loss_config:
        print("Error: 'loss.loss_fns_find' not found in configuration", file=sys.stderr)
        return False
    
    loss_fns = loss_config['loss_fns_find']
    
    # Update presence_loss in IABCEMdetr (index 1)
    if len(loss_fns) > 1:
        iabcem_config = loss_fns[1]
        if '_target_' in iabcem_config and 'IABCEMdetr' in iabcem_config['_target_']:
            if 'weight_dict' in iabcem_config:
                weight_dict = iabcem_config['weight_dict']
                if 'presence_loss' in weight_dict:
                    old_value = weight_dict['presence_loss']
                    if old_value != 5.0:
                        weight_dict['presence_loss'] = 5.0
                        print(f"Updated presence_loss: {old_value} -> 5.0")
                        changes_made = True
                    else:
                        print(f"presence_loss already set to 5.0")
                else:
                    print("Warning: 'presence_loss' not found in IABCEMdetr weight_dict", file=sys.stderr)
    
    # Update loss_dice and loss_iou in Masks (index 2)
    if len(loss_fns) > 2:
        masks_config = loss_fns[2]
        if '_target_' in masks_config and 'Masks' in masks_config['_target_']:
            if 'weight_dict' in masks_config:
                weight_dict = masks_config['weight_dict']
                
                # Update loss_dice
                if 'loss_dice' in weight_dict:
                    old_value = weight_dict['loss_dice']
                    if old_value != 1.0:
                        weight_dict['loss_dice'] = 1.0
                        print(f"Updated loss_dice: {old_value} -> 1.0")
                        changes_made = True
                    else:
                        print(f"loss_dice already set to 1.0")
                else:
                    print("Warning: 'loss_dice' not found in Masks weight_dict", file=sys.stderr)
                
                # Verify loss_iou (should already be 1.0)
                if 'loss_iou' in weight_dict:
                    if weight_dict['loss_iou'] != 1.0:
                        weight_dict['loss_iou'] = 1.0
                        print(f"Updated loss_iou: {weight_dict['loss_iou']} -> 1.0")
                        changes_made = True
                    else:
                        print(f"loss_iou already set to 1.0")
                else:
                    print("Warning: 'loss_iou' not found in Masks weight_dict", file=sys.stderr)
    
    return changes_made


def main():
    """Main function to update loss weights in configuration."""
    # Get project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    config_path = project_root / 'configs' / 'sam3_chicken_finetune.yaml'
    
    print(f"Loading configuration from: {config_path}")
    config = load_yaml_config(config_path)
    
    print("Updating loss weights...")
    changes_made = update_loss_weights(config)
    
    if changes_made:
        print("Saving updated configuration...")
        save_yaml_config(config, config_path)
        print(f"Successfully updated loss weights in {config_path}")
        return 0
    else:
        print("No changes were made to the configuration.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
