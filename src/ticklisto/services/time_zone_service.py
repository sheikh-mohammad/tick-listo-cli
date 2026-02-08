import pytz
from datetime import datetime, time
from typing import Optional


class TimeZoneService:
    """
    Service for handling time zone conversions between UTC and user time zones.

    All timestamps are stored in UTC internally and converted to user's time zone
    for display and input parsing.
    """

    def __init__(self, user_timezone: str = "America/New_York"):
        """
        Initialize TimeZoneService.

        Args:
            user_timezone: User's time zone (must be valid pytz timezone)

        Raises:
            ValueError: If timezone is invalid
        """
        if user_timezone not in pytz.all_timezones:
            raise ValueError(f"Invalid time zone: {user_timezone}")
        self.user_timezone = pytz.timezone(user_timezone)
        self.utc = pytz.UTC

    def set_user_timezone(self, timezone: str):
        """
        Update user's time zone.

        Args:
            timezone: New time zone name

        Raises:
            ValueError: If timezone is invalid
        """
        if timezone not in pytz.all_timezones:
            raise ValueError(f"Invalid time zone: {timezone}")
        self.user_timezone = pytz.timezone(timezone)

    def to_utc(self, local_dt: datetime) -> datetime:
        """
        Convert local datetime to UTC.

        Args:
            local_dt: Datetime in user's time zone (can be naive or aware)

        Returns:
            Datetime in UTC
        """
        # If naive, localize to user's timezone first
        if local_dt.tzinfo is None:
            local_dt = self.user_timezone.localize(local_dt)

        # Convert to UTC
        return local_dt.astimezone(self.utc)

    def to_local(self, utc_dt: datetime) -> datetime:
        """
        Convert UTC datetime to user's local time zone.

        Args:
            utc_dt: Datetime in UTC (can be naive or aware)

        Returns:
            Datetime in user's time zone
        """
        # If naive, assume it's UTC
        if utc_dt.tzinfo is None:
            utc_dt = self.utc.localize(utc_dt)

        # Convert to user's timezone
        return utc_dt.astimezone(self.user_timezone)

    def now_utc(self) -> datetime:
        """
        Get current time in UTC.

        Returns:
            Current datetime in UTC
        """
        return datetime.now(self.utc)

    def now_local(self) -> datetime:
        """
        Get current time in user's time zone.

        Returns:
            Current datetime in user's time zone
        """
        return datetime.now(self.user_timezone)

    def combine_date_time_to_utc(self, date: datetime, time_obj: Optional[time]) -> datetime:
        """
        Combine date and time in user's timezone and convert to UTC.

        Args:
            date: Date component (can include time, but time will be replaced)
            time_obj: Time component (optional)

        Returns:
            Combined datetime in UTC
        """
        if time_obj is None:
            # Use midnight if no time specified
            time_obj = time(0, 0, 0)

        # Create naive datetime with date and time
        naive_dt = datetime.combine(date.date(), time_obj)

        # Localize to user's timezone and convert to UTC
        return self.to_utc(naive_dt)

    def format_local_datetime(self, utc_dt: datetime, include_time: bool = True) -> str:
        """
        Format UTC datetime as string in user's local time zone.

        Args:
            utc_dt: Datetime in UTC
            include_time: Whether to include time in output

        Returns:
            Formatted string (e.g., "Feb 15, 2026 at 2:30 PM" or "Feb 15, 2026")
        """
        local_dt = self.to_local(utc_dt)

        if include_time:
            return local_dt.strftime("%b %d, %Y at %I:%M %p")
        else:
            return local_dt.strftime("%b %d, %Y")

    def parse_time_string(self, time_str: str) -> time:
        """
        Parse time string in various formats.

        Supports:
        - 24-hour: "14:30", "14:30:00"
        - 12-hour: "2:30 PM", "2:30PM", "2:30 pm"

        Args:
            time_str: Time string to parse

        Returns:
            time object

        Raises:
            ValueError: If time string cannot be parsed
        """
        time_str = time_str.strip()

        # Try 24-hour format first
        for fmt in ["%H:%M", "%H:%M:%S"]:
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.time()
            except ValueError:
                continue

        # Try 12-hour format with AM/PM
        for fmt in ["%I:%M %p", "%I:%M%p"]:
            try:
                dt = datetime.strptime(time_str.upper(), fmt)
                return dt.time()
            except ValueError:
                continue

        raise ValueError(f"Unable to parse time string: {time_str}")

    def get_timezone_name(self) -> str:
        """
        Get the name of the user's time zone.

        Returns:
            Time zone name (e.g., "America/New_York")
        """
        return str(self.user_timezone)
