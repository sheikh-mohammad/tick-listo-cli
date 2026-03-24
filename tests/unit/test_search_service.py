"""
Unit tests for SearchService.
Following TDD approach - these tests are written FIRST and should FAIL initially.
"""
import pytest
from datetime import datetime
from tick_listo_cli.models.task import Task, Priority
from tick_listo_cli.services.search_service import SearchService


class TestSearchService:
    """Unit tests for search functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.search_service = SearchService()

        # Create sample tasks for testing
        self.tasks = [
            Task(
                id=1,
                title="Complete project documentation",
                description="Write comprehensive docs for the project",
                priority=Priority.HIGH,
                categories=["work", "documentation"]
            ),
            Task(
                id=2,
                title="Buy groceries",
                description="Milk, eggs, bread",
                priority=Priority.MEDIUM,
                categories=["home", "shopping"]
            ),
            Task(
                id=3,
                title="Review pull request",
                description="Review the new feature PR",
                priority=Priority.HIGH,
                categories=["work", "code-review"]
            ),
            Task(
                id=4,
                title="Schedule dentist appointment",
                description="Call dentist office",
                priority=Priority.LOW,
                categories=["personal", "health"]
            ),
            Task(
                id=5,
                title="Project planning meeting",
                description="Discuss project timeline and milestones",
                priority=Priority.MEDIUM,
                categories=["work", "meeting"]
            )
        ]

    def test_search_by_keyword_in_title(self):
        """Test searching tasks by keyword in title."""
        results = self.search_service.search_tasks(self.tasks, "project")

        assert len(results) == 2
        assert any(task.id == 1 for task in results)
        assert any(task.id == 5 for task in results)

    def test_search_by_keyword_in_description(self):
        """Test searching tasks by keyword in description."""
        results = self.search_service.search_tasks(self.tasks, "review")

        assert len(results) == 1
        assert results[0].id == 3

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        results_lower = self.search_service.search_tasks(self.tasks, "project")
        results_upper = self.search_service.search_tasks(self.tasks, "PROJECT")
        results_mixed = self.search_service.search_tasks(self.tasks, "PrOjEcT")

        assert len(results_lower) == len(results_upper) == len(results_mixed) == 2

    def test_search_partial_match(self):
        """Test that search matches partial words."""
        results = self.search_service.search_tasks(self.tasks, "doc")

        assert len(results) == 1
        assert results[0].id == 1

    def test_search_no_results(self):
        """Test search with no matching results."""
        results = self.search_service.search_tasks(self.tasks, "nonexistent")

        assert len(results) == 0
        assert results == []

    def test_search_empty_keyword(self):
        """Test search with empty keyword returns all tasks."""
        results = self.search_service.search_tasks(self.tasks, "")

        assert len(results) == len(self.tasks)

    def test_search_whitespace_keyword(self):
        """Test search with whitespace keyword returns all tasks."""
        results = self.search_service.search_tasks(self.tasks, "   ")

        assert len(results) == len(self.tasks)

    def test_search_multiple_matches_in_same_task(self):
        """Test that task appears once even if keyword matches multiple fields."""
        results = self.search_service.search_tasks(self.tasks, "project")

        # Task 1 has "project" in both title and description
        # Should only appear once in results
        task_1_count = sum(1 for task in results if task.id == 1)
        assert task_1_count == 1

    def test_search_with_special_characters(self):
        """Test search with special characters."""
        task_with_special = Task(
            id=6,
            title="Fix bug #123",
            description="Critical bug in module-x"
        )
        tasks = self.tasks + [task_with_special]

        results = self.search_service.search_tasks(tasks, "#123")
        assert len(results) == 1
        assert results[0].id == 6

    def test_search_empty_task_list(self):
        """Test search on empty task list."""
        results = self.search_service.search_tasks([], "keyword")

        assert len(results) == 0
        assert results == []

    def test_search_task_without_description(self):
        """Test search on tasks without description."""
        task_no_desc = Task(id=7, title="Task without description")
        tasks = [task_no_desc]

        results = self.search_service.search_tasks(tasks, "description")
        assert len(results) == 1

    def test_search_returns_original_task_objects(self):
        """Test that search returns the original task objects, not copies."""
        results = self.search_service.search_tasks(self.tasks, "project")

        assert all(isinstance(task, Task) for task in results)
        # Verify it's the same object reference
        assert results[0] is self.tasks[0] or results[0] is self.tasks[4]


class TestSearchWithScope:
    """Unit tests for search with scope selection (Phase 11 - Enhanced Features)."""

    def test_search_in_title_only(self):
        """Test searching in title only."""
        from ticklisto.services.search_service import search_tasks_with_scope
        from ticklisto.models.task import Task, Priority
        
        tasks = [
            Task(id=1, title="Work Report", description="Home assignment", priority=Priority.HIGH, categories=["work"]),
            Task(id=2, title="Home Cleaning", description="Work on the house", priority=Priority.MEDIUM, categories=["home"]),
            Task(id=3, title="Meeting Notes", description="Client meeting", priority=Priority.LOW, categories=["work"])
        ]
        
        # Search for "work" in title only
        results = search_tasks_with_scope(tasks, "work", scope="title")
        
        assert len(results) == 1
        assert results[0].id == 1  # Only "Work Report" matches in title

    def test_search_in_description_only(self):
        """Test searching in description only."""
        from ticklisto.services.search_service import search_tasks_with_scope
        from ticklisto.models.task import Task, Priority
        
        tasks = [
            Task(id=1, title="Work Report", description="Home assignment", priority=Priority.HIGH, categories=["work"]),
            Task(id=2, title="Home Cleaning", description="Work on the house", priority=Priority.MEDIUM, categories=["home"]),
            Task(id=3, title="Meeting Notes", description="Client meeting", priority=Priority.LOW, categories=["work"])
        ]
        
        # Search for "work" in description only
        results = search_tasks_with_scope(tasks, "work", scope="description")
        
        assert len(results) == 1
        assert results[0].id == 2  # Only "Home Cleaning" has "work" in description

    def test_search_in_both_fields(self):
        """Test searching in both title and description."""
        from ticklisto.services.search_service import search_tasks_with_scope
        from ticklisto.models.task import Task, Priority
        
        tasks = [
            Task(id=1, title="Work Report", description="Home assignment", priority=Priority.HIGH, categories=["work"]),
            Task(id=2, title="Home Cleaning", description="Work on the house", priority=Priority.MEDIUM, categories=["home"]),
            Task(id=3, title="Meeting Notes", description="Client meeting", priority=Priority.LOW, categories=["work"])
        ]
        
        # Search for "work" in both fields
        results = search_tasks_with_scope(tasks, "work", scope="both")
        
        assert len(results) == 2
        assert {r.id for r in results} == {1, 2}  # Both tasks with "work" in title or description

    def test_search_with_invalid_scope_raises_error(self):
        """Test that invalid scope raises ValueError."""
        from ticklisto.services.search_service import search_tasks_with_scope
        from ticklisto.models.task import Task, Priority
        
        tasks = [
            Task(id=1, title="Test", description="Test", priority=Priority.HIGH, categories=["work"])
        ]
        
        with pytest.raises(ValueError, match="Invalid scope"):
            search_tasks_with_scope(tasks, "test", scope="invalid")
