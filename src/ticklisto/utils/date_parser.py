"""
Date parser utility with flexible format support.
Supports standard formats (MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD) and natural language.
Extended with time parsing support for 24-hour, 12-hour AM/PM, and natural language times.
"""
from datetime import datetime, timedelta, time
from dateutil import parser
import re


def parse_flexible_date(date_input: str) -> datetime:
    """
    Parse flexible date input including natural language.

    Args:
        date_input: Date string in various formats

    Returns:
        datetime object

    Raises:
        ValueError: When date format is invalid

    Supported formats:
        - Standard: MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD
        - Natural language: "today", "tomorrow", "next week", "in X days"
    """
    if not date_input or not date_input.strip():
        raise ValueError("Invalid date format: Date input cannot be empty")

    date_input = date_input.lower().strip()

    # Handle natural language
    if date_input == "today":
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    elif date_input == "tomorrow":
        return datetime.now() + timedelta(days=1)

    elif date_input == "next week":
        return datetime.now() + timedelta(weeks=1)

    elif date_input.startswith("in ") and "day" in date_input:
        # Handle "in X days" or "in X day"
        try:
            parts = date_input.split()
            if len(parts) >= 2:
                days = int(parts[1])
                return datetime.now() + timedelta(days=days)
        except (ValueError, IndexError):
            pass

    # Fall back to dateutil parser for standard formats
    try:
        return parser.parse(date_input)
    except (parser.ParserError, ValueError) as e:
        raise ValueError(
            f"Invalid date format: {date_input}. "
            f"Use MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD, or natural language "
            f"(today, tomorrow, next week, in X days)"
        )


def parse_time(time_input: str) -> time:
    """
    Parse time string in various formats.

    Args:
        time_input: Time string in various formats

    Returns:
        time object

    Raises:
        ValueError: When time format is invalid

    Supported formats:
        - 24-hour: "14:30", "14:30:00"
        - 12-hour: "2:30 PM", "2:30PM", "2:30 pm"
        - Natural language: "2pm", "9am"
    """
    if not time_input or not time_input.strip():
        raise ValueError("Invalid time format: Time input cannot be empty")

    time_input = time_input.strip()

    # Try 24-hour format first (HH:MM or HH:MM:SS)
    for fmt in ["%H:%M", "%H:%M:%S"]:
        try:
            dt = datetime.strptime(time_input, fmt)
            return dt.time()
        except ValueError:
            continue

    # Try 12-hour format with AM/PM (with or without space)
    for fmt in ["%I:%M %p", "%I:%M%p"]:
        try:
            dt = datetime.strptime(time_input.upper(), fmt)
            return dt.time()
        except ValueError:
            continue

    # Try natural language format (e.g., "2pm", "9am")
    # Match patterns like "2pm", "2 pm", "14pm" (though 14pm is invalid, we'll catch it)
    natural_pattern = r'^(\d{1,2})\s*(am|pm)$'
    match = re.match(natural_pattern, time_input.lower())
    if match:
        hour = int(match.group(1))
        period = match.group(2)

        # Validate hour range
        if period == 'am':
            if hour == 12:
                hour = 0  # 12 AM is midnight
            elif hour < 1 or hour > 12:
                raise ValueError(f"Invalid hour for AM: {hour}")
        else:  # pm
            if hour == 12:
                hour = 12  # 12 PM is noon
            elif hour < 1 or hour > 12:
                raise ValueError(f"Invalid hour for PM: {hour}")
            else:
                hour += 12  # Convert to 24-hour format

        return time(hour, 0)

    raise ValueError(
        f"Unable to parse time string: {time_input}. "
        f"Use HH:MM, HH:MM:SS, H:MM AM/PM, or natural language (2pm, 9am)"
    )


def parse_date_time(datetime_input: str) -> datetime:
    """
    Parse combined date and time string.

    Args:
        datetime_input: Date and time string in various formats

    Returns:
        datetime object

    Raises:
        ValueError: When datetime format is invalid

    Supported formats:
        - ISO format: "2026-02-15T14:30:00"
        - Space-separated: "2026-02-15 14:30", "2026-02-15 2:30 PM"
        - Natural language: "Feb 15, 2026 at 2:30 PM"
        - Date only: "2026-02-15" (returns midnight)
    """
    if not datetime_input or not datetime_input.strip():
        raise ValueError("Invalid datetime format: Input cannot be empty")

    datetime_input = datetime_input.strip()

    # Try dateutil parser first (handles most formats)
    try:
        return parser.parse(datetime_input)
    except (parser.ParserError, ValueError) as e:
        raise ValueError(
            f"Unable to parse datetime string: {datetime_input}. "
            f"Use ISO format (YYYY-MM-DDTHH:MM:SS), space-separated (YYYY-MM-DD HH:MM), "
            f"or natural language (Feb 15, 2026 at 2:30 PM)"
        )
