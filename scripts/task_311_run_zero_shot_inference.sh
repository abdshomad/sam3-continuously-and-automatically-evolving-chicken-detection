#!/bin/bash
# Task ID: 3.1.1
# Description: Run Zero-Shot Inference (Wrapper Script)
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 3.1.1: Run Zero-Shot Inference"
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

# Check if virtual environment is activated (for uv)
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment not activated. Will use venv Python directly."
    echo ""
fi

# Check if Python script exists
PYTHON_SCRIPT="scripts/task_311_run_zero_shot_inference.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Check if required Python packages are installed
if ! "$PYTHON_EXE" -c "import torch" 2>/dev/null; then
    echo "WARNING: torch not found in virtual environment"
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

# Run the Python script
echo "Running zero-shot inference script..."
echo ""

if "$PYTHON_EXE" "$PYTHON_SCRIPT"; then
    echo ""
    echo "✓ Zero-shot inference script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: Zero-shot inference script failed"
    exit 1
fi
