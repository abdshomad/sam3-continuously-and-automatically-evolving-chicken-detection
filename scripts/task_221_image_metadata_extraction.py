#!/usr/bin/env python3
"""
Task ID: 2.2.1
Description: Image Metadata Extraction
Created: 2025-01-27

This script extracts image metadata (dimensions, file paths) and creates
metadata entries with text_input="chicken" for all images (both positive and negative).
This prepares the data structure for SA-Co format conversion.
"""

import sys
import json
import hashlib
from pathlib import Path
from PIL import Image
import os

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

def generate_image_id(image_path, index):
    """Generate a unique image ID based on filename hash and index."""
    # Use a combination of filename hash and index for uniqueness
    filename = image_path.name
    hash_obj = hashlib.md5(filename.encode())
    hash_hex = hash_obj.hexdigest()[:8]
    # Combine index and hash for a unique but deterministic ID
    image_id = int(hash_hex, 16) % 1000000000  # Keep it reasonable size
    return image_id

def extract_image_metadata(image_path, base_path, image_id):
    """Extract metadata from an image file."""
    try:
        # Open image using PIL
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Get relative path from base data directory
            try:
                relative_path = image_path.relative_to(base_path)
            except ValueError:
                # If not relative to base_path, use absolute path
                relative_path = Path(image_path.name)
            
            # Create metadata entry
            metadata = {
                'id': image_id,
                'file_name': str(relative_path),
                'height': height,
                'width': width,
                'text_input': 'chicken'  # CRITICAL: Always "chicken" for both positive and negative
            }
            
            return metadata, None
    
    except Exception as e:
        error_msg = f"Error processing {image_path.name}: {e}"
        return None, error_msg

def process_images(chicken_dir, not_chicken_dir, base_path):
    """Process all images from both directories and extract metadata."""
    
    metadata_list = []
    errors = []
    statistics = {
        'chicken_images': 0,
        'not_chicken_images': 0,
        'total_processed': 0,
        'total_errors': 0
    }
    
    # Process chicken images
    print("Processing chicken images...")
    chicken_images = get_image_files(chicken_dir)
    statistics['chicken_images'] = len(chicken_images)
    
    for idx, image_path in enumerate(chicken_images, start=1):
        image_id = generate_image_id(image_path, idx)
        metadata, error = extract_image_metadata(image_path, base_path, image_id)
        
        if metadata:
            metadata_list.append(metadata)
            statistics['total_processed'] += 1
            if idx % 10 == 0 or idx == len(chicken_images):
                print(f"  Processed {idx}/{len(chicken_images)} chicken images...")
        else:
            errors.append(error)
            statistics['total_errors'] += 1
            print(f"  ✗ {error}")
    
    print("")
    
    # Process not_chicken images
    print("Processing not_chicken images...")
    not_chicken_images = get_image_files(not_chicken_dir)
    statistics['not_chicken_images'] = len(not_chicken_images)
    
    start_idx = len(chicken_images) + 1
    for idx, image_path in enumerate(not_chicken_images, start=start_idx):
        image_id = generate_image_id(image_path, idx)
        metadata, error = extract_image_metadata(image_path, base_path, image_id)
        
        if metadata:
            metadata_list.append(metadata)
            statistics['total_processed'] += 1
            if (idx - start_idx + 1) % 10 == 0 or idx == start_idx + len(not_chicken_images) - 1:
                print(f"  Processed {idx - start_idx + 1}/{len(not_chicken_images)} not_chicken images...")
        else:
            errors.append(error)
            statistics['total_errors'] += 1
            print(f"  ✗ {error}")
    
    print("")
    
    return metadata_list, errors, statistics

def main():
    print("=" * 70)
    print("Task 2.2.1: Image Metadata Extraction")
    print("=" * 70)
    print("")
    
    # Define paths
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    base_path = project_root / base_data_path
    chicken_dir = base_path / 'raw_data' / 'images' / 'chicken'
    not_chicken_dir = base_path / 'raw_data' / 'images' / 'not_chicken'
    output_file = base_path / 'image_metadata.json'
    
    print(f"Base data path: {base_path}")
    print(f"Chicken images: {chicken_dir.relative_to(project_root)}")
    print(f"Not-chicken images: {not_chicken_dir.relative_to(project_root)}")
    print(f"Output file: {output_file.relative_to(project_root)}")
    print("")
    
    # Check if directories exist
    if not chicken_dir.exists() and not not_chicken_dir.exists():
        print("⚠ Warning: Neither chicken nor not_chicken directories exist.")
        print("  Please ensure images are placed in the correct directories.")
        print("  Creating empty metadata file...")
        print("")
        
        # Create empty metadata structure
        metadata_list = []
        statistics = {
            'chicken_images': 0,
            'not_chicken_images': 0,
            'total_processed': 0,
            'total_errors': 0
        }
        errors = []
    else:
        # Process images
        metadata_list, errors, statistics = process_images(chicken_dir, not_chicken_dir, base_path)
    
    # Print statistics
    print("=" * 70)
    print("EXTRACTION STATISTICS")
    print("=" * 70)
    print("")
    print(f"Chicken images found: {statistics['chicken_images']}")
    print(f"Not-chicken images found: {statistics['not_chicken_images']}")
    print(f"Total images processed: {statistics['total_processed']}")
    print(f"Total errors: {statistics['total_errors']}")
    print("")
    
    if errors:
        print("ERRORS ENCOUNTERED:")
        print("")
        for error in errors:
            print(f"  ✗ {error}")
        print("")
    
    # Verify all entries have text_input="chicken"
    all_have_chicken_text = all(entry.get('text_input') == 'chicken' for entry in metadata_list)
    if not all_have_chicken_text:
        print("⚠ WARNING: Some entries are missing text_input='chicken'!")
        print("")
    else:
        print("✓ All metadata entries have text_input='chicken' (as required)")
        print("")
    
    # Save metadata to JSON file
    print(f"Saving metadata to: {output_file.relative_to(project_root)}")
    
    try:
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'images': metadata_list,
                'statistics': statistics,
                'errors': errors
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Metadata saved successfully ({len(metadata_list)} images)")
        print("")
        
        # Show sample entries
        if metadata_list:
            print("Sample metadata entries (first 3):")
            print("")
            for entry in metadata_list[:3]:
                print(f"  ID: {entry['id']}")
                print(f"  File: {entry['file_name']}")
                print(f"  Size: {entry['width']}x{entry['height']}")
                print(f"  Text input: {entry['text_input']}")
                print("")
    
    except Exception as e:
        print(f"ERROR: Failed to save metadata file: {e}", file=sys.stderr)
        return 1
    
    # Summary
    print("=" * 70)
    if statistics['total_processed'] > 0:
        print("✓ Image Metadata Extraction: COMPLETED")
    else:
        print("⚠ Image Metadata Extraction: COMPLETED (no images found)")
    print("=" * 70)
    print("")
    print("Next steps:")
    print("  - Use this metadata in etl_processor.py for SA-Co format conversion")
    print("  - Each image entry has text_input='chicken' for SAM 3 compatibility")
    print("  - Image dimensions are ready for annotation coordinate conversion")
    print("")
    
    # Return error code if there were processing errors
    if statistics['total_errors'] > 0:
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
