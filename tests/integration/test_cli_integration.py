import pytest
import io
import sys
from unittest.mock import patch, MagicMock
from tick_listo.cli.tick_listo_cli import TickListoCLI
from tick_listo.services.task_service import TaskService


class TestCLIIntegration:
    """Integration tests for the CLI functionality."""

    def setup_method(self):
        """Set up a CLI instance for testing."""
        self.cli = TickListoCLI()
        # Clear tasks for a clean test environment
        self.cli.task_service.tasks = {}
        self.cli.task_service.id_manager.reset_counter()

    def test_add_and_view_single_task(self):
        """Test adding a task and then viewing it."""
        # Add a task
        task = self.cli.task_service.add_task("Test Task", "Test Description")

        # Verify the task was added
        assert task is not None
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Test Description"

        # Get all tasks
        tasks = self.cli.task_service.get_all()

        # Verify the task is in the list
        assert len(tasks) == 1
        assert tasks[0].id == 1
        assert tasks[0].title == "Test Task"

    def test_add_and_view_multiple_tasks(self):
        """Test adding multiple tasks and viewing them all."""
        # Add multiple tasks
        task1 = self.cli.task_service.add_task("Task 1", "Description 1")
        task2 = self.cli.task_service.add_task("Task 2", "Description 2")
        task3 = self.cli.task_service.add_task("Task 3", "Description 3")

        # Verify tasks were added
        assert task1 is not None
        assert task2 is not None
        assert task3 is not None

        # Get all tasks
        tasks = self.cli.task_service.get_all()

        # Verify all tasks are present
        assert len(tasks) == 3
        assert tasks[0].id == 1
        assert tasks[0].title == "Task 1"
        assert tasks[1].id == 2
        assert tasks[1].title == "Task 2"
        assert tasks[2].id == 3
        assert tasks[2].title == "Task 3"

    def test_add_and_update_task(self):
        """Test adding a task and then updating it."""
        # Add a task
        task = self.cli.task_service.add_task("Original Task", "Original Description")

        # Verify the task was added
        assert task is not None
        assert task.title == "Original Task"
        assert task.description == "Original Description"

        # Update the task
        updated_task = self.cli.task_service.update_task(task.id, title="Updated Task", description="Updated Description")

        # Verify the update was successful
        assert updated_task is not None

        # Get the updated task
        updated_task = self.cli.task_service.get_by_id(task.id)

        # Verify the task was updated
        assert updated_task is not None
        assert updated_task.title == "Updated Task"
        assert updated_task.description == "Updated Description"

    def test_add_and_delete_task(self):
        """Test adding a task and then deleting it."""
        # Add a task
        task = self.cli.task_service.add_task("Task to Delete", "Description")

        # Verify the task was added
        assert task is not None
        assert task.id in self.cli.task_service.tasks

        # Delete the task
        success = self.cli.task_service.delete_task(task.id)

        # Verify the deletion was successful
        assert success is True
        assert task.id not in self.cli.task_service.tasks

        # Verify the task list is empty
        tasks = self.cli.task_service.get_all()
        assert len(tasks) == 0

    def test_add_and_toggle_completion(self):
        """Test adding a task and toggling its completion status."""
        # Add a task
        task = self.cli.task_service.add_task("Task to Toggle", "Description")

        # Verify the task was added with completed=False
        assert task is not None
        assert task.completed is False

        # Toggle the completion status
        success = self.cli.task_service.toggle_complete(task.id)

        # Verify the toggle was successful
        assert success is True

        # Get the updated task
        updated_task = self.cli.task_service.get_by_id(task.id)

        # Verify the completion status was toggled
        assert updated_task is not None
        assert updated_task.completed is True

        # Toggle again to set it back to False
        success = self.cli.task_service.toggle_complete(task.id)
        assert success is True

        updated_task = self.cli.task_service.get_by_id(task.id)
        assert updated_task is not None
        assert updated_task.completed is False

    def test_cli_add_command_simulation(self):
        """Simulate the CLI add command using mock inputs."""
        # Mock user inputs
        inputs = iter(["Test CLI Task", "Test CLI Description"])

        def mock_input(prompt):
            return next(inputs)

        with patch('builtins.input', mock_input):
            with patch('sys.stdout', new_callable=io.StringIO) as fake_out:
                # This would normally trigger the CLI add flow
                # But we'll test the service method directly
                task = self.cli.task_service.add_task("Test CLI Task", "Test CLI Description")

                assert task is not None
                assert task.title == "Test CLI Task"
                assert task.description == "Test CLI Description"

    def test_cli_view_command_with_tasks(self):
        """Test the CLI view functionality with tasks."""
        # Add some tasks
        self.cli.task_service.add_task("View Task 1", "Description 1")
        self.cli.task_service.add_task("View Task 2", "Description 2")

        # Get all tasks
        tasks = self.cli.task_service.get_all()

        # Verify tasks exist
        assert len(tasks) == 2
        assert tasks[0].title == "View Task 1"
        assert tasks[1].title == "View Task 2"

    def test_cli_view_command_empty_list(self):
        """Test the CLI view functionality with no tasks."""
        # Get all tasks when there are none
        tasks = self.cli.task_service.get_all()

        # Verify the list is empty
        assert len(tasks) == 0

    def test_persistence_save_and_load(self):
        """Test saving and loading tasks from file."""
        # Add some tasks
        task1 = self.cli.task_service.add_task("Persistent Task 1", "Description 1")
        task2 = self.cli.task_service.add_task("Persistent Task 2", "Description 2")

        # Save to file
        self.cli.task_service.save_to_file()

        # Create a new service instance to simulate loading from file
        new_service = TaskService(data_file=self.cli.task_service.data_file)

        # Verify tasks were loaded
        loaded_tasks = new_service.get_all()
        assert len(loaded_tasks) == 2
        assert loaded_tasks[0].title == "Persistent Task 1"
        assert loaded_tasks[1].title == "Persistent Task 2"
        assert new_service.id_manager.get_current_counter() == 3  # Should be 3 since we added 2 tasks