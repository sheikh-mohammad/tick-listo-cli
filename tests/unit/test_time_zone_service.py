"""Unit tests for TimeZoneService (T013 - User Story 1)."""

import pytest
import pytz
from datetime import datetime, time
from ticklisto.services.time_zone_service import TimeZoneService


class TestTimeZoneServiceInitialization:
    """Test TimeZoneService initialization."""

    def test_initialize_with_valid_timezone(self):
        """Test initializing with valid timezone."""
        service = TimeZoneService("America/New_York")
        assert service.get_timezone_name() == "America/New_York"

    def test_initialize_with_default_timezone(self):
        """Test initializing with default timezone."""
        service = TimeZoneService()
        assert service.get_timezone_name() == "America/New_York"

    def test_initialize_with_invalid_timezone(self):
        """Test that invalid timezone raises ValueError."""
        with pytest.raises(ValueError, match="Invalid time zone"):
            TimeZoneService("Invalid/Timezone")


class TestTimeZoneConversions:
    """Test time zone conversion utilities."""

    def test_to_utc_from_naive_datetime(self):
        """Test converting naive datetime to UTC."""
        service = TimeZoneService("America/New_York")
        local_dt = datetime(2026, 2, 15, 14, 30)  # Naive datetime
        utc_dt = service.to_utc(local_dt)

        # EST is UTC-5, so 14:30 EST = 19:30 UTC
        assert utc_dt.hour == 19
        assert utc_dt.minute == 30
        assert utc_dt.tzinfo == pytz.UTC

    def test_to_utc_from_aware_datetime(self):
        """Test converting aware datetime to UTC."""
        service = TimeZoneService("America/New_York")
        ny_tz = pytz.timezone("America/New_York")
        local_dt = ny_tz.localize(datetime(2026, 2, 15, 14, 30))
        utc_dt = service.to_utc(local_dt)

        assert utc_dt.hour == 19
        assert utc_dt.tzinfo == pytz.UTC

    def test_to_local_from_utc(self):
        """Test converting UTC datetime to local timezone."""
        service = TimeZoneService("America/New_York")
        utc_dt = pytz.UTC.localize(datetime(2026, 2, 15, 19, 30))
        local_dt = service.to_local(utc_dt)

        # UTC 19:30 = EST 14:30
        assert local_dt.hour == 14
        assert local_dt.minute == 30

    def test_to_local_from_naive_utc(self):
        """Test converting naive UTC datetime to local timezone."""
        service = TimeZoneService("America/New_York")
        utc_dt = datetime(2026, 2, 15, 19, 30)  # Assumed to be UTC
        local_dt = service.to_local(utc_dt)

        assert local_dt.hour == 14
        assert local_dt.minute == 30

    def test_round_trip_conversion(self):
        """Test that converting to UTC and back preserves time."""
        service = TimeZoneService("America/New_York")
        original = datetime(2026, 2, 15, 14, 30)
        utc = service.to_utc(original)
        back_to_local = service.to_local(utc)

        assert back_to_local.hour == original.hour
        assert back_to_local.minute == original.minute


class TestTimeZoneServiceHelpers:
    """Test helper methods in TimeZoneService."""

    def test_now_utc(self):
        """Test getting current time in UTC."""
        service = TimeZoneService("America/New_York")
        now = service.now_utc()

        assert now.tzinfo == pytz.UTC
        assert isinstance(now, datetime)

    def test_now_local(self):
        """Test getting current time in local timezone."""
        service = TimeZoneService("America/New_York")
        now = service.now_local()

        assert now.tzinfo is not None
        assert isinstance(now, datetime)

    def test_combine_date_time_to_utc(self):
        """Test combining date and time to UTC."""
        service = TimeZoneService("America/New_York")
        date = datetime(2026, 2, 15)
        time_obj = time(14, 30)

        result = service.combine_date_time_to_utc(date, time_obj)

        # 14:30 EST = 19:30 UTC
        assert result.hour == 19
        assert result.minute == 30
        assert result.tzinfo == pytz.UTC

    def test_combine_date_time_to_utc_no_time(self):
        """Test combining date without time defaults to midnight."""
        service = TimeZoneService("America/New_York")
        date = datetime(2026, 2, 15)

        result = service.combine_date_time_to_utc(date, None)

        # Midnight EST = 05:00 UTC
        assert result.hour == 5
        assert result.minute == 0

    def test_format_local_datetime_with_time(self):
        """Test formatting UTC datetime as local string with time."""
        service = TimeZoneService("America/New_York")
        utc_dt = pytz.UTC.localize(datetime(2026, 2, 15, 19, 30))

        result = service.format_local_datetime(utc_dt, include_time=True)

        assert "Feb 15, 2026" in result
        assert "2:30 PM" in result

    def test_format_local_datetime_without_time(self):
        """Test formatting UTC datetime as local string without time."""
        service = TimeZoneService("America/New_York")
        utc_dt = pytz.UTC.localize(datetime(2026, 2, 15, 19, 30))

        result = service.format_local_datetime(utc_dt, include_time=False)

        assert "Feb 15, 2026" in result
        assert "PM" not in result


class TestTimeStringParsing:
    """Test time string parsing."""

    def test_parse_time_24_hour(self):
        """Test parsing 24-hour time string."""
        service = TimeZoneService("America/New_York")
        result = service.parse_time_string("14:30")

        assert result == time(14, 30)

    def test_parse_time_12_hour_pm(self):
        """Test parsing 12-hour PM time string."""
        service = TimeZoneService("America/New_York")
        result = service.parse_time_string("2:30 PM")

        assert result == time(14, 30)

    def test_parse_time_12_hour_am(self):
        """Test parsing 12-hour AM time string."""
        service = TimeZoneService("America/New_York")
        result = service.parse_time_string("9:15 AM")

        assert result == time(9, 15)

    def test_parse_time_invalid(self):
        """Test that invalid time string raises ValueError."""
        service = TimeZoneService("America/New_York")

        with pytest.raises(ValueError):
            service.parse_time_string("invalid")


class TestSetUserTimezone:
    """Test updating user timezone."""

    def test_set_valid_timezone(self):
        """Test setting a valid timezone."""
        service = TimeZoneService("America/New_York")
        service.set_user_timezone("Europe/London")

        assert service.get_timezone_name() == "Europe/London"

    def test_set_invalid_timezone(self):
        """Test that setting invalid timezone raises ValueError."""
        service = TimeZoneService("America/New_York")

        with pytest.raises(ValueError, match="Invalid time zone"):
            service.set_user_timezone("Invalid/Timezone")


class TestDSTHandling:
    """Test Daylight Saving Time transitions."""

    def test_dst_spring_forward(self):
        """Test conversion during spring DST transition."""
        service = TimeZoneService("America/New_York")
        # March 9, 2026 - DST begins (2 AM becomes 3 AM)
        local_dt = datetime(2026, 3, 9, 14, 30)
        utc_dt = service.to_utc(local_dt)

        # EDT is UTC-4, so 14:30 EDT = 18:30 UTC
        assert utc_dt.hour == 18
        assert utc_dt.minute == 30

    def test_dst_fall_back(self):
        """Test conversion during fall DST transition."""
        service = TimeZoneService("America/New_York")
        # November 2, 2026 - DST ends (2 AM becomes 1 AM)
        local_dt = datetime(2026, 11, 2, 14, 30)
        utc_dt = service.to_utc(local_dt)

        # EST is UTC-5, so 14:30 EST = 19:30 UTC
        assert utc_dt.hour == 19
        assert utc_dt.minute == 30
