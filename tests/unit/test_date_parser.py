"""
Unit tests for date parser utility.
Following TDD approach - these tests are written FIRST and should FAIL initially.
"""
import pytest
from datetime import datetime, timedelta, time
from ticklisto.utils.date_parser import parse_flexible_date, parse_time, parse_date_time


class TestDateParser:
    """Test date parser utility (T014)."""

    def test_parse_standard_format_mmddyyyy(self):
        """Test parsing MM/DD/YYYY format."""
        result = parse_flexible_date("02/15/2026")
        assert result.year == 2026
        assert result.month == 2
        assert result.day == 15

    def test_parse_standard_format_ddmmyyyy(self):
        """Test parsing DD-MM-YYYY format."""
        result = parse_flexible_date("15-02-2026")
        assert result.year == 2026
        assert result.month == 2
        assert result.day == 15

    def test_parse_standard_format_yyyymmdd(self):
        """Test parsing YYYY-MM-DD format."""
        result = parse_flexible_date("2026-02-15")
        assert result.year == 2026
        assert result.month == 2
        assert result.day == 15

    def test_parse_natural_language_today(self):
        """Test parsing 'today'."""
        result = parse_flexible_date("today")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        assert result.date() == today.date()

    def test_parse_natural_language_tomorrow(self):
        """Test parsing 'tomorrow'."""
        result = parse_flexible_date("tomorrow")
        tomorrow = datetime.now() + timedelta(days=1)
        assert result.date() == tomorrow.date()

    def test_parse_natural_language_next_week(self):
        """Test parsing 'next week'."""
        result = parse_flexible_date("next week")
        next_week = datetime.now() + timedelta(weeks=1)
        assert result.date() == next_week.date()

    def test_parse_natural_language_in_days(self):
        """Test parsing 'in X days' format."""
        result = parse_flexible_date("in 5 days")
        expected = datetime.now() + timedelta(days=5)
        assert result.date() == expected.date()

    def test_parse_natural_language_in_one_day(self):
        """Test parsing 'in 1 day' format."""
        result = parse_flexible_date("in 1 day")
        expected = datetime.now() + timedelta(days=1)
        assert result.date() == expected.date()

    def test_parse_case_insensitive(self):
        """Test that parsing is case-insensitive."""
        result = parse_flexible_date("TODAY")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        assert result.date() == today.date()

    def test_parse_with_whitespace(self):
        """Test that whitespace is handled correctly."""
        result = parse_flexible_date("  today  ")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        assert result.date() == today.date()

    def test_parse_invalid_format(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_flexible_date("not-a-date")

    def test_parse_empty_string(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_flexible_date("")

    def test_parse_invalid_natural_language(self):
        """Test that invalid natural language raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_flexible_date("yesterday")  # Not supported in spec

    def test_parse_returns_datetime_object(self):
        """Test that parser returns datetime object."""
        result = parse_flexible_date("2026-02-15")
        assert isinstance(result, datetime)

    def test_parse_date_with_time_component(self):
        """Test parsing date with time component."""
        result = parse_flexible_date("2026-02-15 14:30:00")
        assert result.year == 2026
        assert result.month == 2
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30


class TestTimeParsingFormats:
    """Test time parsing in various formats (T012 - User Story 1)."""

    def test_parse_24_hour_format(self):
        """Test parsing 24-hour time format (HH:MM)."""
        result = parse_time("14:30")
        assert result == time(14, 30)

    def test_parse_24_hour_format_with_seconds(self):
        """Test parsing 24-hour time format with seconds (HH:MM:SS)."""
        result = parse_time("14:30:45")
        assert result == time(14, 30, 45)

    def test_parse_12_hour_format_pm(self):
        """Test parsing 12-hour time format with PM."""
        result = parse_time("2:30 PM")
        assert result == time(14, 30)

    def test_parse_12_hour_format_am(self):
        """Test parsing 12-hour time format with AM."""
        result = parse_time("9:15 AM")
        assert result == time(9, 15)

    def test_parse_12_hour_format_no_space(self):
        """Test parsing 12-hour time format without space (2:30PM)."""
        result = parse_time("2:30PM")
        assert result == time(14, 30)

    def test_parse_12_hour_format_lowercase(self):
        """Test parsing 12-hour time format with lowercase am/pm."""
        result = parse_time("2:30 pm")
        assert result == time(14, 30)

    def test_parse_midnight_12_hour(self):
        """Test parsing midnight in 12-hour format."""
        result = parse_time("12:00 AM")
        assert result == time(0, 0)

    def test_parse_noon_12_hour(self):
        """Test parsing noon in 12-hour format."""
        result = parse_time("12:00 PM")
        assert result == time(12, 0)

    def test_parse_time_invalid_format(self):
        """Test that invalid time format raises ValueError."""
        with pytest.raises(ValueError):
            parse_time("25:00")

    def test_parse_time_invalid_string(self):
        """Test that invalid time string raises ValueError."""
        with pytest.raises(ValueError):
            parse_time("not a time")

    def test_parse_natural_2pm(self):
        """Test parsing natural language '2pm'."""
        result = parse_time("2pm")
        assert result == time(14, 0)

    def test_parse_natural_9am(self):
        """Test parsing natural language '9am'."""
        result = parse_time("9am")
        assert result == time(9, 0)

    def test_parse_time_with_leading_zeros(self):
        """Test parsing time with leading zeros."""
        result = parse_time("09:05")
        assert result == time(9, 5)

    def test_parse_time_boundary_values(self):
        """Test parsing boundary time values."""
        assert parse_time("00:00") == time(0, 0)
        assert parse_time("23:59") == time(23, 59)

    def test_parse_time_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        result = parse_time("  14:30  ")
        assert result == time(14, 30)


class TestDateTimeParsing:
    """Test combined date and time parsing (T012 - User Story 1)."""

    def test_parse_date_with_24_hour_time(self):
        """Test parsing date with 24-hour time."""
        result = parse_date_time("2026-02-15 14:30")
        assert result.date() == datetime(2026, 2, 15).date()
        assert result.time() == time(14, 30)

    def test_parse_date_with_12_hour_time(self):
        """Test parsing date with 12-hour time."""
        result = parse_date_time("2026-02-15 2:30 PM")
        assert result.date() == datetime(2026, 2, 15).date()
        assert result.time() == time(14, 30)

    def test_parse_date_without_time(self):
        """Test parsing date without time returns midnight."""
        result = parse_date_time("2026-02-15")
        assert result.date() == datetime(2026, 2, 15).date()
        assert result.time() == time(0, 0)

    def test_parse_natural_date_with_time(self):
        """Test parsing natural language date with time."""
        result = parse_date_time("Feb 15, 2026 at 2:30 PM")
        assert result.date() == datetime(2026, 2, 15).date()
        assert result.time() == time(14, 30)

    def test_parse_iso_format(self):
        """Test parsing ISO format datetime."""
        result = parse_date_time("2026-02-15T14:30:00")
        assert result.date() == datetime(2026, 2, 15).date()
        assert result.time() == time(14, 30)

