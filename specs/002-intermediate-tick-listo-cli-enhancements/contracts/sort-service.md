# Sort Service Contract

**Service**: SortService
**Purpose**: Provide multi-level sorting for tasks
**Module**: `src/ticklisto/services/sort_service.py`

## Interface

### sort_tasks

Sort tasks by specified criteria with multi-level sorting support.

#### Signature

```python
def sort_tasks(tasks: list[Task], sort_by: str = "due_date") -> list[Task]:
    """
    Sort tasks by specified criteria.

    Args:
        tasks: List of tasks to sort
        sort_by: Sort criteria ("due_date", "priority", "alphabetical")

    Returns:
        New sorted list of tasks

    Raises:
        ValueError: If invalid sort_by parameter provided
    """
```

#### Input

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| tasks | list[Task] | Yes | - | Valid list | Tasks to sort |
| sort_by | str | No | "due_date" | "due_date", "priority", "alphabetical" | Sort criteria |

#### Output

| Type | Description |
|------|-------------|
| list[Task] | New sorted list (original list unchanged) |

**Behavior**:
- Returns a new list (does not modify original)
- Empty list returns empty list
- Single task returns list with that task

#### Sort Criteria

##### 1. Sort by Due Date (default)

**Primary Sort**: Due date (earliest first)
**Secondary Sort**: Priority (high → medium → low)

**Special Handling**: Tasks without due dates are grouped separately at the end in a "No Due Date" section.

```python
# Sorting logic
tasks_with_dates = [t for t in tasks if t.due_date]
tasks_without_dates = [t for t in tasks if not t.due_date]

# Sort tasks with dates by: (due_date, priority)
sorted_with_dates = sorted(
    tasks_with_dates,
    key=lambda t: (t.due_date, priority_order[t.priority])
)

# Return: tasks with dates + tasks without dates
return sorted_with_dates + tasks_without_dates
```

##### 2. Sort by Priority

**Sort Order**: High → Medium → Low

```python
priority_order = {"high": 0, "medium": 1, "low": 2}
sorted_tasks = sorted(tasks, key=lambda t: priority_order[t.priority])
```

##### 3. Sort Alphabetically

**Sort Order**: A → Z (case-insensitive by title)

```python
sorted_tasks = sorted(tasks, key=lambda t: t.title.lower())
```

#### Examples

```python
from datetime import datetime

# Example 1: Sort by due date (default)
tasks = [
    Task(id=1, title="Task 1", due_date=datetime(2026, 2, 15), priority=Priority.LOW),
    Task(id=2, title="Task 2", due_date=datetime(2026, 1, 15), priority=Priority.HIGH),
    Task(id=3, title="Task 3", due_date=datetime(2026, 1, 15), priority=Priority.MEDIUM),
    Task(id=4, title="Task 4", due_date=None, priority=Priority.HIGH),
]

result = sort_tasks(tasks, "due_date")
# Returns order: Task 2 (Jan 15, high), Task 3 (Jan 15, medium), Task 1 (Feb 15, low), Task 4 (no date)

# Example 2: Sort by priority
tasks = [
    Task(id=1, title="Task 1", priority=Priority.LOW),
    Task(id=2, title="Task 2", priority=Priority.HIGH),
    Task(id=3, title="Task 3", priority=Priority.MEDIUM),
]

result = sort_tasks(tasks, "priority")
# Returns order: Task 2 (high), Task 3 (medium), Task 1 (low)

# Example 3: Sort alphabetically
tasks = [
    Task(id=1, title="Zebra"),
    Task(id=2, title="Apple"),
    Task(id=3, title="banana"),
]

result = sort_tasks(tasks, "alphabetical")
# Returns order: Task 2 (Apple), Task 3 (banana), Task 1 (Zebra)

# Example 4: Empty list
result = sort_tasks([], "due_date")
# Returns: []

# Example 5: Single task
result = sort_tasks([Task(id=1, title="Task 1")], "priority")
# Returns: [Task(id=1, ...)]
```

#### Multi-Level Sorting Details

When sorting by due date, tasks with the same due date are sub-sorted by priority:

```python
tasks = [
    Task(id=1, due_date=datetime(2026, 1, 15), priority=Priority.LOW),
    Task(id=2, due_date=datetime(2026, 1, 15), priority=Priority.HIGH),
    Task(id=3, due_date=datetime(2026, 1, 15), priority=Priority.MEDIUM),
]

result = sort_tasks(tasks, "due_date")
# Returns order: Task 2 (high), Task 3 (medium), Task 1 (low)
# All have same date, sorted by priority
```

#### Error Handling

| Error | Condition | Response |
|-------|-----------|----------|
| ValueError | sort_by not in valid options | Raise ValueError: "Invalid sort_by: '{value}'. Must be one of: due_date, priority, alphabetical" |
| TypeError | tasks is not a list | Raise TypeError: "tasks must be a list" |
| TypeError | tasks contains non-Task objects | Raise TypeError: "All items in tasks must be Task objects" |

#### Performance

- **Time Complexity**: O(n log n) for sorting
- **Space Complexity**: O(n) for new sorted list
- **Target**: <500ms for 1000 tasks

#### Testing Requirements

**Unit Tests**:
1. Sort by due date (earliest first)
2. Sort by due date with secondary priority sorting
3. Sort by due date with tasks without dates (grouped at end)
4. Sort by priority (high → medium → low)
5. Sort alphabetically (case-insensitive)
6. Sort empty list
7. Sort single task
8. Original list unchanged (immutability)
9. Error handling for invalid sort_by
10. Error handling for invalid inputs

**Edge Cases**:
1. All tasks have same due date (sorted by priority)
2. All tasks have same priority (maintain relative order)
3. All tasks have no due date (maintain original order)
4. Mixed: some with dates, some without

**Performance Tests**:
1. Sort 1000 tasks in <500ms

---

**Contract Version**: 1.0
**Date**: 2026-02-01
**Status**: Approved
