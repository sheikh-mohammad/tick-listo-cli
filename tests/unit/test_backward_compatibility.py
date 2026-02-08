"""Backward compatibility tests (T109 - Phase 10).

Verifies that tasks created without new fields (due_time, recurrence_pattern, reminder_settings)
continue to work correctly with the enhanced system.
"""

import pytest
from datetime import datetime
from ticklisto.models.task import Task, TaskStatus, Priority
from ticklisto.services.task_service import TaskService
from ticklisto.services.storage_service import StorageService


class TestBackwardCompatibility:
    """Test backward compatibility with legacy task data."""

    def test_task_without_due_time(self):
        """Test that tasks without due_time work correctly."""
        task = Task(
            id=1,
            title="Legacy task",
            description="Task without time",
            due_date=datetime(2026, 2, 15),
            due_time=None,  # No time component
            priority=Priority.MEDIUM,
            categories=["work"]
        )

        assert task.id == 1
        assert task.title == "Legacy task"
        assert task.due_date is not None
        assert task.due_time is None
        assert task.recurrence_pattern is None
        assert task.reminder_settings is None or task.reminder_settings == []

    def test_task_without_recurrence(self):
        """Test that tasks without recurrence pattern work correctly."""
        task = Task(
            id=2,
            title="Non-recurring task",
            description="Regular task",
            due_date=datetime(2026, 2, 20),
            priority=Priority.HIGH,
            categories=["personal"]
        )

        assert task.recurrence_pattern is None
        assert task.recurrence_interval == 1  # Default
        assert task.recurrence_weekdays is None
        assert task.recurrence_end_date is None
        assert task.series_id is None
        assert task.instance_number is None

    def test_task_without_reminders(self):
        """Test that tasks without reminder settings work correctly."""
        task = Task(
            id=3,
            title="Task without reminders",
            description="No email reminders",
            due_date=datetime(2026, 2, 25),
            priority=Priority.LOW,
            categories=["shopping"]
        )

        assert task.reminder_settings is None or task.reminder_settings == []

    def test_minimal_task(self):
        """Test task with only required fields."""
        task = Task(
            id=4,
            title="Minimal task",
            description="",
            priority=Priority.MEDIUM,
            categories=[]
        )

        assert task.id == 4
        assert task.title == "Minimal task"
        assert task.description == ""
        assert task.due_date is None
        assert task.due_time is None
        assert task.recurrence_pattern is None
        assert task.reminder_settings is None or task.reminder_settings == []
        assert task.status == TaskStatus.PENDING
        assert task.completed is False

    def test_task_serialization_without_new_fields(self):
        """Test that tasks without new fields serialize correctly."""
        task = Task(
            id=5,
            title="Serialization test",
            description="Test serialization",
            priority=Priority.MEDIUM,
            categories=["test"]
        )

        # Serialize to dict
        task_dict = task.to_dict()

        assert "id" in task_dict
        assert "title" in task_dict
        assert "due_date" in task_dict
        assert task_dict["due_date"] is None
        assert "due_time" in task_dict
        assert task_dict["due_time"] is None

    def test_task_deserialization_without_new_fields(self):
        """Test that legacy task data deserializes correctly."""
        # Simulate legacy task data (without new fields)
        legacy_data = {
            "id": 6,
            "title": "Legacy task from old version",
            "description": "Created before new features",
            "completed": False,
            "priority": "medium",
            "categories": ["work", "important"],
            "due_date": "2026-02-15T00:00:00",
            "created_timestamp": "2026-01-01T10:00:00",
            "updated_timestamp": "2026-01-01T10:00:00"
            # Note: No due_time, recurrence_pattern, reminder_settings
        }

        # Deserialize
        task = Task.from_dict(legacy_data)

        assert task.id == 6
        assert task.title == "Legacy task from old version"
        assert task.due_date is not None
        assert task.due_time is None
        assert task.recurrence_pattern is None
        assert task.reminder_settings is None or task.reminder_settings == []

    def test_task_service_with_legacy_tasks(self):
        """Test TaskService operations with legacy tasks."""
        service = TaskService(data_file="test_backward_compat.json")

        # Add task without new fields
        task = service.add_task(
            title="Legacy style task",
            description="No time or recurrence",
            priority=Priority.MEDIUM,
            categories=["test"]
            # Note: No due_date, due_time, reminder_settings
        )

        assert task.id is not None
        assert task.title == "Legacy style task"
        assert task.due_date is None
        assert task.due_time is None
        assert task.recurrence_pattern is None

        # Verify task can be retrieved
        retrieved = service.get_task(task.id)
        assert retrieved is not None
        assert retrieved.title == "Legacy style task"

        # Verify task can be updated
        service.update_task(
            task.id,
            title="Updated legacy task",
            description="Still no new fields",
            priority=Priority.HIGH,
            categories=["updated"]
        )

        updated = service.get_task(task.id)
        assert updated.title == "Updated legacy task"

        # Verify task can be completed
        service.complete_task(task.id)
        completed = service.get_task(task.id)
        assert completed.completed is True

        # Verify task can be deleted
        service.delete_task(task.id)
        # get_task() raises ValueError when task not found
        with pytest.raises(ValueError, match="Task with ID .* not found"):
            service.get_task(task.id)

        # Cleanup
        import os
        if os.path.exists("test_backward_compat.json"):
            os.remove("test_backward_compat.json")

    def test_storage_service_with_legacy_data(self):
        """Test StorageService with legacy task data."""
        storage = StorageService()

        # Create legacy-style data
        legacy_tasks = [
            {
                "id": 1,
                "title": "Old task 1",
                "description": "No new fields",
                "completed": False,
                "priority": "high",
                "categories": ["work"],
                "due_date": None,
                "created_timestamp": "2026-01-01T10:00:00",
                "updated_timestamp": "2026-01-01T10:00:00"
            },
            {
                "id": 2,
                "title": "Old task 2",
                "description": "Also no new fields",
                "completed": True,
                "priority": "low",
                "categories": ["personal"],
                "due_date": "2026-02-15T00:00:00",
                "created_timestamp": "2026-01-02T10:00:00",
                "updated_timestamp": "2026-01-02T10:00:00"
            }
        ]

        # Save legacy data (must include next_id for storage service)
        storage.save_to_json({"tasks": legacy_tasks, "next_id": 3}, "test_legacy.json")

        # Load and verify
        loaded_data = storage.load_from_json("test_legacy.json")
        assert len(loaded_data["tasks"]) == 2

        # Convert to Task objects
        tasks = [Task.from_dict(t) for t in loaded_data["tasks"]]
        assert len(tasks) == 2
        assert all(t.due_time is None for t in tasks)
        assert all(t.recurrence_pattern is None for t in tasks)

        # Cleanup
        import os
        if os.path.exists("test_legacy.json"):
            os.remove("test_legacy.json")

    def test_validation_allows_legacy_tasks(self):
        """Test that validation doesn't break legacy tasks."""
        # Task with due_date but no due_time should be valid
        task1 = Task(
            id=1,
            title="Task with date only",
            due_date=datetime(2026, 2, 15),
            due_time=None,
            priority=Priority.MEDIUM,
            categories=[]
        )
        assert task1.due_date is not None
        assert task1.due_time is None

        # Task with neither due_date nor due_time should be valid
        task2 = Task(
            id=2,
            title="Task with no date",
            due_date=None,
            due_time=None,
            priority=Priority.MEDIUM,
            categories=[]
        )
        assert task2.due_date is None
        assert task2.due_time is None

    def test_task_service_validation_with_legacy_style(self):
        """Test TaskService validation allows legacy-style task creation."""
        service = TaskService(data_file="test_validation.json")

        # Should succeed: task with no due_date or due_time
        task1 = service.add_task(
            title="No dates",
            description="Legacy style",
            priority=Priority.MEDIUM,
            categories=["test"]
        )
        assert task1.due_date is None
        assert task1.due_time is None

        # Should succeed: task with due_date but no due_time
        task2 = service.add_task(
            title="Date only",
            description="Legacy style with date",
            priority=Priority.MEDIUM,
            categories=["test"],
            due_date=datetime(2026, 2, 15)
        )
        assert task2.due_date is not None
        assert task2.due_time is None

        # Cleanup
        import os
        if os.path.exists("test_validation.json"):
            os.remove("test_validation.json")
