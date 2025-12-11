#!/bin/bash
# Task ID: 2.2.2
# Description: YOLO BBox to Polygon Conversion (Wrapper Script)
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 2.2.2: YOLO BBox to Polygon Conversion"
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
PYTHON_SCRIPT="scripts/task_222_yolo_bbox_to_polygon_conversion.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Sync dependencies
echo "Syncing dependencies..."
uv sync
echo ""

# Run the Python script using uv run
echo "Running YOLO bbox to polygon conversion script..."
echo ""

if uv run python "$PYTHON_SCRIPT"; then
    echo ""
    echo "✓ YOLO bbox to polygon conversion script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: YOLO bbox to polygon conversion script failed"
    exit 1
fi
