#!/usr/bin/env -S uv run python
"""
Task ID: 3.3.1
Description: Configure Learning Rate
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


def configure_learning_rate(config_path):
    """Configure conservative learning rate schedule in the config file."""
    
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
    
    changes_made = []
    
    # Target conservative learning rate: 1e-5 for transformer (main component)
    target_lr = 1e-5
    
    # Get max_epochs to calculate warmup steps (5-10% of epochs)
    max_epochs = config_data.get('trainer', {}).get('max_epochs', 20)
    print(f"Max epochs: {max_epochs}")
    
    # Calculate warmup steps (5-10% of total training)
    # Assuming ~1500 steps per epoch (target_epoch_size), warmup should be 5-10% of total steps
    target_epoch_size = config_data.get('scratch', {}).get('target_epoch_size', 1500)
    total_steps = max_epochs * target_epoch_size
    warmup_steps_min = int(total_steps * 0.05)  # 5%
    warmup_steps_max = int(total_steps * 0.10)  # 10%
    warmup_steps = warmup_steps_min  # Use 5% for conservative approach
    print(f"Calculated warmup steps: {warmup_steps} (5% of {total_steps} total steps)")
    
    # Ensure scratch section exists
    if 'scratch' not in config_data:
        config_data['scratch'] = {}
        changes_made.append("Created scratch section")
    
    scratch = config_data['scratch']
    
    # Configure learning rate scale to achieve target LR
    # Current: lr_transformer = 8e-4 * lr_scale
    # Target: lr_transformer = 1e-5
    # So: lr_scale = 1e-5 / 8e-4 = 0.0125
    target_lr_scale = target_lr / 8e-4
    
    if 'lr_scale' not in scratch:
        scratch['lr_scale'] = target_lr_scale
        changes_made.append(f"Set lr_scale to {target_lr_scale:.6f} (target LR: {target_lr})")
    else:
        current_lr_scale = scratch.get('lr_scale', 0.1)
        # Calculate what the current effective LR is
        current_effective_lr = 8e-4 * current_lr_scale
        if abs(current_effective_lr - target_lr) > target_lr * 0.1:  # More than 10% difference
            scratch['lr_scale'] = target_lr_scale
            changes_made.append(f"Updated lr_scale from {current_lr_scale} to {target_lr_scale:.6f}")
            print(f"  Previous effective LR: {current_effective_lr:.2e}")
            print(f"  New effective LR: {target_lr:.2e}")
        else:
            print(f"✓ lr_scale is already set appropriately (effective LR: {current_effective_lr:.2e})")
    
    # Verify learning rate definitions
    if 'lr_transformer' not in scratch:
        scratch['lr_transformer'] = '${times:8e-4,${scratch.lr_scale}}'
        changes_made.append("Added lr_transformer definition")
    else:
        print("✓ lr_transformer is defined")
    
    if 'lr_vision_backbone' not in scratch:
        scratch['lr_vision_backbone'] = '${times:2.5e-4,${scratch.lr_scale}}'
        changes_made.append("Added lr_vision_backbone definition")
    else:
        print("✓ lr_vision_backbone is defined")
    
    if 'lr_language_backbone' not in scratch:
        scratch['lr_language_backbone'] = '${times:5e-5,${scratch.lr_scale}}'
        changes_made.append("Added lr_language_backbone definition")
    else:
        print("✓ lr_language_backbone is defined")
    
    # Configure scheduler warmup steps
    # Note: SAM3 uses InverseSquareRootParamScheduler, not cosine annealing
    # but it does support warmup and cooldown, which provides similar behavior
    if 'scheduler_warmup' not in scratch:
        scratch['scheduler_warmup'] = warmup_steps
        changes_made.append(f"Set scheduler_warmup to {warmup_steps} steps (5% of total)")
    else:
        current_warmup = scratch.get('scheduler_warmup', 20)
        if current_warmup < warmup_steps_min or current_warmup > warmup_steps_max:
            old_warmup = current_warmup
            scratch['scheduler_warmup'] = warmup_steps
            changes_made.append(f"Updated scheduler_warmup from {old_warmup} to {warmup_steps} steps")
        else:
            print(f"✓ scheduler_warmup is already set appropriately ({current_warmup} steps)")
    
    # Ensure scheduler_timescale and scheduler_cooldown are set
    if 'scheduler_timescale' not in scratch:
        # Timescale should be roughly the number of steps for one epoch
        scratch['scheduler_timescale'] = target_epoch_size
        changes_made.append(f"Set scheduler_timescale to {target_epoch_size}")
    else:
        print("✓ scheduler_timescale is defined")
    
    if 'scheduler_cooldown' not in scratch:
        # Cooldown can be similar to warmup
        scratch['scheduler_cooldown'] = warmup_steps
        changes_made.append(f"Set scheduler_cooldown to {warmup_steps} steps")
    else:
        print("✓ scheduler_cooldown is defined")
    
    # Verify scheduler configuration in trainer.optim section
    if 'trainer' in config_data and 'optim' in config_data['trainer']:
        optim = config_data['trainer']['optim']
        if 'options' in optim and 'lr' in optim['options']:
            lr_schedulers = optim['options']['lr']
            print(f"\nFound {len(lr_schedulers)} learning rate scheduler(s)")
            
            # Verify all schedulers use warmup
            for i, scheduler_config in enumerate(lr_schedulers):
                if 'scheduler' in scheduler_config:
                    sched = scheduler_config['scheduler']
                    if 'warmup_steps' in sched:
                        current_warmup = sched.get('warmup_steps')
                        if isinstance(current_warmup, str) and '${scratch.scheduler_warmup}' in current_warmup:
                            print(f"✓ Scheduler {i+1}: warmup_steps references scratch.scheduler_warmup")
                        elif isinstance(current_warmup, (int, float)) and (current_warmup < warmup_steps_min or current_warmup > warmup_steps_max):
                            sched['warmup_steps'] = '${scratch.scheduler_warmup}'
                            changes_made.append(f"Updated scheduler {i+1} warmup_steps to reference scratch.scheduler_warmup")
                    else:
                        sched['warmup_steps'] = '${scratch.scheduler_warmup}'
                        changes_made.append(f"Added warmup_steps to scheduler {i+1}")
    
    # Write updated config back to file
    if changes_made:
        print(f"\nApplying {len(changes_made)} change(s)...")
        for change in changes_made:
            print(f"  - {change}")
        
        try:
            # Read original file to preserve formatting
            with open(config_path, 'r') as f:
                original_content = f.read()
            
            # Write updated config
            yaml_str = yaml.dump(config_data, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)
            
            # Preserve header if it exists
            if original_content.startswith("# @package"):
                header_lines = []
                for line in original_content.split('\n')[:10]:
                    if line.strip().startswith('#') or line.strip().startswith('defaults:'):
                        header_lines.append(line)
                if header_lines:
                    header = '\n'.join(header_lines) + '\n'
                    yaml_str = header + yaml_str
            
            with open(config_path, 'w') as f:
                f.write(yaml_str)
            
            print(f"\n✓ Configuration file updated successfully")
        except Exception as e:
            print(f"ERROR: Failed to write config file: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return False
    else:
        print("\n✓ Learning rate schedule is already correctly configured")
    
    # Print summary
    print("\n" + "=" * 70)
    print("Learning Rate Configuration Summary:")
    print("=" * 70)
    effective_lr_transformer = 8e-4 * scratch.get('lr_scale', target_lr_scale)
    effective_lr_vision = 2.5e-4 * scratch.get('lr_scale', target_lr_scale)
    effective_lr_language = 5e-5 * scratch.get('lr_scale', target_lr_scale)
    print(f"  Transformer LR: {effective_lr_transformer:.2e}")
    print(f"  Vision Backbone LR: {effective_lr_vision:.2e}")
    print(f"  Language Backbone LR: {effective_lr_language:.2e}")
    print(f"  Warmup Steps: {scratch.get('scheduler_warmup', warmup_steps)} ({scratch.get('scheduler_warmup', warmup_steps) / total_steps * 100:.1f}% of total)")
    print(f"  Scheduler: InverseSquareRootParamScheduler (with warmup and cooldown)")
    print("  Note: SAM3 uses InverseSquareRootParamScheduler instead of cosine annealing,")
    print("        but it provides similar behavior with warmup and cooldown phases.")
    print("=" * 70)
    
    return True


def main():
    """Configure learning rate schedule in the SAM3 chicken fine-tuning configuration."""
    print("=" * 70)
    print("Task 3.3.1: Configure Learning Rate")
    print("=" * 70)
    print()
    
    config_path = project_root / "configs" / "sam3_chicken_finetune.yaml"
    
    print("Configuring conservative learning rate schedule...")
    print(f"Config file: {config_path}")
    print()
    
    success = configure_learning_rate(config_path)
    
    if success:
        print()
        print("✓ Learning rate configuration completed successfully")
        print()
        print("Configuration ensures:")
        print("  - Conservative learning rate (~1e-5) to protect pre-trained backbone")
        print("  - Warmup period (5% of training) to stabilize gradients")
        print("  - InverseSquareRootParamScheduler with warmup and cooldown")
        print("  - Different learning rates for transformer, vision, and language components")
        print()
        print("Next steps:")
        print("  - Task 3.3.2: Engineer loss weights (especially focal_loss_weight)")
        print("  - Task 3.3.3: Freeze backbone")
        return 0
    else:
        print()
        print("✗ Configuration failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
