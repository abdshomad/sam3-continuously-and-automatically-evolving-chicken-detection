#!/usr/bin/env -S uv run python
"""
Task ID: 4.1.3
Description: Batch Size Tuning
Created: 2025-01-15

This script monitors VRAM usage via nvidia-smi and adjusts batch size in the config
based on utilization:
- If utilization < 80%, increase train.batch_size
- If OOM occurs, decrease batch size and enable train.accumulate_grad_batches=2

Note: This script should be executed using 'uv run python script.py' to ensure
the virtual environment is used. Dependencies (pyyaml, omegaconf) should be
declared in pyproject.toml and installed via 'uv sync' before running this script.
"""

import sys
import os
import subprocess
from pathlib import Path

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


def check_nvidia_smi():
    """Check if nvidia-smi is available."""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_vram_utilization():
    """
    Get current VRAM utilization percentage.
    Returns tuple: (used_mb, total_mb, utilization_percent)
    """
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the first GPU's memory info
        lines = result.stdout.strip().split('\n')
        if not lines or not lines[0]:
            return None, None, None
        
        # Format: "used_mb, total_mb"
        parts = lines[0].split(',')
        if len(parts) != 2:
            return None, None, None
        
        used_mb = int(parts[0].strip())
        total_mb = int(parts[1].strip())
        utilization = (used_mb / total_mb) * 100 if total_mb > 0 else 0
        
        return used_mb, total_mb, utilization
    except subprocess.CalledProcessError as e:
        print(f"Error running nvidia-smi: {e}", file=sys.stderr)
        return None, None, None
    except ValueError as e:
        print(f"Error parsing nvidia-smi output: {e}", file=sys.stderr)
        return None, None, None


def load_yaml_config(config_path):
    """Load YAML config file using omegaconf or yaml."""
    try:
        from omegaconf import OmegaConf
        return OmegaConf.load(config_path)
    except ImportError:
        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except ImportError:
            print("Error: Neither omegaconf nor pyyaml is available.", file=sys.stderr)
            print("Please install dependencies: uv sync", file=sys.stderr)
            sys.exit(1)


def save_yaml_config(config_path, config_data):
    """Save YAML config file using omegaconf or yaml."""
    try:
        from omegaconf import OmegaConf
        OmegaConf.save(config_data, config_path)
    except ImportError:
        try:
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        except ImportError:
            print("Error: Neither omegaconf nor pyyaml is available.", file=sys.stderr)
            sys.exit(1)


def get_nested_value(config_data, key_path, default=None):
    """Get nested value from config using dot notation (e.g., 'scratch.train_batch_size')."""
    keys = key_path.split('.')
    value = config_data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        elif hasattr(value, key):  # For OmegaConf objects
            value = getattr(value, key)
        else:
            return default
        if value is None:
            return default
    return value


def set_nested_value(config_data, key_path, value):
    """Set nested value in config using dot notation."""
    keys = key_path.split('.')
    current = config_data
    
    # Navigate to the parent of the target key
    for key in keys[:-1]:
        if isinstance(current, dict):
            if key not in current:
                current[key] = {}
            current = current[key]
        elif hasattr(current, key):  # For OmegaConf objects
            if not hasattr(current, '__setitem__'):
                # OmegaConf - use setattr or OmegaConf.set
                try:
                    from omegaconf import OmegaConf
                    OmegaConf.set(current, key, {})
                    current = getattr(current, key)
                except:
                    setattr(current, key, {})
                    current = getattr(current, key)
            else:
                current = current[key]
        else:
            # Create nested structure
            if isinstance(current, dict):
                current[key] = {}
                current = current[key]
            else:
                # For OmegaConf, we need to set it differently
                try:
                    from omegaconf import OmegaConf
                    OmegaConf.set(current, key, {})
                    current = getattr(current, key)
                except:
                    return False
    
    # Set the final value
    final_key = keys[-1]
    if isinstance(current, dict):
        current[final_key] = value
    elif hasattr(current, '__setitem__'):
        current[final_key] = value
    else:
        # For OmegaConf
        try:
            from omegaconf import OmegaConf
            OmegaConf.set(current, final_key, value)
        except:
            return False
    
    return True


def main():
    print("=" * 50)
    print("Task 4.1.3: Batch Size Tuning")
    print("=" * 50)
    print("")
    
    # Check if nvidia-smi is available
    if not check_nvidia_smi():
        print("ERROR: nvidia-smi not found. This script requires NVIDIA GPUs.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please ensure:", file=sys.stderr)
        print("  1. NVIDIA drivers are installed", file=sys.stderr)
        print("  2. nvidia-smi is in PATH", file=sys.stderr)
        return 1
    
    # Get VRAM utilization
    print("Checking VRAM utilization...")
    used_mb, total_mb, utilization = get_vram_utilization()
    
    if utilization is None:
        print("ERROR: Could not get VRAM utilization", file=sys.stderr)
        return 1
    
    print(f"Current VRAM usage: {used_mb} MB / {total_mb} MB ({utilization:.1f}%)")
    print("")
    
    # Load config file
    config_path = project_root / "configs" / "sam3_chicken_finetune.yaml"
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        return 1
    
    print(f"Loading config: {config_path}")
    config_data = load_yaml_config(config_path)
    
    # Get current batch size and gradient accumulation
    current_batch_size = get_nested_value(config_data, 'scratch.train_batch_size', 4)
    current_grad_accum = get_nested_value(config_data, 'scratch.gradient_accumulation_steps', 1)
    
    print(f"Current batch size: {current_batch_size}")
    print(f"Current gradient accumulation steps: {current_grad_accum}")
    print("")
    
    # Determine action based on utilization
    action_taken = False
    
    if utilization < 80:
        # Increase batch size
        new_batch_size = min(current_batch_size * 2, 32)  # Cap at 32
        if new_batch_size > current_batch_size:
            print(f"VRAM utilization ({utilization:.1f}%) is below 80%")
            print(f"Increasing batch size from {current_batch_size} to {new_batch_size}")
            set_nested_value(config_data, 'scratch.train_batch_size', new_batch_size)
            action_taken = True
        else:
            print(f"Batch size is already at maximum recommended value ({current_batch_size})")
    else:
        print(f"VRAM utilization ({utilization:.1f}%) is at or above 80%")
        print("No batch size increase recommended.")
        print("")
        print("If you experience OOM (Out of Memory) errors:")
        print("  1. Decrease batch size")
        print("  2. Enable gradient accumulation")
        print("")
        print("To manually adjust:")
        print(f"  - Edit {config_path}")
        print("  - Set scratch.train_batch_size to a lower value (e.g., 2)")
        print("  - Set scratch.gradient_accumulation_steps to 2 or higher")
    
    # Check for OOM flag (if provided as environment variable or argument)
    if len(sys.argv) > 1 and sys.argv[1] == '--oom':
        print("")
        print("OOM flag detected. Adjusting for out-of-memory conditions...")
        new_batch_size = max(current_batch_size // 2, 1)
        new_grad_accum = max(current_grad_accum * 2, 2)
        
        print(f"Decreasing batch size from {current_batch_size} to {new_batch_size}")
        print(f"Increasing gradient accumulation from {current_grad_accum} to {new_grad_accum}")
        
        set_nested_value(config_data, 'scratch.train_batch_size', new_batch_size)
        set_nested_value(config_data, 'scratch.gradient_accumulation_steps', new_grad_accum)
        action_taken = True
    
    # Save config if changes were made
    if action_taken:
        print("")
        print(f"Saving updated config to {config_path}")
        save_yaml_config(config_path, config_data)
        print("✓ Config updated successfully")
        print("")
        print("Next steps:")
        print("  1. Review the updated config file")
        print("  2. Restart training with the new batch size")
    else:
        print("")
        print("No changes made to config file.")
    
    print("")
    print("=" * 50)
    print("✓ Batch Size Tuning: COMPLETED")
    print("=" * 50)
    print("")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
