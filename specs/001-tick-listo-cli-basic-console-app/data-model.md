# Data Model: Tick Listo Basic Console App

**Feature**: Tick Listo Basic Console App (Phase I)
**Date**: 2026-01-28

## Overview

This document defines the data model for the Phase I Tick Listo Basic Console App, including entity definitions, relationships, validation rules, and state transitions based on the feature requirements.

## Entities

### Task
**Description**: Represents a single todo item with all necessary attributes

**Fields**:
- `id`: Integer (Auto-generated sequential unique identifier)
  - Unique: Yes (auto-generated sequentially)
  - Required: Yes
  - Immutable: Yes (assigned at creation)
- `title`: String (Task title/description in brief)
  - Required: Yes
  - Min length: 1 character
  - Max length: 200 characters
  - Validation: Non-empty after whitespace removal
- `description`: String (Detailed task description)
  - Required: No (can be empty)
  - Max length: 1000 characters
  - Validation: Optional field, can be empty string
- `completed`: Boolean (Completion status indicator)
  - Required: Yes
  - Default: False
  - Values: true/false only
- `created_at`: DateTime (Timestamp of task creation)
  - Required: Yes
  - Format: ISO 8601 format
  - Default: Current timestamp at creation
  - Immutable: Yes (set at creation only)

**Validation Rules**:
1. Title must not be empty (after trimming whitespace)
2. Title length must be between 1-200 characters
3. Description length must not exceed 1000 characters
4. ID must be unique within the task collection
5. Completed status must be boolean (true/false)
6. Created timestamp must be a valid datetime

**State Transitions**:
- `incomplete` → `complete`: When user marks task as complete
- `complete` → `incomplete`: When user marks task as incomplete

### TaskList
**Description**: Collection of tasks managed in memory with CRUD operations

**Operations**:
- `add(task)`: Add a new task to the list
  - Validates task before adding
  - Assigns auto-generated sequential ID
  - Sets creation timestamp
- `get_all()`: Retrieve all tasks in the list
  - Returns ordered list of tasks
  - Maintains insertion order or sorts by ID
- `get_by_id(id)`: Retrieve specific task by ID
  - Returns task if found, None otherwise
  - Validates ID exists in collection
- `update(id, updates)`: Update task properties
  - Validates updates against field constraints
  - Preserves immutable fields (id, created_at)
  - Updates mutable fields (title, description, completed)
- `delete(id)`: Remove task from list
  - Validates ID exists before deletion
  - Returns success/failure status
- `toggle_complete(id)`: Toggle completion status
  - Flips completed boolean value
  - Validates ID exists before toggling

## Relationships

### Task to TaskList
- One-to-many relationship
- Each Task belongs to exactly one TaskList
- TaskList contains zero or more Tasks
- Tasks are uniquely identified within the TaskList by their ID

## Serialization Format

When persisting to temporary file, the data model follows this JSON structure:

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Sample task",
      "description": "Detailed description of the task",
      "completed": false,
      "created_at": "2026-01-28T10:00:00.000000"
    },
    {
      "id": 2,
      "title": "Another task",
      "description": "More details about this task",
      "completed": true,
      "created_at": "2026-01-28T10:05:00.000000"
    }
  ],
  "next_id": 3
}
```

**Fields**:
- `tasks`: Array of serialized Task objects
- `next_id`: Integer representing the next available ID for auto-generation

## Constraints

1. **Uniqueness**: Task IDs must be unique within a single TaskList
2. **Sequential IDs**: New tasks receive the next sequential ID available
3. **Immutability**: Task ID and creation timestamp cannot be modified after creation
4. **Data Integrity**: All validation rules must pass before any CRUD operation
5. **Persistence**: Data model must be serializable to/from JSON format for file persistence
