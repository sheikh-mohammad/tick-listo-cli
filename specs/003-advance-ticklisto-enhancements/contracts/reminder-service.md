# Contract: Reminder Service

**Service**: ReminderService
**Purpose**: Background service for checking and sending task reminders
**Dependencies**: GmailService, TimeZoneService, StorageService

## Interface Definition

### Class: ReminderService

**Responsibility**: Monitor tasks for pending reminders, send emails at scheduled times, handle failures with exponential backoff, and manage daily digest.

## Methods

### `__init__(gmail_service: GmailService, storage_service: StorageService, time_zone_service: TimeZoneService)`

**Description**: Initialize reminder service with required dependencies.

**Parameters**:
- `gmail_service` (GmailService): Service for sending emails
- `storage_service` (StorageService): Service for loading/saving reminders
- `time_zone_service` (TimeZoneService): Service for time zone conversions

**Example**:
```python
service = ReminderService(
    gmail_service=gmail_service,
    storage_service=storage_service,
    time_zone_service=tz_service
)
```

---

### `start() -> None`

**Description**: Start the background reminder checking thread.

**Side Effects**:
- Spawns daemon thread that runs `_check_loop()`
- Loads pending reminders from storage
- Sends any overdue reminders immediately

**Raises**:
- `RuntimeError`: If service is already running

**Example**:
```python
service.start()
# Service now checks reminders every 1 minute
```

---

### `stop() -> None`

**Description**: Stop the background reminder checking thread gracefully.

**Side Effects**:
- Sets running flag to False
- Waits up to 5 seconds for thread to terminate
- Saves pending reminders to storage

**Example**:
```python
service.stop()
# Service stopped, thread terminated
```

---

### `schedule_reminders(task: Task) -> list[EmailReminder]`

**Description**: Create and schedule email reminders for a task based on its reminder_settings.

**Parameters**:
- `task` (Task): Task with reminder_settings configured

**Returns**:
- `list[EmailReminder]`: List of created reminder objects

**Raises**:
- `ValueError`: If task has no due_time but has reminder_settings
- `ValueError`: If reminder offset would result in past scheduled time

**Business Rules**:
- Only creates reminders if task has due_time set
- Calculates scheduled_time = due_datetime - offset_minutes
- Skips reminders with scheduled_time in the past
- Each reminder_setting creates one EmailReminder

**Example**:
```python
task.reminder_settings = [
    ReminderSetting(offset_minutes=60, label="1 hour before"),
    ReminderSetting(offset_minutes=1440, label="1 day before")
]
reminders = service.schedule_reminders(task)
# Creates 2 EmailReminder objects
```

---

### `cancel_reminders(task_id: int) -> int`

**Description**: Cancel all pending reminders for a task (when task is completed or deleted).

**Parameters**:
- `task_id` (int): ID of the task

**Returns**:
- `int`: Number of reminders cancelled

**Side Effects**:
- Updates reminder status to CANCELLED
- Removes from pending reminder queue

**Example**:
```python
cancelled_count = service.cancel_reminders(task_id=5)
print(f"Cancelled {cancelled_count} reminders")
```

---

### `get_pending_reminders() -> list[EmailReminder]`

**Description**: Get all pending reminders sorted by scheduled time.

**Returns**:
- `list[EmailReminder]`: List of pending reminders

**Example**:
```python
pending = service.get_pending_reminders()
for reminder in pending:
    print(f"Task {reminder.task_id} reminder at {reminder.scheduled_time}")
```

---

### `get_next_check_time() -> datetime`

**Description**: Get the timestamp of the next reminder check.

**Returns**:
- `datetime`: UTC timestamp of next check (current_time + 1 minute)

**Example**:
```python
next_check = service.get_next_check_time()
print(f"Next check at {next_check}")
```

---

### `get_status() -> dict`

**Description**: Get current service status and statistics.

**Returns**:
- `dict`: Status information including:
  - `running` (bool): Whether service is running
  - `last_check_time` (datetime): Last reminder check timestamp
  - `next_check_time` (datetime): Next scheduled check
  - `pending_count` (int): Number of pending reminders
  - `failed_count` (int): Number of failed reminders in digest queue
  - `sent_today` (int): Number of reminders sent today

**Example**:
```python
status = service.get_status()
print(f"Pending: {status['pending_count']}, Failed: {status['failed_count']}")
```

---

### `_check_loop() -> None` (Private)

**Description**: Main loop that runs in background thread, checking for reminders every 1 minute.

**Algorithm**:
```
while running:
    1. Get current time (UTC)
    2. Find reminders with scheduled_time <= current_time
    3. For each due reminder:
       - Attempt to send via GmailService
       - On success: mark as SENT
       - On failure: retry with exponential backoff
       - After 3 failures: add to daily digest queue
    4. Check if daily digest should be sent (8 AM user time)
    5. Sleep for 60 seconds
```

**Error Handling**:
- Catches all exceptions to prevent thread crash
- Logs errors for monitoring
- Continues checking even if individual sends fail

---

### `_send_reminder(reminder: EmailReminder) -> bool` (Private)

**Description**: Send a single reminder email with retry logic.

**Parameters**:
- `reminder` (EmailReminder): Reminder to send

**Returns**:
- `bool`: True if sent successfully, False otherwise

**Algorithm**:
```
for attempt in range(3):
    try:
        task = load_task(reminder.task_id)
        success = gmail_service.send_reminder_email(task, reminder.offset_minutes)
        if success:
            reminder.status = SENT
            reminder.sent_time = now()
            return True
    except RateLimitError as e:
        wait_time = (2 ** attempt) + random.uniform(0, 1)
        sleep(wait_time)
        reminder.retry_count += 1
    except Exception as e:
        log_error(e)
        reminder.retry_count += 1

reminder.status = FAILED
return False
```

---

### `_send_daily_digest() -> bool` (Private)

**Description**: Send daily digest email with all failed reminders.

**Returns**:
- `bool`: True if digest sent successfully, False otherwise

**Business Rules**:
- Only sends if failed_reminders list is not empty
- Sends at 8:00 AM in user's configured time zone
- Clears digest queue after successful send
- Logs failure if digest send fails

**Example Digest Content**:
```
Subject: Daily Task Reminder Digest - 2026-02-08

You have 3 pending task reminders:

1. [HIGH] Weekly team meeting
   Due: Feb 10, 2026 at 2:30 PM

2. [MEDIUM] Submit report
   Due: Feb 09, 2026 at 5:00 PM

3. [LOW] Review documentation
   Due: Feb 11, 2026 at 10:00 AM
```

## State Management

### Reminder Queue
- In-memory priority queue sorted by scheduled_time
- Persisted to reminders.json on service stop
- Loaded from reminders.json on service start

### Daily Digest Queue
- Separate list for failed reminders
- Cleared after successful digest send
- Persisted across restarts

## Threading Model

**Thread Type**: Daemon thread
**Check Interval**: 60 seconds (1 minute)
**Graceful Shutdown**: 5 second timeout

**Thread Safety**:
- Use `threading.Lock` for shared state access
- Queue operations are thread-safe
- Storage writes are atomic

## Error Handling

### Retry Strategy

```python
def exponential_backoff(attempt: int) -> float:
    """Calculate wait time with jitter."""
    base_wait = 2 ** attempt  # 1s, 2s, 4s
    jitter = random.uniform(0, 1)
    return min(base_wait + jitter, 60)  # Cap at 60s
```

### Failure Scenarios

| Error | Retry | Fallback |
|-------|-------|----------|
| RateLimitError | Yes (3x) | Daily digest |
| AuthenticationError | Token refresh | Daily digest |
| NetworkError | Yes (3x) | Daily digest |
| TaskNotFound | No | Cancel reminder |

## Performance Requirements

- Reminder check latency: <100ms for 10,000 tasks
- Email send: <2 seconds per reminder
- Memory usage: <50MB for 10,000 pending reminders
- Thread overhead: <1% CPU when idle

## Testing Strategy

### Unit Tests
```python
def test_schedule_reminders():
    task = create_task_with_reminders()
    reminders = service.schedule_reminders(task)
    assert len(reminders) == 2
    assert reminders[0].scheduled_time < task.due_datetime

def test_cancel_reminders():
    service.schedule_reminders(task)
    count = service.cancel_reminders(task.id)
    assert count == 2
    assert len(service.get_pending_reminders()) == 0
```

### Integration Tests
```python
@pytest.mark.integration
def test_reminder_sent_at_scheduled_time():
    task = create_task_due_in_minutes(2)
    service.schedule_reminders(task)
    service.start()
    time.sleep(130)  # Wait for check cycle
    reminders = service.get_pending_reminders()
    assert all(r.status == SENT for r in reminders)
```

## Contract Validation

**Pre-conditions**:
- GmailService initialized and authenticated
- StorageService available for persistence
- TimeZoneService configured with user's time zone

**Post-conditions**:
- All due reminders sent or queued for digest
- Service state persisted to storage
- Thread terminated gracefully on stop

**Invariants**:
- Reminder scheduled_time never in the past
- Each task reminder sent at most once
- Failed reminders always added to digest queue
- Service never crashes due to individual failures
