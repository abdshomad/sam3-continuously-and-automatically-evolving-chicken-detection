#!/usr/bin/env python3
"""
Task ID: 1.3.4
Description: Verify Logging Integration
Created: 2025-01-27

This script verifies that wandb can be imported and can reach the dashboard servers
from the training node. It tests the connection by initializing a test run.
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
    print("=" * 50)
    print("Task 1.3.4: Verify Logging Integration")
    print("=" * 50)
    print("")
    
    # Check if wandb is installed
    try:
        import wandb
        wandb_version = getattr(wandb, '__version__', 'installed')
        print(f"✓ wandb is installed (version: {wandb_version})")
        print("")
    except ImportError:
        print("ERROR: wandb is not installed", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please install dependencies:", file=sys.stderr)
        print("  uv sync", file=sys.stderr)
        print("", file=sys.stderr)
        print("This will install wandb from pyproject.toml", file=sys.stderr)
        return 1
    
    # Get project name from config
    project_name = getattr(config, 'WANDB_PROJECT_NAME', 'chicken-detection')
    print(f"WandB project name: {project_name}")
    print("")
    
    # Check for API key in environment
    wandb_api_key = os.getenv('WANDB_API_KEY')
    
    if not wandb_api_key:
        print("WARNING: WANDB_API_KEY not found in environment variables", file=sys.stderr)
        print("", file=sys.stderr)
        print("The script will attempt to use existing wandb login credentials.", file=sys.stderr)
        print("If this fails, please:", file=sys.stderr)
        print("  1. Get your API key from: https://wandb.ai/authorize", file=sys.stderr)
        print("  2. Add to .env file: WANDB_API_KEY=your_api_key_here", file=sys.stderr)
        print("  3. Or run: wandb login", file=sys.stderr)
        print("")
    
    # Test wandb connection by initializing a test run
    print("Testing WandB connection to dashboard servers...")
    print("")
    
    try:
        # Initialize wandb in offline mode first to test import
        # Then try to sync to test connection
        test_run = wandb.init(
            project=project_name,
            name="connection_test",
            mode="online",  # Try online mode to test connection
            tags=["test", "connection-verification"],
            config={
                "test": True,
                "task": "1.3.4",
                "description": "Verify logging integration"
            }
        )
        
        # Log a test metric to verify connection works
        wandb.log({"connection_test": 1.0})
        
        # Finish the run
        wandb.finish()
        
        print("✓ Successfully connected to WandB dashboard servers")
        print("✓ Test run created and logged")
        print("")
        print("Verification details:")
        print(f"  - Project: {project_name}")
        print("  - Connection: Online")
        print("  - Status: Active")
        print("")
        
    except wandb.errors.AuthenticationError as e:
        print("ERROR: WandB authentication failed", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please ensure you are logged in:", file=sys.stderr)
        print("  1. Set WANDB_API_KEY in .env file", file=sys.stderr)
        print("  2. Or run: wandb login", file=sys.stderr)
        return 1
        
    except wandb.errors.CommError as e:
        print("ERROR: Cannot reach WandB dashboard servers", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Possible causes:", file=sys.stderr)
        print("  - Network connectivity issues", file=sys.stderr)
        print("  - Firewall blocking connection", file=sys.stderr)
        print("  - WandB servers are down", file=sys.stderr)
        print("", file=sys.stderr)
        print("You can try offline mode for testing:", file=sys.stderr)
        print("  wandb.init(mode='offline')", file=sys.stderr)
        return 1
        
    except Exception as e:
        print(f"ERROR: Unexpected error while testing WandB connection: {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please check:", file=sys.stderr)
        print("  1. WandB is properly installed: pip show wandb", file=sys.stderr)
        print("  2. You have network access", file=sys.stderr)
        print("  3. WandB API is accessible", file=sys.stderr)
        return 1
    
    # Additional verification: Test API access
    print("Verifying WandB API access...")
    try:
        api = wandb.Api()
        # Try to access the project
        try:
            project = api.project(project_name)
            print(f"✓ Successfully accessed project: {project_name}")
        except Exception:
            # Project might not exist yet, which is okay
            print(f"⚠ Project '{project_name}' does not exist yet (this is normal for new projects)")
            print("  The project will be created automatically on first run")
        
        print("")
        
    except Exception as e:
        print(f"⚠ WARNING: Could not verify API access: {e}")
        print("  This may be normal if you haven't created any runs yet")
        print("")
    
    print("=" * 50)
    print("✓ Logging Integration Verification: COMPLETED")
    print("=" * 50)
    print("")
    print("WandB is properly configured and can reach the dashboard servers.")
    print("The logging integration is ready for use in training scripts.")
    print("")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
