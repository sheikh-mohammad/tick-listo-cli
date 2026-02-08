from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ReminderStatus(str, Enum):
    """Status of an email reminder."""
    PENDING = "pending"      # Scheduled, not yet sent
    SENDING = "sending"      # Currently being sent
    SENT = "sent"           # Successfully delivered
    FAILED = "failed"       # Failed after max retries
    CANCELLED = "cancelled"  # Task completed/deleted


@dataclass
class ReminderSetting:
    """
    Configuration for a single reminder time relative to task due date/time.

    Attributes:
        offset_minutes: Minutes before due time to send reminder (e.g., 60 = 1 hour before)
        label: Human-readable label (e.g., "1 hour before", "1 day before")
    """
    offset_minutes: int
    label: str = ""

    def __post_init__(self):
        """Validate reminder setting."""
        if self.offset_minutes <= 0:
            raise ValueError("offset_minutes must be greater than 0")

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "offset_minutes": self.offset_minutes,
            "label": self.label
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create ReminderSetting from dictionary."""
        return cls(
            offset_minutes=data["offset_minutes"],
            label=data.get("label", "")
        )


@dataclass
class EmailReminder:
    """
    Represents a scheduled email reminder for a task.

    Attributes:
        id: Unique reminder identifier (UUID)
        task_id: Associated task ID
        scheduled_time: When to send reminder (UTC)
        offset_minutes: Minutes before due time
        status: Reminder status
        retry_count: Number of send attempts
        last_attempt_time: Timestamp of last send attempt
        error_message: Error from last failed attempt
        sent_time: Timestamp when successfully sent
    """
    id: str
    task_id: int
    scheduled_time: datetime
    offset_minutes: int
    status: ReminderStatus = ReminderStatus.PENDING
    retry_count: int = 0
    last_attempt_time: Optional[datetime] = None
    error_message: Optional[str] = None
    sent_time: Optional[datetime] = None

    def __post_init__(self):
        """Validate email reminder."""
        if self.retry_count < 0:
            raise ValueError("retry_count cannot be negative")
        if self.retry_count > 3:
            raise ValueError("retry_count cannot exceed 3")

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "scheduled_time": self.scheduled_time.isoformat(),
            "offset_minutes": self.offset_minutes,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "last_attempt_time": self.last_attempt_time.isoformat() if self.last_attempt_time else None,
            "error_message": self.error_message,
            "sent_time": self.sent_time.isoformat() if self.sent_time else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create EmailReminder from dictionary."""
        return cls(
            id=data["id"],
            task_id=data["task_id"],
            scheduled_time=datetime.fromisoformat(data["scheduled_time"]),
            offset_minutes=data["offset_minutes"],
            status=ReminderStatus(data.get("status", "pending")),
            retry_count=data.get("retry_count", 0),
            last_attempt_time=datetime.fromisoformat(data["last_attempt_time"]) if data.get("last_attempt_time") else None,
            error_message=data.get("error_message"),
            sent_time=datetime.fromisoformat(data["sent_time"]) if data.get("sent_time") else None
        )
