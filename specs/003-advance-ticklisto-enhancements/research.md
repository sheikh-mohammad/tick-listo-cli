# Research: Advanced Ticklisto Enhancements

**Feature**: 003-advance-ticklisto-enhancements
**Date**: 2026-02-08
**Phase**: 0 - Research & Technology Decisions

## Overview

This document captures research findings and technology decisions for implementing recurring tasks, time-based reminders, and Gmail notifications in Ticklisto.

## Technology Decisions

### 1. Gmail API Integration

**Decision**: Use google-api-python-client with OAuth 2.0 authentication

**Rationale**:
- Official Google library with comprehensive documentation
- Supports OAuth 2.0 flow with token refresh
- Existing credentials (token.json, credentials.json) already available
- Well-maintained with active community support
- Handles rate limiting and quota management

**Alternatives Considered**:
- SMTP with Gmail: Rejected - requires app-specific passwords, less secure, no quota management
- Third-party email services (SendGrid, Mailgun): Rejected - adds external dependency, cost, and complexity

**Implementation Pattern**:
```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Load credentials from token.json
creds = Credentials.from_authorized_user_file('token.json', SCOPES)
service = build('gmail', 'v1', credentials=creds)

# Send email
message = create_message(to, subject, body)
service.users().messages().send(userId='me', body=message).execute()
```

**Best Practices**:
- Store credentials securely outside source control
- Implement token refresh logic for expired tokens
- Handle API errors gracefully with try-except blocks
- Use exponential backoff for rate limit errors (429 status)
- Batch requests when possible to reduce quota usage

### 2. Time Zone Handling

**Decision**: Use pytz for time zone conversions with UTC storage

**Rationale**:
- Industry standard for Python time zone handling
- Comprehensive time zone database (IANA/Olson)
- Handles DST transitions correctly
- Works seamlessly with datetime objects
- Widely used and well-tested

**Alternatives Considered**:
- dateutil.tz: Rejected - less comprehensive than pytz for complex time zones
- Python 3.9+ zoneinfo: Considered but pytz more battle-tested for production

**Implementation Pattern**:
```python
import pytz
from datetime import datetime

# Store in UTC
utc_time = datetime.now(pytz.UTC)

# Convert to user's time zone
user_tz = pytz.timezone('America/New_York')
local_time = utc_time.astimezone(user_tz)

# Parse user input in their time zone
naive_time = datetime.strptime('2026-02-15 14:30', '%Y-%m-%d %H:%M')
localized_time = user_tz.localize(naive_time)
utc_time = localized_time.astimezone(pytz.UTC)
```

**Best Practices**:
- Always store timestamps in UTC internally
- Convert to user's time zone only for display/input
- Use timezone-aware datetime objects (not naive)
- Handle DST transitions by using localize() for naive times
- Validate time zone names against pytz.all_timezones

### 3. Time Parsing

**Decision**: Use python-dateutil for flexible time/date parsing

**Rationale**:
- Parses multiple date/time formats automatically
- Handles natural language inputs ("tomorrow at 2pm")
- Works well with existing datetime objects
- Lightweight and fast
- No training required (rule-based)

**Alternatives Considered**:
- Manual parsing with strptime: Rejected - too rigid, doesn't handle variations
- NLP libraries (spaCy, NLTK): Rejected - overkill for date parsing, large dependencies

**Implementation Pattern**:
```python
from dateutil import parser

# Parse various formats
dt1 = parser.parse('2026-02-15 14:30')  # ISO format
dt2 = parser.parse('Feb 15, 2026 at 2:30 PM')  # Natural format
dt3 = parser.parse('tomorrow at 2pm', fuzzy=True)  # Relative with fuzzy matching
```

**Best Practices**:
- Use fuzzy=True for natural language inputs
- Validate parsed results (check if reasonable)
- Provide clear error messages for unparseable inputs
- Default to user's time zone for ambiguous inputs

### 4. Background Reminder Service

**Decision**: Use threading.Thread with daemon mode for continuous reminder checking

**Rationale**:
- Built-in Python threading (no external dependencies)
- Daemon threads automatically terminate when main program exits
- Suitable for I/O-bound tasks (network requests to Gmail API)
- Simple to implement and debug
- Works well with Hugging Face Spaces deployment model

**Alternatives Considered**:
- asyncio: Rejected - adds complexity, not needed for 1-minute intervals
- multiprocessing: Rejected - overkill for single-user application
- APScheduler: Rejected - external dependency, more complex than needed
- Celery: Rejected - requires message broker, too heavy for this use case

**Implementation Pattern**:
```python
import threading
import time

class ReminderService:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._check_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def _check_loop(self):
        while self.running:
            self._check_and_send_reminders()
            time.sleep(60)  # 1 minute interval
```

**Best Practices**:
- Use daemon=True so thread doesn't prevent program exit
- Implement graceful shutdown with stop() method
- Use thread-safe data structures (queue.Queue) for shared state
- Handle exceptions within the thread to prevent crashes
- Log all reminder checks and sends for debugging

### 5. Exponential Backoff Strategy

**Decision**: Implement exponential backoff with jitter for Gmail API rate limiting

**Rationale**:
- Standard approach for handling rate limits
- Reduces thundering herd problem with jitter
- Maximizes successful delivery while respecting quotas
- Recommended by Google API best practices

**Implementation Pattern**:
```python
import time
import random

def send_with_backoff(send_func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return send_func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            # Exponential backoff: 2^attempt seconds + jitter
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

**Best Practices**:
- Start with 1-2 second base delay
- Add random jitter (0-1 seconds) to prevent synchronized retries
- Cap maximum wait time (e.g., 60 seconds)
- Log retry attempts for monitoring
- Queue failed reminders for daily digest after max retries

### 6. Recurring Task Scheduling Algorithm

**Decision**: Calculate next occurrence based on original due date + interval

**Rationale**:
- Maintains consistent schedule (e.g., "every Monday" stays on Monday)
- Prevents schedule drift from early/late completions
- Aligns with user expectations for recurring tasks
- Simpler to implement and reason about

**Algorithm**:
```python
def calculate_next_occurrence(original_due_date, recurrence_pattern, interval=1, weekdays=None):
    if recurrence_pattern == 'daily':
        return original_due_date + timedelta(days=interval)
    elif recurrence_pattern == 'weekly':
        if weekdays:
            # Find next occurrence on specified weekdays
            return find_next_weekday(original_due_date, weekdays, interval)
        else:
            return original_due_date + timedelta(weeks=interval)
    elif recurrence_pattern == 'monthly':
        # Handle month-end edge cases (e.g., Jan 31 -> Feb 28)
        return add_months(original_due_date, interval)
    elif recurrence_pattern == 'yearly':
        return original_due_date.replace(year=original_due_date.year + interval)
```

**Edge Cases Handled**:
- Month-end dates (Feb 30 -> Feb 28/29)
- DST transitions (maintain local time)
- Leap years
- Weekday-specific recurrence (Mon/Wed/Fri)

### 7. Configuration Management

**Decision**: Use JSON file (config.json) for user configuration

**Rationale**:
- Consistent with existing storage approach (tasks.json)
- Human-readable and editable
- No additional dependencies
- Simple to implement and maintain

**Configuration Schema**:
```json
{
  "time_zone": "America/New_York",
  "default_reminder_offset": 3600,
  "email_recipient": "haji08307@gmail.com",
  "daily_digest_time": "08:00"
}
```

**Best Practices**:
- Validate configuration on load
- Provide sensible defaults for missing values
- Document configuration options in README
- Store config.json outside source control (add to .gitignore)

## Performance Considerations

### Task Storage and Retrieval
- JSON file remains efficient for up to 10,000 tasks
- Load entire file into memory on startup (acceptable for this scale)
- Write atomically to prevent corruption
- Consider indexing by due_date for faster reminder queries

### Reminder Checking Optimization
- Maintain in-memory sorted list of upcoming reminders
- Only check reminders due within next 2 minutes
- Rebuild reminder queue when tasks are added/updated
- Use binary search for efficient reminder lookup

### Memory Management
- Limit completed recurring task history (e.g., keep last 100 instances)
- Periodically clean up old reminders (sent/failed > 30 days)
- Monitor thread memory usage in long-running deployment

## Security Considerations

### Gmail Credentials
- Store token.json and credentials.json outside source control
- Use environment variables for sensitive paths in production
- Implement token refresh logic to handle expiration
- Log authentication failures for monitoring

### Email Content
- Sanitize task descriptions before including in emails
- Avoid including sensitive information in email subjects
- Use HTTPS for all Gmail API requests
- Validate email addresses before sending

## Testing Strategy

### Unit Tests
- Mock Gmail API calls to avoid quota usage
- Test time zone conversions with multiple time zones
- Test recurring task calculations for all patterns
- Test exponential backoff logic with simulated failures

### Integration Tests
- Test end-to-end reminder flow with test email account
- Test recurring task creation and completion cycle
- Test configuration loading and validation

### Contract Tests
- Verify Gmail API request/response formats
- Test OAuth token refresh flow
- Validate email message structure

## Deployment Considerations

### Hugging Face Spaces
- Application runs continuously (no cold starts)
- Background thread starts automatically on app launch
- Environment variables for credentials paths
- Logging to stdout for Spaces monitoring
- Graceful shutdown handling for restarts

### Monitoring
- Log all reminder sends (success/failure)
- Track Gmail API quota usage
- Monitor thread health and restart if crashed
- Alert on authentication failures

## Summary

All technology decisions are finalized with clear rationale and implementation patterns. No blocking unknowns remain. Ready to proceed to Phase 1 (Design & Contracts).
