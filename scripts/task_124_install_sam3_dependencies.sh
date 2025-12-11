#!/bin/bash
# Task ID: 1.2.4
# Description: Install SAM 3 Dependencies
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 1.2.4: Install SAM 3 Dependencies"
echo "=========================================="
echo ""

# Check if virtual environment exists
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "ERROR: Virtual environment not found at '$VENV_DIR'"
    echo ""
    echo "Please run task 1.2.2 first to create the virtual environment:"
    echo "  bash scripts/task_122_create_virtual_environment.sh"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment not activated. Activating now..."
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    elif [ -f "$VENV_DIR/Scripts/activate" ]; then
        source "$VENV_DIR/Scripts/activate"
    else
        echo "ERROR: Could not find activation script in '$VENV_DIR'"
        exit 1
    fi
    echo "✓ Virtual environment activated"
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
if ! python -c "import torch" 2>/dev/null; then
    echo "ERROR: PyTorch is not installed"
    echo ""
    echo "Please run task 1.2.3 first to install PyTorch:"
    echo "  bash scripts/task_123_install_pytorch.sh"
    exit 1
fi

echo "Installing SAM 3 dependencies..."
echo ""

# Install numpy first with compatible version (numpy==1.26 may not be available, use 1.26.x)
echo "Step 1: Installing numpy (compatible version)..."
if pip install "numpy>=1.26.0,<1.27.0"; then
    echo "✓ numpy installed"
else
    echo "⚠ WARNING: Failed to install numpy, continuing anyway..."
fi
echo ""

# Install SAM 3 in editable mode
echo "Step 2: Installing SAM 3 package (editable mode)..."
if pip install -e sam3/; then
    echo "✓ SAM 3 package installed"
else
    echo "ERROR: Failed to install SAM 3 package"
    echo ""
    echo "This may be due to dependency conflicts. Trying to install with --no-deps first..."
    # Try installing without dependencies first, then install dependencies separately
    if pip install --no-deps -e sam3/ && pip install timm tqdm "ftfy==6.1.1" regex iopath typing_extensions huggingface_hub; then
        echo "✓ SAM 3 package installed (with manual dependency installation)"
    else
        echo "ERROR: Failed to install SAM 3 package even with manual dependency installation"
        exit 1
    fi
fi
echo ""

# Install additional dependencies
echo "Step 3: Installing additional dependencies (hydra-core, submitit)..."
if pip install hydra-core submitit; then
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
if python -c "import sam3" 2>/dev/null; then
    SAM3_VERSION=$(python -c "import sam3; print(getattr(sam3, '__version__', 'installed'))" 2>/dev/null || echo "installed")
    echo "✓ SAM 3: $SAM3_VERSION"
else
    echo "⚠ WARNING: Could not import sam3"
fi

# Check Hydra
if python -c "import hydra" 2>/dev/null; then
    HYDRA_VERSION=$(python -c "import hydra; print(hydra.__version__)" 2>/dev/null || echo "installed")
    echo "✓ Hydra: $HYDRA_VERSION"
else
    echo "⚠ WARNING: Could not import hydra"
fi

# Check Submitit
if python -c "import submitit" 2>/dev/null; then
    SUBMITIT_VERSION=$(python -c "import submitit; print(getattr(submitit, '__version__', 'installed'))" 2>/dev/null || echo "installed")
    echo "✓ Submitit: $SUBMITIT_VERSION"
else
    echo "⚠ WARNING: Could not import submitit"
fi

echo ""
echo "✓ Install SAM 3 Dependencies: COMPLETED"
echo ""
echo "Next steps:"
echo "  - Download pre-trained weights (Task 1.2.5)"
