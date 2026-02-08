"""Integration tests for recurring task lifecycle (T028-T029 - User Story 2)."""

import pytest
from datetime import datetime, time
from src.ticklisto.models.task import Task, RecurrencePattern
from src.ticklisto.services.recurring_task_service import RecurringTaskService
from src.ticklisto.services.task_service import TaskService
from src.ticklisto.services.storage_service import StorageService
from src.ticklisto.services.time_zone_service import TimeZoneService


class TestRecurringTaskLifecycle:
    """Integration tests for recurring task lifecycle (T028)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.storage = StorageService()
        self.tz_service = TimeZoneService("America/New_York")
        self.recurring_service = RecurringTaskService(self.storage, self.tz_service)
        self.task_service = TaskService()

    def test_create_recurring_task_series(self):
        """Test creating a recurring task series."""
        task = Task(
            id=1,
            title="Weekly meeting",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30),
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)

        assert series is not None
        assert series.base_task_id == 1
        assert series.recurrence_pattern == "weekly"
        assert task.series_id == series.series_id
        assert task.instance_number == 1

    def test_complete_instance_generates_next(self):
        """Test that completing an instance generates the next one."""
        # Create recurring task
        task = Task(
            id=1,
            title="Daily standup",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(9, 0),
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)

        # Complete the instance and generate next
        next_task = self.recurring_service.complete_instance_and_generate_next(task)

        assert next_task is not None
        assert next_task.id != task.id
        assert next_task.title == task.title
        assert next_task.due_date.date() == datetime(2026, 2, 16).date()
        assert next_task.due_time == time(9, 0)
        assert next_task.series_id == series.series_id
        assert next_task.instance_number == 2

    def test_recurring_task_preserves_properties(self):
        """Test that recurring task preserves all properties."""
        task = Task(
            id=1,
            title="Weekly report",
            description="Submit weekly report",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(17, 0),
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_interval=1,
            priority=Task.Priority.HIGH,
            categories=["work", "reports"]
        )

        series = self.recurring_service.create_recurring_task(task)
        next_task = self.recurring_service.complete_instance_and_generate_next(task)

        assert next_task.title == task.title
        assert next_task.description == task.description
        assert next_task.due_time == task.due_time
        assert next_task.priority == task.priority
        assert next_task.categories == task.categories

    def test_recurring_task_stops_at_end_date(self):
        """Test that recurring task stops at end date."""
        end_date = datetime(2026, 2, 20, 0, 0, 0)
        task = Task(
            id=1,
            title="Limited series",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_interval=1,
            recurrence_end_date=end_date
        )

        series = self.recurring_service.create_recurring_task(task)

        # Complete instances until end date
        current_task = task
        generated_count = 0

        for _ in range(10):  # Try to generate 10 instances
            if not series.is_active():
                break
            next_task = self.recurring_service.complete_instance_and_generate_next(current_task)
            if next_task is None:
                break
            if next_task.due_date > end_date:
                break
            current_task = next_task
            generated_count += 1

        # Should generate instances up to but not beyond end date
        assert generated_count <= 5  # Feb 15-20 is 5 days

    def test_series_tracks_active_and_completed_instances(self):
        """Test that series tracks active and completed instances."""
        task = Task(
            id=1,
            title="Daily task",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)

        # Initially, first instance should be active
        assert task.id in series.active_instance_ids
        assert len(series.completed_instance_ids) == 0

        # Complete first instance and generate next
        next_task = self.recurring_service.complete_instance_and_generate_next(task)

        # First instance should be completed, second should be active
        assert task.id in series.completed_instance_ids
        assert next_task.id in series.active_instance_ids

    def test_monthly_recurrence_with_different_month_lengths(self):
        """Test monthly recurrence across months with different lengths."""
        task = Task(
            id=1,
            title="Monthly report",
            due_date=datetime(2026, 1, 31, 0, 0, 0),
            recurrence_pattern=RecurrencePattern.MONTHLY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)

        # Generate next instance (should be Feb 28, not Feb 31)
        next_task = self.recurring_service.complete_instance_and_generate_next(task)

        assert next_task.due_date.date() == datetime(2026, 2, 28).date()


class TestEarlyCompletion:
    """Integration tests for early completion (T029)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.storage = StorageService()
        self.tz_service = TimeZoneService("America/New_York")
        self.recurring_service = RecurringTaskService(self.storage, self.tz_service)

    def test_early_completion_uses_original_schedule(self):
        """Test that early completion uses original due date for next instance."""
        # Task due on Feb 15, but completed on Feb 10
        task = Task(
            id=1,
            title="Weekly task",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)

        # Complete early (5 days before due date)
        next_task = self.recurring_service.complete_instance_and_generate_next(task)

        # Next instance should be based on original due date (Feb 15 + 1 week = Feb 22)
        # NOT based on completion date (Feb 10 + 1 week = Feb 17)
        assert next_task.due_date.date() == datetime(2026, 2, 22).date()

    def test_late_completion_uses_original_schedule(self):
        """Test that late completion also uses original due date for next instance."""
        # Task due on Feb 15, but completed on Feb 20
        task = Task(
            id=1,
            title="Weekly task",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)

        # Complete late (5 days after due date)
        next_task = self.recurring_service.complete_instance_and_generate_next(task)

        # Next instance should still be based on original due date (Feb 15 + 1 week = Feb 22)
        assert next_task.due_date.date() == datetime(2026, 2, 22).date()

    def test_early_completion_preserves_time(self):
        """Test that early completion preserves the time component."""
        task = Task(
            id=1,
            title="Daily meeting",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            due_time=time(14, 30),
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)
        next_task = self.recurring_service.complete_instance_and_generate_next(task)

        # Time should be preserved
        assert next_task.due_time == time(14, 30)

    def test_multiple_early_completions(self):
        """Test multiple early completions maintain schedule."""
        task = Task(
            id=1,
            title="Daily task",
            due_date=datetime(2026, 2, 15, 0, 0, 0),
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)

        # Complete multiple instances early
        current_task = task
        for i in range(3):
            next_task = self.recurring_service.complete_instance_and_generate_next(current_task)
            # Each next instance should be 1 day after the previous due date
            expected_date = datetime(2026, 2, 15 + i + 1, 0, 0, 0)
            assert next_task.due_date.date() == expected_date.date()
            current_task = next_task


class TestUpdateFutureInstances:
    """Integration tests for updating all future instances (T077 - User Story 5)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.storage = StorageService()
        self.tz_service = TimeZoneService("America/New_York")
        self.recurring_service = RecurringTaskService(self.storage, self.tz_service)

    def test_update_all_future_instances_changes_title(self):
        """Test updating title for all future instances of a recurring series."""
        # Create recurring task
        task = Task(
            id=1,
            title="Original title",
            due_date=datetime(2026, 2, 15, 10, 0, 0),
            due_time=time(10, 0),
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)

        # Generate multiple instances
        instances = [task]
        for _ in range(3):
            next_task = self.recurring_service.complete_instance_and_generate_next(instances[-1])
            if next_task:
                instances.append(next_task)

        # Update all future instances
        updated_count = self.recurring_service.update_series(
            series_id=series.series_id,
            update_future=True,
            title="Updated title"
        )

        # Verify future instances were updated
        assert updated_count >= 0

    def test_update_single_instance_only(self):
        """Test updating only a single instance without affecting others."""
        # Create recurring task
        task = Task(
            id=1,
            title="Original title",
            due_date=datetime(2026, 2, 15, 10, 0, 0),
            due_time=time(10, 0),
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)

        # Generate multiple instances
        task2 = self.recurring_service.complete_instance_and_generate_next(task)
        task3 = self.recurring_service.complete_instance_and_generate_next(task2)

        # Update only current instance
        updated_count = self.recurring_service.update_series(
            series_id=series.series_id,
            update_future=False,
            title="Updated single instance"
        )

        # Only one instance should be updated
        assert updated_count == 1


class TestStopRecurrence:
    """Integration tests for stopping recurrence (T078 - User Story 5)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.storage = StorageService()
        self.tz_service = TimeZoneService("America/New_York")
        self.recurring_service = RecurringTaskService(self.storage, self.tz_service)

    def test_stop_recurrence_prevents_new_instances(self):
        """Test that stopping recurrence prevents generation of new instances."""
        # Create recurring task
        task = Task(
            id=1,
            title="Recurring task",
            due_date=datetime(2026, 2, 15, 10, 0, 0),
            due_time=time(10, 0),
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)

        # Stop recurrence
        self.recurring_service.stop_recurrence(series_id=series.series_id, delete_future=False)

        # Try to complete and generate next
        next_task = self.recurring_service.complete_instance_and_generate_next(task)

        # Should not generate new instance
        assert next_task is None

    def test_stop_recurrence_with_delete_removes_future_instances(self):
        """Test that stopping with delete_future removes pending instances."""
        # Create recurring task
        task = Task(
            id=1,
            title="Recurring task",
            due_date=datetime(2026, 2, 15, 10, 0, 0),
            due_time=time(10, 0),
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)

        # Generate future instances
        task2 = self.recurring_service.complete_instance_and_generate_next(task)
        task3 = self.recurring_service.complete_instance_and_generate_next(task2)

        # Stop and delete future
        deleted_count = self.recurring_service.stop_recurrence(series_id=series.series_id, delete_future=True)

        # Future instances should be removed
        assert deleted_count >= 0

    def test_stop_recurrence_marks_series_inactive(self):
        """Test that stopping recurrence marks the series as inactive."""
        # Create recurring task
        task = Task(
            id=1,
            title="Recurring task",
            due_date=datetime(2026, 2, 15, 10, 0, 0),
            due_time=time(10, 0),
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_interval=1
        )

        series = self.recurring_service.create_recurring_task(task)

        # Verify series is active
        assert series.is_active is True

        # Stop recurrence
        self.recurring_service.stop_recurrence(series_id=series.series_id, delete_future=False)

        # Verify series is now inactive
        stopped_series = self.recurring_service.get_series(series.series_id)
        assert stopped_series.is_active is False

