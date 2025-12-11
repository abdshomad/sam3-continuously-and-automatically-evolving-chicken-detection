#!/bin/bash
# Task ID: 2.1.1
# Description: Directory Structure Setup (Wrapper Script)
# Created: 2025-01-27

set -e

echo "=========================================="
echo "Task 2.1.1: Directory Structure Setup"
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
PYTHON_SCRIPT="scripts/task_211_directory_structure_setup.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Run the Python script using uv run (automatically uses the uv-managed venv)
echo "Running directory structure setup script..."
echo ""

if uv run python "$PYTHON_SCRIPT"; then
    echo ""
    echo "✓ Directory structure setup script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: Directory structure setup script failed"
    exit 1
fi
