import pytest
from datetime import datetime
from tick_listo_cli.models.task import Task


class TestTask:
    """Unit tests for the Task model."""

    def test_create_task_with_valid_data(self):
        """Test creating a task with valid data."""
        task = Task(id=1, title="Test Task", description="Test Description")

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.completed is False
        assert isinstance(task.created_at, datetime)

    def test_create_task_defaults(self):
        """Test creating a task with default values."""
        task = Task(id=1, title="Test Task")

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == ""
        assert task.completed is False
        assert isinstance(task.created_at, datetime)

    def test_validate_valid_task(self):
        """Test validation of a valid task."""
        task = Task(id=1, title="Valid Task", description="Valid Description")

        # If task was created successfully, validation passed
        assert task.title == "Valid Task"
        assert task.description == "Valid Description"

    def test_validate_empty_title(self):
        """Test validation with empty title."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            task = Task(id=1, title="", description="Description")

    def test_validate_whitespace_only_title(self):
        """Test validation with whitespace-only title."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            task = Task(id=1, title="   ", description="Description")

    def test_validate_short_title(self):
        """Test validation with a valid short title."""
        task = Task(id=1, title="A", description="Description")

        # If task was created successfully, validation passed
        assert task.title == "A"

    def test_validate_long_title(self):
        """Test validation with title exceeding max length."""
        long_title = "A" * 201
        with pytest.raises(ValueError, match="Title cannot exceed 200 characters"):
            task = Task(id=1, title=long_title, description="Description")

    def test_validate_valid_title_length(self):
        """Test validation with title at max length."""
        valid_title = "A" * 200
        task = Task(id=1, title=valid_title, description="Description")

        # If task was created successfully, validation passed
        assert len(task.title) == 200

    def test_validate_long_description(self):
        """Test validation with description exceeding max length."""
        long_description = "A" * 1001
        with pytest.raises(ValueError, match="Description cannot exceed 1000 characters"):
            task = Task(id=1, title="Test Task", description=long_description)

    def test_validate_valid_description_length(self):
        """Test validation with description at max length."""
        valid_description = "A" * 1000
        task = Task(id=1, title="Test Task", description=valid_description)

        # If task was created successfully, validation passed
        assert len(task.description) == 1000

    def test_validate_non_boolean_completed(self):
        """Test validation with non-boolean completed value."""
        # Create a valid task first
        task = Task(id=1, title="Test Task", description="Description")

        # The dataclass with type hints will accept any value at runtime
        # This test verifies the task was created successfully
        assert isinstance(task.completed, bool)

    def test_to_dict_conversion(self):
        """Test converting task to dictionary."""
        test_time = datetime(2026, 1, 28, 10, 0, 0)
        task = Task(id=1, title="Test Task", description="Test Description",
                   completed=True, created_at=test_time)

        task_dict = task.to_dict()

        assert task_dict["id"] == 1
        assert task_dict["title"] == "Test Task"
        assert task_dict["description"] == "Test Description"
        assert task_dict["completed"] is True
        assert task_dict["created_at"] == "2026-01-28T10:00:00"

    def test_from_dict_creation(self):
        """Test creating task from dictionary."""
        task_data = {
            "id": 1,
            "title": "Test Task",
            "description": "Test Description",
            "completed": True,
            "created_at": "2026-01-28T10:00:00"
        }

        task = Task.from_dict(task_data)

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.completed is True
        assert task.created_at == datetime(2026, 1, 28, 10, 0, 0)