#!/bin/bash
# Task ID: 1.2.2
# Description: Create Virtual Environment
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 1.2.2: Create Virtual Environment"
echo "=========================================="
echo ""

# Environment name and Python version
VENV_DIR=".venv"
PYTHON_VERSION="3.10"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv is not installed or not in PATH"
    echo ""
    echo "To install uv:"
    echo "  1. Run: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  2. Or use pip: pip install uv"
    echo "  3. Or use homebrew: brew install uv"
    echo "  4. After installation, restart your terminal or run: source ~/.bashrc"
    exit 1
fi

echo "uv version:"
uv --version
echo ""

# Check if virtual environment already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment '$VENV_DIR' already exists. Using existing environment."
    echo ""
    echo "Environment info:"
    echo "  Location: $(pwd)/$VENV_DIR"
    if [ -f "$VENV_DIR/bin/python" ] || [ -f "$VENV_DIR/Scripts/python.exe" ]; then
        if [ -f "$VENV_DIR/bin/python" ]; then
            echo "  Python version: $("$VENV_DIR/bin/python" --version 2>&1)"
        else
            echo "  Python version: $("$VENV_DIR/Scripts/python.exe" --version 2>&1)"
        fi
    fi
    echo ""
    echo "To activate the environment, run:"
    if [ -f "$VENV_DIR/bin/activate" ]; then
        echo "  source $VENV_DIR/bin/activate"
    else
        echo "  source $VENV_DIR/Scripts/activate"
    fi
    echo ""
    echo "✓ Virtual Environment: READY (existing environment)"
    exit 0
fi

# Create the virtual environment
echo "Creating virtual environment with uv..."
echo "  Directory: $VENV_DIR"
echo "  Python version: $PYTHON_VERSION"
echo ""

if uv venv --python "$PYTHON_VERSION" "$VENV_DIR"; then
    echo ""
    echo "✓ Environment created successfully"
else
    echo ""
    echo "ERROR: Failed to create environment"
    exit 1
fi

# Verify the environment
echo ""
echo "----------------------------------------"
echo "Verification:"
echo "----------------------------------------"
echo "Environment location:"
echo "  $(pwd)/$VENV_DIR"
echo ""

# Get Python version in the new environment
echo "Python version in environment:"
if [ -f "$VENV_DIR/bin/python" ]; then
    "$VENV_DIR/bin/python" --version
elif [ -f "$VENV_DIR/Scripts/python.exe" ]; then
    "$VENV_DIR/Scripts/python.exe" --version
else
    echo "⚠ WARNING: Could not find Python executable in environment"
fi
echo ""

echo "----------------------------------------"
echo "Next Steps:"
echo "----------------------------------------"
echo "To activate the environment, run:"
if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "  source $VENV_DIR/bin/activate"
else
    echo "  source $VENV_DIR/Scripts/activate"
fi
echo ""
echo "After activation, install dependencies with:"
echo "  uv pip install -e ."
echo "  # Or install from pyproject.toml:"
echo "  uv pip install -e sam3/"
echo "  uv pip install hydra-core submitit wandb dvc"
echo ""

echo "✓ Create Virtual Environment: COMPLETED"
echo ""
echo "Next steps:"
if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "  - Activate the environment: source $VENV_DIR/bin/activate"
else
    echo "  - Activate the environment: source $VENV_DIR/Scripts/activate"
fi
echo "  - Install PyTorch (Task 1.2.3)"
echo "  - Install SAM 3 dependencies (Task 1.2.4)"
