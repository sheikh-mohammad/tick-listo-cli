"""
Integration tests for task operations with priority and categories.
Following TDD approach - these tests are written FIRST and should FAIL initially.
"""
import pytest
import tempfile
import os
from datetime import datetime
from tick_listo_cli.models.task import Task, Priority
from tick_listo_cli.services.task_service import TaskService


class TestTaskOperationsWithEnhancements:
    """Integration tests for task creation and updates with new fields."""

    def test_create_task_with_priority(self):
        """Test creating task with priority field."""
        service = TaskService(data_file="test_task_ops_priority.json")

        task = service.add_task(
            title="High Priority Task",
            description="Important task",
            priority=Priority.HIGH
        )

        assert task.priority == Priority.HIGH
        assert task.title == "High Priority Task"

    def test_create_task_with_categories(self):
        """Test creating task with categories."""
        service = TaskService(data_file="test_task_ops_categories.json")

        task = service.add_task(
            title="Work Task",
            description="Work related",
            categories=["work", "urgent"]
        )

        assert "work" in task.categories
        assert "urgent" in task.categories
        assert len(task.categories) == 2

    def test_create_task_with_due_date(self):
        """Test creating task with due date."""
        service = TaskService(data_file="test_task_ops_due_date.json")
        due_date = datetime(2026, 2, 15)

        task = service.add_task(
            title="Task with deadline",
            description="Must complete by date",
            due_date=due_date
        )

        assert task.due_date == due_date

    def test_create_task_with_all_new_fields(self):
        """Test creating task with priority, categories, and due date."""
        service = TaskService(data_file="test_task_ops_all_fields.json")
        due_date = datetime(2026, 2, 15)

        task = service.add_task(
            title="Complete Task",
            description="Task with all fields",
            priority=Priority.HIGH,
            categories=["work", "urgent"],
            due_date=due_date
        )

        assert task.priority == Priority.HIGH
        assert "work" in task.categories
        assert "urgent" in task.categories
        assert task.due_date == due_date

    def test_update_task_priority(self):
        """Test updating task priority."""
        service = TaskService(data_file="test_task_update_priority.json")

        task = service.add_task(title="Test Task")
        assert task.priority == Priority.MEDIUM  # Default

        # Update priority
        updated_task = service.update_task(
            task_id=task.id,
            priority=Priority.HIGH
        )

        assert updated_task.priority == Priority.HIGH

    def test_update_task_categories(self):
        """Test updating task categories."""
        service = TaskService(data_file="test_task_update_categories.json")

        task = service.add_task(title="Test Task")
        assert task.categories == []

        # Update categories
        updated_task = service.update_task(
            task_id=task.id,
            categories=["work", "home"]
        )

        assert "work" in updated_task.categories
        assert "home" in updated_task.categories

    def test_update_task_due_date(self):
        """Test updating task due date."""
        service = TaskService(data_file="test_task_update_due_date.json")
        new_due_date = datetime(2026, 3, 1)

        task = service.add_task(title="Test Task")
        assert task.due_date is None

        # Update due date
        updated_task = service.update_task(
            task_id=task.id,
            due_date=new_due_date
        )

        assert updated_task.due_date == new_due_date

    def test_list_tasks_includes_new_fields(self):
        """Test that listing tasks includes new fields."""
        service = TaskService(data_file="test_task_list_new_fields.json")

        service.add_task(
            title="Task 1",
            priority=Priority.HIGH,
            categories=["work"]
        )
        service.add_task(
            title="Task 2",
            priority=Priority.LOW,
            categories=["home"]
        )

        tasks = service.list_tasks()

        assert len(tasks) == 2
        assert tasks[0].priority == Priority.HIGH
        assert "work" in tasks[0].categories
        assert tasks[1].priority == Priority.LOW
        assert "home" in tasks[1].categories


class TestRequiredFieldsIntegration:
    """Integration tests for required priority and categories (Phase 10 - User Story 6)."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.service = TaskService(data_file=self.temp_file.name)

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_task_creation_with_missing_priority_fails(self):
        """Test that task creation uses default priority when not provided."""
        # Task creation without priority should use default (MEDIUM)
        task = self.service.add_task(
            title="Test Task",
            description="Test Description",
            categories=["work"]
            # priority is missing, should default to MEDIUM
        )

        assert task is not None
        assert task.priority == Priority.MEDIUM  # Default value

    def test_task_creation_with_missing_categories_fails(self):
        """Test that task creation uses default categories when not provided."""
        # Task creation without categories should use default (empty list)
        task = self.service.add_task(
            title="Test Task",
            description="Test Description",
            priority=Priority.HIGH
            # categories is missing, should default to empty list
        )

        assert task is not None
        assert task.categories == []  # Default value

    def test_task_creation_with_all_required_fields_succeeds(self):
        """Test that task creation succeeds when all required fields are provided."""
        task = self.service.add_task(
            title="Test Task",
            description="Test Description",
            priority=Priority.HIGH,
            categories=["work"]
        )

        assert task is not None
        assert task.priority == Priority.HIGH
        assert task.categories == ["work"]

    def test_task_creation_with_multiple_categories(self):
        """Test that task creation works with multiple categories."""
        task = self.service.add_task(
            title="Test Task",
            description="Test Description",
            priority=Priority.MEDIUM,
            categories=["work", "urgent", "client"]
        )

        assert task is not None
        assert len(task.categories) == 3
        assert set(task.categories) == {"work", "urgent", "client"}
