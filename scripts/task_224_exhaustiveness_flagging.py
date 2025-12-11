#!/usr/bin/env python3
"""
Task ID: 2.2.4
Description: Exhaustiveness Flagging
Created: 2025-01-27

This script adds the is_instance_exhaustive flag to all image entries in the metadata.
This flag instructs the loss function that unannotated regions are true backgrounds.
"""

import sys
import json
from pathlib import Path

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

def add_exhaustiveness_flag(metadata_data):
    """
    Add is_instance_exhaustive flag to all image entries.
    
    Args:
        metadata_data: Dictionary containing 'images' array
        
    Returns:
        Tuple of (updated_data, statistics)
    """
    if 'images' not in metadata_data:
        return metadata_data, {
            'total_images': 0,
            'updated': 0,
            'already_flagged': 0
        }
    
    images = metadata_data['images']
    statistics = {
        'total_images': len(images),
        'updated': 0,
        'already_flagged': 0
    }
    
    # Add flag to each image entry
    for image_entry in images:
        # Check if flag already exists
        if 'is_instance_exhaustive' in image_entry:
            # Verify it's set correctly
            if image_entry['is_instance_exhaustive'] in [True, 1, 'true', '1']:
                statistics['already_flagged'] += 1
            else:
                # Update if it was set incorrectly
                image_entry['is_instance_exhaustive'] = True
                statistics['updated'] += 1
        else:
            # Add the flag
            image_entry['is_instance_exhaustive'] = True
            statistics['updated'] += 1
    
    return metadata_data, statistics

def save_metadata(metadata_data, output_file):
    """Save updated metadata to JSON file."""
    try:
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_data, f, indent=2, ensure_ascii=False)
        
        return True, None
    except Exception as e:
        return False, f"Error saving metadata file: {e}"

def main():
    print("=" * 70)
    print("Task 2.2.4: Exhaustiveness Flagging")
    print("=" * 70)
    print("")
    
    # Define paths
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    base_path = project_root / base_data_path
    input_file = base_path / 'image_metadata.json'
    output_file = base_path / 'image_metadata.json'  # Update same file
    
    print(f"Base data path: {base_path}")
    print(f"Input metadata file: {input_file.relative_to(project_root)}")
    print(f"Output metadata file: {output_file.relative_to(project_root)}")
    print("")
    
    # Load existing metadata
    print("Loading image metadata...")
    metadata_data, error = load_image_metadata(input_file)
    
    if error:
        print(f"⚠ Warning: {error}")
        print("  Creating new metadata structure with exhaustiveness flag...")
        print("")
        
        # Create empty structure
        metadata_data = {
            'images': [],
            'statistics': {
                'chicken_images': 0,
                'not_chicken_images': 0,
                'total_processed': 0,
                'total_errors': 0
            },
            'errors': []
        }
        statistics = {
            'total_images': 0,
            'updated': 0,
            'already_flagged': 0
        }
    else:
        print(f"✓ Metadata loaded successfully")
        print("")
        
        # Add exhaustiveness flag
        print("Adding is_instance_exhaustive flag to all images...")
        print("")
        
        metadata_data, statistics = add_exhaustiveness_flag(metadata_data)
    
    # Print statistics
    print("=" * 70)
    print("FLAGGING STATISTICS")
    print("=" * 70)
    print("")
    print(f"Total images in metadata: {statistics['total_images']}")
    print(f"Images updated with flag: {statistics['updated']}")
    print(f"Images already flagged: {statistics['already_flagged']}")
    print("")
    
    # Verify all entries have the flag
    if 'images' in metadata_data:
        all_flagged = all(
            entry.get('is_instance_exhaustive') in [True, 1, 'true', '1']
            for entry in metadata_data['images']
        )
        
        if all_flagged:
            print("✓ All image entries have is_instance_exhaustive=True")
        else:
            print("⚠ Warning: Some entries may be missing the flag")
        print("")
    
    # Show sample entries
    if 'images' in metadata_data and metadata_data['images']:
        print("Sample entries (first 3):")
        print("")
        for entry in metadata_data['images'][:3]:
            print(f"  ID: {entry.get('id', 'N/A')}")
            print(f"  File: {entry.get('file_name', 'N/A')}")
            print(f"  Size: {entry.get('width', 'N/A')}x{entry.get('height', 'N/A')}")
            print(f"  Text input: {entry.get('text_input', 'N/A')}")
            print(f"  is_instance_exhaustive: {entry.get('is_instance_exhaustive', 'N/A')}")
            print("")
    
    # Save updated metadata
    print(f"Saving updated metadata to: {output_file.relative_to(project_root)}")
    
    success, error = save_metadata(metadata_data, output_file)
    
    if not success:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    
    print(f"✓ Metadata saved successfully")
    print("")
    
    # Summary
    print("=" * 70)
    if statistics['total_images'] > 0:
        print("✓ Exhaustiveness Flagging: COMPLETED")
    else:
        print("⚠ Exhaustiveness Flagging: COMPLETED (no images in metadata)")
    print("=" * 70)
    print("")
    print("Next steps:")
    print("  - The is_instance_exhaustive flag is now set for all images")
    print("  - This flag instructs the loss function that unannotated regions are true backgrounds")
    print("  - Use this metadata in etl_processor.py for SA-Co format conversion")
    print("")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
