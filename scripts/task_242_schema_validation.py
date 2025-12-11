#!/usr/bin/env python3
"""
Task ID: 2.4.2
Description: Schema Validation
Created: 2025-01-27

This script validates SA-Co format JSON files to ensure they conform to the schema.
Checks for type errors (e.g., ensure id is int, segmentation is list of lists).
Uses pycocotools or custom validator.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

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

# Try to import pycocotools for validation
try:
    from pycocotools.coco import COCO
    HAS_PYCOCOTOOLS = True
except ImportError:
    HAS_PYCOCOTOOLS = False
    print("⚠ Warning: pycocotools not available. Using custom validator.", file=sys.stderr)
    print("  Install pycocotools for enhanced validation: uv sync", file=sys.stderr)

def validate_image_schema(image: Dict[str, Any], image_idx: int) -> List[str]:
    """Validate a single image entry against SA-Co schema."""
    errors = []
    
    # Required fields
    required_fields = ['id', 'file_name', 'text_input', 'height', 'width', 'is_instance_exhaustive']
    for field in required_fields:
        if field not in image:
            errors.append(f"Image {image_idx}: Missing required field '{field}'")
    
    # Validate field types
    if 'id' in image:
        if not isinstance(image['id'], int):
            errors.append(f"Image {image_idx}: 'id' must be int, got {type(image['id']).__name__}")
    
    if 'file_name' in image:
        if not isinstance(image['file_name'], str):
            errors.append(f"Image {image_idx}: 'file_name' must be str, got {type(image['file_name']).__name__}")
    
    if 'text_input' in image:
        if not isinstance(image['text_input'], str):
            errors.append(f"Image {image_idx}: 'text_input' must be str, got {type(image['text_input']).__name__}")
    
    if 'height' in image:
        if not isinstance(image['height'], int):
            errors.append(f"Image {image_idx}: 'height' must be int, got {type(image['height']).__name__}")
        elif image['height'] <= 0:
            errors.append(f"Image {image_idx}: 'height' must be positive, got {image['height']}")
    
    if 'width' in image:
        if not isinstance(image['width'], int):
            errors.append(f"Image {image_idx}: 'width' must be int, got {type(image['width']).__name__}")
        elif image['width'] <= 0:
            errors.append(f"Image {image_idx}: 'width' must be positive, got {image['width']}")
    
    if 'is_instance_exhaustive' in image:
        val = image['is_instance_exhaustive']
        if not isinstance(val, (bool, int)):
            errors.append(f"Image {image_idx}: 'is_instance_exhaustive' must be bool or int (0/1), got {type(val).__name__}")
        elif isinstance(val, int) and val not in (0, 1):
            errors.append(f"Image {image_idx}: 'is_instance_exhaustive' must be 0 or 1 if int, got {val}")
    
    return errors

def validate_annotation_schema(annotation: Dict[str, Any], ann_idx: int) -> List[str]:
    """Validate a single annotation entry against SA-Co schema."""
    errors = []
    
    # Required fields
    required_fields = ['id', 'image_id', 'category_id']
    for field in required_fields:
        if field not in annotation:
            errors.append(f"Annotation {ann_idx}: Missing required field '{field}'")
    
    # Validate field types
    if 'id' in annotation:
        if not isinstance(annotation['id'], int):
            errors.append(f"Annotation {ann_idx}: 'id' must be int, got {type(annotation['id']).__name__}")
    
    if 'image_id' in annotation:
        if not isinstance(annotation['image_id'], int):
            errors.append(f"Annotation {ann_idx}: 'image_id' must be int, got {type(annotation['image_id']).__name__}")
    
    if 'category_id' in annotation:
        if not isinstance(annotation['category_id'], int):
            errors.append(f"Annotation {ann_idx}: 'category_id' must be int, got {type(annotation['category_id']).__name__}")
    
    # Validate segmentation (if present)
    if 'segmentation' in annotation:
        seg = annotation['segmentation']
        # Segmentation can be:
        # - List of lists (polygon): [[x1, y1, x2, y2, ...], ...]
        # - Dict (RLE format): {'size': [h, w], 'counts': ...}
        if isinstance(seg, list):
            # Should be list of lists
            if len(seg) > 0 and not isinstance(seg[0], list):
                errors.append(f"Annotation {ann_idx}: 'segmentation' list should contain lists (polygons), got {type(seg[0]).__name__}")
        elif isinstance(seg, dict):
            # RLE format - check for required keys
            if 'size' not in seg or 'counts' not in seg:
                errors.append(f"Annotation {ann_idx}: 'segmentation' dict (RLE) must have 'size' and 'counts' keys")
        else:
            errors.append(f"Annotation {ann_idx}: 'segmentation' must be list or dict, got {type(seg).__name__}")
    
    # Validate bbox (if present)
    if 'bbox' in annotation:
        bbox = annotation['bbox']
        if not isinstance(bbox, list):
            errors.append(f"Annotation {ann_idx}: 'bbox' must be list, got {type(bbox).__name__}")
        elif len(bbox) != 4:
            errors.append(f"Annotation {ann_idx}: 'bbox' must have 4 elements [x, y, w, h], got {len(bbox)}")
    
    # Validate iscrowd (if present)
    if 'iscrowd' in annotation:
        val = annotation['iscrowd']
        if not isinstance(val, (bool, int)):
            errors.append(f"Annotation {ann_idx}: 'iscrowd' must be bool or int (0/1), got {type(val).__name__}")
        elif isinstance(val, int) and val not in (0, 1):
            errors.append(f"Annotation {ann_idx}: 'iscrowd' must be 0 or 1 if int, got {val}")
    
    return errors

def validate_saco_schema(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate SA-Co format JSON schema."""
    errors = []
    
    # Check top-level structure
    if not isinstance(data, dict):
        errors.append("Root element must be a dictionary")
        return False, errors
    
    # Check required top-level keys
    required_keys = ['images', 'annotations', 'categories']
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required top-level key: '{key}'")
    
    if errors:
        return False, errors
    
    # Validate images array
    images = data.get('images', [])
    if not isinstance(images, list):
        errors.append("'images' must be a list")
    else:
        image_ids = set()
        for idx, image in enumerate(images):
            if not isinstance(image, dict):
                errors.append(f"Image {idx}: must be a dictionary")
                continue
            
            # Validate image schema
            img_errors = validate_image_schema(image, idx)
            errors.extend(img_errors)
            
            # Check for duplicate IDs
            img_id = image.get('id')
            if img_id is not None:
                if img_id in image_ids:
                    errors.append(f"Image {idx}: Duplicate image ID {img_id}")
                image_ids.add(img_id)
    
    # Validate annotations array
    annotations = data.get('annotations', [])
    if not isinstance(annotations, list):
        errors.append("'annotations' must be a list")
    else:
        ann_ids = set()
        image_ids_in_annotations = set()
        
        for idx, annotation in enumerate(annotations):
            if not isinstance(annotation, dict):
                errors.append(f"Annotation {idx}: must be a dictionary")
                continue
            
            # Validate annotation schema
            ann_errors = validate_annotation_schema(annotation, idx)
            errors.extend(ann_errors)
            
            # Check for duplicate IDs
            ann_id = annotation.get('id')
            if ann_id is not None:
                if ann_id in ann_ids:
                    errors.append(f"Annotation {idx}: Duplicate annotation ID {ann_id}")
                ann_ids.add(ann_id)
            
            # Track image_ids referenced in annotations
            img_id = annotation.get('image_id')
            if img_id is not None:
                image_ids_in_annotations.add(img_id)
        
        # Check that all annotation image_ids reference valid images
        image_ids_set = {img.get('id') for img in images if isinstance(img, dict) and 'id' in img}
        invalid_image_ids = image_ids_in_annotations - image_ids_set
        if invalid_image_ids:
            errors.append(f"Annotations reference {len(invalid_image_ids)} invalid image_ids: {sorted(list(invalid_image_ids))[:10]}...")
    
    # Validate categories array
    categories = data.get('categories', [])
    if not isinstance(categories, list):
        errors.append("'categories' must be a list")
    else:
        for idx, category in enumerate(categories):
            if not isinstance(category, dict):
                errors.append(f"Category {idx}: must be a dictionary")
                continue
            
            if 'id' not in category:
                errors.append(f"Category {idx}: Missing required field 'id'")
            elif not isinstance(category.get('id'), int):
                errors.append(f"Category {idx}: 'id' must be int")
            
            if 'name' not in category:
                errors.append(f"Category {idx}: Missing required field 'name'")
            elif not isinstance(category.get('name'), str):
                errors.append(f"Category {idx}: 'name' must be str")
    
    is_valid = len(errors) == 0
    return is_valid, errors

def validate_with_pycocotools(json_file: Path) -> Tuple[bool, List[str]]:
    """Validate JSON using pycocotools COCO class."""
    errors = []
    
    try:
        coco = COCO(str(json_file))
        # If COCO initialization succeeds, basic structure is valid
        # Additional checks can be added here
        return True, errors
    except Exception as e:
        errors.append(f"pycocotools validation failed: {str(e)}")
        return False, errors

def load_json_file(json_file: Path) -> Tuple[Dict[str, Any], str]:
    """Load JSON file and return data and error message."""
    if not json_file.exists():
        return None, f"File does not exist: {json_file}"
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"
    except Exception as e:
        return None, f"Error reading file: {e}"

def print_validation_report(json_file: Path, is_valid: bool, errors: List[str], use_pycocotools: bool):
    """Print validation report."""
    print("=" * 70)
    print(f"SCHEMA VALIDATION REPORT: {json_file.name}")
    print("=" * 70)
    print("")
    
    if use_pycocotools:
        print("Validation method: pycocotools + custom validator")
    else:
        print("Validation method: custom validator")
    print("")
    
    if is_valid:
        print("✓ VALIDATION PASSED")
        print("  All schema checks passed successfully")
    else:
        print("✗ VALIDATION FAILED")
        print(f"  Found {len(errors)} error(s):")
        print("")
        for error in errors[:50]:  # Show first 50 errors
            print(f"    - {error}")
        if len(errors) > 50:
            print(f"    ... and {len(errors) - 50} more errors")
    
    print("")
    print("=" * 70)
    print("")

def main():
    print("=" * 70)
    print("Task 2.4.2: Schema Validation")
    print("=" * 70)
    print("")
    
    # Get configuration
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    base_path = project_root / base_data_path
    
    # Input files to validate
    train_file = base_path / 'chicken_train.json'
    val_file = base_path / 'chicken_val.json'
    
    print(f"Base data path: {base_path}")
    print(f"Training set: {train_file.relative_to(project_root)}")
    print(f"Validation set: {val_file.relative_to(project_root)}")
    print("")
    
    all_valid = True
    results = {}
    
    # Validate training set
    if train_file.exists():
        print(f"Validating training set...")
        print("")
        
        data, error = load_json_file(train_file)
        if data is None:
            print(f"ERROR: {error}", file=sys.stderr)
            all_valid = False
        else:
            # Try pycocotools validation if available
            pycoco_valid = True
            pycoco_errors = []
            if HAS_PYCOCOTOOLS:
                pycoco_valid, pycoco_errors = validate_with_pycocotools(train_file)
            
            # Custom validation
            custom_valid, custom_errors = validate_saco_schema(data)
            
            is_valid = pycoco_valid and custom_valid
            all_errors = pycoco_errors + custom_errors
            
            results['train'] = {
                'valid': is_valid,
                'errors': all_errors,
                'use_pycocotools': HAS_PYCOCOTOOLS
            }
            
            print_validation_report(train_file, is_valid, all_errors, HAS_PYCOCOTOOLS)
            
            if not is_valid:
                all_valid = False
    else:
        print(f"⚠ Warning: Training set file not found: {train_file}")
        print("")
        all_valid = False
    
    # Validate validation set
    if val_file.exists():
        print(f"Validating validation set...")
        print("")
        
        data, error = load_json_file(val_file)
        if data is None:
            print(f"ERROR: {error}", file=sys.stderr)
            all_valid = False
        else:
            # Try pycocotools validation if available
            pycoco_valid = True
            pycoco_errors = []
            if HAS_PYCOCOTOOLS:
                pycoco_valid, pycoco_errors = validate_with_pycocotools(val_file)
            
            # Custom validation
            custom_valid, custom_errors = validate_saco_schema(data)
            
            is_valid = pycoco_valid and custom_valid
            all_errors = pycoco_errors + custom_errors
            
            results['val'] = {
                'valid': is_valid,
                'errors': all_errors,
                'use_pycocotools': HAS_PYCOCOTOOLS
            }
            
            print_validation_report(val_file, is_valid, all_errors, HAS_PYCOCOTOOLS)
            
            if not is_valid:
                all_valid = False
    else:
        print(f"⚠ Warning: Validation set file not found: {val_file}")
        print("")
        all_valid = False
    
    # Summary
    print("=" * 70)
    if all_valid:
        print("✓ Schema Validation: COMPLETED - ALL FILES VALID")
    else:
        print("✗ Schema Validation: COMPLETED - ERRORS FOUND")
    print("=" * 70)
    print("")
    
    if all_valid:
        print("All JSON files conform to SA-Co schema.")
        print("")
        print("Next steps:")
        print("  - Version data with DVC (task 2.4.3)")
        print("  - Proceed to Phase 3: Baseline Evaluation")
    else:
        print("Please fix the validation errors before proceeding.")
        print("")
    
    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())
