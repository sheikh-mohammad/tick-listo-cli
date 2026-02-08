"""Integration tests for creating tasks with due time (T014 - User Story 1)."""

import pytest
from datetime import datetime, time
from src.ticklisto.models.task import Task, Priority
from src.ticklisto.services.task_service import TaskService
from src.ticklisto.services.storage_service import StorageService


class TestTaskWithTimeIntegration:
    """Integration tests for creating and managing tasks with due time."""

    def setup_method(self):
        """Set up test fixtures."""
        self.storage = StorageService()
        self.task_service = TaskService(self.storage)

    def test_create_task_with_due_time(self):
        """Test creating a task with due date and time."""
        task = self.task_service.create_task(
            title="Team meeting",
            description="Weekly sync",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )

        assert task.title == "Team meeting"
        assert task.due_date == datetime(2026, 2, 15, 0, 0, 0)
        assert task.due_time == time(14, 30)
        assert task.id is not None

    def test_create_task_without_due_time(self):
        """Test creating a task without due time (backward compatibility)."""
        task = self.task_service.create_task(
            title="Simple task",
            due_date=datetime(2026, 2, 15, 0, 0, 0)
        )

        assert task.title == "Simple task"
        assert task.due_date == datetime(2026, 2, 15, 0, 0, 0)
        assert task.due_time is None

    def test_update_task_add_due_time(self):
        """Test adding due time to existing task."""
        task = self.task_service.create_task(
            title="Task",
            due_date=datetime(2026, 2, 15, 0, 0, 0)
        )

        updated = self.task_service.update_task(
            task.id,
            due_time=time(14, 30)
        )

        assert updated.due_time == time(14, 30)
        assert updated.due_date == datetime(2026, 2, 15, 0, 0, 0)

    def test_update_task_change_due_time(self):
        """Test changing due time of existing task."""
        task = self.task_service.create_task(
            title="Task",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )

        updated = self.task_service.update_task(
            task.id,
            due_time=time(16, 0)
        )

        assert updated.due_time == time(16, 0)

    def test_update_task_remove_due_time(self):
        """Test removing due time from task."""
        task = self.task_service.create_task(
            title="Task",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )

        updated = self.task_service.update_task(
            task.id,
            due_time=None
        )

        assert updated.due_time is None

    def test_task_with_time_persistence(self):
        """Test that task with due time persists correctly."""
        # Create task
        task = self.task_service.create_task(
            title="Persistent task",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )

        # Retrieve task
        retrieved = self.task_service.get_task(task.id)

        assert retrieved.due_time == time(14, 30)
        assert retrieved.due_date == datetime(2026, 2, 15, 0, 0, 0)

    def test_list_tasks_includes_due_time(self):
        """Test that listing tasks includes due time information."""
        self.task_service.create_task(
            title="Task 1",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )
        self.task_service.create_task(
            title="Task 2",
            due_date=datetime(2026, 2, 16, 0, 0, 0)
        )

        tasks = self.task_service.list_tasks()

        assert len(tasks) == 2
        assert tasks[0].due_time == time(14, 30)
        assert tasks[1].due_time is None

    def test_filter_tasks_with_due_time(self):
        """Test filtering tasks that have due time set."""
        self.task_service.create_task(
            title="Task with time",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )
        self.task_service.create_task(
            title="Task without time",
            due_date=datetime(2026, 2, 16, 0, 0, 0)
        )

        all_tasks = self.task_service.list_tasks()
        tasks_with_time = [t for t in all_tasks if t.due_time is not None]

        assert len(tasks_with_time) == 1
        assert tasks_with_time[0].title == "Task with time"

    def test_complete_task_with_due_time(self):
        """Test completing a task that has due time."""
        task = self.task_service.create_task(
            title="Task",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )

        completed = self.task_service.complete_task(task.id)

        assert completed.completed is True
        assert completed.due_time == time(14, 30)

    def test_delete_task_with_due_time(self):
        """Test deleting a task that has due time."""
        task = self.task_service.create_task(
            title="Task",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30)
        )

        self.task_service.delete_task(task.id)

        with pytest.raises(ValueError):
            self.task_service.get_task(task.id)
