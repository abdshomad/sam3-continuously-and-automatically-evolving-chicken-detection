#!/usr/bin/env python3
"""
Task ID: 2.3.2
Description: Ambiguous Class Exclusion
Created: 2025-01-27

This script identifies and excludes images containing "ambiguous" classes
(e.g., "unknown bird") that are neither clearly chicken nor clearly background.
These images are excluded to prevent confusing the model during training.
"""

import sys
import json
import os
from pathlib import Path
from collections import defaultdict

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

# Default ambiguous class patterns (can be overridden in config.py)
DEFAULT_AMBIGUOUS_PATTERNS = [
    "unknown",
    "ambiguous",
    "unclear",
    "unknown bird",
    "unidentified",
    "uncertain",
    "maybe",
    "possibly",
    "questionable",
    "unsure",
]

def get_ambiguous_patterns():
    """Get ambiguous class patterns from config or use defaults."""
    ambiguous_patterns = getattr(config, 'AMBIGUOUS_CLASS_PATTERNS', None)
    if ambiguous_patterns is None:
        ambiguous_patterns = DEFAULT_AMBIGUOUS_PATTERNS
    
    # Convert to lowercase for case-insensitive matching
    return [pattern.lower() for pattern in ambiguous_patterns]

def is_ambiguous_class(class_name, ambiguous_patterns):
    """Check if a class name matches any ambiguous pattern."""
    class_name_lower = class_name.lower().strip()
    
    for pattern in ambiguous_patterns:
        if pattern in class_name_lower or class_name_lower == pattern:
            return True
    
    return False

def scan_labelme_file(labelme_path, ambiguous_patterns):
    """Scan a LabelMe JSON file for ambiguous classes."""
    ambiguous_classes_found = []
    
    try:
        with open(labelme_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'shapes' in data:
            for shape in data['shapes']:
                if 'label' in shape:
                    label = shape['label'].strip()
                    if label and is_ambiguous_class(label, ambiguous_patterns):
                        if label not in ambiguous_classes_found:
                            ambiguous_classes_found.append(label)
    
    except (json.JSONDecodeError, Exception) as e:
        # If we can't parse it, we can't determine if it's ambiguous
        # Return empty list (treat as non-ambiguous)
        pass
    
    return ambiguous_classes_found

def scan_yolo_file(yolo_path, ambiguous_patterns, classes_file=None):
    """Scan a YOLO TXT file for ambiguous classes."""
    ambiguous_classes_found = []
    
    # First, try to get class names from classes.txt if available
    class_names = {}
    if classes_file and classes_file.exists():
        try:
            with open(classes_file, 'r', encoding='utf-8') as f:
                for idx, line in enumerate(f):
                    class_name = line.strip()
                    if class_name:
                        class_names[idx] = class_name
        except Exception:
            pass
    
    try:
        with open(yolo_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    # Check if we have a class name mapping
                    if class_id in class_names:
                        class_name = class_names[class_id]
                        if is_ambiguous_class(class_name, ambiguous_patterns):
                            if class_name not in ambiguous_classes_found:
                                ambiguous_classes_found.append(class_name)
                    else:
                        # If no class name mapping, we can't determine ambiguity
                        # Assume non-ambiguous for now
                        pass
    
    except Exception:
        pass
    
    return ambiguous_classes_found

def get_label_file_for_image(image_path, labels_dir):
    """Find corresponding label file for an image."""
    image_stem = image_path.stem
    
    # Try LabelMe JSON format
    json_label = labels_dir / f"{image_stem}.json"
    if json_label.exists():
        return json_label, 'labelme'
    
    # Try YOLO TXT format
    txt_label = labels_dir / f"{image_stem}.txt"
    if txt_label.exists():
        return txt_label, 'yolo'
    
    return None, None

def scan_images_for_ambiguous_classes(images_dir, labels_dir, ambiguous_patterns, classes_file=None):
    """Scan all images and identify those with ambiguous classes."""
    
    results = {
        'excluded_images': [],
        'included_images': [],
        'ambiguous_classes_found': set(),
        'statistics': {
            'total_images_scanned': 0,
            'excluded_count': 0,
            'included_count': 0,
        }
    }
    
    # Supported image formats
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    if not images_dir.exists():
        print(f"⚠ Warning: Images directory does not exist: {images_dir}")
        return results
    
    # Get all image files
    image_files = []
    for ext in image_extensions:
        image_files.extend(images_dir.glob(f"*{ext}"))
        image_files.extend(images_dir.glob(f"*{ext.upper()}"))
    
    image_files = sorted(image_files)
    results['statistics']['total_images_scanned'] = len(image_files)
    
    print(f"Scanning {len(image_files)} images for ambiguous classes...")
    print("")
    
    for image_path in image_files:
        relative_path = image_path.relative_to(project_root)
        label_file, label_format = get_label_file_for_image(image_path, labels_dir)
        
        if label_file is None:
            # No label file - include (not ambiguous, might be negative sample)
            results['included_images'].append({
                'image': str(relative_path),
                'reason': 'No label file',
            })
            continue
        
        # Scan label file for ambiguous classes
        ambiguous_classes = []
        if label_format == 'labelme':
            ambiguous_classes = scan_labelme_file(label_file, ambiguous_patterns)
        elif label_format == 'yolo':
            ambiguous_classes = scan_yolo_file(label_file, ambiguous_patterns, classes_file)
        
        if ambiguous_classes:
            # Found ambiguous classes - exclude this image
            results['excluded_images'].append({
                'image': str(relative_path),
                'label_file': str(label_file.relative_to(project_root)),
                'ambiguous_classes': ambiguous_classes,
                'reason': f'Contains ambiguous classes: {", ".join(ambiguous_classes)}',
            })
            results['ambiguous_classes_found'].update(ambiguous_classes)
        else:
            # No ambiguous classes - include
            results['included_images'].append({
                'image': str(relative_path),
                'label_file': str(label_file.relative_to(project_root)),
                'reason': 'No ambiguous classes found',
            })
    
    results['statistics']['excluded_count'] = len(results['excluded_images'])
    results['statistics']['included_count'] = len(results['included_images'])
    
    return results

def print_exclusion_report(results, ambiguous_patterns):
    """Print a detailed exclusion report."""
    
    stats = results['statistics']
    excluded = results['excluded_images']
    ambiguous_classes = sorted(results['ambiguous_classes_found'])
    
    print("=" * 70)
    print("AMBIGUOUS CLASS EXCLUSION REPORT")
    print("=" * 70)
    print("")
    
    print("CONFIGURATION:")
    print(f"  Ambiguous patterns: {', '.join(ambiguous_patterns)}")
    print("")
    
    print("STATISTICS:")
    print(f"  Total images scanned: {stats['total_images_scanned']}")
    print(f"  Images excluded: {stats['excluded_count']}")
    print(f"  Images included: {stats['included_count']}")
    print(f"  Unique ambiguous classes found: {len(ambiguous_classes)}")
    print("")
    
    if ambiguous_classes:
        print("AMBIGUOUS CLASSES FOUND:")
        for class_name in ambiguous_classes:
            print(f"  - {class_name}")
        print("")
    
    if excluded:
        print("EXCLUDED IMAGES:")
        print("")
        for item in excluded[:20]:  # Show first 20
            print(f"  ✗ {item['image']}")
            print(f"    Reason: {item['reason']}")
            if 'ambiguous_classes' in item:
                print(f"    Classes: {', '.join(item['ambiguous_classes'])}")
        if len(excluded) > 20:
            print(f"  ... and {len(excluded) - 20} more excluded images")
        print("")
    else:
        print("✓ No images excluded (no ambiguous classes found)")
        print("")
    
    print("=" * 70)
    print("")

def main():
    print("=" * 70)
    print("Task 2.3.2: Ambiguous Class Exclusion")
    print("=" * 70)
    print("")
    
    # Get ambiguous patterns from config
    ambiguous_patterns = get_ambiguous_patterns()
    
    # Define paths
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    base_path = project_root / base_data_path
    images_dir = base_path / 'raw_data' / 'images' / 'chicken'
    labels_dir = base_path / 'raw_data' / 'labels'
    classes_file = base_path / 'raw_data' / 'classes.txt'
    output_file = base_path / 'ambiguous_class_exclusion_report.json'
    
    print(f"Base data path: {base_path}")
    print(f"Images directory: {images_dir.relative_to(project_root)}")
    print(f"Labels directory: {labels_dir.relative_to(project_root)}")
    print("")
    
    # Check if directories exist
    if not images_dir.exists():
        print(f"⚠ Warning: Images directory does not exist: {images_dir}")
        print("  Creating directory...")
        images_dir.mkdir(parents=True, exist_ok=True)
        print("")
    
    if not labels_dir.exists():
        print(f"⚠ Warning: Labels directory does not exist: {labels_dir}")
        print("  Creating directory...")
        labels_dir.mkdir(parents=True, exist_ok=True)
        print("")
    
    # Scan for ambiguous classes
    results = scan_images_for_ambiguous_classes(
        images_dir, 
        labels_dir, 
        ambiguous_patterns,
        classes_file
    )
    
    # Print report
    print_exclusion_report(results, ambiguous_patterns)
    
    # Save detailed report to file
    try:
        # Convert set to list for JSON serialization
        results_json = results.copy()
        results_json['ambiguous_classes_found'] = sorted(list(results['ambiguous_classes_found']))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_json, f, indent=2, ensure_ascii=False)
        
        print(f"Detailed report saved to: {output_file.relative_to(project_root)}")
        print("")
    except Exception as e:
        print(f"⚠ Warning: Could not save report file: {e}")
        print("")
    
    # Summary
    print("=" * 70)
    print("✓ Ambiguous Class Exclusion: COMPLETED")
    print("=" * 70)
    print("")
    print(f"Excluded {results['statistics']['excluded_count']} images with ambiguous classes")
    print(f"Included {results['statistics']['included_count']} images for training")
    print("")
    print("Next steps:")
    print("  - Review excluded images in the report")
    print("  - Use included images for ETL processing")
    print("  - Update ambiguous patterns in config.py if needed")
    print("")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
