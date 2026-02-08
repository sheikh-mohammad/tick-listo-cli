"""RecurringSeries entity for managing recurring task instances."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


@dataclass
class RecurringSeries:
    """
    Represents a series of recurring task instances.

    Attributes:
        series_id: Unique series identifier (UUID)
        base_task_id: ID of the original/template task
        recurrence_pattern: Pattern for recurrence
        recurrence_interval: Interval multiplier
        recurrence_weekdays: Specific weekdays for custom patterns
        recurrence_end_date: Optional end date for series
        active_instance_ids: IDs of current/future task instances
        completed_instance_ids: IDs of completed task instances
        created_at: Series creation timestamp
        last_generated_at: When last instance was created
    """
    series_id: str
    base_task_id: int
    recurrence_pattern: str
    recurrence_interval: int = 1
    recurrence_weekdays: Optional[List[int]] = None
    recurrence_end_date: Optional[datetime] = None
    active_instance_ids: List[int] = field(default_factory=list)
    completed_instance_ids: List[int] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_generated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate recurring series."""
        if self.recurrence_interval < 1:
            raise ValueError("recurrence_interval must be >= 1")

        if self.recurrence_weekdays is not None:
            for day in self.recurrence_weekdays:
                if not (0 <= day <= 6):
                    raise ValueError("recurrence_weekdays values must be 0-6")

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "series_id": self.series_id,
            "base_task_id": self.base_task_id,
            "recurrence_pattern": self.recurrence_pattern,
            "recurrence_interval": self.recurrence_interval,
            "recurrence_weekdays": self.recurrence_weekdays,
            "recurrence_end_date": self.recurrence_end_date.isoformat() if self.recurrence_end_date else None,
            "active_instance_ids": self.active_instance_ids,
            "completed_instance_ids": self.completed_instance_ids,
            "created_at": self.created_at.isoformat(),
            "last_generated_at": self.last_generated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create RecurringSeries from dictionary."""
        return cls(
            series_id=data["series_id"],
            base_task_id=data["base_task_id"],
            recurrence_pattern=data["recurrence_pattern"],
            recurrence_interval=data.get("recurrence_interval", 1),
            recurrence_weekdays=data.get("recurrence_weekdays"),
            recurrence_end_date=datetime.fromisoformat(data["recurrence_end_date"]) if data.get("recurrence_end_date") else None,
            active_instance_ids=data.get("active_instance_ids", []),
            completed_instance_ids=data.get("completed_instance_ids", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            last_generated_at=datetime.fromisoformat(data["last_generated_at"]) if data.get("last_generated_at") else datetime.now()
        )

    def is_active(self) -> bool:
        """Check if series is still active."""
        if self.recurrence_end_date and datetime.now() > self.recurrence_end_date:
            return False
        return True

    def add_active_instance(self, task_id: int):
        """Add a task instance to active list."""
        if task_id not in self.active_instance_ids:
            self.active_instance_ids.append(task_id)

    def mark_instance_completed(self, task_id: int):
        """Move task instance from active to completed."""
        if task_id in self.active_instance_ids:
            self.active_instance_ids.remove(task_id)
        if task_id not in self.completed_instance_ids:
            self.completed_instance_ids.append(task_id)
            # Keep only last 100 completed instances
            if len(self.completed_instance_ids) > 100:
                self.completed_instance_ids = self.completed_instance_ids[-100:]
