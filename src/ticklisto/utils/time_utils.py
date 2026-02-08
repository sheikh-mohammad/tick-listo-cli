"""Time utilities for formatting and validation (T019 - User Story 1)."""

from datetime import time, datetime
from typing import Optional


def format_time_12hour(time_obj: time) -> str:
    """
    Format time object as 12-hour string with AM/PM.

    Args:
        time_obj: time object to format

    Returns:
        Formatted string (e.g., "2:30 PM", "9:00 AM")
    """
    if time_obj is None:
        return ""

    hour = time_obj.hour
    minute = time_obj.minute
    period = "AM" if hour < 12 else "PM"

    # Convert to 12-hour format
    display_hour = hour % 12
    if display_hour == 0:
        display_hour = 12

    return f"{display_hour}:{minute:02d} {period}"


def format_time_24hour(time_obj: time) -> str:
    """
    Format time object as 24-hour string.

    Args:
        time_obj: time object to format

    Returns:
        Formatted string (e.g., "14:30", "09:00")
    """
    if time_obj is None:
        return ""

    return f"{time_obj.hour:02d}:{time_obj.minute:02d}"


def validate_time(time_obj: Optional[time]) -> bool:
    """
    Validate that time object is valid.

    Args:
        time_obj: time object to validate

    Returns:
        True if valid, False otherwise
    """
    if time_obj is None:
        return True

    if not isinstance(time_obj, time):
        return False

    # Check hour and minute ranges
    if not (0 <= time_obj.hour <= 23):
        return False

    if not (0 <= time_obj.minute <= 59):
        return False

    return True


def time_to_minutes(time_obj: time) -> int:
    """
    Convert time object to minutes since midnight.

    Args:
        time_obj: time object to convert

    Returns:
        Minutes since midnight (0-1439)
    """
    if time_obj is None:
        return 0

    return time_obj.hour * 60 + time_obj.minute


def minutes_to_time(minutes: int) -> time:
    """
    Convert minutes since midnight to time object.

    Args:
        minutes: Minutes since midnight (0-1439)

    Returns:
        time object

    Raises:
        ValueError: If minutes is out of range
    """
    if not (0 <= minutes <= 1439):
        raise ValueError(f"Minutes must be between 0 and 1439, got {minutes}")

    hour = minutes // 60
    minute = minutes % 60

    return time(hour, minute)


def compare_times(time1: Optional[time], time2: Optional[time]) -> int:
    """
    Compare two time objects.

    Args:
        time1: First time object
        time2: Second time object

    Returns:
        -1 if time1 < time2, 0 if equal, 1 if time1 > time2
        None times are considered less than any time
    """
    if time1 is None and time2 is None:
        return 0
    if time1 is None:
        return -1
    if time2 is None:
        return 1

    minutes1 = time_to_minutes(time1)
    minutes2 = time_to_minutes(time2)

    if minutes1 < minutes2:
        return -1
    elif minutes1 > minutes2:
        return 1
    else:
        return 0


def format_datetime_with_time(dt: datetime, time_obj: Optional[time] = None) -> str:
    """
    Format datetime with optional time component.

    Args:
        dt: datetime object
        time_obj: Optional time object to use instead of dt's time

    Returns:
        Formatted string (e.g., "Feb 15, 2026 at 2:30 PM" or "Feb 15, 2026")
    """
    if dt is None:
        return ""

    date_str = dt.strftime("%b %d, %Y")

    if time_obj is not None:
        time_str = format_time_12hour(time_obj)
        return f"{date_str} at {time_str}"
    elif dt.hour != 0 or dt.minute != 0:
        # datetime has non-midnight time
        time_str = format_time_12hour(dt.time())
        return f"{date_str} at {time_str}"
    else:
        return date_str


def is_time_in_past(dt: datetime, time_obj: Optional[time] = None) -> bool:
    """
    Check if datetime with optional time is in the past.

    Args:
        dt: datetime object
        time_obj: Optional time object

    Returns:
        True if in the past, False otherwise
    """
    if dt is None:
        return False

    now = datetime.now()

    # If time is specified, combine date and time
    if time_obj is not None:
        check_dt = datetime.combine(dt.date(), time_obj)
    else:
        check_dt = dt

    return check_dt < now


def time_until(dt: datetime, time_obj: Optional[time] = None) -> str:
    """
    Get human-readable string for time until datetime.

    Args:
        dt: datetime object
        time_obj: Optional time object

    Returns:
        Human-readable string (e.g., "in 2 hours", "in 3 days", "overdue")
    """
    if dt is None:
        return ""

    now = datetime.now()

    # If time is specified, combine date and time
    if time_obj is not None:
        target_dt = datetime.combine(dt.date(), time_obj)
    else:
        target_dt = dt

    if target_dt < now:
        return "overdue"

    delta = target_dt - now

    # Calculate time components
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    if days > 0:
        if days == 1:
            return "in 1 day"
        else:
            return f"in {days} days"
    elif hours > 0:
        if hours == 1:
            return "in 1 hour"
        else:
            return f"in {hours} hours"
    elif minutes > 0:
        if minutes == 1:
            return "in 1 minute"
        else:
            return f"in {minutes} minutes"
    else:
        return "now"
