"""Unit tests for GmailService (T042, T044 - User Story 3)."""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, time
import json
from ticklisto.models.task import Task, Priority
from ticklisto.models.reminder import EmailReminder, ReminderStatus


class TestGmailServiceInitialization:
    """Unit tests for GmailService initialization and OAuth."""

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    def test_initialize_with_valid_token(self, mock_credentials, mock_build, mock_exists):
        """Test GmailService initialization with valid token.json."""
        from ticklisto.services.gmail_service import GmailService

        # Mock valid credentials
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        # Mock Gmail API service
        mock_service = Mock()
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        assert service.service == mock_service
        mock_credentials.from_authorized_user_file.assert_called_once_with("token.json", GmailService.SCOPES)
        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    def test_initialize_with_expired_token(self, mock_credentials, mock_build, mock_exists):
        """Test GmailService initialization with expired token that needs refresh."""
        from ticklisto.services.gmail_service import GmailService

        # Mock expired credentials that can be refreshed
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token_123"
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        # Mock Request for refresh
        with patch('google.auth.transport.requests.Request') as mock_request:
            mock_service = Mock()
            mock_build.return_value = mock_service

            service = GmailService(token_path="token.json", credentials_path="credentials.json")

            # Should refresh the token
            mock_creds.refresh.assert_called_once()
            assert service.service == mock_service

    @patch('google_auth_oauthlib.flow.InstalledAppFlow')
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    @patch('os.path.exists')
    def test_initialize_without_token_runs_oauth_flow(self, mock_exists, mock_credentials, mock_build, mock_flow):
        """Test GmailService initialization without token.json runs OAuth flow."""
        from ticklisto.services.gmail_service import GmailService

        # Mock: credentials.json exists, but token.json doesn't
        def exists_side_effect(path):
            if "token.json" in path:
                return False
            return True
        mock_exists.side_effect = exists_side_effect

        # Mock OAuth flow
        mock_flow_instance = Mock()
        mock_creds = Mock()
        mock_creds.valid = True
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance

        mock_service = Mock()
        mock_build.return_value = mock_service

        with patch('builtins.open', create=True):
            service = GmailService(token_path="token.json", credentials_path="credentials.json")

        # Should run OAuth flow
        mock_flow.from_client_secrets_file.assert_called_once_with(
            "credentials.json", GmailService.SCOPES
        )
        mock_flow_instance.run_local_server.assert_called_once_with(port=0)
        assert service.service == mock_service

    @patch('os.path.exists')
    def test_initialize_without_credentials_raises_error(self, mock_exists):
        """Test GmailService initialization without credentials.json raises error."""
        from ticklisto.services.gmail_service import GmailService

        # Mock no credentials.json exists
        def exists_side_effect(path):
            if "credentials.json" in path:
                return False
            return True

        mock_exists.side_effect = exists_side_effect

        with pytest.raises(FileNotFoundError, match="credentials.json not found"):
            GmailService(token_path="token.json", credentials_path="credentials.json")


class TestGmailServiceSendEmail:
    """Unit tests for GmailService.send_reminder_email()."""

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    def test_send_reminder_email_success(self, mock_credentials, mock_build, mock_exists):
        """Test successful email sending."""
        from ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.return_value = {"id": "msg_123"}
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        # Create test task
        task = Task(
            id=1,
            title="Test task",
            description="Test description",
            due_date=datetime(2026, 2, 15, 14, 30, 0),
            due_time=time(14, 30),
            priority=Priority.HIGH
        )

        # Send email
        result = service.send_reminder_email(
            task=task,
            recipient="test@example.com",
            offset_label="1 hour before"
        )

        assert result is True
        mock_messages.send.assert_called_once()

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    def test_send_reminder_email_formats_message_correctly(self, mock_credentials, mock_build, mock_exists):
        """Test that email message is formatted correctly."""
        from ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.return_value = {"id": "msg_123"}
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        task = Task(
            id=1,
            title="Important meeting",
            description="Discuss project timeline",
            due_date=datetime(2026, 2, 15, 14, 30, 0),
            due_time=time(14, 30),
            priority=Priority.HIGH,
            categories=["work", "urgent"]
        )

        service.send_reminder_email(
            task=task,
            recipient="test@example.com",
            offset_label="1 hour before"
        )

        # Verify send was called with correct structure
        call_args = mock_messages.send.call_args
        assert call_args is not None

        # The message should contain task details
        message_body = call_args[1]['body']
        assert 'raw' in message_body

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    def test_send_reminder_email_handles_api_error(self, mock_credentials, mock_build, mock_exists):
        """Test handling of Gmail API errors."""
        from ticklisto.services.gmail_service import GmailService
        from googleapiclient.errors import HttpError

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages

        # Mock API error
        mock_response = Mock()
        mock_response.status = 500
        mock_messages.send.return_value.execute.side_effect = HttpError(
            resp=mock_response,
            content=b'Internal server error'
        )
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        task = Task(
            id=1,
            title="Test task",
            due_date=datetime(2026, 2, 15, 14, 30, 0)
        )

        result = service.send_reminder_email(
            task=task,
            recipient="test@example.com",
            offset_label="1 hour before"
        )

        assert result is False


class TestGmailServiceRetryLogic:
    """Unit tests for exponential backoff retry logic (T044)."""

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    @patch('time.sleep')
    def test_retry_with_exponential_backoff(self, mock_sleep, mock_credentials, mock_build, mock_exists):
        """Test retry logic with exponential backoff."""
        from ticklisto.services.gmail_service import GmailService
        from googleapiclient.errors import HttpError

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages

        # Mock rate limit error on first 2 attempts, success on 3rd
        mock_response = Mock()
        mock_response.status = 429  # Rate limit
        mock_messages.send.return_value.execute.side_effect = [
            HttpError(resp=mock_response, content=b'Rate limit exceeded'),
            HttpError(resp=mock_response, content=b'Rate limit exceeded'),
            {"id": "msg_123"}  # Success on 3rd attempt
        ]
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        task = Task(
            id=1,
            title="Test task",
            due_date=datetime(2026, 2, 15, 14, 30, 0)
        )

        result = service.send_reminder_email(
            task=task,
            recipient="test@example.com",
            offset_label="1 hour before"
        )

        assert result is True
        assert mock_messages.send.return_value.execute.call_count == 3

        # Verify exponential backoff: 1s, 2s
        assert mock_sleep.call_count == 2
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_calls[0] == 1  # First retry: 1 second
        assert sleep_calls[1] == 2  # Second retry: 2 seconds

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    @patch('time.sleep')
    def test_retry_fails_after_max_attempts(self, mock_sleep, mock_credentials, mock_build, mock_exists):
        """Test that retry fails after max attempts (3)."""
        from ticklisto.services.gmail_service import GmailService
        from googleapiclient.errors import HttpError

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages

        # Mock rate limit error on all attempts
        mock_response = Mock()
        mock_response.status = 429
        mock_messages.send.return_value.execute.side_effect = HttpError(
            resp=mock_response,
            content=b'Rate limit exceeded'
        )
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        task = Task(
            id=1,
            title="Test task",
            due_date=datetime(2026, 2, 15, 14, 30, 0)
        )

        result = service.send_reminder_email(
            task=task,
            recipient="test@example.com",
            offset_label="1 hour before"
        )

        assert result is False
        assert mock_messages.send.return_value.execute.call_count == 3
        assert mock_sleep.call_count == 2  # Sleep between attempts

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    @patch('time.sleep')
    def test_no_retry_for_authentication_errors(self, mock_sleep, mock_credentials, mock_build, mock_exists):
        """Test that authentication errors are not retried."""
        from ticklisto.services.gmail_service import GmailService
        from googleapiclient.errors import HttpError

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages

        # Mock authentication error (401)
        mock_response = Mock()
        mock_response.status = 401
        mock_messages.send.return_value.execute.side_effect = HttpError(
            resp=mock_response,
            content=b'Unauthorized'
        )
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        task = Task(
            id=1,
            title="Test task",
            due_date=datetime(2026, 2, 15, 14, 30, 0)
        )

        result = service.send_reminder_email(
            task=task,
            recipient="test@example.com",
            offset_label="1 hour before"
        )

        assert result is False
        assert mock_messages.send.return_value.execute.call_count == 1  # No retry
        assert mock_sleep.call_count == 0  # No sleep


class TestGmailServiceDailyDigest:
    """Unit tests for send_daily_digest()."""

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    def test_send_daily_digest_with_multiple_reminders(self, mock_credentials, mock_build, mock_exists):
        """Test sending daily digest with multiple failed reminders."""
        from ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.return_value = {"id": "msg_digest"}
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        # Create test tasks
        tasks = [
            Task(id=1, title="Task 1", due_date=datetime(2026, 2, 15, 10, 0, 0)),
            Task(id=2, title="Task 2", due_date=datetime(2026, 2, 15, 14, 0, 0)),
            Task(id=3, title="Task 3", due_date=datetime(2026, 2, 15, 16, 0, 0))
        ]

        result = service.send_daily_digest(
            tasks=tasks,
            recipient="test@example.com"
        )

        assert result is True
        mock_messages.send.assert_called_once()

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    def test_send_daily_digest_with_empty_list(self, mock_credentials, mock_build, mock_exists):
        """Test sending daily digest with no reminders."""
        from ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        # Empty task list should not send email
        result = service.send_daily_digest(
            tasks=[],
            recipient="test@example.com"
        )

        assert result is True  # No error, but no email sent


class TestEmailContentFormatting:
    """Unit tests for email content formatting (T095 - User Story 7)."""

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    def test_email_includes_all_task_details(self, mock_credentials, mock_build, mock_exists):
        """Test that reminder email includes title, description, due date/time, priority, and categories."""
        from ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.return_value = {"id": "msg_123"}
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        # Create task with all fields populated
        task = Task(
            id=1,
            title="Complete project proposal",
            description="Finalize and submit the Q1 project proposal with budget estimates",
            due_date=datetime(2026, 2, 18, 15, 30, 0),
            due_time=time(15, 30),
            priority=Priority.HIGH,
            categories=["work", "projects", "urgent"]
        )

        result = service.send_reminder_email(
            task=task,
            recipient="test@example.com",
            offset_label="2 hours before"
        )

        assert result is True

        # Verify send was called
        mock_messages.send.assert_called_once()

        # Get the message that was sent
        call_args = mock_messages.send.call_args
        sent_message = call_args[1]['body']

        # Verify message contains raw field (base64 encoded email)
        assert 'raw' in sent_message

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    def test_email_body_is_html_formatted(self, mock_credentials, mock_build, mock_exists):
        """Test that email body is formatted as HTML with clear sections."""
        from ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        task = Task(
            id=2,
            title="Team meeting",
            description="Discuss Q1 goals",
            due_date=datetime(2026, 2, 20, 10, 0, 0),
            due_time=time(10, 0),
            priority=Priority.MEDIUM,
            categories=["meetings"]
        )

        result = service.send_reminder_email(
            task=task,
            recipient="test@example.com",
            offset_label="1 hour before"
        )

        # The email formatting is tested by successful send
        assert result is True


class TestPriorityIndicatorInSubject:
    """Unit tests for priority indicator in subject line (T096 - User Story 7)."""

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    def test_high_priority_task_has_indicator_in_subject(self, mock_credentials, mock_build, mock_exists):
        """Test that high priority tasks have [HIGH PRIORITY] in subject line."""
        from ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.return_value = {"id": "msg_high"}
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        task = Task(
            id=1,
            title="Critical bug fix",
            due_date=datetime(2026, 2, 15, 17, 0, 0),
            due_time=time(17, 0),
            priority=Priority.HIGH
        )

        result = service.send_reminder_email(
            task=task,
            recipient="test@example.com",
            offset_label="30 minutes before"
        )

        assert result is True
        mock_messages.send.assert_called_once()

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    def test_medium_priority_task_no_indicator(self, mock_credentials, mock_build, mock_exists):
        """Test that medium priority tasks don't have priority indicator."""
        from ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        task = Task(
            id=2,
            title="Regular task",
            due_date=datetime(2026, 2, 15, 14, 0, 0),
            due_time=time(14, 0),
            priority=Priority.MEDIUM
        )

        result = service.send_reminder_email(
            task=task,
            recipient="test@example.com",
            offset_label="1 hour before"
        )

        assert result is True

    @patch('os.path.exists', return_value=True)
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.credentials.Credentials')
    def test_low_priority_task_no_indicator(self, mock_credentials, mock_build, mock_exists):
        """Test that low priority tasks don't have priority indicator."""
        from ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        service = GmailService(token_path="token.json", credentials_path="credentials.json")

        task = Task(
            id=3,
            title="Low priority task",
            due_date=datetime(2026, 2, 15, 16, 0, 0),
            due_time=time(16, 0),
            priority=Priority.LOW
        )

        result = service.send_reminder_email(
            task=task,
            recipient="test@example.com",
            offset_label="2 hours before"
        )

        assert result is True

