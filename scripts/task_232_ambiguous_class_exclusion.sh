#!/bin/bash
# Task ID: 2.3.2
# Description: Ambiguous Class Exclusion (Wrapper Script)
# Created: 2025-01-27

set -e

echo "=========================================="
echo "Task 2.3.2: Ambiguous Class Exclusion"
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

# Check if Python script exists
PYTHON_SCRIPT="scripts/task_232_ambiguous_class_exclusion.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Run the Python script
echo "Running ambiguous class exclusion script..."
echo ""

if uv run python "$PYTHON_SCRIPT"; then
    echo ""
    echo "✓ Ambiguous class exclusion script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: Ambiguous class exclusion script failed"
    exit 1
fi
