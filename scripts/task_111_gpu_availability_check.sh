#!/bin/bash
# Task ID: 1.1.1
# Description: GPU Availability Check
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 1.1.1: GPU Availability Check"
echo "=========================================="
echo ""

# Check if nvidia-smi is available
if ! command -v nvidia-smi &> /dev/null; then
    echo "ERROR: nvidia-smi not found. NVIDIA drivers may not be installed."
    exit 1
fi

echo "Running nvidia-smi..."
echo ""

# Run nvidia-smi and capture output
NVIDIA_OUTPUT=$(nvidia-smi)

# Display the output
echo "$NVIDIA_OUTPUT"
echo ""

# Extract GPU model and driver version
GPU_MODEL=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits | head -n1)
DRIVER_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits | head -n1)

echo "----------------------------------------"
echo "Verification Results:"
echo "----------------------------------------"
echo "GPU Model: $GPU_MODEL"
echo "Driver Version: $DRIVER_VERSION"
echo ""

# Check if GPU model matches target (A100/H100 or RTX 3090/4090)
GPU_OK=false
if echo "$GPU_MODEL" | grep -qiE "(A100|H100|RTX 3090|RTX 4090)"; then
    GPU_OK=true
    echo "✓ GPU model matches target (A100/H100 or RTX 3090/4090)"
else
    echo "⚠ WARNING: GPU model does not match target (A100/H100 or RTX 3090/4090)"
    echo "  Detected: $GPU_MODEL"
fi

# Check driver version (extract major version number)
DRIVER_MAJOR=$(echo "$DRIVER_VERSION" | cut -d'.' -f1)
DRIVER_MINOR=$(echo "$DRIVER_VERSION" | cut -d'.' -f2)

# Validate driver version components
if [ -z "$DRIVER_MAJOR" ] || ! [ "$DRIVER_MAJOR" -eq "$DRIVER_MAJOR" ] 2>/dev/null; then
    echo "⚠ WARNING: Could not parse driver version"
    echo "  Current: $DRIVER_VERSION"
    DRIVER_OK=false
else
    # Compare driver version (need >= 525.xx)
    DRIVER_OK=false
    if [ "$DRIVER_MAJOR" -gt 525 ]; then
        DRIVER_OK=true
        echo "✓ Driver version is >= 525.xx"
    elif [ "$DRIVER_MAJOR" -eq 525 ] && [ -n "$DRIVER_MINOR" ]; then
        DRIVER_OK=true
        echo "✓ Driver version is >= 525.xx"
    else
        echo "⚠ WARNING: Driver version should be >= 525.xx"
        echo "  Current: $DRIVER_VERSION"
    fi
fi

echo ""

# Final status
if [ "$GPU_OK" = true ] && [ "$DRIVER_OK" = true ]; then
    echo "✓ GPU Availability Check: PASSED"
    exit 0
else
    echo "⚠ GPU Availability Check: WARNINGS DETECTED"
    exit 0  # Exit 0 to allow workflow to continue, but with warnings
fi
