# Storage Service Contract

**Service**: StorageService
**Purpose**: Provide JSON file persistence for tasks with atomic write operations
**Module**: `src/ticklisto/services/storage_service.py`

## Interface

### load_from_json

Load tasks from JSON file with error handling for corrupted files.

#### Signature

```python
def load_from_json(file_path: str = "ticklisto_data.json") -> dict:
    """
    Load tasks and metadata from JSON file.

    Args:
        file_path: Path to JSON file (default: ticklisto_data.json)

    Returns:
        Dictionary containing:
        - tasks: List of task dictionaries
        - next_id: Next available task ID (integer)

    Raises:
        FileNotFoundError: If file doesn't exist (returns empty structure)
        ValueError: If JSON is corrupted or invalid format
    """
```

#### Input

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| file_path | str | No | "ticklisto_data.json" | Valid file path | Path to JSON storage file |

#### Output

| Type | Description |
|------|-------------|
| dict | Dictionary with 'tasks' (list) and 'next_id' (int) keys |

**Behavior**:
- If file doesn't exist, returns `{"tasks": [], "next_id": 1}`
- If file exists but is empty, returns `{"tasks": [], "next_id": 1}`
- If JSON is corrupted, raises ValueError with helpful message
- Validates JSON structure has required keys
- Returns deep copy to prevent external modification

#### Examples

```python
# Example 1: Load from existing file
data = load_from_json("ticklisto_data.json")
# Returns: {"tasks": [...], "next_id": 5}

# Example 2: File doesn't exist (first run)
data = load_from_json("ticklisto_data.json")
# Returns: {"tasks": [], "next_id": 1}

# Example 3: Corrupted JSON
data = load_from_json("corrupted.json")
# Raises: ValueError("JSON file is corrupted: ...")
```

---

### save_to_json

Save tasks to JSON file with atomic write operation (temp file + rename).

#### Signature

```python
def save_to_json(data: dict, file_path: str = "ticklisto_data.json") -> None:
    """
    Save tasks and metadata to JSON file atomically.

    Args:
        data: Dictionary containing tasks and next_id
        file_path: Path to JSON file (default: ticklisto_data.json)

    Raises:
        ValueError: If data structure is invalid
        IOError: If write operation fails
    """
```

#### Input

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| data | dict | Yes | - | Must have 'tasks' and 'next_id' keys | Data to save |
| file_path | str | No | "ticklisto_data.json" | Valid file path | Path to JSON storage file |

#### Output

| Type | Description |
|------|-------------|
| None | No return value (raises exception on error) |

**Behavior**:
- Validates data structure before writing
- Writes to temporary file first (file_path + ".tmp")
- Uses atomic rename operation to replace original file
- Ensures data integrity (all-or-nothing write)
- Creates parent directories if they don't exist
- Uses JSON indent=2 for human readability

#### Atomic Write Process

```
1. Validate data structure
2. Write to ticklisto_data.json.tmp
3. Flush and sync to disk
4. Rename .tmp to ticklisto_data.json (atomic operation)
5. If any step fails, original file remains unchanged
```

#### Examples

```python
# Example 1: Save tasks
data = {
    "tasks": [
        {"id": 1, "title": "Task 1", "completed": False, ...},
        {"id": 2, "title": "Task 2", "completed": True, ...}
    ],
    "next_id": 3
}
save_to_json(data, "ticklisto_data.json")
# File saved atomically

# Example 2: Invalid data structure
data = {"tasks": []}  # Missing next_id
save_to_json(data)
# Raises: ValueError("Data must contain 'next_id' key")
```

---

## Error Handling

| Error | Condition | Response |
|-------|-----------|----------|
| FileNotFoundError | JSON file doesn't exist on load | Return empty structure (not an error) |
| ValueError | JSON is corrupted or invalid format | Raise with detailed error message |
| ValueError | Data structure missing required keys | Raise with validation error |
| IOError | Write operation fails | Raise with file system error details |
| PermissionError | No write permission | Raise with permission error |

## Data Structure

### JSON File Format

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Task title",
      "description": "Task description",
      "completed": false,
      "priority": "high",
      "categories": ["work", "urgent"],
      "due_date": "2026-02-15T00:00:00",
      "created_at": "2026-02-01T10:30:00",
      "updated_at": "2026-02-01T10:30:00"
    }
  ],
  "next_id": 2
}
```

### Validation Rules

- `tasks` must be a list
- `next_id` must be a positive integer
- Each task must have all required fields
- Dates stored as ISO 8601 strings

## Performance

- **Time Complexity**: O(n) where n = number of tasks
- **Space Complexity**: O(n) for in-memory representation
- **Target**: <100ms for 1000 tasks

## Testing Requirements

**Unit Tests**:
1. Load from non-existent file (returns empty structure)
2. Load from valid JSON file
3. Load from corrupted JSON file (raises ValueError)
4. Load from JSON with missing keys (raises ValueError)
5. Save valid data structure
6. Save with invalid data structure (raises ValueError)
7. Atomic write operation (verify temp file usage)
8. Error handling for write failures
9. Directory creation if parent doesn't exist

**Integration Tests**:
1. Save and load round-trip (data integrity)
2. Concurrent access handling
3. Large dataset (1000 tasks) performance

---

**Contract Version**: 1.0
**Date**: 2026-02-03
**Status**: Approved
