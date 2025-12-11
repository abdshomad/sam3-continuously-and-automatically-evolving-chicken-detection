#!/usr/bin/env python3
"""
Task ID: 1.2.5
Description: Download Pre-trained Weights
Created: 2025-12-12
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv is optional

# Import configuration from config.py
try:
    import config
except ImportError:
    print("Error: config.py not found. Please create config.py with required settings.", file=sys.stderr)
    sys.exit(1)

def main():
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("Error: huggingface_hub not found. Please install it first:", file=sys.stderr)
        print("  uv pip install huggingface_hub", file=sys.stderr)
        return 1
    
    # Get checkpoint path from config
    checkpoint_dir = Path(config.DEFAULT_CHECKPOINT_PATH)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # SAM 3 checkpoint information
    SAM3_MODEL_ID = "facebook/sam3"
    SAM3_CKPT_NAME = "sam3.pt"
    SAM3_CFG_NAME = "config.json"
    
    checkpoint_path = checkpoint_dir / SAM3_CKPT_NAME
    config_path = checkpoint_dir / SAM3_CFG_NAME
    
    print("=" * 50)
    print("Task 1.2.5: Download Pre-trained Weights")
    print("=" * 50)
    print("")
    print(f"Checkpoint directory: {checkpoint_dir.absolute()}")
    print(f"Model repository: {SAM3_MODEL_ID}")
    print("")
    
    # Check if checkpoint already exists
    if checkpoint_path.exists():
        print(f"✓ Checkpoint already exists: {checkpoint_path}")
        print(f"  Size: {checkpoint_path.stat().st_size / (1024**3):.2f} GB")
        print("")
        print("To re-download, delete the existing checkpoint first:")
        print(f"  rm {checkpoint_path}")
        return 0
    
    # Check if user is authenticated with Hugging Face
    hf_token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_HUB_TOKEN')
    if not hf_token:
        print("⚠ WARNING: No Hugging Face token found in environment variables.")
        print("  You may need to authenticate to download the checkpoint.")
        print("")
        print("To authenticate:")
        print("  1. Get an access token from: https://huggingface.co/settings/tokens")
        print("  2. Request access to: https://huggingface.co/facebook/sam3")
        print("  3. Run: huggingface-cli login")
        print("     Or set HF_TOKEN or HUGGINGFACE_HUB_TOKEN environment variable")
        print("")
        # Check if running in interactive mode
        if sys.stdin.isatty():
            try:
                response = input("Continue anyway? (y/n): ").strip().lower()
                if response != 'y':
                    print("Download cancelled.")
                    return 1
            except (EOFError, KeyboardInterrupt):
                print("\nDownload cancelled.")
                return 1
        else:
            print("Non-interactive mode: Attempting download without token...")
            print("  (This may fail if authentication is required)")
            print("")
    
    # Download checkpoint
    print("Downloading SAM 3 checkpoint...")
    print("  This may take several minutes depending on your connection speed.")
    print("")
    
    try:
        downloaded_path = hf_hub_download(
            repo_id=SAM3_MODEL_ID,
            filename=SAM3_CKPT_NAME,
            local_dir=str(checkpoint_dir),
            token=hf_token
        )
        print(f"✓ Checkpoint downloaded: {downloaded_path}")
        
        # Verify file exists and has reasonable size
        if Path(downloaded_path).exists():
            file_size = Path(downloaded_path).stat().st_size / (1024**3)
            print(f"  Size: {file_size:.2f} GB")
            if file_size < 0.1:  # Less than 100MB seems suspicious
                print("  ⚠ WARNING: File size seems unusually small. Download may have failed.")
                return 1
        else:
            print("  ⚠ WARNING: Downloaded file not found at expected location")
            return 1
        
    except Exception as e:
        print(f"ERROR: Failed to download checkpoint: {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Possible issues:", file=sys.stderr)
        print("  1. Not authenticated with Hugging Face", file=sys.stderr)
        print("  2. Access not granted to facebook/sam3 repository", file=sys.stderr)
        print("  3. Network connectivity issues", file=sys.stderr)
        print("", file=sys.stderr)
        print("To fix:", file=sys.stderr)
        print("  1. Request access: https://huggingface.co/facebook/sam3", file=sys.stderr)
        print("  2. Authenticate: huggingface-cli login", file=sys.stderr)
        return 1
    
    # Download config file (optional but useful)
    print("")
    print("Downloading config file...")
    try:
        config_downloaded = hf_hub_download(
            repo_id=SAM3_MODEL_ID,
            filename=SAM3_CFG_NAME,
            local_dir=str(checkpoint_dir),
            token=hf_token
        )
        print(f"✓ Config downloaded: {config_downloaded}")
    except Exception as e:
        print(f"⚠ WARNING: Failed to download config file: {e}")
        print("  This is optional and the checkpoint should still work.")
    
    print("")
    print("=" * 50)
    print("✓ Download Pre-trained Weights: COMPLETED")
    print("=" * 50)
    print("")
    print(f"Checkpoint location: {checkpoint_path.absolute()}")
    print("")
    print("Next steps:")
    print("  - Proceed to Phase 1.3: WandB & DVC Configuration")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
