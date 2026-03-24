from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class RichUIConfig:
    """
    Configuration object for Rich UI elements and styling.

    Attributes:
        color_scheme: Dictionary of color definitions for different statuses
        table_style: Dictionary of table formatting options
        animation_enabled: Whether animations are enabled (default: True)
        progress_bar_width: Width of progress bars (default: 30)
    """
    color_scheme: Optional[Dict[str, str]] = None
    table_style: Optional[Dict[str, any]] = None
    animation_enabled: bool = True
    progress_bar_width: int = 30

    def __post_init__(self):
        """Initialize default values if not provided."""
        if self.color_scheme is None:
            self.color_scheme = {
                "completed": "#28a745",  # Green
                "pending": "#dc3545",    # Red
                "in_progress": "#ffc107", # Yellow
                "header": "#007bff",     # Blue
                "success": "#28a745",    # Green
                "warning": "#ffc107",    # Yellow
                "error": "#dc3545"       # Red
            }

        if self.table_style is None:
            self.table_style = {
                "show_header": True,
                "show_lines": True,
                "alternating_colors": True,
                "border_color": "#808080"
            }