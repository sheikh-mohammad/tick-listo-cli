# Data Model: Advanced Ticklisto Enhancements

**Feature**: 003-advance-ticklisto-enhancements
**Date**: 2026-02-08
**Phase**: 1 - Design & Contracts

## Overview

This document defines the data model for recurring tasks, time-based reminders, and email notifications. All entities extend or integrate with the existing Ticklisto data model while maintaining backward compatibility.

## Core Entities

### 1. Task (Enhanced)

**Description**: Extended task entity with time support, recurrence configuration, and reminder settings.

**Attributes**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | int | Yes | Auto-increment | Unique task identifier |
| title | str | Yes | - | Task title (max 200 chars) |
| description | str | No | "" | Task description (max 1000 chars) |
| completed | bool | No | False | Completion status |
| priority | Priority | No | MEDIUM | Priority level (HIGH/MEDIUM/LOW) |
| categories | list[str] | No | [] | Category tags |
| due_date | datetime | No | None | Due date (existing field) |
| **due_time** | **time** | **No** | **None** | **NEW: Time component (HH:MM)** |
| status | TaskStatus | No | PENDING | Task status enum |
| **recurrence_pattern** | **RecurrencePattern** | **No** | **None** | **NEW: Recurrence type (daily/weekly/monthly/yearly/custom)** |
| **recurrence_interval** | **int** | **No** | **1** | **NEW: Interval multiplier for custom recurrence** |
| **recurrence_weekdays** | **list[int]** | **No** | **None** | **NEW: Weekdays for custom patterns (0=Mon, 6=Sun)** |
| **recurrence_end_date** | **datetime** | **No** | **None** | **NEW: Optional end date for recurring series** |
| **series_id** | **str** | **No** | **None** | **NEW: UUID linking recurring task instances** |
| **instance_number** | **int** | **No** | **None** | **NEW: Position in recurring series (1, 2, 3...)** |
| **reminder_settings** | **list[ReminderSetting]** | **No** | **[]** | **NEW: List of reminder configurations** |
| created_at | datetime | Yes | now() | Creation timestamp |
| updated_at | datetime | Yes | now() | Last update timestamp |

**Validation Rules**:
- title: Non-empty, max 200 characters
- description: Max 1000 characters
- categories: Each max 50 characters, normalized to lowercase
- due_time: Required if reminder_settings is not empty
- recurrence_interval: Must be >= 1 if recurrence_pattern is set
- recurrence_weekdays: Valid only for weekly custom patterns, values 0-6
- instance_number: Must be >= 1 if series_id is set

**State Transitions**:
```
PENDING -> IN_PROGRESS -> COMPLETED
         -> COMPLETED (direct)
```

**Relationships**:
- One Task belongs to zero or one RecurringSeries (via series_id)
- One Task has zero or many ReminderSettings
- One Task generates zero or many EmailReminders

**Backward Compatibility**:
- All new fields are optional with None/empty defaults
- Existing tasks without new fields continue to function
- Serialization includes all fields; deserialization handles missing fields

### 2. RecurrencePattern (Enum)

**Description**: Enumeration of supported recurrence patterns.

**Values**:
```python
class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BI_WEEKLY = "bi-weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"
```

### 3. ReminderSetting (Value Object)

**Description**: Configuration for a single reminder time relative to task due date/time.

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| offset_minutes | int | Yes | Minutes before due time to send reminder (e.g., 60 = 1 hour before) |
| label | str | No | Human-readable label (e.g., "1 hour before", "1 day before") |

**Validation Rules**:
- offset_minutes: Must be > 0
- Common values: 15 (15 min), 60 (1 hour), 1440 (1 day), 10080 (1 week)

**Example**:
```python
ReminderSetting(offset_minutes=60, label="1 hour before")
ReminderSetting(offset_minutes=1440, label="1 day before")
```

### 4. EmailReminder (Entity)

**Description**: Represents a scheduled email reminder for a task.

**Attributes**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | str | Yes | UUID | Unique reminder identifier |
| task_id | int | Yes | - | Associated task ID |
| scheduled_time | datetime | Yes | - | When to send reminder (UTC) |
| offset_minutes | int | Yes | - | Minutes before due time |
| status | ReminderStatus | Yes | PENDING | Reminder status |
| retry_count | int | Yes | 0 | Number of send attempts |
| last_attempt_time | datetime | No | None | Timestamp of last send attempt |
| error_message | str | No | None | Error from last failed attempt |
| sent_time | datetime | No | None | Timestamp when successfully sent |

**Validation Rules**:
- scheduled_time: Must be in the future when created
- retry_count: Max 3 attempts
- status: PENDING -> SENDING -> SENT or FAILED

**State Transitions**:
```
PENDING -> SENDING -> SENT
                   -> FAILED (after 3 retries)
                   -> PENDING (retry with backoff)
```

**Lifecycle**:
1. Created when task with reminder_settings is saved
2. Checked every 1 minute by ReminderService
3. Sent when scheduled_time <= current_time
4. Retried with exponential backoff on failure
5. Moved to daily digest queue after 3 failures
6. Deleted when task is completed or deleted

### 5. ReminderStatus (Enum)

**Description**: Status of an email reminder.

**Values**:
```python
class ReminderStatus(str, Enum):
    PENDING = "pending"      # Scheduled, not yet sent
    SENDING = "sending"      # Currently being sent
    SENT = "sent"           # Successfully delivered
    FAILED = "failed"       # Failed after max retries
    CANCELLED = "cancelled"  # Task completed/deleted
```

### 6. RecurringSeries (Entity)

**Description**: Represents a series of recurring task instances.

**Attributes**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| series_id | str | Yes | UUID | Unique series identifier |
| base_task_id | int | Yes | - | ID of the original/template task |
| recurrence_pattern | RecurrencePattern | Yes | - | Pattern for recurrence |
| recurrence_interval | int | Yes | 1 | Interval multiplier |
| recurrence_weekdays | list[int] | No | None | Specific weekdays for custom patterns |
| recurrence_end_date | datetime | No | None | Optional end date for series |
| active_instance_ids | list[int] | Yes | [] | IDs of current/future task instances |
| completed_instance_ids | list[int] | Yes | [] | IDs of completed task instances |
| created_at | datetime | Yes | now() | Series creation timestamp |
| last_generated_at | datetime | Yes | now() | When last instance was created |

**Validation Rules**:
- series_id: Must be unique across all series
- recurrence_interval: Must be >= 1
- recurrence_weekdays: Valid only for weekly patterns
- active_instance_ids: All must reference existing tasks with matching series_id

**Operations**:
- `create_next_instance()`: Generate next task instance based on pattern
- `stop_recurrence()`: Prevent future instances from being created
- `update_all_future()`: Apply changes to all future instances
- `get_next_due_date()`: Calculate next occurrence date

**Lifecycle**:
1. Created when user creates a recurring task
2. Generates first task instance with series_id
3. When instance is completed, generates next instance
4. Continues until recurrence_end_date or manually stopped
5. Maintains history of completed instances (limited to last 100)

### 7. DailyDigest (Value Object)

**Description**: Aggregates failed reminders for daily digest email.

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| date | date | Yes | Date of digest (YYYY-MM-DD) |
| failed_reminders | list[EmailReminder] | Yes | Reminders that failed after 3 retries |
| scheduled_send_time | datetime | Yes | 8:00 AM in user's time zone |
| sent | bool | Yes | Whether digest has been sent |

**Business Rules**:
- Only created if reminders fail after 3 retry attempts
- Sent at 8:00 AM in user's configured time zone
- Not sent if failed_reminders list is empty
- Cleared after successful send

## Relationships Diagram

```
Task (1) ----< (0..n) EmailReminder
  |
  | (0..1)
  |
  v
RecurringSeries (1) ----< (1..n) Task (instances)

Task (1) ----< (0..n) ReminderSetting (embedded)
```

## Storage Schema (JSON)

### tasks.json
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Weekly team meeting",
      "description": "Discuss project progress",
      "completed": false,
      "priority": "high",
      "categories": ["work", "meetings"],
      "due_date": "2026-02-10T00:00:00Z",
      "due_time": "14:30:00",
      "status": "pending",
      "recurrence_pattern": "weekly",
      "recurrence_interval": 1,
      "recurrence_weekdays": null,
      "recurrence_end_date": null,
      "series_id": "550e8400-e29b-41d4-a716-446655440000",
      "instance_number": 1,
      "reminder_settings": [
        {"offset_minutes": 60, "label": "1 hour before"},
        {"offset_minutes": 1440, "label": "1 day before"}
      ],
      "created_at": "2026-02-08T10:00:00Z",
      "updated_at": "2026-02-08T10:00:00Z"
    }
  ],
  "recurring_series": [
    {
      "series_id": "550e8400-e29b-41d4-a716-446655440000",
      "base_task_id": 1,
      "recurrence_pattern": "weekly",
      "recurrence_interval": 1,
      "recurrence_weekdays": null,
      "recurrence_end_date": null,
      "active_instance_ids": [1],
      "completed_instance_ids": [],
      "created_at": "2026-02-08T10:00:00Z",
      "last_generated_at": "2026-02-08T10:00:00Z"
    }
  ]
}
```

### reminders.json (transient state)
```json
{
  "reminders": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "task_id": 1,
      "scheduled_time": "2026-02-10T13:30:00Z",
      "offset_minutes": 60,
      "status": "pending",
      "retry_count": 0,
      "last_attempt_time": null,
      "error_message": null,
      "sent_time": null
    }
  ],
  "daily_digest": {
    "date": "2026-02-08",
    "failed_reminders": [],
    "scheduled_send_time": "2026-02-08T13:00:00Z",
    "sent": false
  }
}
```

### config.json
```json
{
  "time_zone": "America/New_York",
  "default_reminder_offset": 3600,
  "email_recipient": "haji08307@gmail.com",
  "daily_digest_time": "08:00"
}
```

## Migration Strategy

### Backward Compatibility
1. All new Task fields are optional with None/empty defaults
2. Existing tasks load successfully without new fields
3. Serialization includes all fields; missing fields default on load
4. Old task format continues to work indefinitely

### Data Migration
- No migration required for existing tasks
- New fields added on first save after upgrade
- Existing due_date field preserved and used
- No data loss or corruption risk

## Performance Considerations

### Indexing Strategy
- In-memory index by due_date + due_time for reminder queries
- In-memory index by series_id for recurring task lookups
- Binary search for efficient reminder scheduling

### Memory Limits
- Limit completed_instance_ids to last 100 instances per series
- Clean up sent/cancelled reminders older than 30 days
- Estimated memory: ~1KB per task, ~10MB for 10,000 tasks

### Query Optimization
- Load all tasks into memory on startup (acceptable for 10K tasks)
- Maintain sorted reminder queue for O(log n) insertion
- Cache next reminder check time to avoid unnecessary scans

## Summary

Data model is complete with all entities, relationships, validation rules, and storage schema defined. All entities support the functional requirements from the specification. Ready to proceed with contract definitions.
