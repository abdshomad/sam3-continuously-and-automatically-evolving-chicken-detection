#!/bin/bash
# Task ID: 4.2.3
# Description: Watch Gradient Norms (Wrapper Script)
# Created: 2025-01-15

set -e

echo "=========================================="
echo "Task 4.2.3: Watch Gradient Norms"
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
PYTHON_SCRIPT="$PROJECT_ROOT/scripts/task_423_watch_gradient_norms.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Pass through any command line arguments to the Python script
# Run the Python script using uv run (automatically uses the uv-managed venv)
echo "Running gradient norm monitoring script..."
echo ""

if uv run python "$PYTHON_SCRIPT" "$@"; then
    echo ""
    echo "✓ Gradient norm monitoring script completed successfully"
    exit 0
else
    echo ""
    echo "ERROR: Gradient norm monitoring script failed"
    exit 1
fi
