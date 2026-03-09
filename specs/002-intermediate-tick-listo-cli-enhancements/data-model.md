# Data Model: Intermediate Ticklisto Enhancements

**Feature**: 002-intermediate-ticklisto-enhancements
**Date**: 2026-02-01
**Status**: Phase 1 Design

## Overview

This document defines the enhanced data model for the Ticklisto application, adding priority levels, category tags, and due dates to the existing Task entity.

## Entities

### Task (Enhanced)

The core entity representing a user task with organizational metadata.

#### Fields

| Field | Type | Required | Default | Validation | Description |
|-------|------|----------|---------|------------|-------------|
| `id` | int | Yes | Auto-increment | Positive integer | Unique task identifier |
| `title` | str | Yes | - | Non-empty, max 200 chars | Task title/summary |
| `description` | str | No | None | Max 1000 chars | Detailed task description |
| `completed` | bool | Yes | False | - | Task completion status |
| `priority` | Priority (enum) | Yes | Priority.MEDIUM | Must be high/medium/low | Task priority level |
| `categories` | list[str] | Yes | [] | Each category max 50 chars | Category tags for organization |
| `due_date` | datetime | No | None | Must be valid datetime | Task due date (optional) |
| `created_at` | datetime | Yes | Auto (now) | - | Task creation timestamp |
| `updated_at` | datetime | Yes | Auto (now) | - | Last update timestamp |

#### Priority Enum

```python
from enum import Enum

class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

**Validation Rules**:
- MUST be one of: high, medium, low (case-insensitive input, stored lowercase)
- Invalid values MUST raise ValueError with clear message
- Display order: HIGH → MEDIUM → LOW

#### Categories Field

**Type**: `list[str]`

**Validation Rules**:
- Can be empty list (no categories assigned)
- Can contain multiple categories (no limit on count)
- Each category string:
  - Trimmed of whitespace
  - Converted to lowercase for consistency
  - Maximum 50 characters
  - No validation against predefined list (flexible)
- Duplicates automatically removed
- Predefined suggestions: ["work", "home", "personal"]

**Examples**:
```python
# Valid
categories = []  # No categories
categories = ["work"]  # Single category
categories = ["work", "home"]  # Multiple categories
categories = ["work", "home", "urgent", "client-meeting"]  # Custom categories

# Normalized
input: ["Work", "HOME", "work"]
stored: ["work", "home"]  # Deduplicated, lowercase
```

#### Due Date Field

**Type**: `datetime | None`

**Validation Rules**:
- Optional (can be None)
- If provided, must be valid datetime object
- No restriction on past dates (allows tracking overdue tasks)
- Stored with date and time components
- Display format: YYYY-MM-DD (time component optional in UI)

**Input Formats Supported** (via date parser):
- Standard: MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD
- Natural language: "today", "tomorrow", "next week", "next Monday", "in 3 days"

#### Timestamps

**created_at** and **updated_at**:
- Automatically managed by the system
- Set to current datetime on creation
- `updated_at` refreshed on any field modification
- Immutable by user (system-managed)

### Task Entity Example

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Task:
    """Enhanced task entity with priority, categories, and due date."""
    id: int
    title: str
    description: str | None = None
    completed: bool = False
    priority: Priority = Priority.MEDIUM
    categories: list[str] = field(default_factory=list)
    due_date: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        # Validate title
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Title cannot exceed 200 characters")

        # Validate description
        if self.description and len(self.description) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")

        # Normalize categories
        if self.categories:
            self.categories = list(set(
                cat.strip().lower()
                for cat in self.categories
                if cat.strip()
            ))
            # Validate each category length
            for cat in self.categories:
                if len(cat) > 50:
                    raise ValueError(f"Category '{cat}' exceeds 50 characters")

    def mark_complete(self):
        """Mark task as completed and update timestamp."""
        self.completed = True
        self.updated_at = datetime.now()

    def mark_incomplete(self):
        """Mark task as incomplete and update timestamp."""
        self.completed = False
        self.updated_at = datetime.now()

    def update_field(self, field_name: str, value):
        """Update a field and refresh updated_at timestamp."""
        setattr(self, field_name, value)
        self.updated_at = datetime.now()

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date or self.completed:
            return False
        return datetime.now() > self.due_date

    def matches_keyword(self, keyword: str) -> bool:
        """Check if task matches search keyword (case-insensitive)."""
        keyword_lower = keyword.lower()
        return (
            keyword_lower in self.title.lower() or
            (self.description and keyword_lower in self.description.lower())
        )

    def has_category(self, category: str) -> bool:
        """Check if task has specific category."""
        return category.lower() in self.categories

    def has_any_category(self, categories: list[str]) -> bool:
        """Check if task has any of the specified categories (OR logic)."""
        return any(self.has_category(cat) for cat in categories)

    def has_all_categories(self, categories: list[str]) -> bool:
        """Check if task has all of the specified categories (AND logic)."""
        return all(self.has_category(cat) for cat in categories)
```

## State Transitions

### Task Lifecycle

```
[Created] → [Active] → [Completed]
              ↓  ↑
              └──┘ (can toggle completion status)
```

**States**:
1. **Created**: Task just created, `completed=False`
2. **Active**: Task in progress, `completed=False`
3. **Completed**: Task finished, `completed=True`

**Transitions**:
- Create → Active: Automatic on creation
- Active → Completed: User marks task complete
- Completed → Active: User marks task incomplete (reopens)
- Any state → Updated: User modifies any field (updates `updated_at`)

**No terminal state**: Tasks can always be modified or toggled between active/completed.

## Validation Rules Summary

### Field-Level Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| title | Non-empty, ≤200 chars | "Title cannot be empty" / "Title cannot exceed 200 characters" |
| description | ≤1000 chars | "Description cannot exceed 1000 characters" |
| priority | Must be high/medium/low | "Invalid priority: '{value}'. Must be one of: high, medium, low" |
| categories | Each ≤50 chars | "Category '{cat}' exceeds 50 characters" |
| due_date | Valid datetime or None | "Invalid date format: {input}. Use MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD, or natural language" |

### Business Rules

1. **Unique IDs**: Each task must have unique ID (enforced by task manager)
2. **Immutable Timestamps**: `created_at` never changes; `updated_at` auto-refreshed
3. **Category Normalization**: Categories stored lowercase, deduplicated
4. **Priority Default**: New tasks default to MEDIUM priority
5. **Backward Compatibility**: Existing tasks without priority/categories/due_date get defaults

## Relationships

### Task → Categories (One-to-Many)

A task can have zero or more categories. Categories are not separate entities in Phase I (in-memory storage), but stored as list of strings within the Task entity.

**Future Consideration**: In later phases with persistent storage, categories might become separate entities with many-to-many relationship to tasks.

## Migration Strategy

### Backward Compatibility

Existing tasks (from basic implementation) need to be enhanced with new fields:

```python
def migrate_task(old_task) -> Task:
    """Migrate existing task to enhanced model."""
    return Task(
        id=old_task.id,
        title=old_task.title,
        description=getattr(old_task, 'description', None),
        completed=old_task.completed,
        priority=Priority.MEDIUM,  # Default for existing tasks
        categories=[],  # Empty for existing tasks
        due_date=None,  # No due date for existing tasks
        created_at=getattr(old_task, 'created_at', datetime.now()),
        updated_at=datetime.now()
    )
```

## Performance Considerations

### In-Memory Storage

- **Task List**: Python list, O(n) for search/filter operations
- **ID Lookup**: Linear search, acceptable for ≤1000 tasks
- **Category Filtering**: List comprehension, O(n) per filter
- **Sorting**: Python's Timsort, O(n log n)

**Performance Targets** (for 1000 tasks):
- Task creation: <1ms
- Search by keyword: <100ms
- Filter by criteria: <300ms
- Sort operations: <500ms
- All within specification requirements

### Memory Footprint

Estimated per task:
- Base fields: ~200 bytes
- Title/description: ~100-500 bytes
- Categories: ~50 bytes per category
- Total: ~500-1000 bytes per task

For 1000 tasks: ~0.5-1 MB (negligible for modern systems)

## Testing Strategy

### Unit Tests Required

1. **Task Creation**:
   - Valid task with all fields
   - Valid task with minimal fields (defaults)
   - Invalid title (empty, too long)
   - Invalid priority
   - Invalid categories (too long)

2. **Task Methods**:
   - `mark_complete()` / `mark_incomplete()`
   - `update_field()` updates timestamp
   - `is_overdue()` logic
   - `matches_keyword()` case-insensitive
   - `has_category()` / `has_any_category()` / `has_all_categories()`

3. **Validation**:
   - Priority enum validation
   - Category normalization (lowercase, deduplication)
   - Date parsing (multiple formats)

4. **State Transitions**:
   - Toggle completion status
   - Timestamp updates on modifications

### Integration Tests Required

1. Task manager operations with enhanced model
2. Search/filter/sort with new fields
3. Backward compatibility with existing tasks

---

**Data Model Status**: COMPLETE
**Date**: 2026-02-01
**Next**: Create API contracts
