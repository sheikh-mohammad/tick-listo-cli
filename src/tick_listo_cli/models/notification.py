from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class NotificationType(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Notification:
    """
    Represents a notification or message to be displayed to the user.

    Attributes:
        id: Unique identifier for the notification
        type: Type of notification ('info', 'success', 'warning', 'error')
        title: Notification title
        message: Notification message content
        timestamp: When the notification was created
        duration: Duration to display in milliseconds (default: 3000)
    """
    id: int
    type: NotificationType
    title: str
    message: str
    timestamp: datetime = None
    duration: int = 3000  # Default 3 seconds

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

        # Validate type is one of the allowed values
        if not isinstance(self.type, NotificationType):
            raise ValueError(f"Type must be one of {list(NotificationType)}")

        # Validate message is not empty
        if not self.message or not self.message.strip():
            raise ValueError("Message must not be empty")

        # Validate duration is positive if provided
        if self.duration and self.duration <= 0:
            raise ValueError("Duration must be positive if provided")

        # Normalize title and message
        self.title = self.title.strip()
        self.message = self.message.strip()

    def to_dict(self) -> dict:
        """
        Convert the notification to a dictionary for serialization.

        Returns:
            Dictionary representation of the notification
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "duration": self.duration
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a Notification instance from a dictionary.

        Args:
            data: Dictionary containing notification data

        Returns:
            Notification instance
        """
        return cls(
            id=data["id"],
            type=NotificationType(data["type"]),
            title=data["title"],
            message=data["message"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            duration=data.get("duration", 3000)
        )