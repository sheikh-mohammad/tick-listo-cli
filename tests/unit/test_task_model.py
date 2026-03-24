"""
Unit tests for enhanced Task model with priority, categories, and due_date.
Following TDD approach - these tests are written FIRST and should FAIL initially.
"""
import pytest
from datetime import datetime, timedelta
from tick_listo_cli.models.task import Task, Priority


class TestPriorityEnum:
    """Test Priority enum validation (T008)."""

    def test_priority_enum_values(self):
        """Test that Priority enum has correct values."""
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"

    def test_priority_enum_from_string(self):
        """Test creating Priority from string."""
        assert Priority("high") == Priority.HIGH
        assert Priority("medium") == Priority.MEDIUM
        assert Priority("low") == Priority.LOW

    def test_priority_enum_invalid_value(self):
        """Test that invalid priority raises ValueError."""
        with pytest.raises(ValueError):
            Priority("invalid")

    def test_priority_enum_case_sensitive(self):
        """Test that Priority enum is case-sensitive."""
        with pytest.raises(ValueError):
            Priority("HIGH")


class TestTaskModelEnhanced:
    """Test enhanced Task model with new fields (T009)."""

    def test_create_task_with_priority(self):
        """Test creating task with priority field."""
        task = Task(
            id=1,
            title="Test Task",
            priority=Priority.HIGH
        )
        assert task.priority == Priority.HIGH

    def test_create_task_with_default_priority(self):
        """Test that default priority is MEDIUM."""
        task = Task(id=1, title="Test Task")
        assert task.priority == Priority.MEDIUM

    def test_create_task_with_categories(self):
        """Test creating task with categories."""
        task = Task(
            id=1,
            title="Test Task",
            categories=["work", "urgent"]
        )
        assert task.categories == ["work", "urgent"]

    def test_create_task_with_empty_categories(self):
        """Test that default categories is empty list."""
        task = Task(id=1, title="Test Task")
        assert task.categories == []

    def test_create_task_with_due_date(self):
        """Test creating task with due date."""
        due_date = datetime(2026, 2, 15, 10, 0, 0)
        task = Task(
            id=1,
            title="Test Task",
            due_date=due_date
        )
        assert task.due_date == due_date

    def test_create_task_with_no_due_date(self):
        """Test that default due_date is None."""
        task = Task(id=1, title="Test Task")
        assert task.due_date is None

    def test_task_has_created_at_timestamp(self):
        """Test that created_at is auto-generated."""
        task = Task(id=1, title="Test Task")
        assert isinstance(task.created_at, datetime)

    def test_task_has_updated_at_timestamp(self):
        """Test that updated_at is auto-generated."""
        task = Task(id=1, title="Test Task")
        assert isinstance(task.updated_at, datetime)

    def test_category_normalization_lowercase(self):
        """Test that categories are normalized to lowercase."""
        task = Task(
            id=1,
            title="Test Task",
            categories=["Work", "HOME", "Personal"]
        )
        assert "work" in task.categories
        assert "home" in task.categories
        assert "personal" in task.categories

    def test_category_deduplication(self):
        """Test that duplicate categories are removed."""
        task = Task(
            id=1,
            title="Test Task",
            categories=["work", "work", "home"]
        )
        assert len(task.categories) == 2
        assert "work" in task.categories
        assert "home" in task.categories

    def test_category_whitespace_trimming(self):
        """Test that category whitespace is trimmed."""
        task = Task(
            id=1,
            title="Test Task",
            categories=["  work  ", "home"]
        )
        assert "work" in task.categories
        assert "  work  " not in task.categories

    def test_category_max_length_validation(self):
        """Test that categories exceeding 50 chars raise error."""
        long_category = "a" * 51
        with pytest.raises(ValueError, match="exceeds 50 characters"):
            Task(
                id=1,
                title="Test Task",
                categories=[long_category]
            )

    def test_title_validation_empty(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(id=1, title="")

    def test_title_validation_max_length(self):
        """Test that title exceeding 200 chars raises error."""
        long_title = "a" * 201
        with pytest.raises(ValueError, match="Title cannot exceed 200 characters"):
            Task(id=1, title=long_title)

    def test_description_validation_max_length(self):
        """Test that description exceeding 1000 chars raises error."""
        long_description = "a" * 1001
        with pytest.raises(ValueError, match="Description cannot exceed 1000 characters"):
            Task(id=1, title="Test", description=long_description)


class TestTaskHelperMethods:
    """Test Task model helper methods (T010)."""

    def test_mark_complete(self):
        """Test marking task as complete."""
        task = Task(id=1, title="Test Task")
        task.mark_complete()
        assert task.completed is True

    def test_mark_incomplete(self):
        """Test marking task as incomplete."""
        task = Task(id=1, title="Test Task", completed=True)
        task.mark_incomplete()
        assert task.completed is False

    def test_update_field_updates_timestamp(self):
        """Test that update_field refreshes updated_at."""
        task = Task(id=1, title="Test Task")
        old_timestamp = task.updated_at
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        task.update_field("title", "New Title")
        assert task.updated_at > old_timestamp

    def test_is_overdue_with_past_due_date(self):
        """Test is_overdue returns True for past due date."""
        past_date = datetime.now() - timedelta(days=1)
        task = Task(id=1, title="Test Task", due_date=past_date)
        assert task.is_overdue() is True

    def test_is_overdue_with_future_due_date(self):
        """Test is_overdue returns False for future due date."""
        future_date = datetime.now() + timedelta(days=1)
        task = Task(id=1, title="Test Task", due_date=future_date)
        assert task.is_overdue() is False

    def test_is_overdue_with_no_due_date(self):
        """Test is_overdue returns False when no due date."""
        task = Task(id=1, title="Test Task")
        assert task.is_overdue() is False

    def test_is_overdue_completed_task(self):
        """Test is_overdue returns False for completed tasks."""
        past_date = datetime.now() - timedelta(days=1)
        task = Task(id=1, title="Test Task", due_date=past_date, completed=True)
        assert task.is_overdue() is False

    def test_matches_keyword_in_title(self):
        """Test matches_keyword finds keyword in title."""
        task = Task(id=1, title="Buy groceries")
        assert task.matches_keyword("groceries") is True

    def test_matches_keyword_in_description(self):
        """Test matches_keyword finds keyword in description."""
        task = Task(id=1, title="Shopping", description="Buy milk and eggs")
        assert task.matches_keyword("milk") is True

    def test_matches_keyword_case_insensitive(self):
        """Test matches_keyword is case-insensitive."""
        task = Task(id=1, title="Buy Groceries")
        assert task.matches_keyword("groceries") is True
        assert task.matches_keyword("GROCERIES") is True

    def test_matches_keyword_not_found(self):
        """Test matches_keyword returns False when not found."""
        task = Task(id=1, title="Buy groceries")
        assert task.matches_keyword("meeting") is False

    def test_has_category(self):
        """Test has_category checks for specific category."""
        task = Task(id=1, title="Test", categories=["work", "urgent"])
        assert task.has_category("work") is True
        assert task.has_category("home") is False

    def test_has_category_case_insensitive(self):
        """Test has_category is case-insensitive."""
        task = Task(id=1, title="Test", categories=["work"])
        assert task.has_category("Work") is True
        assert task.has_category("WORK") is True

    def test_has_any_category_or_logic(self):
        """Test has_any_category with OR logic."""
        task = Task(id=1, title="Test", categories=["work", "urgent"])
        assert task.has_any_category(["work", "home"]) is True
        assert task.has_any_category(["home", "personal"]) is False

    def test_has_all_categories_and_logic(self):
        """Test has_all_categories with AND logic."""
        task = Task(id=1, title="Test", categories=["work", "urgent"])
        assert task.has_all_categories(["work", "urgent"]) is True
        assert task.has_all_categories(["work", "home"]) is False
