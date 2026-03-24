"""
Date parser utility with flexible format support.
Supports standard formats (MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD) and natural language.
"""
from datetime import datetime, timedelta
from dateutil import parser


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
