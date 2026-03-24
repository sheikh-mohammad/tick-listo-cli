"""
Unit tests for FilterService.
Following TDD approach - these tests are written FIRST and should FAIL initially.
"""
import pytest
from datetime import datetime, timedelta
from tick_listo_cli.models.task import Task, Priority
from tick_listo_cli.services.filter_service import FilterService


class TestFilterService:
    """Unit tests for filter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.filter_service = FilterService()

        # Create sample tasks for testing
        today = datetime.now()
        self.tasks = [
            Task(
                id=1,
                title="High priority work task",
                priority=Priority.HIGH,
                categories=["work", "urgent"],
                completed=False,
                due_date=today + timedelta(days=1)
            ),
            Task(
                id=2,
                title="Medium priority home task",
                priority=Priority.MEDIUM,
                categories=["home"],
                completed=True,
                due_date=today + timedelta(days=7)
            ),
            Task(
                id=3,
                title="Low priority personal task",
                priority=Priority.LOW,
                categories=["personal", "health"],
                completed=False,
                due_date=today + timedelta(days=30)
            ),
            Task(
                id=4,
                title="Overdue high priority task",
                priority=Priority.HIGH,
                categories=["work"],
                completed=False,
                due_date=today - timedelta(days=5)
            ),
            Task(
                id=5,
                title="Task without due date",
                priority=Priority.MEDIUM,
                categories=["work", "planning"],
                completed=False,
                due_date=None
            )
        ]

    def test_filter_by_status_incomplete(self):
        """Test filtering tasks by incomplete status."""
        results = self.filter_service.filter_tasks(self.tasks, status="incomplete")

        assert len(results) == 4
        assert all(not task.completed for task in results)

    def test_filter_by_status_complete(self):
        """Test filtering tasks by complete status."""
        results = self.filter_service.filter_tasks(self.tasks, status="complete")

        assert len(results) == 1
        assert results[0].id == 2
        assert results[0].completed is True

    def test_filter_by_priority_high(self):
        """Test filtering tasks by high priority."""
        results = self.filter_service.filter_tasks(self.tasks, priority=Priority.HIGH)

        assert len(results) == 2
        assert all(task.priority == Priority.HIGH for task in results)

    def test_filter_by_priority_medium(self):
        """Test filtering tasks by medium priority."""
        results = self.filter_service.filter_tasks(self.tasks, priority=Priority.MEDIUM)

        assert len(results) == 2
        assert all(task.priority == Priority.MEDIUM for task in results)

    def test_filter_by_priority_low(self):
        """Test filtering tasks by low priority."""
        results = self.filter_service.filter_tasks(self.tasks, priority=Priority.LOW)

        assert len(results) == 1
        assert results[0].priority == Priority.LOW

    def test_filter_by_single_category(self):
        """Test filtering tasks by a single category."""
        results = self.filter_service.filter_tasks(self.tasks, categories=["work"])

        assert len(results) == 3
        assert all(task.has_category("work") for task in results)

    def test_filter_by_multiple_categories_or_logic(self):
        """Test filtering tasks by multiple categories with OR logic."""
        results = self.filter_service.filter_tasks(
            self.tasks,
            categories=["home", "personal"],
            category_match="any"
        )

        assert len(results) == 2
        assert any(task.id == 2 for task in results)
        assert any(task.id == 3 for task in results)

    def test_filter_by_multiple_categories_and_logic(self):
        """Test filtering tasks by multiple categories with AND logic."""
        results = self.filter_service.filter_tasks(
            self.tasks,
            categories=["work", "urgent"],
            category_match="all"
        )

        assert len(results) == 1
        assert results[0].id == 1

    def test_filter_by_due_date_before(self):
        """Test filtering tasks due before a specific date."""
        cutoff_date = datetime.now() + timedelta(days=10)
        results = self.filter_service.filter_tasks(
            self.tasks,
            due_before=cutoff_date
        )

        # Should include tasks 1, 2, and 4 (due within 10 days or overdue)
        assert len(results) >= 3

    def test_filter_by_due_date_after(self):
        """Test filtering tasks due after a specific date."""
        cutoff_date = datetime.now() + timedelta(days=10)
        results = self.filter_service.filter_tasks(
            self.tasks,
            due_after=cutoff_date
        )

        # Should include task 3 (due in 30 days)
        assert len(results) >= 1

    def test_filter_overdue_tasks(self):
        """Test filtering overdue tasks."""
        results = self.filter_service.filter_tasks(self.tasks, overdue=True)

        assert len(results) == 1
        assert results[0].id == 4
        assert results[0].is_overdue()

    def test_filter_tasks_with_no_due_date(self):
        """Test filtering tasks without due date."""
        results = self.filter_service.filter_tasks(self.tasks, has_due_date=False)

        assert len(results) == 1
        assert results[0].id == 5
        assert results[0].due_date is None

    def test_filter_tasks_with_due_date(self):
        """Test filtering tasks with due date."""
        results = self.filter_service.filter_tasks(self.tasks, has_due_date=True)

        assert len(results) == 4
        assert all(task.due_date is not None for task in results)

    def test_filter_combined_criteria(self):
        """Test filtering with multiple criteria combined."""
        results = self.filter_service.filter_tasks(
            self.tasks,
            status="incomplete",
            priority=Priority.HIGH,
            categories=["work"]
        )

        # Should return high priority, incomplete work tasks
        assert len(results) == 2
        assert all(task.priority == Priority.HIGH for task in results)
        assert all(not task.completed for task in results)
        assert all(task.has_category("work") for task in results)

    def test_filter_no_criteria_returns_all(self):
        """Test that filtering with no criteria returns all tasks."""
        results = self.filter_service.filter_tasks(self.tasks)

        assert len(results) == len(self.tasks)

    def test_filter_no_matches(self):
        """Test filtering with criteria that match no tasks."""
        results = self.filter_service.filter_tasks(
            self.tasks,
            categories=["nonexistent"]
        )

        assert len(results) == 0

    def test_filter_empty_task_list(self):
        """Test filtering an empty task list."""
        results = self.filter_service.filter_tasks([], priority=Priority.HIGH)

        assert len(results) == 0

    def test_filter_preserves_task_order(self):
        """Test that filtering preserves the original task order."""
        results = self.filter_service.filter_tasks(
            self.tasks,
            categories=["work"]
        )

        # Verify order is preserved (task 1, 4, 5 in that order)
        work_task_ids = [task.id for task in results]
        assert work_task_ids == sorted(work_task_ids)


class TestDateFilterLogic:
    """Unit tests for date filtering logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.filter_service = FilterService()
        today = datetime.now()

        self.tasks = [
            Task(id=1, title="Past task", due_date=today - timedelta(days=10)),
            Task(id=2, title="Yesterday", due_date=today - timedelta(days=1)),
            Task(id=3, title="Today", due_date=today),
            Task(id=4, title="Tomorrow", due_date=today + timedelta(days=1)),
            Task(id=5, title="Next week", due_date=today + timedelta(days=7)),
            Task(id=6, title="Next month", due_date=today + timedelta(days=30)),
            Task(id=7, title="No due date", due_date=None)
        ]

    def test_filter_due_today(self):
        """Test filtering tasks due today."""
        today = datetime.now()
        results = self.filter_service.filter_tasks(
            self.tasks,
            due_date=today.date()
        )

        assert len(results) >= 1
        assert any(task.id == 3 for task in results)

    def test_filter_due_this_week(self):
        """Test filtering tasks due within the next 7 days."""
        cutoff = datetime.now() + timedelta(days=7)
        results = self.filter_service.filter_tasks(
            self.tasks,
            due_before=cutoff
        )

        # Should include tasks 2, 3, 4, 5 (and possibly 1 if overdue included)
        assert len(results) >= 4

    def test_filter_date_range(self):
        """Test filtering tasks within a date range."""
        # Use a fixed reference point to avoid timing issues
        now = datetime.now()
        start = now - timedelta(hours=1)  # Slightly before now to include "today" task
        end = now + timedelta(days=10)

        results = self.filter_service.filter_tasks(
            self.tasks,
            due_after=start,
            due_before=end
        )

        # Should include tasks 3 (today), 4 (tomorrow), 5 (next week)
        assert len(results) >= 3


class TestCategoryFilterLogic:
    """Unit tests for category filtering with OR/AND logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.filter_service = FilterService()

        self.tasks = [
            Task(id=1, title="Task 1", categories=["work"]),
            Task(id=2, title="Task 2", categories=["work", "urgent"]),
            Task(id=3, title="Task 3", categories=["work", "urgent", "client"]),
            Task(id=4, title="Task 4", categories=["home"]),
            Task(id=5, title="Task 5", categories=["home", "urgent"]),
            Task(id=6, title="Task 6", categories=[])
        ]

    def test_category_filter_or_logic(self):
        """Test category filtering with OR logic (any match)."""
        results = self.filter_service.filter_tasks(
            self.tasks,
            categories=["work", "home"],
            category_match="any"
        )

        # Should match tasks with either work OR home
        assert len(results) == 5
        assert all(
            task.has_any_category(["work", "home"])
            for task in results
        )

    def test_category_filter_and_logic(self):
        """Test category filtering with AND logic (all match)."""
        results = self.filter_service.filter_tasks(
            self.tasks,
            categories=["work", "urgent"],
            category_match="all"
        )

        # Should match tasks with both work AND urgent
        assert len(results) == 2
        assert all(
            task.has_all_categories(["work", "urgent"])
            for task in results
        )

    def test_category_filter_three_categories_and(self):
        """Test category filtering with three categories using AND logic."""
        results = self.filter_service.filter_tasks(
            self.tasks,
            categories=["work", "urgent", "client"],
            category_match="all"
        )

        assert len(results) == 1
        assert results[0].id == 3

    def test_category_filter_no_categories(self):
        """Test filtering tasks with no categories."""
        results = self.filter_service.filter_tasks(
            self.tasks,
            has_categories=False
        )

        assert len(results) == 1
        assert results[0].id == 6
