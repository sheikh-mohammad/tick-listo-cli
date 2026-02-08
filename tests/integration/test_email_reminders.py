"""Integration tests for email reminders (T046 - User Story 3)."""

import pytest
from datetime import datetime, time, timedelta
from unittest.mock import Mock, patch
from src.ticklisto.models.task import Task, Priority
from src.ticklisto.models.reminder import EmailReminder, ReminderStatus, ReminderSetting


class TestEmailReminderIntegration:
    """Integration tests for sending reminder emails."""

    @patch('src.ticklisto.services.gmail_service.build')
    @patch('src.ticklisto.services.gmail_service.Credentials')
    def test_send_reminder_for_task_with_due_time(self, mock_credentials, mock_build):
        """Test sending reminder for a task with due date and time."""
        from src.ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.return_value = {"id": "msg_123"}
        mock_build.return_value = mock_service

        # Create GmailService
        gmail_service = GmailService(
            token_path="token.json",
            credentials_path="credentials.json"
        )

        # Create task with due time
        task = Task(
            id=1,
            title="Team meeting",
            description="Discuss Q1 goals",
            due_date=datetime(2026, 2, 15, 14, 30, 0),
            due_time=time(14, 30),
            priority=Priority.HIGH,
            categories=["work", "meetings"]
        )

        # Send reminder
        result = gmail_service.send_reminder_email(
            task=task,
            recipient="haji08307@gmail.com",
            offset_label="1 hour before"
        )

        assert result is True
        mock_messages.send.assert_called_once()

    @patch('src.ticklisto.services.gmail_service.build')
    @patch('src.ticklisto.services.gmail_service.Credentials')
    def test_send_reminder_for_recurring_task(self, mock_credentials, mock_build):
        """Test sending reminder for a recurring task."""
        from src.ticklisto.services.gmail_service import GmailService
        from src.ticklisto.models.task import RecurrencePattern

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.return_value = {"id": "msg_456"}
        mock_build.return_value = mock_service

        gmail_service = GmailService(
            token_path="token.json",
            credentials_path="credentials.json"
        )

        # Create recurring task
        task = Task(
            id=2,
            title="Weekly standup",
            description="Team sync meeting",
            due_date=datetime(2026, 2, 17, 9, 0, 0),
            due_time=time(9, 0),
            priority=Priority.MEDIUM,
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_interval=1,
            series_id="series-123",
            instance_number=3
        )

        result = gmail_service.send_reminder_email(
            task=task,
            recipient="haji08307@gmail.com",
            offset_label="15 minutes before"
        )

        assert result is True
        mock_messages.send.assert_called_once()

    @patch('src.ticklisto.services.gmail_service.build')
    @patch('src.ticklisto.services.gmail_service.Credentials')
    def test_send_multiple_reminders_for_same_task(self, mock_credentials, mock_build):
        """Test sending multiple reminders for the same task."""
        from src.ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.return_value = {"id": "msg_789"}
        mock_build.return_value = mock_service

        gmail_service = GmailService(
            token_path="token.json",
            credentials_path="credentials.json"
        )

        task = Task(
            id=3,
            title="Project deadline",
            description="Submit final report",
            due_date=datetime(2026, 2, 20, 17, 0, 0),
            due_time=time(17, 0),
            priority=Priority.HIGH
        )

        # Send first reminder (1 day before)
        result1 = gmail_service.send_reminder_email(
            task=task,
            recipient="haji08307@gmail.com",
            offset_label="1 day before"
        )

        # Send second reminder (1 hour before)
        result2 = gmail_service.send_reminder_email(
            task=task,
            recipient="haji08307@gmail.com",
            offset_label="1 hour before"
        )

        assert result1 is True
        assert result2 is True
        assert mock_messages.send.call_count == 2

    @patch('src.ticklisto.services.gmail_service.build')
    @patch('src.ticklisto.services.gmail_service.Credentials')
    @patch('time.sleep')
    def test_retry_on_rate_limit_then_success(self, mock_sleep, mock_credentials, mock_build):
        """Test that rate limit errors are retried and eventually succeed."""
        from src.ticklisto.services.gmail_service import GmailService
        from googleapiclient.errors import HttpError

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages

        # First attempt: rate limit, second attempt: success
        mock_response = Mock()
        mock_response.status = 429
        mock_messages.send.return_value.execute.side_effect = [
            HttpError(resp=mock_response, content=b'Rate limit exceeded'),
            {"id": "msg_success"}
        ]
        mock_build.return_value = mock_service

        gmail_service = GmailService(
            token_path="token.json",
            credentials_path="credentials.json"
        )

        task = Task(
            id=4,
            title="Important task",
            due_date=datetime(2026, 2, 15, 10, 0, 0),
            due_time=time(10, 0)
        )

        result = gmail_service.send_reminder_email(
            task=task,
            recipient="haji08307@gmail.com",
            offset_label="30 minutes before"
        )

        assert result is True
        assert mock_messages.send.return_value.execute.call_count == 2
        mock_sleep.assert_called_once_with(1)  # First retry delay

    @patch('src.ticklisto.services.gmail_service.build')
    @patch('src.ticklisto.services.gmail_service.Credentials')
    def test_send_daily_digest_with_failed_reminders(self, mock_credentials, mock_build):
        """Test sending daily digest with multiple failed reminders."""
        from src.ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.return_value = {"id": "msg_digest"}
        mock_build.return_value = mock_service

        gmail_service = GmailService(
            token_path="token.json",
            credentials_path="credentials.json"
        )

        # Create multiple tasks for digest
        tasks = [
            Task(
                id=5,
                title="Task 1",
                description="First task",
                due_date=datetime(2026, 2, 15, 10, 0, 0),
                due_time=time(10, 0),
                priority=Priority.HIGH
            ),
            Task(
                id=6,
                title="Task 2",
                description="Second task",
                due_date=datetime(2026, 2, 15, 14, 0, 0),
                due_time=time(14, 0),
                priority=Priority.MEDIUM
            ),
            Task(
                id=7,
                title="Task 3",
                description="Third task",
                due_date=datetime(2026, 2, 15, 16, 30, 0),
                due_time=time(16, 30),
                priority=Priority.LOW
            )
        ]

        result = gmail_service.send_daily_digest(
            tasks=tasks,
            recipient="haji08307@gmail.com"
        )

        assert result is True
        mock_messages.send.assert_called_once()

    @patch('src.ticklisto.services.gmail_service.build')
    @patch('src.ticklisto.services.gmail_service.Credentials')
    def test_handle_network_error_gracefully(self, mock_credentials, mock_build):
        """Test that network errors are handled gracefully."""
        from src.ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.side_effect = ConnectionError("Network unreachable")
        mock_build.return_value = mock_service

        gmail_service = GmailService(
            token_path="token.json",
            credentials_path="credentials.json"
        )

        task = Task(
            id=8,
            title="Test task",
            due_date=datetime(2026, 2, 15, 12, 0, 0)
        )

        result = gmail_service.send_reminder_email(
            task=task,
            recipient="haji08307@gmail.com",
            offset_label="1 hour before"
        )

        assert result is False

    @patch('src.ticklisto.services.gmail_service.build')
    @patch('src.ticklisto.services.gmail_service.Credentials')
    def test_send_reminder_with_all_task_details(self, mock_credentials, mock_build):
        """Test that reminder email includes all task details."""
        from src.ticklisto.services.gmail_service import GmailService

        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.return_value = {"id": "msg_complete"}
        mock_build.return_value = mock_service

        gmail_service = GmailService(
            token_path="token.json",
            credentials_path="credentials.json"
        )

        # Task with all fields populated
        task = Task(
            id=9,
            title="Complete project proposal",
            description="Finalize and submit the Q1 project proposal with budget estimates",
            due_date=datetime(2026, 2, 18, 15, 30, 0),
            due_time=time(15, 30),
            priority=Priority.HIGH,
            categories=["work", "projects", "urgent"]
        )

        result = gmail_service.send_reminder_email(
            task=task,
            recipient="haji08307@gmail.com",
            offset_label="2 hours before"
        )

        assert result is True
        mock_messages.send.assert_called_once()


class TestMultipleReminderDelivery:
    """Integration tests for multiple reminder delivery (T089 - User Story 6)."""

    def setup_method(self):
        """Clean up reminders.json before each test."""
        import os
        if os.path.exists("reminders.json"):
            os.remove("reminders.json")

    @patch('os.path.exists', return_value=True)
    @patch('src.ticklisto.services.gmail_service.build')
    @patch('src.ticklisto.services.gmail_service.Credentials')
    def test_schedule_and_deliver_multiple_reminders(self, mock_credentials, mock_build, mock_exists):
        """Test scheduling and delivering multiple reminders for a single task."""
        from src.ticklisto.services.gmail_service import GmailService
        from src.ticklisto.services.reminder_service import ReminderService
        from src.ticklisto.services.storage_service import StorageService
        from src.ticklisto.services.time_zone_service import TimeZoneService

        # Setup Gmail mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.return_value = {"id": "msg_123"}
        mock_build.return_value = mock_service

        # Create services
        gmail_service = GmailService(
            token_path="token.json",
            credentials_path="credentials.json"
        )
        storage_service = StorageService()
        tz_service = TimeZoneService("America/New_York")
        reminder_service = ReminderService(gmail_service, storage_service, tz_service)

        # Create task with multiple reminder settings
        future_time = datetime.now() + timedelta(hours=5)
        task = Task(
            id=1,
            title="Important presentation",
            description="Present Q1 results to board",
            due_date=future_time,
            due_time=future_time.time(),
            priority=Priority.HIGH,
            categories=["work", "presentations"],
            reminder_settings=[
                ReminderSetting(offset_minutes=15, label="15 minutes before"),
                ReminderSetting(offset_minutes=60, label="1 hour before"),
                ReminderSetting(offset_minutes=240, label="4 hours before")
            ]
        )

        # Schedule reminders
        reminders = reminder_service.schedule_reminders(task)

        # Should create 3 reminders
        assert len(reminders) == 3
        assert all(r.task_id == 1 for r in reminders)
        assert all(r.status == ReminderStatus.PENDING for r in reminders)

        # Verify reminders are in the queue
        pending = reminder_service.get_pending_reminders()
        assert len(pending) == 3

    @patch('os.path.exists', return_value=True)
    @patch('src.ticklisto.services.gmail_service.build')
    @patch('src.ticklisto.services.gmail_service.Credentials')
    def test_multiple_reminders_sent_at_different_times(self, mock_credentials, mock_build, mock_exists):
        """Test that multiple reminders are sent at their scheduled times."""
        from src.ticklisto.services.gmail_service import GmailService
        from src.ticklisto.services.reminder_service import ReminderService
        from src.ticklisto.services.storage_service import StorageService
        from src.ticklisto.services.time_zone_service import TimeZoneService

        # Setup Gmail mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_messages.send.return_value.execute.return_value = {"id": "msg_456"}
        mock_build.return_value = mock_service

        # Create services
        gmail_service = GmailService(
            token_path="token.json",
            credentials_path="credentials.json"
        )
        storage_service = StorageService()
        tz_service = TimeZoneService("America/New_York")
        reminder_service = ReminderService(gmail_service, storage_service, tz_service)

        # Create task due in 3 hours
        due_time = datetime.now() + timedelta(hours=3)
        task = Task(
            id=2,
            title="Team meeting",
            due_date=due_time,
            due_time=due_time.time(),
            reminder_settings=[
                ReminderSetting(offset_minutes=30, label="30 min before"),
                ReminderSetting(offset_minutes=120, label="2 hours before")
            ]
        )

        # Schedule reminders
        reminders = reminder_service.schedule_reminders(task)
        assert len(reminders) == 2

        # Verify scheduled times are different
        times = [r.scheduled_time for r in reminders]
        assert len(set(times)) == 2  # Two distinct times

        # Verify time differences
        time_diff = abs((times[0] - times[1]).total_seconds())
        assert time_diff == 90 * 60  # 1.5 hours difference (120 - 30 minutes)

    @patch('os.path.exists', return_value=True)
    @patch('src.ticklisto.services.gmail_service.build')
    @patch('src.ticklisto.services.gmail_service.Credentials')
    def test_cancel_all_reminders_for_task(self, mock_credentials, mock_build, mock_exists):
        """Test cancelling all reminders when task is completed."""
        from src.ticklisto.services.gmail_service import GmailService
        from src.ticklisto.services.reminder_service import ReminderService
        from src.ticklisto.services.storage_service import StorageService
        from src.ticklisto.services.time_zone_service import TimeZoneService

        # Setup Gmail mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        # Create services
        gmail_service = GmailService(
            token_path="token.json",
            credentials_path="credentials.json"
        )
        storage_service = StorageService()
        tz_service = TimeZoneService("America/New_York")
        reminder_service = ReminderService(gmail_service, storage_service, tz_service)

        # Create task with multiple reminders (due in 2 days to allow 1-day-before reminder)
        future_time = datetime.now() + timedelta(days=2)
        task = Task(
            id=3,
            title="Project deadline",
            due_date=future_time,
            due_time=future_time.time(),
            reminder_settings=[
                ReminderSetting(offset_minutes=30, label="30 min"),
                ReminderSetting(offset_minutes=120, label="2 hours"),
                ReminderSetting(offset_minutes=1440, label="1 day")
            ]
        )

        # Schedule reminders
        reminders = reminder_service.schedule_reminders(task)
        assert len(reminders) == 3

        # Verify all are pending
        pending_before = reminder_service.get_pending_reminders()
        task_reminders_before = [r for r in pending_before if r.task_id == 3]
        assert len(task_reminders_before) == 3

        # Cancel all reminders for this task
        reminder_service.cancel_reminders(task_id=3)

        # Verify all are cancelled
        pending_after = reminder_service.get_pending_reminders()
        task_reminders_after = [r for r in pending_after if r.task_id == 3]
        assert len(task_reminders_after) == 0

    @patch('os.path.exists', return_value=True)
    @patch('src.ticklisto.services.gmail_service.build')
    @patch('src.ticklisto.services.gmail_service.Credentials')
    def test_multiple_tasks_with_multiple_reminders(self, mock_credentials, mock_build, mock_exists):
        """Test managing multiple reminders across multiple tasks."""
        from src.ticklisto.services.gmail_service import GmailService
        from src.ticklisto.services.reminder_service import ReminderService
        from src.ticklisto.services.storage_service import StorageService
        from src.ticklisto.services.time_zone_service import TimeZoneService

        # Setup Gmail mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        # Create services
        gmail_service = GmailService(
            token_path="token.json",
            credentials_path="credentials.json"
        )
        storage_service = StorageService()
        tz_service = TimeZoneService("America/New_York")
        reminder_service = ReminderService(gmail_service, storage_service, tz_service)

        # Create multiple tasks with multiple reminders each
        base_time = datetime.now() + timedelta(hours=10)

        task1 = Task(
            id=10,
            title="Task 1",
            due_date=base_time,
            due_time=base_time.time(),
            reminder_settings=[
                ReminderSetting(offset_minutes=30, label="30 min"),
                ReminderSetting(offset_minutes=60, label="1 hour")
            ]
        )

        task2 = Task(
            id=11,
            title="Task 2",
            due_date=base_time + timedelta(hours=2),
            due_time=(base_time + timedelta(hours=2)).time(),
            reminder_settings=[
                ReminderSetting(offset_minutes=15, label="15 min"),
                ReminderSetting(offset_minutes=45, label="45 min"),
                ReminderSetting(offset_minutes=120, label="2 hours")
            ]
        )

        # Schedule reminders for both tasks
        reminders1 = reminder_service.schedule_reminders(task1)
        reminders2 = reminder_service.schedule_reminders(task2)

        assert len(reminders1) == 2
        assert len(reminders2) == 3

        # Verify total pending count
        all_pending = reminder_service.get_pending_reminders()
        assert len(all_pending) == 5

        # Cancel task 1's reminders
        reminder_service.cancel_reminders(task_id=10)

        # Verify only task 2's reminders remain
        remaining_pending = reminder_service.get_pending_reminders()
        assert len(remaining_pending) == 3
        assert all(r.task_id == 11 for r in remaining_pending)

    @patch('os.path.exists', return_value=True)
    @patch('src.ticklisto.services.gmail_service.build')
    @patch('src.ticklisto.services.gmail_service.Credentials')
    def test_reminder_delivery_with_retry_for_multiple_reminders(self, mock_credentials, mock_build, mock_exists):
        """Test that retry logic works for multiple reminders."""
        from src.ticklisto.services.gmail_service import GmailService
        from src.ticklisto.services.reminder_service import ReminderService
        from src.ticklisto.services.storage_service import StorageService
        from src.ticklisto.services.time_zone_service import TimeZoneService
        from googleapiclient.errors import HttpError

        # Setup Gmail mocks with rate limit on first call
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_messages = Mock()
        mock_service.users.return_value.messages.return_value = mock_messages

        # First reminder: rate limit then success
        # Second reminder: immediate success
        mock_response = Mock()
        mock_response.status = 429
        mock_messages.send.return_value.execute.side_effect = [
            HttpError(resp=mock_response, content=b'Rate limit'),
            {"id": "msg_1"},  # Retry success
            {"id": "msg_2"}   # Second reminder success
        ]
        mock_build.return_value = mock_service

        # Create services
        gmail_service = GmailService(
            token_path="token.json",
            credentials_path="credentials.json"
        )
        storage_service = StorageService()
        tz_service = TimeZoneService("America/New_York")
        reminder_service = ReminderService(gmail_service, storage_service, tz_service)

        # Create task with 2 reminders
        future_time = datetime.now() + timedelta(hours=4)
        task = Task(
            id=4,
            title="Critical task",
            due_date=future_time,
            due_time=future_time.time(),
            reminder_settings=[
                ReminderSetting(offset_minutes=30, label="30 min"),
                ReminderSetting(offset_minutes=60, label="1 hour")
            ]
        )

        # Schedule reminders
        reminders = reminder_service.schedule_reminders(task)
        assert len(reminders) == 2
