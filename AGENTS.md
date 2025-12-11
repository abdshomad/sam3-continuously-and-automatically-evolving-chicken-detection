# Agent Instructions

## Automated Task Script Creation Workflow

When the user types **"next"** or **"n"**, follow this workflow to process tasks from `docs/plan/plan.md`:

### Step 1: Parse and Identify Next Tasks

1. Read the file `docs/plan/plan.md`
2. Parse all markdown tables to find task rows
3. Identify tasks where:
   - Status column contains `[ ] Pending` (brackets with a space: `[ ]`)
   - Implementation Date column is empty (appears as `|  |` in the table)
4. Sort tasks by Task ID (e.g., 1.1.1, 1.1.2, 1.1.3, etc.)
   - Note: Task IDs appear as `**1.1.1**` (bolded) in the markdown, but sort by the numeric value
5. Select the **next 3 consecutive pending tasks** in order

### Step 2: Create Scripts for Tasks

For each of the 3 selected tasks:

1. **Read the Task Details**: Extract the Task ID, Description, and Technical Details/Commands
2. **Create Script File**: 
   - Determine the appropriate script type (Python or Shell) based on the task content:
     - Use **Python** (.py) for tasks involving data processing, API calls, file operations with logic, or when Python libraries are mentioned
     - Use **Shell** (.sh) for tasks involving system commands, environment setup, package installation, or simple command sequences
   - Create script file in the `scripts/` directory with naming format: `task_{TaskID}_{TaskName}.py` or `task_{TaskID}_{TaskName}.sh`
     - Sanitize Task ID for filename (remove dots and underscores, keep only numbers): `1.1.1` → `111`
     - Sanitize Task Name for filename: convert to lowercase, replace spaces with underscores, remove special characters (keep only alphanumeric and underscores)
     - Example: Task ID `1.1.1` with Description "GPU Availability Check" → `task_111_gpu_availability_check.sh`
     - Example: Task ID `1.2.3` with Description "Verify Logging Integration" → `task_123_verify_logging_integration.py`
3. **Write Script Content**:
   - Include shebang line (`#!/bin/bash` for shell, `#!/usr/bin/env python3` for Python)
   - Add a header comment with Task ID, Description, and Implementation Date
   - Convert Technical Details/Commands into executable script code:
     - For shell scripts: Write commands as-is, add error handling (`set -e` for exit on error)
     - For Python scripts: Write Python code that executes the equivalent operations
   - Add output/logging to indicate task progress and completion
   - Make the script executable (for shell scripts, add `chmod +x`)
4. **Script Structure**:
   - Shell scripts should include: `set -e` (exit on error), proper error messages, and status output
   - Python scripts should include: `if __name__ == "__main__"`, try-except error handling, and informative print statements

5. **Test and Fix Script**:
   - **CRITICAL**: After creating each script, immediately test it to ensure it works correctly
   - For shell scripts: Run the script using `bash scripts/task_{TaskID}_{TaskName}.sh` or make it executable and run directly
   - For Python scripts: Run the script using `python3 scripts/task_{TaskID}_{TaskName}.py`
   - Check for errors, missing dependencies, import issues, syntax errors, or logical problems
   - If the script fails:
     - Analyze the error output
     - Fix the issue in the script
     - Re-test the script
     - Repeat this process until the script executes successfully without errors
   - Only proceed to update task status after the script has been successfully tested and verified to work
   - If testing reveals that the script cannot be fixed (e.g., missing system dependencies that cannot be installed), mark the task as failed with appropriate notes

### Step 3: Update Task Status

After creating the script for each task:

1. **Update Status**: 
   - Change `[ ] Pending` to `[x] Script Created` only for scripts that have been successfully created AND tested
   - Change `[ ] Pending` to `[x] Failed` if script creation or testing fails after all reasonable attempts to fix it
   - Preserve the exact spacing and formatting of the table

2. **Update Implementation Date**:
   - Set the Implementation Date column to the current date in **ISO format: YYYY-MM-DD**
   - Example: `2024-01-15`
   - Use the actual current date when updating

3. **Add Script Reference**:
   - Optionally, add a note in the Technical Details column or create a mapping document that links Task IDs to their corresponding script files

### Step 4: Commit and Push Changes

After updating all 3 tasks:

1. **Stage Changes**: 
   - Stage `docs/plan/plan.md` with `git add docs/plan/plan.md`
   - Stage all created and tested script files: `git add scripts/task_*.py scripts/task_*.sh`
   - Stage any other files that were created or modified during script creation and testing

2. **Create Commit Message**:
   - Format: `Create scripts for tasks [Task IDs]: [Brief descriptions]`
   - Example: `Create scripts for tasks 1.1.1, 1.1.2, 1.1.3: GPU check, CUDA verification, VRAM health check`
   - Include all 3 Task IDs and brief descriptions

3. **Commit**: 
   - Run `git commit -m "[commit message]"`

4. **Push**: 
   - Run `git push` to push changes to the remote repository

### Configuration and Secrets Management

**CRITICAL**: All scripts must follow these configuration management rules:

1. **Settings and Configuration (`config.py`)**:
   - Store all non-sensitive settings, configuration values, and parameters in `config.py` at the project root
   - Examples: project names, default paths, timeout values, feature flags, model parameters, etc.
   - Use Python variables/constants in `config.py` for easy import
   - Example structure:
     ```python
     # config.py
     WANDB_PROJECT_NAME = "chicken-detection"
     DEFAULT_BATCH_SIZE = 32
     MODEL_CHECKPOINT_PATH = "./checkpoints"
     LOG_LEVEL = "INFO"
     ```

2. **Secrets and Credentials (`.env` file)**:
   - Store all sensitive information in `.env` file at the project root
   - Examples: API keys, passwords, tokens, database credentials, secret keys, etc.
   - Use `python-dotenv` library to load environment variables from `.env`
   - Access secrets using `os.getenv('VARIABLE_NAME')` after loading `.env`
   - Example structure:
     ```
     # .env
     WANDB_API_KEY=your_api_key_here
     DATABASE_PASSWORD=your_password_here
     SECRET_TOKEN=your_token_here
     ```

3. **Implementation Requirements**:
   - Python scripts must import from `config.py`: `import config`
   - Python scripts must load `.env` using: `load_dotenv(Path(__file__).parent.parent / '.env')`
   - Never hardcode configuration values or secrets directly in script files
   - Ensure `.env` is in `.gitignore` to prevent committing secrets
   - Shell scripts can source `.env` using: `source .env` or `set -a; source .env; set +a`

4. **File Locations**:
   - `config.py` should be at the project root: `/project_root/config.py`
   - `.env` should be at the project root: `/project_root/.env`
   - Scripts should reference these files relative to their location or use absolute paths from project root

### Important Notes

- **Script Directory**: Ensure the `scripts/` directory exists before creating scripts. Create it if it doesn't exist.
- **Table Format Preservation**: When updating status and dates, maintain the exact markdown table structure with pipe separators (`|`)
- **Task Order**: Always process tasks in sequential order by Task ID
- **Partial Completion**: If less than 3 tasks remain, process all remaining pending tasks
- **No Tasks Available**: If no pending tasks are found, inform the user that all tasks are complete
- **Date Format**: Always use ISO format (YYYY-MM-DD) for dates
- **Error Handling**: Continue processing remaining tasks even if script creation or testing fails for one, but clearly mark failed tasks
- **Script Type Selection**: Choose Python for complex logic, data processing, or when Python libraries are needed. Choose Shell for simple command sequences, system setup, or package installation.
- **Script Quality**: Ensure scripts are well-commented, handle errors gracefully, and provide clear output indicating their progress and completion status.
- **Testing Requirement**: **MANDATORY** - Every script must be tested immediately after creation. Fix all issues found during testing before marking the task as complete. Do not proceed to the next task until the current script has been successfully tested and verified to work.
- **Task Name in Filename**: Always include the sanitized task name in the script filename to make it easier to identify scripts by their purpose.
- **Configuration Management**: 
  - **Settings/Configs**: Always store any settings, configuration values, or non-sensitive parameters in `config.py` at the project root
  - **Secrets**: Always store any secrets, API keys, passwords, tokens, or sensitive credentials in `.env` file at the project root
  - Python scripts should import from `config.py` for settings and use `python-dotenv` to load secrets from `.env`
  - Never hardcode configuration values or secrets directly in scripts
  - Ensure `.env` is listed in `.gitignore` to prevent committing secrets to version control

### Example Workflow

When user types "next":

```
1. Parse plan.md → Find tasks 1.1.1, 1.1.2, 1.1.3 (all pending)
2. Create scripts/ directory if it doesn't exist
3. Create script for task 1.1.1:
   - Extract Task ID: 1.1.1, Description: "GPU Availability Check"
   - Create scripts/task_111_gpu_availability_check.sh (shell script)
   - Content: nvidia-smi command with error handling and verification logic
   - Test script: Run `bash scripts/task_111_gpu_availability_check.sh`
   - Fix any issues found during testing, re-test until successful
4. Create script for task 1.1.2:
   - Extract Task ID: 1.1.2, Description: "CUDA Version Verification"
   - Create scripts/task_112_cuda_version_verification.sh (shell script)
   - Content: nvcc --version command with CUDA version verification
   - Test script: Run `bash scripts/task_112_cuda_version_verification.sh`
   - Fix any issues found during testing, re-test until successful
5. Create script for task 1.1.3:
   - Extract Task ID: 1.1.3, Description: "VRAM Health Check"
   - Create scripts/task_113_vram_health_check.sh (shell script)
   - Content: VRAM availability check using nvidia-smi
   - Test script: Run `bash scripts/task_113_vram_health_check.sh`
   - Fix any issues found during testing, re-test until successful
6. Update plan.md:
   - 1.1.1: `[ ] Pending` → `[x] Script Created`, date → `2024-01-15`
   - 1.1.2: `[ ] Pending` → `[x] Script Created`, date → `2024-01-15`
   - 1.1.3: `[ ] Pending` → `[x] Script Created`, date → `2024-01-15`
7. git add docs/plan/plan.md scripts/task_*.sh scripts/task_*.py
8. git commit -m "Create scripts for tasks 1.1.1, 1.1.2, 1.1.3: GPU check, CUDA verification, VRAM health check"
9. git push
```

### Script Examples

**Example Shell Script (task_111_gpu_availability_check.sh):**
```bash
#!/bin/bash
# Task ID: 1.1.1
# Description: GPU Availability Check
# Created: 2024-01-15

set -e

echo "Checking GPU availability..."

if ! command -v nvidia-smi &> /dev/null; then
    echo "Error: nvidia-smi not found. NVIDIA drivers may not be installed."
    exit 1
fi

nvidia-smi

echo "GPU check completed successfully."
```

**Example Python Script (task_134_verify_logging_integration.py):**
```python
#!/usr/bin/env python3
"""
Task ID: 1.3.4
Description: Verify Logging Integration
Created: 2024-01-15
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Import configuration from config.py
try:
    import config
except ImportError:
    print("Error: config.py not found. Please create config.py with required settings.", file=sys.stderr)
    sys.exit(1)

def main():
    try:
        import wandb
        
        # Use settings from config.py
        project_name = config.WANDB_PROJECT_NAME
        print(f"Initializing WandB for project: {project_name}")
        
        # Use secrets from .env file
        wandb_api_key = os.getenv('WANDB_API_KEY')
        if not wandb_api_key:
            print("Error: WANDB_API_KEY not found in .env file", file=sys.stderr)
            return 1
        
        # Initialize wandb with API key from .env
        wandb.login(key=wandb_api_key)
        print("Successfully imported and configured wandb")
        
        # Add verification logic here
        print("WandB logging integration verified.")
        return 0
    except ImportError as e:
        print(f"Error: Failed to import wandb: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

