#!/bin/bash
# Task ID: 1.2.5
# Description: Download Pre-trained Weights (Wrapper Script)
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 1.2.5: Download Pre-trained Weights"
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

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment not activated. Activating now..."
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    elif [ -f "$VENV_DIR/Scripts/activate" ]; then
        source "$VENV_DIR/Scripts/activate"
    else
        echo "ERROR: Could not find activation script in '$VENV_DIR'"
        exit 1
    fi
    echo "✓ Virtual environment activated"
    echo ""
fi

# Check if Python script exists
PYTHON_SCRIPT="scripts/task_125_download_pretrained_weights.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Check if required Python packages are installed
if ! python -c "import huggingface_hub" 2>/dev/null; then
    echo "ERROR: huggingface_hub not found"
    echo ""
    echo "Please run task 1.2.4 first to install SAM 3 dependencies:"
    echo "  bash scripts/task_124_install_sam3_dependencies.sh"
    exit 1
fi

# Run the Python script
echo "Running download script..."
echo ""

if python "$PYTHON_SCRIPT"; then
    echo ""
    echo "✓ Download script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: Download script failed"
    exit 1
fi
