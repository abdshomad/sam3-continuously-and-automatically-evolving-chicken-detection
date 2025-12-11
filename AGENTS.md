# Agent Instructions

## Automated Task Execution Workflow

When the user types **"next"** or **"n"**, follow this workflow to process tasks from `docs/plan/plan.md`:

### Step 1: Parse and Identify Next Tasks

1. Read the file `docs/plan/plan.md`
2. Parse all markdown tables to find task rows
3. Identify tasks where:
   - Status column contains `\[ \] Pending` (escaped brackets with a space: `\[ \]`)
   - Implementation Date column is empty (appears as `|  |` in the table)
4. Sort tasks by Task ID (e.g., 1.1.1, 1.1.2, 1.1.3, etc.)
   - Note: Task IDs appear as `**1.1.1**` (bolded) in the markdown, but sort by the numeric value
5. Select the **next 3 consecutive pending tasks** in order

### Step 2: Execute Tasks

For each of the 3 selected tasks:

1. **Read the Task Details**: Extract the Task ID, Description, and Technical Details/Commands
2. **Execute the Task**: 
   - If the task contains commands (e.g., shell commands, code snippets), execute them appropriately
   - If the task requires manual steps or verification, perform those actions
   - If the task involves creating files or modifying code, do so
3. **Handle Errors**: 
   - If a task fails, mark it with status `\[x\] Failed` (preserve escaped brackets) and add the current date
   - Continue with the remaining tasks
   - Report any failures to the user

### Step 3: Update Task Status

After executing each task (successfully or with failure):

1. **Update Status**: 
   - Change `\[ \] Pending` to `\[x\] Done` for successful tasks (preserve escaped brackets)
   - Change `\[ \] Pending` to `\[x\] Failed` for failed tasks (preserve escaped brackets)
   - Preserve the exact spacing and formatting of the table

2. **Update Implementation Date**:
   - Set the Implementation Date column to the current date in **ISO format: YYYY-MM-DD**
   - Example: `2024-01-15`
   - Use the actual current date when updating

### Step 4: Commit and Push Changes

After updating all 3 tasks:

1. **Stage Changes**: 
   - Stage `docs/plan/plan.md` with `git add docs/plan/plan.md`
   - Stage any other files that were created or modified during task execution

2. **Create Commit Message**:
   - Format: `Complete tasks [Task IDs]: [Brief descriptions]`
   - Example: `Complete tasks 1.1.1, 1.1.2, 1.1.3: GPU check, CUDA verification, VRAM health check`
   - Include all 3 Task IDs and brief descriptions

3. **Commit**: 
   - Run `git commit -m "[commit message]"`

4. **Push**: 
   - Run `git push` to push changes to the remote repository

### Important Notes

- **Table Format Preservation**: When updating status and dates, maintain the exact markdown table structure with pipe separators (`|`)
- **Task Order**: Always process tasks in sequential order by Task ID
- **Partial Completion**: If less than 3 tasks remain, process all remaining pending tasks
- **No Tasks Available**: If no pending tasks are found, inform the user that all tasks are complete
- **Date Format**: Always use ISO format (YYYY-MM-DD) for dates
- **Error Handling**: Continue processing remaining tasks even if one fails, but clearly mark failed tasks

### Example Workflow

When user types "next":

```
1. Parse plan.md → Find tasks 1.1.1, 1.1.2, 1.1.3 (all pending)
2. Execute task 1.1.1: Run nvidia-smi, verify GPU
3. Execute task 1.1.2: Run nvcc --version, verify CUDA
4. Execute task 1.1.3: Check VRAM availability
5. Update plan.md:
   - 1.1.1: `\[ \] Pending` → `\[x\] Done`, date → `2024-01-15`
   - 1.1.2: `\[ \] Pending` → `\[x\] Done`, date → `2024-01-15`
   - 1.1.3: `\[ \] Pending` → `\[x\] Done`, date → `2024-01-15`
6. git add docs/plan/plan.md
7. git commit -m "Complete tasks 1.1.1, 1.1.2, 1.1.3: GPU check, CUDA verification, VRAM health check"
8. git push
```

