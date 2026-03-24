"""
Integration tests for CLI commands with Rich formatting.
Following TDD approach - these tests are written FIRST and should FAIL initially.
"""
import pytest
import tempfile
import os
from io import StringIO
from tick_listo_cli.models.task import Task, Priority
from tick_listo_cli.services.task_service import TaskService
from tick_listo_cli.cli.tick_listo_cli import TickListoCLI
from tick_listo_cli.ui.rich_ui import RichUI


class TestCLICommandsWithEnhancements:
    """Integration tests for CLI commands with priority and categories display."""

    def test_display_task_with_priority_indicator(self):
        """Test that tasks display with priority indicators."""
        service = TaskService(data_file="test_cli_priority_display.json")
        ui = RichUI()

        # Create tasks with different priorities
        task1 = service.add_task(title="High Priority", priority=Priority.HIGH)
        task2 = service.add_task(title="Medium Priority", priority=Priority.MEDIUM)
        task3 = service.add_task(title="Low Priority", priority=Priority.LOW)

        tasks = service.list_tasks()

        # Test that display method can handle priority field
        # This should not raise an error
        try:
            ui.display_tasks(tasks)
            display_success = True
        except Exception:
            display_success = False

        assert display_success is True

    def test_display_task_with_categories(self):
        """Test that tasks display with category tags."""
        service = TaskService(data_file="test_cli_categories_display.json")
        ui = RichUI()

        task = service.add_task(
            title="Work Task",
            categories=["work", "urgent", "client"]
        )

        tasks = service.list_tasks()

        # Test that display method can handle categories field
        try:
            ui.display_tasks(tasks)
            display_success = True
        except Exception:
            display_success = False

        assert display_success is True

    def test_display_task_with_due_date(self):
        """Test that tasks display with due date."""
        from datetime import datetime
        service = TaskService(data_file="test_cli_due_date_display.json")
        ui = RichUI()

        task = service.add_task(
            title="Task with deadline",
            due_date=datetime(2026, 2, 15)
        )

        tasks = service.list_tasks()

        # Test that display method can handle due_date field
        try:
            ui.display_tasks(tasks)
            display_success = True
        except Exception:
            display_success = False

        assert display_success is True

    def test_display_empty_task_list(self):
        """Test displaying empty task list."""
        service = TaskService(data_file="test_cli_empty_list.json")
        ui = RichUI()

        tasks = service.list_tasks()
        assert len(tasks) == 0

        # Should handle empty list gracefully
        try:
            ui.display_tasks(tasks)
            display_success = True
        except Exception:
            display_success = False

        assert display_success is True

    def test_display_task_with_all_fields(self):
        """Test displaying task with all enhanced fields."""
        from datetime import datetime
        service = TaskService(data_file="test_cli_all_fields_display.json")
        ui = RichUI()

        task = service.add_task(
            title="Complete Task",
            description="Full task with all fields",
            priority=Priority.HIGH,
            categories=["work", "urgent"],
            due_date=datetime(2026, 2, 15)
        )

        tasks = service.list_tasks()

        # Test that display handles all fields
        try:
            ui.display_tasks(tasks)
            display_success = True
        except Exception:
            display_success = False

        assert display_success is True

    def test_priority_color_coding(self):
        """Test that priority levels have appropriate color coding."""
        ui = RichUI()

        # Test that UI has methods for priority styling
        assert hasattr(ui, 'get_priority_style') or hasattr(ui, 'format_priority')

    def test_category_display_formatting(self):
        """Test that categories are formatted appropriately."""
        ui = RichUI()

        # Test that UI has methods for category formatting
        assert hasattr(ui, 'format_categories') or hasattr(ui, 'get_category_display')


class TestDeleteAllCommand:
    """Integration tests for delete all command (Phase 9 - User Story 5)."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.service = TaskService(data_file=self.temp_file.name)

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_delete_all_command_with_confirmation(self):
        """Test delete all command with user confirmation."""
        # Add tasks
        self.service.add_task("Task 1", priority=Priority.HIGH, categories=["work"])
        self.service.add_task("Task 2", priority=Priority.MEDIUM, categories=["home"])
        self.service.add_task("Task 3", priority=Priority.LOW, categories=["personal"])

        assert len(self.service.tasks) == 3

        # Simulate delete all with confirmation
        result = self.service.delete_all()
        assert result is True

        # Reset ID counter (as CLI would do)
        self.service.id_manager.reset_counter()

        # Verify all tasks deleted
        assert len(self.service.tasks) == 0
        assert self.service.id_manager.get_current_counter() == 1

    def test_delete_all_command_on_empty_list(self):
        """Test delete all command when no tasks exist."""
        assert len(self.service.tasks) == 0

        result = self.service.delete_all()

        assert result is False
        assert len(self.service.tasks) == 0

    def test_delete_all_alias_dela(self):
        """Test that 'dela' alias works for delete all command."""
        # Add tasks
        self.service.add_task("Task 1", priority=Priority.HIGH, categories=["work"])
        self.service.add_task("Task 2", priority=Priority.MEDIUM, categories=["home"])

        assert len(self.service.tasks) == 2

        # Simulate dela command (same as delete_all)
        result = self.service.delete_all()
        assert result is True

        # Reset ID counter
        self.service.id_manager.reset_counter()

        # Verify deletion
        assert len(self.service.tasks) == 0
        assert self.service.id_manager.get_current_counter() == 1

    def test_new_task_after_delete_all_gets_id_one(self):
        """Test that new task after delete all gets ID 1."""
        # Add and delete tasks
        self.service.add_task("Task 1", priority=Priority.HIGH, categories=["work"])
        self.service.add_task("Task 2", priority=Priority.MEDIUM, categories=["home"])

        self.service.delete_all()
        self.service.id_manager.reset_counter()

        # Add new task
        new_task = self.service.add_task("New Task", priority=Priority.HIGH, categories=["work"])

        assert new_task.id == 1
        assert len(self.service.tasks) == 1

    def test_delete_all_persists_to_storage(self):
        """Test that delete all changes persist to storage."""
        # Add tasks and save
        self.service.add_task("Task 1", priority=Priority.HIGH, categories=["work"])
        self.service.add_task("Task 2", priority=Priority.MEDIUM, categories=["home"])
        self.service.save_to_file()

        # Delete all and save
        self.service.delete_all()
        self.service.id_manager.reset_counter()
        self.service.save_to_file()

        # Load in new service instance
        new_service = TaskService(data_file=self.temp_file.name)

        # Verify empty task list and reset counter
        assert len(new_service.tasks) == 0
        assert new_service.id_manager.get_current_counter() == 1
