"""
ValidationService for task field validation.
Provides validation for priority, categories, and date inputs.
"""
from tick_listo_cli.models.task import Priority
from tick_listo_cli.utils.date_parser import parse_flexible_date
from datetime import datetime


# Predefined category suggestions
DEFAULT_CATEGORIES = ["work", "home", "personal"]


def validate_priority(priority: str) -> Priority:
    """
    Validate and convert priority string to enum.

    Args:
        priority: Priority string (high/medium/low)

    Returns:
        Priority enum value

    Raises:
        ValueError: If priority is invalid
    """
    if not priority or not priority.strip():
        raise ValueError("Invalid priority: ''. Must be one of: high, medium, low")

    try:
        return Priority(priority.strip().lower())
    except ValueError:
        valid_values = ", ".join([p.value for p in Priority])
        raise ValueError(
            f"Invalid priority: '{priority}'. "
            f"Must be one of: {valid_values}"
        )


def validate_categories(categories: list[str]) -> list[str]:
    """
    Validate category list (accepts any string, provides suggestions).

    Args:
        categories: List of category strings

    Returns:
        Cleaned and deduplicated category list

    Raises:
        ValueError: If any category exceeds 50 characters
    """
    if not categories:
        return []

    # Clean and deduplicate
    cleaned = []
    seen = set()

    for cat in categories:
        if not cat or not cat.strip():
            continue

        normalized = cat.strip().lower()

        # Validate length
        if len(normalized) > 50:
            raise ValueError(f"Category '{normalized}' exceeds 50 characters")

        # Add if not duplicate
        if normalized not in seen:
            cleaned.append(normalized)
            seen.add(normalized)

    return cleaned


def validate_date_input(date_input: str) -> datetime:
    """
    Validate and parse date input.

    Args:
        date_input: Date string in various formats

    Returns:
        datetime object

    Raises:
        ValueError: If date format is invalid
    """
    return parse_flexible_date(date_input)


def get_category_suggestions(partial: str = "") -> list[str]:
    """
    Get category suggestions for autocomplete.

    Args:
        partial: Partial category string

    Returns:
        List of matching category suggestions
    """
    if not partial:
        return DEFAULT_CATEGORIES

    partial_lower = partial.lower()
    return [
        cat for cat in DEFAULT_CATEGORIES
        if cat.startswith(partial_lower)
    ]


def validate_required_fields(priority: str = None, categories: list[str] = None) -> bool:
    """
    Validate that required fields (priority and categories) are provided.

    Phase 10 - User Story 6: Make priority and categories mandatory.

    Args:
        priority: Priority string (required)
        categories: List of category strings (required, at least one)

    Returns:
        True if all required fields are valid

    Raises:
        ValueError: If any required field is missing or invalid
    """
    # Check priority is provided
    if priority is None or (isinstance(priority, str) and not priority.strip()):
        raise ValueError("Priority is required. Must be one of: high, medium, low")

    # Check categories are provided
    if categories is None or (isinstance(categories, list) and len(categories) == 0):
        raise ValueError("At least one category is required. Suggestions: work, home, personal")

    return True
