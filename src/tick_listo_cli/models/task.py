from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"


class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Task:
    """
    Enhanced task entity with priority, categories, and due date.

    Attributes:
        id: Auto-generated sequential unique identifier
        title: Task title (required, max 200 characters)
        description: Task description (optional, max 1000 characters)
        completed: Boolean indicating completion status (default: False)
        priority: Task priority level (high/medium/low, default: medium)
        categories: List of category tags (default: empty list)
        due_date: Optional due date for the task
        status: Task status enum ('pending', 'in-progress', 'completed') (default: 'pending')
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
    status: TaskStatus = TaskStatus.PENDING
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
            "status": self.status.value,
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
        # Handle both old and new timestamp field names
        created_at = data.get("created_at") or data.get("created_timestamp")
        updated_at = data.get("updated_at") or data.get("updated_timestamp")

        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            completed=data.get("completed", False),
            priority=Priority(data.get("priority", "medium")),
            categories=data.get("categories", []),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            status=TaskStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(created_at) if created_at else datetime.now(),
            updated_at=datetime.fromisoformat(updated_at) if updated_at else datetime.now()
        )