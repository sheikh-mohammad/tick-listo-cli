# Tick Listo

A command-line task management application with **persistent JSON storage**, **recurring tasks**, **email reminders**, and advanced organization features. Built with Python 3.14+ and Rich for beautiful console formatting.

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
- **Due Dates with Times**: Set deadlines with optional time components (e.g., "2026-02-15 at 2:30 PM")
- **Time Zone Support**: Configure your local time zone for accurate due date/time display
- **Search with Scope**: Find tasks by keyword in title only, description only, or both
- **Filter**: Filter tasks by status, priority, categories, and due dates
- **Sort**: Sort tasks by due date, priority, or alphabetically
- **Delete All**: Remove all tasks at once with confirmation prompt
- **Enhanced Clear**: Properly clear terminal buffer (not just scroll)

### Recurring Tasks
- **Automatic Rescheduling**: Create tasks that repeat on a schedule
- **Flexible Patterns**: Daily, weekly, monthly, or yearly recurrence
- **Custom Intervals**: Every N days/weeks/months/years (e.g., every 2 weeks)
- **Weekday-Specific**: For weekly tasks, specify exact days (e.g., Mon/Wed/Fri)
- **End Dates**: Optionally set when recurrence should stop
- **Instance Management**: Update or delete single instances or all future instances
- **Series Tracking**: View and manage all recurring task series

### Email Reminders
- **Gmail Integration**: Send reminder emails via Gmail API with OAuth 2.0
- **Multiple Reminders**: Set multiple reminder times per task (e.g., 1 hour and 1 day before)
- **Default Reminders**: Automatically apply default reminder offsets from config
- **Background Service**: Reminder service runs in background checking every minute
- **Retry Logic**: Automatic retry with exponential backoff for failed sends
- **Daily Digest**: Receive daily summary of pending reminders at 8 AM
- **Rich Email Content**: HTML-formatted emails with all task details and priority indicators

### Data Persistence
- **JSON Storage**: All tasks saved to `ticklisto_data.json` in the project directory
- **Atomic Writes**: Safe file operations prevent data corruption
- **ID Management**: Task IDs never reused during normal operation
- **ID Reset**: After "delete all", ID counter resets to 1 for fresh start
- **Reminder State**: Reminder queue persisted to `reminders.json`

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

#### Advanced Features
- `reminders` or `rem` - View email reminder service status
- `recurring` or `rec` - List and manage recurring task series
- `timezone` or `tz` - Configure time zone settings

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

## Troubleshooting

### Gmail Authentication Issues

**Problem**: "credentials.json not found" error when starting the application

**Solution**:
1. Email reminders are optional. The application will work without Gmail credentials
2. To enable email reminders:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials file and save it as `credentials.json` in the project root
3. On first use, you'll be prompted to authorize the application in your browser

**Problem**: "Token expired" or authentication errors

**Solution**:
1. Delete the `token.json` file in the project root
2. Restart the application
3. Re-authorize when prompted in your browser
4. The new token will be saved automatically

**Problem**: Reminders not sending

**Solution**:
1. Check reminder service status: `reminders` or `rem` command
2. Verify your email address in `config/config.json` matches your Gmail account
3. Check that tasks have both `due_date` and `due_time` set (reminders require time)
4. Review logs for error messages (if logging is enabled)
5. Ensure Gmail API quota hasn't been exceeded (check Google Cloud Console)

### Reminder Service Issues

**Problem**: Reminder service not starting

**Solution**:
1. Verify `credentials.json` exists in the project root
2. Check that all required packages are installed: `pip install google-api-python-client google-auth google-auth-oauthlib`
3. Restart the application
4. If the issue persists, the application will continue to work without reminders

**Problem**: Reminders sent at wrong time

**Solution**:
1. Check your time zone configuration: `timezone` or `tz` command
2. Verify the time zone is correct (e.g., "America/New_York", not "EST")
3. Update if needed and restart the application
4. Due times are displayed in your local time zone but stored in UTC

**Problem**: Multiple reminder emails for the same task

**Solution**:
1. This is expected if you configured multiple reminder offsets (e.g., 1 hour and 1 day before)
2. To change: update the task and modify reminder settings
3. To disable: remove reminder settings when updating the task

### Time Zone Configuration

**Problem**: Due dates/times showing in wrong time zone

**Solution**:
1. Configure your time zone: `timezone` or `tz` command
2. Use IANA time zone names (e.g., "America/Los_Angeles", "Europe/London", "Asia/Tokyo")
3. Common time zones:
   - US Eastern: `America/New_York`
   - US Pacific: `America/Los_Angeles`
   - US Central: `America/Chicago`
   - UK: `Europe/London`
   - Central Europe: `Europe/Paris`
   - Japan: `Asia/Tokyo`
   - Australia: `Australia/Sydney`
4. Restart the application after changing time zone

**Problem**: "Invalid time zone" error

**Solution**:
1. Use full IANA time zone names, not abbreviations (use "America/New_York", not "EST")
2. Check spelling and capitalization (time zones are case-sensitive)
3. See full list: [IANA Time Zone Database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

### Recurring Task Issues

**Problem**: Next instance not generated after completing recurring task

**Solution**:
1. Verify the task has a recurrence pattern set
2. Check if the series has reached its end date
3. Use `recurring` or `rec` command to view series status
4. If series is inactive, it won't generate new instances

**Problem**: Can't update all future instances

**Solution**:
1. When updating a recurring task, you'll be prompted: "Update this instance only or all future instances?"
2. Select "future" to update all upcoming instances
3. Select "this" to update only the current instance
4. Completed instances are never modified

### General Issues

**Problem**: Application crashes or freezes

**Solution**:
1. Check for corrupted data files: `ticklisto_data.json`, `reminders.json`
2. Backup and delete these files to start fresh (you'll lose existing tasks)
3. Ensure Python 3.14+ is installed: `python --version`
4. Reinstall dependencies: `uv sync` or `pip install -r requirements.txt`

**Problem**: Tasks not persisting after restart

**Solution**:
1. Always exit using `quit` or `q` command (not Ctrl+C)
2. Check file permissions on `ticklisto_data.json`
3. Verify the file exists and is not empty
4. Check disk space availability

**Problem**: Performance degradation with many tasks

**Solution**:
1. The application is tested with 1000+ tasks
2. If experiencing slowness:
   - Use filters to view subsets of tasks
   - Archive completed tasks periodically
   - Consider splitting into multiple data files for different projects

### Configuration Issues

**Problem**: Config file not found

**Solution**:
1. Copy `config/config.example.json` to `config/config.json`
2. Customize settings as needed
3. The application will create default config if missing

**Problem**: Changes to config not taking effect

**Solution**:
1. Restart the application after modifying `config/config.json`
2. Verify JSON syntax is valid (use a JSON validator)
3. Check that field names match exactly (case-sensitive)

### Getting Help

If you encounter issues not covered here:
1. Check the logs (if logging is enabled)
2. Review error messages carefully - they often indicate the solution
3. Verify all prerequisites are installed
4. Try with a fresh data file to rule out data corruption
5. Report issues at: [GitHub Issues](https://github.com/anthropics/claude-code/issues)

## License

This project is part of a hackathon and is provided as-is for educational purposes.
