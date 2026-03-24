from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ProgressStats:
    """
    Statistics for task completion and progress tracking.

    Attributes:
        total_tasks: Total number of tasks
        completed_tasks: Number of completed tasks
        pending_tasks: Number of pending tasks
        in_progress_tasks: Number of in-progress tasks
        completion_percentage: Percentage of completed tasks (0-100)
        last_updated: When stats were last calculated
    """
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    in_progress_tasks: int = 0
    completion_percentage: float = 0.0
    last_updated: datetime = None

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.last_updated is None:
            self.last_updated = datetime.now()

        # Validate that counts are non-negative
        if any(count < 0 for count in [self.total_tasks, self.completed_tasks,
                                      self.pending_tasks, self.in_progress_tasks]):
            raise ValueError("Task counts must be non-negative")

        # Validate that the sum of individual counts equals total_tasks
        calculated_total = self.completed_tasks + self.pending_tasks + self.in_progress_tasks
        if self.total_tasks != calculated_total:
            raise ValueError(f"Total tasks ({self.total_tasks}) must equal sum of individual counts ({calculated_total})")

        # Validate completion percentage
        if self.completion_percentage < 0 or self.completion_percentage > 100:
            raise ValueError("Completion percentage must be between 0 and 100")

        # Recalculate percentage if total_tasks > 0
        if self.total_tasks > 0:
            calculated_percentage = (self.completed_tasks / self.total_tasks) * 100
            # Round to 2 decimal places
            self.completion_percentage = round(calculated_percentage, 2)
        else:
            self.completion_percentage = 0.0

    def update_counts(self, completed: int, pending: int, in_progress: int):
        """Update the task counts and recalculate the completion percentage."""
        if any(count < 0 for count in [completed, pending, in_progress]):
            raise ValueError("Task counts must be non-negative")

        self.completed_tasks = completed
        self.pending_tasks = pending
        self.in_progress_tasks = in_progress
        self.total_tasks = completed + pending + in_progress

        if self.total_tasks > 0:
            calculated_percentage = (self.completed_tasks / self.total_tasks) * 100
            self.completion_percentage = round(calculated_percentage, 2)
        else:
            self.completion_percentage = 0.0

        self.last_updated = datetime.now()

    def to_dict(self) -> dict:
        """
        Convert the progress stats to a dictionary for serialization.

        Returns:
            Dictionary representation of the progress stats
        """
        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "pending_tasks": self.pending_tasks,
            "in_progress_tasks": self.in_progress_tasks,
            "completion_percentage": self.completion_percentage,
            "last_updated": self.last_updated.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a ProgressStats instance from a dictionary.

        Args:
            data: Dictionary containing progress stats data

        Returns:
            ProgressStats instance
        """
        return cls(
            total_tasks=data["total_tasks"],
            completed_tasks=data["completed_tasks"],
            pending_tasks=data["pending_tasks"],
            in_progress_tasks=data["in_progress_tasks"],
            completion_percentage=data["completion_percentage"],
            last_updated=datetime.fromisoformat(data["last_updated"])
        )