#!/usr/bin/env -S uv run python
"""
Task ID: 3.1.2
Description: Calculate Baseline Metrics
Created: 2025-12-12

Note: This script should be executed using 'uv run python script.py' to ensure
the virtual environment is used. Dependencies should be declared in pyproject.toml
and installed via 'uv sync' before running this script.
"""

import sys
import json
import os
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

# Add sam3 to path for imports
sam3_path = project_root / "sam3"
if sam3_path.exists():
    sys.path.insert(0, str(sam3_path))


def find_prediction_file(results_dir):
    """Find the prediction JSON file from evaluation results."""
    results_path = Path(results_dir)
    if not results_path.exists():
        return None
    
    # Look for COCO format prediction files
    # Typically in dumps/chicken_val/coco_predictions_segm.json
    possible_paths = [
        results_path / "dumps" / "chicken_val" / "coco_predictions_segm.json",
        results_path / "dumps" / "chicken_val" / "coco_predictions_bbox.json",
        results_path / "coco_predictions_segm.json",
        results_path / "coco_predictions_bbox.json",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # Try to find any JSON file with "prediction" or "coco" in the name
    for json_file in results_path.rglob("*.json"):
        if "prediction" in json_file.name.lower() or "coco" in json_file.name.lower():
            return json_file
    
    return None


def calculate_metrics_from_evaluator(gt_path, pred_path, iou_type="segm"):
    """Calculate metrics using CGF1Evaluator."""
    try:
        from sam3.eval.cgf1_eval import CGF1Evaluator
        
        print(f"Loading ground truth from: {gt_path}")
        print(f"Loading predictions from: {pred_path}")
        print()
        
        evaluator = CGF1Evaluator(
            gt_path=str(gt_path),
            verbose=True,
            iou_type=iou_type
        )
        
        summary = evaluator.evaluate(str(pred_path))
        
        return summary
    except ImportError as e:
        print(f"ERROR: Failed to import CGF1Evaluator: {e}", file=sys.stderr)
        print("Make sure SAM3 submodule is initialized and dependencies are installed.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Failed to calculate metrics: {e}", file=sys.stderr)
        return None


def extract_metrics(summary, iou_type="segm"):
    """Extract pmF1, IL_MCC, and calculate CGF1 from evaluation summary."""
    if summary is None:
        return None
    
    # Key names in the summary dictionary
    pmf1_key = f"cgF1_eval_{iou_type}_positive_micro_F1"
    il_mcc_key = f"cgF1_eval_{iou_type}_IL_MCC"
    cgf1_key = f"cgF1_eval_{iou_type}_cgF1"
    
    # Try to get metrics
    pmf1 = summary.get(pmf1_key, None)
    il_mcc = summary.get(il_mcc_key, None)
    cgf1 = summary.get(cgf1_key, None)
    
    # If CGF1 is not directly available, calculate it
    if cgf1 is None and pmf1 is not None and il_mcc is not None:
        cgf1 = pmf1 * il_mcc
    
    return {
        "pmF1": pmf1,
        "IL_MCC": il_mcc,
        "CGF1": cgf1,
        "raw_summary": summary
    }


def log_to_wandb(metrics):
    """Log metrics to WandB if enabled."""
    if not config.USE_WANDB:
        return
    
    try:
        import wandb
        wandb_api_key = os.getenv('WANDB_API_KEY')
        if not wandb_api_key:
            print("WARNING: WandB enabled but WANDB_API_KEY not found in .env", file=sys.stderr)
            return
        
        # Initialize wandb if not already initialized
        if wandb.run is None:
            wandb.init(
                project=config.WANDB_PROJECT_NAME,
                name="zero-shot-baseline",
                config={"task": "3.1.2", "description": "Baseline metrics calculation"}
            )
        
        # Log metrics
        log_dict = {}
        if metrics["pmF1"] is not None:
            log_dict["baseline/pmF1"] = metrics["pmF1"]
        if metrics["IL_MCC"] is not None:
            log_dict["baseline/IL_MCC"] = metrics["IL_MCC"]
        if metrics["CGF1"] is not None:
            log_dict["baseline/CGF1"] = metrics["CGF1"]
        
        if log_dict:
            wandb.log(log_dict)
            print("✓ Metrics logged to WandB")
    except ImportError:
        print("WARNING: wandb not available, skipping WandB logging", file=sys.stderr)
    except Exception as e:
        print(f"WARNING: Failed to log to WandB: {e}", file=sys.stderr)


def main():
    """Calculate baseline metrics from zero-shot evaluation results."""
    print("=" * 50)
    print("Task 3.1.2: Calculate Baseline Metrics")
    print("=" * 50)
    print()
    
    # Get paths from config (project_root already set above)
    val_json_path = project_root / config.DEFAULT_DATA_PATH / "chicken_val.json"
    results_dir = project_root / "results" / "zero_shot_baseline"
    
    # Check if validation JSON exists
    if not val_json_path.exists():
        print(f"ERROR: Validation JSON not found: {val_json_path}", file=sys.stderr)
        print("Please run Phase 2 tasks first to generate chicken_val.json.", file=sys.stderr)
        return 1
    
    # Find prediction file
    pred_path = find_prediction_file(results_dir)
    if pred_path is None:
        print(f"ERROR: Prediction file not found in results directory: {results_dir}", file=sys.stderr)
        print("Please run task 3.1.1 first to generate predictions.", file=sys.stderr)
        return 1
    
    print(f"Ground truth: {val_json_path}")
    print(f"Predictions: {pred_path}")
    print()
    
    # Calculate metrics for segmentation (preferred)
    print("Calculating metrics for segmentation (segm)...")
    summary_segm = calculate_metrics_from_evaluator(val_json_path, pred_path, iou_type="segm")
    
    if summary_segm is None:
        # Try bbox as fallback
        print("\nTrying bbox evaluation as fallback...")
        summary_bbox = calculate_metrics_from_evaluator(val_json_path, pred_path, iou_type="bbox")
        if summary_bbox is None:
            print("ERROR: Failed to calculate metrics", file=sys.stderr)
            return 1
        summary = summary_bbox
        iou_type = "bbox"
    else:
        summary = summary_segm
        iou_type = "segm"
    
    # Extract metrics
    metrics = extract_metrics(summary, iou_type=iou_type)
    
    if metrics is None:
        print("ERROR: Failed to extract metrics from evaluation summary", file=sys.stderr)
        return 1
    
    # Display results
    print()
    print("=" * 50)
    print("Baseline Metrics (Zero-Shot)")
    print("=" * 50)
    print()
    
    if metrics["pmF1"] is not None:
        print(f"pmF1 (Prompt-Mask F1): {metrics['pmF1']:.4f}")
    else:
        print("pmF1: Not available")
    
    if metrics["IL_MCC"] is not None:
        print(f"IL_MCC (Image-Level Matthews Correlation Coefficient): {metrics['IL_MCC']:.4f}")
    else:
        print("IL_MCC: Not available")
    
    if metrics["CGF1"] is not None:
        print(f"CGF1 (Composite Score = pmF1 × IL_MCC): {metrics['CGF1']:.4f}")
    else:
        print("CGF1: Not available")
    
    print()
    
    # Save metrics to JSON file
    results_file = project_root / "results" / "baseline_metrics.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    output_metrics = {
        "pmF1": metrics["pmF1"],
        "IL_MCC": metrics["IL_MCC"],
        "CGF1": metrics["CGF1"],
        "iou_type": iou_type,
        "gt_path": str(val_json_path),
        "pred_path": str(pred_path)
    }
    
    with open(results_file, 'w') as f:
        json.dump(output_metrics, f, indent=2)
    
    print(f"✓ Metrics saved to: {results_file}")
    print()
    
    # Log to WandB if enabled
    if config.USE_WANDB:
        log_to_wandb(metrics)
        print()
    
    print("=" * 50)
    print("✓ Baseline metrics calculation completed")
    print("=" * 50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
