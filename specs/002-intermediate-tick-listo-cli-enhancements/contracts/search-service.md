# Search Service Contract

**Service**: SearchService
**Purpose**: Provide keyword-based search functionality for tasks
**Module**: `src/ticklisto/services/search_service.py`

## Interface

### search_tasks

Search tasks by keyword in title and description fields.

#### Signature

```python
def search_tasks(tasks: list[Task], keyword: str) -> list[Task]:
    """
    Search tasks by keyword (case-insensitive).

    Args:
        tasks: List of tasks to search
        keyword: Search keyword to match against title and description

    Returns:
        List of tasks matching the keyword

    Raises:
        TypeError: If tasks is not a list or keyword is not a string
    """
```

#### Input

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| tasks | list[Task] | Yes | Valid list of Task objects | Tasks to search |
| keyword | str | Yes | Non-None string | Search keyword (can be empty) |

#### Output

| Type | Description |
|------|-------------|
| list[Task] | Filtered list of tasks matching keyword |

**Behavior**:
- If keyword is empty string, returns all tasks (no filtering)
- Matching is case-insensitive
- Searches in both title and description fields
- Returns tasks where keyword appears anywhere in title OR description
- Preserves original task order
- Returns empty list if no matches found

#### Examples

```python
# Example 1: Basic search
tasks = [
    Task(id=1, title="Buy groceries", description="Milk and eggs"),
    Task(id=2, title="Write report", description="Q4 financial report"),
    Task(id=3, title="Call dentist", description="Schedule appointment")
]

result = search_tasks(tasks, "report")
# Returns: [Task(id=2, title="Write report", ...)]

# Example 2: Case-insensitive
result = search_tasks(tasks, "REPORT")
# Returns: [Task(id=2, title="Write report", ...)]

# Example 3: Empty keyword
result = search_tasks(tasks, "")
# Returns: all 3 tasks

# Example 4: No matches
result = search_tasks(tasks, "xyz")
# Returns: []

# Example 5: Search in description
result = search_tasks(tasks, "appointment")
# Returns: [Task(id=3, title="Call dentist", ...)]
```

#### Error Handling

| Error | Condition | Response |
|-------|-----------|----------|
| TypeError | tasks is not a list | Raise TypeError with message "tasks must be a list" |
| TypeError | keyword is not a string | Raise TypeError with message "keyword must be a string" |
| TypeError | tasks contains non-Task objects | Raise TypeError with message "All items in tasks must be Task objects" |

#### Performance

- **Time Complexity**: O(n) where n = number of tasks
- **Space Complexity**: O(m) where m = number of matching tasks
- **Target**: <100ms for 1000 tasks

#### Testing Requirements

**Unit Tests**:
1. Search with matching keyword in title
2. Search with matching keyword in description
3. Search with keyword matching multiple tasks
4. Search with no matches
5. Search with empty keyword (returns all)
6. Case-insensitive matching
7. Search with special characters
8. Error handling for invalid inputs

**Performance Tests**:
1. Search 1000 tasks completes in <100ms

---

**Contract Version**: 1.0
**Date**: 2026-02-01
**Status**: Approved
