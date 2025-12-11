#!/bin/bash
# Helper script to configure DVC with Google Drive
# Created: 2025-12-12

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$REPO_ROOT/.env"

echo "=========================================="
echo "DVC Google Drive Setup"
echo "=========================================="
echo ""

# Check if DVC is initialized
if [ ! -d "$REPO_ROOT/.dvc" ]; then
    echo "ERROR: DVC is not initialized"
    echo ""
    echo "Please run task 1.3.2 first to initialize DVC:"
    echo "  bash scripts/task_132_dvc_initialization.sh"
    exit 1
fi

# Check if dvc-gdrive is installed
cd "$REPO_ROOT"
if [ -f ".venv/bin/python" ]; then
    PYTHON_EXE=".venv/bin/python"
elif [ -f ".venv/Scripts/python.exe" ]; then
    PYTHON_EXE=".venv/Scripts/python.exe"
else
    echo "ERROR: Could not find virtual environment Python"
    exit 1
fi

if ! "$PYTHON_EXE" -c "import dvc_gdrive" 2>/dev/null; then
    echo "Installing dvc-gdrive..."
    if ! command -v uv &> /dev/null; then
        echo "ERROR: uv is not installed"
        exit 1
    fi
    uv sync
    echo ""
fi

echo "To set up Google Drive with DVC, you need:"
echo ""
echo "1. A Google Drive folder ID"
echo "   - Create a folder in Google Drive (or use an existing one)"
echo "   - Open the folder in Google Drive"
echo "   - The folder ID is in the URL:"
echo "     https://drive.google.com/drive/folders/FOLDER_ID_HERE"
echo "     Example: https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j"
echo "     The folder ID is: 1a2b3c4d5e6f7g8h9i0j"
echo ""
echo "2. Authenticate with Google Drive (will be done automatically on first use)"
echo ""

# Check if folder ID is already in .env
if [ -f "$ENV_FILE" ] && grep -q "^DVC_REMOTE_STORAGE_URL=" "$ENV_FILE" 2>/dev/null; then
    CURRENT_URL=$(grep "^DVC_REMOTE_STORAGE_URL=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    if [[ "$CURRENT_URL" == gdrive://* ]]; then
        echo "⚠ Found existing Google Drive configuration:"
        echo "  $CURRENT_URL"
        echo ""
        read -p "Do you want to update it? (y/n): " update_remote
        if [ "$update_remote" != "y" ] && [ "$update_remote" != "Y" ]; then
            echo "Keeping existing configuration."
            exit 0
        fi
    fi
fi

read -p "Enter your Google Drive folder ID: " folder_id

if [ -z "$folder_id" ]; then
    echo "ERROR: No folder ID provided"
    exit 1
fi

# Remove any URL encoding or extra characters
folder_id=$(echo "$folder_id" | sed 's|.*/folders/||' | sed 's|[?&].*||' | tr -d ' ')

# Validate folder ID format (should be alphanumeric, typically 33 characters)
if [ ${#folder_id} -lt 20 ] || [ ${#folder_id} -gt 50 ]; then
    echo "⚠ WARNING: Folder ID length seems unusual (${#folder_id} chars)"
    echo "  Typical Google Drive folder IDs are around 33 characters"
    read -p "Continue anyway? (y/n): " continue_anyway
    if [ "$continue_anyway" != "y" ] && [ "$continue_anyway" != "Y" ]; then
        exit 1
    fi
fi

# Create or update .env file
if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
    echo "# DVC Configuration" >> "$ENV_FILE"
    echo "" >> "$ENV_FILE"
fi

# Remove old DVC_REMOTE_STORAGE_URL if exists
if grep -q "^DVC_REMOTE_STORAGE_URL=" "$ENV_FILE" 2>/dev/null; then
    sed -i '/^DVC_REMOTE_STORAGE_URL=/d' "$ENV_FILE"
fi

# Add new configuration
echo "" >> "$ENV_FILE"
echo "DVC_REMOTE_STORAGE_URL=gdrive://$folder_id" >> "$ENV_FILE"

echo ""
echo "✓ Google Drive folder ID saved to .env file"
echo "  DVC_REMOTE_STORAGE_URL=gdrive://$folder_id"
echo ""

# Configure DVC remote
echo "Configuring DVC remote..."
cd "$REPO_ROOT"

# Find dvc command
if [ -f ".venv/bin/dvc" ]; then
    DVC_CMD=".venv/bin/dvc"
elif [ -f ".venv/Scripts/dvc.exe" ]; then
    DVC_CMD=".venv/Scripts/dvc.exe"
else
    DVC_CMD="dvc"
fi

# Check if remote already exists
if "$DVC_CMD" remote list 2>/dev/null | grep -q "storage"; then
    echo "Updating existing 'storage' remote..."
    "$DVC_CMD" remote modify storage url "gdrive://$folder_id"
else
    echo "Adding new 'storage' remote..."
    "$DVC_CMD" remote add -d storage "gdrive://$folder_id"
fi

echo ""
echo "✓ DVC remote configured"
echo ""

# Verify configuration
echo "Verifying configuration..."
if "$DVC_CMD" remote list | grep -q "storage"; then
    REMOTE_URL=$("$DVC_CMD" remote get-url storage 2>/dev/null || echo "")
    echo "  Remote name: storage"
    echo "  Remote URL: $REMOTE_URL"
    echo ""
    echo "✓ Configuration complete!"
    echo ""
    echo "Note: On first use (dvc push/pull), you will be prompted to authenticate"
    echo "      with Google Drive. Follow the OAuth flow in your browser."
    echo ""
    echo "Next steps:"
    echo "  1. Test the connection: dvc push (will prompt for authentication)"
    echo "  2. Or run the configuration script: bash scripts/task_133_configure_remote_storage.sh"
else
    echo "⚠ WARNING: Could not verify remote configuration"
    echo "  Please check manually: dvc remote list"
fi
