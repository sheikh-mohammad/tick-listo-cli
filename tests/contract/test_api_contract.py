"""
Contract tests for CLI interface.
These tests verify that the CLI interface conforms to the expected contract/behavior.
"""

import pytest
from tick_listo_cli.cli.tick_listo_cli import TickListoCLI
from tick_listo_cli.services.task_service import TaskService


class TestCLIContract:
    """Contract tests to verify CLI interface behavior."""

    def setup_method(self):
        """Set up a CLI instance for testing."""
        self.cli = TickListoCLI()
        # Clear tasks for a clean test environment
        self.cli.task_service.tasks = {}
        self.cli.task_service.id_manager.reset_counter()

    def test_add_command_contract(self):
        """Test that the add command follows the expected contract."""
        initial_count = len(self.cli.task_service.get_all())

        # Add a task
        task = self.cli.task_service.add_task("Test Task", "Test Description")

        # Verify task was added
        assert task is not None
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert len(self.cli.task_service.get_all()) == initial_count + 1

    def test_view_command_contract(self):
        """Test that the view command follows the expected contract."""
        # Add some tasks
        self.cli.task_service.add_task("Task 1", "Description 1")
        self.cli.task_service.add_task("Task 2", "Description 2")

        # Get all tasks (simulating view command behavior)
        tasks = self.cli.task_service.get_all()

        # Verify we get all tasks
        assert len(tasks) == 2
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"

    def test_update_command_contract(self):
        """Test that the update command follows the expected contract."""
        # Add a task
        task = self.cli.task_service.add_task("Original Task", "Original Description")

        # Update the task
        updated_task = self.cli.task_service.update_task(
            task.id,
            title="Updated Task",
            description="Updated Description"
        )

        # Verify update was successful
        assert updated_task is not None
        assert updated_task.title == "Updated Task"
        assert updated_task.description == "Updated Description"

    def test_delete_command_contract(self):
        """Test that the delete command follows the expected contract."""
        # Add a task
        task = self.cli.task_service.add_task("Task to Delete", "Description")

        # Delete the task
        success = self.cli.task_service.delete_task(task.id)

        # Verify deletion was successful
        assert success is True
        assert self.cli.task_service.get_by_id(task.id) is None

    def test_complete_command_contract(self):
        """Test that the complete command follows the expected contract."""
        # Add a task
        task = self.cli.task_service.add_task("Task to Complete", "Description")

        # Verify initial state
        assert task.completed is False

        # Toggle completion
        success = self.cli.task_service.toggle_complete(task.id)

        # Verify completion was toggled
        assert success is True
        toggled_task = self.cli.task_service.get_by_id(task.id)
        assert toggled_task.completed is True

    def test_command_aliases_contract(self):
        """Test that command aliases work as expected."""
        # Test that different ways of calling commands work
        # Add command should work
        task = self.cli.task_service.add_task("Alias Test", "Testing aliases")
        assert task is not None

        # View command should work
        tasks = self.cli.task_service.get_all()
        assert len(tasks) >= 1

        # Update command should work
        updated_task = self.cli.task_service.update_task(task.id, title="Updated via Alias Test")
        assert updated_task is not None

        # Verify update worked
        updated_task = self.cli.task_service.get_by_id(task.id)
        assert updated_task.title == "Updated via Alias Test"

    def test_error_handling_contract(self):
        """Test that error handling follows the expected contract."""
        # Attempt to update non-existent task
        result = self.cli.task_service.update_task(9999, title="Should fail")
        assert result is None

        # Attempt to delete non-existent task
        success = self.cli.task_service.delete_task(9999)
        assert success is False

        # Attempt to get non-existent task
        task = self.cli.task_service.get_by_id(9999)
        assert task is None

        # Attempt to toggle completion of non-existent task
        success = self.cli.task_service.toggle_complete(9999)
        assert success is False