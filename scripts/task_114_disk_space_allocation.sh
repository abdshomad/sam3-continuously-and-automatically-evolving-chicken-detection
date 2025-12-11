#!/bin/bash
# Task ID: 1.1.4
# Description: Disk Space Allocation
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 1.1.4: Disk Space Allocation"
echo "=========================================="
echo ""

# Check disk space using df
echo "Checking available disk space..."
echo ""

# Get disk information
DISK_INFO=$(df -h / | tail -n1)
AVAILABLE_SPACE=$(echo "$DISK_INFO" | awk '{print $4}')
FILESYSTEM=$(echo "$DISK_INFO" | awk '{print $1}')
MOUNT_POINT=$(echo "$DISK_INFO" | awk '{print $6}')

echo "----------------------------------------"
echo "Current Disk Status:"
echo "----------------------------------------"
df -h
echo ""

# Check for NVMe devices
echo "Checking for NVMe storage devices..."
echo ""

NVME_DEVICES=$(lsblk -d -o NAME,TYPE | grep -i nvme || true)

if [ -n "$NVME_DEVICES" ]; then
    echo "✓ NVMe devices detected:"
    echo "$NVME_DEVICES"
    echo ""
    
    # Get NVMe mount points and available space
    NVME_MOUNTS=$(df -h | grep -E '/dev/nvme' || true)
    if [ -n "$NVME_MOUNTS" ]; then
        echo "NVMe mount points and available space:"
        echo "$NVME_MOUNTS"
        echo ""
    else
        echo "⚠ NVMe devices found but may not be mounted"
        echo ""
    fi
else
    echo "⚠ No NVMe devices detected"
    echo "  Note: NVMe storage is preferred for fast I/O"
    echo ""
fi

# Check available space on root filesystem
echo "----------------------------------------"
echo "Space Requirements Check:"
echo "----------------------------------------"
echo "Required: ~100GB+ for images and checkpoints"
echo ""

# Check if bc is available for calculations
if ! command -v bc &> /dev/null; then
    echo "⚠ WARNING: bc command not found. Skipping precise space conversion."
    echo "Available space: ${AVAILABLE_SPACE}"
else
    # Extract numeric value from available space (handles both G and T suffixes)
    AVAILABLE_GB=$(echo "$AVAILABLE_SPACE" | sed 's/[^0-9.]//g')
    
    # Check if we have enough space (convert to GB if needed)
    if [ -z "$AVAILABLE_GB" ] || [ "$AVAILABLE_GB" = "" ]; then
        echo "Available space: ${AVAILABLE_SPACE}"
    elif echo "$AVAILABLE_SPACE" | grep -qi "T"; then
        # If in TB, convert to GB
        AVAILABLE_GB=$(echo "$AVAILABLE_GB * 1024" | bc)
        echo "Available space: ${AVAILABLE_SPACE} (${AVAILABLE_GB} GB)"
    elif echo "$AVAILABLE_SPACE" | grep -qi "G"; then
        echo "Available space: ${AVAILABLE_SPACE}"
    else
        # If in MB or KB, convert
        if echo "$AVAILABLE_SPACE" | grep -qi "M"; then
            AVAILABLE_GB=$(echo "scale=2; $AVAILABLE_GB / 1024" | bc)
            echo "Available space: ${AVAILABLE_SPACE} (~${AVAILABLE_GB} GB)"
        else
            AVAILABLE_GB=$(echo "scale=2; $AVAILABLE_GB / 1024 / 1024" | bc)
            echo "Available space: ${AVAILABLE_SPACE} (~${AVAILABLE_GB} GB)"
        fi
    fi
fi

echo ""

# Simple check: if available space contains "G" and the number is >= 100, or if it contains "T"
SPACE_OK=false
if echo "$AVAILABLE_SPACE" | grep -qiE "[0-9]+[0-9]*[GT]"; then
    # Has G or T suffix, likely sufficient
    NUM_VALUE=$(echo "$AVAILABLE_SPACE" | grep -oE "[0-9]+" | head -n1)
    if echo "$AVAILABLE_SPACE" | grep -qi "T"; then
        SPACE_OK=true
        echo "✓ Sufficient space available (TB scale)"
    elif [ -n "$NUM_VALUE" ] && [ "$NUM_VALUE" -ge 100 ]; then
        SPACE_OK=true
        echo "✓ Sufficient space available (>= 100GB)"
    else
        echo "⚠ WARNING: Available space may be less than 100GB"
        echo "  Current: ${AVAILABLE_SPACE}"
    fi
else
    echo "⚠ WARNING: Available space format unclear or may be insufficient"
    echo "  Current: ${AVAILABLE_SPACE}"
fi

echo ""

# Recommendations
echo "----------------------------------------"
echo "Recommendations:"
echo "----------------------------------------"
if [ -z "$NVME_DEVICES" ]; then
    echo "⚠ Consider using NVMe storage for better I/O performance"
fi

echo "Ensure you have at least 100GB+ free space for:"
echo "  - Dataset images"
echo "  - Model checkpoints"
echo "  - Training artifacts"
echo ""

# Final status
if [ "$SPACE_OK" = true ]; then
    echo "✓ Disk Space Allocation Check: PASSED"
    exit 0
else
    echo "⚠ Disk Space Allocation Check: WARNINGS DETECTED"
    echo "  Please ensure sufficient space is available before proceeding"
    exit 0  # Exit 0 to allow workflow to continue, but with warnings
fi
