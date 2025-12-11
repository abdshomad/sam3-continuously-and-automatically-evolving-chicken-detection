#!/bin/bash
# Task ID: 1.3.3
# Description: Configure Remote Storage (Wrapper Script)
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 1.3.3: Configure Remote Storage"
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
PYTHON_SCRIPT="scripts/task_133_configure_remote_storage.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Check if DVC is initialized (required for this task)
if [ ! -d ".dvc" ]; then
    echo "WARNING: DVC is not initialized"
    echo ""
    echo "Please run task 1.3.2 first to initialize DVC:"
    echo "  bash scripts/task_132_dvc_initialization.sh"
    exit 1
fi

# Run the Python script using uv run (automatically uses the uv-managed venv)
echo "Running remote storage configuration script..."
echo ""

if uv run python "$PYTHON_SCRIPT"; then
    echo ""
    echo "✓ Remote storage configuration script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: Remote storage configuration script failed"
    exit 1
fi
