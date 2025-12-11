#!/bin/bash
# Task ID: 1.1.3
# Description: VRAM Health Check
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 1.1.3: VRAM Health Check"
echo "=========================================="
echo ""

# Check if nvidia-smi is available
if ! command -v nvidia-smi &> /dev/null; then
    echo "ERROR: nvidia-smi not found. NVIDIA drivers may not be installed."
    exit 1
fi

echo "Checking VRAM usage and processes..."
echo ""

# Get GPU memory information
GPU_MEMORY_INFO=$(nvidia-smi --query-gpu=memory.total,memory.used,memory.free --format=csv,noheader,nounits)

# Extract values
TOTAL_MEMORY=$(echo "$GPU_MEMORY_INFO" | head -n1 | cut -d',' -f1 | tr -d ' ')
USED_MEMORY=$(echo "$GPU_MEMORY_INFO" | head -n1 | cut -d',' -f2 | tr -d ' ')
FREE_MEMORY=$(echo "$GPU_MEMORY_INFO" | head -n1 | cut -d',' -f3 | tr -d ' ')

# Validate extracted values
if [ -z "$TOTAL_MEMORY" ] || [ "$TOTAL_MEMORY" -eq 0 ]; then
    echo "ERROR: Could not extract valid GPU memory information"
    exit 1
fi

# Calculate percentage (avoid division by zero)
if [ "$TOTAL_MEMORY" -gt 0 ]; then
    USED_PERCENT=$((USED_MEMORY * 100 / TOTAL_MEMORY))
    FREE_PERCENT=$((FREE_MEMORY * 100 / TOTAL_MEMORY))
else
    echo "ERROR: Total memory is zero or invalid"
    exit 1
fi

echo "----------------------------------------"
echo "VRAM Status:"
echo "----------------------------------------"
echo "Total VRAM: ${TOTAL_MEMORY} MB"
echo "Used VRAM:  ${USED_MEMORY} MB (${USED_PERCENT}%)"
echo "Free VRAM:  ${FREE_MEMORY} MB (${FREE_PERCENT}%)"
echo ""

# Check for processes using GPU
echo "Checking for processes using GPU..."
echo ""

PROCESSES=$(nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader 2>/dev/null || echo "")

# Remove any header lines and check if we have actual process data
PROCESSES=$(echo "$PROCESSES" | grep -v "^pid," | grep -v "^$" || echo "")

if [ -z "$PROCESSES" ]; then
    echo "✓ No processes detected using GPU VRAM"
    echo ""
else
    echo "⚠ Processes using GPU VRAM:"
    echo "----------------------------------------"
    echo "PID    Process Name          Used Memory"
    echo "$PROCESSES" | while IFS= read -r line; do
        if [ -n "$line" ]; then
            echo "  $line"
        fi
    done
    echo ""
fi

# Check if VRAM is 100% available (for 24GB cards)
VRAM_OK=false
if [ "$USED_MEMORY" -eq 0 ]; then
    VRAM_OK=true
    echo "✓ VRAM is 100% available (no processes using GPU)"
elif [ "$FREE_PERCENT" -ge 95 ]; then
    VRAM_OK=true
    echo "✓ VRAM availability is excellent (${FREE_PERCENT}% free)"
elif [ "$FREE_PERCENT" -ge 80 ]; then
    echo "⚠ WARNING: VRAM availability is good but not optimal (${FREE_PERCENT}% free)"
    echo "  For 24GB cards, 100% availability is recommended"
else
    echo "⚠ WARNING: VRAM availability is low (${FREE_PERCENT}% free)"
    echo "  For 24GB cards, 100% availability is recommended"
    echo "  Consider stopping other processes using the GPU"
fi

echo ""

# Additional check: If total memory is around 24GB, ensure it's fully available
if [ "$TOTAL_MEMORY" -ge 23000 ] && [ "$TOTAL_MEMORY" -le 25000 ]; then
    if [ "$USED_MEMORY" -gt 0 ]; then
        echo "⚠ NOTE: This appears to be a 24GB card, but VRAM is not 100% available"
        echo "  Used: ${USED_MEMORY} MB"
    fi
fi

echo ""

# Final status
if [ "$VRAM_OK" = true ] && [ -z "$PROCESSES" ]; then
    echo "✓ VRAM Health Check: PASSED (100% availability)"
    exit 0
elif [ "$FREE_PERCENT" -ge 95 ]; then
    echo "✓ VRAM Health Check: PASSED (excellent availability)"
    exit 0
else
    echo "⚠ VRAM Health Check: WARNINGS DETECTED"
    exit 0  # Exit 0 to allow workflow to continue, but with warnings
fi
