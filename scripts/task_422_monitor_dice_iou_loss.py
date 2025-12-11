#!/usr/bin/env python3
"""
Task ID: 4.2.2
Description: Monitor Dice/IoU Loss (Masks)
Created: 2025-01-15

This script monitors the dice loss and IoU loss curves in WandB to check if they're decreasing
for positive samples. These losses should decrease only for positive samples.

Note: This script should be executed using the wrapper shell script (task_422_monitor_dice_iou_loss.sh)
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


def get_loss_history(api, project_name: str, entity: str, metric_name: str, run_id: Optional[str] = None) -> Optional[List[Tuple[int, float]]]:
    """
    Get loss history from WandB for a specific metric.
    Returns list of (step, loss_value) tuples.
    """
    try:
        if run_id:
            try:
                run = api.run(f"{entity}/{project_name}/{run_id}")
            except Exception:
                return None
        else:
            # Get the most recent run
            try:
                runs = api.runs(f"{entity}/{project_name}", order="-created_at", per_page=1)
                if not runs or len(runs) == 0:
                    return None
                run = runs[0]
            except Exception:
                return None
        
        # Try various metric name patterns
        metric_patterns = [
            metric_name,
            f"train/{metric_name}",
            f"losses/{metric_name}",
            f"train/losses/{metric_name}",
        ]
        
        history = None
        for pattern in metric_patterns:
            try:
                history = run.history(keys=[pattern, "train/step", "step"])
                if not history.empty:
                    break
            except Exception:
                continue
        
        if history is None or history.empty:
            return None
        
        # Extract step and loss values
        loss_data = []
        for _, row in history.iterrows():
            step = int(row.get('train/step', row.get('step', 0)))
            loss = None
            for pattern in metric_patterns:
                if pattern in row and row[pattern] is not None:
                    loss = float(row[pattern])
                    break
            
            if loss is not None and not (isinstance(loss, float) and (loss != loss)):  # Check for NaN
                loss_data.append((step, loss))
        
        return loss_data if loss_data else None
        
    except Exception as e:
        print(f"Error fetching {metric_name} history: {e}", file=sys.stderr)
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
    print("Task 4.2.2: Monitor Dice/IoU Loss (Masks)")
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
        print("Skipping dice/IoU loss monitoring.")
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
                entity = getattr(viewer, 'entity', None) or getattr(viewer, 'username', None)
                if entity is None and hasattr(viewer, '__dict__'):
                    entity = viewer.__dict__.get('entity') or viewer.__dict__.get('username')
        except Exception as e:
            print(f"Warning: Could not get entity from viewer: {e}")
        
        # Fallback: use environment variable or try to infer from project
        if not entity:
            entity = os.getenv('WANDB_ENTITY')
            if not entity:
                try:
                    test_runs = api.runs(project_name, per_page=1)
                    if test_runs:
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
    
    # Fetch dice loss history
    print("Fetching dice loss history from WandB...")
    dice_loss_data = get_loss_history(api, project_name, entity, "loss_dice", run_id)
    
    # Fetch IoU loss history
    print("Fetching IoU loss history from WandB...")
    iou_loss_data = get_loss_history(api, project_name, entity, "loss_iou", run_id)
    
    if not dice_loss_data and not iou_loss_data:
        print("WARNING: No dice or IoU loss data found in the run(s).", file=sys.stderr)
        print("", file=sys.stderr)
        print("Possible reasons:", file=sys.stderr)
        print("  1. Training hasn't started yet", file=sys.stderr)
        print("  2. The metric names are different (expected: 'loss_dice', 'loss_iou')", file=sys.stderr)
        print("  3. No runs exist in the project yet", file=sys.stderr)
        print("")
        print("To monitor a specific run, provide the run ID:")
        print("  bash scripts/task_422_monitor_dice_iou_loss.sh <run_id>")
        return 1
    
    # Analyze Dice Loss
    if dice_loss_data:
        print(f"Found {len(dice_loss_data)} dice loss data points")
        print("")
        print("Recent dice loss values:")
        recent = dice_loss_data[-10:] if len(dice_loss_data) >= 10 else dice_loss_data
        for step, loss in recent:
            print(f"  Step {step}: {loss:.6f}")
        print("")
        
        dice_trend = analyze_loss_trend(dice_loss_data)
        print("Dice Loss Trend Analysis:")
        if dice_trend == 'decreasing':
            print("  ✓ Dice loss is decreasing steadily (GOOD)")
            print("  The model is learning to segment positive samples accurately.")
        elif dice_trend == 'flat':
            print("  ⚠ Dice loss is staying flat (WARNING)")
            print("  The model may not be learning to segment masks effectively.")
            print("  Consider checking:")
            print("    - Learning rate may be too low")
            print("    - Data quality issues")
            print("    - Model capacity limitations")
        elif dice_trend == 'increasing':
            print("  ⚠ Dice loss is increasing (WARNING)")
            print("  The loss is getting worse, which may indicate:")
            print("    - Learning rate is too high")
            print("    - Model instability")
            print("    - Data quality issues")
        else:
            print(f"  ⚠ Insufficient data to determine trend ({len(dice_loss_data)} data points)")
        print("")
    else:
        print("WARNING: No dice loss data found")
        print("")
    
    # Analyze IoU Loss
    if iou_loss_data:
        print(f"Found {len(iou_loss_data)} IoU loss data points")
        print("")
        print("Recent IoU loss values:")
        recent = iou_loss_data[-10:] if len(iou_loss_data) >= 10 else iou_loss_data
        for step, loss in recent:
            print(f"  Step {step}: {loss:.6f}")
        print("")
        
        iou_trend = analyze_loss_trend(iou_loss_data)
        print("IoU Loss Trend Analysis:")
        if iou_trend == 'decreasing':
            print("  ✓ IoU loss is decreasing steadily (GOOD)")
            print("  The model is learning to segment positive samples accurately.")
        elif iou_trend == 'flat':
            print("  ⚠ IoU loss is staying flat (WARNING)")
            print("  The model may not be learning to segment masks effectively.")
            print("  Consider checking:")
            print("    - Learning rate may be too low")
            print("    - Data quality issues")
            print("    - Model capacity limitations")
        elif iou_trend == 'increasing':
            print("  ⚠ IoU loss is increasing (WARNING)")
            print("  The loss is getting worse, which may indicate:")
            print("    - Learning rate is too high")
            print("    - Model instability")
            print("    - Data quality issues")
        else:
            print(f"  ⚠ Insufficient data to determine trend ({len(iou_loss_data)} data points)")
        print("")
    else:
        print("WARNING: No IoU loss data found")
        print("")
    
    # Overall summary
    print("=" * 50)
    print("Summary:")
    print("=" * 50)
    if dice_loss_data and iou_loss_data:
        dice_trend = analyze_loss_trend(dice_loss_data)
        iou_trend = analyze_loss_trend(iou_loss_data)
        if dice_trend == 'decreasing' and iou_trend == 'decreasing':
            print("✓ Both dice and IoU losses are decreasing (EXCELLENT)")
            print("The model is learning to segment positive samples effectively.")
        elif dice_trend == 'decreasing' or iou_trend == 'decreasing':
            print("⚠ One loss is decreasing, but the other needs attention")
        else:
            print("⚠ Both losses need attention - review training configuration")
    elif dice_loss_data:
        dice_trend = analyze_loss_trend(dice_loss_data)
        if dice_trend == 'decreasing':
            print("✓ Dice loss is decreasing (GOOD)")
        else:
            print("⚠ Dice loss needs attention")
    elif iou_loss_data:
        iou_trend = analyze_loss_trend(iou_loss_data)
        if iou_trend == 'decreasing':
            print("✓ IoU loss is decreasing (GOOD)")
        else:
            print("⚠ IoU loss needs attention")
    
    print("")
    print("=" * 50)
    print("✓ Dice/IoU Loss Monitoring: COMPLETED")
    print("=" * 50)
    print("")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
