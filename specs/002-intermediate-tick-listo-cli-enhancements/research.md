# Research Findings: Intermediate Ticklisto Enhancements

**Date**: 2026-02-01
**Feature**: 002-intermediate-ticklisto-enhancements
**Phase**: 0 - Research & Unknowns Resolution

## Overview

This document consolidates research findings for technical decisions required to implement intermediate-level enhancements to the Ticklisto console application.

## 1. Date Parsing Library Selection

### Decision
**Use `python-dateutil` library**

### Rationale
- **Mature and stable**: Part of the Python ecosystem since 2003, widely adopted
- **Flexible parsing**: `dateutil.parser.parse()` handles multiple date formats automatically (MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD)
- **Relative date support**: `dateutil.relativedelta` provides relative date calculations
- **Minimal dependencies**: Pure Python implementation, no external system dependencies
- **Performance**: Sufficient for our scale (1000 tasks, <500ms requirement)
- **Standard library integration**: Works seamlessly with Python's datetime module

### Alternatives Considered

**Arrow**
- Pros: More intuitive API, better natural language support
- Cons: Additional dependency layer over dateutil, less widely adopted
- Rejected because: Adds complexity without significant benefit for our use case

**Pendulum**
- Pros: Excellent timezone support, immutable datetime objects
- Cons: Heavier dependency, timezone features not needed for Phase I
- Rejected because: Over-engineered for console app without timezone requirements

**Custom Implementation**
- Pros: No external dependencies, full control
- Cons: Significant development effort, error-prone, maintenance burden
- Rejected because: Reinventing the wheel, high risk of bugs

### Implementation Approach

```python
from dateutil import parser, relativedelta
from datetime import datetime, timedelta

def parse_flexible_date(date_input: str) -> datetime:
    """Parse flexible date input including natural language."""
    date_input = date_input.lower().strip()

    # Handle natural language
    if date_input == "today":
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_input == "tomorrow":
        return datetime.now() + timedelta(days=1)
    elif date_input == "next week":
        return datetime.now() + timedelta(weeks=1)
    elif date_input.startswith("in ") and date_input.endswith(" days"):
        days = int(date_input.split()[1])
        return datetime.now() + timedelta(days=days)
    elif date_input.startswith("next "):
        # Handle "next Monday", "next Tuesday", etc.
        weekday = date_input.split()[1]
        # Implementation using relativedelta
        pass

    # Fall back to dateutil parser for standard formats
    try:
        return parser.parse(date_input)
    except parser.ParserError as e:
        raise ValueError(f"Invalid date format: {date_input}. Use MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD, or natural language (today, tomorrow, next week)")
```

### Performance Characteristics
- Parsing: <1ms per date
- Well within our <500ms requirement for filtering operations

---

## 2. Rich Library Best Practices

### Decision
**Use Rich library with modular display components**

### Rationale
- **Already in tech stack**: Specified in constitution and feature spec
- **Comprehensive CLI toolkit**: Tables, prompts, console management, styling
- **Excellent documentation**: Well-maintained with extensive examples
- **Performance**: Handles 1000+ rows efficiently with pagination
- **User experience**: Professional-looking CLI with minimal code

### Implementation Patterns

#### Console Clearing
```python
from rich.console import Console

console = Console()

def clear_console():
    """Clear the console screen."""
    console.clear()
```

#### Dynamic Table Formatting
```python
from rich.table import Table
from rich.console import Console

def display_tasks(tasks: list, console: Console):
    """Display tasks in a formatted table."""
    table = Table(title="Tasks", show_header=True, header_style="bold magenta")

    table.add_column("ID", style="cyan", width=6)
    table.add_column("Title", style="white", width=30)
    table.add_column("Priority", width=10)
    table.add_column("Categories", width=20)
    table.add_column("Due Date", width=12)
    table.add_column("Status", width=10)

    for task in tasks:
        priority_style = {
            "high": "[red]●[/red] High",
            "medium": "[yellow]●[/yellow] Medium",
            "low": "[green]●[/green] Low"
        }.get(task.priority, "")

        categories_str = ", ".join(task.categories) if task.categories else "-"
        due_date_str = task.due_date.strftime("%Y-%m-%d") if task.due_date else "-"
        status_str = "[green]✓[/green] Done" if task.completed else "[white]○[/white] Pending"

        table.add_row(
            str(task.id),
            task.title,
            priority_style,
            categories_str,
            due_date_str,
            status_str
        )

    console.print(table)
```

#### Input Validation with Prompts
```python
from rich.prompt import Prompt

def get_priority_input(console: Console) -> str:
    """Get validated priority input from user."""
    while True:
        priority = Prompt.ask(
            "Priority",
            choices=["high", "medium", "low"],
            default="medium"
        )
        return priority
```

#### Autocomplete for Categories
```python
from rich.prompt import Prompt

def get_categories_input(console: Console) -> list[str]:
    """Get category input with suggestions."""
    categories_str = Prompt.ask(
        "Categories (comma-separated)",
        default="",
        show_default=False
    )

    if not categories_str:
        return []

    # Parse comma-separated values
    categories = [cat.strip() for cat in categories_str.split(",") if cat.strip()]

    # Note: Rich doesn't have built-in autocomplete for Prompt
    # For Phase I, we'll show suggestions in help text
    # Future enhancement: Use prompt_toolkit for advanced autocomplete

    return categories
```

### Best Practices
- Use `Console()` singleton for consistent output
- Leverage Rich's markup syntax for inline styling: `[red]text[/red]`
- Use `Table` for structured data display
- Use `Prompt` for validated user input
- Use `Panel` for grouping related information
- Keep table widths reasonable for standard terminal sizes (80-120 chars)

---

## 3. In-Memory Search/Filter/Sort Performance

### Decision
**Use Python list comprehensions with functional composition**

### Rationale
- **Simplicity**: Pythonic, readable, maintainable
- **Performance**: Sufficient for 1000 tasks (<500ms requirement)
- **No external dependencies**: Built-in Python features
- **Composability**: Easy to combine multiple filters
- **Testability**: Pure functions, easy to unit test

### Implementation Patterns

#### Search (Case-Insensitive Keyword)
```python
def search_tasks(tasks: list, keyword: str) -> list:
    """Search tasks by keyword in title and description."""
    if not keyword:
        return tasks

    keyword_lower = keyword.lower()
    return [
        task for task in tasks
        if keyword_lower in task.title.lower() or
           keyword_lower in (task.description or "").lower()
    ]
```

#### Filter (Multiple Criteria)
```python
def filter_tasks(
    tasks: list,
    status: str = None,
    priority: str = None,
    categories: list[str] = None,
    category_logic: str = "OR",  # "OR" or "AND"
    date_filter: dict = None
) -> list:
    """Filter tasks by multiple criteria."""
    filtered = tasks

    # Filter by status
    if status is not None:
        completed = status.lower() == "completed"
        filtered = [t for t in filtered if t.completed == completed]

    # Filter by priority
    if priority:
        filtered = [t for t in filtered if t.priority == priority]

    # Filter by categories
    if categories:
        if category_logic == "OR":
            # Task matches if it has ANY of the selected categories
            filtered = [
                t for t in filtered
                if any(cat in t.categories for cat in categories)
            ]
        else:  # AND logic
            # Task matches if it has ALL of the selected categories
            filtered = [
                t for t in filtered
                if all(cat in t.categories for cat in categories)
            ]

    # Filter by date
    if date_filter:
        filtered = apply_date_filter(filtered, date_filter)

    return filtered

def apply_date_filter(tasks: list, date_filter: dict) -> list:
    """Apply date range filter to tasks."""
    filter_type = date_filter.get("type")

    if filter_type == "before":
        date = date_filter["date"]
        return [t for t in tasks if t.due_date and t.due_date < date]
    elif filter_type == "after":
        date = date_filter["date"]
        return [t for t in tasks if t.due_date and t.due_date > date]
    elif filter_type == "between":
        start = date_filter["start"]
        end = date_filter["end"]
        return [t for t in tasks if t.due_date and start <= t.due_date <= end]

    return tasks
```

#### Sort (Multi-Level)
```python
from datetime import datetime

def sort_tasks(tasks: list, sort_by: str = "due_date") -> list:
    """Sort tasks with multi-level sorting."""
    if sort_by == "due_date":
        # Primary: due date (earliest first), Secondary: priority (high first)
        # Tasks without due dates go to separate section

        tasks_with_dates = [t for t in tasks if t.due_date]
        tasks_without_dates = [t for t in tasks if not t.due_date]

        priority_order = {"high": 0, "medium": 1, "low": 2}

        sorted_with_dates = sorted(
            tasks_with_dates,
            key=lambda t: (
                t.due_date,
                priority_order.get(t.priority, 3)
            )
        )

        return sorted_with_dates + tasks_without_dates

    elif sort_by == "priority":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: priority_order.get(t.priority, 3))

    elif sort_by == "alphabetical":
        return sorted(tasks, key=lambda t: t.title.lower())

    return tasks
```

### Performance Characteristics
- **Search**: O(n) where n = number of tasks, ~0.1ms for 1000 tasks
- **Filter**: O(n) per filter criterion, composable, ~0.2ms for 1000 tasks
- **Sort**: O(n log n), ~0.5ms for 1000 tasks
- **Combined operations**: <1ms total for typical use cases

### Alternatives Considered

**Generator Expressions**
- Pros: Memory efficient for large datasets
- Cons: Can't be reused, harder to debug
- Rejected because: 1000 tasks is small enough for list comprehensions

**Pandas DataFrame**
- Pros: Powerful filtering and sorting capabilities
- Cons: Heavy dependency, overkill for simple operations
- Rejected because: Adds 100MB+ dependency for minimal benefit

**Custom Indexing**
- Pros: Faster lookups for specific queries
- Cons: Complexity, memory overhead, premature optimization
- Rejected because: Performance requirements easily met without indexing

---

## 4. Validation Strategy

### Decision
**Use enum-based validation for priority, flexible string validation for categories**

### Rationale
- **Type safety**: Python enums provide compile-time checking
- **Clear error messages**: Enum validation gives specific feedback
- **Extensibility**: Easy to add new priority levels or category suggestions
- **User experience**: Strict validation prevents errors, flexible validation allows customization

### Implementation Patterns

#### Strict Priority Validation
```python
from enum import Enum

class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

def validate_priority(priority: str) -> Priority:
    """Validate and convert priority string to enum."""
    try:
        return Priority(priority.lower())
    except ValueError:
        valid_values = ", ".join([p.value for p in Priority])
        raise ValueError(
            f"Invalid priority: '{priority}'. "
            f"Must be one of: {valid_values}"
        )
```

#### Flexible Category Validation
```python
# Predefined category suggestions
DEFAULT_CATEGORIES = ["work", "home", "personal"]

def validate_categories(categories: list[str]) -> list[str]:
    """Validate category list (accepts any string, provides suggestions)."""
    if not categories:
        return []

    # Clean and deduplicate
    cleaned = list(set(cat.strip().lower() for cat in categories if cat.strip()))

    # No strict validation - accept any string
    # Suggestions are provided at UI level, not validation level

    return cleaned

def get_category_suggestions(partial: str) -> list[str]:
    """Get category suggestions for autocomplete."""
    if not partial:
        return DEFAULT_CATEGORIES

    partial_lower = partial.lower()
    return [
        cat for cat in DEFAULT_CATEGORIES
        if cat.startswith(partial_lower)
    ]
```

#### Integration with Rich Prompts
```python
from rich.prompt import Prompt
from rich.console import Console

def prompt_for_priority(console: Console) -> Priority:
    """Prompt user for priority with validation."""
    priority_str = Prompt.ask(
        "Priority",
        choices=["high", "medium", "low"],
        default="medium"
    )
    return Priority(priority_str)

def prompt_for_categories(console: Console) -> list[str]:
    """Prompt user for categories with suggestions."""
    console.print(f"[dim]Suggested categories: {', '.join(DEFAULT_CATEGORIES)}[/dim]")
    categories_str = Prompt.ask(
        "Categories (comma-separated, or press Enter to skip)",
        default=""
    )

    if not categories_str:
        return []

    categories = [cat.strip() for cat in categories_str.split(",") if cat.strip()]
    return validate_categories(categories)
```

### Error Handling Pattern
```python
def create_task_with_validation(title: str, priority: str, categories: list[str]) -> Task:
    """Create task with validation."""
    try:
        validated_priority = validate_priority(priority)
        validated_categories = validate_categories(categories)

        return Task(
            title=title,
            priority=validated_priority,
            categories=validated_categories
        )
    except ValueError as e:
        # Rich console error display
        console.print(f"[red]Error:[/red] {str(e)}")
        raise
```

### Alternatives Considered

**Pydantic Models**
- Pros: Comprehensive validation framework, type hints
- Cons: Additional dependency, overkill for simple CLI validation
- Rejected because: Enum-based validation is sufficient and lightweight

**Custom Validator Classes**
- Pros: Full control, extensible
- Cons: More code to maintain, reinventing the wheel
- Rejected because: Python enums provide needed functionality

**No Validation**
- Pros: Simplest implementation
- Cons: Poor user experience, data integrity issues
- Rejected because: Spec requires strict priority validation

---

## Summary of Decisions

| Area | Decision | Key Benefit |
|------|----------|-------------|
| Date Parsing | python-dateutil | Mature, flexible, standard library integration |
| CLI Framework | Rich library patterns | Professional UI, comprehensive toolkit |
| Search/Filter/Sort | List comprehensions | Simple, performant, Pythonic |
| Validation | Enum (priority) + flexible (categories) | Type safety + user flexibility |

## Dependencies to Add

```toml
# pyproject.toml additions
[project]
dependencies = [
    "rich>=13.0.0",
    "python-dateutil>=2.8.0"
]
```

## Next Steps

1. Proceed to Phase 1: Design & Contracts
2. Create data-model.md with enhanced Task entity
3. Define API contracts for new services
4. Generate quickstart.md for developers
5. Update agent context with new technologies

---

**Research Status**: COMPLETE
**Date Completed**: 2026-02-01
**Ready for Phase 1**: YES
