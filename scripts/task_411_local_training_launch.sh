#!/bin/bash
# Task ID: 4.1.1
# Description: Local Training Launch (Debugging)
# Created: 2025-01-15

set -e

echo "=========================================="
echo "Task 4.1.1: Local Training Launch (Debugging)"
echo "=========================================="
echo ""

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv is not installed or not in PATH"
    echo ""
    echo "To install uv:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# Ensure virtual environment exists (uv will create it if needed)
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating with uv..."
    uv venv
    echo ""
fi

# Sync dependencies to ensure all packages are installed
echo "Ensuring dependencies are installed..."
uv sync
echo ""

# Check if config file exists
CONFIG_FILE="$PROJECT_ROOT/configs/sam3_chicken_finetune.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Configuration file not found: $CONFIG_FILE"
    echo ""
    echo "Please ensure the configuration file exists before running training."
    exit 1
fi

# Check if checkpoint exists (required for training)
# Try multiple possible checkpoint names
CHECKPOINT_BASE="$PROJECT_ROOT/checkpoints"
CHECKPOINT_PATH=""
for name in "sam3_vit_h.pt" "sam3.pt" "sam3_vit_l.pt" "sam3_vit_b.pt"; do
    if [ -f "$CHECKPOINT_BASE/$name" ]; then
        CHECKPOINT_PATH="$CHECKPOINT_BASE/$name"
        echo "Found checkpoint: $CHECKPOINT_PATH"
        break
    fi
done

if [ -z "$CHECKPOINT_PATH" ]; then
    echo "WARNING: No checkpoint file found in $CHECKPOINT_BASE"
    echo "Looked for: sam3_vit_h.pt, sam3.pt, sam3_vit_l.pt, sam3_vit_b.pt"
    echo ""
    echo "The checkpoint is required for training. Please run task 1.2.5 first:"
    echo "  bash scripts/task_125_download_pretrained_weights.sh"
    exit 1
fi

# Update config to use the found checkpoint if it's different
if [ "$(basename "$CHECKPOINT_PATH")" != "sam3_vit_h.pt" ]; then
    echo "Updating config to use checkpoint: $(basename "$CHECKPOINT_PATH")"
    # This will be done when we copy the config
fi

# Check if SAM3 training script exists
TRAIN_SCRIPT="$PROJECT_ROOT/sam3/sam3/train/train.py"
if [ ! -f "$TRAIN_SCRIPT" ]; then
    echo "ERROR: SAM3 training script not found: $TRAIN_SCRIPT"
    echo ""
    echo "Please ensure SAM3 is properly set up (run task 1.2.1 first)."
    exit 1
fi

# Check if SAM3 directory exists
SAM3_DIR="$PROJECT_ROOT/sam3"
if [ ! -d "$SAM3_DIR" ]; then
    echo "ERROR: SAM3 directory not found: $SAM3_DIR"
    echo ""
    echo "Please ensure SAM3 is properly set up (run task 1.2.1 first)."
    exit 1
fi

# Check for GPU availability (optional, but good to know)
if command -v nvidia-smi &> /dev/null; then
    echo "Checking GPU availability..."
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1
    echo ""
else
    echo "WARNING: nvidia-smi not found. Training will use CPU (may be very slow)."
    echo ""
fi

# Copy config to sam3/train/configs/ if it doesn't exist there
SAM3_CONFIG_DIR="$SAM3_DIR/sam3/train/configs"
CONFIG_NAME="sam3_chicken_finetune.yaml"
SAM3_CONFIG_PATH="$SAM3_CONFIG_DIR/$CONFIG_NAME"

if [ ! -d "$SAM3_CONFIG_DIR" ]; then
    mkdir -p "$SAM3_CONFIG_DIR"
fi

# Copy config file to sam3 configs directory and replace project_root with actual path
echo "Copying config file to SAM3 configs directory..."
cp "$CONFIG_FILE" "$SAM3_CONFIG_PATH"

# Add @package _global_ header if not present (required by Hydra)
if ! grep -q "^# @package _global_" "$SAM3_CONFIG_PATH"; then
    echo "Adding @package _global_ header..."
    sed -i '1i# @package _global_' "$SAM3_CONFIG_PATH"
    # Add blank line after header if needed
    if ! sed -n '2p' "$SAM3_CONFIG_PATH" | grep -q "^$"; then
        sed -i '1a\' "$SAM3_CONFIG_PATH"
    fi
fi

# Update checkpoint path BEFORE replacing project_root if we found a different checkpoint
if [ -n "$CHECKPOINT_PATH" ] && [ "$(basename "$CHECKPOINT_PATH")" != "sam3_vit_h.pt" ]; then
    echo "Updating checkpoint path in config to: $CHECKPOINT_PATH"
    # Escape special characters in path for sed
    ESCAPED_CHECKPOINT=$(echo "$CHECKPOINT_PATH" | sed 's/[[\.*^$()+?{|]/\\&/g')
    # Replace the checkpoint path BEFORE project_root replacement
    sed -i "s|\${project_root}/checkpoints/sam3_vit_h\.pt|$ESCAPED_CHECKPOINT|g" "$SAM3_CONFIG_PATH"
fi

# Replace ${project_root} with actual PROJECT_ROOT path
echo "Replacing \${project_root} with actual path..."
sed -i "s|\${project_root}|$PROJECT_ROOT|g" "$SAM3_CONFIG_PATH"

# Also fix relative paths for train_json and val_json to be absolute
echo "Fixing dataset paths to be absolute..."
sed -i "s|train_json: data/|train_json: $PROJECT_ROOT/data/|g" "$SAM3_CONFIG_PATH"
sed -i "s|val_json: data/|val_json: $PROJECT_ROOT/data/|g" "$SAM3_CONFIG_PATH"
sed -i "s|img_dir: data/|img_dir: $PROJECT_ROOT/data/|g" "$SAM3_CONFIG_PATH"

# Temporarily modify config to set max_epochs=1 for sanity check
echo "Setting max_epochs=1 for sanity check..."
sed -i 's/^  max_epochs: [0-9]*/  max_epochs: 1/' "$SAM3_CONFIG_PATH"
echo "Config copied and modified: $SAM3_CONFIG_PATH"
echo ""

# Set environment variables for config path resolution
export PROJECT_ROOT="$PROJECT_ROOT"
export SAM3_ROOT="$SAM3_DIR"

# Suppress pkg_resources deprecation warnings from SAM3
if [ -n "$PYTHONWARNINGS" ]; then
    export PYTHONWARNINGS="$PYTHONWARNINGS,ignore::UserWarning:sam3.model_builder"
else
    export PYTHONWARNINGS="ignore::UserWarning:sam3.model_builder"
fi

# Get Python executable from project root venv (absolute path)
if [ -f "$PROJECT_ROOT/$VENV_DIR/bin/python" ]; then
    PYTHON_EXE="$PROJECT_ROOT/$VENV_DIR/bin/python"
elif [ -f "$PROJECT_ROOT/$VENV_DIR/Scripts/python.exe" ]; then
    PYTHON_EXE="$PROJECT_ROOT/$VENV_DIR/Scripts/python.exe"
else
    echo "ERROR: Could not find Python executable in '$PROJECT_ROOT/$VENV_DIR'"
    exit 1
fi

# Change to sam3 directory so Hydra can resolve configs
cd "$SAM3_DIR"

# Set PYTHONPATH to include sam3 directory for Hydra config resolution
export PYTHONPATH="$SAM3_DIR:${PYTHONPATH:-}"

# Use relative path from sam3.train package (Hydra expects configs/ prefix)
CONFIG_ARG="configs/$CONFIG_NAME"

# Run the training script using the project root venv Python
echo "Starting local training run (1 epoch sanity check)..."
echo ""
echo "Working directory: $(pwd)"
echo "Using Python: $PYTHON_EXE"
echo "Command: $PYTHON_EXE sam3/train/train.py -c $CONFIG_ARG --use-cluster 0 --num-gpus 1"
echo ""

if "$PYTHON_EXE" sam3/train/train.py -c "$CONFIG_ARG" --use-cluster 0 --num-gpus 1; then
    echo ""
    echo "✓ Local training launch completed successfully"
    echo ""
    echo "Note: This was a 1-epoch sanity check to verify data loading."
    echo "For full training, use task 4.1.2 (Cluster Training Launch)."
    exit 0
else
    echo ""
    echo "ERROR: Local training launch failed"
    echo ""
    echo "Common issues:"
    echo "  - Data files not found (check data/chicken_train.json and data/chicken_val.json)"
    echo "  - Missing dependencies (run 'uv sync' to install)"
    echo "  - GPU not available or CUDA issues"
    echo "  - Configuration errors in configs/sam3_chicken_finetune.yaml"
    exit 1
fi
