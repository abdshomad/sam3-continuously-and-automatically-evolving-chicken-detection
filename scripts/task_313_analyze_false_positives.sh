#!/bin/bash
# Task ID: 3.1.3
# Description: Analyze False Positives (Wrapper Script)
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 3.1.3: Analyze False Positives"
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
PYTHON_SCRIPT="scripts/task_313_analyze_false_positives.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Run the Python script
echo "Running false positives analysis script..."
echo ""

if uv run python "$PYTHON_SCRIPT"; then
    echo ""
    echo "✓ False positives analysis script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: False positives analysis script failed"
    exit 1
fi
