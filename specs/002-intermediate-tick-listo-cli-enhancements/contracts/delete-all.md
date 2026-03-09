# Delete All Contract

**Feature**: Delete All Tasks
**Purpose**: Provide bulk deletion of all tasks with confirmation prompt and ID counter reset
**Module**: `src/ticklisto/cli/commands.py` (command handler)

## Interface

### delete_all_tasks

Delete all tasks from storage with confirmation prompt and ID counter reset.

#### Signature

```python
def delete_all_tasks(task_manager: TaskManager, id_manager: IDManager) -> bool:
    """
    Delete all tasks with user confirmation.

    Args:
        task_manager: TaskManager instance
        id_manager: IDManager instance for counter reset

    Returns:
        True if tasks were deleted, False if cancelled or no tasks exist

    Raises:
        RuntimeError: If deletion operation fails
    """
```

#### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_manager | TaskManager | Yes | Task manager instance |
| id_manager | IDManager | Yes | ID manager instance |

#### Output

| Type | Description |
|------|-------------|
| bool | True if deleted, False if cancelled or no tasks |

**Behavior**:
1. Check if any tasks exist
2. If no tasks, display message and return False
3. If tasks exist, prompt for confirmation
4. If user confirms, delete all tasks and reset ID counter
5. If user cancels, return False without changes
6. Display success message after deletion

#### Workflow

```
1. Check task count
   ├─ If 0 tasks → Display "No tasks to delete" → Return False
   └─ If tasks exist → Continue to step 2

2. Display confirmation prompt
   "Are you sure you want to delete ALL tasks? This cannot be undone. (yes/no)"

3. Wait for user input
   ├─ If "yes" or "y" (case-insensitive) → Continue to step 4
   └─ If "no" or "n" or anything else → Display "Cancelled" → Return False

4. Delete all tasks
   - Call task_manager.delete_all()
   - Call id_manager.reset_counter()
   - Save to storage

5. Display success message
   "All tasks deleted successfully. ID counter reset to 1."

6. Return True
```

#### Examples

```python
# Example 1: Delete all with confirmation
result = delete_all_tasks(task_manager, id_manager)
# Prompts: "Are you sure you want to delete ALL tasks? (yes/no)"
# User enters: "yes"
# Output: "All tasks deleted successfully. ID counter reset to 1."
# Returns: True

# Example 2: User cancels
result = delete_all_tasks(task_manager, id_manager)
# Prompts: "Are you sure you want to delete ALL tasks? (yes/no)"
# User enters: "no"
# Output: "Delete all cancelled."
# Returns: False

# Example 3: No tasks exist
result = delete_all_tasks(task_manager, id_manager)
# Output: "No tasks to delete."
# Returns: False
```

---

## CLI Command Integration

### Command Names

- Primary: `delete all`
- Alias: `dela`

### Command Handler

```python
def handle_delete_all_command():
    """Handle delete all / dela command."""
    result = delete_all_tasks(task_manager, id_manager)
    if result:
        console.print("[green]✓ All tasks deleted successfully[/green]")
        console.print("[yellow]ID counter reset to 1[/yellow]")
```

---

## Confirmation Prompt

### Prompt Text

```
⚠️  WARNING: Delete All Tasks

This will permanently delete ALL tasks and reset the ID counter to 1.
This action cannot be undone.

Are you sure you want to continue? (yes/no):
```

### Accepted Responses

**Confirmation (proceed with deletion)**:
- `yes` (case-insensitive)
- `y` (case-insensitive)

**Cancellation (abort deletion)**:
- `no` (case-insensitive)
- `n` (case-insensitive)
- Any other input
- Empty input (just pressing Enter)

### Rich Prompt Implementation

```python
from rich.prompt import Confirm

def confirm_delete_all() -> bool:
    """Prompt user to confirm delete all operation."""
    console.print("\n[bold red]⚠️  WARNING: Delete All Tasks[/bold red]")
    console.print("This will permanently delete ALL tasks and reset the ID counter to 1.")
    console.print("This action cannot be undone.\n")

    return Confirm.ask("Are you sure you want to continue?", default=False)
```

---

## ID Counter Reset

After successful deletion:

1. **Reset counter to 1**: `id_manager.reset_counter()`
2. **Next task gets ID 1**: Fresh start for new tasks
3. **No conflict**: Old tasks are gone, so no ID conflicts

### Example Scenario

```
# Before delete all
Tasks: [ID 1, ID 2, ID 3]
Next ID: 4

# User runs "delete all" and confirms
Tasks: []
Next ID: 1 (reset)

# User creates new task
Tasks: [ID 1]
Next ID: 2
```

---

## Error Handling

| Error | Condition | Response |
|-------|-----------|----------|
| RuntimeError | Task deletion fails | Display error, don't reset counter |
| RuntimeError | Counter reset fails | Display error, tasks already deleted |
| IOError | Storage save fails | Display error, data may be inconsistent |

### Error Recovery

If deletion succeeds but counter reset fails:
- Tasks are deleted (cannot be undone)
- Counter remains at old value
- Display warning to user
- Suggest manual counter reset or restart

---

## Testing Requirements

**Unit Tests**:
1. Delete all with confirmation (yes)
2. Delete all cancelled (no)
3. Delete all with no tasks (returns False)
4. ID counter reset after deletion
5. Confirmation prompt with various inputs (yes/y/no/n/empty)

**Integration Tests**:
1. Delete all command in CLI
2. Dela alias in CLI
3. Verify tasks deleted from storage
4. Verify ID counter reset in storage
5. Create new task after delete all (gets ID 1)

**Manual Testing**:
1. Run "delete all" with tasks, confirm
2. Run "delete all" with tasks, cancel
3. Run "delete all" with no tasks
4. Run "dela" alias
5. Verify no scroll-back after confirmation

---

## User Experience

### Success Flow

```
> delete all

⚠️  WARNING: Delete All Tasks

This will permanently delete ALL tasks and reset the ID counter to 1.
This action cannot be undone.

Are you sure you want to continue? (yes/no): yes

✓ All tasks deleted successfully
ID counter reset to 1
```

### Cancellation Flow

```
> delete all

⚠️  WARNING: Delete All Tasks

This will permanently delete ALL tasks and reset the ID counter to 1.
This action cannot be undone.

Are you sure you want to continue? (yes/no): no

Delete all cancelled. No changes made.
```

### No Tasks Flow

```
> delete all

No tasks to delete.
```

---

**Contract Version**: 1.0
**Date**: 2026-02-03
**Status**: Approved
