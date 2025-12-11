#!/usr/bin/env python3
"""
Task ID: 2.2.2
Description: YOLO BBox to Polygon Conversion
Created: 2025-01-27

This script converts YOLO format bounding boxes (normalized [x_center, y_center, width, height])
to 4-point polygons in the flat list format required by SA-Co segmentation field.
Format: [x1, y1, x2, y1, x2, y2, x1, y2]
"""

import sys
import json
from pathlib import Path
from PIL import Image
import numpy as np

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

def get_image_dimensions(image_path):
    """Get image dimensions (width, height) from image file."""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            return width, height
    except Exception as e:
        return None, None

def find_corresponding_image(label_path, images_dir, base_path):
    """Find the corresponding image file for a label file."""
    label_stem = label_path.stem
    
    # Search in chicken and not_chicken directories
    for subdir in ['chicken', 'not_chicken']:
        image_subdir = images_dir / subdir
        if not image_subdir.exists():
            continue
        
        for ext in IMAGE_EXTENSIONS:
            # Try lowercase extension
            image_path = image_subdir / f"{label_stem}{ext}"
            if image_path.exists():
                return image_path
            
            # Try uppercase extension
            image_path = image_subdir / f"{label_stem}{ext.upper()}"
            if image_path.exists():
                return image_path
    
    # If not found in subdirs, try directly in images_dir
    for ext in IMAGE_EXTENSIONS:
        image_path = images_dir / f"{label_stem}{ext}"
        if image_path.exists():
            return image_path
        image_path = images_dir / f"{label_stem}{ext.upper()}"
        if image_path.exists():
            return image_path
    
    return None

def yolo_to_absolute_coords(yolo_coords, img_width, img_height):
    """
    Convert YOLO normalized coordinates to absolute pixel coordinates.
    
    YOLO format: [class_id, x_center, y_center, width, height]
    All values are normalized (0-1 range).
    
    Returns: [x_min, y_min, x_max, y_max] in absolute pixel coordinates
    """
    class_id, x_center_norm, y_center_norm, width_norm, height_norm = yolo_coords
    
    # Convert to absolute coordinates
    x_center = x_center_norm * img_width
    y_center = y_center_norm * img_height
    width = width_norm * img_width
    height = height_norm * img_height
    
    # Calculate bounding box corners
    x_min = x_center - (width / 2)
    y_min = y_center - (height / 2)
    x_max = x_center + (width / 2)
    y_max = y_center + (height / 2)
    
    # Ensure coordinates are within image bounds
    x_min = max(0, min(x_min, img_width))
    y_min = max(0, min(y_min, img_height))
    x_max = max(0, min(x_max, img_width))
    y_max = max(0, min(y_max, img_height))
    
    return [x_min, y_min, x_max, y_max], class_id

def bbox_to_polygon(x_min, y_min, x_max, y_max):
    """
    Convert bounding box coordinates to 4-point polygon.
    
    Creates a rectangle polygon with points:
    Top-left: (x_min, y_min)
    Top-right: (x_max, y_min)
    Bottom-right: (x_max, y_max)
    Bottom-left: (x_min, y_max)
    
    Returns flat list format: [x1, y1, x2, y1, x2, y2, x1, y2]
    """
    polygon_flat = [
        x_min, y_min,  # Top-left
        x_max, y_min,  # Top-right
        x_max, y_max,  # Bottom-right
        x_min, y_max   # Bottom-left
    ]
    
    return polygon_flat

def parse_yolo_label_file(label_path):
    """Parse YOLO format label file and extract bounding boxes."""
    boxes = []
    
    if not label_path.exists():
        return boxes
    
    # Check if file is empty
    if label_path.stat().st_size == 0:
        return boxes
    
    try:
        with open(label_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                
                # YOLO format: class_id x_center y_center width height
                parts = line.split()
                if len(parts) != 5:
                    print(f"  ⚠ Warning: Line {line_num} in {label_path.name} has invalid format (expected 5 values, got {len(parts)})")
                    continue
                
                try:
                    coords = [float(part) for part in parts]
                    
                    # Validate normalized coordinates (should be 0-1)
                    if not (0 <= coords[1] <= 1 and 0 <= coords[2] <= 1 and 
                            0 <= coords[3] <= 1 and 0 <= coords[4] <= 1):
                        print(f"  ⚠ Warning: Line {line_num} in {label_path.name} has values outside [0,1] range")
                        continue
                    
                    boxes.append(coords)
                
                except ValueError as e:
                    print(f"  ⚠ Warning: Line {line_num} in {label_path.name} has invalid numeric values: {e}")
                    continue
    
    except Exception as e:
        print(f"  ✗ Error reading {label_path.name}: {e}")
    
    return boxes

def convert_yolo_labels(labels_dir, images_dir, base_path):
    """Convert all YOLO label files to polygon format."""
    
    # Find all YOLO label files (.txt)
    label_files = sorted(labels_dir.glob("*.txt"))
    
    if not label_files:
        print(f"  No YOLO label files (.txt) found in {labels_dir.relative_to(project_root)}")
        return [], {
            'total_label_files': 0,
            'processed': 0,
            'skipped_no_image': 0,
            'skipped_empty': 0,
            'total_boxes': 0,
            'errors': 0
        }
    
    print(f"  Found {len(label_files)} YOLO label files")
    print("")
    
    conversions = []
    statistics = {
        'total_label_files': len(label_files),
        'processed': 0,
        'skipped_no_image': 0,
        'skipped_empty': 0,
        'total_boxes': 0,
        'errors': 0
    }
    
    for label_path in label_files:
        relative_label_path = label_path.relative_to(project_root)
        
        # Parse YOLO boxes
        yolo_boxes = parse_yolo_label_file(label_path)
        
        if len(yolo_boxes) == 0:
            statistics['skipped_empty'] += 1
            continue
        
        # Find corresponding image
        image_path = find_corresponding_image(label_path, images_dir, base_path)
        
        if image_path is None:
            print(f"  ⚠ Warning: Could not find corresponding image for {label_path.name}")
            statistics['skipped_no_image'] += 1
            continue
        
        # Get image dimensions
        img_width, img_height = get_image_dimensions(image_path)
        
        if img_width is None or img_height is None:
            print(f"  ✗ Error: Could not read image dimensions from {image_path.name}")
            statistics['errors'] += 1
            continue
        
        # Convert each YOLO box to polygon
        polygons = []
        for yolo_box in yolo_boxes:
            try:
                bbox_abs, class_id = yolo_to_absolute_coords(yolo_box, img_width, img_height)
                polygon_flat = bbox_to_polygon(*bbox_abs)
                
                polygons.append({
                    'class_id': int(yolo_box[0]),
                    'polygon': polygon_flat,
                    'bbox': bbox_abs  # Keep original bbox for reference
                })
                
                statistics['total_boxes'] += 1
            
            except Exception as e:
                print(f"  ✗ Error converting box in {label_path.name}: {e}")
                statistics['errors'] += 1
        
        if polygons:
            conversions.append({
                'label_file': str(relative_label_path),
                'image_file': str(image_path.relative_to(project_root)),
                'image_width': img_width,
                'image_height': img_height,
                'polygons': polygons,
                'num_boxes': len(polygons)
            })
            
            statistics['processed'] += 1
    
    return conversions, statistics

def main():
    print("=" * 70)
    print("Task 2.2.2: YOLO BBox to Polygon Conversion")
    print("=" * 70)
    print("")
    
    # Define paths
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    base_path = project_root / base_data_path
    labels_dir = base_path / 'raw_data' / 'labels'
    images_dir = base_path / 'raw_data' / 'images'
    output_file = base_path / 'yolo_to_polygon_conversions.json'
    
    print(f"Base data path: {base_path}")
    print(f"Labels directory: {labels_dir.relative_to(project_root)}")
    print(f"Images directory: {images_dir.relative_to(project_root)}")
    print(f"Output file: {output_file.relative_to(project_root)}")
    print("")
    
    # Check if directories exist
    if not labels_dir.exists():
        print(f"⚠ Warning: Labels directory does not exist: {labels_dir}")
        print("  Creating empty conversion file...")
        print("")
        
        conversions = []
        statistics = {
            'total_label_files': 0,
            'processed': 0,
            'skipped_no_image': 0,
            'skipped_empty': 0,
            'total_boxes': 0,
            'errors': 0
        }
    else:
        # Convert YOLO labels to polygons
        print("Converting YOLO bounding boxes to polygons...")
        print("")
        
        conversions, statistics = convert_yolo_labels(labels_dir, images_dir, base_path)
    
    # Print statistics
    print("=" * 70)
    print("CONVERSION STATISTICS")
    print("=" * 70)
    print("")
    print(f"Total label files found: {statistics['total_label_files']}")
    print(f"Successfully processed: {statistics['processed']}")
    print(f"Skipped (empty files): {statistics['skipped_empty']}")
    print(f"Skipped (no corresponding image): {statistics['skipped_no_image']}")
    print(f"Total bounding boxes converted: {statistics['total_boxes']}")
    print(f"Errors encountered: {statistics['errors']}")
    print("")
    
    # Show sample conversions
    if conversions:
        print("Sample conversions (first 2):")
        print("")
        for conv in conversions[:2]:
            print(f"  Label: {Path(conv['label_file']).name}")
            print(f"  Image: {Path(conv['image_file']).name}")
            print(f"  Image size: {conv['image_width']}x{conv['image_height']}")
            print(f"  Polygons: {conv['num_boxes']}")
            if conv['polygons']:
                sample_poly = conv['polygons'][0]['polygon']
                print(f"  Sample polygon (first 8 values): {sample_poly[:8]}")
            print("")
    
    # Save conversions to JSON file
    print(f"Saving conversions to: {output_file.relative_to(project_root)}")
    
    try:
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'conversions': conversions,
                'statistics': statistics
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Conversions saved successfully ({statistics['processed']} files processed)")
        print("")
    
    except Exception as e:
        print(f"ERROR: Failed to save conversions file: {e}", file=sys.stderr)
        return 1
    
    # Summary
    print("=" * 70)
    if statistics['processed'] > 0:
        print("✓ YOLO BBox to Polygon Conversion: COMPLETED")
    else:
        print("⚠ YOLO BBox to Polygon Conversion: COMPLETED (no labels processed)")
    print("=" * 70)
    print("")
    print("Next steps:")
    print("  - Use converted polygons in etl_processor.py for SA-Co format")
    print("  - Polygons are in flat list format: [x1, y1, x2, y1, x2, y2, x1, y2]")
    print("  - Each polygon represents a 4-point rectangle converted from YOLO bbox")
    print("")
    
    # Return error code if there were processing errors
    if statistics['errors'] > 0:
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
