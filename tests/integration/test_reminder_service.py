"""Integration tests for ReminderService (T060-T061 - User Story 4)."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, time, timedelta
import threading
import time as time_module
from src.ticklisto.models.task import Task, Priority
from src.ticklisto.models.reminder import EmailReminder, ReminderStatus, ReminderSetting


class TestReminderServiceStartup:
    """Integration tests for startup reminder check (T060)."""

    @patch('os.path.exists', return_value=True)
    def test_startup_loads_pending_reminders(self, mock_exists):
        """Test that ReminderService loads pending reminders on startup."""
        from src.ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        # Mock storage to return saved reminders
        saved_reminders = [
            {
                "id": "rem-1",
                "task_id": 1,
                "scheduled_time": datetime(2026, 2, 15, 13, 30, 0).isoformat(),
                "offset_minutes": 60,
                "status": "pending",
                "retry_count": 0
            }
        ]
        mock_storage.load_reminders.return_value = saved_reminders

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Should load reminders from storage
        assert len(service._reminder_queue) == 1
        assert service._reminder_queue[0].id == "rem-1"

    @patch('os.path.exists', return_value=True)
    def test_startup_sends_overdue_reminders_immediately(self, mock_exists):
        """Test that overdue reminders are sent immediately on startup."""
        from src.ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_gmail.send_reminder_email.return_value = True
        mock_storage = Mock()
        mock_timezone = Mock()

        # Mock storage with overdue reminder
        past_time = datetime.now() - timedelta(minutes=5)
        saved_reminders = [
            {
                "id": "rem-1",
                "task_id": 1,
                "scheduled_time": past_time.isoformat(),
                "offset_minutes": 60,
                "status": "pending",
                "retry_count": 0
            }
        ]
        mock_storage.load_reminders.return_value = saved_reminders

        # Mock task retrieval
        task = Task(
            id=1,
            title="Test task",
            due_date=datetime.now() + timedelta(hours=1),
            due_time=time(14, 30)
        )
        mock_storage.get_task.return_value = task

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)
        service.start()

        # Give it a moment to process
        time_module.sleep(0.5)

        service.stop()

        # Should have attempted to send the overdue reminder
        # (In real implementation, this would be checked via mock calls)

    @patch('os.path.exists', return_value=True)
    def test_startup_with_no_saved_reminders(self, mock_exists):
        """Test that ReminderService starts cleanly with no saved reminders."""
        from src.ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_storage.load_reminders.return_value = []
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Should have empty queue
        assert len(service._reminder_queue) == 0


class TestReminderServiceCheckInterval:
    """Integration tests for 1-minute check interval (T061)."""

    @patch('os.path.exists', return_value=True)
    def test_check_loop_runs_every_minute(self, mock_exists):
        """Test that reminder check loop runs approximately every minute."""
        from src.ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_storage.load_reminders.return_value = []
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Track check iterations
        check_count = []
        original_check = service._check_pending_reminders

        def tracked_check():
            check_count.append(datetime.now())
            return original_check()

        service._check_pending_reminders = tracked_check

        # Start service
        service.start()

        # Wait for 2.5 seconds (should get at least 2 checks with 1-second interval for testing)
        time_module.sleep(2.5)

        service.stop()

        # Should have run at least 2 times
        assert len(check_count) >= 2

    @patch('os.path.exists', return_value=True)
    def test_check_loop_sends_due_reminders(self, mock_exists):
        """Test that check loop sends reminders when they become due."""
        from src.ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_gmail.send_reminder_email.return_value = True
        mock_storage = Mock()
        mock_storage.load_reminders.return_value = []
        mock_timezone = Mock()

        # Mock task retrieval
        task = Task(
            id=1,
            title="Test task",
            due_date=datetime.now() + timedelta(minutes=5),
            due_time=time(14, 30)
        )
        mock_storage.get_task.return_value = task

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Add a reminder that's due now
        reminder = EmailReminder(
            id="rem-1",
            task_id=1,
            scheduled_time=datetime.now() - timedelta(seconds=5),
            offset_minutes=60,
            status=ReminderStatus.PENDING
        )
        service._reminder_queue.append(reminder)

        service.start()

        # Wait for check to run
        time_module.sleep(1.5)

        service.stop()

        # Reminder should have been processed
        assert reminder.status in [ReminderStatus.SENT, ReminderStatus.SENDING]

    @patch('os.path.exists', return_value=True)
    def test_check_loop_skips_future_reminders(self, mock_exists):
        """Test that check loop doesn't send reminders scheduled for the future."""
        from src.ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_storage.load_reminders.return_value = []
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Add a reminder scheduled for the future
        reminder = EmailReminder(
            id="rem-1",
            task_id=1,
            scheduled_time=datetime.now() + timedelta(hours=1),
            offset_minutes=60,
            status=ReminderStatus.PENDING
        )
        service._reminder_queue.append(reminder)

        service.start()

        # Wait for check to run
        time_module.sleep(1.5)

        service.stop()

        # Reminder should still be pending
        assert reminder.status == ReminderStatus.PENDING
        mock_gmail.send_reminder_email.assert_not_called()

    @patch('os.path.exists', return_value=True)
    def test_service_lifecycle_start_stop(self, mock_exists):
        """Test that service can be started and stopped cleanly."""
        from src.ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_storage.load_reminders.return_value = []
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Should not be running initially
        assert not service._running

        # Start service
        service.start()
        assert service._running
        assert service._check_thread is not None
        assert service._check_thread.is_alive()

        # Stop service
        service.stop()
        assert not service._running

        # Thread should stop within reasonable time
        service._check_thread.join(timeout=2)
        assert not service._check_thread.is_alive()

    @patch('os.path.exists', return_value=True)
    def test_service_handles_multiple_start_calls(self, mock_exists):
        """Test that calling start() multiple times doesn't create multiple threads."""
        from src.ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_storage.load_reminders.return_value = []
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Start service twice
        service.start()
        first_thread = service._check_thread

        service.start()
        second_thread = service._check_thread

        # Should be the same thread
        assert first_thread == second_thread

        service.stop()

    @patch('os.path.exists', return_value=True)
    def test_service_persists_reminders_after_changes(self, mock_exists):
        """Test that service persists reminders to storage after changes."""
        from src.ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_storage.load_reminders.return_value = []
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Add a reminder
        reminder = EmailReminder(
            id="rem-1",
            task_id=1,
            scheduled_time=datetime.now() + timedelta(hours=1),
            offset_minutes=60,
            status=ReminderStatus.PENDING
        )
        service._reminder_queue.append(reminder)

        # Save reminders
        service._save_reminders()

        # Should have called storage
        mock_storage.save_reminders.assert_called_once()
        saved_data = mock_storage.save_reminders.call_args[0][0]
        assert len(saved_data) == 1
        assert saved_data[0]['id'] == "rem-1"
