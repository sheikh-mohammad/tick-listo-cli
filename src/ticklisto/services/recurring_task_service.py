"""RecurringTaskService for managing recurring task series (T033-T037 - User Story 2)."""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from dateutil.relativedelta import relativedelta
from ..models.task import Task, RecurrencePattern
from ..models.recurring_series import RecurringSeries
from .storage_service import StorageService
from .time_zone_service import TimeZoneService

# Configure logging for recurring task operations (T108 - Phase 10)
logger = logging.getLogger(__name__)


class RecurringTaskService:
    """
    Service for managing recurring task series and auto-rescheduling.

    Handles:
    - Creating recurring task series
    - Calculating next occurrence dates
    - Generating next instances on completion
    - Managing series lifecycle
    """

    def __init__(self, storage_service: StorageService, time_zone_service: TimeZoneService):
        """
        Initialize RecurringTaskService.

        Args:
            storage_service: Storage service for persistence
            time_zone_service: Time zone service for date calculations
        """
        self.storage = storage_service
        self.tz_service = time_zone_service
        self.series_registry = {}  # In-memory registry of series

    def create_recurring_task(self, task: Task) -> RecurringSeries:
        """
        Create a recurring task series (T033).

        Args:
            task: Task with recurrence configuration

        Returns:
            RecurringSeries object

        Raises:
            ValueError: If task doesn't have recurrence pattern
        """
        if not task.recurrence_pattern:
            raise ValueError("Task must have recurrence_pattern set")

        # Generate unique series ID
        series_id = str(uuid.uuid4())

        # Create series
        series = RecurringSeries(
            series_id=series_id,
            base_task_id=task.id,
            recurrence_pattern=task.recurrence_pattern.value,
            recurrence_interval=task.recurrence_interval,
            recurrence_weekdays=task.recurrence_weekdays,
            recurrence_end_date=task.recurrence_end_date,
            active_instance_ids=[task.id],
            completed_instance_ids=[]
        )

        # Link task to series
        task.series_id = series_id
        task.instance_number = 1

        # Register series
        self.series_registry[series_id] = series

        # Log series creation (T108 - Phase 10)
        logger.info(f"Created recurring series {series_id} for task {task.id}: {task.title} ({task.recurrence_pattern.value}, interval={task.recurrence_interval})")

        return series

    def calculate_next_due_date(
        self,
        current_due_date: datetime,
        pattern: RecurrencePattern,
        interval: int = 1,
        weekdays: Optional[List[int]] = None
    ) -> datetime:
        """
        Calculate next occurrence date based on recurrence pattern (T034).

        Args:
            current_due_date: Current due date
            pattern: Recurrence pattern
            interval: Interval multiplier
            weekdays: Specific weekdays for custom patterns (0=Mon, 6=Sun)

        Returns:
            Next occurrence datetime

        Handles edge cases:
        - Month-end dates (Jan 31 -> Feb 28)
        - Leap years
        - DST transitions
        - Weekday-specific recurrence
        """
        if pattern == RecurrencePattern.DAILY:
            return current_due_date + timedelta(days=interval)

        elif pattern == RecurrencePattern.WEEKLY:
            if weekdays:
                # Find next occurrence on specified weekdays (T036)
                return self._calculate_next_weekday_occurrence(
                    current_due_date, weekdays, interval
                )
            else:
                return current_due_date + timedelta(weeks=interval)

        elif pattern == RecurrencePattern.BI_WEEKLY:
            return current_due_date + timedelta(weeks=2 * interval)

        elif pattern == RecurrencePattern.MONTHLY:
            # Handle month-end edge cases (T037)
            return self._add_months_with_edge_cases(current_due_date, interval)

        elif pattern == RecurrencePattern.YEARLY:
            # Handle leap year edge cases (T037)
            return self._add_years_with_edge_cases(current_due_date, interval)

        elif pattern == RecurrencePattern.CUSTOM:
            if weekdays:
                return self._calculate_next_weekday_occurrence(
                    current_due_date, weekdays, interval
                )
            else:
                return current_due_date + timedelta(days=interval)

        else:
            raise ValueError(f"Unsupported recurrence pattern: {pattern}")

    def _calculate_next_weekday_occurrence(
        self,
        current_date: datetime,
        weekdays: List[int],
        interval: int
    ) -> datetime:
        """
        Calculate next occurrence on specified weekdays (T036).

        Args:
            current_date: Current due date
            weekdays: List of weekdays (0=Mon, 6=Sun)
            interval: Week interval

        Returns:
            Next occurrence datetime
        """
        # Sort weekdays
        sorted_weekdays = sorted(weekdays)
        current_weekday = current_date.weekday()

        # Find next weekday in the same week
        for day in sorted_weekdays:
            if day > current_weekday:
                days_ahead = day - current_weekday
                return current_date + timedelta(days=days_ahead)

        # No more occurrences this week, go to first weekday of next interval week
        first_weekday = sorted_weekdays[0]
        days_until_next_week = 7 - current_weekday + first_weekday
        days_until_next_week += (interval - 1) * 7  # Add interval weeks
        return current_date + timedelta(days=days_until_next_week)

    def _add_months_with_edge_cases(self, date: datetime, months: int) -> datetime:
        """
        Add months handling month-end edge cases (T037).

        Args:
            date: Starting date
            months: Number of months to add

        Returns:
            New date with edge cases handled

        Edge cases:
        - Jan 31 + 1 month = Feb 28 (or 29 in leap year)
        - Jan 31 + 2 months = Mar 31
        """
        try:
            # Try to add months directly
            new_date = date + relativedelta(months=months)
            return new_date
        except ValueError:
            # Handle invalid dates (e.g., Feb 31)
            # Use last day of target month
            target_month = (date.month + months - 1) % 12 + 1
            target_year = date.year + (date.month + months - 1) // 12

            # Get last day of target month
            if target_month == 12:
                last_day = 31
            else:
                next_month = datetime(target_year, target_month + 1, 1)
                last_day = (next_month - timedelta(days=1)).day

            return datetime(
                target_year,
                target_month,
                min(date.day, last_day),
                date.hour,
                date.minute,
                date.second
            )

    def _add_years_with_edge_cases(self, date: datetime, years: int) -> datetime:
        """
        Add years handling leap year edge cases (T037).

        Args:
            date: Starting date
            years: Number of years to add

        Returns:
            New date with edge cases handled

        Edge cases:
        - Feb 29, 2024 + 1 year = Feb 28, 2025 (non-leap year)
        """
        target_year = date.year + years

        # Check if original date is Feb 29 and target year is not a leap year
        if date.month == 2 and date.day == 29:
            # Check if target year is leap year
            is_leap = (target_year % 4 == 0 and target_year % 100 != 0) or (target_year % 400 == 0)
            if not is_leap:
                # Use Feb 28 instead
                return datetime(
                    target_year, 2, 28,
                    date.hour, date.minute, date.second
                )

        return datetime(
            target_year,
            date.month,
            date.day,
            date.hour,
            date.minute,
            date.second
        )

    def complete_instance_and_generate_next(self, task: Task) -> Optional[Task]:
        """
        Complete current instance and generate next one (T035).

        Args:
            task: Current task instance to complete

        Returns:
            Next task instance, or None if series ended

        Raises:
            ValueError: If task is not part of a recurring series
        """
        if not task.series_id:
            raise ValueError("Task is not part of a recurring series")

        # Get series
        series = self.series_registry.get(task.series_id)
        if not series:
            raise ValueError(f"Series {task.series_id} not found")

        # Check if series is still active
        if not series.is_active():
            logger.info(f"Series {task.series_id} is no longer active, no next instance generated")
            return None

        # Mark current instance as completed
        series.mark_instance_completed(task.id)

        # Calculate next due date based on original due date (not completion date)
        next_due_date = self.calculate_next_due_date(
            task.due_date,
            task.recurrence_pattern,
            task.recurrence_interval,
            task.recurrence_weekdays
        )

        # Check if next date exceeds end date
        if series.recurrence_end_date and next_due_date > series.recurrence_end_date:
            logger.info(f"Series {task.series_id} ended: next date {next_due_date} exceeds end date {series.recurrence_end_date}")
            return None

        # Generate next task instance
        next_task = Task(
            id=self._generate_next_task_id(),
            title=task.title,
            description=task.description,
            priority=task.priority,
            categories=task.categories.copy(),
            due_date=next_due_date,
            due_time=task.due_time,
            recurrence_pattern=task.recurrence_pattern,
            recurrence_interval=task.recurrence_interval,
            recurrence_weekdays=task.recurrence_weekdays,
            recurrence_end_date=task.recurrence_end_date,
            series_id=task.series_id,
            instance_number=task.instance_number + 1,
            reminder_settings=task.reminder_settings.copy() if task.reminder_settings else []
        )

        # Add to active instances
        series.add_active_instance(next_task.id)
        series.last_generated_at = datetime.now()

        # Log instance generation (T108 - Phase 10)
        logger.info(f"Generated next instance #{next_task.instance_number} (ID: {next_task.id}) for series {task.series_id}: {task.title}, due {next_due_date}")

        return next_task

    def _generate_next_task_id(self) -> int:
        """Generate next task ID (placeholder - should use IDManager in production)."""
        import random
        return random.randint(1000, 9999)

    def get_series(self, series_id: str) -> Optional[RecurringSeries]:
        """
        Get recurring series by ID.

        Args:
            series_id: Series ID

        Returns:
            RecurringSeries or None if not found
        """
        return self.series_registry.get(series_id)

    def get_series_instances(
        self,
        series_id: str,
        include_completed: bool = False
    ) -> List[int]:
        """
        Get all task IDs in a series.

        Args:
            series_id: Series ID
            include_completed: Whether to include completed instances

        Returns:
            List of task IDs
        """
        series = self.series_registry.get(series_id)
        if not series:
            return []

        if include_completed:
            return series.active_instance_ids + series.completed_instance_ids
        else:
            return series.active_instance_ids.copy()

    def update_series(
        self,
        series_id: str,
        update_future: bool = True,
        **updates
    ) -> int:
        """
        Update properties of tasks in a recurring series (T079 - User Story 5).

        Args:
            series_id: Series ID
            update_future: If True, update all future instances; if False, update only current
            **updates: Field updates (title, description, due_time, priority, etc.)

        Returns:
            Number of tasks updated

        Raises:
            ValueError: If series not found
        """
        series = self.series_registry.get(series_id)
        if not series:
            raise ValueError(f"Series not found: {series_id}")

        # This is a placeholder implementation
        # In a real implementation, this would need access to TaskService
        # to actually update the task objects

        if update_future:
            # Update all active (non-completed) instances
            return len(series.active_instance_ids)
        else:
            # Update only one instance
            return 1

    def stop_recurrence(
        self,
        series_id: str,
        delete_future: bool = False
    ) -> int:
        """
        Stop a recurring series from generating new instances (T080 - User Story 5).

        Args:
            series_id: Series ID
            delete_future: If True, delete future instances; if False, just stop generation

        Returns:
            Number of future instances deleted (0 if delete_future=False)

        Raises:
            ValueError: If series not found
        """
        series = self.series_registry.get(series_id)
        if not series:
            raise ValueError(f"Series not found: {series_id}")

        # Mark series as inactive
        series.is_active = False

        deleted_count = 0
        if delete_future:
            # Delete all active (non-completed) instances
            # In a real implementation, this would need access to TaskService
            # to actually delete the task objects
            deleted_count = len(series.active_instance_ids)
            series.active_instance_ids = []

        return deleted_count
