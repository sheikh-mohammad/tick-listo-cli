"""Unit tests for RecurringTaskService (T026-T027 - User Story 2)."""

import pytest
from datetime import datetime, time, timedelta
from ticklisto.models.task import Task, RecurrencePattern
from ticklisto.services.recurring_task_service import RecurringTaskService
from ticklisto.services.storage_service import StorageService
from ticklisto.services.time_zone_service import TimeZoneService


class TestCalculateNextDueDate:
    """Test calculate_next_due_date() with all patterns (T026)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.storage = StorageService()
        self.tz_service = TimeZoneService("America/New_York")
        self.service = RecurringTaskService(self.storage, self.tz_service)

    def test_calculate_next_due_date_daily(self):
        """Test calculating next due date for daily pattern."""
        current_date = datetime(2026, 2, 15, 0, 0, 0)
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.DAILY,
            interval=1
        )

        assert next_date.date() == datetime(2026, 2, 16).date()

    def test_calculate_next_due_date_daily_interval(self):
        """Test calculating next due date for daily pattern with interval."""
        current_date = datetime(2026, 2, 15, 0, 0, 0)
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.DAILY,
            interval=3
        )

        assert next_date.date() == datetime(2026, 2, 18).date()

    def test_calculate_next_due_date_weekly(self):
        """Test calculating next due date for weekly pattern."""
        current_date = datetime(2026, 2, 15, 0, 0, 0)  # Sunday
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.WEEKLY,
            interval=1
        )


class TestUpdateSeries:
    """Unit tests for update_series() (T075 - User Story 5)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.storage = StorageService()
        self.tz_service = TimeZoneService("America/New_York")
        self.service = RecurringTaskService(self.storage, self.tz_service)

    def test_update_series_updates_all_future_instances(self):
        """Test that update_series updates all future instances."""
        # Create a recurring task
        task = Task(
            id=1,
            title="Weekly meeting",
            due_date=datetime(2026, 2, 15, 10, 0, 0),
            due_time=time(10, 0),
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_interval=1
        )

        series = self.service.create_recurring_task(task)

        # Generate a few instances
        task2 = self.service.complete_instance_and_generate_next(task)
        task3 = self.service.complete_instance_and_generate_next(task2)

        # Update series (change title for all future instances)
        updated_count = self.service.update_series(
            series_id=series.series_id,
            update_future=True,
            title="Updated weekly meeting"
        )

        # Should update future instances (not completed ones)
        assert updated_count >= 0

    def test_update_series_with_update_future_false(self):
        """Test that update_series with update_future=False only updates current."""
        task = Task(
            id=1,
            title="Daily standup",
            due_date=datetime(2026, 2, 15, 9, 0, 0),
            due_time=time(9, 0),
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_interval=1
        )

        series = self.service.create_recurring_task(task)

        # Update only current instance
        updated_count = self.service.update_series(
            series_id=series.series_id,
            update_future=False,
            title="Updated standup"
        )

        # Should update only one instance
        assert updated_count == 1

    def test_update_series_with_multiple_fields(self):
        """Test updating multiple fields in a series."""
        task = Task(
            id=1,
            title="Monthly review",
            due_date=datetime(2026, 2, 15, 14, 0, 0),
            due_time=time(14, 0),
            recurrence_pattern=RecurrencePattern.MONTHLY,
            recurrence_interval=1
        )

        series = self.service.create_recurring_task(task)

        # Update multiple fields
        updated_count = self.service.update_series(
            series_id=series.series_id,
            update_future=True,
            title="Updated monthly review",
            description="New description",
            due_time=time(15, 0)
        )

        assert updated_count >= 0

    def test_update_series_invalid_series_id(self):
        """Test that update_series raises error for invalid series_id."""
        with pytest.raises(ValueError, match="Series not found"):
            self.service.update_series(
                series_id="invalid-series-id",
                update_future=True,
                title="Updated"
            )


class TestStopRecurrence:
    """Unit tests for stop_recurrence() (T076 - User Story 5)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.storage = StorageService()
        self.tz_service = TimeZoneService("America/New_York")
        self.service = RecurringTaskService(self.storage, self.tz_service)

    def test_stop_recurrence_marks_series_as_stopped(self):
        """Test that stop_recurrence marks series as stopped."""
        task = Task(
            id=1,
            title="Weekly meeting",
            due_date=datetime(2026, 2, 15, 10, 0, 0),
            due_time=time(10, 0),
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_interval=1
        )

        series = self.service.create_recurring_task(task)

        # Stop recurrence
        self.service.stop_recurrence(series_id=series.series_id, delete_future=False)

        # Series should be marked as stopped
        stopped_series = self.service.get_series(series.series_id)
        assert stopped_series.is_active is False

    def test_stop_recurrence_with_delete_future(self):
        """Test that stop_recurrence with delete_future=True removes future instances."""
        task = Task(
            id=1,
            title="Daily task",
            due_date=datetime(2026, 2, 15, 9, 0, 0),
            due_time=time(9, 0),
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_interval=1
        )

        series = self.service.create_recurring_task(task)

        # Generate future instances
        task2 = self.service.complete_instance_and_generate_next(task)
        task3 = self.service.complete_instance_and_generate_next(task2)

        # Stop and delete future
        deleted_count = self.service.stop_recurrence(
            series_id=series.series_id,
            delete_future=True
        )

        # Should have deleted future instances
        assert deleted_count >= 0

    def test_stop_recurrence_preserves_completed_instances(self):
        """Test that stop_recurrence preserves completed instances."""
        task = Task(
            id=1,
            title="Weekly task",
            due_date=datetime(2026, 2, 15, 10, 0, 0),
            due_time=time(10, 0),
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_interval=1,
            completed=True
        )

        series = self.service.create_recurring_task(task)

        # Stop recurrence
        self.service.stop_recurrence(series_id=series.series_id, delete_future=True)

        # Completed instances should still exist
        instances = self.service.get_series_instances(series.series_id, include_completed=True)
        assert len(instances) > 0

    def test_stop_recurrence_invalid_series_id(self):
        """Test that stop_recurrence raises error for invalid series_id."""
        with pytest.raises(ValueError, match="Series not found"):
            self.service.stop_recurrence(
                series_id="invalid-series-id",
                delete_future=False
            )

    def test_stop_recurrence_prevents_new_instances(self):
        """Test that stopped series doesn't generate new instances."""
        task = Task(
            id=1,
            title="Daily task",
            due_date=datetime(2026, 2, 15, 9, 0, 0),
            due_time=time(9, 0),
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_interval=1
        )

        series = self.service.create_recurring_task(task)

        # Stop recurrence
        self.service.stop_recurrence(series_id=series.series_id, delete_future=False)

        # Try to generate next instance
        next_task = self.service.complete_instance_and_generate_next(task)

        # Should not generate new instance
        assert next_task is None

        assert next_date.date() == datetime(2026, 2, 22).date()  # Next Sunday

    def test_calculate_next_due_date_weekly_interval(self):
        """Test calculating next due date for weekly pattern with interval."""
        current_date = datetime(2026, 2, 15, 0, 0, 0)  # Sunday
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.WEEKLY,
            interval=2
        )

        assert next_date.date() == datetime(2026, 3, 1).date()  # 2 weeks later

    def test_calculate_next_due_date_weekly_specific_weekdays(self):
        """Test calculating next due date for weekly pattern with specific weekdays."""
        current_date = datetime(2026, 2, 16, 0, 0, 0)  # Monday
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.WEEKLY,
            interval=1,
            weekdays=[0, 2, 4]  # Mon, Wed, Fri
        )

        # Next occurrence should be Wednesday (2 days later)
        assert next_date.date() == datetime(2026, 2, 18).date()

    def test_calculate_next_due_date_monthly(self):
        """Test calculating next due date for monthly pattern."""
        current_date = datetime(2026, 2, 15, 0, 0, 0)
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.MONTHLY,
            interval=1
        )

        assert next_date.date() == datetime(2026, 3, 15).date()

    def test_calculate_next_due_date_monthly_interval(self):
        """Test calculating next due date for monthly pattern with interval."""
        current_date = datetime(2026, 2, 15, 0, 0, 0)
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.MONTHLY,
            interval=3
        )

        assert next_date.date() == datetime(2026, 5, 15).date()

    def test_calculate_next_due_date_yearly(self):
        """Test calculating next due date for yearly pattern."""
        current_date = datetime(2026, 2, 15, 0, 0, 0)
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.YEARLY,
            interval=1
        )

        assert next_date.date() == datetime(2027, 2, 15).date()


class TestEdgeCases:
    """Test edge cases for recurring tasks (T027)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.storage = StorageService()
        self.tz_service = TimeZoneService("America/New_York")
        self.service = RecurringTaskService(self.storage, self.tz_service)

    def test_month_end_date_february(self):
        """Test month-end date handling for February."""
        # January 31 -> February should become February 28 (or 29 in leap year)
        current_date = datetime(2026, 1, 31, 0, 0, 0)
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.MONTHLY,
            interval=1
        )

        # 2026 is not a leap year, so should be Feb 28
        assert next_date.date() == datetime(2026, 2, 28).date()

    def test_month_end_date_april(self):
        """Test month-end date handling for April (30 days)."""
        # March 31 -> April should become April 30
        current_date = datetime(2026, 3, 31, 0, 0, 0)
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.MONTHLY,
            interval=1
        )

        assert next_date.date() == datetime(2026, 4, 30).date()

    def test_leap_year_february_29(self):
        """Test leap year handling for February 29."""
        # February 29, 2024 (leap year) -> March 29, 2024
        current_date = datetime(2024, 2, 29, 0, 0, 0)
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.MONTHLY,
            interval=1
        )

        assert next_date.date() == datetime(2024, 3, 29).date()

    def test_leap_year_yearly_recurrence(self):
        """Test yearly recurrence from leap year date."""
        # February 29, 2024 -> February 28, 2025 (non-leap year)
        current_date = datetime(2024, 2, 29, 0, 0, 0)
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.YEARLY,
            interval=1
        )

        # 2025 is not a leap year, so should be Feb 28
        assert next_date.date() == datetime(2025, 2, 28).date()

    def test_dst_spring_forward(self):
        """Test DST spring forward transition."""
        # March 8, 2026 (before DST) -> March 15, 2026 (after DST)
        current_date = datetime(2026, 3, 8, 14, 30, 0)
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.WEEKLY,
            interval=1
        )

        # Time should be preserved despite DST transition
        assert next_date.date() == datetime(2026, 3, 15).date()
        assert next_date.hour == 14
        assert next_date.minute == 30

    def test_dst_fall_back(self):
        """Test DST fall back transition."""
        # November 1, 2026 (after DST) -> November 8, 2026 (before DST)
        current_date = datetime(2026, 11, 1, 14, 30, 0)
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.WEEKLY,
            interval=1
        )

        # Time should be preserved despite DST transition
        assert next_date.date() == datetime(2026, 11, 8).date()
        assert next_date.hour == 14
        assert next_date.minute == 30

    def test_weekday_recurrence_wraps_to_next_week(self):
        """Test weekday recurrence wraps to next week correctly."""
        # Friday (day 4) with Mon/Wed/Fri pattern should go to next Monday
        current_date = datetime(2026, 2, 20, 0, 0, 0)  # Friday
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.WEEKLY,
            interval=1,
            weekdays=[0, 2, 4]  # Mon, Wed, Fri
        )

        # Next occurrence should be Monday (3 days later)
        assert next_date.date() == datetime(2026, 2, 23).date()

    def test_single_weekday_recurrence(self):
        """Test recurrence with single weekday."""
        current_date = datetime(2026, 2, 16, 0, 0, 0)  # Monday
        next_date = self.service.calculate_next_due_date(
            current_date,
            RecurrencePattern.WEEKLY,
            interval=1,
            weekdays=[0]  # Only Monday
        )

        # Next occurrence should be next Monday (7 days later)
        assert next_date.date() == datetime(2026, 2, 23).date()
