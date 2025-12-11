#!/bin/bash
# Task ID: 1.2.1
# Description: Add SAM 3 as Git Submodule
# Created: 2025-12-12

set -e

echo "=========================================="
echo "Task 1.2.1: Add SAM 3 as Git Submodule"
echo "=========================================="
echo ""

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "ERROR: git is not installed. Please install git first."
    exit 1
fi

echo "Git version:"
git --version
echo ""

# Repository URL
REPO_URL="https://github.com/facebookresearch/sam3.git"
REPO_DIR="sam3"

# Check if submodule already exists in .gitmodules
if [ -f ".gitmodules" ] && grep -q "\[submodule \"$REPO_DIR\"\]" .gitmodules 2>/dev/null; then
    echo "✓ Submodule '$REPO_DIR' already exists in .gitmodules"
    echo ""
    echo "Initializing and updating submodule..."
    git submodule update --init --recursive "$REPO_DIR"
    echo ""
    echo "✓ Submodule initialized successfully"
else
    # Check if directory already exists (might be from previous clone)
    if [ -d "$REPO_DIR" ]; then
        echo "⚠ WARNING: Directory '$REPO_DIR' already exists"
        echo ""
        
        # Check if it's already a submodule
        if [ -f "$REPO_DIR/.git" ] && ! [ -d "$REPO_DIR/.git" ]; then
            # It's a submodule (has .git file, not directory)
            echo "✓ Directory appears to be a git submodule already"
            echo "Initializing submodule..."
            git submodule update --init --recursive "$REPO_DIR"
        else
            echo "Options:"
            echo "  1. Remove existing directory and add as submodule"
            echo "  2. Skip (use existing directory)"
            echo ""
            read -p "Choose option (1 or 2, default: 1): " choice
            choice=${choice:-1}
            
            if [ "$choice" = "1" ]; then
                echo "Removing existing directory..."
                rm -rf "$REPO_DIR"
                echo "Directory removed."
                echo ""
            else
                echo "Skipping submodule addition. Using existing directory."
                exit 0
            fi
        fi
    fi
    
    # Add the submodule
    if [ ! -d "$REPO_DIR" ]; then
        echo "Adding SAM 3 as git submodule..."
        echo "Repository: $REPO_URL"
        echo "Path: $REPO_DIR"
        echo ""
        
        if git submodule add "$REPO_URL" "$REPO_DIR"; then
            echo ""
            echo "✓ Submodule added successfully"
        else
            echo ""
            echo "ERROR: Failed to add submodule"
            echo "Possible causes:"
            echo "  - Network connectivity issues"
            echo "  - Repository URL is incorrect"
            echo "  - Insufficient permissions"
            echo "  - Git repository not initialized"
            exit 1
        fi
    fi
fi

# Verify submodule
echo ""
echo "----------------------------------------"
echo "Verification:"
echo "----------------------------------------"

# Check .gitmodules file
if [ -f ".gitmodules" ]; then
    echo "✓ .gitmodules file exists"
    echo ""
    echo "Submodule configuration:"
    grep -A 2 "\[submodule \"$REPO_DIR\"\]" .gitmodules || echo "  (Not found in .gitmodules)"
    echo ""
fi

# Check submodule directory
if [ -d "$REPO_DIR" ]; then
    echo "✓ Submodule directory exists: $REPO_DIR"
    
    # Check if it's properly initialized
    if [ -f "$REPO_DIR/.git" ] || [ -d "$REPO_DIR/.git" ]; then
        echo "✓ Submodule is initialized"
        
        cd "$REPO_DIR"
        echo "Current directory: $(pwd)"
        echo "Repository URL: $(git remote get-url origin 2>/dev/null || echo 'N/A')"
        
        # Show latest commit info
        echo ""
        echo "Latest commit:"
        git log -1 --oneline 2>/dev/null || echo "  (No commits yet or detached HEAD)"
        
        cd ..
    else
        echo "⚠ WARNING: Submodule directory exists but is not initialized"
        echo "Run: git submodule update --init --recursive $REPO_DIR"
    fi
else
    echo "⚠ WARNING: Submodule directory not found"
    exit 1
fi

echo ""
echo "✓ Add SAM 3 as Git Submodule: COMPLETED"
echo ""
echo "Next steps:"
echo "  - Submodule is ready at: $REPO_DIR"
echo "  - To update submodule later: git submodule update --remote $REPO_DIR"
echo "  - Proceed with environment setup (Task 1.2.2)"
echo ""
echo "Note: When others clone this repository, they should run:"
echo "  git submodule update --init --recursive"
