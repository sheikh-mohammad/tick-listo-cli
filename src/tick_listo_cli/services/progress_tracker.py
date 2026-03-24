"""
Progress tracker for calculating completion stats per data-model.md.
"""

from datetime import datetime
from typing import List, Dict
from ..models.task import Task, TaskStatus
from ..models.progress_stats import ProgressStats


class ProgressTracker:
    """
    Progress tracker class for calculating completion stats per data-model.md.
    """

    def __init__(self):
        """
        Initialize the progress tracker.
        """
        self.stats = ProgressStats()
        self.last_updated = datetime.now()

    def calculate_from_task_list(self, tasks: List[Task]) -> Dict[str, int]:
        """
        Calculate progress statistics from a list of tasks.

        Args:
            tasks: List of Task objects

        Returns:
            Dictionary with calculated statistics
        """
        total = len(tasks)
        completed = 0
        pending = 0
        in_progress = 0

        for task in tasks:
            if task.status == TaskStatus.COMPLETED:
                completed += 1
            elif task.status == TaskStatus.IN_PROGRESS:
                in_progress += 1
            else:  # pending
                pending += 1

        # Update the internal stats
        self.stats.update_counts(completed, pending, in_progress)
        self.last_updated = datetime.now()

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "in_progress_tasks": in_progress,
            "completion_percentage": self.stats.completion_percentage
        }

    def get_current_stats(self) -> ProgressStats:
        """
        Get the current progress statistics.

        Returns:
            ProgressStats object with current statistics
        """
        return self.stats

    def get_formatted_stats(self) -> Dict[str, any]:
        """
        Get formatted statistics suitable for display.

        Returns:
            Dictionary with formatted statistics
        """
        return {
            "total_tasks": self.stats.total_tasks,
            "completed_tasks": self.stats.completed_tasks,
            "pending_tasks": self.stats.pending_tasks,
            "in_progress_tasks": self.stats.in_progress_tasks,
            "completion_percentage": self.stats.completion_percentage,
            "last_updated": self.stats.last_updated
        }

    def update_task_completion(self, tasks: List[Task]) -> Dict[str, any]:
        """
        Update progress statistics when tasks change per acceptance scenario in US4.

        Args:
            tasks: Updated list of tasks

        Returns:
            Dictionary with updated statistics
        """
        return self.calculate_from_task_list(tasks)

    def get_completion_summary(self) -> str:
        """
        Get a textual summary of completion status.

        Returns:
            Formatted string with completion summary
        """
        stats = self.get_formatted_stats()
        return (
            f"Total: {stats['total_tasks']}, "
            f"Completed: {stats['completed_tasks']}, "
            f"Pending: {stats['pending_tasks']}, "
            f"In Progress: {stats['in_progress_tasks']}, "
            f"Completion: {stats['completion_percentage']:.1f}%"
        )

    def has_changed_since(self, timestamp: datetime) -> bool:
        """
        Check if progress stats have changed since a given timestamp.

        Args:
            timestamp: The timestamp to compare against

        Returns:
            True if stats have changed since the timestamp, False otherwise
        """
        return self.last_updated > timestamp