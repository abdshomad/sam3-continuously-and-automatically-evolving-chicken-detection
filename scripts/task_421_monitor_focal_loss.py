#!/usr/bin/env python3
"""
Task ID: 4.2.1
Description: Monitor Focal Loss (Presence)
Created: 2025-01-15

This script monitors the focal loss curve in WandB to check if it's decreasing steadily.
If the loss stays flat, it suggests increasing loss.focal_loss_weight.

Note: This script should be executed using the wrapper shell script (task_421_monitor_focal_loss.sh)
which handles virtual environment setup via uv. Dependencies (wandb, python-dotenv) should be
declared in pyproject.toml and installed via 'uv sync'.
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Tuple

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


def get_focal_loss_history(api, project_name: str, entity: str, run_id: Optional[str] = None) -> Optional[List[Tuple[int, float]]]:
    """
    Get focal loss history from WandB.
    Returns list of (step, loss_value) tuples.
    """
    try:
        if run_id:
            run = api.run(f"{entity}/{project_name}/{run_id}")
        else:
            # Get the most recent run
            runs = api.runs(f"{entity}/{project_name}", order="-created_at", per_page=1)
            if not runs:
                return None
            run = runs[0]
        
        # Get history for loss_focal metric
        history = run.history(keys=["loss_focal", "train/step"])
        
        if history.empty:
            # Try alternative metric names
            history = run.history(keys=["train/loss_focal", "step"])
            if history.empty:
                history = run.history(keys=["losses/loss_focal", "step"])
        
        if history.empty:
            return None
        
        # Extract step and loss values
        focal_loss_data = []
        for _, row in history.iterrows():
            step = int(row.get('train/step', row.get('step', 0)))
            loss = float(row.get('loss_focal', row.get('train/loss_focal', row.get('losses/loss_focal', None))))
            if loss is not None and not (isinstance(loss, float) and (loss != loss)):  # Check for NaN
                focal_loss_data.append((step, loss))
        
        return focal_loss_data if focal_loss_data else None
        
    except Exception as e:
        print(f"Error fetching focal loss history: {e}", file=sys.stderr)
        return None


def analyze_loss_trend(loss_data: List[Tuple[int, float]], window_size: int = 10) -> str:
    """
    Analyze if the loss is decreasing, flat, or increasing.
    Returns: 'decreasing', 'flat', 'increasing', or 'insufficient_data'
    """
    if len(loss_data) < window_size:
        return 'insufficient_data'
    
    # Get recent window
    recent = loss_data[-window_size:]
    recent_losses = [loss for _, loss in recent]
    
    # Calculate trend: compare first half vs second half of window
    mid = len(recent_losses) // 2
    first_half_avg = sum(recent_losses[:mid]) / len(recent_losses[:mid])
    second_half_avg = sum(recent_losses[mid:]) / len(recent_losses[mid:])
    
    change_percent = ((first_half_avg - second_half_avg) / first_half_avg) * 100 if first_half_avg > 0 else 0
    
    # Threshold: if change is less than 1%, consider it flat
    if abs(change_percent) < 1.0:
        return 'flat'
    elif change_percent > 0:
        return 'decreasing'
    else:
        return 'increasing'


def main():
    print("=" * 50)
    print("Task 4.2.1: Monitor Focal Loss (Presence)")
    print("=" * 50)
    print("")
    
    # Check if WandB is enabled
    use_wandb = getattr(config, 'USE_WANDB', False)
    env_use_wandb = os.getenv('USE_WANDB', '').lower()
    if env_use_wandb in ('true', '1', 'yes', 'on'):
        use_wandb = True
    elif env_use_wandb in ('false', '0', 'no', 'off'):
        use_wandb = False
    
    if not use_wandb:
        print("WandB is disabled in configuration (USE_WANDB=False)")
        print("")
        print("To enable WandB:")
        print("  1. Set USE_WANDB=True in config.py, or")
        print("  2. Set USE_WANDB=true in .env file")
        print("")
        print("Skipping focal loss monitoring.")
        return 0
    
    # Check if wandb is installed
    try:
        import wandb
    except ImportError:
        print("ERROR: wandb is not installed", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please install dependencies:", file=sys.stderr)
        print("  uv sync", file=sys.stderr)
        return 1
    
    # Get project name from config
    project_name = getattr(config, 'WANDB_PROJECT_NAME', 'chicken-detection')
    print(f"WandB project name: {project_name}")
    print("")
    
    # Check for API key
    wandb_api_key = os.getenv('WANDB_API_KEY')
    if not wandb_api_key:
        print("WARNING: WANDB_API_KEY not found in environment variables", file=sys.stderr)
        print("", file=sys.stderr)
        print("The script will attempt to use existing wandb login credentials.", file=sys.stderr)
        print("If this fails, please:", file=sys.stderr)
        print("  1. Get your API key from: https://wandb.ai/authorize", file=sys.stderr)
        print("  2. Add to .env file: WANDB_API_KEY=your_api_key_here", file=sys.stderr)
        print("")
    
    # Initialize WandB API
    try:
        api = wandb.Api()
        # Get entity from viewer - handle both dict and object responses
        entity = None
        try:
            viewer = api.viewer()
            if isinstance(viewer, dict):
                entity = viewer.get('entity') or viewer.get('username')
            else:
                # Try to get entity or username attribute from object
                entity = getattr(viewer, 'entity', None) or getattr(viewer, 'username', None)
                # If still None, try to get from string representation
                if entity is None:
                    viewer_str = str(viewer)
                    # Try to extract from string if it contains entity info
                    if hasattr(viewer, '__dict__'):
                        entity = viewer.__dict__.get('entity') or viewer.__dict__.get('username')
        except Exception as e:
            print(f"Warning: Could not get entity from viewer: {e}")
        
        # Fallback: use environment variable or try to infer from project
        if not entity:
            entity = os.getenv('WANDB_ENTITY')
            if not entity:
                # Try to access a run to infer entity (will fail gracefully if no runs)
                try:
                    # This will work if there are any runs
                    test_runs = api.runs(project_name, per_page=1)
                    if test_runs:
                        # Extract entity from run path
                        run_path = str(test_runs[0])
                        if '/' in run_path:
                            entity = run_path.split('/')[0]
                except Exception:
                    pass
        
        # Final fallback: use username from system
        if not entity:
            import getpass
            entity = getpass.getuser()
            print(f"Warning: Using system username as entity: {entity}")
        
        print(f"Connected to WandB (entity: {entity})")
        print("")
    except Exception as e:
        print(f"ERROR: Could not connect to WandB API: {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please ensure you are logged in:", file=sys.stderr)
        print("  1. Set WANDB_API_KEY in .env file", file=sys.stderr)
        print("  2. Or run: wandb login", file=sys.stderr)
        return 1
    
    # Get run ID from command line or use most recent
    run_id = None
    if len(sys.argv) > 1:
        run_id = sys.argv[1]
        print(f"Monitoring run: {run_id}")
    else:
        print("Monitoring most recent run...")
    print("")
    
    # Fetch focal loss history
    print("Fetching focal loss history from WandB...")
    try:
        loss_data = get_focal_loss_history(api, project_name, entity, run_id)
    except Exception as e:
        print(f"ERROR: Could not fetch focal loss history: {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Troubleshooting:", file=sys.stderr)
        print(f"  - Entity used: {entity}", file=sys.stderr)
        print(f"  - Project: {project_name}", file=sys.stderr)
        if run_id:
            print(f"  - Run ID: {run_id}", file=sys.stderr)
        print("", file=sys.stderr)
        print("You can set the entity explicitly:", file=sys.stderr)
        print("  export WANDB_ENTITY=your_username", file=sys.stderr)
        return 1
    
    if not loss_data:
        print("WARNING: No focal loss data found in the run(s).", file=sys.stderr)
        print("", file=sys.stderr)
        print("Possible reasons:", file=sys.stderr)
        print("  1. Training hasn't started yet", file=sys.stderr)
        print("  2. The metric name is different (expected: 'loss_focal')", file=sys.stderr)
        print("  3. No runs exist in the project yet", file=sys.stderr)
        print("")
        print("To monitor a specific run, provide the run ID:")
        print("  bash scripts/task_421_monitor_focal_loss.sh <run_id>")
        return 1
    
    print(f"Found {len(loss_data)} data points")
    print("")
    
    # Display recent values
    print("Recent focal loss values:")
    recent = loss_data[-10:] if len(loss_data) >= 10 else loss_data
    for step, loss in recent:
        print(f"  Step {step}: {loss:.6f}")
    print("")
    
    # Analyze trend
    trend = analyze_loss_trend(loss_data)
    
    print("Trend Analysis:")
    if trend == 'decreasing':
        print("  ✓ Focal loss is decreasing steadily (GOOD)")
        print("")
        print("The model is learning to suppress 'Not-Chicken' samples.")
        print("No action needed.")
    elif trend == 'flat':
        print("  ⚠ Focal loss is staying flat (WARNING)")
        print("")
        print("The model may be ignoring the 'Not-Chicken' samples.")
        print("")
        print("RECOMMENDATION: Increase loss.focal_loss_weight in config")
        print("")
        print("To fix this:")
        print("  1. Edit configs/sam3_chicken_finetune.yaml")
        print("  2. Find the loss configuration (chicken_dataset.loss)")
        print("  3. Increase the presence_loss weight (currently may be 5.0)")
        print("     Example: presence_loss: 10.0 or higher")
        print("")
        print("Then restart training with the updated config.")
    elif trend == 'increasing':
        print("  ⚠ Focal loss is increasing (WARNING)")
        print("")
        print("The loss is getting worse, which may indicate:")
        print("  - Learning rate is too high")
        print("  - Model instability")
        print("  - Data quality issues")
        print("")
        print("Consider:")
        print("  1. Reducing learning rate")
        print("  2. Checking data quality")
        print("  3. Reviewing training logs for errors")
    else:
        print("  ⚠ Insufficient data to determine trend")
        print("")
        print(f"Only {len(loss_data)} data points available. Need at least 10 for reliable analysis.")
        print("Continue training and check again later.")
    
    print("")
    print("=" * 50)
    print("✓ Focal Loss Monitoring: COMPLETED")
    print("=" * 50)
    print("")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
