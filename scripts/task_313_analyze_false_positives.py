#!/usr/bin/env -S uv run python
"""
Task ID: 3.1.3
Description: Analyze False Positives
Created: 2025-01-15

Note: This script should be executed using 'uv run python script.py' to ensure
the virtual environment is used. Dependencies should be declared in pyproject.toml
and installed via 'uv sync' before running this script.
"""

import sys
import json
import os
from pathlib import Path
from collections import defaultdict
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


def identify_negative_images(gt_data):
    """
    Identify images that are "Not-Chicken" (negative samples).
    These are images with no annotations in the ground truth.
    """
    # Build a set of image IDs that have annotations
    images_with_annotations = set()
    if "annotations" in gt_data:
        for ann in gt_data["annotations"]:
            images_with_annotations.add(ann["image_id"])
    
    # Negative images are those NOT in the set above
    negative_image_ids = set()
    if "images" in gt_data:
        for img in gt_data["images"]:
            img_id = img["id"]
            if img_id not in images_with_annotations:
                negative_image_ids.add(img_id)
    
    return negative_image_ids


def analyze_false_positives(gt_data, pred_data, negative_image_ids):
    """
    Analyze false positives: detections on negative (Not-Chicken) images.
    """
    # Group predictions by image_id
    predictions_by_image = defaultdict(list)
    for pred in pred_data:
        img_id = pred.get("image_id")
        if img_id is not None:
            predictions_by_image[img_id].append(pred)
    
    # Analyze false positives on negative images
    false_positive_stats = {
        "total_negative_images": len(negative_image_ids),
        "negative_images_with_detections": 0,
        "total_false_positives": 0,
        "false_positive_images": [],
        "avg_detections_per_negative_image": 0.0,
        "max_detections_on_single_image": 0,
        "presence_scores": []
    }
    
    # Create image ID to file name mapping
    image_id_to_filename = {}
    if "images" in gt_data:
        for img in gt_data["images"]:
            image_id_to_filename[img["id"]] = img.get("file_name", f"image_{img['id']}")
    
    # Analyze each negative image
    for img_id in negative_image_ids:
        if img_id in predictions_by_image:
            detections = predictions_by_image[img_id]
            num_detections = len(detections)
            
            if num_detections > 0:
                false_positive_stats["negative_images_with_detections"] += 1
                false_positive_stats["total_false_positives"] += num_detections
                false_positive_stats["max_detections_on_single_image"] = max(
                    false_positive_stats["max_detections_on_single_image"],
                    num_detections
                )
                
                # Extract scores (presence or confidence scores)
                scores = [det.get("score", 0.0) for det in detections]
                avg_score = sum(scores) / len(scores) if scores else 0.0
                max_score = max(scores) if scores else 0.0
                
                false_positive_stats["false_positive_images"].append({
                    "image_id": img_id,
                    "file_name": image_id_to_filename.get(img_id, f"image_{img_id}"),
                    "num_detections": num_detections,
                    "avg_score": avg_score,
                    "max_score": max_score,
                    "scores": scores
                })
                
                # Track presence scores
                false_positive_stats["presence_scores"].extend(scores)
    
    # Calculate average detections per negative image
    if false_positive_stats["total_negative_images"] > 0:
        false_positive_stats["avg_detections_per_negative_image"] = (
            false_positive_stats["total_false_positives"] / 
            false_positive_stats["total_negative_images"]
        )
    
    # Calculate statistics on presence scores
    if false_positive_stats["presence_scores"]:
        scores = false_positive_stats["presence_scores"]
        false_positive_stats["avg_presence_score"] = sum(scores) / len(scores)
        false_positive_stats["min_presence_score"] = min(scores)
        false_positive_stats["max_presence_score"] = max(scores)
    else:
        false_positive_stats["avg_presence_score"] = 0.0
        false_positive_stats["min_presence_score"] = 0.0
        false_positive_stats["max_presence_score"] = 0.0
    
    return false_positive_stats


def generate_report(stats, output_file):
    """Generate a text report of false positive analysis."""
    report_lines = [
        "=" * 70,
        "False Positive Analysis Report (Zero-Shot Baseline)",
        "=" * 70,
        "",
        "SUMMARY:",
        f"  Total negative images (Not-Chicken): {stats['total_negative_images']}",
        f"  Negative images with detections (False Positives): {stats['negative_images_with_detections']}",
        f"  Total false positive detections: {stats['total_false_positives']}",
        f"  Average detections per negative image: {stats['avg_detections_per_negative_image']:.2f}",
        f"  Max detections on a single negative image: {stats['max_detections_on_single_image']}",
        "",
        "PRESENCE SCORES (on false positives):",
        f"  Average: {stats.get('avg_presence_score', 0.0):.4f}",
        f"  Minimum: {stats.get('min_presence_score', 0.0):.4f}",
        f"  Maximum: {stats.get('max_presence_score', 0.0):.4f}",
        "",
        "INTERPRETATION:",
    ]
    
    if stats['total_negative_images'] == 0:
        report_lines.append("  ⚠️  No negative images found in validation set.")
    elif stats['negative_images_with_detections'] == 0:
        report_lines.append("  ✓ No false positives detected - model correctly rejects negative images.")
        report_lines.append("  This is excellent! The model does not hallucinate chickens in empty scenes.")
    else:
        false_positive_rate = (
            stats['negative_images_with_detections'] / stats['total_negative_images'] * 100
        )
        report_lines.append(f"  ⚠️  False positive rate: {false_positive_rate:.1f}% of negative images have detections")
        
        if false_positive_rate > 50:
            report_lines.append("  ❌ HIGH FALSE POSITIVE RATE - Model is hallucinating chickens frequently.")
            report_lines.append("  This confirms the need for fine-tuning with negative samples.")
        elif false_positive_rate > 20:
            report_lines.append("  ⚠️  MODERATE FALSE POSITIVE RATE - Some false detections on background.")
            report_lines.append("  Fine-tuning should improve background rejection.")
        else:
            report_lines.append("  ✓ LOW FALSE POSITIVE RATE - Few false detections.")
            report_lines.append("  Fine-tuning may still help improve precision.")
        
        if stats.get('avg_presence_score', 0.0) > 0.5:
            report_lines.append("  ⚠️  High average presence scores (>0.5) indicate confident false detections.")
        elif stats.get('avg_presence_score', 0.0) > 0.1:
            report_lines.append("  ⚠️  Moderate presence scores (0.1-0.5) indicate ambiguous detections.")
        else:
            report_lines.append("  ✓ Low presence scores (<0.1) indicate weak/uncertain false detections.")
    
    report_lines.extend([
        "",
        "TOP FALSE POSITIVE IMAGES (by detection count):",
    ])
    
    # Sort false positive images by number of detections (descending)
    sorted_fp_images = sorted(
        stats['false_positive_images'],
        key=lambda x: x['num_detections'],
        reverse=True
    )[:10]  # Show top 10
    
    if sorted_fp_images:
        for i, fp_img in enumerate(sorted_fp_images, 1):
            report_lines.append(
                f"  {i}. {fp_img['file_name']} - "
                f"{fp_img['num_detections']} detections, "
                f"avg score: {fp_img['avg_score']:.4f}, "
                f"max score: {fp_img['max_score']:.4f}"
            )
    else:
        report_lines.append("  (None)")
    
    report_lines.extend([
        "",
        "=" * 70,
    ])
    
    report_text = "\n".join(report_lines)
    
    # Print to console
    print(report_text)
    
    # Save to file
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report_text)
        print(f"\n✓ Report saved to: {output_file}")
    
    return report_text


def main():
    """Analyze false positives from zero-shot inference results."""
    print("=" * 70)
    print("Task 3.1.3: Analyze False Positives")
    print("=" * 70)
    print()
    
    # Get paths from config
    val_json_path = project_root / config.DEFAULT_DATA_PATH / "chicken_val.json"
    results_dir = project_root / "results" / "zero_shot_baseline"
    
    # Check if validation JSON exists
    if not val_json_path.exists():
        print(f"ERROR: Validation JSON not found: {val_json_path}", file=sys.stderr)
        print("Please run Phase 2 tasks first to generate chicken_val.json.", file=sys.stderr)
        return 1
    
    # Load ground truth
    print(f"Loading ground truth from: {val_json_path}")
    try:
        with open(val_json_path, 'r') as f:
            gt_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load ground truth JSON: {e}", file=sys.stderr)
        return 1
    
    # Find prediction file
    pred_path = find_prediction_file(results_dir)
    if pred_path is None:
        print(f"WARNING: Prediction file not found in results directory: {results_dir}", file=sys.stderr)
        print("Zero-shot inference may not have been run yet.", file=sys.stderr)
        print("Please run task 3.1.1 first to generate predictions.", file=sys.stderr)
        print()
        print("Continuing with analysis based on ground truth only...")
        print()
        
        # Still identify negative images for reference
        negative_image_ids = identify_negative_images(gt_data)
        print(f"Found {len(negative_image_ids)} negative images (Not-Chicken) in validation set.")
        print("Run zero-shot inference (task 3.1.1) to analyze false positives.")
        return 1
    
    # Load predictions
    print(f"Loading predictions from: {pred_path}")
    try:
        with open(pred_path, 'r') as f:
            pred_data = json.load(f)
        
        # Handle both list format and COCO format
        if isinstance(pred_data, dict) and "annotations" in pred_data:
            pred_data = pred_data["annotations"]
        elif not isinstance(pred_data, list):
            print(f"ERROR: Unexpected prediction format. Expected list or COCO dict.", file=sys.stderr)
            return 1
        
    except Exception as e:
        print(f"ERROR: Failed to load prediction JSON: {e}", file=sys.stderr)
        return 1
    
    print(f"Loaded {len(pred_data)} predictions")
    print()
    
    # Identify negative images
    print("Identifying negative images (Not-Chicken)...")
    negative_image_ids = identify_negative_images(gt_data)
    print(f"Found {len(negative_image_ids)} negative images")
    print()
    
    # Analyze false positives
    print("Analyzing false positives...")
    stats = analyze_false_positives(gt_data, pred_data, negative_image_ids)
    print()
    
    # Generate and save report
    report_file = project_root / "results" / "false_positive_analysis.txt"
    generate_report(stats, report_file)
    
    # Save detailed stats to JSON
    stats_json_file = project_root / "results" / "false_positive_stats.json"
    stats_json_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert sets to lists for JSON serialization
    stats_for_json = stats.copy()
    stats_for_json["negative_image_ids"] = list(negative_image_ids)
    
    with open(stats_json_file, 'w') as f:
        json.dump(stats_for_json, f, indent=2)
    
    print(f"✓ Detailed statistics saved to: {stats_json_file}")
    print()
    
    print("=" * 70)
    print("✓ False positive analysis completed")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
