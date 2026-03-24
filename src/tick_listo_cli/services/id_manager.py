"""ID Manager service for auto-incrementing task IDs."""


class IDManager:
    """
    Service for managing auto-incrementing task IDs.

    Provides:
    - Sequential ID generation (1, 2, 3, ...)
    - Counter persistence support
    - Counter reset for "delete all" operation
    - IDs never reused during normal operation
    """

    def __init__(self):
        """Initialize ID manager with counter starting at 1."""
        self._counter: int = 1

    def generate_id(self) -> int:
        """
        Generate next unique task ID and increment counter.

        Returns:
            Next available task ID (positive integer)

        Raises:
            RuntimeError: If ID counter reaches maximum value
        """
        if self._counter >= 2**31 - 1:  # Max int value
            raise RuntimeError("ID counter has reached maximum value")

        current_id = self._counter
        self._counter += 1
        return current_id

    def get_current_counter(self) -> int:
        """
        Get current ID counter value without incrementing.

        Returns:
            Current counter value (next ID to be generated)
        """
        return self._counter

    def set_counter(self, value: int) -> None:
        """
        Set ID counter to specific value.

        Used when loading persisted counter from storage.

        Args:
            value: Counter value to set (must be positive integer)

        Raises:
            TypeError: If value is not an integer
            ValueError: If value is not a positive integer
        """
        if not isinstance(value, int):
            raise TypeError("Counter must be an integer")

        if value < 1:
            raise ValueError("Counter must be a positive integer")

        self._counter = value

    def reset_counter(self) -> None:
        """
        Reset ID counter to 1.

        Used after "delete all" operation to start fresh numbering.
        Next generated ID will be 1.
        """
        self._counter = 1
