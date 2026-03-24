"""
Unit tests for date parser utility.
Following TDD approach - these tests are written FIRST and should FAIL initially.
"""
import pytest
from datetime import datetime, timedelta
from tick_listo_cli.utils.date_parser import parse_flexible_date


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
