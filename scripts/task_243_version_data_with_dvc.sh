#!/bin/bash
# Task ID: 2.4.3
# Description: Version Data with DVC
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 2.4.3: Version Data with DVC"
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

# Determine Python executable in venv
if [ -f "$VENV_DIR/bin/python" ]; then
    PYTHON_EXE="$VENV_DIR/bin/python"
elif [ -f "$VENV_DIR/Scripts/python.exe" ]; then
    PYTHON_EXE="$VENV_DIR/Scripts/python.exe"
else
    echo "ERROR: Could not find Python executable in '$VENV_DIR'"
    exit 1
fi

# Check if DVC is initialized
if [ ! -d ".dvc" ]; then
    echo "ERROR: DVC is not initialized"
    echo ""
    echo "Please run task 1.3.2 first to initialize DVC:"
    echo "  bash scripts/task_132_dvc_initialization.sh"
    exit 1
fi

# Check if required Python packages are installed (dvc should be in pyproject.toml)
if ! "$PYTHON_EXE" -c "import dvc" 2>/dev/null; then
    echo "WARNING: dvc not found in virtual environment"
    echo ""
    echo "Installing dependencies from pyproject.toml..."
    if ! command -v uv &> /dev/null; then
        echo "ERROR: uv is not installed or not in PATH"
        echo ""
        echo "To install uv:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    uv sync
    echo ""
fi

# Check if data/images directory exists
if [ ! -d "data/images" ]; then
    echo "WARNING: data/images directory not found"
    echo "Skipping 'dvc add data/images'"
    echo ""
else
    echo "Adding data/images to DVC..."
    "$PYTHON_EXE" -m dvc add data/images
    echo "✓ data/images added to DVC"
    echo ""
fi

# Check if annotation files exist (could be data/annotations directory or JSON files)
ANNOTATIONS_ADDED=0

if [ -d "data/annotations" ]; then
    echo "Adding data/annotations to DVC..."
    "$PYTHON_EXE" -m dvc add data/annotations
    echo "✓ data/annotations added to DVC"
    echo ""
    ANNOTATIONS_ADDED=1
fi

# Check for JSON annotation files
if [ -f "data/chicken_train.json" ]; then
    echo "Adding data/chicken_train.json to DVC..."
    "$PYTHON_EXE" -m dvc add data/chicken_train.json
    echo "✓ data/chicken_train.json added to DVC"
    echo ""
    ANNOTATIONS_ADDED=1
fi

if [ -f "data/chicken_val.json" ]; then
    echo "Adding data/chicken_val.json to DVC..."
    "$PYTHON_EXE" -m dvc add data/chicken_val.json
    echo "✓ data/chicken_val.json added to DVC"
    echo ""
    ANNOTATIONS_ADDED=1
fi

if [ $ANNOTATIONS_ADDED -eq 0 ]; then
    echo "WARNING: No annotation files or directories found"
    echo "Expected one of: data/annotations, data/chicken_train.json, or data/chicken_val.json"
    echo ""
fi

# Commit to git
echo "Committing changes to git..."
# Add .dvc files (they should not be git-ignored now)
DVC_FILES_ADDED=0
for dvc_file in data/*.dvc; do
    if [ -f "$dvc_file" ]; then
        git add "$dvc_file"
        DVC_FILES_ADDED=1
    fi
done

# Also check for .dvc files in subdirectories
for dvc_file in data/**/*.dvc; do
    if [ -f "$dvc_file" ]; then
        git add "$dvc_file"
        DVC_FILES_ADDED=1
    fi
done

# Add .gitignore if it exists in data directory
if [ -f "data/.gitignore" ]; then
    git add data/.gitignore
    DVC_FILES_ADDED=1
fi

if [ $DVC_FILES_ADDED -eq 1 ]; then
    if git commit -m "Create v1.0 SA-Co dataset"; then
        echo "✓ Changes committed to git"
        echo ""
    else
        echo "WARNING: No changes to commit (files may already be committed)"
        echo ""
    fi
else
    echo "WARNING: No DVC files found to add to git"
    echo ""
fi

echo "=========================================="
echo "✓ Task 2.4.3 completed successfully"
echo "=========================================="
