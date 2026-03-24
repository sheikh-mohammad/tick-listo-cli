"""
Rich UI layer handling all visual presentation elements.
"""

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from datetime import datetime
from typing import List, Optional
from ..models.task import Task, TaskStatus, Priority
from ..models.rich_ui_config import RichUIConfig


class RichUI:
    """
    Rich UI class to manage all Rich formatting and visual presentation.
    """

    def __init__(self, config: Optional[RichUIConfig] = None):
        """
        Initialize RichUI with optional configuration.

        Args:
            config: RichUIConfig object with styling options
        """
        import sys
        import io

        # Ensure UTF-8 encoding on Windows to support Unicode characters
        if sys.platform == 'win32':
            # Reconfigure stdout and stderr to use UTF-8 encoding
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')

        self.console = Console()
        self.config = config or RichUIConfig()

    def display_ascii_header(self):
        """
        Display the ASCII art header with branded message per FR-011.
        Handles terminal resizing gracefully.
        """
        # Check terminal width and adjust display if necessary
        terminal_width = self.console.size.width

        # Define the ASCII art
        ascii_art_lines = [
        "                   ████████╗██╗ ██████╗██╗  ██╗    ██╗     ██╗███████╗████████╗ ██████╗ ",
        "                   ╚══██╔══╝██║██╔════╝██║ ██╔╝    ██║     ██║██╔════╝╚══██╔══╝██╔═══██╗",
        "                      ██║   ██║██║     █████╔╝     ██║     ██║███████╗   ██║   ██║   ██║",
        "                      ██║   ██║██║     ██╔═██╗     ██║     ██║╚════██║   ██║   ██║   ██║",
        "                      ██║   ██║╚██████╗██║  ██╗    ███████╗██║███████║   ██║   ╚██████╔╝",
        "                      ╚═╝   ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚══════╝╚═╝╚══════╝   ╚═╝    ╚═════╝ ",
        "",
        "          Tick Listo CLI - Your Ultimate Task Management Companion - Where Productivity Meets Elegance"
        ]


        # If terminal is too narrow, display a simplified version
        if terminal_width < 80:
            # Fallback for narrow terminals
            self.console.print("\n[b]TICK LISTO CLI[/b]\n", style="bold blue")
            self.console.print("Your Ultimate Task Management Companion\n", style="italic")
        else:
            # Display the full ASCII art
            ascii_art = "\n".join(ascii_art_lines)
            self.console.print(ascii_art)

    def display_startup_message(self):
        """
        Display startup message with ASCII art header and branded message.
        """
        self.display_ascii_header()
        self.console.print("\nWelcome to Tick Listo CLI! Your productivity companion.\n", style="bold blue")

    def get_priority_style(self, priority: Priority) -> str:
        """
        Get styled priority indicator with color coding.

        Args:
            priority: Priority enum value

        Returns:
            Formatted priority string with Rich markup
        """
        priority_styles = {
            Priority.HIGH: "[red]●[/red] High",
            Priority.MEDIUM: "[yellow]●[/yellow] Medium",
            Priority.LOW: "[green]●[/green] Low"
        }
        return priority_styles.get(priority, "[white]●[/white] Unknown")

    def format_priority(self, priority: Priority) -> str:
        """
        Format priority for display (alias for get_priority_style).

        Args:
            priority: Priority enum value

        Returns:
            Formatted priority string with Rich markup
        """
        return self.get_priority_style(priority)

    def format_categories(self, categories: List[str]) -> str:
        """
        Format categories for display as comma-separated tags.

        Args:
            categories: List of category strings

        Returns:
            Formatted categories string
        """
        if not categories:
            return "[dim]-[/dim]"
        return ", ".join([f"[cyan]{cat}[/cyan]" for cat in categories])

    def get_category_display(self, categories: List[str]) -> str:
        """
        Get category display string (alias for format_categories).

        Args:
            categories: List of category strings

        Returns:
            Formatted categories string
        """
        return self.format_categories(categories)

    def display_tasks(self, tasks: List[Task]):
        """
        Display tasks with enhanced fields (priority, categories, due_date).
        This is the enhanced version that includes new fields.

        Args:
            tasks: List of Task objects to display
        """
        from .components import create_styled_table

        if not tasks:
            self.console.print("[bold italic]No tasks found.[/bold italic]", style="yellow")
            return

        table = create_styled_table()
        table.add_column("ID", justify="center", style="bold", width=6)
        table.add_column("Title", style="white", width=25)
        table.add_column("Priority", width=12)
        table.add_column("Categories", width=20)
        table.add_column("Due Date", width=12)
        table.add_column("Status", justify="center", width=12)

        for task in tasks:
            # Priority with color coding
            priority_display = self.get_priority_style(task.priority)

            # Categories display
            categories_display = self.format_categories(task.categories)

            # Due date display
            if task.due_date:
                due_date_display = task.due_date.strftime("%Y-%m-%d")
                # Check if overdue
                if task.is_overdue():
                    due_date_display = f"[red]{due_date_display}[/red]"
            else:
                due_date_display = "[dim]-[/dim]"

            # Status with color coding
            if task.status == TaskStatus.COMPLETED or task.completed:
                status_display = "[green]✓[/green] Done"
            elif task.status == TaskStatus.IN_PROGRESS:
                status_display = "[yellow]●[/yellow] Progress"
            else:
                status_display = "[white]○[/white] Pending"

            table.add_row(
                str(task.id),
                task.title,
                priority_display,
                categories_display,
                due_date_display,
                status_display
            )

        self.console.print(table)

    def display_task_list(self, tasks: List[Task]):
        """
        Display tasks in a styled table with color coding per FR-003 and FR-012.

        Args:
            tasks: List of Task objects to display
        """
        from .components import create_styled_table

        if not tasks:
            self.console.print("[bold italic]No tasks found.[/bold italic]", style="yellow")
            return

        table = create_styled_table()
        table.add_column("ID", justify="center", style="bold")
        table.add_column("Title", style="dim")
        table.add_column("Description", style="dim")
        table.add_column("Status", justify="center")
        table.add_column("Created", style="italic")

        for task in tasks:
            # Determine color based on status per FR-012
            if task.status == TaskStatus.COMPLETED:
                status_color = "green"
                status_text = f"[{status_color}]✓ Completed[/]"
            elif task.status == TaskStatus.IN_PROGRESS:
                status_color = "yellow"
                status_text = f"[{status_color}]● In Progress[/]"
            else:  # pending
                status_color = "red"
                status_text = f"[{status_color}]○ Pending[/]"

            table.add_row(
                str(task.id),
                task.title,
                task.description,
                status_text,
                task.created_timestamp.strftime("%Y-%m-%d %H:%M")
            )

        self.console.print(table)

    def display_success_message(self, message: str):
        """
        Display a success message with Rich styling.

        Args:
            message: Success message to display
        """
        self.console.print(f"✓ {message}", style="bold green")

    def display_error_message(self, message: str):
        """
        Display an error message with Rich styling per FR-015.

        Args:
            message: Error message to display
        """
        self.console.print(f"✗ {message}", style="bold red")

    def display_warning_message(self, message: str):
        """
        Display a warning message with Rich styling.

        Args:
            message: Warning message to display
        """
        self.console.print(f"⚠ {message}", style="bold yellow")

    def display_info_message(self, message: str):
        """
        Display an info message with Rich styling.

        Args:
            message: Info message to display
        """
        self.console.print(f"ℹ {message}", style="bold blue")

    def display_confirmation_prompt(self, message: str) -> bool:
        """
        Display a confirmation prompt and get user input.

        Args:
            message: Confirmation message to display

        Returns:
            True if user confirms, False otherwise
        """
        self.console.print(f"? {message} [y/N]: ", style="bold cyan", end="")
        response = input().strip().lower()
        return response in ['y', 'yes']

    def display_progress_stats(self, stats_data: dict):
        """
        Display progress statistics with visual elements.

        Args:
            stats_data: Dictionary containing progress statistics
        """
        from .components import display_progress_bar

        total = stats_data.get('total_tasks', 0)
        completed = stats_data.get('completed_tasks', 0)
        pending = stats_data.get('pending_tasks', 0)
        in_progress = stats_data.get('in_progress_tasks', 0)
        percentage = stats_data.get('completion_percentage', 0.0)

        self.console.print("\n[b]Task Progress Summary:[/b]\n", style="bold underline")

        # Display summary stats
        stats_text = (
            f"Total Tasks: [bold]{total}[/bold] | "
            f"Completed: [green bold]{completed}[/green bold] | "
            f"Pending: [red bold]{pending}[/red bold] | "
            f"In Progress: [yellow bold]{in_progress}[/yellow bold]"
        )
        self.console.print(stats_text)

        # Display progress bar
        if total > 0:
            display_progress_bar(completed, total, f"Completion: {percentage:.1f}%")
        else:
            self.console.print("[italic]No tasks to calculate progress.[/italic]", style="yellow")

    def display_visual_feedback(self, message: str, style: str = "bold"):
        """
        Provide visual feedback for user actions per FR-020.

        Args:
            message: Feedback message to display
            style: Rich style to apply to the message
        """
        self.console.print(f"{message}", style=style)

    def clear_screen(self):
        """
        Clear the console screen.
        """
        self.console.clear()