#!/bin/bash
# Task ID: 1.2.2
# Description: Create Virtual Environment
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 1.2.2: Create Virtual Environment"
echo "=========================================="
echo ""

# Environment name
ENV_NAME="sam3_chicken"
PYTHON_VERSION="3.10"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda is not installed or not in PATH"
    echo ""
    echo "To install conda:"
    echo "  1. Download Miniconda: https://docs.conda.io/en/latest/miniconda.html"
    echo "  2. Or install Anaconda: https://www.anaconda.com/products/distribution"
    echo "  3. After installation, restart your terminal or run: source ~/.bashrc"
    exit 1
fi

echo "Conda version:"
conda --version
echo ""

# Check if environment already exists
if conda env list | grep -q "^${ENV_NAME}\s"; then
    echo "⚠ WARNING: Environment '$ENV_NAME' already exists"
    echo ""
    echo "Options:"
    echo "  1. Use existing environment (skip creation)"
    echo "  2. Remove existing environment and create fresh"
    echo ""
    read -p "Choose option (1 or 2, default: 1): " choice
    choice=${choice:-1}
    
    if [ "$choice" = "2" ]; then
        echo "Removing existing environment..."
        conda env remove -n "$ENV_NAME" -y
        echo "Environment removed."
        echo ""
    else
        echo "Using existing environment. Skipping creation."
        echo ""
        echo "Environment info:"
        conda env list | grep "^${ENV_NAME}\s"
        echo ""
        echo "To activate the environment, run:"
        echo "  conda activate $ENV_NAME"
        echo ""
        echo "✓ Virtual Environment: READY (existing environment)"
        exit 0
    fi
fi

# Create the environment
echo "Creating Conda environment..."
echo "  Name: $ENV_NAME"
echo "  Python version: $PYTHON_VERSION"
echo ""

if conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y; then
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
echo "Environment list:"
conda env list | grep -E "^(${ENV_NAME}|#)" || conda env list
echo ""

# Get Python version in the new environment
echo "Python version in environment:"
conda run -n "$ENV_NAME" python --version
echo ""

echo "----------------------------------------"
echo "Next Steps:"
echo "----------------------------------------"
echo "To activate the environment, run:"
echo "  conda activate $ENV_NAME"
echo ""
echo "Note: In scripts, you may need to:"
echo "  1. Source conda: eval \"\$(conda shell.bash hook)\""
echo "  2. Then activate: conda activate $ENV_NAME"
echo ""
echo "Or use conda run to execute commands in the environment:"
echo "  conda run -n $ENV_NAME python --version"
echo ""

echo "✓ Create Virtual Environment: COMPLETED"
echo ""
echo "Next steps:"
echo "  - Activate the environment: conda activate $ENV_NAME"
echo "  - Install PyTorch (Task 1.2.3)"
echo "  - Install SAM 3 dependencies (Task 1.2.4)"
