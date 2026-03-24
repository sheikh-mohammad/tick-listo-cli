"""
FilterService for task filtering functionality.
Provides filtering by status, priority, categories, and due dates.
"""
from typing import List, Optional
from datetime import datetime
from ..models.task import Task, Priority


class FilterService:
    """Service for filtering tasks by various criteria."""

    def filter_tasks(
        self,
        tasks: List[Task],
        status: Optional[str] = None,
        priority: Optional[Priority] = None,
        categories: Optional[List[str]] = None,
        category_match: str = "any",
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
        overdue: Optional[bool] = None,
        has_due_date: Optional[bool] = None,
        has_categories: Optional[bool] = None
    ) -> List[Task]:
        """
        Filter tasks by multiple criteria.

        Args:
            tasks: List of tasks to filter
            status: Filter by status ("complete" or "incomplete")
            priority: Filter by priority level
            categories: Filter by categories
            category_match: Category match logic ("any" for OR, "all" for AND)
            due_before: Filter tasks due before this date
            due_after: Filter tasks due after this date
            due_date: Filter tasks due on this specific date
            overdue: Filter overdue tasks (True) or non-overdue (False)
            has_due_date: Filter tasks with due date (True) or without (False)
            has_categories: Filter tasks with categories (True) or without (False)

        Returns:
            List of tasks matching all criteria
        """
        results = tasks

        # Filter by status
        if status is not None:
            results = self._filter_by_status(results, status)

        # Filter by priority
        if priority is not None:
            results = self._filter_by_priority(results, priority)

        # Filter by categories
        if categories is not None:
            results = self._filter_by_categories(results, categories, category_match)

        # Filter by has_categories
        if has_categories is not None:
            results = self._filter_by_has_categories(results, has_categories)

        # Filter by due date
        if due_date is not None:
            results = self._filter_by_due_date(results, due_date)

        # Filter by due before
        if due_before is not None:
            results = self._filter_by_due_before(results, due_before)

        # Filter by due after
        if due_after is not None:
            results = self._filter_by_due_after(results, due_after)

        # Filter by overdue
        if overdue is not None:
            results = self._filter_by_overdue(results, overdue)

        # Filter by has_due_date
        if has_due_date is not None:
            results = self._filter_by_has_due_date(results, has_due_date)

        return results

    def _filter_by_status(self, tasks: List[Task], status: str) -> List[Task]:
        """Filter tasks by completion status."""
        if status == "complete":
            return [task for task in tasks if task.completed]
        elif status == "incomplete":
            return [task for task in tasks if not task.completed]
        return tasks

    def _filter_by_priority(self, tasks: List[Task], priority: Priority) -> List[Task]:
        """Filter tasks by priority level."""
        return [task for task in tasks if task.priority == priority]

    def _filter_by_categories(
        self,
        tasks: List[Task],
        categories: List[str],
        match_logic: str
    ) -> List[Task]:
        """Filter tasks by categories with OR/AND logic."""
        if not categories:
            return tasks

        if match_logic == "any":
            # OR logic: task must have at least one of the categories
            return [task for task in tasks if task.has_any_category(categories)]
        elif match_logic == "all":
            # AND logic: task must have all of the categories
            return [task for task in tasks if task.has_all_categories(categories)]

        return tasks

    def _filter_by_has_categories(self, tasks: List[Task], has_categories: bool) -> List[Task]:
        """Filter tasks by whether they have categories or not."""
        if has_categories:
            return [task for task in tasks if task.categories]
        else:
            return [task for task in tasks if not task.categories]

    def _filter_by_due_date(self, tasks: List[Task], due_date: datetime) -> List[Task]:
        """Filter tasks due on a specific date."""
        results = []
        for task in tasks:
            if task.due_date is not None:
                # Compare dates only (ignore time)
                if isinstance(due_date, datetime):
                    target_date = due_date.date()
                else:
                    target_date = due_date

                task_date = task.due_date.date() if isinstance(task.due_date, datetime) else task.due_date

                if task_date == target_date:
                    results.append(task)
        return results

    def _filter_by_due_before(self, tasks: List[Task], due_before: datetime) -> List[Task]:
        """Filter tasks due before a specific date."""
        return [
            task for task in tasks
            if task.due_date is not None and task.due_date <= due_before
        ]

    def _filter_by_due_after(self, tasks: List[Task], due_after: datetime) -> List[Task]:
        """Filter tasks due after a specific date."""
        return [
            task for task in tasks
            if task.due_date is not None and task.due_date >= due_after
        ]

    def _filter_by_overdue(self, tasks: List[Task], overdue: bool) -> List[Task]:
        """Filter overdue or non-overdue tasks."""
        if overdue:
            return [task for task in tasks if task.is_overdue()]
        else:
            return [task for task in tasks if not task.is_overdue()]

    def _filter_by_has_due_date(self, tasks: List[Task], has_due_date: bool) -> List[Task]:
        """Filter tasks by whether they have a due date or not."""
        if has_due_date:
            return [task for task in tasks if task.due_date is not None]
        else:
            return [task for task in tasks if task.due_date is None]
