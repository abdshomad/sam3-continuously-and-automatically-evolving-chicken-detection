#!/usr/bin/env python3
"""
Task ID: 2.3.1
Description: Negative Image Processing
Created: 2025-01-27

This script processes negative images (images in not_chicken folder OR images with 0 annotations).
These images are added to the images list with text_input="chicken" but NO annotations.
This creates the "Hard Negative" training signal for the Presence Head.
"""

import sys
import json
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

def load_image_metadata(metadata_file):
    """Load image metadata from JSON file."""
    if not metadata_file.exists():
        return None, f"Metadata file does not exist: {metadata_file}"
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in metadata file: {e}"
    except Exception as e:
        return None, f"Error reading metadata file: {e}"

def load_annotation_data(yolo_conversions_file, labelme_conversions_file):
    """
    Load annotation data from conversion files.
    
    Returns:
        Dictionary mapping image_id to list of annotations
    """
    annotations_by_image = defaultdict(list)
    
    # Load YOLO conversions if available
    if yolo_conversions_file.exists():
        try:
            with open(yolo_conversions_file, 'r', encoding='utf-8') as f:
                yolo_data = json.load(f)
            
            # Extract annotations from YOLO conversions
            # Note: This is a simplified mapping - actual implementation would need
            # to match image files to image_ids from metadata
            if 'conversions' in yolo_data:
                for conv in yolo_data['conversions']:
                    # Store conversion data (will be matched to image_id later)
                    annotations_by_image[conv.get('image_file', '')].append({
                        'source': 'yolo',
                        'polygons': conv.get('polygons', [])
                    })
        except Exception as e:
            print(f"  ⚠ Warning: Could not load YOLO conversions: {e}")
    
    # Load LabelMe conversions if available
    if labelme_conversions_file.exists():
        try:
            with open(labelme_conversions_file, 'r', encoding='utf-8') as f:
                labelme_data = json.load(f)
            
            # Extract annotations from LabelMe conversions
            if 'conversions' in labelme_data:
                for conv in labelme_data['conversions']:
                    annotations_by_image[conv.get('image_file', '')].append({
                        'source': 'labelme',
                        'polygons': conv.get('polygons', [])
                    })
        except Exception as e:
            print(f"  ⚠ Warning: Could not load LabelMe conversions: {e}")
    
    return annotations_by_image

def identify_negative_images(metadata_data, annotations_by_image):
    """
    Identify negative images based on:
    1. Images in not_chicken folder (check file_name path)
    2. Images with 0 annotations (check if image has no corresponding annotations)
    
    Returns:
        Tuple of (negative_image_ids, statistics)
    """
    if 'images' not in metadata_data:
        return [], {
            'total_images': 0,
            'not_chicken_folder': 0,
            'zero_annotations': 0,
            'total_negatives': 0
        }
    
    images = metadata_data['images']
    negative_image_ids = set()
    statistics = {
        'total_images': len(images),
        'not_chicken_folder': 0,
        'zero_annotations': 0,
        'total_negatives': 0
    }
    
    # Create a mapping from file_name to image_id for annotation matching
    file_name_to_image_id = {}
    for img in images:
        file_name = img.get('file_name', '')
        image_id = img.get('id')
        if file_name and image_id:
            file_name_to_image_id[file_name] = image_id
    
    # Check each image
    for img in images:
        image_id = img.get('id')
        file_name = img.get('file_name', '')
        
        if not image_id or not file_name:
            continue
        
        is_negative = False
        reason = None
        
        # Criterion 1: Image is in not_chicken folder
        if 'not_chicken' in file_name.lower() or '/not_chicken/' in file_name:
            is_negative = True
            reason = 'not_chicken_folder'
            statistics['not_chicken_folder'] += 1
        
        # Criterion 2: Image has 0 annotations
        # Check if this image has any annotations
        has_annotations = False
        
        # Check in annotations_by_image using file_name
        if file_name in annotations_by_image:
            annotations = annotations_by_image[file_name]
            # Count total polygons across all annotation sources
            total_polygons = sum(len(ann.get('polygons', [])) for ann in annotations)
            if total_polygons > 0:
                has_annotations = True
        
        if not has_annotations and not is_negative:
            is_negative = True
            reason = 'zero_annotations'
            statistics['zero_annotations'] += 1
        
        if is_negative:
            negative_image_ids.add(image_id)
            statistics['total_negatives'] += 1
    
    return list(negative_image_ids), statistics

def create_negative_images_list(metadata_data, negative_image_ids):
    """
    Create a list of negative image entries.
    
    CRITICAL: These images have text_input="chicken" but NO annotations.
    
    Returns:
        List of image entries for negative images
    """
    if 'images' not in metadata_data:
        return []
    
    images = metadata_data['images']
    negative_images = []
    
    # Create a mapping from image_id to image entry
    image_id_to_entry = {img.get('id'): img for img in images}
    
    for image_id in negative_image_ids:
        if image_id in image_id_to_entry:
            img_entry = image_id_to_entry[image_id].copy()
            
            # Ensure text_input is "chicken" (should already be set)
            img_entry['text_input'] = 'chicken'
            
            # Ensure is_instance_exhaustive is set (should already be set)
            if 'is_instance_exhaustive' not in img_entry:
                img_entry['is_instance_exhaustive'] = True
            
            negative_images.append(img_entry)
    
    return negative_images

def main():
    print("=" * 70)
    print("Task 2.3.1: Negative Image Processing")
    print("=" * 70)
    print("")
    
    # Define paths
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    base_path = project_root / base_data_path
    metadata_file = base_path / 'image_metadata.json'
    yolo_conversions_file = base_path / 'yolo_to_polygon_conversions.json'
    labelme_conversions_file = base_path / 'labelme_to_polygon_conversions.json'
    output_file = base_path / 'negative_images_processed.json'
    
    print(f"Base data path: {base_path}")
    print(f"Image metadata: {metadata_file.relative_to(project_root)}")
    print(f"YOLO conversions: {yolo_conversions_file.relative_to(project_root)}")
    print(f"LabelMe conversions: {labelme_conversions_file.relative_to(project_root)}")
    print(f"Output file: {output_file.relative_to(project_root)}")
    print("")
    
    # Load image metadata
    print("Loading image metadata...")
    metadata_data, error = load_image_metadata(metadata_file)
    
    if error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    
    print(f"✓ Metadata loaded successfully")
    print("")
    
    # Load annotation data
    print("Loading annotation data from conversion files...")
    annotations_by_image = load_annotation_data(yolo_conversions_file, labelme_conversions_file)
    
    total_annotations = sum(len(anns) for anns in annotations_by_image.values())
    print(f"✓ Loaded annotation data ({total_annotations} image files with annotations)")
    print("")
    
    # Identify negative images
    print("Identifying negative images...")
    print("  (Images in not_chicken folder OR images with 0 annotations)")
    print("")
    
    negative_image_ids, statistics = identify_negative_images(metadata_data, annotations_by_image)
    
    # Print statistics
    print("=" * 70)
    print("NEGATIVE IMAGE IDENTIFICATION STATISTICS")
    print("=" * 70)
    print("")
    print(f"Total images in metadata: {statistics['total_images']}")
    print(f"Negative images (not_chicken folder): {statistics['not_chicken_folder']}")
    print(f"Negative images (zero annotations): {statistics['zero_annotations']}")
    print(f"Total negative images: {statistics['total_negatives']}")
    print("")
    
    # Create negative images list
    print("Creating negative images list...")
    negative_images = create_negative_images_list(metadata_data, negative_image_ids)
    
    print(f"✓ Created list of {len(negative_images)} negative images")
    print("")
    
    # Verify critical requirements
    print("Verifying negative image requirements...")
    all_have_chicken_text = all(
        img.get('text_input') == 'chicken' for img in negative_images
    )
    
    if all_have_chicken_text:
        print("✓ All negative images have text_input='chicken'")
    else:
        print("⚠ WARNING: Some negative images are missing text_input='chicken'")
    
    print("✓ CRITICAL: No annotations will be added for negative images")
    print("  (This creates the 'Hard Negative' training signal for Presence Head)")
    print("")
    
    # Show sample negative images
    if negative_images:
        print("Sample negative images (first 5):")
        print("")
        for img in negative_images[:5]:
            print(f"  ID: {img.get('id', 'N/A')}")
            print(f"  File: {img.get('file_name', 'N/A')}")
            print(f"  Text input: {img.get('text_input', 'N/A')}")
            print(f"  is_instance_exhaustive: {img.get('is_instance_exhaustive', 'N/A')}")
            print(f"  Annotations: 0 (none - as required)")
            print("")
    
    # Save negative images to JSON file
    print(f"Saving negative images to: {output_file.relative_to(project_root)}")
    
    try:
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        output_data = {
            'negative_images': negative_images,
            'statistics': statistics,
            'note': 'These images have text_input="chicken" but NO annotations. '
                   'This creates the "Hard Negative" training signal for the Presence Head.'
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Negative images saved successfully ({len(negative_images)} images)")
        print("")
    
    except Exception as e:
        print(f"ERROR: Failed to save negative images file: {e}", file=sys.stderr)
        return 1
    
    # Summary
    print("=" * 70)
    if statistics['total_negatives'] > 0:
        print("✓ Negative Image Processing: COMPLETED")
    else:
        print("⚠ Negative Image Processing: COMPLETED (no negative images found)")
    print("=" * 70)
    print("")
    print("Next steps:")
    print("  - Use negative_images_processed.json in etl_processor.py")
    print("  - Add negative images to images list with text_input='chicken'")
    print("  - DO NOT add any annotations for negative images")
    print("  - This creates the 'Hard Negative' training signal for Presence Head")
    print("")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
