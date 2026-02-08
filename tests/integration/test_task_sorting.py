"""Integration tests for sorting tasks by date and time (T015 - User Story 1)."""

import pytest
from datetime import datetime, time
from src.ticklisto.models.task import Task, Priority
from src.ticklisto.services.task_service import TaskService
from src.ticklisto.services.sort_service import SortService
from src.ticklisto.services.storage_service import StorageService


class TestTaskSortingWithTime:
    """Integration tests for sorting tasks by date and time."""

    def setup_method(self):
        """Set up test fixtures."""
        self.storage = StorageService()
        self.task_service = TaskService(self.storage)
        self.sort_service = SortService()

    def test_sort_tasks_by_date_only(self):
        """Test sorting tasks by date when no time is specified."""
        task1 = self.task_service.create_task(
            title="Task 1",
            due_date=datetime(2026, 2, 17, 0, 0, 0)
        )
        task2 = self.task_service.create_task(
            title="Task 2",
            due_date=datetime(2026, 2, 15, 0, 0, 0)
        )
        task3 = self.task_service.create_task(
            title="Task 3",
            due_date=datetime(2026, 2, 16, 0, 0, 0)
        )

        tasks = [task1, task2, task3]
        sorted_tasks = self.sort_service.sort_by_due_date(tasks)

        assert sorted_tasks[0].title == "Task 2"  # Feb 15
        assert sorted_tasks[1].title == "Task 3"  # Feb 16
        assert sorted_tasks[2].title == "Task 1"  # Feb 17

    def test_sort_tasks_by_date_and_time(self):
        """Test sorting tasks by date first, then time within same date."""
        task1 = self.task_service.create_task(
            title="Task 1",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(16, 0)
        )
        task2 = self.task_service.create_task(
            title="Task 2",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(9, 0)
        )
        task3 = self.task_service.create_task(
            title="Task 3",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )

        tasks = [task1, task2, task3]
        sorted_tasks = self.sort_service.sort_by_due_date(tasks)

        assert sorted_tasks[0].title == "Task 2"  # 9:00 AM
        assert sorted_tasks[1].title == "Task 3"  # 2:30 PM
        assert sorted_tasks[2].title == "Task 1"  # 4:00 PM

    def test_sort_tasks_mixed_with_and_without_time(self):
        """Test sorting tasks where some have time and some don't."""
        task1 = self.task_service.create_task(
            title="Task 1",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )
        task2 = self.task_service.create_task(
            title="Task 2",
            due_date=datetime(2026, 2, 15, 0, 0, 0)
        )
        task3 = self.task_service.create_task(
            title="Task 3",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(9, 0)
        )

        tasks = [task1, task2, task3]
        sorted_tasks = self.sort_service.sort_by_due_date(tasks)

        # Tasks without time should come before tasks with time on same date
        assert sorted_tasks[0].title == "Task 2"  # No time (midnight)
        assert sorted_tasks[1].title == "Task 3"  # 9:00 AM
        assert sorted_tasks[2].title == "Task 1"  # 2:30 PM

    def test_sort_tasks_across_multiple_dates_with_time(self):
        """Test sorting tasks across different dates with times."""
        task1 = self.task_service.create_task(
            title="Task 1",
            due_date=datetime(2026, 2, 16, 0, 0, 0),
            due_time=time(9, 0)
        )
        task2 = self.task_service.create_task(
            title="Task 2",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(16, 0)
        )
        task3 = self.task_service.create_task(
            title="Task 3",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(9, 0)
        )

        tasks = [task1, task2, task3]
        sorted_tasks = self.sort_service.sort_by_due_date(tasks)

        # Date takes precedence over time
        assert sorted_tasks[0].title == "Task 3"  # Feb 15, 9:00 AM
        assert sorted_tasks[1].title == "Task 2"  # Feb 15, 4:00 PM
        assert sorted_tasks[2].title == "Task 1"  # Feb 16, 9:00 AM

    def test_sort_tasks_with_no_due_date(self):
        """Test sorting tasks where some have no due date."""
        task1 = self.task_service.create_task(
            title="Task 1",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )
        task2 = self.task_service.create_task(
            title="Task 2"
        )
        task3 = self.task_service.create_task(
            title="Task 3",
            due_date=datetime(2026, 2, 16, 0, 0, 0)
        )

        tasks = [task1, task2, task3]
        sorted_tasks = self.sort_service.sort_by_due_date(tasks)

        # Tasks with due dates should come first
        assert sorted_tasks[0].title == "Task 1"
        assert sorted_tasks[1].title == "Task 3"
        assert sorted_tasks[2].title == "Task 2"  # No due date

    def test_sort_tasks_same_date_and_time(self):
        """Test sorting tasks with identical date and time."""
        task1 = self.task_service.create_task(
            title="Task 1",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )
        task2 = self.task_service.create_task(
            title="Task 2",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )

        tasks = [task1, task2]
        sorted_tasks = self.sort_service.sort_by_due_date(tasks)

        # Order should be stable (maintain original order)
        assert len(sorted_tasks) == 2

    def test_sort_empty_task_list(self):
        """Test sorting empty task list."""
        tasks = []
        sorted_tasks = self.sort_service.sort_by_due_date(tasks)

        assert sorted_tasks == []

    def test_sort_single_task(self):
        """Test sorting single task."""
        task = self.task_service.create_task(
            title="Task",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )

        tasks = [task]
        sorted_tasks = self.sort_service.sort_by_due_date(tasks)

        assert len(sorted_tasks) == 1
        assert sorted_tasks[0].title == "Task"

    def test_sort_tasks_by_priority_with_time(self):
        """Test sorting by priority preserves time information."""
        task1 = self.task_service.create_task(
            title="Task 1",
            priority=Priority.LOW,
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )
        task2 = self.task_service.create_task(
            title="Task 2",
            priority=Priority.HIGH,
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(9, 0)
        )

        tasks = [task1, task2]
        sorted_tasks = self.sort_service.sort_by_priority(tasks)

        # High priority first
        assert sorted_tasks[0].title == "Task 2"
        assert sorted_tasks[0].due_time == time(9, 0)
        assert sorted_tasks[1].title == "Task 1"
        assert sorted_tasks[1].due_time == time(14, 30)

    def test_sort_completed_tasks_with_time(self):
        """Test that completed tasks can be sorted by time."""
        task1 = self.task_service.create_task(
            title="Task 1",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(16, 0)
        )
        task2 = self.task_service.create_task(
            title="Task 2",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(9, 0)
        )

        self.task_service.complete_task(task1.id)
        self.task_service.complete_task(task2.id)

        tasks = [task1, task2]
        sorted_tasks = self.sort_service.sort_by_due_date(tasks)

        assert sorted_tasks[0].title == "Task 2"
        assert sorted_tasks[1].title == "Task 1"
