"""
SearchService for task search functionality.
Provides keyword-based search across task titles and descriptions.
"""
from typing import List
from ..models.task import Task


class SearchService:
    """Service for searching tasks by keyword."""

    def search_tasks(self, tasks: List[Task], keyword: str) -> List[Task]:
        """
        Search tasks by keyword in title and description.

        Args:
            tasks: List of tasks to search
            keyword: Search keyword (case-insensitive)

        Returns:
            List of tasks matching the keyword
        """
        # Handle empty or whitespace-only keyword
        if not keyword or not keyword.strip():
            return tasks

        keyword_lower = keyword.lower()
        results = []

        for task in tasks:
            if self._task_matches_keyword(task, keyword_lower):
                results.append(task)

        return results

    def search_tasks_with_scope(
        self, tasks: List[Task], keyword: str, scope: str = "both"
    ) -> List[Task]:
        """
        Search tasks by keyword with scope selection (Phase 11 - Enhanced Features).

        Args:
            tasks: List of tasks to search
            keyword: Search keyword (case-insensitive)
            scope: Search scope - "title", "description", or "both" (default: "both")

        Returns:
            List of tasks matching the keyword in the specified scope

        Raises:
            ValueError: If scope is invalid
        """
        # Validate scope
        valid_scopes = ["title", "description", "both"]
        if scope not in valid_scopes:
            raise ValueError(
                f"Invalid scope: '{scope}'. Must be one of: {', '.join(valid_scopes)}"
            )

        # Handle empty or whitespace-only keyword
        if not keyword or not keyword.strip():
            return tasks

        keyword_lower = keyword.lower()
        results = []

        for task in tasks:
            if self._task_matches_keyword_with_scope(task, keyword_lower, scope):
                results.append(task)

        return results

    def _task_matches_keyword(self, task: Task, keyword_lower: str) -> bool:
        """
        Check if a task matches the search keyword.

        Args:
            task: Task to check
            keyword_lower: Lowercase keyword to search for

        Returns:
            True if task matches keyword, False otherwise
        """
        # Search in title
        if keyword_lower in task.title.lower():
            return True

        # Search in description if it exists
        if task.description and keyword_lower in task.description.lower():
            return True

        return False

    def _task_matches_keyword_with_scope(
        self, task: Task, keyword_lower: str, scope: str
    ) -> bool:
        """
        Check if a task matches the search keyword in the specified scope.

        Args:
            task: Task to check
            keyword_lower: Lowercase keyword to search for
            scope: Search scope - "title", "description", or "both"

        Returns:
            True if task matches keyword in scope, False otherwise
        """
        if scope == "title":
            return keyword_lower in task.title.lower()

        elif scope == "description":
            return task.description and keyword_lower in task.description.lower()

        else:  # scope == "both"
            # Search in title
            if keyword_lower in task.title.lower():
                return True

            # Search in description if it exists
            if task.description and keyword_lower in task.description.lower():
                return True

            return False


# Module-level function for backward compatibility and easier testing
def search_tasks_with_scope(
    tasks: List[Task], keyword: str, scope: str = "both"
) -> List[Task]:
    """
    Search tasks by keyword with scope selection.

    Args:
        tasks: List of tasks to search
        keyword: Search keyword (case-insensitive)
        scope: Search scope - "title", "description", or "both" (default: "both")

    Returns:
        List of tasks matching the keyword in the specified scope

    Raises:
        ValueError: If scope is invalid
    """
    service = SearchService()
    return service.search_tasks_with_scope(tasks, keyword, scope)
