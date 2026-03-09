# ID Manager Contract

**Service**: IDManager
**Purpose**: Manage auto-incrementing task IDs with persistence and reset capability
**Module**: `src/ticklisto/services/id_manager.py`

## Interface

### generate_id

Generate the next unique task ID and increment the counter.

#### Signature

```python
def generate_id(self) -> int:
    """
    Generate next unique task ID and increment counter.

    Returns:
        Next available task ID (positive integer)

    Raises:
        RuntimeError: If ID counter reaches maximum value
    """
```

#### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| None | - | - | Uses internal counter state |

#### Output

| Type | Description |
|------|-------------|
| int | Next unique task ID (1, 2, 3, ...) |

**Behavior**:
- Returns current counter value
- Increments counter by 1
- Counter persists across method calls
- IDs are never reused during normal operation
- Thread-safe (if needed for future enhancements)

#### Examples

```python
# Example 1: First ID generation
id_manager = IDManager()
task_id = id_manager.generate_id()
# Returns: 1

# Example 2: Subsequent IDs
task_id = id_manager.generate_id()
# Returns: 2
task_id = id_manager.generate_id()
# Returns: 3
```

---

### get_current_counter

Get the current ID counter value without incrementing.

#### Signature

```python
def get_current_counter(self) -> int:
    """
    Get current ID counter value without incrementing.

    Returns:
        Current counter value (next ID to be generated)
    """
```

#### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| None | - | - | Uses internal counter state |

#### Output

| Type | Description |
|------|-------------|
| int | Current counter value |

**Behavior**:
- Returns current counter without side effects
- Does not increment counter
- Useful for persistence and debugging

#### Examples

```python
# Example: Check current counter
id_manager = IDManager()
id_manager.generate_id()  # Returns 1
id_manager.generate_id()  # Returns 2
current = id_manager.get_current_counter()
# Returns: 3 (next ID to be generated)
```

---

### set_counter

Set the ID counter to a specific value (used for loading persisted state).

#### Signature

```python
def set_counter(self, value: int) -> None:
    """
    Set ID counter to specific value.

    Args:
        value: Counter value to set (must be positive integer)

    Raises:
        ValueError: If value is not a positive integer
    """
```

#### Input

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| value | int | Yes | Must be >= 1 | Counter value to set |

#### Output

| Type | Description |
|------|-------------|
| None | No return value (raises exception on error) |

**Behavior**:
- Sets internal counter to specified value
- Validates value is positive integer
- Used when loading persisted counter from storage
- Does not affect previously generated IDs

#### Examples

```python
# Example 1: Load persisted counter
id_manager = IDManager()
id_manager.set_counter(10)
next_id = id_manager.generate_id()
# Returns: 10

# Example 2: Invalid value
id_manager.set_counter(0)
# Raises: ValueError("Counter must be a positive integer")
```

---

### reset_counter

Reset the ID counter to 1 (used after "delete all" operation).

#### Signature

```python
def reset_counter(self) -> None:
    """
    Reset ID counter to 1.

    Used after "delete all" operation to start fresh numbering.
    """
```

#### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| None | - | - | Resets to initial state |

#### Output

| Type | Description |
|------|-------------|
| None | No return value |

**Behavior**:
- Sets counter to 1
- Next generated ID will be 1
- Only called after "delete all" operation
- Provides fresh start for new task numbering

#### Examples

```python
# Example: Reset after delete all
id_manager = IDManager()
id_manager.generate_id()  # Returns 1
id_manager.generate_id()  # Returns 2
id_manager.reset_counter()
id_manager.generate_id()  # Returns 1 (fresh start)
```

---

## ID Management Rules

### Normal Operation

1. **Never Reuse IDs**: During normal operation, IDs are never reused
2. **Sequential**: IDs increment sequentially (1, 2, 3, ...)
3. **Persistent**: Counter persists across application restarts
4. **Unique**: Each task gets a unique ID

### After Delete All

1. **Counter Reset**: Counter resets to 1
2. **Fresh Start**: New tasks start from ID 1 again
3. **No Conflict**: Old IDs are gone, so no conflict with new IDs

### Example Scenario

```
# Session 1
create task → ID 1
create task → ID 2
delete task 1
create task → ID 3 (ID 1 NOT reused)

# Application restart
create task → ID 4 (counter persisted)

# Delete all operation
delete all tasks → counter resets to 1
create task → ID 1 (fresh start)
```

## Error Handling

| Error | Condition | Response |
|-------|-----------|----------|
| ValueError | set_counter with value < 1 | Raise with validation error |
| RuntimeError | Counter reaches max int value | Raise with overflow error |
| TypeError | set_counter with non-integer | Raise with type error |

## Integration with Storage

The IDManager works with StorageService:

```python
# Load counter from storage
data = storage_service.load_from_json()
id_manager.set_counter(data["next_id"])

# Save counter to storage
data = {
    "tasks": [...],
    "next_id": id_manager.get_current_counter()
}
storage_service.save_to_json(data)
```

## Performance

- **Time Complexity**: O(1) for all operations
- **Space Complexity**: O(1) (single integer counter)
- **Target**: <1ms per operation

## Testing Requirements

**Unit Tests**:
1. Generate first ID (returns 1)
2. Generate sequential IDs (1, 2, 3, ...)
3. Get current counter without incrementing
4. Set counter to specific value
5. Set counter with invalid value (raises ValueError)
6. Reset counter to 1
7. Generate ID after reset (returns 1)
8. Counter persistence across instances

**Integration Tests**:
1. ID generation with storage persistence
2. Counter reset after delete all
3. Load counter from storage on startup

---

**Contract Version**: 1.0
**Date**: 2026-02-03
**Status**: Approved
