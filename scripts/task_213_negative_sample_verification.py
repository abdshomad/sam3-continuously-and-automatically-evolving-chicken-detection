#!/usr/bin/env python3
"""
Task ID: 2.1.3
Description: Negative Sample Verification
Created: 2025-01-27

This script verifies that "Not-Chicken" images meet one of these criteria:
1. Image is in the not_chicken/ directory
2. No corresponding label file exists
3. Corresponding label file exists but is empty (0 annotations)
"""

import sys
import json
import os
from pathlib import Path
from collections import defaultdict

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import configuration from config.py
try:
    import config
except ImportError:
    print("Error: config.py not found. Please create config.py with required settings.", file=sys.stderr)
    sys.exit(1)

# Supported image formats
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}

def get_image_files(directory):
    """Get all image files from a directory."""
    image_files = []
    if not directory.exists():
        return image_files
    
    for ext in IMAGE_EXTENSIONS:
        image_files.extend(directory.glob(f"*{ext}"))
        image_files.extend(directory.glob(f"*{ext.upper()}"))
    
    return sorted(image_files)

def get_label_file_for_image(image_path, labels_dir):
    """Find corresponding label file for an image."""
    # Try common label formats: .json (LabelMe), .txt (YOLO)
    image_stem = image_path.stem
    
    # Try LabelMe JSON format
    json_label = labels_dir / f"{image_stem}.json"
    if json_label.exists():
        return json_label
    
    # Try YOLO TXT format
    txt_label = labels_dir / f"{image_stem}.txt"
    if txt_label.exists():
        return txt_label
    
    return None

def is_label_file_empty(label_path):
    """Check if a label file is empty (no annotations)."""
    if not label_path.exists():
        return True
    
    # Check file size first
    if label_path.stat().st_size == 0:
        return True
    
    try:
        # Try LabelMe JSON format
        if label_path.suffix.lower() == '.json':
            with open(label_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Check if shapes array is empty or doesn't exist
                if 'shapes' not in data or len(data.get('shapes', [])) == 0:
                    return True
        
        # Try YOLO TXT format
        elif label_path.suffix.lower() == '.txt':
            with open(label_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                if len(lines) == 0:
                    return True
    
    except (json.JSONDecodeError, Exception) as e:
        # If we can't parse it, consider it non-empty (might have data)
        print(f"  ⚠ Warning: Could not parse label file {label_path.name}: {e}")
        return False
    
    return False

def verify_negative_samples(not_chicken_dir, chicken_dir, labels_dir):
    """Verify negative samples meet the required criteria."""
    
    results = {
        'valid_negative_samples': [],
        'invalid_negative_samples': [],
        'warnings': [],
        'statistics': {
            'total_not_chicken_images': 0,
            'total_chicken_images_without_labels': 0,
            'valid_count': 0,
            'invalid_count': 0,
        }
    }
    
    print("Scanning not_chicken directory...")
    not_chicken_images = get_image_files(not_chicken_dir)
    results['statistics']['total_not_chicken_images'] = len(not_chicken_images)
    print(f"  Found {len(not_chicken_images)} images in not_chicken/")
    print("")
    
    # Check images in not_chicken directory
    for image_path in not_chicken_images:
        relative_path = image_path.relative_to(project_root)
        label_file = get_label_file_for_image(image_path, labels_dir)
        
        if label_file is None:
            # No label file - VALID (criterion 2)
            results['valid_negative_samples'].append({
                'image': str(relative_path),
                'reason': 'No corresponding label file',
                'location': 'not_chicken/'
            })
        elif is_label_file_empty(label_file):
            # Empty label file - VALID (criterion 3)
            results['valid_negative_samples'].append({
                'image': str(relative_path),
                'reason': 'Empty label file',
                'location': 'not_chicken/',
                'label_file': label_file.name
            })
        else:
            # Has non-empty label file - INVALID
            results['invalid_negative_samples'].append({
                'image': str(relative_path),
                'reason': 'Has non-empty label file',
                'location': 'not_chicken/',
                'label_file': label_file.name,
                'suggestion': f'Remove or empty label file: {label_file.relative_to(project_root)}'
            })
    
    # Check chicken directory for images without labels (potential negatives)
    print("Scanning chicken directory for images without labels...")
    chicken_images = get_image_files(chicken_dir)
    
    images_without_labels = []
    for image_path in chicken_images:
        label_file = get_label_file_for_image(image_path, labels_dir)
        
        if label_file is None or is_label_file_empty(label_file):
            relative_path = image_path.relative_to(project_root)
            images_without_labels.append(image_path)
            
            # This could be a negative sample that should be moved
            results['warnings'].append({
                'image': str(relative_path),
                'type': 'Potential negative sample in chicken directory',
                'suggestion': f'Consider moving to not_chicken/ directory or add proper labels'
            })
    
    results['statistics']['total_chicken_images_without_labels'] = len(images_without_labels)
    results['statistics']['valid_count'] = len(results['valid_negative_samples'])
    results['statistics']['invalid_count'] = len(results['invalid_negative_samples'])
    
    print(f"  Found {len(images_without_labels)} images in chicken/ without labels")
    print("")
    
    return results

def print_verification_report(results):
    """Print a detailed verification report."""
    
    stats = results['statistics']
    valid = results['valid_negative_samples']
    invalid = results['invalid_negative_samples']
    warnings = results['warnings']
    
    print("=" * 70)
    print("NEGATIVE SAMPLE VERIFICATION REPORT")
    print("=" * 70)
    print("")
    
    print("STATISTICS:")
    print(f"  Total images in not_chicken/: {stats['total_not_chicken_images']}")
    print(f"  Valid negative samples: {stats['valid_count']}")
    print(f"  Invalid negative samples: {stats['invalid_count']}")
    print(f"  Potential negatives in chicken/: {stats['total_chicken_images_without_labels']}")
    print(f"  Warnings: {len(warnings)}")
    print("")
    
    if valid:
        print("✓ VALID NEGATIVE SAMPLES:")
        print("")
        for item in valid[:10]:  # Show first 10
            print(f"  ✓ {item['image']}")
            print(f"    Reason: {item['reason']}")
            if 'label_file' in item:
                print(f"    Label: {item['label_file']}")
        if len(valid) > 10:
            print(f"  ... and {len(valid) - 10} more valid samples")
        print("")
    else:
        print("⚠ No valid negative samples found in not_chicken/ directory")
        print("")
    
    if invalid:
        print("✗ INVALID NEGATIVE SAMPLES:")
        print("")
        for item in invalid:
            print(f"  ✗ {item['image']}")
            print(f"    Reason: {item['reason']}")
            if 'suggestion' in item:
                print(f"    Suggestion: {item['suggestion']}")
        print("")
    
    if warnings:
        print("⚠ WARNINGS:")
        print("")
        for item in warnings[:10]:  # Show first 10
            print(f"  ⚠ {item['image']}")
            print(f"    Type: {item['type']}")
            if 'suggestion' in item:
                print(f"    Suggestion: {item['suggestion']}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings")
        print("")
    
    print("=" * 70)
    print("")

def main():
    print("=" * 70)
    print("Task 2.1.3: Negative Sample Verification")
    print("=" * 70)
    print("")
    
    # Define paths
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    base_path = project_root / base_data_path
    not_chicken_dir = base_path / 'raw_data' / 'images' / 'not_chicken'
    chicken_dir = base_path / 'raw_data' / 'images' / 'chicken'
    labels_dir = base_path / 'raw_data' / 'labels'
    
    print(f"Base data path: {base_path}")
    print(f"Not-chicken images: {not_chicken_dir.relative_to(project_root)}")
    print(f"Chicken images: {chicken_dir.relative_to(project_root)}")
    print(f"Labels directory: {labels_dir.relative_to(project_root)}")
    print("")
    
    # Check if directories exist
    if not not_chicken_dir.exists():
        print(f"⚠ Warning: not_chicken directory does not exist: {not_chicken_dir}")
        print("  Creating directory...")
        not_chicken_dir.mkdir(parents=True, exist_ok=True)
        print("")
    
    if not chicken_dir.exists():
        print(f"⚠ Warning: chicken directory does not exist: {chicken_dir}")
        print("  Creating directory...")
        chicken_dir.mkdir(parents=True, exist_ok=True)
        print("")
    
    if not labels_dir.exists():
        print(f"⚠ Warning: labels directory does not exist: {labels_dir}")
        print("  Creating directory...")
        labels_dir.mkdir(parents=True, exist_ok=True)
        print("")
    
    # Verify negative samples
    results = verify_negative_samples(not_chicken_dir, chicken_dir, labels_dir)
    
    # Print report
    print_verification_report(results)
    
    # Save detailed report to file
    report_file = base_path / 'negative_sample_verification_report.json'
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Detailed report saved to: {report_file.relative_to(project_root)}")
        print("")
    except Exception as e:
        print(f"⚠ Warning: Could not save report file: {e}")
        print("")
    
    # Determine exit status
    if results['statistics']['invalid_count'] > 0:
        print("⚠ ATTENTION: Found invalid negative samples that need correction!")
        print("  Please review the report above and fix the issues.")
        print("")
        return 1
    elif results['statistics']['valid_count'] == 0:
        print("⚠ WARNING: No valid negative samples found!")
        print("  Ensure you have negative samples in the not_chicken/ directory.")
        print("")
        return 1
    else:
        print("✓ Negative Sample Verification: COMPLETED")
        print("  All negative samples meet the required criteria.")
        print("")
        return 0

if __name__ == "__main__":
    sys.exit(main())
