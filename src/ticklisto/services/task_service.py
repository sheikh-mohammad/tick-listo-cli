from datetime import datetime, time
from typing import Dict, List, Optional
import json
import os
from ..models.task import Task, TaskStatus, Priority
from ..utils.file_handler import FileHandler
from ..ui.rich_ui import RichUI
from .progress_tracker import ProgressTracker
from .storage_service import StorageService
from .id_manager import IDManager
from .recurring_task_service import RecurringTaskService
from .time_zone_service import TimeZoneService


class TaskService:
    """
    Service class for managing tasks with CRUD operations.
    Implements the TaskList operations as defined in the data model.
    """

    def __init__(self, data_file: str = "ticklisto_data.json", reminder_service=None):
        """
        Initialize the TaskService with an empty task list and next_id counter.
        Loads existing data from file if it exists.

        Args:
            data_file: Path to data file
            reminder_service: Optional ReminderService for email reminders (T071)
        """
        self.tasks: Dict[int, Task] = {}
        self.data_file = data_file

        # Initialize new services for Phase 8
        self.storage_service = StorageService()
        self.id_manager = IDManager()

        # Initialize RecurringTaskService for User Story 2
        self.tz_service = TimeZoneService()
        self.recurring_service = RecurringTaskService(self.storage_service, self.tz_service)

        # Initialize ReminderService for User Story 4 (T071)
        self.reminder_service = reminder_service

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
        due_date: Optional[datetime] = None,
        due_time: Optional[time] = None,
        reminder_settings: Optional[List] = None
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
            due_time: Optional time component (HH:MM)
            reminder_settings: Optional list of ReminderSetting objects (T093 - User Story 6)

        Returns:
            Created Task object
        """
        # Validation: due_time requires due_date (T103 - Phase 10)
        if due_time and not due_date:
            raise ValueError("due_time requires due_date to be set")

        # Validation: reminder_settings requires due_time (T104 - Phase 10)
        if reminder_settings and not due_time:
            raise ValueError("reminder_settings requires due_time to be set")

        # Generate ID using IDManager (Phase 8)
        task_id = self.id_manager.generate_id()

        # Apply default reminder settings if task has due_time but no explicit reminders (T093)
        if due_time and not reminder_settings:
            try:
                from ..utils.config_manager import ConfigManager
                from ..models.reminder import ReminderSetting

                config = ConfigManager()
                default_offsets = config.get_default_reminder_offsets()

                # Create ReminderSetting objects from default offsets
                reminder_settings = []
                for offset_minutes in default_offsets:
                    # Generate label
                    if offset_minutes < 60:
                        label = f"{offset_minutes} minutes before"
                    elif offset_minutes < 1440:
                        hours = offset_minutes // 60
                        label = f"{hours} hour{'s' if hours > 1 else ''} before"
                    else:
                        days = offset_minutes // 1440
                        label = f"{days} day{'s' if days > 1 else ''} before"

                    reminder_settings.append(ReminderSetting(
                        offset_minutes=offset_minutes,
                        label=label
                    ))
            except Exception as e:
                print(f"Warning: Failed to load default reminder settings: {e}")
                reminder_settings = None

        # Create a new task with the generated ID
        new_task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            categories=categories if categories is not None else [],
            due_date=due_date,
            due_time=due_time,
            reminder_settings=reminder_settings,
            status=TaskStatus.PENDING  # Default to pending status
        )

        self.tasks[task_id] = new_task

        # Schedule reminders if task has reminder_settings (T071 - User Story 4)
        if self.reminder_service and new_task.reminder_settings:
            try:
                self.reminder_service.schedule_reminders(new_task)
            except Exception as e:
                print(f"Warning: Failed to schedule reminders: {e}")

        # Update progress tracking when task is added
        self.update_progress_on_task_change()

        return new_task

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        categories: List[str] = None,
        due_date: Optional[datetime] = None,
        due_time: Optional[time] = None
    ) -> Task:
        """
        Create a new task (alias for add_task for consistency with tests).

        Args:
            title: Task title
            description: Task description (optional)
            priority: Task priority level (default: MEDIUM)
            categories: List of category tags (optional)
            due_date: Optional due date for the task
            due_time: Optional time component (HH:MM)

        Returns:
            Created Task object
        """
        return self.add_task(title, description, priority, categories, due_date, due_time)

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Get a task by ID (alias for get_by_id for consistency with tests).

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task object if found, None otherwise

        Raises:
            ValueError: If task not found
        """
        task = self.get_by_id(task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} not found")
        return task

    def complete_task(self, task_id: int) -> Task:
        """
        Mark a task as complete.
        For recurring tasks, generates the next instance (T038 - User Story 2).

        Args:
            task_id: ID of the task to complete

        Returns:
            Completed Task object

        Raises:
            ValueError: If task not found
        """
        task = self.get_by_id(task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} not found")

        task.mark_complete()
        self.tasks[task_id] = task

        # Cancel reminders for completed task (T072 - User Story 4)
        if self.reminder_service:
            try:
                self.reminder_service.cancel_reminders(task_id)
            except Exception as e:
                print(f"Warning: Failed to cancel reminders: {e}")

        # If task is recurring, generate next instance (T038 - User Story 2)
        if task.series_id:
            try:
                next_task = self.recurring_service.complete_instance_and_generate_next(task)
                if next_task:
                    # Add next instance to task list
                    self.tasks[next_task.id] = next_task
            except ValueError as e:
                # Log error but don't fail the completion
                print(f"Warning: Failed to generate next recurring instance: {e}")

        # Update progress tracking when task is completed
        self.update_progress_on_task_change()

        return task

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
        due_date: Optional[datetime] = None,
        due_time: Optional[time] = None
    ) -> Optional[Task]:
        """
        Update task properties including enhanced fields.
        Validates updates against field constraints, preserves immutable fields (id, created_at),
        updates mutable fields (title, description, priority, categories, due_date, due_time).

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority level (optional)
            categories: New categories list (optional)
            due_date: New due date (optional)
            due_time: New due time (optional)

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

        # Update due_time if provided (can be set to None to remove time)
        if due_time is not None or 'due_time' in locals():
            task.due_time = due_time
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
            # Cancel reminders for deleted task (T072 - User Story 4)
            if self.reminder_service:
                try:
                    self.reminder_service.cancel_reminders(task_id)
                except Exception as e:
                    print(f"Warning: Failed to cancel reminders: {e}")

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
        """Save all tasks, recurring_series, and next_id to the data file (T039 - User Story 2)."""
        data = {
            "tasks": [task.to_dict() for task in self.tasks.values()],
            "next_id": self.id_manager.get_current_counter(),
            "recurring_series": [
                series.to_dict()
                for series in self.recurring_service.series_registry.values()
            ]
        }
        self.storage_service.save_to_json(data, self.data_file)

    def load_from_file(self):
        """Load tasks, recurring_series, and next_id from the data file (T039 - User Story 2)."""
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

                # Load recurring_series if present (T039 - User Story 2)
                if "recurring_series" in data:
                    from ..models.recurring_series import RecurringSeries
                    for series_data in data["recurring_series"]:
                        series = RecurringSeries.from_dict(series_data)
                        self.recurring_service.series_registry[series.series_id] = series

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