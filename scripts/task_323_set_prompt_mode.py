#!/usr/bin/env -S uv run python
"""
Task ID: 3.2.3
Description: Set Prompt Mode
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


def verify_prompt_mode(config_path):
    """Verify that prompt mode is correctly configured in the config file."""
    
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
    
    issues = []
    fixes_applied = []
    
    # Check train dataset configuration
    train_dataset = None
    if 'trainer' in config_data and 'data' in config_data['trainer']:
        if 'train' in config_data['trainer']['data']:
            train_data = config_data['trainer']['data']['train']
            if 'dataset' in train_data:
                train_dataset = train_data['dataset']
    
    if train_dataset:
        # Verify use_text_prompts
        if 'use_text_prompts' not in train_dataset:
            train_dataset['use_text_prompts'] = True
            fixes_applied.append("Added use_text_prompts: true to train dataset")
        elif train_dataset.get('use_text_prompts') != True:
            train_dataset['use_text_prompts'] = True
            fixes_applied.append("Updated use_text_prompts to true in train dataset")
        else:
            print("✓ Train dataset: use_text_prompts is correctly set to true")
        
        # Verify prompt_column
        if 'prompt_column' not in train_dataset:
            train_dataset['prompt_column'] = 'text_input'
            fixes_applied.append("Added prompt_column: 'text_input' to train dataset")
        elif train_dataset.get('prompt_column') != 'text_input':
            train_dataset['prompt_column'] = 'text_input'
            fixes_applied.append(f"Updated prompt_column to 'text_input' in train dataset (was: {train_dataset.get('prompt_column')})")
        else:
            print("✓ Train dataset: prompt_column is correctly set to 'text_input'")
    else:
        issues.append("Train dataset configuration not found")
    
    # Check val dataset configuration
    val_dataset = None
    if 'trainer' in config_data and 'data' in config_data['trainer']:
        if 'val' in config_data['trainer']['data']:
            val_data = config_data['trainer']['data']['val']
            if 'dataset' in val_data:
                val_dataset = val_data['dataset']
    
    if val_dataset:
        # Verify use_text_prompts
        if 'use_text_prompts' not in val_dataset:
            val_dataset['use_text_prompts'] = True
            fixes_applied.append("Added use_text_prompts: true to val dataset")
        elif val_dataset.get('use_text_prompts') != True:
            val_dataset['use_text_prompts'] = True
            fixes_applied.append("Updated use_text_prompts to true in val dataset")
        else:
            print("✓ Val dataset: use_text_prompts is correctly set to true")
        
        # Verify prompt_column
        if 'prompt_column' not in val_dataset:
            val_dataset['prompt_column'] = 'text_input'
            fixes_applied.append("Added prompt_column: 'text_input' to val dataset")
        elif val_dataset.get('prompt_column') != 'text_input':
            val_dataset['prompt_column'] = 'text_input'
            fixes_applied.append(f"Updated prompt_column to 'text_input' in val dataset (was: {val_dataset.get('prompt_column')})")
        else:
            print("✓ Val dataset: prompt_column is correctly set to 'text_input'")
    else:
        issues.append("Val dataset configuration not found")
    
    # Write updated config back to file if fixes were applied
    if fixes_applied:
        print(f"\nApplying {len(fixes_applied)} fix(es)...")
        for fix in fixes_applied:
            print(f"  - {fix}")
        
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
    
    if issues:
        print("\nWARNINGS:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    if not fixes_applied:
        print("\n✓ Prompt mode is already correctly configured in both train and val datasets")
        print("  - use_text_prompts: true")
        print("  - prompt_column: 'text_input'")
    
    return True


def main():
    """Verify and configure prompt mode settings in the SAM3 chicken fine-tuning configuration."""
    print("=" * 70)
    print("Task 3.2.3: Set Prompt Mode")
    print("=" * 70)
    print()
    
    config_path = project_root / "configs" / "sam3_chicken_finetune.yaml"
    
    print("Verifying prompt mode configuration...")
    print(f"Config file: {config_path}")
    print()
    
    success = verify_prompt_mode(config_path)
    
    if success:
        print()
        print("✓ Prompt mode configuration verified and updated successfully")
        print()
        print("Configuration ensures:")
        print("  - Data loader is configured for Prompted Class Segmentation (PCS)")
        print("  - use_text_prompts: true (enables text prompt support)")
        print("  - prompt_column: 'text_input' (specifies the column name in SA-Co JSON)")
        print()
        print("Next steps:")
        print("  - Task 3.2.4: Configure hardware optimization settings")
        print("  - Task 3.3.1: Configure learning rate schedule")
        return 0
    else:
        print()
        print("✗ Some issues were found. Please review the warnings above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
