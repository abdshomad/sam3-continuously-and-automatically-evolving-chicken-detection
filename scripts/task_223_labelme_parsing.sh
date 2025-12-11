#!/bin/bash
# Task ID: 2.2.3
# Description: LabelMe Parsing (Wrapper Script)
# Created: 2025-01-27

set -e

echo "=========================================="
echo "Task 2.2.3: LabelMe Parsing"
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
PYTHON_SCRIPT="scripts/task_223_labelme_parsing.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Sync dependencies
echo "Syncing dependencies..."
uv sync
echo ""

# Run the Python script using uv run
echo "Running LabelMe parsing script..."
echo ""

if uv run python "$PYTHON_SCRIPT"; then
    echo ""
    echo "✓ LabelMe parsing script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: LabelMe parsing script failed"
    exit 1
fi
