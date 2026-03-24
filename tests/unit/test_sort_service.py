"""
Unit tests for SortService.
Following TDD approach - these tests are written FIRST and should FAIL initially.
"""
import pytest
from datetime import datetime, timedelta
from tick_listo_cli.models.task import Task, Priority
from tick_listo_cli.services.sort_service import SortService


class TestSortService:
    """Unit tests for sort functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sort_service = SortService()

        today = datetime.now()
        self.tasks = [
            Task(
                id=1,
                title="Task C - High priority, due tomorrow",
                priority=Priority.HIGH,
                due_date=today + timedelta(days=1)
            ),
            Task(
                id=2,
                title="Task A - Medium priority, due today",
                priority=Priority.MEDIUM,
                due_date=today
            ),
            Task(
                id=3,
                title="Task B - Low priority, no due date",
                priority=Priority.LOW,
                due_date=None
            ),
            Task(
                id=4,
                title="Task D - High priority, due in 3 days",
                priority=Priority.HIGH,
                due_date=today + timedelta(days=3)
            ),
            Task(
                id=5,
                title="Task E - Medium priority, no due date",
                priority=Priority.MEDIUM,
                due_date=None
            )
        ]

    def test_sort_by_due_date_ascending(self):
        """Test sorting tasks by due date (earliest first)."""
        sorted_tasks = self.sort_service.sort_tasks(self.tasks, "due_date")

        # Tasks with due dates should come first, sorted by date
        # Tasks without due dates should come last
        assert sorted_tasks[0].id == 2  # Due today
        assert sorted_tasks[1].id == 1  # Due tomorrow
        assert sorted_tasks[2].id == 4  # Due in 3 days
        # Tasks 3 and 5 have no due date, should be at the end

    def test_sort_by_due_date_with_secondary_priority(self):
        """Test sorting by due date with secondary priority sorting."""
        sorted_tasks = self.sort_service.sort_tasks(
            self.tasks,
            "due_date",
            secondary_sort="priority"
        )

        # Within same due date, higher priority should come first
        # Tasks without due dates should be sorted by priority
        assert sorted_tasks[0].id == 2  # Due today
        assert sorted_tasks[1].id == 1  # Due tomorrow (high priority)
        assert sorted_tasks[2].id == 4  # Due in 3 days (high priority)

    def test_sort_by_priority_high_to_low(self):
        """Test sorting tasks by priority (high to low)."""
        sorted_tasks = self.sort_service.sort_tasks(self.tasks, "priority")

        # High priority tasks first
        assert sorted_tasks[0].priority == Priority.HIGH
        assert sorted_tasks[1].priority == Priority.HIGH
        # Medium priority tasks next
        assert sorted_tasks[2].priority == Priority.MEDIUM
        assert sorted_tasks[3].priority == Priority.MEDIUM
        # Low priority tasks last
        assert sorted_tasks[4].priority == Priority.LOW

    def test_sort_alphabetically_by_title(self):
        """Test sorting tasks alphabetically by title."""
        sorted_tasks = self.sort_service.sort_tasks(self.tasks, "title")

        # Should be sorted A, B, C, D, E
        assert "Task A" in sorted_tasks[0].title
        assert "Task B" in sorted_tasks[1].title
        assert "Task C" in sorted_tasks[2].title
        assert "Task D" in sorted_tasks[3].title
        assert "Task E" in sorted_tasks[4].title

    def test_sort_handles_tasks_without_due_dates(self):
        """Test that sorting handles tasks without due dates correctly."""
        sorted_tasks = self.sort_service.sort_tasks(self.tasks, "due_date")

        # Tasks without due dates should be at the end
        tasks_without_dates = [t for t in sorted_tasks if t.due_date is None]
        assert len(tasks_without_dates) == 2
        # They should be the last tasks in the list
        assert sorted_tasks[-2].due_date is None
        assert sorted_tasks[-1].due_date is None

    def test_sort_empty_task_list(self):
        """Test sorting an empty task list."""
        sorted_tasks = self.sort_service.sort_tasks([], "priority")

        assert sorted_tasks == []

    def test_sort_single_task(self):
        """Test sorting a list with a single task."""
        single_task = [self.tasks[0]]
        sorted_tasks = self.sort_service.sort_tasks(single_task, "priority")

        assert len(sorted_tasks) == 1
        assert sorted_tasks[0] == single_task[0]

    def test_sort_preserves_task_objects(self):
        """Test that sorting returns the same task objects, not copies."""
        sorted_tasks = self.sort_service.sort_tasks(self.tasks, "priority")

        # Verify all original tasks are in the sorted list
        original_ids = set(t.id for t in self.tasks)
        sorted_ids = set(t.id for t in sorted_tasks)
        assert original_ids == sorted_ids

    def test_sort_invalid_criteria_raises_error(self):
        """Test that invalid sort criteria raises an error."""
        with pytest.raises(ValueError, match="Invalid sort criteria"):
            self.sort_service.sort_tasks(self.tasks, "invalid_field")

    def test_sort_by_priority_then_title(self):
        """Test sorting by priority with secondary sort by title."""
        # Create tasks with same priority but different titles
        tasks = [
            Task(id=1, title="Zebra task", priority=Priority.HIGH),
            Task(id=2, title="Apple task", priority=Priority.HIGH),
            Task(id=3, title="Banana task", priority=Priority.MEDIUM)
        ]

        sorted_tasks = self.sort_service.sort_tasks(
            tasks,
            "priority",
            secondary_sort="title"
        )

        # Within HIGH priority, should be alphabetical
        assert sorted_tasks[0].title == "Apple task"
        assert sorted_tasks[1].title == "Zebra task"
        assert sorted_tasks[2].title == "Banana task"


class TestSortWithComplexScenarios:
    """Test sorting with more complex scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sort_service = SortService()

    def test_sort_overdue_tasks_first(self):
        """Test that overdue tasks appear first when sorting by due date."""
        today = datetime.now()
        tasks = [
            Task(id=1, title="Future task", due_date=today + timedelta(days=5)),
            Task(id=2, title="Overdue task", due_date=today - timedelta(days=2)),
            Task(id=3, title="Today task", due_date=today),
            Task(id=4, title="Very overdue", due_date=today - timedelta(days=10))
        ]

        sorted_tasks = self.sort_service.sort_tasks(tasks, "due_date")

        # Most overdue should be first
        assert sorted_tasks[0].id == 4  # 10 days overdue
        assert sorted_tasks[1].id == 2  # 2 days overdue
        assert sorted_tasks[2].id == 3  # Due today
        assert sorted_tasks[3].id == 1  # Future

    def test_sort_mixed_priorities_and_dates(self):
        """Test sorting with mixed priorities and due dates."""
        today = datetime.now()
        tasks = [
            Task(id=1, title="Low, tomorrow", priority=Priority.LOW, due_date=today + timedelta(days=1)),
            Task(id=2, title="High, next week", priority=Priority.HIGH, due_date=today + timedelta(days=7)),
            Task(id=3, title="Medium, today", priority=Priority.MEDIUM, due_date=today),
            Task(id=4, title="High, today", priority=Priority.HIGH, due_date=today)
        ]

        # Sort by due date with priority as secondary
        sorted_tasks = self.sort_service.sort_tasks(
            tasks,
            "due_date",
            secondary_sort="priority"
        )

        # Today's tasks first, with high priority before medium
        assert sorted_tasks[0].id == 4  # High, today
        assert sorted_tasks[1].id == 3  # Medium, today

    def test_sort_case_insensitive_title(self):
        """Test that title sorting is case-insensitive."""
        tasks = [
            Task(id=1, title="zebra"),
            Task(id=2, title="Apple"),
            Task(id=3, title="banana")
        ]

        sorted_tasks = self.sort_service.sort_tasks(tasks, "title")

        assert sorted_tasks[0].title == "Apple"
        assert sorted_tasks[1].title == "banana"
        assert sorted_tasks[2].title == "zebra"
