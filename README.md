```
████████╗██╗ ██████╗██╗  ██╗    ██╗     ██╗███████╗████████╗ ██████╗      ██████╗██╗     ██╗
╚══██╔══╝██║██╔════╝██║ ██╔╝    ██║     ██║██╔════╝╚══██╔══╝██╔═══██╗    ██╔════╝██║     ██║
   ██║   ██║██║     █████╔╝     ██║     ██║███████╗   ██║   ██║   ██║    ██║     ██║     ██║
   ██║   ██║██║     ██╔═██╗     ██║     ██║╚════██║   ██║   ██║   ██║    ██║     ██║     ██║
   ██║   ██║╚██████╗██║  ██╗    ███████╗██║███████║   ██║   ╚██████╔╝    ╚██████╗███████╗██║
   ╚═╝   ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚══════╝╚═╝╚══════╝   ╚═╝    ╚═════╝      ╚═════╝╚══════╝╚═╝
Tick Listo CLI - Your Ultimate Task Management Companion - Where Productivity Meets Elegance
```


# Tick Listo CLI

A command-line task management application with **persistent JSON storage** and advanced organization features. Built with Python 3.14+ and Rich for beautiful console formatting.

## Features

### Core Task Management
- Add, view, update, delete, and mark tasks as complete/incomplete
- **Auto-incrementing task IDs** (1, 2, 3...) that persist across sessions
- **JSON file persistence** (ticklisto_data.json) - tasks survive application restarts
- Rich-formatted console interface with visual status indicators
- Sub-second response times for all operations
- Graceful error handling with informative messages

### Advanced Organization
- **Priority Levels** (REQUIRED): Assign high, medium, or low priority to every task
- **Category Tags** (REQUIRED): Organize tasks with one or more category labels
- **Due Dates**: Set deadlines with flexible date parsing (MM/DD/YYYY, natural language like "tomorrow", "next week")
- **Search with Scope**: Find tasks by keyword in title only, description only, or both
- **Filter**: Filter tasks by status, priority, categories, and due dates
- **Sort**: Sort tasks by due date, priority, or alphabetically
- **Delete All**: Remove all tasks at once with confirmation prompt
- **Enhanced Clear**: Properly clear terminal buffer (not just scroll)

### Data Persistence
- **JSON Storage**: All tasks saved to `ticklisto_data.json` in the project directory
- **Atomic Writes**: Safe file operations prevent data corruption
- **ID Management**: Task IDs never reused during normal operation
- **ID Reset**: After "delete all", ID counter resets to 1 for fresh start

## Prerequisites

- Python 3.14+
- UV package manager

## Installation

1. Clone or download the repository
2. Install dependencies using UV:

```bash
uv sync
```

Or install the required packages directly:

```bash
pip install rich pytest python-dateutil
```

## Usage

Run the application:

```bash
python -m src.ticklisto
```

Or alternatively:

```bash
cd src
python -m todo_app
```

### Available Commands

#### Basic Commands
- `add` or `a` - Add a new task (priority and categories REQUIRED)
- `view` or `v` - View all tasks with enhanced formatting
- `update` or `u` - Update a task (full re-entry of all fields required)
- `delete` or `d` - Delete a single task
- `delete all` or `dela` - Delete all tasks with confirmation
- `complete` or `c` - Mark task as complete/incomplete
- `stats` or `s` - View task statistics

#### Organization Commands
- `search` or `find` or `f` - Search tasks by keyword with scope selection
- `filter` or `fl` - Filter tasks by status, priority, categories, or dates
- `sort` or `sr` - Sort tasks by due date, priority, or title
- `clear` or `clr` - Clear the terminal screen and buffer

#### System Commands
- `help` or `h` - Show help information
- `quit` or `q` - Save and exit the application

### Example Workflow

1. Start the application: `python -m src.ticklisto`
2. Add a task: Enter `add` or `a` and follow the prompts (priority and categories required)
3. View tasks: Enter `view` or `v` to see all tasks
4. Mark as complete: Enter `complete` or `c` and specify task ID
5. Update task: Enter `update` or `u` and specify task ID (full re-entry required)
6. Delete task: Enter `delete` or `d` and specify task ID
7. Exit: Enter `quit` or `q` to save and exit

## Usage Examples

### Adding Tasks (Priority and Categories Required)

**Adding a task with required fields:**
```
> add
Enter task title: Complete project documentation
Enter task description (optional): Write comprehensive docs for the new features
Enter task priority (high/medium/low) *required: high
Suggested categories: work, home, personal
Enter task categories (comma-separated) *required: work, documentation, urgent
Add a due date? (y/n): y
Enter due date (MM/DD/YYYY, YYYY-MM-DD, or 'tomorrow', 'next week', etc.): tomorrow

✓ Task added successfully with ID: 1
```

**Priority and categories are mandatory:**
```
> add
Enter task title: Buy groceries
Enter task description (optional):
Enter task priority (high/medium/low) *required: [press Enter without input]
❌ Priority is required. Must be one of: high, medium, low
Try again? (y/n): y
Enter task priority (high/medium/low) *required: medium
Enter task categories (comma-separated) *required: home, shopping

✓ Task added successfully with ID: 2
```

### JSON Persistence

**Tasks persist across application restarts:**
```
Session 1:
> add
[Create tasks with IDs 1, 2, 3]
> quit
Tasks saved successfully. Goodbye!

[Restart application]

Session 2:
> view
[All tasks from Session 1 are still there with IDs 1, 2, 3]
> add
[New task gets ID 4]
```

**Data file location:**
- All tasks stored in `ticklisto_data.json` in the project directory
- File uses atomic write operations for data safety
- Backup recommended before major operations

### ID Management

**IDs never reused during normal operation:**
```
> add
Task added with ID: 1

> add
Task added with ID: 2

> delete
Enter task ID to delete: 1
Task 1 deleted successfully!

> add
Task added with ID: 3  (NOT 1 - IDs never reused)
```

**ID counter resets after delete all:**
```
> view
[Shows tasks with IDs 5, 7, 9]

> delete all
⚠️  WARNING: Delete All Tasks
This will permanently delete ALL tasks and reset the ID counter to 1.
Are you sure you want to continue? (y/n): y
✓ All tasks deleted successfully
ID counter reset to 1

> add
Task added with ID: 1  (Fresh start!)
```

### Updating Tasks (Full Re-entry Required)

**Update requires re-entering all fields:**
```
> update
Enter task ID to update: 3

Current Task Details:
  Title: Old Title
  Description: Old Description
  Priority: medium
  Categories: work
  Due Date: 2026-02-15
  Completed: False

Please re-enter ALL fields (full re-entry required):

Enter task title [Old Title]: New Title
Enter task description [Old Description]: New Description
Enter task priority (high/medium/low) [medium]: high
Enter task categories (comma-separated) [work]: work, urgent, client
Add/update due date? (y/n): y
Enter due date [2026-02-15]: next week

✓ Task 3 updated successfully!
```
```

**Updating task priority:**
```
> update
Enter task ID to update: 5
Enter new priority (high/medium/low) or press Enter to keep current: high
```

**Adding categories to existing task:**
```
> update
Enter task ID to update: 3
Enter new categories (comma-separated) or press Enter to keep current: work, client, urgent
```

### Searching Tasks with Scope Selection

**Search with scope selection (title, description, or both):**
```
> search
Enter search keyword: documentation

Search scope options:
  1. Title only
  2. Description only
  3. Both title and description (default)

Select search scope [3]: 1

Found 2 task(s) matching 'documentation' in titles:
[Displays tasks with "documentation" in title only]
```

**Search in description only:**
```
> search
Enter search keyword: meeting
Select search scope [3]: 2

Found 3 task(s) matching 'meeting' in descriptions:
[Displays tasks with "meeting" in description only]
```

**Search in both fields (default):**
```
> search
Enter search keyword: project
Select search scope [3]: 3

Found 7 task(s) matching 'project' in titles and descriptions:
[Displays all tasks with "project" in either title or description]
```

**Search is case-insensitive and matches partial words:**
```
> search
Enter search keyword: proj
Select search scope [3]: 3

Found 5 task(s) matching 'proj':
- Complete project documentation
- Project planning meeting
- Review project proposal
...
```

### Delete All Tasks

**Delete all tasks with confirmation:**
```
> delete all

⚠️  WARNING: Delete All Tasks

This will permanently delete ALL tasks and reset the ID counter to 1.
This action cannot be undone.

Are you sure you want to continue? (y/n): y

✓ All tasks deleted successfully
ID counter reset to 1
```

**Using the dela alias:**
```
> dela

⚠️  WARNING: Delete All Tasks
...
```

**Delete all with no tasks:**
```
> delete all

No tasks to delete.
```

**Cancelling delete all:**
```
> delete all

⚠️  WARNING: Delete All Tasks
...
Are you sure you want to continue? (y/n): n

Delete all cancelled. No changes made.
```

### Enhanced Clear Command

**Clear terminal buffer completely:**
```
> clear

Terminal cleared successfully!
```

**Using the clr alias:**
```
> clr

Terminal cleared successfully!
```

The enhanced clear command:
- Properly clears the terminal buffer (not just scrolling)
- Prevents scroll-back to previous commands
- Uses platform-specific mechanisms (Windows: cls, Linux/macOS: ANSI codes + clear)
- Works across Windows, Linux, and macOS

### Searching Tasks

**Search by keyword in title or description:**
```
> search
Enter search keyword: documentation

Found 3 task(s) matching 'documentation':
[Displays matching tasks with priority indicators and category tags]
```

**Search is case-insensitive and matches partial words:**
```
> search
Enter search keyword: proj

Found 5 task(s) matching 'proj':
- Complete project documentation
- Project planning meeting
- Review project proposal
...
```

### Filtering Tasks

**Filter by status:**
```
> filter
Select filter option: 1 (Status)
Filter by status: incomplete

Found 12 task(s) matching your criteria:
[Displays all incomplete tasks]
```

**Filter by priority:**
```
> filter
Select filter option: 2 (Priority)
Filter by priority: high

Found 5 task(s) matching your criteria:
[Displays all high-priority tasks]
```

**Filter by categories (OR logic):**
```
> filter
Select filter option: 3 (Categories)
Enter categories (comma-separated): work, urgent
Match logic: any

Found 8 task(s) matching your criteria:
[Displays tasks with either 'work' OR 'urgent' category]
```

**Filter by categories (AND logic):**
```
> filter
Select filter option: 3 (Categories)
Enter categories (comma-separated): work, urgent
Match logic: all

Found 3 task(s) matching your criteria:
[Displays tasks with both 'work' AND 'urgent' categories]
```

**Filter by multiple criteria:**
```
> filter
Select filter option: 4 (All criteria)
Filter by status: incomplete
Filter by priority: high
Enter categories: work
Match logic: any

Found 2 task(s) matching your criteria:
[Displays incomplete, high-priority tasks in 'work' category]
```

### Sorting Tasks

**Sort by due date (earliest first):**
```
> sort
Select sort option: 1 (Due Date)
Apply secondary sort? Yes
Secondary sort: priority

Tasks sorted by due date (then by priority):
[Displays tasks ordered by due date, with high priority first for same dates]
```

**Sort by priority (high to low):**
```
> sort
Select sort option: 2 (Priority)
Apply secondary sort? No

Tasks sorted by priority:
[Displays all high priority tasks first, then medium, then low]
```

**Sort alphabetically by title:**
```
> sort
Select sort option: 3 (Title)

Tasks sorted by title:
[Displays tasks in alphabetical order]
```

### Clearing the Console

**Clear the screen for a fresh view:**
```
> clear
Console cleared!
```

Or use the shorter alias:
```
> clr
Console cleared!
```

## Project Structure

```
src/
├── ticklisto/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py              # Enhanced Task data model with priority, categories, due_date
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_service.py      # Core task CRUD operations
│   │   ├── search_service.py    # Search functionality
│   │   ├── filter_service.py    # Filter functionality
│   │   ├── sort_service.py      # Sort functionality
│   │   └── validation_service.py # Input validation
│   ├── cli/
│   │   ├── __init__.py
│   │   └── ticklisto_cli.py     # Command-line interface with all commands
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── rich_ui.py           # Rich formatting and display
│   │   └── components.py        # Reusable UI components
│   └── utils/
│       ├── __init__.py
│       ├── file_handler.py      # File persistence logic
│       └── date_parser.py       # Flexible date parsing utility
│
tests/
├── unit/
│   ├── test_task.py             # Unit tests for Task model
│   ├── test_task_model.py       # Enhanced Task model tests
│   ├── test_task_service.py     # Unit tests for task service
│   ├── test_search_service.py   # Search service tests
│   ├── test_filter_service.py   # Filter service tests
│   ├── test_sort_service.py     # Sort service tests
│   ├── test_validation_service.py # Validation tests
│   └── test_date_parser.py      # Date parser tests
├── integration/
│   ├── test_cli_integration.py  # CLI integration tests
│   ├── test_cli_commands.py     # Enhanced CLI command tests
│   ├── test_task_operations.py  # Task operations with new fields
│   └── test_search_filter_integration.py # Combined search/filter tests
└── contract/
    ├── test_api_contract.py     # Contract tests for CLI interface
    └── test_backward_compatibility.py # Backward compatibility tests
```

## Testing

Run the tests using pytest:

```bash
pytest
```

To run tests with verbose output:

```bash
pytest -v
```

To run specific test files:

```bash
# Unit tests
pytest tests/unit/test_task_model.py
pytest tests/unit/test_search_service.py
pytest tests/unit/test_filter_service.py
pytest tests/unit/test_sort_service.py

# Integration tests
pytest tests/integration/test_task_operations.py
pytest tests/integration/test_cli_commands.py
pytest tests/integration/test_search_filter_integration.py

# Contract tests
pytest tests/contract/test_backward_compatibility.py
```

To run tests with coverage:

```bash
pytest --cov=src/ticklisto --cov-report=html
```

### Test Coverage

The project maintains comprehensive test coverage:
- **Unit Tests**: 75+ tests covering all services and models
- **Integration Tests**: End-to-end testing of CLI commands and workflows
- **Contract Tests**: Backward compatibility verification
- **Total Coverage**: 163+ passing tests

## Performance

The application is optimized for responsive performance:

- **Search**: < 500ms for up to 10,000 tasks
- **Filter**: < 300ms for up to 10,000 tasks
- **Sort**: < 500ms for up to 10,000 tasks
- **Task Operations**: Sub-second response for all CRUD operations

## Data Persistence

The application stores tasks in memory during runtime and persists them to a file named `ticklisto_data.json` when exiting. The file is automatically loaded when the application starts.

### Data Format

Tasks are stored with the following fields:
- `id`: Unique task identifier
- `title`: Task title (max 200 characters)
- `description`: Optional description (max 1000 characters)
- `completed`: Boolean completion status
- `priority`: Priority level (high/medium/low)
- `categories`: List of category tags
- `due_date`: Optional due date (ISO format)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Backward Compatibility

The application maintains full backward compatibility with existing task data. Tasks created without priority, categories, or due dates will automatically receive default values:
- Priority: `medium`
- Categories: `[]` (empty list)
- Due date: `None`

## License

This project is part of a hackathon and is provided as-is for educational purposes.

This project is for educational purposes only.

**READ ONLY - DO NOT COPY**
Any use of this project's code, ideas, or concepts must include proper attribution and credit to the original authors. If you use any part of this project or draw inspiration from it, please clearly reference this repository and provide appropriate credit in your work.
