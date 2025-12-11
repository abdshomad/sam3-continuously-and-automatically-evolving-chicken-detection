#!/bin/bash
# Task ID: 4.3.1
# Description: Configure Checkpoint Callback (Wrapper Script)
# Created: 2025-01-15

set -e

echo "=========================================="
echo "Task 4.3.1: Configure Checkpoint Callback"
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

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

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
PYTHON_SCRIPT="$PROJECT_ROOT/scripts/task_431_configure_checkpoint_callback.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Run the Python script using uv run (automatically uses the uv-managed venv)
echo "Running checkpoint callback configuration script..."
echo ""

if uv run python "$PYTHON_SCRIPT"; then
    echo ""
    echo "✓ Checkpoint callback configuration script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: Checkpoint callback configuration script failed"
    exit 1
fi
