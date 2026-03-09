# Validation Service Contract

**Service**: ValidationService
**Purpose**: Provide input validation for task fields
**Module**: `src/ticklisto/services/validation_service.py`

## Interface

### validate_priority

Validate and normalize priority input.

#### Signature

```python
def validate_priority(priority: str) -> Priority:
    """
    Validate priority string and convert to Priority enum.

    Args:
        priority: Priority string to validate

    Returns:
        Priority enum value

    Raises:
        ValueError: If priority is not valid
    """
```

#### Input

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| priority | str | Yes | Non-None string | Priority value to validate |

#### Output

| Type | Description |
|------|-------------|
| Priority | Validated Priority enum value |

**Behavior**:
- Accepts case-insensitive input ("High", "HIGH", "high" all valid)
- Converts to lowercase Priority enum value
- Strict validation: only accepts "high", "medium", "low"

#### Examples

```python
# Example 1: Valid priority (lowercase)
result = validate_priority("high")
# Returns: Priority.HIGH

# Example 2: Valid priority (mixed case)
result = validate_priority("Medium")
# Returns: Priority.MEDIUM

# Example 3: Valid priority (uppercase)
result = validate_priority("LOW")
# Returns: Priority.LOW

# Example 4: Invalid priority
try:
    result = validate_priority("urgent")
except ValueError as e:
    print(e)
    # Prints: "Invalid priority: 'urgent'. Must be one of: high, medium, low"
```

#### Error Handling

| Error | Condition | Response |
|-------|-----------|----------|
| ValueError | Priority not in [high, medium, low] | Raise ValueError: "Invalid priority: '{value}'. Must be one of: high, medium, low" |
| TypeError | Priority is not a string | Raise TypeError: "priority must be a string" |

---

### validate_categories

Validate and normalize category list.

#### Signature

```python
def validate_categories(categories: list[str]) -> list[str]:
    """
    Validate and normalize category list.

    Args:
        categories: List of category strings

    Returns:
        Normalized list of categories (lowercase, deduplicated, trimmed)

    Raises:
        ValueError: If any category exceeds length limit
    """
```

#### Input

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| categories | list[str] | Yes | List of strings | Categories to validate |

#### Output

| Type | Description |
|------|-------------|
| list[str] | Normalized category list |

**Behavior**:
- Accepts any string values (flexible validation)
- Normalizes: lowercase, trim whitespace, deduplicate
- Validates: each category ≤50 characters
- Empty list is valid
- Empty strings are filtered out

#### Examples

```python
# Example 1: Valid categories
result = validate_categories(["work", "home"])
# Returns: ["work", "home"]

# Example 2: Normalization (case, whitespace)
result = validate_categories(["Work", "  HOME  ", "personal"])
# Returns: ["work", "home", "personal"]

# Example 3: Deduplication
result = validate_categories(["work", "Work", "WORK"])
# Returns: ["work"]

# Example 4: Empty list
result = validate_categories([])
# Returns: []

# Example 5: Filter empty strings
result = validate_categories(["work", "", "  ", "home"])
# Returns: ["work", "home"]

# Example 6: Custom categories (accepted)
result = validate_categories(["urgent", "client-meeting", "q4-goals"])
# Returns: ["urgent", "client-meeting", "q4-goals"]

# Example 7: Category too long
try:
    result = validate_categories(["a" * 51])
except ValueError as e:
    print(e)
    # Prints: "Category 'aaa...' exceeds 50 characters"
```

#### Error Handling

| Error | Condition | Response |
|-------|-----------|----------|
| ValueError | Any category >50 characters | Raise ValueError: "Category '{cat}' exceeds 50 characters" |
| TypeError | categories is not a list | Raise TypeError: "categories must be a list" |
| TypeError | categories contains non-string | Raise TypeError: "All categories must be strings" |

---

### get_category_suggestions

Get category suggestions for autocomplete.

#### Signature

```python
def get_category_suggestions(partial: str = "") -> list[str]:
    """
    Get category suggestions for autocomplete.

    Args:
        partial: Partial category string for filtering suggestions

    Returns:
        List of suggested categories
    """
```

#### Input

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| partial | str | No | "" | Partial string to filter suggestions |

#### Output

| Type | Description |
|------|-------------|
| list[str] | List of suggested categories |

**Behavior**:
- Returns predefined suggestions: ["work", "home", "personal"]
- If partial provided, filters suggestions by prefix match (case-insensitive)
- If no partial, returns all suggestions

#### Examples

```python
# Example 1: No partial (all suggestions)
result = get_category_suggestions()
# Returns: ["work", "home", "personal"]

# Example 2: Partial match
result = get_category_suggestions("wo")
# Returns: ["work"]

# Example 3: Case-insensitive
result = get_category_suggestions("HO")
# Returns: ["home"]

# Example 4: No matches
result = get_category_suggestions("xyz")
# Returns: []
```

---

### validate_date_input

Validate and parse date input.

#### Signature

```python
def validate_date_input(date_input: str) -> datetime:
    """
    Validate and parse flexible date input.

    Args:
        date_input: Date string in various formats

    Returns:
        Parsed datetime object

    Raises:
        ValueError: If date format is invalid
    """
```

#### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| date_input | str | Yes | Date string to parse |

**Supported Formats**:
- Standard: MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD
- Natural language: "today", "tomorrow", "next week", "next Monday", "in 3 days"

#### Output

| Type | Description |
|------|-------------|
| datetime | Parsed datetime object |

#### Examples

```python
from datetime import datetime

# Example 1: Standard format (MM/DD/YYYY)
result = validate_date_input("02/15/2026")
# Returns: datetime(2026, 2, 15, 0, 0, 0)

# Example 2: Standard format (YYYY-MM-DD)
result = validate_date_input("2026-02-15")
# Returns: datetime(2026, 2, 15, 0, 0, 0)

# Example 3: Natural language (today)
result = validate_date_input("today")
# Returns: datetime for today at midnight

# Example 4: Natural language (tomorrow)
result = validate_date_input("tomorrow")
# Returns: datetime for tomorrow at midnight

# Example 5: Natural language (relative)
result = validate_date_input("in 3 days")
# Returns: datetime for 3 days from now

# Example 6: Invalid format
try:
    result = validate_date_input("invalid-date")
except ValueError as e:
    print(e)
    # Prints: "Invalid date format: 'invalid-date'. Use MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD, or natural language (today, tomorrow, next week)"
```

#### Error Handling

| Error | Condition | Response |
|-------|-----------|----------|
| ValueError | Invalid date format | Raise ValueError with helpful message listing valid formats |
| TypeError | date_input is not a string | Raise TypeError: "date_input must be a string" |

---

## Testing Requirements

### Unit Tests

**validate_priority**:
1. Valid priorities (high, medium, low)
2. Case-insensitive input
3. Invalid priority values
4. Type errors

**validate_categories**:
1. Valid category list
2. Normalization (lowercase, trim, deduplicate)
3. Empty list
4. Filter empty strings
5. Custom categories accepted
6. Category length validation
7. Type errors

**get_category_suggestions**:
1. No partial (all suggestions)
2. Partial match
3. Case-insensitive matching
4. No matches

**validate_date_input**:
1. Standard formats (MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD)
2. Natural language (today, tomorrow, next week, etc.)
3. Relative dates (in X days)
4. Invalid formats
5. Type errors

### Integration Tests

1. Validation in task creation workflow
2. Validation in task update workflow
3. Error messages displayed to user
4. Suggestions shown in CLI prompts

---

**Contract Version**: 1.0
**Date**: 2026-02-01
**Status**: Approved
