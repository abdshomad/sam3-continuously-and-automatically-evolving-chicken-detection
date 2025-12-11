#!/bin/bash
# Task ID: 1.2.3
# Description: Install PyTorch
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 1.2.3: Install PyTorch"
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

# Detect CUDA version from nvcc if available
CUDA_VERSION=""
CUDA_INDEX="cu118"  # Default to CUDA 11.8

if command -v nvcc &> /dev/null; then
    echo "Detecting CUDA version..."
    NVCC_OUTPUT=$(nvcc --version 2>/dev/null || echo "")
    if [ -n "$NVCC_OUTPUT" ]; then
        CUDA_VERSION=$(echo "$NVCC_OUTPUT" | grep "release" | sed -n 's/.*release \([0-9]\+\.[0-9]\+\).*/\1/p')
        if [ -n "$CUDA_VERSION" ]; then
            echo "Detected CUDA version: $CUDA_VERSION"
            CUDA_MAJOR=$(echo "$CUDA_VERSION" | cut -d'.' -f1)
            CUDA_MINOR=$(echo "$CUDA_VERSION" | cut -d'.' -f2)
            
            # Determine PyTorch index URL based on CUDA version
            if [ "$CUDA_MAJOR" -eq 11 ] && [ "$CUDA_MINOR" -eq 8 ]; then
                CUDA_INDEX="cu118"
                echo "Using PyTorch index for CUDA 11.8"
            elif [ "$CUDA_MAJOR" -eq 12 ] && [ "$CUDA_MINOR" -eq 1 ]; then
                CUDA_INDEX="cu121"
                echo "Using PyTorch index for CUDA 12.1"
            elif [ "$CUDA_MAJOR" -eq 12 ] && [ "$CUDA_MINOR" -ge 6 ]; then
                CUDA_INDEX="cu126"
                echo "Using PyTorch index for CUDA 12.6+"
            else
                echo "⚠ WARNING: CUDA version $CUDA_VERSION may not be fully supported"
                echo "  Defaulting to CUDA 11.8 index. You may need to adjust manually."
            fi
        fi
    fi
    echo ""
fi

# Check if PyTorch is already installed
if python -c "import torch" 2>/dev/null; then
    TORCH_VERSION=$(python -c "import torch; print(torch.__version__)" 2>/dev/null)
    CUDA_AVAILABLE=$(python -c "import torch; print(torch.cuda.is_available())" 2>/dev/null)
    echo "PyTorch is already installed:"
    echo "  Version: $TORCH_VERSION"
    echo "  CUDA Available: $CUDA_AVAILABLE"
    echo ""
    
    if [ "$CUDA_AVAILABLE" = "True" ]; then
        CUDA_VERSION_PT=$(python -c "import torch; print(torch.version.cuda)" 2>/dev/null || echo "N/A")
        echo "  PyTorch CUDA Version: $CUDA_VERSION_PT"
        echo ""
        echo "✓ PyTorch installation verified with CUDA support"
        exit 0
    else
        echo "⚠ WARNING: PyTorch is installed but CUDA is not available"
        echo "  Reinstalling with CUDA support..."
        echo ""
    fi
fi

# Install PyTorch with CUDA support
echo "Installing PyTorch with CUDA support..."
echo "  Using index: https://download.pytorch.org/whl/$CUDA_INDEX"
echo ""

if pip install torch torchvision --index-url "https://download.pytorch.org/whl/$CUDA_INDEX"; then
    echo ""
    echo "✓ PyTorch installation completed"
else
    echo ""
    echo "ERROR: Failed to install PyTorch"
    exit 1
fi

# Verify installation
echo ""
echo "----------------------------------------"
echo "Verification:"
echo "----------------------------------------"

TORCH_VERSION=$(python -c "import torch; print(torch.__version__)" 2>/dev/null || echo "N/A")
CUDA_AVAILABLE=$(python -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "False")

echo "PyTorch Version: $TORCH_VERSION"
echo "CUDA Available: $CUDA_AVAILABLE"

if [ "$CUDA_AVAILABLE" = "True" ]; then
    CUDA_VERSION_PT=$(python -c "import torch; print(torch.version.cuda)" 2>/dev/null || echo "N/A")
    GPU_COUNT=$(python -c "import torch; print(torch.cuda.device_count())" 2>/dev/null || echo "0")
    echo "PyTorch CUDA Version: $CUDA_VERSION_PT"
    echo "GPU Count: $GPU_COUNT"
    if [ "$GPU_COUNT" -gt 0 ]; then
        GPU_NAME=$(python -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null || echo "N/A")
        echo "GPU Name: $GPU_NAME"
    fi
    echo ""
    echo "✓ PyTorch Installation: SUCCESS (with CUDA support)"
else
    echo ""
    echo "⚠ WARNING: PyTorch installed but CUDA is not available"
    echo "  This may indicate:"
    echo "    - CUDA drivers are not properly installed"
    echo "    - PyTorch was installed without CUDA support"
    echo "    - GPU is not accessible"
fi

echo ""
echo "✓ Install PyTorch: COMPLETED"
