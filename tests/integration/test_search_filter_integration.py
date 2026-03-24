"""
Integration tests for combined search and filter operations.
Following TDD approach - these tests are written FIRST and should FAIL initially.
"""
import pytest
from datetime import datetime, timedelta
from tick_listo_cli.models.task import Task, Priority
from tick_listo_cli.services.search_service import SearchService
from tick_listo_cli.services.filter_service import FilterService


class TestSearchFilterIntegration:
    """Integration tests for combining search and filter operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.search_service = SearchService()
        self.filter_service = FilterService()

        today = datetime.now()
        self.tasks = [
            Task(
                id=1,
                title="Complete project documentation",
                description="Write comprehensive docs for the project",
                priority=Priority.HIGH,
                categories=["work", "documentation"],
                completed=False,
                due_date=today + timedelta(days=3)
            ),
            Task(
                id=2,
                title="Buy groceries for project party",
                description="Milk, eggs, bread, snacks",
                priority=Priority.MEDIUM,
                categories=["home", "shopping"],
                completed=False,
                due_date=today + timedelta(days=1)
            ),
            Task(
                id=3,
                title="Review pull request",
                description="Review the new feature PR for project",
                priority=Priority.HIGH,
                categories=["work", "code-review"],
                completed=True,
                due_date=today - timedelta(days=2)
            ),
            Task(
                id=4,
                title="Schedule dentist appointment",
                description="Call dentist office",
                priority=Priority.LOW,
                categories=["personal", "health"],
                completed=False,
                due_date=today + timedelta(days=30)
            ),
            Task(
                id=5,
                title="Project planning meeting",
                description="Discuss project timeline and milestones",
                priority=Priority.MEDIUM,
                categories=["work", "meeting"],
                completed=False,
                due_date=today + timedelta(days=7)
            ),
            Task(
                id=6,
                title="Update project status report",
                description="Weekly status update",
                priority=Priority.HIGH,
                categories=["work", "documentation"],
                completed=False,
                due_date=today + timedelta(days=2)
            )
        ]

    def test_search_then_filter_by_priority(self):
        """Test searching first, then filtering results by priority."""
        # Search for "project"
        search_results = self.search_service.search_tasks(self.tasks, "project")
        assert len(search_results) == 5

        # Filter search results by high priority
        filtered_results = self.filter_service.filter_tasks(
            search_results,
            priority=Priority.HIGH
        )

        assert len(filtered_results) == 3
        assert all("project" in task.title.lower() or
                   (task.description and "project" in task.description.lower())
                   for task in filtered_results)
        assert all(task.priority == Priority.HIGH for task in filtered_results)

    def test_filter_then_search(self):
        """Test filtering first, then searching within results."""
        # Filter by work category
        filter_results = self.filter_service.filter_tasks(
            self.tasks,
            categories=["work"]
        )
        assert len(filter_results) == 4

        # Search within filtered results for "documentation" in title/description
        search_results = self.search_service.search_tasks(
            filter_results,
            "documentation"
        )

        # Only Task 1 has "documentation" in title (Task 6 has it in categories but not title/description)
        assert len(search_results) == 1
        assert all(task.has_category("work") for task in search_results)
        assert all("documentation" in task.title.lower() or
                   (task.description and "documentation" in task.description.lower())
                   for task in search_results)

    def test_search_filter_by_status_and_priority(self):
        """Test search combined with status and priority filters."""
        # Search for "project"
        search_results = self.search_service.search_tasks(self.tasks, "project")

        # Filter by incomplete status and high priority
        filtered_results = self.filter_service.filter_tasks(
            search_results,
            status="incomplete",
            priority=Priority.HIGH
        )

        assert len(filtered_results) == 2
        assert all(not task.completed for task in filtered_results)
        assert all(task.priority == Priority.HIGH for task in filtered_results)

    def test_complex_search_filter_combination(self):
        """Test complex combination of search and multiple filters."""
        # Search for "project"
        search_results = self.search_service.search_tasks(self.tasks, "project")

        # Apply multiple filters
        filtered_results = self.filter_service.filter_tasks(
            search_results,
            status="incomplete",
            priority=Priority.HIGH,
            categories=["work"]
        )

        assert len(filtered_results) >= 1
        assert all(not task.completed for task in filtered_results)
        assert all(task.priority == Priority.HIGH for task in filtered_results)
        assert all(task.has_category("work") for task in filtered_results)
