#!/bin/bash
# Task ID: 2.2.1
# Description: Image Metadata Extraction (Wrapper Script)
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 2.2.1: Image Metadata Extraction"
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
PYTHON_SCRIPT="scripts/task_221_image_metadata_extraction.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Sync dependencies
echo "Syncing dependencies..."
uv sync
echo ""

# Run the Python script using uv run
echo "Running image metadata extraction script..."
echo ""

if uv run python "$PYTHON_SCRIPT"; then
    echo ""
    echo "✓ Image metadata extraction script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: Image metadata extraction script failed"
    exit 1
fi
