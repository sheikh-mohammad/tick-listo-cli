"""Unit tests for ReminderService (T057-T061 - User Story 4)."""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, time, timedelta
import threading
from ticklisto.models.task import Task, Priority
from ticklisto.models.reminder import EmailReminder, ReminderStatus, ReminderSetting


class TestReminderServiceScheduling:
    """Unit tests for ReminderService.schedule_reminders() (T057)."""

    def test_schedule_reminders_creates_email_reminders(self):
        """Test that schedule_reminders creates EmailReminder objects for each ReminderSetting."""
        from ticklisto.services.reminder_service import ReminderService

        # Mock dependencies
        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Create task with reminder settings
        due_datetime = datetime(2026, 2, 15, 14, 30, 0)
        task = Task(
            id=1,
            title="Test task",
            due_date=due_datetime,
            due_time=time(14, 30),
            reminder_settings=[
                ReminderSetting(offset_minutes=60, label="1 hour before"),
                ReminderSetting(offset_minutes=1440, label="1 day before")
            ]
        )

        # Schedule reminders
        reminders = service.schedule_reminders(task)

        # Should create 2 reminders
        assert len(reminders) == 2
        assert all(isinstance(r, EmailReminder) for r in reminders)
        assert reminders[0].task_id == 1
        assert reminders[0].offset_minutes == 60
        assert reminders[1].offset_minutes == 1440

    def test_schedule_reminders_calculates_correct_times(self):
        """Test that reminder scheduled times are calculated correctly."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        # Mock timezone conversion to return UTC
        def to_utc_side_effect(dt, tz):
            return dt
        mock_timezone.to_utc.side_effect = to_utc_side_effect

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Task due at 2:30 PM
        due_datetime = datetime(2026, 2, 15, 14, 30, 0)
        task = Task(
            id=1,
            title="Test task",
            due_date=due_datetime,
            due_time=time(14, 30),
            reminder_settings=[
                ReminderSetting(offset_minutes=60, label="1 hour before")
            ]
        )

        reminders = service.schedule_reminders(task)

        # Reminder should be scheduled for 1:30 PM (1 hour before 2:30 PM)
        expected_time = datetime(2026, 2, 15, 13, 30, 0)
        assert reminders[0].scheduled_time == expected_time

    def test_schedule_reminders_skips_past_reminders(self):
        """Test that reminders in the past are not scheduled."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        def to_utc_side_effect(dt, tz):
            return dt
        mock_timezone.to_utc.side_effect = to_utc_side_effect

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Task due in the past
        past_datetime = datetime.now() - timedelta(hours=2)
        task = Task(
            id=1,
            title="Past task",
            due_date=past_datetime,
            due_time=past_datetime.time(),
            reminder_settings=[
                ReminderSetting(offset_minutes=60, label="1 hour before")
            ]
        )

        reminders = service.schedule_reminders(task)

        # Should not create reminders for past tasks
        assert len(reminders) == 0

    def test_schedule_reminders_without_due_time_returns_empty(self):
        """Test that tasks without due_time don't get reminders."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Task without due_time
        task = Task(
            id=1,
            title="No time task",
            due_date=datetime(2026, 2, 15),
            reminder_settings=[
                ReminderSetting(offset_minutes=60, label="1 hour before")
            ]
        )

        reminders = service.schedule_reminders(task)

        # Should not create reminders
        assert len(reminders) == 0


class TestReminderServiceCancellation:
    """Unit tests for ReminderService.cancel_reminders() (T058)."""

    def test_cancel_reminders_marks_as_cancelled(self):
        """Test that cancel_reminders marks all task reminders as cancelled."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Add some reminders to the queue
        reminder1 = EmailReminder(
            id="rem-1",
            task_id=1,
            scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
            offset_minutes=60,
            status=ReminderStatus.PENDING
        )
        reminder2 = EmailReminder(
            id="rem-2",
            task_id=1,
            scheduled_time=datetime(2026, 2, 14, 14, 30, 0),
            offset_minutes=1440,
            status=ReminderStatus.PENDING
        )
        service._reminder_queue = [reminder1, reminder2]

        # Cancel reminders for task 1
        service.cancel_reminders(task_id=1)

        # Both reminders should be cancelled
        assert reminder1.status == ReminderStatus.CANCELLED
        assert reminder2.status == ReminderStatus.CANCELLED

    def test_cancel_reminders_only_affects_specified_task(self):
        """Test that cancel_reminders only cancels reminders for the specified task."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Add reminders for different tasks
        reminder1 = EmailReminder(
            id="rem-1",
            task_id=1,
            scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
            offset_minutes=60,
            status=ReminderStatus.PENDING
        )
        reminder2 = EmailReminder(
            id="rem-2",
            task_id=2,
            scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
            offset_minutes=60,
            status=ReminderStatus.PENDING
        )
        service._reminder_queue = [reminder1, reminder2]

        # Cancel reminders for task 1 only
        service.cancel_reminders(task_id=1)

        # Only task 1's reminder should be cancelled
        assert reminder1.status == ReminderStatus.CANCELLED
        assert reminder2.status == ReminderStatus.PENDING


class TestReminderServiceQueueManagement:
    """Unit tests for reminder queue management (T059)."""

    def test_reminder_queue_stores_pending_reminders(self):
        """Test that reminder queue stores pending reminders."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Initially empty
        assert len(service._reminder_queue) == 0

        # Add a reminder
        reminder = EmailReminder(
            id="rem-1",
            task_id=1,
            scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
            offset_minutes=60
        )
        service._reminder_queue.append(reminder)

        assert len(service._reminder_queue) == 1
        assert service._reminder_queue[0] == reminder

    def test_get_pending_reminders_filters_by_status(self):
        """Test that get_pending_reminders returns only pending reminders."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Add reminders with different statuses
        service._reminder_queue = [
            EmailReminder(
                id="rem-1",
                task_id=1,
                scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
                offset_minutes=60,
                status=ReminderStatus.PENDING
            ),
            EmailReminder(
                id="rem-2",
                task_id=2,
                scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
                offset_minutes=60,
                status=ReminderStatus.SENT
            ),
            EmailReminder(
                id="rem-3",
                task_id=3,
                scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
                offset_minutes=60,
                status=ReminderStatus.CANCELLED
            )
        ]

        pending = service.get_pending_reminders()

        # Should only return pending reminder
        assert len(pending) == 1
        assert pending[0].id == "rem-1"

    def test_get_failed_reminders_filters_by_status(self):
        """Test that get_failed_reminders returns only failed reminders."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Add reminders with different statuses
        service._reminder_queue = [
            EmailReminder(
                id="rem-1",
                task_id=1,
                scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
                offset_minutes=60,
                status=ReminderStatus.PENDING
            ),
            EmailReminder(
                id="rem-2",
                task_id=2,
                scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
                offset_minutes=60,
                status=ReminderStatus.FAILED
            ),
            EmailReminder(
                id="rem-3",
                task_id=3,
                scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
                offset_minutes=60,
                status=ReminderStatus.FAILED
            )
        ]

        failed = service.get_failed_reminders()

        # Should return both failed reminders
        assert len(failed) == 2
        assert all(r.status == ReminderStatus.FAILED for r in failed)


class TestReminderServiceStatus:
    """Unit tests for ReminderService.get_status() (T069)."""

    def test_get_status_returns_counts(self):
        """Test that get_status returns pending and failed counts."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Add reminders with various statuses
        service._reminder_queue = [
            EmailReminder(
                id="rem-1",
                task_id=1,
                scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
                offset_minutes=60,
                status=ReminderStatus.PENDING
            ),
            EmailReminder(
                id="rem-2",
                task_id=2,
                scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
                offset_minutes=60,
                status=ReminderStatus.PENDING
            ),
            EmailReminder(
                id="rem-3",
                task_id=3,
                scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
                offset_minutes=60,
                status=ReminderStatus.FAILED
            ),
            EmailReminder(
                id="rem-4",
                task_id=4,
                scheduled_time=datetime(2026, 2, 15, 13, 30, 0),
                offset_minutes=60,
                status=ReminderStatus.SENT
            )
        ]

        status = service.get_status()

        assert status['pending_count'] == 2
        assert status['failed_count'] == 1
        assert status['total_count'] == 4


class TestMultipleRemindersPerTask:
    """Unit tests for multiple reminders per task (T088 - User Story 6)."""

    def test_task_with_multiple_reminder_settings(self):
        """Test that a task can have multiple reminder settings configured."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        def to_utc_side_effect(dt, tz):
            return dt
        mock_timezone.to_utc.side_effect = to_utc_side_effect

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Task with 4 different reminder settings
        due_datetime = datetime(2026, 2, 20, 15, 0, 0)
        task = Task(
            id=1,
            title="Important meeting",
            due_date=due_datetime,
            due_time=time(15, 0),
            reminder_settings=[
                ReminderSetting(offset_minutes=10, label="10 minutes before"),
                ReminderSetting(offset_minutes=60, label="1 hour before"),
                ReminderSetting(offset_minutes=1440, label="1 day before"),
                ReminderSetting(offset_minutes=10080, label="1 week before")
            ]
        )

        reminders = service.schedule_reminders(task)

        # Should create 4 separate reminders
        assert len(reminders) == 4
        assert all(isinstance(r, EmailReminder) for r in reminders)
        assert all(r.task_id == 1 for r in reminders)

        # Verify each reminder has correct offset
        offsets = [r.offset_minutes for r in reminders]
        assert 10 in offsets
        assert 60 in offsets
        assert 1440 in offsets
        assert 10080 in offsets

    def test_multiple_reminders_have_different_scheduled_times(self):
        """Test that multiple reminders for same task have different scheduled times."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        def to_utc_side_effect(dt, tz):
            return dt
        mock_timezone.to_utc.side_effect = to_utc_side_effect

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Task due at 3:00 PM on Feb 20
        due_datetime = datetime(2026, 2, 20, 15, 0, 0)
        task = Task(
            id=1,
            title="Test task",
            due_date=due_datetime,
            due_time=time(15, 0),
            reminder_settings=[
                ReminderSetting(offset_minutes=30, label="30 min before"),
                ReminderSetting(offset_minutes=120, label="2 hours before"),
                ReminderSetting(offset_minutes=1440, label="1 day before")
            ]
        )

        reminders = service.schedule_reminders(task)

        # Extract scheduled times
        scheduled_times = [r.scheduled_time for r in reminders]

        # Should have 3 different times
        assert len(set(scheduled_times)) == 3

        # Verify specific times
        # 30 min before: 2:30 PM
        assert datetime(2026, 2, 20, 14, 30, 0) in scheduled_times
        # 2 hours before: 1:00 PM
        assert datetime(2026, 2, 20, 13, 0, 0) in scheduled_times
        # 1 day before: 3:00 PM on Feb 19
        assert datetime(2026, 2, 19, 15, 0, 0) in scheduled_times

    def test_cancel_reminders_cancels_all_task_reminders(self):
        """Test that cancelling reminders cancels all reminders for a task."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Add multiple reminders for same task
        service._reminder_queue = [
            EmailReminder(
                id="rem-1",
                task_id=1,
                scheduled_time=datetime(2026, 2, 20, 14, 30, 0),
                offset_minutes=30,
                status=ReminderStatus.PENDING
            ),
            EmailReminder(
                id="rem-2",
                task_id=1,
                scheduled_time=datetime(2026, 2, 20, 13, 0, 0),
                offset_minutes=120,
                status=ReminderStatus.PENDING
            ),
            EmailReminder(
                id="rem-3",
                task_id=1,
                scheduled_time=datetime(2026, 2, 19, 15, 0, 0),
                offset_minutes=1440,
                status=ReminderStatus.PENDING
            ),
            EmailReminder(
                id="rem-4",
                task_id=2,
                scheduled_time=datetime(2026, 2, 20, 14, 0, 0),
                offset_minutes=60,
                status=ReminderStatus.PENDING
            )
        ]

        # Cancel all reminders for task 1
        service.cancel_reminders(task_id=1)

        # All 3 reminders for task 1 should be cancelled
        task1_reminders = [r for r in service._reminder_queue if r.task_id == 1]
        assert all(r.status == ReminderStatus.CANCELLED for r in task1_reminders)
        assert len(task1_reminders) == 3

        # Task 2's reminder should remain pending
        task2_reminders = [r for r in service._reminder_queue if r.task_id == 2]
        assert task2_reminders[0].status == ReminderStatus.PENDING

    def test_empty_reminder_settings_creates_no_reminders(self):
        """Test that task with empty reminder_settings list creates no reminders."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Task with empty reminder settings
        task = Task(
            id=1,
            title="No reminders task",
            due_date=datetime(2026, 2, 20, 15, 0, 0),
            due_time=time(15, 0),
            reminder_settings=[]
        )

        reminders = service.schedule_reminders(task)

        assert len(reminders) == 0

    def test_some_reminders_in_past_only_schedules_future_ones(self):
        """Test that only future reminders are scheduled when some are in the past."""
        from ticklisto.services.reminder_service import ReminderService

        mock_gmail = Mock()
        mock_storage = Mock()
        mock_timezone = Mock()

        def to_utc_side_effect(dt, tz):
            return dt
        mock_timezone.to_utc.side_effect = to_utc_side_effect

        service = ReminderService(mock_gmail, mock_storage, mock_timezone)

        # Task due 30 minutes from now (use UTC to match reminder service)
        now = datetime.utcnow()
        due_datetime = now + timedelta(minutes=30)
        task = Task(
            id=1,
            title="Soon task",
            due_date=due_datetime,
            due_time=due_datetime.time(),
            reminder_settings=[
                ReminderSetting(offset_minutes=10, label="10 min before"),  # Future
                ReminderSetting(offset_minutes=60, label="1 hour before"),  # Past
                ReminderSetting(offset_minutes=1440, label="1 day before")  # Past
            ]
        )

        reminders = service.schedule_reminders(task)

        # Should only schedule the 10-minute reminder (future)
        assert len(reminders) == 1
        assert reminders[0].offset_minutes == 10
