#!/bin/bash
# Task ID: 2.3.1
# Description: Negative Image Processing (Wrapper Script)
# Created: 2025-01-27

set -e

echo "=========================================="
echo "Task 2.3.1: Negative Image Processing"
echo "=========================================="
echo ""

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv not found. Please install uv first."
    echo ""
    echo "Visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Ensure virtual environment exists
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    uv venv
    echo ""
fi

# Check if Python script exists
PYTHON_SCRIPT="scripts/task_231_negative_image_processing.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Sync dependencies
echo "Syncing dependencies..."
uv sync
echo ""

# Run the Python script using uv run
echo "Running negative image processing script..."
echo ""

if uv run python "$PYTHON_SCRIPT"; then
    echo ""
    echo "✓ Negative image processing script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: Negative image processing script failed"
    exit 1
fi
