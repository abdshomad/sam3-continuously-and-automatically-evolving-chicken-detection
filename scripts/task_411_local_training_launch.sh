#!/bin/bash
# Task ID: 4.1.1
# Description: Local Training Launch (Debugging)
# Created: 2025-01-15

set -e

echo "=========================================="
echo "Task 4.1.1: Local Training Launch (Debugging)"
echo "=========================================="
echo ""

# Check if virtual environment exists
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "ERROR: Virtual environment not found at '$VENV_DIR'"
    echo ""
    echo "Please run task 1.2.2 first to create the virtual environment:"
    echo "  bash scripts/task_122_create_virtual_environment.sh"
    exit 1
fi

# Determine Python executable in venv
if [ -f "$VENV_DIR/bin/python" ]; then
    PYTHON_EXE="$VENV_DIR/bin/python"
elif [ -f "$VENV_DIR/Scripts/python.exe" ]; then
    PYTHON_EXE="$VENV_DIR/Scripts/python.exe"
else
    echo "ERROR: Could not find Python executable in '$VENV_DIR'"
    exit 1
fi

# Check if config file exists
CONFIG_FILE="configs/sam3_chicken_finetune.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Configuration file not found: $CONFIG_FILE"
    echo ""
    echo "Please ensure the configuration file exists before running training."
    exit 1
fi

# Check if SAM3 training script exists
TRAIN_SCRIPT="sam3/train/train.py"
if [ ! -f "$TRAIN_SCRIPT" ]; then
    echo "ERROR: SAM3 training script not found: $TRAIN_SCRIPT"
    echo ""
    echo "Please ensure SAM3 is properly set up (run task 1.2.1 first)."
    exit 1
fi

# Check if required Python packages are installed
if ! "$PYTHON_EXE" -c "import torch" 2>/dev/null; then
    echo "WARNING: PyTorch not found in virtual environment"
    echo ""
    echo "Installing dependencies from pyproject.toml..."
    if ! command -v uv &> /dev/null; then
        echo "ERROR: uv is not installed or not in PATH"
        echo ""
        echo "To install uv:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    uv sync
    echo ""
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

# Run the training script
echo "Starting local training run (1 epoch sanity check)..."
echo ""
echo "Command: $PYTHON_EXE $TRAIN_SCRIPT -c $CONFIG_FILE --use-cluster 0 --num-gpus 1 trainer.max_epochs=1"
echo ""

if "$PYTHON_EXE" "$TRAIN_SCRIPT" -c "$CONFIG_FILE" --use-cluster 0 --num-gpus 1 trainer.max_epochs=1; then
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
