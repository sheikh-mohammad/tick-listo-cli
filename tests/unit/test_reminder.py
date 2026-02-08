"""Unit tests for EmailReminder entity (T043 - User Story 3)."""

import pytest
from datetime import datetime
from ticklisto.models.reminder import EmailReminder, ReminderStatus, ReminderSetting


class TestReminderSetting:
    """Unit tests for ReminderSetting value object."""

    def test_create_reminder_setting(self):
        """Test creating a reminder setting."""
        setting = ReminderSetting(offset_minutes=60, label="1 hour before")

        assert setting.offset_minutes == 60
        assert setting.label == "1 hour before"

    def test_reminder_setting_requires_positive_offset(self):
        """Test that offset_minutes must be positive."""
        with pytest.raises(ValueError, match="offset_minutes must be greater than 0"):
            ReminderSetting(offset_minutes=0, label="Invalid")

        with pytest.raises(ValueError, match="offset_minutes must be greater than 0"):
            ReminderSetting(offset_minutes=-60, label="Invalid")

    def test_reminder_setting_serialization(self):
        """Test ReminderSetting to_dict() and from_dict()."""
        setting = ReminderSetting(offset_minutes=1440, label="1 day before")

        data = setting.to_dict()
        assert data == {
            "offset_minutes": 1440,
            "label": "1 day before"
        }

        restored = ReminderSetting.from_dict(data)
        assert restored.offset_minutes == setting.offset_minutes
        assert restored.label == setting.label

    def test_reminder_setting_default_label(self):
        """Test ReminderSetting with default empty label."""
        setting = ReminderSetting(offset_minutes=30)
        assert setting.label == ""


class TestEmailReminder:
    """Unit tests for EmailReminder entity."""

    def test_create_email_reminder(self):
        """Test creating an email reminder."""
        scheduled_time = datetime(2026, 2, 15, 13, 30, 0)
        reminder = EmailReminder(
            id="rem-001",
            task_id=1,
            scheduled_time=scheduled_time,
            offset_minutes=60
        )

        assert reminder.id == "rem-001"
        assert reminder.task_id == 1
        assert reminder.scheduled_time == scheduled_time
        assert reminder.offset_minutes == 60
        assert reminder.status == ReminderStatus.PENDING
        assert reminder.retry_count == 0
        assert reminder.last_attempt_time is None
        assert reminder.error_message is None
        assert reminder.sent_time is None

    def test_email_reminder_with_all_fields(self):
        """Test creating email reminder with all fields."""
        scheduled_time = datetime(2026, 2, 15, 13, 30, 0)
        last_attempt = datetime(2026, 2, 15, 13, 31, 0)
        sent_time = datetime(2026, 2, 15, 13, 32, 0)

        reminder = EmailReminder(
            id="rem-002",
            task_id=2,
            scheduled_time=scheduled_time,
            offset_minutes=1440,
            status=ReminderStatus.SENT,
            retry_count=1,
            last_attempt_time=last_attempt,
            error_message=None,
            sent_time=sent_time
        )

        assert reminder.status == ReminderStatus.SENT
        assert reminder.retry_count == 1
        assert reminder.last_attempt_time == last_attempt
        assert reminder.sent_time == sent_time

    def test_email_reminder_validates_retry_count(self):
        """Test that retry_count is validated."""
        scheduled_time = datetime(2026, 2, 15, 13, 30, 0)

        # Negative retry count
        with pytest.raises(ValueError, match="retry_count cannot be negative"):
            EmailReminder(
                id="rem-003",
                task_id=3,
                scheduled_time=scheduled_time,
                offset_minutes=60,
                retry_count=-1
            )

        # Retry count exceeds max (3)
        with pytest.raises(ValueError, match="retry_count cannot exceed 3"):
            EmailReminder(
                id="rem-004",
                task_id=4,
                scheduled_time=scheduled_time,
                offset_minutes=60,
                retry_count=4
            )

    def test_email_reminder_serialization(self):
        """Test EmailReminder to_dict() and from_dict()."""
        scheduled_time = datetime(2026, 2, 15, 13, 30, 0)
        last_attempt = datetime(2026, 2, 15, 13, 31, 0)

        reminder = EmailReminder(
            id="rem-005",
            task_id=5,
            scheduled_time=scheduled_time,
            offset_minutes=60,
            status=ReminderStatus.FAILED,
            retry_count=3,
            last_attempt_time=last_attempt,
            error_message="Rate limit exceeded"
        )

        data = reminder.to_dict()

        assert data["id"] == "rem-005"
        assert data["task_id"] == 5
        assert data["scheduled_time"] == scheduled_time.isoformat()
        assert data["offset_minutes"] == 60
        assert data["status"] == "failed"
        assert data["retry_count"] == 3
        assert data["last_attempt_time"] == last_attempt.isoformat()
        assert data["error_message"] == "Rate limit exceeded"
        assert data["sent_time"] is None

        # Test deserialization
        restored = EmailReminder.from_dict(data)
        assert restored.id == reminder.id
        assert restored.task_id == reminder.task_id
        assert restored.scheduled_time == reminder.scheduled_time
        assert restored.offset_minutes == reminder.offset_minutes
        assert restored.status == reminder.status
        assert restored.retry_count == reminder.retry_count
        assert restored.last_attempt_time == reminder.last_attempt_time
        assert restored.error_message == reminder.error_message
        assert restored.sent_time is None

    def test_email_reminder_serialization_with_sent_time(self):
        """Test EmailReminder serialization with sent_time."""
        scheduled_time = datetime(2026, 2, 15, 13, 30, 0)
        sent_time = datetime(2026, 2, 15, 13, 32, 0)

        reminder = EmailReminder(
            id="rem-006",
            task_id=6,
            scheduled_time=scheduled_time,
            offset_minutes=60,
            status=ReminderStatus.SENT,
            sent_time=sent_time
        )

        data = reminder.to_dict()
        assert data["sent_time"] == sent_time.isoformat()

        restored = EmailReminder.from_dict(data)
        assert restored.sent_time == sent_time

    def test_email_reminder_status_transitions(self):
        """Test valid status transitions."""
        scheduled_time = datetime(2026, 2, 15, 13, 30, 0)

        # PENDING -> SENDING
        reminder = EmailReminder(
            id="rem-007",
            task_id=7,
            scheduled_time=scheduled_time,
            offset_minutes=60,
            status=ReminderStatus.PENDING
        )
        assert reminder.status == ReminderStatus.PENDING

        # SENDING -> SENT
        reminder.status = ReminderStatus.SENDING
        assert reminder.status == ReminderStatus.SENDING

        reminder.status = ReminderStatus.SENT
        assert reminder.status == ReminderStatus.SENT

        # PENDING -> FAILED
        reminder2 = EmailReminder(
            id="rem-008",
            task_id=8,
            scheduled_time=scheduled_time,
            offset_minutes=60,
            status=ReminderStatus.PENDING
        )
        reminder2.status = ReminderStatus.FAILED
        assert reminder2.status == ReminderStatus.FAILED

        # PENDING -> CANCELLED
        reminder3 = EmailReminder(
            id="rem-009",
            task_id=9,
            scheduled_time=scheduled_time,
            offset_minutes=60,
            status=ReminderStatus.PENDING
        )
        reminder3.status = ReminderStatus.CANCELLED
        assert reminder3.status == ReminderStatus.CANCELLED
