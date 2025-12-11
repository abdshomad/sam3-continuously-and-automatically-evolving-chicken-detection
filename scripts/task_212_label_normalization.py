#!/usr/bin/env python3
"""
Task ID: 2.1.2
Description: Label Normalization
Created: 2025-01-27

This script scans LabelMe JSON files and YOLO classes.txt files to create
a mapping dictionary that merges synonymous tags (e.g., "rooster" -> "chicken",
"chick" -> "chicken").
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

def scan_labelme_files(labels_dir):
    """Scan LabelMe JSON files and extract class labels."""
    labels_found = set()
    json_files = list(labels_dir.glob("*.json"))
    
    print(f"Scanning LabelMe JSON files in {labels_dir}...")
    print(f"  Found {len(json_files)} JSON files")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # LabelMe format: shapes contain label information
            if 'shapes' in data:
                for shape in data['shapes']:
                    if 'label' in shape:
                        label = shape['label'].strip()
                        if label:
                            labels_found.add(label)
        except json.JSONDecodeError as e:
            print(f"  ⚠ Warning: Could not parse {json_file.name}: {e}")
        except Exception as e:
            print(f"  ⚠ Warning: Error reading {json_file.name}: {e}")
    
    return labels_found

def scan_yolo_classes(classes_file):
    """Scan YOLO classes.txt file and extract class names."""
    labels_found = set()
    
    if not classes_file.exists():
        return labels_found
    
    print(f"Scanning YOLO classes file: {classes_file}")
    
    try:
        with open(classes_file, 'r', encoding='utf-8') as f:
            for line in f:
                label = line.strip()
                if label:
                    labels_found.add(label)
    except Exception as e:
        print(f"  ⚠ Warning: Could not read classes file: {e}")
    
    return labels_found

def create_label_mapping(all_labels, default_mapping=None):
    """Create a mapping dictionary for synonymous tags."""
    
    if default_mapping is None:
        # Default mapping for chicken-related synonyms
        default_mapping = {
            "rooster": "chicken",
            "chick": "chicken",
            "hen": "chicken",
            "cock": "chicken",
            "roosters": "chicken",
            "chicks": "chicken",
            "hens": "chicken",
            "cocks": "chicken",
        }
    
    # Start with default mapping
    label_mapping = default_mapping.copy()
    
    # Check if any found labels match known synonyms
    all_labels_lower = {label.lower() for label in all_labels}
    
    for found_label in all_labels:
        found_label_lower = found_label.lower()
        
        # If label is already in mapping, use it
        if found_label_lower in label_mapping:
            continue
        
        # Check for case-insensitive matches
        for synonym, canonical in default_mapping.items():
            if found_label_lower == synonym.lower():
                label_mapping[found_label_lower] = canonical
                break
    
    # Add any labels that don't have mappings (keep as-is)
    for label in all_labels:
        label_lower = label.lower()
        if label_lower not in label_mapping:
            # Keep original label (no mapping needed)
            pass
    
    return label_mapping

def main():
    print("=" * 50)
    print("Task 2.1.2: Label Normalization")
    print("=" * 50)
    print("")
    
    # Define paths
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    base_path = project_root / base_data_path
    labels_dir = base_path / 'raw_data' / 'labels'
    classes_file = base_path / 'raw_data' / 'classes.txt'
    output_file = base_path / 'label_mapping.json'
    
    # Check if labels directory exists
    if not labels_dir.exists():
        print(f"⚠ Warning: Labels directory does not exist: {labels_dir}")
        print("  Creating empty mapping with default synonyms...")
        print("")
        
        # Create default mapping even if no labels found
        default_mapping = {
            "rooster": "chicken",
            "chick": "chicken",
            "hen": "chicken",
            "cock": "chicken",
            "roosters": "chicken",
            "chicks": "chicken",
            "hens": "chicken",
            "cocks": "chicken",
        }
        
        label_mapping = default_mapping
        
    else:
        # Scan for labels
        all_labels = set()
        
        # Scan LabelMe JSON files
        labelme_labels = scan_labelme_files(labels_dir)
        all_labels.update(labelme_labels)
        
        print("")
        
        # Scan YOLO classes file
        yolo_labels = scan_yolo_classes(classes_file)
        all_labels.update(yolo_labels)
        
        print("")
        
        if all_labels:
            print(f"Found {len(all_labels)} unique labels:")
            for label in sorted(all_labels):
                print(f"  - {label}")
            print("")
        else:
            print("⚠ No labels found in scanned files")
            print("  Creating default mapping with common synonyms...")
            print("")
        
        # Create mapping
        label_mapping = create_label_mapping(all_labels)
    
    # Display mapping
    print("Label mapping (synonym -> canonical):")
    print("")
    
    if label_mapping:
        for synonym, canonical in sorted(label_mapping.items()):
            print(f"  {synonym} -> {canonical}")
    else:
        print("  (no mappings defined)")
    
    print("")
    
    # Save mapping to file
    print(f"Saving label mapping to: {output_file.relative_to(project_root)}")
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(label_mapping, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Label mapping saved successfully")
        print("")
        
    except Exception as e:
        print(f"ERROR: Failed to save label mapping: {e}", file=sys.stderr)
        return 1
    
    # Summary
    print("=" * 50)
    print("✓ Label Normalization: COMPLETED")
    print("=" * 50)
    print("")
    print(f"Label mapping file: {output_file.relative_to(project_root)}")
    print(f"Total mappings: {len(label_mapping)}")
    print("")
    print("The mapping dictionary can be used to normalize labels during ETL processing.")
    print("Labels will be converted from synonyms to canonical forms.")
    print("")
    print("Next steps:")
    print("  - Use this mapping in etl_processor.py to normalize labels")
    print("  - Update mapping if new synonyms are discovered")
    print("")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
