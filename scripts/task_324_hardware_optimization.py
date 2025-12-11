#!/usr/bin/env -S uv run python
"""
Task ID: 3.2.4
Description: Hardware Optimization
Created: 2025-01-15

Note: This script should be executed using 'uv run python script.py' to ensure
the virtual environment is used. Dependencies should be declared in pyproject.toml
and installed via 'uv sync' before running this script.
"""

import sys
import yaml
import subprocess
import re
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


def detect_gpu_model():
    """Detect GPU model to determine optimal precision setting."""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            gpu_name = result.stdout.strip().upper()
            print(f"Detected GPU: {gpu_name}")
            
            # Check for A100/H100 (support bfloat16)
            if 'A100' in gpu_name or 'H100' in gpu_name:
                return 'bf16', 'A100/H100'
            # Check for V100 (fp16 only)
            elif 'V100' in gpu_name:
                return 'fp16', 'V100'
            # Check for RTX series (fp16)
            elif 'RTX' in gpu_name or 'GTX' in gpu_name:
                return 'fp16', 'RTX/GTX'
            else:
                # Default to fp16 for unknown GPUs
                return 'fp16', 'Unknown (defaulting to fp16)'
        else:
            print("WARNING: Could not detect GPU model. Defaulting to fp16.")
            return 'fp16', 'Unknown'
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
        print(f"WARNING: Could not run nvidia-smi: {e}")
        print("Defaulting to fp16 precision.")
        return 'fp16', 'Unknown'


def configure_hardware_optimization(config_path):
    """Configure hardware optimization settings in the config file."""
    
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
    
    # Detect GPU and determine precision
    precision, gpu_info = detect_gpu_model()
    print(f"Recommended precision: {precision} (for {gpu_info})")
    print()
    
    # Configure precision in optim.amp section
    if 'trainer' not in config_data:
        config_data['trainer'] = {}
    
    if 'optim' not in config_data['trainer']:
        config_data['trainer']['optim'] = {}
    
    if 'amp' not in config_data['trainer']['optim']:
        config_data['trainer']['optim']['amp'] = {}
        changes_made.append("Created optim.amp section")
    
    amp_config = config_data['trainer']['optim']['amp']
    
    # Enable AMP if not already enabled
    if 'enabled' not in amp_config or not amp_config.get('enabled'):
        amp_config['enabled'] = True
        changes_made.append("Enabled AMP (Automatic Mixed Precision)")
    
    # Set precision dtype
    if precision == 'bf16':
        target_dtype = 'bfloat16'
    else:
        target_dtype = 'float16'
    
    if 'amp_dtype' not in amp_config:
        amp_config['amp_dtype'] = target_dtype
        changes_made.append(f"Set amp_dtype to {target_dtype}")
    elif amp_config.get('amp_dtype') != target_dtype:
        old_dtype = amp_config.get('amp_dtype')
        amp_config['amp_dtype'] = target_dtype
        changes_made.append(f"Updated amp_dtype from {old_dtype} to {target_dtype}")
    else:
        print(f"✓ AMP dtype is already set to {target_dtype}")
    
    # Configure gradient checkpointing
    # Note: SAM3 model builder doesn't directly expose gradient checkpointing,
    # but we can add it to the model config if the trainer supports it
    # For now, we'll add a note that gradient checkpointing should be enabled
    # at the model level if supported
    
    # Check if model section exists and add use_act_checkpoint if possible
    if 'trainer' in config_data and 'model' in config_data['trainer']:
        model_config = config_data['trainer']['model']
        
        # Check if we can add use_act_checkpoint parameter
        # This depends on whether the model builder supports it
        # For now, we'll document it in a comment or add it if the structure allows
        if isinstance(model_config, dict):
            # Note: Gradient checkpointing in SAM3 is typically handled at the component level
            # (e.g., in vision_backbone, text_encoder) via use_act_checkpoint parameter
            # Since the model is built via _target_, we can't directly set this,
            # but we document that it should be enabled if the model builder supports it
            print("Note: Gradient checkpointing in SAM3 is handled at component level")
            print("      (vision_backbone, text_encoder) via use_act_checkpoint parameter.")
            print("      The model builder will need to support this parameter.")
    
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
        print("\n✓ Hardware optimization settings are already correctly configured")
    
    return True


def main():
    """Configure hardware optimization settings in the SAM3 chicken fine-tuning configuration."""
    print("=" * 70)
    print("Task 3.2.4: Hardware Optimization")
    print("=" * 70)
    print()
    
    config_path = project_root / "configs" / "sam3_chicken_finetune.yaml"
    
    print("Configuring hardware optimization settings...")
    print(f"Config file: {config_path}")
    print()
    
    success = configure_hardware_optimization(config_path)
    
    if success:
        print()
        print("✓ Hardware optimization configuration completed successfully")
        print()
        print("Configuration includes:")
        print("  - AMP (Automatic Mixed Precision) enabled")
        print("  - Precision set based on GPU capabilities (bf16 for A100/H100, fp16 for others)")
        print("  - Note: Gradient checkpointing is handled at component level in SAM3")
        print()
        print("Next steps:")
        print("  - Task 3.3.1: Configure learning rate schedule")
        print("  - Task 3.3.2: Engineer loss weights (especially focal_loss_weight)")
        print("  - Task 3.3.3: Freeze backbone")
        return 0
    else:
        print()
        print("✗ Configuration failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
