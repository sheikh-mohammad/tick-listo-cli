from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .reminder import ReminderSetting


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"


class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecurrencePattern(str, Enum):
    """Recurrence pattern types for recurring tasks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BI_WEEKLY = "bi-weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


@dataclass
class Task:
    """
    Enhanced task entity with priority, categories, due date, time support, recurrence, and reminders.

    Attributes:
        id: Auto-generated sequential unique identifier
        title: Task title (required, max 200 characters)
        description: Task description (optional, max 1000 characters)
        completed: Boolean indicating completion status (default: False)
        priority: Task priority level (high/medium/low, default: medium)
        categories: List of category tags (default: empty list)
        due_date: Optional due date for the task
        due_time: Optional time component (HH:MM)
        status: Task status enum ('pending', 'in-progress', 'completed') (default: 'pending')
        recurrence_pattern: Recurrence type (daily/weekly/monthly/yearly/custom)
        recurrence_interval: Interval multiplier for custom recurrence
        recurrence_weekdays: Weekdays for custom patterns (0=Mon, 6=Sun)
        recurrence_end_date: Optional end date for recurring series
        series_id: UUID linking recurring task instances
        instance_number: Position in recurring series (1, 2, 3...)
        reminder_settings: List of reminder configurations
        created_at: DateTime of creation (auto-generated)
        updated_at: DateTime of last update (auto-generated)
        created_timestamp: DateTime of creation (deprecated, for backward compatibility)
        updated_timestamp: DateTime of last update (deprecated, for backward compatibility)
    """
    id: int
    title: str
    description: str = ""
    completed: bool = False
    priority: Priority = Priority.MEDIUM
    categories: list[str] = field(default_factory=list)
    due_date: Optional[datetime] = None
    due_time: Optional[time] = None
    status: TaskStatus = TaskStatus.PENDING
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_interval: int = 1
    recurrence_weekdays: Optional[list[int]] = None
    recurrence_end_date: Optional[datetime] = None
    series_id: Optional[str] = None
    instance_number: Optional[int] = None
    reminder_settings: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_timestamp: Optional[datetime] = None
    updated_timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        # Backward compatibility: sync old timestamp fields with new ones
        if self.created_timestamp is not None:
            self.created_at = self.created_timestamp
        if self.updated_timestamp is not None:
            self.updated_at = self.updated_timestamp

        # Sync new fields to old fields for backward compatibility
        self.created_timestamp = self.created_at
        self.updated_timestamp = self.updated_at

        # Validate title
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Title cannot exceed 200 characters")

        # Validate description
        if self.description and len(self.description) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")

        # Normalize whitespace
        self.title = self.title.strip()
        self.description = self.description.strip() if self.description else ""

        # Normalize categories (preserve order while deduplicating)
        if self.categories:
            seen = set()
            normalized = []
            for cat in self.categories:
                if not cat or not cat.strip():
                    continue
                cat_lower = cat.strip().lower()
                if cat_lower not in seen:
                    normalized.append(cat_lower)
                    seen.add(cat_lower)
            self.categories = normalized

            # Validate each category length
            for cat in self.categories:
                if len(cat) > 50:
                    raise ValueError(f"Category '{cat}' exceeds 50 characters")

        # Validate recurrence fields
        if self.recurrence_pattern is not None:
            if self.recurrence_interval < 1:
                raise ValueError("recurrence_interval must be >= 1")

        if self.recurrence_weekdays is not None:
            for day in self.recurrence_weekdays:
                if not (0 <= day <= 6):
                    raise ValueError("recurrence_weekdays values must be 0-6")

        if self.instance_number is not None:
            if self.instance_number < 1:
                raise ValueError("instance_number must be >= 1")

        # Validate reminder_settings requires due_time
        if self.reminder_settings and not self.due_time:
            raise ValueError("reminder_settings requires due_time to be set")

    def update_status(self, new_status: TaskStatus):
        """Update the task status and refresh the updated timestamp."""
        self.status = new_status
        self.updated_at = datetime.now()
        self.updated_timestamp = self.updated_at
        # Update completed flag based on status
        self.completed = (new_status == TaskStatus.COMPLETED)

    def mark_complete(self):
        """Mark task as completed and update timestamp."""
        self.completed = True
        self.updated_at = datetime.now()
        self.updated_timestamp = self.updated_at

    def mark_incomplete(self):
        """Mark task as incomplete and update timestamp."""
        self.completed = False
        self.updated_at = datetime.now()
        self.updated_timestamp = self.updated_at

    def update_field(self, field_name: str, value):
        """Update a field and refresh updated_at timestamp."""
        setattr(self, field_name, value)
        self.updated_at = datetime.now()
        self.updated_timestamp = self.updated_at

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date or self.completed:
            return False
        return datetime.now() > self.due_date

    def matches_keyword(self, keyword: str) -> bool:
        """Check if task matches search keyword (case-insensitive)."""
        keyword_lower = keyword.lower()
        return (
            keyword_lower in self.title.lower() or
            keyword_lower in self.description.lower()
        )

    def has_category(self, category: str) -> bool:
        """Check if task has specific category."""
        return category.lower() in self.categories

    def has_any_category(self, categories: list[str]) -> bool:
        """Check if task has any of the specified categories (OR logic)."""
        return any(self.has_category(cat) for cat in categories)

    def has_all_categories(self, categories: list[str]) -> bool:
        """Check if task has all of the specified categories (AND logic)."""
        return all(self.has_category(cat) for cat in categories)

    def update_details(self, title: str = None, description: str = None):
        """Update task details and refresh the updated timestamp."""
        if title is not None:
            if len(title.strip()) == 0:
                raise ValueError("Title must not be empty")
            if len(title) > 200:
                raise ValueError("Title must be 200 characters or less")
            self.title = title.strip()

        if description is not None:
            if len(description) > 1000:
                raise ValueError("Description must be 1000 characters or less")
            self.description = description.strip()

        self.updated_at = datetime.now()
        self.updated_timestamp = self.updated_at

    def to_dict(self) -> dict:
        """
        Convert the task to a dictionary for serialization.

        Returns:
            Dictionary representation of the task
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority.value,
            "categories": self.categories,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "due_time": self.due_time.isoformat() if self.due_time else None,
            "status": self.status.value,
            "recurrence_pattern": self.recurrence_pattern.value if self.recurrence_pattern else None,
            "recurrence_interval": self.recurrence_interval,
            "recurrence_weekdays": self.recurrence_weekdays,
            "recurrence_end_date": self.recurrence_end_date.isoformat() if self.recurrence_end_date else None,
            "series_id": self.series_id,
            "instance_number": self.instance_number,
            "reminder_settings": [rs.to_dict() for rs in self.reminder_settings] if self.reminder_settings else [],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_timestamp": self.created_timestamp.isoformat(),
            "updated_timestamp": self.updated_timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a Task instance from a dictionary.

        Args:
            data: Dictionary containing task data

        Returns:
            Task instance
        """
        # Import here to avoid circular dependency
        from .reminder import ReminderSetting

        # Handle both old and new timestamp field names
        created_at = data.get("created_at") or data.get("created_timestamp")
        updated_at = data.get("updated_at") or data.get("updated_timestamp")

        # Parse due_time if present
        due_time = None
        if data.get("due_time"):
            if isinstance(data["due_time"], str):
                # Parse from ISO format string (HH:MM:SS)
                due_time = time.fromisoformat(data["due_time"])
            else:
                due_time = data["due_time"]

        # Parse recurrence_pattern if present
        recurrence_pattern = None
        if data.get("recurrence_pattern"):
            recurrence_pattern = RecurrencePattern(data["recurrence_pattern"])

        # Parse recurrence_end_date if present
        recurrence_end_date = None
        if data.get("recurrence_end_date"):
            recurrence_end_date = datetime.fromisoformat(data["recurrence_end_date"])

        # Parse reminder_settings if present
        reminder_settings = []
        if data.get("reminder_settings"):
            reminder_settings = [
                ReminderSetting.from_dict(rs) if isinstance(rs, dict) else rs
                for rs in data["reminder_settings"]
            ]

        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            completed=data.get("completed", False),
            priority=Priority(data.get("priority", "medium")),
            categories=data.get("categories", []),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            due_time=due_time,
            status=TaskStatus(data.get("status", "pending")),
            recurrence_pattern=recurrence_pattern,
            recurrence_interval=data.get("recurrence_interval", 1),
            recurrence_weekdays=data.get("recurrence_weekdays"),
            recurrence_end_date=recurrence_end_date,
            series_id=data.get("series_id"),
            instance_number=data.get("instance_number"),
            reminder_settings=reminder_settings,
            created_at=datetime.fromisoformat(created_at) if created_at else datetime.now(),
            updated_at=datetime.fromisoformat(updated_at) if updated_at else datetime.now()
        )