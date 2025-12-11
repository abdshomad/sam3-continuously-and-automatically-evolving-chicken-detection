#!/bin/bash
# Helper script to login to WandB
# This script helps you add your WandB API key to .env file

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$REPO_ROOT/.env"

echo "=========================================="
echo "WandB Login Helper"
echo "=========================================="
echo ""

# Check if .env exists, create if not
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating .env file..."
    touch "$ENV_FILE"
    echo "# WandB Configuration" >> "$ENV_FILE"
    echo "" >> "$ENV_FILE"
fi

# Check if WANDB_API_KEY already exists
if grep -q "^WANDB_API_KEY=" "$ENV_FILE" 2>/dev/null; then
    echo "⚠ WARNING: WANDB_API_KEY already exists in .env file"
    echo ""
    read -p "Do you want to update it? (y/n): " update_key
    if [ "$update_key" != "y" ] && [ "$update_key" != "Y" ]; then
        echo "Keeping existing key."
        exit 0
    fi
    # Remove old key
    sed -i '/^WANDB_API_KEY=/d' "$ENV_FILE"
fi

echo "To get your WandB API key:"
echo "  1. Visit: https://wandb.ai/authorize"
echo "  2. Copy your API key"
echo ""
read -p "Enter your WandB API key: " api_key

if [ -z "$api_key" ]; then
    echo "ERROR: No API key provided"
    exit 1
fi

# Add the key to .env
echo "" >> "$ENV_FILE"
echo "WANDB_API_KEY=$api_key" >> "$ENV_FILE"

echo ""
echo "✓ API key added to .env file"
echo ""

# Verify login
echo "Verifying login..."
cd "$REPO_ROOT"

if [ -f ".venv/bin/python" ]; then
    PYTHON_EXE=".venv/bin/python"
elif [ -f ".venv/Scripts/python.exe" ]; then
    PYTHON_EXE=".venv/Scripts/python.exe"
else
    echo "⚠ WARNING: Could not find virtual environment Python"
    echo "Please run the initialization script manually:"
    echo "  python3 scripts/task_131_wandb_initialization.py"
    exit 0
fi

# Test the login
if "$PYTHON_EXE" -c "import wandb; import os; from dotenv import load_dotenv; from pathlib import Path; load_dotenv(Path('.env')); wandb.login(key=os.getenv('WANDB_API_KEY'))" 2>/dev/null; then
    echo "✓ WandB login successful!"
    echo ""
    echo "You can now use WandB in your scripts."
else
    echo "⚠ Could not automatically verify login, but API key has been saved."
    echo "Please run the initialization script to verify:"
    echo "  bash scripts/task_131_wandb_initialization.sh"
fi
