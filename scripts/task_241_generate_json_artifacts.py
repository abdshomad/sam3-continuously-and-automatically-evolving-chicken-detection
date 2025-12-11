#!/usr/bin/env python3
"""
Task ID: 2.4.1
Description: Generate JSON Artifacts
Created: 2025-01-27

This script splits the processed dataset into train (80%) and validation (20%) sets
with stratified sampling to ensure both sets contain "Not-Chicken" examples.
Outputs SA-Co format JSON files: chicken_train.json and chicken_val.json.
"""

import sys
import json
import random
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

# Try to import sklearn for stratified splitting
try:
    from sklearn.model_selection import train_test_split
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("⚠ Warning: sklearn not available. Using simple random split instead of stratified split.", file=sys.stderr)
    print("  Install sklearn for proper stratified sampling: uv sync", file=sys.stderr)

def load_consolidated_dataset(dataset_file):
    """Load consolidated dataset from ETL processing."""
    if not dataset_file.exists():
        return None, f"Dataset file does not exist: {dataset_file}"
    
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in dataset file: {e}"
    except Exception as e:
        return None, f"Error reading dataset file: {e}"

def consolidate_from_etl_outputs(base_path):
    """
    Consolidate dataset from existing ETL output files.
    Combines image_metadata.json and negative_images_processed.json into SA-Co format.
    """
    image_metadata_file = base_path / 'image_metadata.json'
    negative_images_file = base_path / 'negative_images_processed.json'
    yolo_conversions_file = base_path / 'yolo_to_polygon_conversions.json'
    labelme_conversions_file = base_path / 'labelme_to_polygon_conversions.json'
    
    images = []
    images_by_id = {}  # Track images by ID to avoid duplicates
    annotations = []
    image_id_to_annotations = defaultdict(list)
    annotation_id_counter = 1
    
    # Load image metadata
    if image_metadata_file.exists():
        try:
            with open(image_metadata_file, 'r', encoding='utf-8') as f:
                metadata_data = json.load(f)
                if 'images' in metadata_data:
                    for img in metadata_data['images']:
                        img_id = img.get('id')
                        if img_id is not None and img_id not in images_by_id:
                            images_by_id[img_id] = img
                    print(f"  Loaded {len(metadata_data['images'])} images from image_metadata.json")
        except Exception as e:
            print(f"  ⚠ Warning: Could not load image_metadata.json: {e}")
    
    # Load negative images (avoid duplicates)
    if negative_images_file.exists():
        try:
            with open(negative_images_file, 'r', encoding='utf-8') as f:
                negative_data = json.load(f)
                if 'negative_images' in negative_data:
                    added_count = 0
                    duplicate_count = 0
                    for img in negative_data['negative_images']:
                        img_id = img.get('id')
                        if img_id is not None:
                            if img_id not in images_by_id:
                                images_by_id[img_id] = img
                                added_count += 1
                            else:
                                duplicate_count += 1
                    print(f"  Loaded {len(negative_data['negative_images'])} negative images ({added_count} new, {duplicate_count} duplicates skipped)")
        except Exception as e:
            print(f"  ⚠ Warning: Could not load negative_images_processed.json: {e}")
    
    # Convert dict to list
    images = list(images_by_id.values())
    
    # Load annotations from YOLO conversions
    if yolo_conversions_file.exists():
        try:
            with open(yolo_conversions_file, 'r', encoding='utf-8') as f:
                yolo_data = json.load(f)
                if 'conversions' in yolo_data:
                    for conv in yolo_data['conversions']:
                        image_file = conv.get('image_file', '')
                        # Find matching image by file_name
                        for img in images:
                            if img.get('file_name') == image_file or img.get('file_name', '').endswith(Path(image_file).name):
                                img_id = img.get('id')
                                if img_id:
                                    for poly_data in conv.get('polygons', []):
                                        polygon = poly_data.get('polygon', [])
                                        bbox = poly_data.get('bbox', [])
                                        
                                        ann = {
                                            'id': annotation_id_counter,
                                            'image_id': img_id,
                                            'category_id': 1,
                                            'segmentation': [polygon],  # List of polygons
                                            'bbox': bbox,
                                            'area': poly_data.get('area', 0.0),
                                            'iscrowd': 0
                                        }
                                        image_id_to_annotations[img_id].append(ann)
                                        annotation_id_counter += 1
                    if yolo_data['conversions']:
                        print(f"  Processed {len(yolo_data['conversions'])} YOLO conversions")
        except Exception as e:
            print(f"  ⚠ Warning: Could not load YOLO conversions: {e}")
    
    # Load annotations from LabelMe conversions
    if labelme_conversions_file.exists():
        try:
            with open(labelme_conversions_file, 'r', encoding='utf-8') as f:
                labelme_data = json.load(f)
                if 'conversions' in labelme_data:
                    for conv in labelme_data['conversions']:
                        image_file = conv.get('image_file', '')
                        # Find matching image by file_name
                        for img in images:
                            if img.get('file_name') == image_file or img.get('file_name', '').endswith(Path(image_file).name):
                                img_id = img.get('id')
                                if img_id:
                                    for poly_data in conv.get('polygons', []):
                                        polygon = poly_data.get('points_flat', [])
                                        
                                        ann = {
                                            'id': annotation_id_counter,
                                            'image_id': img_id,
                                            'category_id': 1,
                                            'segmentation': [polygon],  # List of polygons
                                            'bbox': poly_data.get('bbox', []),
                                            'area': poly_data.get('area', 0.0),
                                            'iscrowd': 0
                                        }
                                        image_id_to_annotations[img_id].append(ann)
                                        annotation_id_counter += 1
                    if labelme_data['conversions']:
                        print(f"  Processed {len(labelme_data['conversions'])} LabelMe conversions")
        except Exception as e:
            print(f"  ⚠ Warning: Could not load LabelMe conversions: {e}")
    
    # Flatten annotations
    for img_id, anns in image_id_to_annotations.items():
        annotations.extend(anns)
    
    # Create consolidated dataset
    consolidated = {
        'info': {
            'description': 'Chicken Detection Dataset (Consolidated from ETL outputs)',
            'version': '1.0',
            'year': 2025
        },
        'images': images,
        'annotations': annotations,
        'categories': [
            {
                'id': 1,
                'name': 'chicken'
            }
        ]
    }
    
    return consolidated

def separate_positive_negative(images, annotations):
    """Separate images into positive (with annotations) and negative (without annotations)."""
    # Get set of image_ids that have annotations
    image_ids_with_annotations = set()
    for ann in annotations:
        image_ids_with_annotations.add(ann.get('image_id'))
    
    positive_images = []
    negative_images = []
    
    for img in images:
        img_id = img.get('id')
        if img_id in image_ids_with_annotations:
            positive_images.append(img)
        else:
            negative_images.append(img)
    
    return positive_images, negative_images

def get_annotations_for_images(annotations, image_ids):
    """Get all annotations for a set of image IDs."""
    image_ids_set = set(image_ids)
    return [ann for ann in annotations if ann.get('image_id') in image_ids_set]

def stratified_split(images, annotations, train_ratio=0.8, random_seed=42):
    """
    Perform stratified split ensuring both train and val contain positive and negative samples.
    
    Args:
        images: List of image dictionaries
        annotations: List of annotation dictionaries
        train_ratio: Ratio for training set (default 0.8)
        random_seed: Random seed for reproducibility
    
    Returns:
        Tuple of (train_images, val_images, train_annotations, val_annotations)
    """
    random.seed(random_seed)
    
    # Separate positive and negative images
    positive_images, negative_images = separate_positive_negative(images, annotations)
    
    print(f"  Positive images (with annotations): {len(positive_images)}")
    print(f"  Negative images (without annotations): {len(negative_images)}")
    print("")
    
    if len(positive_images) == 0 and len(negative_images) == 0:
        print("⚠ Warning: No images found in dataset")
        return [], [], [], []
    
    # Split positive images
    if len(positive_images) > 0:
        if HAS_SKLEARN and len(positive_images) > 1:
            # Use sklearn for proper stratified split
            pos_train, pos_val = train_test_split(
                positive_images,
                test_size=1 - train_ratio,
                random_state=random_seed,
                shuffle=True
            )
        else:
            # Simple random split
            random.shuffle(positive_images)
            split_idx = int(len(positive_images) * train_ratio)
            pos_train = positive_images[:split_idx]
            pos_val = positive_images[split_idx:]
    else:
        pos_train, pos_val = [], []
    
    # Split negative images
    if len(negative_images) > 0:
        if HAS_SKLEARN and len(negative_images) > 1:
            # Use sklearn for proper stratified split
            neg_train, neg_val = train_test_split(
                negative_images,
                test_size=1 - train_ratio,
                random_state=random_seed,
                shuffle=True
            )
        else:
            # Simple random split
            random.shuffle(negative_images)
            split_idx = int(len(negative_images) * train_ratio)
            neg_train = negative_images[:split_idx]
            neg_val = negative_images[split_idx:]
    else:
        neg_train, neg_val = [], []
    
    # Combine train and val sets
    train_images = pos_train + neg_train
    val_images = pos_val + neg_val
    
    # Get corresponding annotations
    train_image_ids = {img.get('id') for img in train_images}
    val_image_ids = {img.get('id') for img in val_images}
    
    train_annotations = get_annotations_for_images(annotations, train_image_ids)
    val_annotations = get_annotations_for_images(annotations, val_image_ids)
    
    # Shuffle final sets
    random.shuffle(train_images)
    random.shuffle(val_images)
    
    return train_images, val_images, train_annotations, val_annotations

def create_saco_json(images, annotations, info=None):
    """Create SA-Co format JSON structure."""
    # Default categories for SA-Co format
    categories = [
        {
            "id": 1,
            "name": "chicken"
        }
    ]
    
    # Create info dict if not provided
    if info is None:
        info = {
            "description": "Chicken Detection Dataset",
            "version": "1.0",
            "year": 2025
        }
    
    return {
        "info": info,
        "images": images,
        "annotations": annotations,
        "categories": categories
    }

def save_json_file(data, output_file):
    """Save data to JSON file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True, None
    except Exception as e:
        return False, str(e)

def print_split_report(train_images, val_images, train_annotations, val_annotations):
    """Print a report of the train/val split."""
    
    # Count positive and negative in each set
    train_pos = sum(1 for img in train_images if any(ann.get('image_id') == img.get('id') for ann in train_annotations))
    train_neg = len(train_images) - train_pos
    
    val_pos = sum(1 for img in val_images if any(ann.get('image_id') == img.get('id') for ann in val_annotations))
    val_neg = len(val_images) - val_pos
    
    print("=" * 70)
    print("DATASET SPLIT REPORT")
    print("=" * 70)
    print("")
    
    print("TRAINING SET:")
    print(f"  Total images: {len(train_images)}")
    print(f"  Positive images (with annotations): {train_pos}")
    print(f"  Negative images (without annotations): {train_neg}")
    print(f"  Total annotations: {len(train_annotations)}")
    print("")
    
    print("VALIDATION SET:")
    print(f"  Total images: {len(val_images)}")
    print(f"  Positive images (with annotations): {val_pos}")
    print(f"  Negative images (without annotations): {val_neg}")
    print(f"  Total annotations: {len(val_annotations)}")
    print("")
    
    # Check if both sets have negatives
    if train_neg == 0:
        print("⚠ WARNING: Training set has no negative samples!")
    if val_neg == 0:
        print("⚠ WARNING: Validation set has no negative samples!")
    
    if train_neg > 0 and val_neg > 0:
        print("✓ Both train and val sets contain negative samples (stratified split successful)")
    
    print("")
    print("=" * 70)
    print("")

def main():
    print("=" * 70)
    print("Task 2.4.1: Generate JSON Artifacts")
    print("=" * 70)
    print("")
    
    # Get configuration
    base_data_path = getattr(config, 'DEFAULT_DATA_PATH', './data')
    train_ratio = getattr(config, 'TRAIN_SPLIT_RATIO', 0.8)
    random_seed = getattr(config, 'RANDOM_SEED', 42)
    
    base_path = project_root / base_data_path
    
    # Input: consolidated dataset from ETL (if exists)
    # If not, we'll need to generate from raw data (future enhancement)
    consolidated_dataset = base_path / 'chicken_consolidated.json'
    etl_output = base_path / 'etl_output.json'
    
    # Try to find consolidated dataset
    dataset_file = None
    if consolidated_dataset.exists():
        dataset_file = consolidated_dataset
    elif etl_output.exists():
        dataset_file = etl_output
    else:
        # Look for any JSON file that might be the consolidated dataset
        json_files = list(base_path.glob('*_consolidated.json'))
        if json_files:
            dataset_file = json_files[0]
    
    # Output files
    train_output = base_path / 'chicken_train.json'
    val_output = base_path / 'chicken_val.json'
    
    print(f"Base data path: {base_path}")
    print(f"Train split ratio: {train_ratio} ({(1-train_ratio)*100}% for validation)")
    print(f"Random seed: {random_seed}")
    print("")
    
    # Load dataset
    dataset = None
    if dataset_file is not None and dataset_file.exists():
        print(f"Loading consolidated dataset from: {dataset_file.relative_to(project_root)}")
        print("")
        dataset, error = load_consolidated_dataset(dataset_file)
        if dataset is None:
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
    else:
        # Try to consolidate from ETL outputs
        print("No consolidated dataset file found. Attempting to consolidate from ETL outputs...")
        print("")
        print("Looking for ETL output files:")
        print("  - image_metadata.json")
        print("  - negative_images_processed.json")
        print("  - yolo_to_polygon_conversions.json")
        print("  - labelme_to_polygon_conversions.json")
        print("")
        
        dataset = consolidate_from_etl_outputs(base_path)
        
        if not dataset or not dataset.get('images'):
            print("⚠ Warning: Could not consolidate dataset from ETL outputs.")
            print(f"  Expected consolidated file: {consolidated_dataset} or {etl_output}")
            print("")
            print("  This script expects either:")
            print("  1. A consolidated SA-Co format JSON file from ETL processing, OR")
            print("  2. ETL output files (image_metadata.json, negative_images_processed.json, etc.)")
            print("")
            print("  Please run ETL processing steps first (tasks 2.2.x and 2.3.x).")
            print("")
            return 1
        
        print(f"✓ Successfully consolidated dataset from ETL outputs")
        print("")
    
    # Extract images and annotations
    images = dataset.get('images', [])
    annotations = dataset.get('annotations', [])
    info = dataset.get('info', {})
    
    if not images:
        print("ERROR: Dataset contains no images", file=sys.stderr)
        return 1
    
    print(f"Loaded dataset:")
    print(f"  Total images: {len(images)}")
    print(f"  Total annotations: {len(annotations)}")
    print("")
    
    # Perform stratified split
    print("Performing stratified train/validation split...")
    print("")
    
    train_images, val_images, train_annotations, val_annotations = stratified_split(
        images, annotations, train_ratio=train_ratio, random_seed=random_seed
    )
    
    if len(train_images) == 0 and len(val_images) == 0:
        print("ERROR: Split resulted in empty datasets", file=sys.stderr)
        return 1
    
    # Print split report
    print_split_report(train_images, val_images, train_annotations, val_annotations)
    
    # Create SA-Co JSON structures
    train_data = create_saco_json(train_images, train_annotations, info)
    val_data = create_saco_json(val_images, val_annotations, info)
    
    # Save output files
    print(f"Saving training set to: {train_output.relative_to(project_root)}")
    success, error = save_json_file(train_data, train_output)
    if not success:
        print(f"ERROR: Failed to save training set: {error}", file=sys.stderr)
        return 1
    print("✓ Training set saved")
    print("")
    
    print(f"Saving validation set to: {val_output.relative_to(project_root)}")
    success, error = save_json_file(val_data, val_output)
    if not success:
        print(f"ERROR: Failed to save validation set: {error}", file=sys.stderr)
        return 1
    print("✓ Validation set saved")
    print("")
    
    # Summary
    print("=" * 70)
    print("✓ Generate JSON Artifacts: COMPLETED")
    print("=" * 70)
    print("")
    print(f"Training set: {train_output.relative_to(project_root)}")
    print(f"  Images: {len(train_images)}, Annotations: {len(train_annotations)}")
    print("")
    print(f"Validation set: {val_output.relative_to(project_root)}")
    print(f"  Images: {len(val_images)}, Annotations: {len(val_annotations)}")
    print("")
    print("Next steps:")
    print("  - Run schema validation (task 2.4.2)")
    print("  - Version data with DVC (task 2.4.3)")
    print("")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
