from datetime import datetime
from typing import Dict, List, Optional
import json
import os
from ..models.task import Task, TaskStatus, Priority
from ..utils.file_handler import FileHandler
from ..ui.rich_ui import RichUI
from .progress_tracker import ProgressTracker
from .storage_service import StorageService
from .id_manager import IDManager


class TaskService:
    """
    Service class for managing tasks with CRUD operations.
    Implements the TaskList operations as defined in the data model.
    """

    def __init__(self, data_file: str = "ticklisto_data.json"):
        """
        Initialize the TaskService with an empty task list and next_id counter.
        Loads existing data from file if it exists.
        """
        self.tasks: Dict[int, Task] = {}
        self.data_file = data_file

        # Initialize new services for Phase 8
        self.storage_service = StorageService()
        self.id_manager = IDManager()

        # Keep FileHandler for backward compatibility (deprecated)
        self.file_handler = FileHandler()

        self.rich_ui = RichUI()  # Initialize Rich UI for enhanced display
        self.progress_tracker = ProgressTracker()  # Initialize ProgressTracker for US4 integration

        # Load existing data if file exists
        if os.path.exists(self.data_file):
            self.load_from_file()

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        categories: List[str] = None,
        due_date: Optional[datetime] = None
    ) -> Task:
        """
        Add a new task to the list with enhanced fields.
        Validates task before adding, assigns auto-generated sequential ID, sets creation timestamp.

        Args:
            title: Task title
            description: Task description (optional)
            priority: Task priority level (default: MEDIUM)
            categories: List of category tags (optional)
            due_date: Optional due date for the task

        Returns:
            Created Task object
        """
        # Generate ID using IDManager (Phase 8)
        task_id = self.id_manager.generate_id()

        # Create a new task with the generated ID
        new_task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            categories=categories if categories is not None else [],
            due_date=due_date,
            status=TaskStatus.PENDING  # Default to pending status
        )

        self.tasks[task_id] = new_task

        # Update progress tracking when task is added
        self.update_progress_on_task_change()

        return new_task

    def get_all(self) -> List[Task]:
        """
        Retrieve all tasks in the list.
        Returns ordered list of tasks, maintaining insertion order or sorts by ID.

        Returns:
            List of all tasks
        """
        # Return tasks sorted by ID
        return sorted(self.tasks.values(), key=lambda x: x.id)

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """
        Retrieve specific task by ID.
        Validates ID exists in collection.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task object if found, None otherwise
        """
        return self.tasks.get(task_id)

    def update_task(
        self,
        task_id: int,
        title: str = None,
        description: str = None,
        priority: Priority = None,
        categories: List[str] = None,
        due_date: Optional[datetime] = None
    ) -> Optional[Task]:
        """
        Update task properties including enhanced fields.
        Validates updates against field constraints, preserves immutable fields (id, created_at),
        updates mutable fields (title, description, priority, categories, due_date).

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority level (optional)
            categories: New categories list (optional)
            due_date: New due date (optional)

        Returns:
            Updated Task object if successful, None otherwise
        """
        task = self.get_by_id(task_id)
        if not task:
            return None

        # Update basic fields if provided
        if title is not None or description is not None:
            task.update_details(title=title, description=description)

        # Update priority if provided
        if priority is not None:
            task.priority = priority
            task.updated_at = datetime.now()
            task.updated_timestamp = task.updated_at

        # Update categories if provided
        if categories is not None:
            task.categories = categories
            task.updated_at = datetime.now()
            task.updated_timestamp = task.updated_at

        # Update due_date if provided
        if due_date is not None:
            task.due_date = due_date
            task.updated_at = datetime.now()
            task.updated_timestamp = task.updated_at

        # Update the task in the collection
        self.tasks[task_id] = task
        return task

    def list_tasks(self) -> List[Task]:
        """
        Retrieve all tasks in the list (alias for get_all for consistency).
        Returns ordered list of tasks, maintaining insertion order or sorts by ID.

        Returns:
            List of all tasks
        """
        return self.get_all()

    def delete_task(self, task_id: int) -> bool:
        """
        Remove task from list.
        Validates ID exists before deletion.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            # Update progress tracking when task is deleted
            self.update_progress_on_task_change()
            return True
        return False

    def toggle_complete(self, task_id: int) -> bool:
        """
        Toggle completion status.
        Updates the status to completed or pending based on current status,
        validates ID exists before toggling.

        Args:
            task_id: ID of the task to toggle

        Returns:
            True if toggle was successful, False otherwise
        """
        task = self.get_by_id(task_id)
        if not task:
            return False

        # Toggle status based on current status
        if task.status == TaskStatus.COMPLETED:
            task.update_status(TaskStatus.PENDING)
        else:
            task.update_status(TaskStatus.COMPLETED)

        self.tasks[task_id] = task

        # Update progress tracking when task status changes
        self.update_progress_on_task_change()

        return True

    def update_task_status(self, task_id: int, status: TaskStatus) -> bool:
        """
        Update task status directly.

        Args:
            task_id: ID of the task to update
            status: New status for the task

        Returns:
            True if update was successful, False otherwise
        """
        task = self.get_by_id(task_id)
        if not task:
            return False

        task.update_status(status)
        self.tasks[task_id] = task
        return True

    def save_to_file(self):
        """Save all tasks and next_id to the data file using StorageService (Phase 8)."""
        data = {
            "tasks": [task.to_dict() for task in self.tasks.values()],
            "next_id": self.id_manager.get_current_counter()
        }
        self.storage_service.save_to_json(data, self.data_file)

    def load_from_file(self):
        """Load tasks and next_id from the data file using StorageService (Phase 8)."""
        try:
            # Use new StorageService for loading
            data = self.storage_service.load_from_json(self.data_file)

            if data and "tasks" in data and "next_id" in data:
                self.tasks = {}
                for task_data in data["tasks"]:
                    task = Task.from_dict(task_data)
                    self.tasks[task.id] = task

                # Set ID counter from loaded data
                self.id_manager.set_counter(data["next_id"])

                # Update progress tracking after loading tasks
                self.update_progress_on_task_change()
        except ValueError as e:
            # If there's a validation error, start with empty data
            print(f"Warning: Could not load data from {self.data_file}: {e}. Starting with empty task list.")
            self.tasks = {}
            self.id_manager.reset_counter()

            # Update progress tracking with empty data
            self.update_progress_on_task_change()
        except Exception as e:
            # If there's any other error loading the file, start with empty data
            print(f"Warning: Could not load data from {self.data_file}. Starting with empty task list.")
            self.tasks = {}
            self.id_manager.reset_counter()

            # Update progress tracking with empty data
            self.update_progress_on_task_change()

    def delete_all(self) -> bool:
        """
        Delete all tasks from the task list (Phase 8 - User Story 5).

        Returns:
            True if tasks were deleted, False if no tasks exist
        """
        if not self.tasks:
            return False

        self.tasks = {}

        # Update progress tracking after deletion
        self.update_progress_on_task_change()

        return True

    def display_all_tasks_enhanced(self):
        """
        Display all tasks using Rich UI formatting per T019.
        """
        tasks = self.get_all()
        self.rich_ui.display_task_list(tasks)

    def display_task_enhanced(self, task_id: int):
        """
        Display a specific task using Rich UI formatting.

        Args:
            task_id: ID of the task to display
        """
        task = self.get_by_id(task_id)
        if task:
            self.rich_ui.display_task_list([task])
        else:
            self.rich_ui.display_error_message(f"Task with ID {task_id} not found.")

    def display_success_message(self, message: str):
        """
        Display a success message using Rich UI formatting.

        Args:
            message: Success message to display
        """
        self.rich_ui.display_success_message(message)

    def display_error_message(self, message: str):
        """
        Display an error message using Rich UI formatting.

        Args:
            message: Error message to display
        """
        self.rich_ui.display_error_message(message)

    def display_visual_feedback(self, message: str, style: str = "bold"):
        """
        Display visual feedback using Rich UI formatting per FR-020.

        Args:
            message: Feedback message to display
            style: Rich style to apply to the message
        """
        self.rich_ui.display_visual_feedback(message, style)

    def get_progress_stats(self) -> dict:
        """
        Get progress statistics using the ProgressTracker per US4 integration.

        Returns:
            Dictionary with progress statistics
        """
        all_tasks = self.get_all()
        return self.progress_tracker.calculate_from_task_list(all_tasks)

    def display_progress_stats_enhanced(self):
        """
        Display progress statistics using Rich UI formatting per US4.
        """
        stats = self.get_progress_stats()
        self.rich_ui.display_progress_stats(stats)

    def update_progress_on_task_change(self):
        """
        Update progress statistics when tasks change per US4 acceptance scenario.
        """
        all_tasks = self.get_all()
        self.progress_tracker.update_task_completion(all_tasks)