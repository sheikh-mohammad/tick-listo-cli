# Quickstart Guide: Advanced Ticklisto Enhancements

**Feature**: 003-advance-ticklisto-enhancements
**Date**: 2026-02-08
**Audience**: Developers implementing this feature

## Overview

This guide provides a quick reference for implementing recurring tasks, time-based reminders, and Gmail notifications in Ticklisto. Follow the implementation order to ensure dependencies are satisfied.

## Implementation Order

### Phase 1: Foundation (Data Model & Time Support)

**Goal**: Extend Task model and add time zone support

**Files to Modify/Create**:
1. `src/ticklisto/models/task.py` - Add new fields
2. `src/ticklisto/utils/time_utils.py` - NEW: Time zone utilities
3. `src/ticklisto/utils/config_manager.py` - NEW: Config file management
4. `src/ticklisto/utils/date_parser.py` - Extend for time parsing
5. `src/ticklisto/services/storage_service.py` - Handle new Task fields

**Key Changes**:
- Add optional fields to Task: `due_time`, `recurrence_pattern`, `recurrence_interval`, `recurrence_weekdays`, `recurrence_end_date`, `series_id`, `instance_number`, `reminder_settings`
- Implement time zone conversion utilities (UTC storage, user TZ display)
- Create config.json schema for user preferences
- Extend date parser to handle time formats (24-hour, 12-hour AM/PM, natural language)

**Testing**: Unit tests for Task model validation, time zone conversions, date/time parsing

---

### Phase 2: Recurring Tasks

**Goal**: Implement recurring task series and auto-rescheduling

**Files to Create**:
1. `src/ticklisto/models/recurring_series.py` - NEW: RecurringSeries entity
2. `src/ticklisto/services/recurring_task_service.py` - NEW: Series management
3. `src/ticklisto/services/time_zone_service.py` - NEW: Time zone service

**Files to Modify**:
1. `src/ticklisto/services/task_service.py` - Integrate recurring logic
2. `src/ticklisto/services/storage_service.py` - Store recurring_series data

**Key Features**:
- Create recurring series on task creation
- Calculate next occurrence based on pattern (daily/weekly/monthly/yearly/custom)
- Generate next instance on task completion
- Handle weekday-specific recurrence (Mon/Wed/Fri)
- Support series-wide updates and deletion

**Testing**: Unit tests for date calculations, integration tests for series lifecycle

---

### Phase 3: Gmail Integration

**Goal**: Implement Gmail API integration for sending emails

**Files to Create**:
1. `src/ticklisto/services/gmail_service.py` - NEW: Gmail API wrapper
2. `src/ticklisto/models/reminder.py` - NEW: EmailReminder entity

**Key Features**:
- OAuth 2.0 authentication with token refresh
- Send reminder emails with task details
- Send daily digest emails
- Handle rate limiting with exponential backoff
- Error handling for authentication and network failures

**Testing**: Unit tests with mocked Gmail API, integration tests with real API (limited)

---

### Phase 4: Reminder Service

**Goal**: Implement background reminder checking and sending

**Files to Create**:
1. `src/ticklisto/services/reminder_service.py` - NEW: Background reminder service

**Files to Modify**:
1. `src/ticklisto/__main__.py` - Start reminder service on app launch

**Key Features**:
- Background thread checking reminders every 1 minute
- Schedule reminders based on task reminder_settings
- Send reminders at scheduled times via GmailService
- Retry failed reminders with exponential backoff (max 3 attempts)
- Queue failed reminders for daily digest (8 AM user time)
- Cancel reminders when task completed/deleted

**Testing**: Unit tests for scheduling logic, integration tests for end-to-end flow

---

### Phase 5: CLI & UI Updates

**Goal**: Add CLI commands and UI for new features

**Files to Modify**:
1. `src/ticklisto/cli/ticklisto_cli.py` - Add commands for recurring, reminders, config
2. `src/ticklisto/ui/rich_ui.py` - Display due times, recurrence patterns, reminder status

**New Commands**:
- `ticklisto config timezone <timezone>` - Set user time zone
- `ticklisto add --recurring <pattern>` - Create recurring task
- `ticklisto add --remind <offset>` - Add reminder to task
- `ticklisto status reminders` - Show reminder service status
- `ticklisto series list` - List all recurring series
- `ticklisto series stop <series_id>` - Stop recurring series

**UI Enhancements**:
- Display due date with time (e.g., "Feb 15, 2026 at 2:30 PM")
- Show recurrence indicator (🔁) for recurring tasks
- Display reminder status (⏰ pending, ✅ sent)
- Show next occurrence for recurring tasks

**Testing**: Integration tests for CLI commands, manual UI testing

---

### Phase 6: Documentation

**Goal**: Update README and create user documentation

**Files to Modify**:
1. `README.md` - Add new features section

**Documentation Sections**:
- Recurring Tasks: How to create, manage, and stop recurring tasks
- Due Times: How to set specific times for tasks
- Email Reminders: How to configure reminders and daily digest
- Time Zone Configuration: How to set preferred time zone
- Troubleshooting: Common issues and solutions

---

## Quick Reference

### Storage Schema

**ticklisto_data.json**:
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Weekly meeting",
      "due_date": "2026-02-10T00:00:00Z",
      "due_time": "14:30:00",
      "recurrence_pattern": "weekly",
      "recurrence_interval": 1,
      "series_id": "uuid",
      "instance_number": 1,
      "reminder_settings": [
        {"offset_minutes": 60, "label": "1 hour before"}
      ]
    }
  ],
  "next_id": 2,
  "recurring_series": [
    {
      "series_id": "uuid",
      "base_task_id": 1,
      "recurrence_pattern": "weekly",
      "active_instance_ids": [1],
      "completed_instance_ids": []
    }
  ]
}
```

**config/config.json**:
```json
{
  "time_zone": "America/New_York",
  "default_reminder_offset": 3600,
  "email_recipient": "haji08307@gmail.com",
  "daily_digest_time": "08:00"
}
```

**reminders.json** (transient):
```json
{
  "reminders": [
    {
      "id": "uuid",
      "task_id": 1,
      "scheduled_time": "2026-02-10T13:30:00Z",
      "status": "pending"
    }
  ],
  "daily_digest": {
    "date": "2026-02-08",
    "failed_reminders": []
  }
}
```

### Key Dependencies

**Installation** (using UV per project constitution):
```bash
uv add google-api-python-client
uv add google-auth
uv add google-auth-oauthlib
uv add python-dateutil
uv add pytz
```

**Note**: Use `uv add` for all package management as specified in project constitution. UV handles dependency resolution and virtual environment management.

**Credentials Setup**:
1. Place `credentials.json` in `credentials/` folder
2. Run OAuth flow to generate `token.json`
3. Both files already exist per specification

### Service Initialization

```python
# In __main__.py or app startup
from ticklisto.services.gmail_service import GmailService
from ticklisto.services.reminder_service import ReminderService
from ticklisto.services.recurring_task_service import RecurringTaskService
from ticklisto.services.time_zone_service import TimeZoneService
from ticklisto.services.storage_service import StorageService

# Initialize services
storage = StorageService()
tz_service = TimeZoneService()
gmail = GmailService('credentials/credentials.json', 'credentials/token.json')
reminder_service = ReminderService(gmail, storage, tz_service)
recurring_service = RecurringTaskService(storage, tz_service)

# Start reminder service
reminder_service.start()

# On shutdown
reminder_service.stop()
```

### Common Patterns

**Create Recurring Task**:
```python
task = Task(
    id=next_id,
    title="Weekly team meeting",
    due_date=datetime(2026, 2, 10),
    due_time=time(14, 30),
    recurrence_pattern=RecurrencePattern.WEEKLY,
    recurrence_interval=1
)
series = recurring_service.create_recurring_task(task)
```

**Add Reminders**:
```python
task.reminder_settings = [
    ReminderSetting(offset_minutes=60, label="1 hour before"),
    ReminderSetting(offset_minutes=1440, label="1 day before")
]
reminders = reminder_service.schedule_reminders(task)
```

**Complete Recurring Task**:
```python
# Mark current instance complete
task.mark_complete()

# Generate next instance
next_task = recurring_service.complete_instance_and_generate_next(task)
```

## Testing Strategy

### Unit Tests
- Test each service method independently
- Mock external dependencies (Gmail API, file I/O)
- Test edge cases (month-end dates, DST transitions, rate limits)

### Integration Tests
- Test end-to-end flows (create recurring task → complete → generate next)
- Test reminder flow (schedule → send → verify)
- Test with real Gmail API (limited, use test account)

### Manual Testing
- Create recurring tasks with various patterns
- Verify reminders sent at correct times
- Test time zone conversions
- Verify UI displays correctly

## Deployment Checklist

- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Gmail API credentials configured
- [ ] Time zone set in config.json
- [ ] README.md updated
- [ ] Reminder service starts on app launch
- [ ] Backward compatibility verified (existing tasks work)
- [ ] Performance tested with 1000+ tasks
- [ ] Error handling tested (network failures, auth errors)
- [ ] Daily digest tested (8 AM send time)

## Troubleshooting

**Gmail Authentication Fails**:
- Verify credentials.json and token.json exist
- Check token expiration, refresh if needed
- Ensure Gmail API enabled for account

**Reminders Not Sending**:
- Check reminder service is running (`service.get_status()`)
- Verify task has due_time set
- Check network connectivity
- Review logs for errors

**Recurring Tasks Not Generating**:
- Verify series_id is set on task
- Check recurrence_end_date not reached
- Ensure series is active (`is_series_active()`)

**Time Zone Issues**:
- Verify config.json has valid time zone
- Check time zone name against pytz.all_timezones
- Ensure UTC storage, user TZ display pattern followed

## Next Steps

After completing implementation:
1. Run `/sp.tasks` to generate detailed task breakdown
2. Implement in order: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
3. Follow TDD: Write tests → Get approval → Tests fail → Implement → Tests pass
4. Commit atomically with co-authoring
5. Update documentation as you go
6. Test on Hugging Face Spaces deployment

## Resources

- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [pytz Documentation](https://pythonhosted.org/pytz/)
- [python-dateutil Documentation](https://dateutil.readthedocs.io/)
- [Spec Document](./spec.md)
- [Data Model](./data-model.md)
- [Service Contracts](./contracts/)
