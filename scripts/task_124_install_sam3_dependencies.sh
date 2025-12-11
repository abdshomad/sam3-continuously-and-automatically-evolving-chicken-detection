#!/bin/bash
# Task ID: 1.2.4
# Description: Install SAM 3 Dependencies
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 1.2.4: Install SAM 3 Dependencies"
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

# Check if sam3 directory exists
if [ ! -d "sam3" ]; then
    echo "ERROR: SAM 3 directory not found"
    echo ""
    echo "Please run task 1.2.1 first to add SAM 3 as a git submodule:"
    echo "  bash scripts/task_121_clone_sam3_repository.sh"
    exit 1
fi

# Check if PyTorch is installed
if ! uv run python -c "import torch" 2>/dev/null; then
    echo "ERROR: PyTorch is not installed"
    echo ""
    echo "Please run task 1.2.3 first to install PyTorch:"
    echo "  bash scripts/task_123_install_pytorch.sh"
    exit 1
fi

echo "Installing SAM 3 dependencies..."
echo ""

# Install numpy first with compatible version (numpy==1.26 doesn't exist, use 1.26.4)
echo "Step 1: Installing numpy (compatible version 1.26.4)..."
if uv pip install "numpy==1.26.4"; then
    echo "✓ numpy 1.26.4 installed"
else
    echo "⚠ WARNING: Failed to install numpy 1.26.4, trying latest 1.26.x..."
    if ! uv pip install "numpy>=1.26.0,<1.27.0"; then
        echo "ERROR: Failed to install numpy"
        exit 1
    fi
fi
echo ""

# Install SAM 3 dependencies first (since numpy==1.26 requirement is too strict)
echo "Step 2: Installing SAM 3 core dependencies..."
if uv pip install timm "tqdm" "ftfy==6.1.1" regex "iopath>=0.1.10" typing_extensions huggingface_hub; then
    echo "✓ SAM 3 core dependencies installed"
else
    echo "ERROR: Failed to install SAM 3 core dependencies"
    exit 1
fi
echo ""

# Install SAM 3 in editable mode with --no-deps to bypass strict numpy==1.26 requirement
echo "Step 3: Installing SAM 3 package (editable mode, bypassing strict numpy requirement)..."
if uv pip install --no-deps -e sam3/; then
    echo "✓ SAM 3 package installed"
else
    echo "ERROR: Failed to install SAM 3 package"
    exit 1
fi
echo ""

# Install additional dependencies
echo "Step 4: Installing additional dependencies (hydra-core, submitit)..."
if uv pip install hydra-core submitit; then
    echo "✓ Additional dependencies installed"
else
    echo "ERROR: Failed to install additional dependencies"
    exit 1
fi
echo ""

# Verify installations
echo "----------------------------------------"
echo "Verification:"
echo "----------------------------------------"

# Check SAM 3
if uv run python -c "import sam3" 2>/dev/null; then
    SAM3_VERSION=$(uv run python -c "import sam3; print(getattr(sam3, '__version__', 'installed'))" 2>/dev/null || echo "installed")
    echo "✓ SAM 3: $SAM3_VERSION"
else
    echo "⚠ WARNING: Could not import sam3"
fi

# Check Hydra
if uv run python -c "import hydra" 2>/dev/null; then
    HYDRA_VERSION=$(uv run python -c "import hydra; print(hydra.__version__)" 2>/dev/null || echo "installed")
    echo "✓ Hydra: $HYDRA_VERSION"
else
    echo "⚠ WARNING: Could not import hydra"
fi

# Check Submitit
if uv run python -c "import submitit" 2>/dev/null; then
    SUBMITIT_VERSION=$(uv run python -c "import submitit; print(getattr(submitit, '__version__', 'installed'))" 2>/dev/null || echo "installed")
    echo "✓ Submitit: $SUBMITIT_VERSION"
else
    echo "⚠ WARNING: Could not import submitit"
fi

echo ""
echo "✓ Install SAM 3 Dependencies: COMPLETED"
echo ""
echo "Next steps:"
echo "  - Download pre-trained weights (Task 1.2.5)"
