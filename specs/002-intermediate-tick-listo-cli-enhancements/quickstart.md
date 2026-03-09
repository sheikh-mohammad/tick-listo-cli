# Quickstart Guide: Intermediate Ticklisto Enhancements

**Feature**: 002-intermediate-ticklisto-enhancements
**Date**: 2026-02-01
**Audience**: Developers implementing this feature

## Overview

This guide helps developers understand the architecture and implementation approach for adding intermediate-level enhancements to the Ticklisto console application.

## Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────────────┐
│         CLI Layer (User Interface)       │
│  - commands.py: Command handlers         │
│  - display.py: Rich formatting          │
│  - parsers.py: Input parsing             │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Service Layer (Business Logic)   │
│  - task_manager.py: Core operations      │
│  - search_service.py: Search logic       │
│  - filter_service.py: Filter logic       │
│  - sort_service.py: Sort logic           │
│  - validation_service.py: Validation     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Model Layer (Data)               │
│  - task.py: Task entity with Priority    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Storage Layer (In-Memory)        │
│  - Python list of Task objects           │
└─────────────────────────────────────────┘
```

### Key Design Principles

1. **Separation of Concerns**: Each layer has distinct responsibilities
2. **Modularity**: Services are independent and composable
3. **Testability**: Pure functions with clear inputs/outputs
4. **Backward Compatibility**: Existing functionality preserved
5. **Immutability**: Sort/filter return new lists, don't modify originals

## Development Environment Setup

### Prerequisites

- Python 3.13+
- UV package manager
- Git

### Installation

```bash
# Clone repository
git clone <repo-url>
cd Phase_I

# Install dependencies with UV
uv sync

# Verify installation
uv run python -c "import rich; print('Rich installed successfully')"
```

### Dependencies

```toml
# pyproject.toml
[project]
dependencies = [
    "rich>=13.0.0",
    "python-dateutil>=2.8.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0"
]
```

## Project Structure

```
src/ticklisto/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── task.py              # Enhanced Task entity
├── services/
│   ├── __init__.py
│   ├── task_manager.py      # Core task operations (existing)
│   ├── search_service.py    # NEW: Search functionality
│   ├── filter_service.py    # NEW: Filter operations
│   ├── sort_service.py      # NEW: Sort operations
│   └── validation_service.py # NEW: Input validation
├── cli/
│   ├── __init__.py
│   ├── commands.py          # CLI command handlers (enhanced)
│   ├── display.py           # Rich formatting (enhanced)
│   └── parsers.py           # NEW: Date and input parsing
└── utils/
    ├── __init__.py
    └── date_parser.py       # NEW: Flexible date parsing

tests/
├── unit/
│   ├── test_task_model.py
│   ├── test_search_service.py
│   ├── test_filter_service.py
│   ├── test_sort_service.py
│   ├── test_validation_service.py
│   └── test_date_parser.py
├── integration/
│   ├── test_task_operations.py
│   ├── test_search_filter_integration.py
│   └── test_cli_commands.py
└── contract/
    └── test_backward_compatibility.py
```

## Implementation Workflow

### Step 1: Enhance Task Model

**File**: `src/ticklisto/models/task.py`

Add new fields to Task entity:
- `priority: Priority` (enum: high/medium/low)
- `categories: list[str]` (list of category tags)
- `due_date: datetime | None` (optional due date)

**Key Points**:
- Use `@dataclass` decorator
- Add `__post_init__` for validation
- Implement helper methods: `is_overdue()`, `matches_keyword()`, `has_category()`

**Test First**: Write tests in `tests/unit/test_task_model.py` before implementation

### Step 2: Create Validation Service

**File**: `src/ticklisto/services/validation_service.py`

Implement validation functions:
- `validate_priority(priority: str) -> Priority`
- `validate_categories(categories: list[str]) -> list[str]`
- `get_category_suggestions(partial: str) -> list[str]`
- `validate_date_input(date_input: str) -> datetime`

**Key Points**:
- Use Priority enum for type safety
- Normalize categories (lowercase, deduplicate)
- Support flexible date parsing with python-dateutil

**Test First**: Write tests in `tests/unit/test_validation_service.py`

### Step 3: Create Search Service

**File**: `src/ticklisto/services/search_service.py`

Implement search function:
- `search_tasks(tasks: list[Task], keyword: str) -> list[Task]`

**Key Points**:
- Case-insensitive matching
- Search in title and description
- O(n) time complexity

**Test First**: Write tests in `tests/unit/test_search_service.py`

### Step 4: Create Filter Service

**File**: `src/ticklisto/services/filter_service.py`

Implement filter function:
- `filter_tasks(tasks, status, priority, categories, category_logic, date_filter) -> list[Task]`

**Key Points**:
- Composable filters (all criteria with AND logic)
- Category filter supports OR/AND logic
- Date filter handles before/after/between

**Test First**: Write tests in `tests/unit/test_filter_service.py`

### Step 5: Create Sort Service

**File**: `src/ticklisto/services/sort_service.py`

Implement sort function:
- `sort_tasks(tasks: list[Task], sort_by: str) -> list[Task]`

**Key Points**:
- Multi-level sorting (due_date + priority)
- Tasks without due dates grouped separately
- Returns new list (immutable)

**Test First**: Write tests in `tests/unit/test_sort_service.py`

### Step 6: Enhance CLI Layer

**Files**:
- `src/ticklisto/cli/commands.py` - Add new commands
- `src/ticklisto/cli/display.py` - Enhance Rich formatting
- `src/ticklisto/cli/parsers.py` - Add input parsing

**New Commands**:
- Search command
- Filter command
- Sort command
- Clear command (alias: clr)

**Enhanced Display**:
- Table with priority indicators (colored dots)
- Category tags display
- Due date formatting
- Status indicators

**Test First**: Write tests in `tests/integration/test_cli_commands.py`

### Step 7: Update Task Manager

**File**: `src/ticklisto/services/task_manager.py`

Integrate new services:
- Use validation service for task creation/updates
- Expose search/filter/sort operations
- Maintain backward compatibility

**Test First**: Write tests in `tests/contract/test_backward_compatibility.py`

## Testing Strategy

### Test-Driven Development (TDD)

**Red-Green-Refactor Cycle**:
1. **Red**: Write failing test
2. **Green**: Implement minimal code to pass
3. **Refactor**: Improve code quality

### Test Levels

**Unit Tests** (tests/unit/):
- Test individual functions in isolation
- Mock dependencies
- Fast execution (<1s total)

**Integration Tests** (tests/integration/):
- Test service interactions
- Test CLI command workflows
- Moderate execution time (<5s total)

**Contract Tests** (tests/contract/):
- Test backward compatibility
- Ensure existing features work
- Critical for regression prevention

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/ticklisto --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_task_model.py

# Run specific test
uv run pytest tests/unit/test_task_model.py::test_task_creation

# Run tests matching pattern
uv run pytest -k "search"
```

### Test Coverage Requirements

- Minimum 90% code coverage
- 100% coverage for validation logic
- All edge cases tested

## Common Patterns

### Pattern 1: Service Function

```python
def service_function(input_data: InputType) -> OutputType:
    """
    Brief description.

    Args:
        input_data: Description

    Returns:
        Description

    Raises:
        ValueError: When validation fails
    """
    # Validate input
    if not input_data:
        raise ValueError("Input cannot be empty")

    # Process
    result = process(input_data)

    # Return
    return result
```

### Pattern 2: Rich Table Display

```python
from rich.table import Table
from rich.console import Console

def display_tasks(tasks: list[Task]):
    """Display tasks in formatted table."""
    console = Console()
    table = Table(title="Tasks")

    # Add columns
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Priority")

    # Add rows
    for task in tasks:
        priority_style = {
            "high": "[red]●[/red] High",
            "medium": "[yellow]●[/yellow] Medium",
            "low": "[green]●[/green] Low"
        }[task.priority.value]

        table.add_row(str(task.id), task.title, priority_style)

    console.print(table)
```

### Pattern 3: Input Validation with Rich

```python
from rich.prompt import Prompt
from rich.console import Console

def get_validated_input():
    """Get validated user input."""
    console = Console()

    # Show suggestions
    console.print("[dim]Suggested: work, home, personal[/dim]")

    # Get input with validation
    priority = Prompt.ask(
        "Priority",
        choices=["high", "medium", "low"],
        default="medium"
    )

    return priority
```

## Debugging Tips

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Processing {len(tasks)} tasks")
```

### Rich Console Debugging

```python
from rich.console import Console

console = Console()
console.print(f"[yellow]Debug:[/yellow] tasks={tasks}")
```

### Common Issues

**Issue**: Date parsing fails
**Solution**: Check date format, ensure python-dateutil is installed

**Issue**: Priority validation fails
**Solution**: Ensure input is lowercase before validation

**Issue**: Category filter returns no results
**Solution**: Check category normalization (lowercase, trimmed)

## Performance Optimization

### Profiling

```bash
# Profile with cProfile
uv run python -m cProfile -o profile.stats src/ticklisto/main.py

# Analyze with snakeviz
uv run snakeviz profile.stats
```

### Performance Targets

| Operation | Target | Current |
|-----------|--------|---------|
| Search 1000 tasks | <100ms | TBD |
| Filter 1000 tasks | <300ms | TBD |
| Sort 1000 tasks | <500ms | TBD |
| Task creation | <2s | TBD |

## Git Workflow

### Branch Strategy

```bash
# Feature branch (already created)
git checkout 002-intermediate-ticklisto-enhancements

# Create commits for each atomic change
git add src/ticklisto/models/task.py
git commit -m "feat: enhance Task model with priority, categories, due_date

- Add Priority enum (high/medium/low)
- Add categories field (list of strings)
- Add due_date field (optional datetime)
- Add validation in __post_init__
- Add helper methods for filtering

Co-authored-by: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Commit Message Format

```
<type>: <subject>

<body>

Co-authored-by: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types**: feat, fix, refactor, test, docs

## Next Steps

1. Review this quickstart guide
2. Set up development environment
3. Review contracts in `contracts/` directory
4. Start with Task model enhancement (TDD)
5. Implement services one by one (TDD)
6. Enhance CLI layer
7. Run full test suite
8. Update README.md with new features
9. Create pull request

## Resources

- [Rich Documentation](https://rich.readthedocs.io/)
- [python-dateutil Documentation](https://dateutil.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Python Enums](https://docs.python.org/3/library/enum.html)

## Support

For questions or issues:
1. Review the spec: `specs/002-intermediate-ticklisto-enhancements/spec.md`
2. Check contracts: `specs/002-intermediate-ticklisto-enhancements/contracts/`
3. Review research: `specs/002-intermediate-ticklisto-enhancements/research.md`
4. Consult constitution: `.specify/memory/constitution.md`

---

**Quickstart Version**: 1.0
**Date**: 2026-02-01
**Status**: Ready for Implementation
