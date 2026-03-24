"""
Unit tests for ValidationService.
Following TDD approach - these tests are written FIRST and should FAIL initially.
"""
import pytest
from datetime import datetime
from tick_listo_cli.services.validation_service import (
    validate_priority,
    validate_categories,
    validate_date_input,
    get_category_suggestions
)
from tick_listo_cli.models.task import Priority


class TestValidatePriority:
    """Test validate_priority function (T011)."""

    def test_validate_priority_high(self):
        """Test validating 'high' priority."""
        result = validate_priority("high")
        assert result == Priority.HIGH

    def test_validate_priority_medium(self):
        """Test validating 'medium' priority."""
        result = validate_priority("medium")
        assert result == Priority.MEDIUM

    def test_validate_priority_low(self):
        """Test validating 'low' priority."""
        result = validate_priority("low")
        assert result == Priority.LOW

    def test_validate_priority_case_insensitive(self):
        """Test that priority validation is case-insensitive."""
        assert validate_priority("HIGH") == Priority.HIGH
        assert validate_priority("Medium") == Priority.MEDIUM
        assert validate_priority("LoW") == Priority.LOW

    def test_validate_priority_invalid(self):
        """Test that invalid priority raises ValueError."""
        with pytest.raises(ValueError, match="Invalid priority"):
            validate_priority("urgent")

    def test_validate_priority_empty_string(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid priority"):
            validate_priority("")

    def test_validate_priority_with_whitespace(self):
        """Test that priority with whitespace is handled."""
        result = validate_priority("  high  ")
        assert result == Priority.HIGH


class TestValidateCategories:
    """Test validate_categories function (T012)."""

    def test_validate_empty_categories(self):
        """Test validating empty category list."""
        result = validate_categories([])
        assert result == []

    def test_validate_single_category(self):
        """Test validating single category."""
        result = validate_categories(["work"])
        assert result == ["work"]

    def test_validate_multiple_categories(self):
        """Test validating multiple categories."""
        result = validate_categories(["work", "home", "personal"])
        assert len(result) == 3
        assert "work" in result
        assert "home" in result
        assert "personal" in result

    def test_validate_categories_lowercase_normalization(self):
        """Test that categories are normalized to lowercase."""
        result = validate_categories(["Work", "HOME", "Personal"])
        assert "work" in result
        assert "home" in result
        assert "personal" in result
        assert "Work" not in result

    def test_validate_categories_whitespace_trimming(self):
        """Test that whitespace is trimmed from categories."""
        result = validate_categories(["  work  ", "home"])
        assert "work" in result
        assert "  work  " not in result

    def test_validate_categories_deduplication(self):
        """Test that duplicate categories are removed."""
        result = validate_categories(["work", "work", "home", "Work"])
        assert len(result) == 2
        assert "work" in result
        assert "home" in result

    def test_validate_categories_empty_strings_removed(self):
        """Test that empty strings are filtered out."""
        result = validate_categories(["work", "", "  ", "home"])
        assert len(result) == 2
        assert "work" in result
        assert "home" in result

    def test_validate_categories_max_length(self):
        """Test that categories exceeding 50 chars raise error."""
        long_category = "a" * 51
        with pytest.raises(ValueError, match="exceeds 50 characters"):
            validate_categories([long_category])

    def test_validate_categories_valid_max_length(self):
        """Test that categories at 50 chars are valid."""
        valid_category = "a" * 50
        result = validate_categories([valid_category])
        assert valid_category in result


class TestValidateDateInput:
    """Test validate_date_input function (T013)."""

    def test_validate_date_standard_format_mmddyyyy(self):
        """Test parsing MM/DD/YYYY format."""
        result = validate_date_input("02/15/2026")
        assert result.year == 2026
        assert result.month == 2
        assert result.day == 15

    def test_validate_date_standard_format_ddmmyyyy(self):
        """Test parsing DD-MM-YYYY format."""
        result = validate_date_input("15-02-2026")
        assert result.year == 2026
        assert result.month == 2
        assert result.day == 15

    def test_validate_date_standard_format_yyyymmdd(self):
        """Test parsing YYYY-MM-DD format."""
        result = validate_date_input("2026-02-15")
        assert result.year == 2026
        assert result.month == 2
        assert result.day == 15

    def test_validate_date_natural_language_today(self):
        """Test parsing 'today'."""
        result = validate_date_input("today")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        assert result.date() == today.date()

    def test_validate_date_natural_language_tomorrow(self):
        """Test parsing 'tomorrow'."""
        result = validate_date_input("tomorrow")
        from datetime import timedelta
        tomorrow = datetime.now() + timedelta(days=1)
        assert result.date() == tomorrow.date()

    def test_validate_date_natural_language_next_week(self):
        """Test parsing 'next week'."""
        result = validate_date_input("next week")
        from datetime import timedelta
        next_week = datetime.now() + timedelta(weeks=1)
        assert result.date() == next_week.date()

    def test_validate_date_natural_language_in_days(self):
        """Test parsing 'in X days'."""
        result = validate_date_input("in 5 days")
        from datetime import timedelta
        expected = datetime.now() + timedelta(days=5)
        assert result.date() == expected.date()

    def test_validate_date_case_insensitive(self):
        """Test that natural language parsing is case-insensitive."""
        result = validate_date_input("TODAY")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        assert result.date() == today.date()

    def test_validate_date_invalid_format(self):
        """Test that invalid date format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date_input("not-a-date")

    def test_validate_date_empty_string(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date_input("")


class TestGetCategorySuggestions:
    """Test get_category_suggestions function."""

    def test_get_suggestions_empty_partial(self):
        """Test getting suggestions with empty partial string."""
        result = get_category_suggestions("")
        assert "work" in result
        assert "home" in result
        assert "personal" in result

    def test_get_suggestions_matching_partial(self):
        """Test getting suggestions with matching partial."""
        result = get_category_suggestions("wo")
        assert "work" in result

    def test_get_suggestions_no_match(self):
        """Test getting suggestions with no match."""
        result = get_category_suggestions("xyz")
        assert len(result) == 0

    def test_get_suggestions_case_insensitive(self):
        """Test that suggestions are case-insensitive."""
        result = get_category_suggestions("WO")
        assert "work" in result


class TestRequiredFieldValidation:
    """Unit tests for required field validation (Phase 10 - User Story 6)."""

    def test_validate_required_fields_with_all_fields(self):
        """Test validation passes when all required fields are provided."""
        from tick_listo_cli.services.validation_service import validate_required_fields
        
        result = validate_required_fields(
            priority="high",
            categories=["work"]
        )
        
        assert result is True

    def test_validate_required_fields_missing_priority(self):
        """Test validation fails when priority is missing."""
        from tick_listo_cli.services.validation_service import validate_required_fields
        
        with pytest.raises(ValueError, match="Priority is required"):
            validate_required_fields(
                priority=None,
                categories=["work"]
            )

    def test_validate_required_fields_missing_categories(self):
        """Test validation fails when categories are missing."""
        from tick_listo_cli.services.validation_service import validate_required_fields
        
        with pytest.raises(ValueError, match="At least one category is required"):
            validate_required_fields(
                priority="high",
                categories=None
            )

    def test_validate_required_fields_empty_categories(self):
        """Test validation fails when categories list is empty."""
        from tick_listo_cli.services.validation_service import validate_required_fields
        
        with pytest.raises(ValueError, match="At least one category is required"):
            validate_required_fields(
                priority="high",
                categories=[]
            )

    def test_validate_required_fields_both_missing(self):
        """Test validation fails when both required fields are missing."""
        from tick_listo_cli.services.validation_service import validate_required_fields
        
        with pytest.raises(ValueError, match="Priority is required"):
            validate_required_fields(
                priority=None,
                categories=None
            )
