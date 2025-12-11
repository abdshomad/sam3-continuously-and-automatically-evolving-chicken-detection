#!/usr/bin/env python3
"""
Task ID: 4.2.3
Description: Watch Gradient Norms
Created: 2025-01-15

This script monitors gradient norms in WandB to detect spikes that indicate instability.
If spikes are observed, it recommends lowering the learning rate or increasing warm-up steps.

Note: This script should be executed using the wrapper shell script (task_423_watch_gradient_norms.sh)
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


def get_gradient_norm_history(api, project_name: str, entity: str, run_id: Optional[str] = None) -> Optional[List[Tuple[int, float]]]:
    """
    Get gradient norm history from WandB.
    Returns list of (step, grad_norm_value) tuples.
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
            "grad_norm",
            "train/grad_norm",
            "gradient_norm",
            "train/gradient_norm",
            "trainer/grad_norm",
            "optimizer/grad_norm",
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
        
        # Extract step and grad norm values
        grad_norm_data = []
        for _, row in history.iterrows():
            step = int(row.get('train/step', row.get('step', 0)))
            grad_norm = None
            for pattern in metric_patterns:
                if pattern in row and row[pattern] is not None:
                    grad_norm = float(row[pattern])
                    break
            
            if grad_norm is not None and not (isinstance(grad_norm, float) and (grad_norm != grad_norm)):  # Check for NaN
                grad_norm_data.append((step, grad_norm))
        
        return grad_norm_data if grad_norm_data else None
        
    except Exception as e:
        print(f"Error fetching gradient norm history: {e}", file=sys.stderr)
        return None


def detect_spikes(grad_norm_data: List[Tuple[int, float]], window_size: int = 20, spike_threshold: float = 2.0) -> List[Tuple[int, float, float]]:
    """
    Detect spikes in gradient norms.
    Returns list of (step, grad_norm, spike_ratio) tuples where spike_ratio is how many
    standard deviations above the mean the value is.
    
    Args:
        grad_norm_data: List of (step, grad_norm) tuples
        window_size: Number of previous values to use for baseline calculation
        spike_threshold: Number of standard deviations above mean to consider a spike
    """
    if len(grad_norm_data) < window_size + 1:
        return []
    
    spikes = []
    values = [grad_norm for _, grad_norm in grad_norm_data]
    
    for i in range(window_size, len(grad_norm_data)):
        # Calculate baseline from previous window
        baseline = values[i - window_size:i]
        baseline_mean = sum(baseline) / len(baseline)
        baseline_std = (sum((x - baseline_mean) ** 2 for x in baseline) / len(baseline)) ** 0.5
        
        if baseline_std == 0:
            continue
        
        current_value = values[i]
        current_step, _ = grad_norm_data[i]
        
        # Calculate how many standard deviations above the mean
        z_score = (current_value - baseline_mean) / baseline_std
        
        if z_score > spike_threshold:
            spikes.append((current_step, current_value, z_score))
    
    return spikes


def analyze_gradient_stability(grad_norm_data: List[Tuple[int, float]]) -> dict:
    """
    Analyze gradient norm stability.
    Returns a dictionary with analysis results.
    """
    if len(grad_norm_data) < 10:
        return {
            'status': 'insufficient_data',
            'mean': None,
            'std': None,
            'max': None,
            'min': None,
            'spikes': [],
        }
    
    values = [grad_norm for _, grad_norm in grad_norm_data]
    mean = sum(values) / len(values)
    std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
    max_val = max(values)
    min_val = min(values)
    
    # Detect spikes
    spikes = detect_spikes(grad_norm_data, window_size=min(20, len(grad_norm_data) // 2))
    
    # Determine stability status
    if len(spikes) > len(grad_norm_data) * 0.1:  # More than 10% are spikes
        status = 'unstable'
    elif len(spikes) > 0:
        status = 'moderate_instability'
    elif std / mean > 0.5 if mean > 0 else False:  # High variance
        status = 'high_variance'
    else:
        status = 'stable'
    
    return {
        'status': status,
        'mean': mean,
        'std': std,
        'max': max_val,
        'min': min_val,
        'spikes': spikes,
    }


def main():
    print("=" * 50)
    print("Task 4.2.3: Watch Gradient Norms")
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
        print("Skipping gradient norm monitoring.")
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
    
    # Fetch gradient norm history
    print("Fetching gradient norm history from WandB...")
    grad_norm_data = get_gradient_norm_history(api, project_name, entity, run_id)
    
    if not grad_norm_data:
        print("WARNING: No gradient norm data found in the run(s).", file=sys.stderr)
        print("", file=sys.stderr)
        print("Possible reasons:", file=sys.stderr)
        print("  1. Training hasn't started yet", file=sys.stderr)
        print("  2. The metric name is different (expected: 'grad_norm')", file=sys.stderr)
        print("  3. No runs exist in the project yet", file=sys.stderr)
        print("  4. Gradient clipping may be disabled", file=sys.stderr)
        print("")
        print("To monitor a specific run, provide the run ID:")
        print("  bash scripts/task_423_watch_gradient_norms.sh <run_id>")
        return 1
    
    print(f"Found {len(grad_norm_data)} gradient norm data points")
    print("")
    
    # Display recent values
    print("Recent gradient norm values:")
    recent = grad_norm_data[-10:] if len(grad_norm_data) >= 10 else grad_norm_data
    for step, grad_norm in recent:
        print(f"  Step {step}: {grad_norm:.6f}")
    print("")
    
    # Analyze stability
    analysis = analyze_gradient_stability(grad_norm_data)
    
    print("Gradient Norm Statistics:")
    print(f"  Mean: {analysis['mean']:.6f}")
    print(f"  Std Dev: {analysis['std']:.6f}")
    print(f"  Min: {analysis['min']:.6f}")
    print(f"  Max: {analysis['max']:.6f}")
    print("")
    
    # Report spikes
    if analysis['spikes']:
        print(f"⚠ Detected {len(analysis['spikes'])} spike(s) in gradient norms:")
        for step, value, z_score in analysis['spikes'][:10]:  # Show first 10 spikes
            print(f"  Step {step}: {value:.6f} ({z_score:.2f}σ above mean)")
        if len(analysis['spikes']) > 10:
            print(f"  ... and {len(analysis['spikes']) - 10} more spike(s)")
        print("")
    
    # Provide recommendations
    print("=" * 50)
    print("Stability Analysis:")
    print("=" * 50)
    
    if analysis['status'] == 'insufficient_data':
        print("⚠ Insufficient data to determine stability")
        print(f"Only {len(grad_norm_data)} data points available. Need at least 10 for reliable analysis.")
        print("Continue training and check again later.")
    elif analysis['status'] == 'stable':
        print("✓ Gradient norms are stable (GOOD)")
        print("")
        print("No action needed. Training appears to be stable.")
    elif analysis['status'] == 'high_variance':
        print("⚠ Gradient norms show high variance (WARNING)")
        print("")
        print("RECOMMENDATIONS:")
        print("  1. Consider reducing learning rate")
        print("  2. Increase warm-up steps to stabilize early training")
        print("  3. Check if batch size is too small")
        print("")
        print("To fix this:")
        print("  1. Edit configs/sam3_chicken_finetune.yaml")
        print("  2. Reduce learning rate (e.g., multiply by 0.5)")
        print("  3. Increase scheduler_warmup (e.g., from 1500 to 3000)")
    elif analysis['status'] == 'moderate_instability':
        print("⚠ Gradient norms show moderate instability (WARNING)")
        print("")
        print("RECOMMENDATIONS:")
        print("  1. Reduce learning rate by 50%")
        print("  2. Increase warm-up steps by 50-100%")
        print("  3. Consider enabling gradient clipping if not already enabled")
        print("")
        print("To fix this:")
        print("  1. Edit configs/sam3_chicken_finetune.yaml")
        print("  2. Reduce learning rate in scratch.lr_transformer")
        print("  3. Increase scratch.scheduler_warmup")
        print("  4. Check trainer.optim.gradient_clip.max_norm is set (should be 0.1)")
    elif analysis['status'] == 'unstable':
        print("⚠⚠ Gradient norms are highly unstable (CRITICAL)")
        print("")
        print("RECOMMENDATIONS:")
        print("  1. Immediately reduce learning rate by 50-75%")
        print("  2. Double or triple warm-up steps")
        print("  3. Verify gradient clipping is enabled and set appropriately")
        print("  4. Consider reducing batch size if very small")
        print("  5. Check for data quality issues")
        print("")
        print("To fix this:")
        print("  1. Edit configs/sam3_chicken_finetune.yaml")
        print("  2. Reduce scratch.lr_transformer significantly (e.g., multiply by 0.25)")
        print("  3. Increase scratch.scheduler_warmup (e.g., from 1500 to 4500)")
        print("  4. Verify trainer.optim.gradient_clip.max_norm is 0.1")
        print("  5. Restart training with the updated configuration")
    
    print("")
    print("=" * 50)
    print("✓ Gradient Norm Monitoring: COMPLETED")
    print("=" * 50)
    print("")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
