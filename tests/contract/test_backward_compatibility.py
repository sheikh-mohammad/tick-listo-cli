"""
Contract tests for backward compatibility with existing tasks.
Ensures that existing basic operations continue to work with enhanced Task model.
Following TDD approach - these tests are written FIRST and should FAIL initially.
"""
import pytest
from datetime import datetime
from tick_listo_cli.models.task import Task, Priority, TaskStatus
from tick_listo_cli.services.task_service import TaskService


class TestBackwardCompatibility:
    """Test that existing functionality still works with enhanced Task model."""

    def test_create_task_without_new_fields(self):
        """Test creating task without priority, categories, or due_date (backward compatibility)."""
        task = Task(id=1, title="Old style task")

        # Should have default values for new fields
        assert task.priority == Priority.MEDIUM
        assert task.categories == []
        assert task.due_date is None
        assert task.title == "Old style task"
        assert task.completed is False

    def test_task_service_add_task_basic(self):
        """Test TaskService.add_task with basic parameters (backward compatibility)."""
        service = TaskService(data_file="test_backward_compat.json")

        task = service.add_task(title="Test Task", description="Test Description")

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.completed is False
        # New fields should have defaults
        assert task.priority == Priority.MEDIUM
        assert task.categories == []
        assert task.due_date is None

    def test_task_to_dict_includes_new_fields(self):
        """Test that to_dict includes new fields."""
        task = Task(
            id=1,
            title="Test Task",
            priority=Priority.HIGH,
            categories=["work"],
            due_date=datetime(2026, 2, 15)
        )

        task_dict = task.to_dict()

        assert "priority" in task_dict
        assert "categories" in task_dict
        assert "due_date" in task_dict
        assert task_dict["priority"] == "high"
        assert task_dict["categories"] == ["work"]

    def test_task_from_dict_with_old_format(self):
        """Test loading task from old format (without new fields)."""
        old_format_data = {
            "id": 1,
            "title": "Old Task",
            "description": "Old Description",
            "completed": False,
            "status": "pending",
            "created_timestamp": "2026-01-01T10:00:00",
            "updated_timestamp": "2026-01-01T10:00:00"
        }

        task = Task.from_dict(old_format_data)

        assert task.id == 1
        assert task.title == "Old Task"
        # Should have defaults for new fields
        assert task.priority == Priority.MEDIUM
        assert task.categories == []
        assert task.due_date is None

    def test_task_from_dict_with_new_format(self):
        """Test loading task from new format (with new fields)."""
        new_format_data = {
            "id": 1,
            "title": "New Task",
            "description": "New Description",
            "completed": False,
            "priority": "high",
            "categories": ["work", "urgent"],
            "due_date": "2026-02-15T00:00:00",
            "status": "pending",
            "created_at": "2026-01-01T10:00:00",
            "updated_at": "2026-01-01T10:00:00"
        }

        task = Task.from_dict(new_format_data)

        assert task.id == 1
        assert task.title == "New Task"
        assert task.priority == Priority.HIGH
        assert task.categories == ["work", "urgent"]
        assert task.due_date == datetime(2026, 2, 15)

    def test_existing_task_methods_still_work(self):
        """Test that existing Task methods work with enhanced model."""
        task = Task(id=1, title="Test Task")

        # Test mark_complete (existing method)
        task.mark_complete()
        assert task.completed is True

        # Test mark_incomplete (new method)
        task.mark_incomplete()
        assert task.completed is False

        # Test update_details (existing method)
        task.update_details(title="Updated Title")
        assert task.title == "Updated Title"
