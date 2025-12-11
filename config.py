"""
Configuration file for SAM3 Chicken Detection project.

This file contains all non-sensitive settings, configuration values, and parameters.
For secrets and credentials, use the .env file.
"""

# Project settings
PROJECT_NAME = "sam3-chicken-detection"
WANDB_PROJECT_NAME = "chicken-detection"

# WandB Settings
# Set to True to enable WandB logging, False to disable (default: OFF)
# Can be overridden by environment variable: USE_WANDB=true or USE_WANDB=false
USE_WANDB = True

# Paths
DEFAULT_CHECKPOINT_PATH = "./checkpoints"
DEFAULT_DATA_PATH = "./data"
DEFAULT_SCRIPTS_PATH = "./scripts"

# Model settings
DEFAULT_BATCH_SIZE = 32
DEFAULT_LEARNING_RATE = 1e-5

# Logging
LOG_LEVEL = "INFO"

# DVC Remote Storage Configuration
# Remote storage URL for DVC data versioning
# Can be overridden by environment variable: DVC_REMOTE_STORAGE_URL
# Examples:
#   - GDrive: DVC_REMOTE_STORAGE_URL = 'gdrive://folder-id'
#   - S3: DVC_REMOTE_STORAGE_URL = 's3://bucket-name/path'
#   - Local: DVC_REMOTE_STORAGE_URL = '/path/to/storage'
DVC_REMOTE_STORAGE_URL = 'gdrive://1T5DKMlXdH6_5E6UB0ZltbxZizgppmCsk'
