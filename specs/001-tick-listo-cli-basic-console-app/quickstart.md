# Quickstart Guide: Tick Listo Basic Console App

**Feature**: Tick Listo Basic Console App (Phase I)
**Date**: 2026-01-28

## Overview

This guide provides step-by-step instructions to get started with the Phase I Tick Listo Basic Console App, including installation, setup, and basic usage.

## Prerequisites

- Python 3.13+ installed
- UV package manager installed
- Git for version control (optional for local development)

## Installation

### 1. Clone or Create Project
```bash
# If starting fresh
mkdir Phase_I
cd Phase_I
uv init .
```

### 2. Add Dependencies
```bash
# Install Rich for CLI formatting
uv add rich

# Install Pytest for testing
uv add pytest --dev
```

### 3. Project Structure
After initialization, your project should look like this:
```
Phase_I/
├── src/
│   └── ticklisto/
├── tests/
├── pyproject.toml
├── uv.lock
└── README.md
```

## Setup

### 1. Initialize the Project
```bash
# Navigate to your project directory
cd Phase_I

# Initialize with UV (creates pyproject.toml)
uv init .

# Add the required dependencies
uv add rich pytest --dev
```

### 2. Create Directory Structure
```bash
# Create the source directory structure
mkdir -p src/ticklisto/{models,services,cli,utils}
touch src/ticklisto/__init__.py
touch src/ticklisto/models/__init__.py
touch src/ticklisto/services/__init__.py
touch src/ticklisto/cli/__init__.py
touch src/ticklisto/utils/__init__.py
```

## Running the Application

### 1. Start the Console Application
```bash
# Run the main application
python -m src.ticklisto.cli.todo_cli
```

### 2. Using the Interactive CLI
Once the application starts, you'll see the main prompt where you can enter commands:

```
Todo App >
```

## Available Commands

### Main Commands
- `add` or `a` - Add a new task
- `view` or `v` - View all tasks
- `update` or `u` - Update a task
- `delete` or `d` - Delete a task
- `complete` or `c` - Mark task as complete/incomplete
- `quit` or `q` - Exit the application

### Command Usage Examples

#### Adding a Task
```
Todo App > add
Title: Buy groceries
Description: Need to buy milk, bread, and eggs
Task added successfully with ID: 1
```

Alternative with single-letter command:
```
Todo App > a
Title: Walk the dog
Description: Take the dog for a 30-minute walk
Task added successfully with ID: 2
```

#### Viewing Tasks
```
Todo App > view
┌─────┬────────────────┬──────────────────────────────────────┬──────────┐
│  ID │ Title          │ Description                          │ Status   │
├─────┼────────────────┼──────────────────────────────────────┼──────────┤
│   1 │ Buy groceries  │ Need to buy milk, bread, and eggs    │ Pending  │
│   2 │ Walk the dog   │ Take the dog for a 30-minute walk    │ Pending  │
└─────┴────────────────┴──────────────────────────────────────┴──────────┘
```

#### Updating a Task
```
Todo App > update
Task ID: 1
New title (leave blank to keep current): Buy weekly groceries
New description (leave blank to keep current): Need to buy milk, bread, eggs, and vegetables
Task updated successfully!
```

#### Marking Complete
```
Todo App > complete
Task ID: 1
Mark as complete (y/n): y
Task marked as complete!
```

#### Deleting a Task
```
Todo App > delete
Task ID: 2
Are you sure you want to delete this task? (y/n): y
Task deleted successfully!
```

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_task.py
```

### Project Structure Reference
```
src/
├── ticklisto/
│   ├── models/
│   │   └── task.py          # Task data model
│   ├── services/
│   │   └── task_service.py  # Business logic for task operations
│   ├── cli/
│   │   └── todo_cli.py      # Command-line interface
│   └── utils/
│       └── file_handler.py  # File persistence logic
```

## Configuration

The application uses temporary file persistence by default. The data is stored in a file called `todo_data.json` in the project root directory.

## Troubleshooting

### Common Issues

1. **Module not found errors**: Make sure you're running the application from the project root directory
2. **Permission errors**: Ensure the application has write permissions for the data file
3. **Rich formatting not displaying**: Some terminals may not support all Rich features; try a different terminal

### Getting Help
If you encounter issues, try running:
```bash
python -m src.ticklisto.cli.todo_cli --help
```
