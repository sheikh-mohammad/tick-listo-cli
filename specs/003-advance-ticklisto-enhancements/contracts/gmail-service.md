# Contract: Gmail Service

**Service**: GmailService
**Purpose**: Handle Gmail API integration for sending email reminders
**Dependencies**: google-api-python-client, google-auth, google-auth-oauthlib

## Interface Definition

### Class: GmailService

**Responsibility**: Authenticate with Gmail API and send email notifications for task reminders.

## Methods

### `__init__(credentials_path: str, token_path: str)`

**Description**: Initialize Gmail service with OAuth credentials.

**Parameters**:
- `credentials_path` (str): Path to credentials.json file
- `token_path` (str): Path to token.json file

**Raises**:
- `FileNotFoundError`: If credentials or token file not found
- `AuthenticationError`: If credentials are invalid

**Example**:
```python
service = GmailService(
    credentials_path='credentials/credentials.json',
    token_path='credentials/token.json'
)
```

---

### `send_reminder_email(task: Task, reminder_offset: int) -> bool`

**Description**: Send a reminder email for a specific task.

**Parameters**:
- `task` (Task): Task object containing details for the reminder
- `reminder_offset` (int): Minutes before due time (for email subject)

**Returns**:
- `bool`: True if email sent successfully, False otherwise

**Raises**:
- `AuthenticationError`: If token is expired or invalid
- `RateLimitError`: If Gmail API rate limit exceeded
- `NetworkError`: If network connection fails

**Email Format**:
- **To**: haji08307@gmail.com (from config)
- **Subject**: `[{priority}] Reminder: {task.title} due in {time_until_due}`
- **Body**: HTML formatted with task details (title, description, due date/time, priority, categories)

**Example**:
```python
success = service.send_reminder_email(task, reminder_offset=60)
if not success:
    # Handle failure (retry or queue for digest)
```

---

### `send_daily_digest(failed_reminders: list[EmailReminder], date: date) -> bool`

**Description**: Send daily digest email summarizing failed reminders.

**Parameters**:
- `failed_reminders` (list[EmailReminder]): List of reminders that failed after retries
- `date` (date): Date of the digest

**Returns**:
- `bool`: True if digest sent successfully, False otherwise

**Raises**:
- `AuthenticationError`: If token is expired or invalid
- `RateLimitError`: If Gmail API rate limit exceeded
- `NetworkError`: If network connection fails

**Email Format**:
- **To**: haji08307@gmail.com
- **Subject**: `Daily Task Reminder Digest - {date}`
- **Body**: HTML table with all failed reminders (task title, due date/time, priority)

**Example**:
```python
success = service.send_daily_digest(failed_reminders, date.today())
```

---

### `refresh_token() -> bool`

**Description**: Refresh expired OAuth token.

**Returns**:
- `bool`: True if token refreshed successfully, False otherwise

**Raises**:
- `AuthenticationError`: If refresh token is invalid or expired

**Side Effects**:
- Updates token.json file with new access token

**Example**:
```python
if service.refresh_token():
    # Retry failed operation
```

---

### `test_connection() -> bool`

**Description**: Test Gmail API connection and authentication.

**Returns**:
- `bool`: True if connection successful, False otherwise

**Example**:
```python
if not service.test_connection():
    print("Gmail API authentication failed")
```

## Error Handling

### Custom Exceptions

```python
class AuthenticationError(Exception):
    """Raised when Gmail authentication fails."""
    pass

class RateLimitError(Exception):
    """Raised when Gmail API rate limit is exceeded."""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after  # Seconds to wait
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s")

class NetworkError(Exception):
    """Raised when network connection fails."""
    pass
```

### Error Recovery Strategy

1. **AuthenticationError**: Attempt token refresh, then fail gracefully
2. **RateLimitError**: Implement exponential backoff with jitter
3. **NetworkError**: Queue reminder for retry, log error

## Rate Limiting

**Gmail API Quotas**:
- 250 quota units per user per second
- Sending message costs 100 units
- Maximum ~2.5 emails per second

**Implementation Strategy**:
- Track quota usage in-memory
- Implement exponential backoff on 429 errors
- Queue failed reminders for daily digest after 3 retries

## Security Considerations

- Store credentials outside source control
- Use environment variables for paths in production
- Validate token expiration before each request
- Log authentication failures for monitoring
- Never log email content or credentials

## Testing Strategy

### Unit Tests (Mocked)
```python
def test_send_reminder_email_success(mock_gmail_api):
    service = GmailService('creds.json', 'token.json')
    task = create_test_task()
    assert service.send_reminder_email(task, 60) == True

def test_send_reminder_email_rate_limit(mock_gmail_api):
    mock_gmail_api.side_effect = RateLimitError(retry_after=30)
    service = GmailService('creds.json', 'token.json')
    with pytest.raises(RateLimitError):
        service.send_reminder_email(task, 60)
```

### Integration Tests (Real API)
```python
@pytest.mark.integration
def test_send_real_email():
    service = GmailService('credentials.json', 'token.json')
    task = create_test_task()
    success = service.send_reminder_email(task, 60)
    assert success == True
```

## Performance Requirements

- Email send latency: <2 seconds under normal conditions
- Token refresh: <1 second
- Connection test: <500ms

## Contract Validation

**Pre-conditions**:
- Valid credentials.json and token.json files exist
- Network connectivity available
- Gmail API enabled for the account

**Post-conditions**:
- Email delivered to recipient or error raised
- Token refreshed if expired
- All operations logged

**Invariants**:
- Credentials never exposed in logs or errors
- Rate limits respected
- Failed sends queued for retry or digest
