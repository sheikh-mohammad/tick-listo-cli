# Filter Service Contract

**Service**: FilterService
**Purpose**: Provide multi-criteria filtering for tasks
**Module**: `src/ticklisto/services/filter_service.py`

## Interface

### filter_tasks

Filter tasks by multiple criteria: status, priority, categories, and date range.

#### Signature

```python
def filter_tasks(
    tasks: list[Task],
    status: str | None = None,
    priority: Priority | None = None,
    categories: list[str] | None = None,
    category_logic: str = "OR",
    date_filter: dict | None = None
) -> list[Task]:
    """
    Filter tasks by multiple criteria.

    Args:
        tasks: List of tasks to filter
        status: Filter by completion status ("completed" or "incomplete")
        priority: Filter by priority level (Priority enum)
        categories: Filter by category tags
        category_logic: "OR" (any category) or "AND" (all categories)
        date_filter: Date range filter specification

    Returns:
        List of tasks matching all specified criteria

    Raises:
        ValueError: If invalid filter parameters provided
    """
```

#### Input

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| tasks | list[Task] | Yes | - | Valid list | Tasks to filter |
| status | str \| None | No | None | "completed" or "incomplete" | Filter by completion status |
| priority | Priority \| None | No | None | Valid Priority enum | Filter by priority level |
| categories | list[str] \| None | No | None | List of category strings | Filter by categories |
| category_logic | str | No | "OR" | "OR" or "AND" | Category matching logic |
| date_filter | dict \| None | No | None | Valid date filter dict | Date range filter |

#### Date Filter Specification

The `date_filter` parameter accepts a dictionary with the following structures:

**Before a date**:
```python
{
    "type": "before",
    "date": datetime(2026, 12, 31)
}
```

**After a date**:
```python
{
    "type": "after",
    "date": datetime(2026, 1, 1)
}
```

**Between two dates**:
```python
{
    "type": "between",
    "start": datetime(2026, 1, 1),
    "end": datetime(2026, 12, 31)
}
```

**Relative dates** (handled by date parser before calling filter):
- "today", "tomorrow", "next week", etc. are parsed to datetime objects

#### Output

| Type | Description |
|------|-------------|
| list[Task] | Filtered list of tasks matching ALL criteria |

**Behavior**:
- All filters are applied with AND logic (task must match all specified criteria)
- If no filters specified (all None), returns all tasks
- Category filter uses OR or AND logic based on `category_logic` parameter
- Date filter only considers tasks with due_date set (tasks without due_date are excluded from date filtering)
- Preserves original task order
- Returns empty list if no matches found

#### Examples

```python
# Example 1: Filter by status
tasks = [
    Task(id=1, title="Task 1", completed=True),
    Task(id=2, title="Task 2", completed=False),
]

result = filter_tasks(tasks, status="completed")
# Returns: [Task(id=1, ...)]

# Example 2: Filter by priority
tasks = [
    Task(id=1, title="Task 1", priority=Priority.HIGH),
    Task(id=2, title="Task 2", priority=Priority.LOW),
]

result = filter_tasks(tasks, priority=Priority.HIGH)
# Returns: [Task(id=1, ...)]

# Example 3: Filter by categories (OR logic)
tasks = [
    Task(id=1, title="Task 1", categories=["work"]),
    Task(id=2, title="Task 2", categories=["home"]),
    Task(id=3, title="Task 3", categories=["work", "urgent"]),
]

result = filter_tasks(tasks, categories=["work", "home"], category_logic="OR")
# Returns: all 3 tasks (each has at least one matching category)

# Example 4: Filter by categories (AND logic)
result = filter_tasks(tasks, categories=["work", "urgent"], category_logic="AND")
# Returns: [Task(id=3, ...)] (only task with both categories)

# Example 5: Multiple criteria
result = filter_tasks(
    tasks,
    status="incomplete",
    priority=Priority.HIGH,
    categories=["work"]
)
# Returns: tasks matching ALL criteria

# Example 6: Date filter (before)
from datetime import datetime

tasks = [
    Task(id=1, title="Task 1", due_date=datetime(2026, 1, 15)),
    Task(id=2, title="Task 2", due_date=datetime(2026, 2, 15)),
    Task(id=3, title="Task 3", due_date=None),
]

result = filter_tasks(
    tasks,
    date_filter={"type": "before", "date": datetime(2026, 2, 1)}
)
# Returns: [Task(id=1, ...)] (Task 3 excluded - no due date)

# Example 7: Date filter (between)
result = filter_tasks(
    tasks,
    date_filter={
        "type": "between",
        "start": datetime(2026, 1, 1),
        "end": datetime(2026, 1, 31)
    }
)
# Returns: [Task(id=1, ...)]
```

#### Error Handling

| Error | Condition | Response |
|-------|-----------|----------|
| ValueError | status not "completed" or "incomplete" | Raise ValueError with message |
| ValueError | category_logic not "OR" or "AND" | Raise ValueError with message |
| ValueError | date_filter missing required keys | Raise ValueError with message |
| ValueError | date_filter has invalid type | Raise ValueError with message |
| TypeError | tasks is not a list | Raise TypeError with message |
| TypeError | categories is not a list | Raise TypeError with message |

#### Performance

- **Time Complexity**: O(n × f) where n = tasks, f = number of filters
- **Space Complexity**: O(m) where m = matching tasks
- **Target**: <300ms for 1000 tasks with multiple filters

#### Testing Requirements

**Unit Tests**:
1. Filter by status (completed/incomplete)
2. Filter by priority (each level)
3. Filter by single category
4. Filter by multiple categories (OR logic)
5. Filter by multiple categories (AND logic)
6. Filter by date (before/after/between)
7. Multiple criteria combined
8. No filters (returns all)
9. No matches (returns empty)
10. Tasks without due_date excluded from date filtering
11. Error handling for invalid parameters

**Performance Tests**:
1. Filter 1000 tasks with multiple criteria in <300ms

---

**Contract Version**: 1.0
**Date**: 2026-02-01
**Status**: Approved
