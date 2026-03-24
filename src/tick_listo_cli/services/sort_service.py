"""
SortService for task sorting functionality.
Provides sorting by due date, priority, and title with secondary sort options.
"""
from typing import List, Optional
from datetime import datetime
from ..models.task import Task, Priority


class SortService:
    """Service for sorting tasks by various criteria."""

    # Priority order mapping for sorting
    PRIORITY_ORDER = {
        Priority.HIGH: 0,
        Priority.MEDIUM: 1,
        Priority.LOW: 2
    }

    def sort_tasks(
        self,
        tasks: List[Task],
        sort_by: str,
        secondary_sort: Optional[str] = None
    ) -> List[Task]:
        """
        Sort tasks by specified criteria.

        Args:
            tasks: List of tasks to sort
            sort_by: Primary sort criteria ("due_date", "priority", "title")
            secondary_sort: Optional secondary sort criteria

        Returns:
            Sorted list of tasks

        Raises:
            ValueError: If sort criteria is invalid
        """
        if not tasks:
            return []

        valid_criteria = ["due_date", "priority", "title"]
        if sort_by not in valid_criteria:
            raise ValueError(
                f"Invalid sort criteria: {sort_by}. "
                f"Must be one of: {', '.join(valid_criteria)}"
            )

        if secondary_sort and secondary_sort not in valid_criteria:
            raise ValueError(
                f"Invalid secondary sort criteria: {secondary_sort}. "
                f"Must be one of: {', '.join(valid_criteria)}"
            )

        # Create sort key function based on criteria
        if sort_by == "due_date":
            return self._sort_by_due_date(tasks, secondary_sort)
        elif sort_by == "priority":
            return self._sort_by_priority(tasks, secondary_sort)
        elif sort_by == "title":
            return self._sort_by_title(tasks, secondary_sort)

        return tasks

    def _sort_by_due_date(
        self,
        tasks: List[Task],
        secondary_sort: Optional[str] = None
    ) -> List[Task]:
        """Sort tasks by due date, with tasks without due dates at the end."""
        def sort_key(task: Task):
            # Tasks without due dates go to the end
            if task.due_date is None:
                # Use a very large datetime for tasks without due dates
                primary = datetime.max
            else:
                primary = task.due_date

            # Apply secondary sort if specified
            if secondary_sort == "priority":
                secondary = self.PRIORITY_ORDER.get(task.priority, 999)
            elif secondary_sort == "title":
                secondary = task.title.lower()
            else:
                secondary = 0

            return (primary, secondary)

        return sorted(tasks, key=sort_key)

    def _sort_by_priority(
        self,
        tasks: List[Task],
        secondary_sort: Optional[str] = None
    ) -> List[Task]:
        """Sort tasks by priority (HIGH > MEDIUM > LOW)."""
        def sort_key(task: Task):
            primary = self.PRIORITY_ORDER.get(task.priority, 999)

            # Apply secondary sort if specified
            if secondary_sort == "due_date":
                if task.due_date is None:
                    secondary = datetime.max
                else:
                    secondary = task.due_date
            elif secondary_sort == "title":
                secondary = task.title.lower()
            else:
                secondary = 0

            return (primary, secondary)

        return sorted(tasks, key=sort_key)

    def _sort_by_title(
        self,
        tasks: List[Task],
        secondary_sort: Optional[str] = None
    ) -> List[Task]:
        """Sort tasks alphabetically by title (case-insensitive)."""
        def sort_key(task: Task):
            primary = task.title.lower()

            # Apply secondary sort if specified
            if secondary_sort == "priority":
                secondary = self.PRIORITY_ORDER.get(task.priority, 999)
            elif secondary_sort == "due_date":
                if task.due_date is None:
                    secondary = datetime.max
                else:
                    secondary = task.due_date
            else:
                secondary = 0

            return (primary, secondary)

        return sorted(tasks, key=sort_key)
