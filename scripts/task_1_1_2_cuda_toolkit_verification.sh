#!/bin/bash
# Task ID: 1.1.2
# Description: CUDA Toolkit Verification
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 1.1.2: CUDA Toolkit Verification"
echo "=========================================="
echo ""

# Check if nvcc is available
if ! command -v nvcc &> /dev/null; then
    echo "ERROR: nvcc not found. CUDA Toolkit may not be installed."
    echo ""
    echo "To install CUDA Toolkit:"
    echo "  - Visit: https://developer.nvidia.com/cuda-downloads"
    echo "  - Or use conda: conda install cudatoolkit"
    exit 1
fi

echo "Running nvcc --version..."
echo ""

# Run nvcc --version and capture output
NVCC_OUTPUT=$(nvcc --version)

# Display the output
echo "$NVCC_OUTPUT"
echo ""

# Extract CUDA version
CUDA_VERSION=$(echo "$NVCC_OUTPUT" | grep "release" | sed -n 's/.*release \([0-9]\+\.[0-9]\+\).*/\1/p')

if [ -z "$CUDA_VERSION" ]; then
    echo "ERROR: Could not extract CUDA version from nvcc output"
    exit 1
fi

echo "----------------------------------------"
echo "Verification Results:"
echo "----------------------------------------"
echo "CUDA Version: $CUDA_VERSION"
echo ""

# Check if CUDA version is compatible with PyTorch 2.x (11.8 or 12.1)
CUDA_OK=false
CUDA_MAJOR=$(echo "$CUDA_VERSION" | cut -d'.' -f1)
CUDA_MINOR=$(echo "$CUDA_VERSION" | cut -d'.' -f2)

if [ "$CUDA_MAJOR" -eq 11 ] && [ "$CUDA_MINOR" -eq 8 ]; then
    CUDA_OK=true
    echo "✓ CUDA version 11.8 is compatible with PyTorch 2.x"
elif [ "$CUDA_MAJOR" -eq 12 ] && [ "$CUDA_MINOR" -eq 1 ]; then
    CUDA_OK=true
    echo "✓ CUDA version 12.1 is compatible with PyTorch 2.x"
else
    echo "⚠ WARNING: CUDA version should be 11.8 or 12.1 for PyTorch 2.x compatibility"
    echo "  Current: $CUDA_VERSION"
    echo "  Target: 11.8 or 12.1"
fi

echo ""

# Final status
if [ "$CUDA_OK" = true ]; then
    echo "✓ CUDA Toolkit Verification: PASSED"
    exit 0
else
    echo "⚠ CUDA Toolkit Verification: WARNINGS DETECTED"
    exit 0  # Exit 0 to allow workflow to continue, but with warnings
fi
