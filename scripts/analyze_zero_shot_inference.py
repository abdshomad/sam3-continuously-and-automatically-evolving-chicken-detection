#!/usr/bin/env -S uv run python
"""
Comprehensive Zero-Shot Inference Analysis Script

This script performs a detailed analysis of zero-shot inference results, including:
- Metrics summary and interpretation
- False positive analysis
- False negative analysis
- Per-image performance breakdown
- Distribution analysis
- Comprehensive markdown report

Created: 2025-12-12
"""

import sys
import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
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

# Try to import visualization libraries (optional)
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available. Visualizations will be skipped.", file=sys.stderr)


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
    """Identify images that are 'Not-Chicken' (negative samples)."""
    images_with_annotations = set()
    if "annotations" in gt_data:
        for ann in gt_data["annotations"]:
            images_with_annotations.add(ann["image_id"])
    
    negative_image_ids = set()
    if "images" in gt_data:
        for img in gt_data["images"]:
            img_id = img["id"]
            if img_id not in images_with_annotations:
                negative_image_ids.add(img_id)
    
    return negative_image_ids


def analyze_false_positives(gt_data, pred_data, negative_image_ids):
    """Analyze false positives: detections on negative (Not-Chicken) images."""
    predictions_by_image = defaultdict(list)
    for pred in pred_data:
        img_id = pred.get("image_id")
        if img_id is not None:
            predictions_by_image[img_id].append(pred)
    
    false_positive_stats = {
        "total_negative_images": len(negative_image_ids),
        "negative_images_with_detections": 0,
        "total_false_positives": 0,
        "false_positive_images": [],
        "avg_detections_per_negative_image": 0.0,
        "max_detections_on_single_image": 0,
        "presence_scores": []
    }
    
    image_id_to_filename = {}
    if "images" in gt_data:
        for img in gt_data["images"]:
            image_id_to_filename[img["id"]] = img.get("file_name", f"image_{img['id']}")
    
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
                
                false_positive_stats["presence_scores"].extend(scores)
    
    if false_positive_stats["total_negative_images"] > 0:
        false_positive_stats["avg_detections_per_negative_image"] = (
            false_positive_stats["total_false_positives"] / 
            false_positive_stats["total_negative_images"]
        )
    
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


def analyze_false_negatives(gt_data, pred_data, positive_image_ids):
    """Analyze false negatives: missed detections on positive images."""
    predictions_by_image = defaultdict(list)
    for pred in pred_data:
        img_id = pred.get("image_id")
        if img_id is not None:
            predictions_by_image[img_id].append(pred)
    
    # Count ground truth annotations per image
    gt_annotations_by_image = defaultdict(int)
    if "annotations" in gt_data:
        for ann in gt_data["annotations"]:
            gt_annotations_by_image[ann["image_id"]] += 1
    
    false_negative_stats = {
        "total_positive_images": len(positive_image_ids),
        "positive_images_with_detections": 0,
        "positive_images_without_detections": 0,
        "total_gt_annotations": sum(gt_annotations_by_image.values()),
        "total_predictions_on_positive": 0,
        "false_negative_images": [],
        "avg_detections_per_positive_image": 0.0,
        "avg_gt_annotations_per_positive_image": 0.0
    }
    
    image_id_to_filename = {}
    if "images" in gt_data:
        for img in gt_data["images"]:
            image_id_to_filename[img["id"]] = img.get("file_name", f"image_{img['id']}")
    
    for img_id in positive_image_ids:
        num_gt = gt_annotations_by_image.get(img_id, 0)
        num_pred = len(predictions_by_image.get(img_id, []))
        
        false_negative_stats["total_predictions_on_positive"] += num_pred
        
        if num_pred > 0:
            false_negative_stats["positive_images_with_detections"] += 1
        else:
            false_negative_stats["positive_images_without_detections"] += 1
            false_negative_stats["false_negative_images"].append({
                "image_id": img_id,
                "file_name": image_id_to_filename.get(img_id, f"image_{img_id}"),
                "num_gt_annotations": num_gt,
                "num_predictions": 0
            })
        # Also track images with fewer predictions than GT annotations
        if num_pred < num_gt:
            false_negative_stats["false_negative_images"].append({
                "image_id": img_id,
                "file_name": image_id_to_filename.get(img_id, f"image_{img_id}"),
                "num_gt_annotations": num_gt,
                "num_predictions": num_pred,
                "missing_detections": num_gt - num_pred
            })
    
    if false_negative_stats["total_positive_images"] > 0:
        false_negative_stats["avg_detections_per_positive_image"] = (
            false_negative_stats["total_predictions_on_positive"] / 
            false_negative_stats["total_positive_images"]
        )
        false_negative_stats["avg_gt_annotations_per_positive_image"] = (
            false_negative_stats["total_gt_annotations"] / 
            false_negative_stats["total_positive_images"]
        )
    
    return false_negative_stats


def analyze_per_image_performance(gt_data, pred_data):
    """Analyze performance on a per-image basis."""
    predictions_by_image = defaultdict(list)
    for pred in pred_data:
        img_id = pred.get("image_id")
        if img_id is not None:
            predictions_by_image[img_id].append(pred)
    
    gt_annotations_by_image = defaultdict(int)
    if "annotations" in gt_data:
        for ann in gt_data["annotations"]:
            gt_annotations_by_image[ann["image_id"]] += 1
    
    image_id_to_filename = {}
    if "images" in gt_data:
        for img in gt_data["images"]:
            image_id_to_filename[img["id"]] = img.get("file_name", f"image_{img['id']}")
    
    per_image_stats = []
    for img_id, filename in image_id_to_filename.items():
        num_gt = gt_annotations_by_image.get(img_id, 0)
        num_pred = len(predictions_by_image.get(img_id, []))
        
        # Calculate average score for predictions
        preds = predictions_by_image.get(img_id, [])
        avg_score = sum(p.get("score", 0.0) for p in preds) / len(preds) if preds else 0.0
        max_score = max((p.get("score", 0.0) for p in preds), default=0.0)
        
        per_image_stats.append({
            "image_id": img_id,
            "file_name": filename,
            "num_gt_annotations": num_gt,
            "num_predictions": num_pred,
            "avg_prediction_score": avg_score,
            "max_prediction_score": max_score,
            "is_positive": num_gt > 0,
            "is_negative": num_gt == 0
        })
    
    return per_image_stats


def analyze_distributions(pred_data):
    """Analyze score and detection count distributions."""
    scores = [pred.get("score", 0.0) for pred in pred_data if "score" in pred]
    
    predictions_by_image = defaultdict(list)
    for pred in pred_data:
        img_id = pred.get("image_id")
        if img_id is not None:
            predictions_by_image[img_id].append(pred)
    
    detection_counts = [len(preds) for preds in predictions_by_image.values()]
    
    distribution_stats = {
        "score_stats": {
            "count": len(scores),
            "mean": sum(scores) / len(scores) if scores else 0.0,
            "min": min(scores) if scores else 0.0,
            "max": max(scores) if scores else 0.0,
            "median": sorted(scores)[len(scores)//2] if scores else 0.0
        },
        "detection_count_stats": {
            "count": len(detection_counts),
            "mean": sum(detection_counts) / len(detection_counts) if detection_counts else 0.0,
            "min": min(detection_counts) if detection_counts else 0,
            "max": max(detection_counts) if detection_counts else 0,
            "median": sorted(detection_counts)[len(detection_counts)//2] if detection_counts else 0
        }
    }
    
    return distribution_stats, scores, detection_counts


def create_visualizations(scores, detection_counts, output_dir):
    """Create visualization plots if matplotlib is available."""
    if not HAS_MATPLOTLIB:
        return []
    
    viz_dir = output_dir / "visualizations"
    viz_dir.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    
    # Histogram of presence scores
    if scores:
        plt.figure(figsize=(10, 6))
        plt.hist(scores, bins=50, edgecolor='black', alpha=0.7)
        plt.xlabel('Presence/Confidence Score')
        plt.ylabel('Frequency')
        plt.title('Distribution of Prediction Scores')
        plt.grid(True, alpha=0.3)
        score_hist_path = viz_dir / "presence_scores_hist.png"
        plt.savefig(score_hist_path, dpi=150, bbox_inches='tight')
        plt.close()
        created_files.append(score_hist_path)
    
    # Distribution of detection counts per image
    if detection_counts:
        plt.figure(figsize=(10, 6))
        plt.hist(detection_counts, bins=min(50, max(detection_counts) + 1), edgecolor='black', alpha=0.7)
        plt.xlabel('Number of Detections per Image')
        plt.ylabel('Frequency')
        plt.title('Distribution of Detection Counts per Image')
        plt.grid(True, alpha=0.3)
        count_hist_path = viz_dir / "detection_counts_dist.png"
        plt.savefig(count_hist_path, dpi=150, bbox_inches='tight')
        plt.close()
        created_files.append(count_hist_path)
    
    return created_files


def generate_markdown_report(metrics, fp_stats, fn_stats, per_image_stats, dist_stats, output_file):
    """Generate comprehensive markdown analysis report."""
    report_lines = [
        "# Zero-Shot Inference Analysis Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "This report provides a comprehensive analysis of the zero-shot inference results using the pre-trained SAM3 model on the chicken detection validation dataset.",
        "",
        "### Key Metrics",
        "",
        f"- **pmF1 (Prompt-Mask F1):** {metrics.get('pmF1', 0.0):.4f}",
        f"- **IL_MCC (Image-Level Matthews Correlation Coefficient):** {metrics.get('IL_MCC', 0.0):.4f}",
        f"- **CGF1 (Composite Score):** {metrics.get('CGF1', 0.0):.4f}",
        "",
        "---",
        "",
        "## 1. Metrics Overview",
        "",
        "### 1.1 Prompt-Mask F1 (pmF1)",
        "",
        f"The pmF1 score of **{metrics.get('pmF1', 0.0):.4f}** measures the segmentation quality on positive detections.",
        "",
        "- **Range:** 0.0 to 1.0 (higher is better)",
        "- **Interpretation:** ",
        "  - High pmF1 (>0.7): Model produces accurate masks when it detects chickens",
        "  - Low pmF1 (<0.3): Model struggles with mask quality even when detecting objects",
        "",
        "### 1.2 Image-Level Matthews Correlation Coefficient (IL_MCC)",
        "",
        f"The IL_MCC score of **{metrics.get('IL_MCC', 0.0):.4f}** measures the binary classification accuracy (presence vs absence of chickens).",
        "",
        "- **Range:** -1.0 to 1.0 (higher is better, 0 = random guessing)",
        "- **Interpretation:** ",
        "  - High IL_MCC (>0.5): Model correctly identifies when chickens are present/absent",
        "  - Low IL_MCC (<0.2): Model struggles with presence detection, may hallucinate",
        "  - Negative IL_MCC: Model performs worse than random guessing",
        "",
        "### 1.3 Composite Score (CGF1)",
        "",
        f"The CGF1 score of **{metrics.get('CGF1', 0.0):.4f}** is the product of pmF1 and IL_MCC, providing an overall performance metric.",
        "",
        "- **Formula:** CGF1 = pmF1 × IL_MCC",
        "- **Interpretation:** ",
        "  - High CGF1 (>0.5): Good overall performance on both segmentation and presence detection",
        "  - Low CGF1 (<0.2): Significant room for improvement in one or both components",
        "",
        "---",
        "",
        "## 2. False Positive Analysis",
        "",
        "False positives are detections made on images that contain no chickens (negative samples).",
        "",
        f"- **Total negative images:** {fp_stats.get('total_negative_images', 0)}",
        f"- **Negative images with detections:** {fp_stats.get('negative_images_with_detections', 0)}",
        f"- **Total false positive detections:** {fp_stats.get('total_false_positives', 0)}",
        f"- **Average detections per negative image:** {fp_stats.get('avg_detections_per_negative_image', 0.0):.2f}",
        f"- **Maximum detections on a single negative image:** {fp_stats.get('max_detections_on_single_image', 0)}",
        "",
        "### 2.1 False Positive Rate",
        "",
    ]
    
    if fp_stats.get('total_negative_images', 0) > 0:
        fp_rate = (fp_stats.get('negative_images_with_detections', 0) / 
                  fp_stats.get('total_negative_images', 1)) * 100
        report_lines.extend([
            f"The false positive rate is **{fp_rate:.1f}%** of negative images have at least one detection.",
            "",
        ])
        
        if fp_rate > 50:
            report_lines.append("⚠️ **HIGH FALSE POSITIVE RATE** - The model is frequently hallucinating chickens in empty scenes. Fine-tuning with negative samples is critical.")
        elif fp_rate > 20:
            report_lines.append("⚠️ **MODERATE FALSE POSITIVE RATE** - Some false detections on background. Fine-tuning should improve background rejection.")
        else:
            report_lines.append("✓ **LOW FALSE POSITIVE RATE** - Few false detections. Fine-tuning may still help improve precision.")
    else:
        report_lines.append("No negative images found in the validation set.")
    
    report_lines.extend([
        "",
        "### 2.2 Presence Scores on False Positives",
        "",
        f"- **Average score:** {fp_stats.get('avg_presence_score', 0.0):.4f}",
        f"- **Minimum score:** {fp_stats.get('min_presence_score', 0.0):.4f}",
        f"- **Maximum score:** {fp_stats.get('max_presence_score', 0.0):.4f}",
        "",
    ])
    
    avg_fp_score = fp_stats.get('avg_presence_score', 0.0)
    if avg_fp_score > 0.5:
        report_lines.append("⚠️ High average presence scores (>0.5) indicate confident false detections.")
    elif avg_fp_score > 0.1:
        report_lines.append("⚠️ Moderate presence scores (0.1-0.5) indicate ambiguous detections.")
    else:
        report_lines.append("✓ Low presence scores (<0.1) indicate weak/uncertain false detections.")
    
    # Top false positive images
    report_lines.extend([
        "",
        "### 2.3 Top False Positive Images",
        "",
        "Images with the most false positive detections:",
        "",
    ])
    
    sorted_fp_images = sorted(
        fp_stats.get('false_positive_images', []),
        key=lambda x: x.get('num_detections', 0),
        reverse=True
    )[:10]
    
    if sorted_fp_images:
        report_lines.append("| Rank | Image | Detections | Avg Score | Max Score |")
        report_lines.append("|------|-------|------------|-----------|-----------|")
        for i, fp_img in enumerate(sorted_fp_images, 1):
            report_lines.append(
                f"| {i} | {fp_img.get('file_name', 'N/A')} | "
                f"{fp_img.get('num_detections', 0)} | "
                f"{fp_img.get('avg_score', 0.0):.4f} | "
                f"{fp_img.get('max_score', 0.0):.4f} |"
            )
    else:
        report_lines.append("No false positives detected.")
    
    report_lines.extend([
        "",
        "---",
        "",
        "## 3. False Negative Analysis",
        "",
        "False negatives are missed detections on images that contain chickens (positive samples).",
        "",
        f"- **Total positive images:** {fn_stats.get('total_positive_images', 0)}",
        f"- **Positive images with detections:** {fn_stats.get('positive_images_with_detections', 0)}",
        f"- **Positive images without detections:** {fn_stats.get('positive_images_without_detections', 0)}",
        f"- **Total ground truth annotations:** {fn_stats.get('total_gt_annotations', 0)}",
        f"- **Total predictions on positive images:** {fn_stats.get('total_predictions_on_positive', 0)}",
        f"- **Average detections per positive image:** {fn_stats.get('avg_detections_per_positive_image', 0.0):.2f}",
        f"- **Average GT annotations per positive image:** {fn_stats.get('avg_gt_annotations_per_positive_image', 0.0):.2f}",
        "",
    ])
    
    if fn_stats.get('total_positive_images', 0) > 0:
        fn_rate = (fn_stats.get('positive_images_without_detections', 0) / 
                  fn_stats.get('total_positive_images', 1)) * 100
        report_lines.extend([
            f"### 3.1 False Negative Rate",
            "",
            f"The false negative rate is **{fn_rate:.1f}%** of positive images have no detections.",
            "",
        ])
        
        if fn_rate > 50:
            report_lines.append("❌ **HIGH FALSE NEGATIVE RATE** - The model is missing chickens in many positive images.")
        elif fn_rate > 20:
            report_lines.append("⚠️ **MODERATE FALSE NEGATIVE RATE** - Some missed detections. Fine-tuning should improve recall.")
        else:
            report_lines.append("✓ **LOW FALSE NEGATIVE RATE** - Most positive images are detected.")
    
    # Top false negative images
    report_lines.extend([
        "",
        "### 3.2 Top False Negative Images",
        "",
        "Images with missed detections:",
        "",
    ])
    
    sorted_fn_images = sorted(
        fn_stats.get('false_negative_images', []),
        key=lambda x: x.get('missing_detections', x.get('num_gt_annotations', 0)),
        reverse=True
    )[:10]
    
    if sorted_fn_images:
        report_lines.append("| Rank | Image | GT Annotations | Predictions | Missing |")
        report_lines.append("|------|-------|----------------|-------------|---------|")
        for i, fn_img in enumerate(sorted_fn_images, 1):
            missing = fn_img.get('missing_detections', fn_img.get('num_gt_annotations', 0))
            report_lines.append(
                f"| {i} | {fn_img.get('file_name', 'N/A')} | "
                f"{fn_img.get('num_gt_annotations', 0)} | "
                f"{fn_img.get('num_predictions', 0)} | "
                f"{missing} |"
            )
    else:
        report_lines.append("No false negatives detected (or all positive images have detections).")
    
    report_lines.extend([
        "",
        "---",
        "",
        "## 4. Distribution Analysis",
        "",
        "### 4.1 Prediction Score Distribution",
        "",
        f"- **Count:** {dist_stats.get('score_stats', {}).get('count', 0)}",
        f"- **Mean:** {dist_stats.get('score_stats', {}).get('mean', 0.0):.4f}",
        f"- **Min:** {dist_stats.get('score_stats', {}).get('min', 0.0):.4f}",
        f"- **Max:** {dist_stats.get('score_stats', {}).get('max', 0.0):.4f}",
        f"- **Median:** {dist_stats.get('score_stats', {}).get('median', 0.0):.4f}",
        "",
        "### 4.2 Detection Count Distribution",
        "",
        f"- **Count:** {dist_stats.get('detection_count_stats', {}).get('count', 0)}",
        f"- **Mean:** {dist_stats.get('detection_count_stats', {}).get('mean', 0.0):.2f}",
        f"- **Min:** {dist_stats.get('detection_count_stats', {}).get('min', 0)}",
        f"- **Max:** {dist_stats.get('detection_count_stats', {}).get('max', 0)}",
        f"- **Median:** {dist_stats.get('detection_count_stats', {}).get('median', 0)}",
        "",
        "---",
        "",
        "## 5. Key Findings and Recommendations",
        "",
        "### 5.1 Key Findings",
        "",
    ])
    
    # Generate findings based on metrics
    findings = []
    
    if metrics.get('pmF1', 0.0) < 0.3:
        findings.append("- **Low pmF1:** The model struggles with mask quality. Consider increasing Dice/IoU loss weights during fine-tuning.")
    
    if metrics.get('IL_MCC', 0.0) < 0.2:
        findings.append("- **Low IL_MCC:** The model has difficulty with presence detection. This suggests the need for fine-tuning with negative samples to suppress hallucinations.")
    
    if metrics.get('CGF1', 0.0) < 0.2:
        findings.append("- **Low CGF1:** Overall performance is low. Fine-tuning is essential to improve both segmentation and presence detection.")
    
    if fp_stats.get('negative_images_with_detections', 0) > 0:
        fp_rate = (fp_stats.get('negative_images_with_detections', 0) / 
                  max(fp_stats.get('total_negative_images', 1), 1)) * 100
        if fp_rate > 20:
            findings.append(f"- **High false positive rate ({fp_rate:.1f}%):** The model frequently detects chickens in empty scenes. Fine-tuning with negative samples is critical.")
    
    if fn_stats.get('positive_images_without_detections', 0) > 0:
        fn_rate = (fn_stats.get('positive_images_without_detections', 0) / 
                  max(fn_stats.get('total_positive_images', 1), 1)) * 100
        if fn_rate > 20:
            findings.append(f"- **High false negative rate ({fn_rate:.1f}%):** The model misses chickens in many positive images. Fine-tuning should improve recall.")
    
    if not findings:
        findings.append("- The zero-shot baseline shows reasonable performance, but fine-tuning can still provide improvements.")
    
    report_lines.extend(findings)
    
    report_lines.extend([
        "",
        "### 5.2 Recommendations",
        "",
        "1. **Proceed with Fine-Tuning:** Based on the zero-shot baseline, fine-tuning is recommended to improve performance.",
        "",
        "2. **Focus Areas for Fine-Tuning:**",
        "   - If IL_MCC is low: Increase focal loss weight to better handle negative samples",
        "   - If pmF1 is low: Increase Dice/IoU loss weights to improve mask quality",
        "   - If false positive rate is high: Ensure negative samples are included in training",
        "",
        "3. **Training Configuration:**",
        "   - Use frozen backbone initially to preserve general visual knowledge",
        "   - Set conservative learning rate (1e-5) to protect the backbone",
        "   - Monitor both pmF1 and IL_MCC during training",
        "",
        "4. **Evaluation:**",
        "   - Compare fine-tuned metrics against this zero-shot baseline",
        "   - Target: Significant improvement in IL_MCC (presence detection)",
        "   - Target: Maintain or improve pmF1 (segmentation quality)",
        "",
        "---",
        "",
        "## 6. Appendix: Detailed Statistics",
        "",
        "See the following JSON files for detailed statistics:",
        "",
        "- `metrics_summary.json`: Core metrics (pmF1, IL_MCC, CGF1)",
        "- `false_positive_details.json`: Detailed false positive analysis",
        "- `false_negative_details.json`: Detailed false negative analysis",
        "- `per_image_performance.json`: Per-image performance breakdown",
        "- `statistics.json`: Comprehensive statistics dictionary",
        "",
        "---",
        "",
        "*Report generated by analyze_zero_shot_inference.py*",
    ])
    
    report_text = "\n".join(report_lines)
    
    # Save to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(report_text)
    
    return report_text


def main():
    """Main analysis function."""
    print("=" * 70)
    print("Comprehensive Zero-Shot Inference Analysis")
    print("=" * 70)
    print()
    
    # Set up paths
    val_json_path = project_root / config.DEFAULT_DATA_PATH / "chicken_val.json"
    results_dir = project_root / "results" / "zero_shot_baseline"
    baseline_metrics_path = project_root / "results" / "baseline_metrics.json"
    analysis_output_dir = project_root / "analysis" / "311-zero-shot-inference"
    
    # Check if validation JSON exists
    if not val_json_path.exists():
        print(f"ERROR: Validation JSON not found: {val_json_path}", file=sys.stderr)
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
        print(f"ERROR: Prediction file not found in results directory: {results_dir}", file=sys.stderr)
        print("Please run zero-shot inference first (task 3.1.1).", file=sys.stderr)
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
    
    # Load baseline metrics
    metrics = {}
    if baseline_metrics_path.exists():
        print(f"Loading baseline metrics from: {baseline_metrics_path}")
        try:
            with open(baseline_metrics_path, 'r') as f:
                metrics = json.load(f)
        except Exception as e:
            print(f"WARNING: Failed to load baseline metrics: {e}", file=sys.stderr)
    else:
        print("WARNING: Baseline metrics file not found. Some metrics may be missing.")
    
    print()
    
    # Identify positive and negative images
    print("Identifying positive and negative images...")
    negative_image_ids = identify_negative_images(gt_data)
    positive_image_ids = set()
    if "images" in gt_data:
        for img in gt_data["images"]:
            if img["id"] not in negative_image_ids:
                positive_image_ids.add(img["id"])
    
    print(f"Found {len(positive_image_ids)} positive images and {len(negative_image_ids)} negative images")
    print()
    
    # Perform analyses
    print("Analyzing false positives...")
    fp_stats = analyze_false_positives(gt_data, pred_data, negative_image_ids)
    print()
    
    print("Analyzing false negatives...")
    fn_stats = analyze_false_negatives(gt_data, pred_data, positive_image_ids)
    print()
    
    print("Analyzing per-image performance...")
    per_image_stats = analyze_per_image_performance(gt_data, pred_data)
    print()
    
    print("Analyzing distributions...")
    dist_stats, scores, detection_counts = analyze_distributions(pred_data)
    print()
    
    # Create output directory
    analysis_output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Analysis output directory: {analysis_output_dir}")
    print()
    
    # Create visualizations
    print("Creating visualizations...")
    viz_files = create_visualizations(scores, detection_counts, analysis_output_dir)
    if viz_files:
        print(f"Created {len(viz_files)} visualization(s)")
    print()
    
    # Generate markdown report
    print("Generating markdown report...")
    report_path = analysis_output_dir / "analysis_report.md"
    generate_markdown_report(metrics, fp_stats, fn_stats, per_image_stats, dist_stats, report_path)
    print(f"✓ Report saved to: {report_path}")
    print()
    
    # Save JSON artifacts
    print("Saving analysis artifacts...")
    
    # Metrics summary
    metrics_summary_path = analysis_output_dir / "metrics_summary.json"
    with open(metrics_summary_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✓ Metrics summary saved to: {metrics_summary_path}")
    
    # False positive details
    fp_details_path = analysis_output_dir / "false_positive_details.json"
    with open(fp_details_path, 'w') as f:
        json.dump(fp_stats, f, indent=2)
    print(f"✓ False positive details saved to: {fp_details_path}")
    
    # False negative details
    fn_details_path = analysis_output_dir / "false_negative_details.json"
    with open(fn_details_path, 'w') as f:
        json.dump(fn_stats, f, indent=2)
    print(f"✓ False negative details saved to: {fn_details_path}")
    
    # Per-image performance
    per_image_path = analysis_output_dir / "per_image_performance.json"
    with open(per_image_path, 'w') as f:
        json.dump(per_image_stats, f, indent=2)
    print(f"✓ Per-image performance saved to: {per_image_path}")
    
    # Comprehensive statistics
    all_stats = {
        "metrics": metrics,
        "false_positive_stats": fp_stats,
        "false_negative_stats": fn_stats,
        "distribution_stats": dist_stats,
        "summary": {
            "total_images": len(positive_image_ids) + len(negative_image_ids),
            "total_positive_images": len(positive_image_ids),
            "total_negative_images": len(negative_image_ids),
            "total_predictions": len(pred_data),
            "total_gt_annotations": fn_stats.get("total_gt_annotations", 0)
        }
    }
    statistics_path = analysis_output_dir / "statistics.json"
    with open(statistics_path, 'w') as f:
        json.dump(all_stats, f, indent=2)
    print(f"✓ Comprehensive statistics saved to: {statistics_path}")
    print()
    
    print("=" * 70)
    print("✓ Analysis completed successfully")
    print("=" * 70)
    print()
    print(f"All analysis artifacts saved to: {analysis_output_dir}")
    print(f"Main report: {report_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
