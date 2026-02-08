"""Unit tests for RecurringSeries entity (T025 - User Story 2)."""

import pytest
from datetime import datetime
from ticklisto.models.recurring_series import RecurringSeries


class TestRecurringSeriesEntity:
    """Test RecurringSeries entity."""

    def test_create_recurring_series(self):
        """Test creating a recurring series."""
        series = RecurringSeries(
            series_id="test-series-123",
            base_task_id=1,
            recurrence_pattern="weekly",
            recurrence_interval=1
        )

        assert series.series_id == "test-series-123"
        assert series.base_task_id == 1
        assert series.recurrence_pattern == "weekly"
        assert series.recurrence_interval == 1
        assert series.active_instance_ids == []
        assert series.completed_instance_ids == []

    def test_recurring_series_with_weekdays(self):
        """Test recurring series with specific weekdays."""
        series = RecurringSeries(
            series_id="test-series-123",
            base_task_id=1,
            recurrence_pattern="custom",
            recurrence_interval=1,
            recurrence_weekdays=[0, 2, 4]  # Mon, Wed, Fri
        )

        assert series.recurrence_weekdays == [0, 2, 4]

    def test_recurring_series_with_end_date(self):
        """Test recurring series with end date."""
        end_date = datetime(2026, 12, 31)
        series = RecurringSeries(
            series_id="test-series-123",
            base_task_id=1,
            recurrence_pattern="daily",
            recurrence_interval=1,
            recurrence_end_date=end_date
        )

        assert series.recurrence_end_date == end_date

    def test_recurring_series_validation_interval(self):
        """Test that recurrence_interval must be >= 1."""
        with pytest.raises(ValueError, match="recurrence_interval must be >= 1"):
            RecurringSeries(
                series_id="test-series-123",
                base_task_id=1,
                recurrence_pattern="daily",
                recurrence_interval=0
            )

    def test_recurring_series_validation_weekdays(self):
        """Test that recurrence_weekdays values must be 0-6."""
        with pytest.raises(ValueError, match="recurrence_weekdays values must be 0-6"):
            RecurringSeries(
                series_id="test-series-123",
                base_task_id=1,
                recurrence_pattern="custom",
                recurrence_interval=1,
                recurrence_weekdays=[0, 7]  # 7 is invalid
            )

    def test_recurring_series_serialization(self):
        """Test RecurringSeries.to_dict()."""
        series = RecurringSeries(
            series_id="test-series-123",
            base_task_id=1,
            recurrence_pattern="weekly",
            recurrence_interval=2,
            active_instance_ids=[1, 2],
            completed_instance_ids=[3, 4]
        )

        data = series.to_dict()

        assert data["series_id"] == "test-series-123"
        assert data["base_task_id"] == 1
        assert data["recurrence_pattern"] == "weekly"
        assert data["recurrence_interval"] == 2
        assert data["active_instance_ids"] == [1, 2]
        assert data["completed_instance_ids"] == [3, 4]

    def test_recurring_series_deserialization(self):
        """Test RecurringSeries.from_dict()."""
        data = {
            "series_id": "test-series-123",
            "base_task_id": 1,
            "recurrence_pattern": "monthly",
            "recurrence_interval": 1,
            "recurrence_weekdays": None,
            "recurrence_end_date": None,
            "active_instance_ids": [1],
            "completed_instance_ids": [],
            "created_at": "2026-02-08T10:00:00",
            "last_generated_at": "2026-02-08T10:00:00"
        }

        series = RecurringSeries.from_dict(data)

        assert series.series_id == "test-series-123"
        assert series.base_task_id == 1
        assert series.recurrence_pattern == "monthly"
        assert series.active_instance_ids == [1]

    def test_is_active_no_end_date(self):
        """Test is_active() returns True when no end date."""
        series = RecurringSeries(
            series_id="test-series-123",
            base_task_id=1,
            recurrence_pattern="daily",
            recurrence_interval=1
        )

        assert series.is_active() is True

    def test_is_active_future_end_date(self):
        """Test is_active() returns True when end date is in future."""
        future_date = datetime(2030, 12, 31)
        series = RecurringSeries(
            series_id="test-series-123",
            base_task_id=1,
            recurrence_pattern="daily",
            recurrence_interval=1,
            recurrence_end_date=future_date
        )

        assert series.is_active() is True

    def test_is_active_past_end_date(self):
        """Test is_active() returns False when end date is in past."""
        past_date = datetime(2020, 1, 1)
        series = RecurringSeries(
            series_id="test-series-123",
            base_task_id=1,
            recurrence_pattern="daily",
            recurrence_interval=1,
            recurrence_end_date=past_date
        )

        assert series.is_active() is False

    def test_add_active_instance(self):
        """Test adding active instance."""
        series = RecurringSeries(
            series_id="test-series-123",
            base_task_id=1,
            recurrence_pattern="daily",
            recurrence_interval=1
        )

        series.add_active_instance(2)
        assert 2 in series.active_instance_ids

        # Adding duplicate should not create duplicate
        series.add_active_instance(2)
        assert series.active_instance_ids.count(2) == 1

    def test_mark_instance_completed(self):
        """Test marking instance as completed."""
        series = RecurringSeries(
            series_id="test-series-123",
            base_task_id=1,
            recurrence_pattern="daily",
            recurrence_interval=1,
            active_instance_ids=[1, 2]
        )

        series.mark_instance_completed(1)

        assert 1 not in series.active_instance_ids
        assert 1 in series.completed_instance_ids
        assert 2 in series.active_instance_ids

    def test_completed_instances_limit(self):
        """Test that completed instances are limited to 100."""
        series = RecurringSeries(
            series_id="test-series-123",
            base_task_id=1,
            recurrence_pattern="daily",
            recurrence_interval=1
        )

        # Add 150 completed instances
        for i in range(150):
            series.completed_instance_ids.append(i)
            if len(series.completed_instance_ids) > 100:
                series.completed_instance_ids = series.completed_instance_ids[-100:]

        assert len(series.completed_instance_ids) == 100
        # Should keep the last 100 (50-149)
        assert series.completed_instance_ids[0] == 50
        assert series.completed_instance_ids[-1] == 149
