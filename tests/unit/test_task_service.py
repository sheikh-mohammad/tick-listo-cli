import pytest
import os
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch
from tick_listo_cli.services.task_service import TaskService
from tick_listo_cli.models.task import Task, Priority


class TestTaskService:
    """Unit tests for the TaskService class."""

    def setup_method(self):
        """Set up a temporary file for testing."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.service = TaskService(data_file=self.temp_file.name)

    def teardown_method(self):
        """Clean up the temporary file."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_initialization(self):
        """Test that TaskService initializes with empty task list and ID counter at 1."""
        assert len(self.service.tasks) == 0
        assert self.service.id_manager.get_current_counter() == 1

    def test_add_task_success(self):
        """Test adding a valid task."""
        task = self.service.add_task("Test Task", "Test Description")

        assert task is not None
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.completed is False
        assert task.id in self.service.tasks
        assert self.service.id_manager.get_current_counter() == 2

    def test_add_task_with_minimal_params(self):
        """Test adding a task with only required parameters."""
        task = self.service.add_task("Test Task")

        assert task is not None
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == ""
        assert task.completed is False

    def test_add_task_invalid_title(self):
        """Test adding a task with invalid title."""
        with pytest.raises(ValueError):
            task = self.service.add_task("", "Test Description")

    def test_add_task_invalid_title_length(self):
        """Test adding a task with title too long."""
        long_title = "A" * 201
        with pytest.raises(ValueError):
            task = self.service.add_task(long_title, "Test Description")

    def test_add_task_invalid_description_length(self):
        """Test adding a task with description too long."""
        long_description = "A" * 1001
        with pytest.raises(ValueError):
            task = self.service.add_task("Test Task", long_description)

    def test_get_all_empty_list(self):
        """Test getting all tasks when list is empty."""
        tasks = self.service.get_all()

        assert tasks == []

    def test_get_all_with_tasks(self):
        """Test getting all tasks when list has tasks."""
        self.service.add_task("Task 1", "Description 1")
        self.service.add_task("Task 2", "Description 2")

        tasks = self.service.get_all()

        assert len(tasks) == 2
        assert tasks[0].id == 1
        assert tasks[1].id == 2
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"

    def test_get_by_id_exists(self):
        """Test getting a task by ID that exists."""
        added_task = self.service.add_task("Test Task", "Description")
        retrieved_task = self.service.get_by_id(added_task.id)

        assert retrieved_task is not None
        assert retrieved_task.id == added_task.id
        assert retrieved_task.title == "Test Task"

    def test_get_by_id_not_exists(self):
        """Test getting a task by ID that doesn't exist."""
        retrieved_task = self.service.get_by_id(999)

        assert retrieved_task is None

    def test_update_task_success(self):
        """Test updating a task successfully."""
        task = self.service.add_task("Original Task", "Original Description")

        updated_task = self.service.update_task(task.id, title="Updated Task", description="Updated Description")

        assert updated_task is not None
        assert updated_task.title == "Updated Task"
        assert updated_task.description == "Updated Description"

    def test_update_task_partial(self):
        """Test updating only some fields of a task."""
        task = self.service.add_task("Original Task", "Original Description")

        updated_task = self.service.update_task(task.id, title="Updated Task")

        assert updated_task is not None
        assert updated_task.title == "Updated Task"
        assert updated_task.description == "Original Description"  # Should remain unchanged

    def test_update_task_not_exists(self):
        """Test updating a task that doesn't exist."""
        result = self.service.update_task(999, title="Updated Task")

        assert result is None

    def test_update_task_invalid_data(self):
        """Test updating a task with invalid data."""
        task = self.service.add_task("Original Task", "Original Description")

        # Invalid title should raise ValueError
        with pytest.raises(ValueError):
            self.service.update_task(task.id, title="")  # Invalid title

        # Original task should remain unchanged
        original_task = self.service.get_by_id(task.id)
        assert original_task.title == "Original Task"

    def test_delete_task_success(self):
        """Test deleting a task successfully."""
        task = self.service.add_task("Test Task", "Description")

        success = self.service.delete_task(task.id)

        assert success is True
        assert len(self.service.tasks) == 0
        assert self.service.get_by_id(task.id) is None

    def test_delete_task_not_exists(self):
        """Test deleting a task that doesn't exist."""
        success = self.service.delete_task(999)

        assert success is False

    def test_toggle_complete_success(self):
        """Test toggling completion status successfully."""
        task = self.service.add_task("Test Task", "Description")

        # Initially should be False
        assert task.completed is False

        # Toggle to True
        success = self.service.toggle_complete(task.id)
        assert success is True
        toggled_task = self.service.get_by_id(task.id)
        assert toggled_task.completed is True

        # Toggle back to False
        success = self.service.toggle_complete(task.id)
        assert success is True
        toggled_task = self.service.get_by_id(task.id)
        assert toggled_task.completed is False

    def test_toggle_complete_not_exists(self):
        """Test toggling completion status for a task that doesn't exist."""
        success = self.service.toggle_complete(999)

        assert success is False

class TestDeleteAll:
    """Unit tests for delete_all function (Phase 9 - User Story 5)."""

    def setup_method(self):
        """Set up a temporary file for testing."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.service = TaskService(data_file=self.temp_file.name)

    def teardown_method(self):
        """Clean up the temporary file."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_delete_all_with_tasks(self):
        """Test delete_all removes all tasks."""
        # Add some tasks
        self.service.add_task("Task 1", priority=Priority.HIGH, categories=["work"])
        self.service.add_task("Task 2", priority=Priority.MEDIUM, categories=["home"])
        self.service.add_task("Task 3", priority=Priority.LOW, categories=["personal"])

        assert len(self.service.tasks) == 3

        # Delete all
        result = self.service.delete_all()

        assert result is True
        assert len(self.service.tasks) == 0

    def test_delete_all_with_no_tasks(self):
        """Test delete_all returns False when no tasks exist."""
        assert len(self.service.tasks) == 0

        result = self.service.delete_all()

        assert result is False
        assert len(self.service.tasks) == 0

    def test_delete_all_preserves_id_counter(self):
        """Test that delete_all doesn't automatically reset ID counter."""
        # Add and delete tasks
        self.service.add_task("Task 1", priority=Priority.HIGH, categories=["work"])
        self.service.add_task("Task 2", priority=Priority.MEDIUM, categories=["home"])

        # Counter should be at 3
        assert self.service.id_manager.get_current_counter() == 3

        # Delete all
        self.service.delete_all()

        # Counter should still be at 3 (not reset automatically)
        assert self.service.id_manager.get_current_counter() == 3

    def test_id_counter_reset_after_delete_all(self):
        """Test that ID counter can be reset after delete_all."""
        # Add tasks
        self.service.add_task("Task 1", priority=Priority.HIGH, categories=["work"])
        self.service.add_task("Task 2", priority=Priority.MEDIUM, categories=["home"])

        # Delete all
        self.service.delete_all()

        # Manually reset counter (as would be done in CLI command)
        self.service.id_manager.reset_counter()

        # Counter should be at 1
        assert self.service.id_manager.get_current_counter() == 1

        # New task should get ID 1
        new_task = self.service.add_task("New Task", priority=Priority.HIGH, categories=["work"])
        assert new_task.id == 1
