"""
Animation and transition effects.
"""

import time
import sys
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.spinner import Spinner
from rich.panel import Panel
from typing import Callable, Any


def show_loading_animation(duration: float = 2.0, message: str = "Processing..."):
    """
    Display an animated loading indicator per FR-018.

    Args:
        duration: Duration to show the animation (in seconds)
        message: Message to display with the animation
    """
    console = Console()

    with Progress(
        SpinnerColumn(spinner_name="clock"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        task_id = progress.add_task(description=message)
        total_time = 0
        while not progress.finished:
            progress.update(task_id, advance=1)
            time.sleep(0.1)
            total_time += 0.1
            if total_time >= duration:
                break


def animate_loading_indicator(message: str = "Loading..."):
    """
    Show a continuous loading indicator until stopped.

    Args:
        message: Message to display with the loading indicator
    """
    console = Console()
    spinner = Spinner("clock", style="bold green")

    with Live(Panel(spinner, title=message, border_style="blue"), refresh_per_second=10) as live:
        try:
            # This would typically run until some condition is met
            # For now, we'll just simulate with a sleep
            time.sleep(2)
        except KeyboardInterrupt:
            pass


def show_smooth_transition(start_func: Callable[[], Any], end_func: Callable[[], Any],
                          transition_duration: float = 0.5):
    """
    Show a smooth transition between two UI states per FR-019.

    Args:
        start_func: Function to call for the starting state
        end_func: Function to call for the ending state
        transition_duration: Duration of the transition (in seconds)
    """
    console = Console()

    # Show start state
    start_func()

    # Brief pause to show the transition happening
    time.sleep(transition_duration)

    # Clear screen and show end state
    console.clear()
    end_func()


def show_visual_feedback(message: str, duration: float = 1.0, style: str = "bold green"):
    """
    Show visual feedback for user actions per FR-020.

    Args:
        message: Feedback message to show
        duration: How long to show the feedback (in seconds)
        style: Rich style to apply to the message
    """
    console = Console()

    # Show feedback message
    console.print(f"{message}", style=style)

    # Brief pause to let user see the feedback
    time.sleep(duration)


def show_operation_feedback(operation_name: str, func: Callable[[], Any],
                          success_message: str = "Operation completed successfully!",
                          error_message: str = "Operation failed!"):
    """
    Show feedback for an operation with loading indicator and result.

    Args:
        operation_name: Name of the operation being performed
        func: Function to execute
        success_message: Message to show on success
        error_message: Message to show on error
    """
    console = Console()

    # Show loading animation
    with Progress(
        SpinnerColumn(spinner_name="clock"),
        TextColumn(f"[progress.description]{{task.description}}"),
        transient=True,
        console=console
    ) as progress:
        task_id = progress.add_task(description=f"{operation_name}...")

        try:
            result = func()
            progress.update(task_id, completed=100)

            # Show success feedback
            console.print(f"✓ {success_message}", style="bold green")
            return result
        except Exception as e:
            progress.update(task_id, completed=100)

            # Show error feedback
            console.print(f"✗ {error_message}: {str(e)}", style="bold red")
            raise e


def fade_effect(content: str, duration: float = 1.0):
    """
    Simulate a fade effect for content display.

    Args:
        content: Content to display with fade effect
        duration: Duration of the fade effect
    """
    console = Console()

    # For now, just display the content (more sophisticated fading would require frame-by-frame control)
    console.print(content)
    time.sleep(duration)