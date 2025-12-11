#!/bin/bash
# Task ID: 2.1.3
# Description: Negative Sample Verification (Wrapper Script)
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 2.1.3: Negative Sample Verification"
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
PYTHON_SCRIPT="scripts/task_213_negative_sample_verification.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Sync dependencies
echo "Syncing dependencies..."
uv sync
echo ""

# Run the Python script using uv run
echo "Running negative sample verification script..."
echo ""

if uv run python "$PYTHON_SCRIPT"; then
    echo ""
    echo "✓ Negative sample verification script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: Negative sample verification script failed"
    exit 1
fi
