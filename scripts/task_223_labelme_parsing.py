#!/usr/bin/env python3
"""
Task ID: 2.2.3
Description: LabelMe Parsing
Created: 2025-01-27

This script parses LabelMe JSON files and converts polygon points to flat list format
[x1, y1, x2, y2, ...] required by SA-Co segmentation field.
"""

import sys
import json
from pathlib import Path
from PIL import Image

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

def find_corresponding_image(labelme_json_path, images_dir, base_path):
    """Find the corresponding image file for a LabelMe JSON file."""
    # LabelMe JSON files typically have the same name as the image (without extension)
    json_stem = labelme_json_path.stem
    
    # Search in chicken and not_chicken directories
    for subdir in ['chicken', 'not_chicken']:
        image_subdir = images_dir / subdir
        if not image_subdir.exists():
            continue
        
        for ext in IMAGE_EXTENSIONS:
            # Try lowercase extension
            image_path = image_subdir / f"{json_stem}{ext}"
            if image_path.exists():
                return image_path
            
            # Try uppercase extension
            image_path = image_subdir / f"{json_stem}{ext.upper()}"
            if image_path.exists():
                return image_path
    
    # If not found in subdirs, try directly in images_dir
    for ext in IMAGE_EXTENSIONS:
        image_path = images_dir / f"{json_stem}{ext}"
        if image_path.exists():
            return image_path
        image_path = images_dir / f"{json_stem}{ext.upper()}"
        if image_path.exists():
            return image_path
    
    return None

def points_to_flat_list(points):
    """
    Convert LabelMe points format to flat list format.
    
    LabelMe format: [[x1, y1], [x2, y2], [x3, y3], ...]
    SA-Co format: [x1, y1, x2, y2, x3, y3, ...]
    
    Args:
        points: List of [x, y] coordinate pairs
        
    Returns:
        Flat list of coordinates [x1, y1, x2, y2, ...]
    """
    flat_list = []
    for point in points:
        if len(point) >= 2:
            flat_list.extend([float(point[0]), float(point[1])])
    return flat_list

def parse_labelme_file(labelme_json_path):
    """
    Parse a LabelMe JSON file and extract polygon annotations.
    
    LabelMe format:
    {
        "version": "...",
        "flags": {},
        "shapes": [
            {
                "label": "chicken",
                "points": [[x1, y1], [x2, y2], ...],
                "group_id": null,
                "shape_type": "polygon",
                "flags": {}
            },
            ...
        ],
        "imagePath": "...",
        "imageData": "...",
        "imageHeight": height,
        "imageWidth": width
    }
    
    Returns:
        List of polygon dictionaries with flat coordinate lists
    """
    polygons = []
    
    if not labelme_json_path.exists():
        return polygons
    
    try:
        with open(labelme_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract shapes from LabelMe format
        if 'shapes' in data:
            for shape_idx, shape in enumerate(data['shapes']):
                # Only process polygon shapes
                if shape.get('shape_type') != 'polygon':
                    continue
                
                # Extract points
                if 'points' in shape and len(shape['points']) > 0:
                    # Convert points to flat list format
                    flat_points = points_to_flat_list(shape['points'])
                    
                    if len(flat_points) >= 6:  # At least 3 points (x,y pairs)
                        polygon = {
                            'label': shape.get('label', 'chicken'),
                            'points_flat': flat_points,
                            'num_points': len(shape['points']),
                            'shape_index': shape_idx
                        }
                        polygons.append(polygon)
        
    except json.JSONDecodeError as e:
        print(f"  ✗ Error: Invalid JSON in {labelme_json_path.name}: {e}")
    except Exception as e:
        print(f"  ✗ Error reading {labelme_json_path.name}: {e}")
    
    return polygons

def convert_labelme_files(labels_dir, images_dir, base_path):
    """Convert all LabelMe JSON files to polygon format."""
    
    # Find all LabelMe JSON files
    json_files = sorted(labels_dir.glob("*.json"))
    
    if not json_files:
        print(f"  No LabelMe JSON files found in {labels_dir.relative_to(project_root)}")
        return [], {
            'total_json_files': 0,
            'processed': 0,
            'skipped_no_image': 0,
            'skipped_empty': 0,
            'total_polygons': 0,
            'errors': 0
        }
    
    print(f"  Found {len(json_files)} LabelMe JSON files")
    print("")
    
    conversions = []
    statistics = {
        'total_json_files': len(json_files),
        'processed': 0,
        'skipped_no_image': 0,
        'skipped_empty': 0,
        'total_polygons': 0,
        'errors': 0
    }
    
    for json_path in json_files:
        relative_json_path = json_path.relative_to(project_root)
        
        # Parse LabelMe polygons
        polygons = parse_labelme_file(json_path)
        
        if len(polygons) == 0:
            statistics['skipped_empty'] += 1
            continue
        
        # Find corresponding image
        image_path = find_corresponding_image(json_path, images_dir, base_path)
        
        if image_path is None:
            print(f"  ⚠ Warning: Could not find corresponding image for {json_path.name}")
            statistics['skipped_no_image'] += 1
            continue
        
        # Get image dimensions (prefer from image file, fallback to LabelMe JSON)
        img_width, img_height = get_image_dimensions(image_path)
        
        if img_width is None or img_height is None:
            print(f"  ✗ Error: Could not read image dimensions from {image_path.name}")
            statistics['errors'] += 1
            continue
        
        # Create conversion entry
        conversion = {
            'labelme_file': str(relative_json_path),
            'image_file': str(image_path.relative_to(project_root)),
            'image_width': img_width,
            'image_height': img_height,
            'polygons': polygons,
            'num_polygons': len(polygons)
        }
        
        conversions.append(conversion)
        statistics['processed'] += 1
        statistics['total_polygons'] += len(polygons)
    
    return conversions, statistics

def main():
    print("=" * 70)
    print("Task 2.2.3: LabelMe Parsing")
    print("=" * 70)
    print("")
    
    # Define paths
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    base_path = project_root / base_data_path
    labels_dir = base_path / 'raw_data' / 'labels'
    images_dir = base_path / 'raw_data' / 'images'
    output_file = base_path / 'labelme_to_polygon_conversions.json'
    
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
            'total_json_files': 0,
            'processed': 0,
            'skipped_no_image': 0,
            'skipped_empty': 0,
            'total_polygons': 0,
            'errors': 0
        }
    else:
        # Convert LabelMe files to polygons
        print("Parsing LabelMe JSON files and converting to polygon format...")
        print("")
        
        conversions, statistics = convert_labelme_files(labels_dir, images_dir, base_path)
    
    # Print statistics
    print("=" * 70)
    print("CONVERSION STATISTICS")
    print("=" * 70)
    print("")
    print(f"Total LabelMe JSON files found: {statistics['total_json_files']}")
    print(f"Successfully processed: {statistics['processed']}")
    print(f"Skipped (empty/no polygons): {statistics['skipped_empty']}")
    print(f"Skipped (no corresponding image): {statistics['skipped_no_image']}")
    print(f"Total polygons extracted: {statistics['total_polygons']}")
    print(f"Errors encountered: {statistics['errors']}")
    print("")
    
    # Show sample conversions
    if conversions:
        print("Sample conversions (first 2):")
        print("")
        for conv in conversions[:2]:
            print(f"  LabelMe file: {Path(conv['labelme_file']).name}")
            print(f"  Image: {Path(conv['image_file']).name}")
            print(f"  Image size: {conv['image_width']}x{conv['image_height']}")
            print(f"  Polygons: {conv['num_polygons']}")
            if conv['polygons']:
                sample_poly = conv['polygons'][0]
                flat_points = sample_poly['points_flat']
                print(f"  Sample polygon (first 8 values): {flat_points[:8]}")
                print(f"  Label: {sample_poly['label']}")
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
        print("✓ LabelMe Parsing: COMPLETED")
    else:
        print("⚠ LabelMe Parsing: COMPLETED (no LabelMe files processed)")
    print("=" * 70)
    print("")
    print("Next steps:")
    print("  - Use converted polygons in etl_processor.py for SA-Co format")
    print("  - Polygons are in flat list format: [x1, y1, x2, y2, ...]")
    print("  - Each polygon represents a segmentation mask from LabelMe annotations")
    print("")
    
    # Return error code if there were processing errors
    if statistics['errors'] > 0:
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
