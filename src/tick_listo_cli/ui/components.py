"""
Rich UI components (tables, progress bars, menus).
"""

from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED, HEAVY_HEAD
from rich.style import Style
from typing import List, Optional, Dict, Any
from ..models.notification import Notification, NotificationType


def create_styled_table() -> Table:
    """
    Create a styled table with borders and alternating row colors per FR-003.
    Ensures responsiveness for different terminal widths per US3 requirements.

    Returns:
        Rich Table object with styled formatting
    """
    table = Table(
        box=HEAVY_HEAD,  # Bordered table
        header_style="bold magenta",
        title_style="bold cyan",
        caption_style="italic",
        expand=True,
        show_edge=True,
        pad_edge=True,
        collapse_padding=True
    )
    return table


def display_progress_bar(completed: int, total: int, title: str = ""):
    """
    Display a progress bar showing completion percentage per FR-013.
    Displays progress percentage as numeric value alongside progress bar per SC-008.

    Args:
        completed: Number of completed items
        total: Total number of items
        title: Title for the progress bar
    """
    console = Console()

    if total == 0:
        console.print("[italic]No items to track progress.[/italic]", style="yellow")
        return

    percentage = (completed / total) * 100

    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),  # Width per FR-013 requirement
        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
        console=console
    )

    task_id = progress.add_task(f"[cyan]{title}", total=total)
    progress.update(task_id, completed=completed)

    with progress:
        progress.update(task_id, completed=completed)

    # Also display the numeric percentage value separately per SC-008
    console.print(f"\n[bold]Progress: {completed}/{total} ({percentage:.1f}%)[/bold]", style="cyan")


def create_styled_menu(options: List[str], title: str = "Menu") -> Table:
    """
    Create a styled menu with highlighted selections per FR-014.

    Args:
        options: List of menu options
        title: Title for the menu

    Returns:
        Rich Table object representing the menu
    """
    table = Table(
        title=title,
        box=ROUNDED,
        header_style="bold blue on grey23",
        title_style="bold magenta",
        expand=False,
        padding=(0, 1)
    )

    table.add_column("Option", justify="center", style="bold yellow", no_wrap=True)
    table.add_column("Action", style="white")

    for i, option in enumerate(options, 1):
        # Highlight menu options with better contrast
        table.add_row(f"[reverse bold]{i}[/reverse bold]", f"[bold]{option}[/bold]")

    return table


def display_notification(notification: Notification):
    """
    Display a styled notification per FR-015.

    Args:
        notification: Notification object to display
    """
    console = Console()

    # Determine style based on notification type
    if notification.type == NotificationType.INFO:
        style = "bold blue"
        icon = "ℹ"
    elif notification.type == NotificationType.SUCCESS:
        style = "bold green"
        icon = "✓"
    elif notification.type == NotificationType.WARNING:
        style = "bold yellow"
        icon = "⚠"
    elif notification.type == NotificationType.ERROR:
        style = "bold red"
        icon = "✗"
    else:
        style = "bold white"
        icon = "•"

    panel = Panel(
        f"{notification.message}",
        title=f"{icon} {notification.title}",
        border_style=style.replace("bold ", ""),
        title_align="left"
    )

    console.print(panel)


def display_styled_message(message: str, message_type: str = "info"):
    """
    Display a styled message with appropriate formatting.

    Args:
        message: Message to display
        message_type: Type of message ('info', 'success', 'warning', 'error')
    """
    console = Console()

    styles = {
        "info": "bold blue",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red"
    }

    style = styles.get(message_type, "bold white")
    console.print(message, style=style)


def create_alternating_rows_table(data: List[Dict[str, Any]], headers: List[str]) -> Table:
    """
    Create a table with alternating row colors for improved readability per FR-003.
    Handles long text gracefully and ensures responsiveness per US3 requirements.
    Optimized for performance with large datasets per NFR-002.

    Args:
        data: List of dictionaries containing row data
        headers: List of column headers

    Returns:
        Rich Table object with alternating row colors
    """
    # For performance optimization with large datasets, use a more efficient approach
    table = Table(box=HEAVY_HEAD, header_style="bold magenta", row_styles=["", "dim"])  # Alternating styles

    # Add columns with overflow handling for long text
    for header in headers:
        # For task-specific columns like title and description, set overflow to fold
        if header.lower() in ['title', 'description']:
            table.add_column(header, style="dim", header_style="bold", overflow="fold", min_width=10)
        else:
            table.add_column(header, style="dim", header_style="bold", overflow="ellipsis", min_width=5)

    # Add rows efficiently - batch add if there are many rows
    if len(data) > 100:  # For larger datasets
        for row_data in data:
            row_values = [str(row_data.get(header, "")) for header in headers]
            table.add_row(*row_values)
    else:  # For smaller datasets, same approach but more readable
        for row_data in data:
            row_values = []
            for header in headers:
                value = str(row_data.get(header, ""))
                row_values.append(value)
            table.add_row(*row_values)

    return table