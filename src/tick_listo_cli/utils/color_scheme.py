"""
Color management for consistent visual identity per plan.md.
"""

from typing import Dict


class ColorScheme:
    """
    Centralized color scheme management for consistent visual identity per FR-017.
    """

    def __init__(self):
        """
        Initialize the color scheme with default values.
        """
        self.colors = {
            # Task status colors per FR-012
            "completed": "#28a745",  # Green
            "pending": "#dc3545",    # Red
            "in_progress": "#ffc107", # Yellow

            # UI element colors
            "header": "#007bff",     # Blue
            "success": "#28a745",    # Green
            "warning": "#ffc107",    # Yellow
            "error": "#dc3545",      # Red
            "info": "#17a2b8",       # Cyan
            "primary": "#007bff",    # Blue
            "secondary": "#6c757d",  # Gray
            "light": "#f8f9fa",      # Light gray
            "dark": "#343a40",       # Dark gray
            "background": "#ffffff", # White
            "text": "#212529",       # Dark gray/black
            "border": "#dee2e6"      # Light gray
        }

    def get_color(self, key: str) -> str:
        """
        Get a color by key.

        Args:
            key: The color key to retrieve

        Returns:
            The color value as a hex string
        """
        return self.colors.get(key, "#000000")  # Default to black if key not found

    def set_color(self, key: str, value: str):
        """
        Set a color for a specific key.

        Args:
            key: The color key to set
            value: The color value as a hex string
        """
        self.colors[key] = value

    def get_status_color(self, status: str) -> str:
        """
        Get the appropriate color for a task status per FR-012.

        Args:
            status: The task status ('completed', 'pending', 'in-progress')

        Returns:
            The appropriate color for the status
        """
        status_map = {
            'completed': self.colors['completed'],
            'pending': self.colors['pending'],
            'in-progress': self.colors['in_progress'],
            'in_progress': self.colors['in_progress']  # Alternative format
        }

        return status_map.get(status.lower(), self.colors['pending'])  # Default to pending

    def get_notification_color(self, notification_type: str) -> str:
        """
        Get the appropriate color for a notification type.

        Args:
            notification_type: The notification type ('info', 'success', 'warning', 'error')

        Returns:
            The appropriate color for the notification type
        """
        type_map = {
            'info': self.colors['info'],
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'error': self.colors['error']
        }

        return type_map.get(notification_type.lower(), self.colors['info'])  # Default to info

    def get_all_colors(self) -> Dict[str, str]:
        """
        Get all colors in the scheme.

        Returns:
            Dictionary of all colors
        """
        return self.colors.copy()

    def apply_terminal_compatibility(self, terminal_capabilities: dict = None):
        """
        Apply terminal compatibility adjustments if needed per NFR-003.

        Args:
            terminal_capabilities: Dictionary of terminal capabilities
        """
        if terminal_capabilities is None:
            terminal_capabilities = {}

        # If terminal doesn't support certain features, adjust colors accordingly
        if not terminal_capabilities.get('supports_truecolor', True):
            # Use standard ANSI colors instead of hex for compatibility
            self.colors = {
                "completed": "green",
                "pending": "red",
                "in_progress": "yellow",
                "header": "blue",
                "success": "green",
                "warning": "yellow",
                "error": "red",
                "info": "cyan",
                "primary": "blue",
                "secondary": "bright_black",
                "light": "white",
                "dark": "bright_black",
                "background": "white",
                "text": "black",
                "border": "bright_black"
            }