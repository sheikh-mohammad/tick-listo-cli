# Contract: Recurring Task Service

**Service**: RecurringTaskService
**Purpose**: Manage recurring task series and auto-rescheduling
**Dependencies**: StorageService, TimeZoneService

## Interface Definition

### Class: RecurringTaskService

**Responsibility**: Create and manage recurring task series, generate next instances on completion, and handle series-wide operations.

## Methods

### `__init__(storage_service: StorageService, time_zone_service: TimeZoneService)`

**Description**: Initialize recurring task service with required dependencies.

**Parameters**:
- `storage_service` (StorageService): Service for persisting tasks and series
- `time_zone_service` (TimeZoneService): Service for time zone conversions

**Example**:
```python
service = RecurringTaskService(
    storage_service=storage_service,
    time_zone_service=tz_service
)
```

---

### `create_recurring_task(task: Task) -> RecurringSeries`

**Description**: Create a new recurring task series from a task with recurrence configuration.

**Parameters**:
- `task` (Task): Task with recurrence_pattern, recurrence_interval, and optional recurrence_weekdays set

**Returns**:
- `RecurringSeries`: Created series object

**Raises**:
- `ValueError`: If task has no recurrence_pattern set
- `ValueError`: If recurrence_interval < 1
- `ValueError`: If recurrence_weekdays invalid for pattern

**Side Effects**:
- Generates unique series_id (UUID)
- Sets task.series_id and task.instance_number = 1
- Saves series to storage
- Returns series object

**Example**:
```python
task.recurrence_pattern = RecurrencePattern.WEEKLY
task.recurrence_interval = 1
series = service.create_recurring_task(task)
# series_id assigned, task is first instance
```

---

### `complete_instance_and_generate_next(task: Task) -> Task`

**Description**: Mark current instance as complete and generate the next instance in the series.

**Parameters**:
- `task` (Task): Completed task instance from a recurring series

**Returns**:
- `Task`: Newly created next instance

**Raises**:
- `ValueError`: If task is not part of a recurring series (no series_id)
- `ValueError`: If series not found

**Business Rules**:
- Next due date calculated from original due date + recurrence interval
- New instance inherits: title, description, priority, categories, recurrence settings, reminder settings
- New instance gets: series_id (same), instance_number (incremented), status=PENDING, completed=False
- Original task moved to completed_instance_ids in series
- New task added to active_instance_ids in series
- If recurrence_end_date reached, no new instance created

**Example**:
```python
# User completes weekly task due Monday
completed_task.due_date = datetime(2026, 2, 10)  # Monday
next_task = service.complete_instance_and_generate_next(completed_task)
# next_task.due_date = datetime(2026, 2, 17)  # Next Monday
```

---

### `calculate_next_due_date(current_due_date: datetime, pattern: RecurrencePattern, interval: int, weekdays: list[int] = None) -> datetime`

**Description**: Calculate the next occurrence date based on recurrence pattern.

**Parameters**:
- `current_due_date` (datetime): Current due date (with time)
- `pattern` (RecurrencePattern): Recurrence pattern type
- `interval` (int): Interval multiplier (e.g., 2 for "every 2 weeks")
- `weekdays` (list[int], optional): Specific weekdays for custom patterns (0=Mon, 6=Sun)

**Returns**:
- `datetime`: Next occurrence date/time

**Algorithm by Pattern**:

**DAILY**:
```python
return current_due_date + timedelta(days=interval)
```

**WEEKLY**:
```python
if weekdays:
    # Find next occurrence on specified weekdays
    # e.g., [0, 2, 4] = Mon/Wed/Fri
    return find_next_weekday_occurrence(current_due_date, weekdays, interval)
else:
    return current_due_date + timedelta(weeks=interval)
```

**MONTHLY**:
```python
# Handle month-end edge cases
next_month = current_due_date.month + interval
next_year = current_due_date.year + (next_month - 1) // 12
next_month = ((next_month - 1) % 12) + 1

# Handle day overflow (e.g., Jan 31 -> Feb 28)
try:
    return current_due_date.replace(year=next_year, month=next_month)
except ValueError:
    # Day doesn't exist in target month, use last day
    return last_day_of_month(next_year, next_month, current_due_date.time())
```

**YEARLY**:
```python
# Handle leap year edge case (Feb 29)
next_year = current_due_date.year + interval
try:
    return current_due_date.replace(year=next_year)
except ValueError:
    # Feb 29 in non-leap year -> Feb 28
    return current_due_date.replace(year=next_year, day=28)
```

**Edge Cases Handled**:
- Month-end dates (Jan 31 -> Feb 28/29)
- Leap years (Feb 29 -> Feb 28 in non-leap years)
- DST transitions (maintains local time)
- Weekday-specific recurrence (Mon/Wed/Fri)

**Example**:
```python
# Weekly on Mon/Wed/Fri
current = datetime(2026, 2, 9)  # Monday
weekdays = [0, 2, 4]  # Mon, Wed, Fri
next_date = service.calculate_next_due_date(current, RecurrencePattern.WEEKLY, 1, weekdays)
# Returns: datetime(2026, 2, 11)  # Wednesday
```

---

### `update_series(series_id: str, update_future: bool, **updates) -> int`

**Description**: Update recurring task series and optionally all future instances.

**Parameters**:
- `series_id` (str): UUID of the series
- `update_future` (bool): If True, update all future instances; if False, only update series template
- `**updates`: Field updates (title, description, priority, categories, reminder_settings, etc.)

**Returns**:
- `int`: Number of task instances updated

**Business Rules**:
- If update_future=False: Only updates series template (affects next generated instances)
- If update_future=True: Updates all active (non-completed) instances in the series
- Completed instances are never updated
- Cannot change recurrence_pattern or series_id

**Example**:
```python
# Update all future instances
count = service.update_series(
    series_id="550e8400-e29b-41d4-a716-446655440000",
    update_future=True,
    priority=Priority.HIGH,
    reminder_settings=[ReminderSetting(offset_minutes=1440)]
)
print(f"Updated {count} future instances")
```

---

### `stop_recurrence(series_id: str, delete_future: bool = False) -> int`

**Description**: Stop a recurring series from generating new instances.

**Parameters**:
- `series_id` (str): UUID of the series
- `delete_future` (bool): If True, delete all future (non-completed) instances

**Returns**:
- `int`: Number of future instances deleted (if delete_future=True)

**Side Effects**:
- Sets series as inactive (no new instances generated)
- If delete_future=True: Deletes all active instances, cancels their reminders
- If delete_future=False: Keeps existing instances, just stops generating new ones
- Completed instances always preserved

**Example**:
```python
# Stop recurrence but keep existing future instances
service.stop_recurrence(series_id, delete_future=False)

# Stop recurrence and delete all future instances
deleted_count = service.stop_recurrence(series_id, delete_future=True)
```

---

### `get_series(series_id: str) -> RecurringSeries`

**Description**: Retrieve a recurring series by ID.

**Parameters**:
- `series_id` (str): UUID of the series

**Returns**:
- `RecurringSeries`: Series object

**Raises**:
- `ValueError`: If series not found

**Example**:
```python
series = service.get_series("550e8400-e29b-41d4-a716-446655440000")
print(f"Pattern: {series.recurrence_pattern}, Active: {len(series.active_instance_ids)}")
```

---

### `get_series_instances(series_id: str, include_completed: bool = False) -> list[Task]`

**Description**: Get all task instances in a recurring series.

**Parameters**:
- `series_id` (str): UUID of the series
- `include_completed` (bool): If True, include completed instances

**Returns**:
- `list[Task]`: List of task instances sorted by instance_number

**Example**:
```python
# Get only active instances
active_tasks = service.get_series_instances(series_id, include_completed=False)

# Get all instances including completed
all_tasks = service.get_series_instances(series_id, include_completed=True)
```

---

### `is_series_active(series_id: str) -> bool`

**Description**: Check if a recurring series is still active (generating new instances).

**Parameters**:
- `series_id` (str): UUID of the series

**Returns**:
- `bool`: True if series is active, False if stopped or end date reached

**Example**:
```python
if service.is_series_active(series_id):
    print("Series will continue generating instances")
```

## Data Structures

### RecurringSeries Storage

Stored in `ticklisto_data.json` under `recurring_series` key:

```json
{
  "tasks": [...],
  "next_id": 10,
  "recurring_series": [
    {
      "series_id": "550e8400-e29b-41d4-a716-446655440000",
      "base_task_id": 1,
      "recurrence_pattern": "weekly",
      "recurrence_interval": 1,
      "recurrence_weekdays": null,
      "recurrence_end_date": null,
      "active_instance_ids": [1, 5, 9],
      "completed_instance_ids": [2, 3, 4, 6, 7, 8],
      "created_at": "2026-02-08T10:00:00Z",
      "last_generated_at": "2026-02-08T15:00:00Z",
      "is_active": true
    }
  ]
}
```

## Business Rules

### Instance Generation
1. New instance created only when current instance marked complete
2. Next due date calculated from original due date (not completion date)
3. If recurrence_end_date set and next date > end date, no instance created
4. Instance inherits all properties except: id, status, completed, created_at, updated_at

### Series Lifecycle
1. Created when user creates first recurring task
2. Generates instances on completion until stopped or end date reached
3. Maintains history of completed instances (limited to last 100)
4. Can be stopped manually or automatically (end date)

### Weekday Recurrence
- Weekdays represented as integers: 0=Monday, 1=Tuesday, ..., 6=Sunday
- For custom weekly patterns with specific weekdays (e.g., Mon/Wed/Fri):
  - Next occurrence is the next matching weekday
  - Respects interval (e.g., every 2 weeks on Mon/Wed/Fri)

## Performance Considerations

- Series lookup by series_id: O(1) with in-memory index
- Instance generation: O(1) for date calculation
- Series update (all future): O(n) where n = number of active instances
- Memory: ~500 bytes per series, ~50KB for 100 series

## Testing Strategy

### Unit Tests
```python
def test_calculate_next_due_date_weekly():
    current = datetime(2026, 2, 10)  # Monday
    next_date = service.calculate_next_due_date(
        current, RecurrencePattern.WEEKLY, 1
    )
    assert next_date == datetime(2026, 2, 17)  # Next Monday

def test_calculate_next_due_date_monthly_edge_case():
    current = datetime(2026, 1, 31)  # Jan 31
    next_date = service.calculate_next_due_date(
        current, RecurrencePattern.MONTHLY, 1
    )
    assert next_date == datetime(2026, 2, 28)  # Feb 28 (no Feb 31)

def test_complete_instance_generates_next():
    task = create_recurring_task_weekly()
    next_task = service.complete_instance_and_generate_next(task)
    assert next_task.series_id == task.series_id
    assert next_task.instance_number == task.instance_number + 1
    assert next_task.due_date == task.due_date + timedelta(weeks=1)
```

### Integration Tests
```python
@pytest.mark.integration
def test_recurring_series_lifecycle():
    # Create series
    task = create_task_with_recurrence()
    series = service.create_recurring_task(task)

    # Complete and generate 3 instances
    for i in range(3):
        task = service.complete_instance_and_generate_next(task)

    # Verify series state
    series = service.get_series(series.series_id)
    assert len(series.completed_instance_ids) == 3
    assert len(series.active_instance_ids) == 1
```

## Contract Validation

**Pre-conditions**:
- StorageService initialized and functional
- TimeZoneService configured with user's time zone
- Tasks have valid recurrence configuration

**Post-conditions**:
- Series persisted to storage
- All instances linked via series_id
- Next instance generated on completion
- Completed instances tracked in series

**Invariants**:
- series_id unique across all series
- instance_number sequential within series
- Next due date always >= current due date
- Completed instances never modified
- Active instances count matches active_instance_ids length
