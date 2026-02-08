from typing import Optional
import sys
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from ..services.task_service import TaskService
from ..services.search_service import SearchService
from ..services.filter_service import FilterService
from ..services.sort_service import SortService
from ..ui.components import create_styled_menu
from ..models.task import Priority


class TickListoCLI:
    """
    Command-line interface for the Tick Listo application.
    Implements all the required commands with Rich formatting.
    """

    def __init__(self):
        """Initialize the CLI with a task service and console."""
        self.task_service = TaskService()
        self.search_service = SearchService()
        self.filter_service = FilterService()
        self.sort_service = SortService()
        self.console = Console()

        # Initialize ReminderService if Gmail credentials are available (T073 - User Story 4)
        self.reminder_service = None
        try:
            from ..services.gmail_service import GmailService
            from ..services.reminder_service import ReminderService
            from ..services.time_zone_service import TimeZoneService
            from ..services.storage_service import StorageService

            # Try to initialize Gmail service (requires credentials.json)
            gmail_service = GmailService()
            storage_service = StorageService()
            tz_service = TimeZoneService()

            # Initialize ReminderService
            self.reminder_service = ReminderService(
                gmail_service=gmail_service,
                storage_service=storage_service,
                time_zone_service=tz_service
            )

            # Update TaskService with ReminderService
            self.task_service.reminder_service = self.reminder_service

            # Start the reminder service
            self.reminder_service.start()

            self.console.print("[green]✓ Email reminder service started[/green]")

        except FileNotFoundError:
            # Gmail credentials not found - reminders disabled
            self.console.print("[yellow]⚠ Email reminders disabled (credentials.json not found)[/yellow]")
        except Exception as e:
            # Other error - reminders disabled
            self.console.print(f"[yellow]⚠ Email reminders disabled: {e}[/yellow]")

    def run(self):
        """Main CLI loop that handles user commands."""
        # Display startup message with ASCII art header
        self.task_service.rich_ui.display_startup_message()

        while True:
            try:
                # Use styled menu for command input
                command = Prompt.ask("[bold green]Tick Listo[/bold green]", default="help").strip().lower()

                if command in ['quit', 'q']:
                    self._handle_quit()
                    break
                elif command in ['add', 'a']:
                    self._handle_add()
                elif command in ['view', 'v']:
                    self._handle_view()
                elif command in ['update', 'u']:
                    self._handle_update()
                elif command in ['delete', 'd']:
                    self._handle_delete()
                elif command in ['complete', 'c']:
                    self._handle_complete()
                elif command in ['search', 'find', 'f']:
                    self._handle_search()
                elif command in ['filter', 'fl']:
                    self._handle_filter()
                elif command in ['sort', 'sr']:
                    self._handle_sort()
                elif command in ['clear', 'clr']:
                    self._handle_clear()
                elif command in ['delete all', 'dela']:
                    self._handle_delete_all()
                elif command in ['stats', 's']:  # Add stats command
                    self._handle_stats()
                elif command in ['reminders', 'rem']:  # Add reminder status command (T074)
                    self._handle_reminders()
                elif command in ['recurring', 'rec']:  # Add recurring series command (T083)
                    self._handle_recurring_series()
                elif command in ['timezone', 'tz']:  # Add timezone configuration command (T102)
                    self._handle_timezone()
                elif command in ['help', 'h']:
                    self._handle_help()
                else:
                    self.task_service.display_error_message(f"Unknown command: {command}")
                    self.console.print("Type 'help' for available commands.\n")

            except KeyboardInterrupt:
                self.task_service.display_error_message("Received interrupt signal. Quitting...")
                self._handle_quit()
                break
            except EOFError:
                self.task_service.display_error_message("End of input received. Quitting...")
                self._handle_quit()
                break

    def _handle_add(self):
        """Handle the add command to create a new task with required priority and categories (Phase 10 - User Story 6)."""
        self.task_service.rich_ui.display_info_message("Adding a new task:")

        title = Prompt.ask("Enter task title")

        # Validate title length
        if not title or len(title.strip()) < 1 or len(title.strip()) > 200:
            self.task_service.display_error_message("Title must be between 1 and 200 characters.")
            return

        description = Prompt.ask("Enter task description (optional)", default="")

        # Validate description length
        if len(description) > 1000:
            self.task_service.display_error_message("Description cannot exceed 1000 characters.")
            return

        # REQUIRED: Prompt for priority (Phase 10 - User Story 6)
        priority = None
        while priority is None:
            priority_input = Prompt.ask(
                "Enter task priority [bold](high/medium/low)[/bold] [red]*required[/red]"
            ).strip().lower()

            try:
                from ..services.validation_service import validate_priority
                priority = validate_priority(priority_input)
            except ValueError as e:
                self.task_service.display_error_message(str(e))
                retry = Confirm.ask("Try again?", default=True)
                if not retry:
                    self.task_service.display_error_message("Task creation cancelled.")
                    return

        # REQUIRED: Prompt for categories (Phase 10 - User Story 6)
        categories = None
        while categories is None or len(categories) == 0:
            self.console.print("\n[yellow]Suggested categories: work, home, personal[/yellow]")
            categories_input = Prompt.ask(
                "Enter task categories (comma-separated) [red]*required[/red]"
            ).strip()

            if not categories_input:
                self.task_service.display_error_message("At least one category is required.")
                retry = Confirm.ask("Try again?", default=True)
                if not retry:
                    self.task_service.display_error_message("Task creation cancelled.")
                    return
                continue

            # Parse categories
            categories = [cat.strip() for cat in categories_input.split(",") if cat.strip()]

            if len(categories) == 0:
                self.task_service.display_error_message("At least one category is required.")
                retry = Confirm.ask("Try again?", default=True)
                if not retry:
                    self.task_service.display_error_message("Task creation cancelled.")
                    return
                categories = None

        # Optional: Prompt for due date
        due_date = None
        due_time = None
        has_due_date = Confirm.ask("Add a due date?", default=False)
        if has_due_date:
            due_date_input = Prompt.ask(
                "Enter due date (MM/DD/YYYY, YYYY-MM-DD, or 'tomorrow', 'next week', etc.)"
            ).strip()

            if due_date_input:
                try:
                    from ..services.validation_service import validate_date_input
                    due_date = validate_date_input(due_date_input)

                    # If due date is set, optionally prompt for time (T024 - User Story 1)
                    has_due_time = Confirm.ask("Add a specific time?", default=False)
                    if has_due_time:
                        due_time_input = Prompt.ask(
                            "Enter time (HH:MM, HH:MM AM/PM, or '2pm', '9am', etc.)"
                        ).strip()

                        if due_time_input:
                            try:
                                from ..utils.date_parser import parse_time
                                due_time = parse_time(due_time_input)
                            except ValueError as e:
                                self.task_service.display_error_message(f"Invalid time: {str(e)}")
                                self.console.print("[yellow]Continuing without time...[/yellow]")

                except ValueError as e:
                    self.task_service.display_error_message(f"Invalid date: {str(e)}")
                    self.console.print("[yellow]Continuing without due date...[/yellow]")

        # Optional: Make task recurring (T041 - User Story 2)
        recurrence_pattern = None
        recurrence_interval = 1
        recurrence_weekdays = None
        recurrence_end_date = None

        if due_date:  # Recurring tasks require a due date
            has_recurrence = Confirm.ask("Make this a recurring task?", default=False)
            if has_recurrence:
                # Prompt for recurrence pattern
                pattern_input = Prompt.ask(
                    "Enter recurrence pattern [bold](daily/weekly/monthly/yearly)[/bold]"
                ).strip().lower()

                try:
                    from ..models.task import RecurrencePattern
                    pattern_map = {
                        "daily": RecurrencePattern.DAILY,
                        "weekly": RecurrencePattern.WEEKLY,
                        "monthly": RecurrencePattern.MONTHLY,
                        "yearly": RecurrencePattern.YEARLY
                    }
                    recurrence_pattern = pattern_map.get(pattern_input)

                    if not recurrence_pattern:
                        self.task_service.display_error_message(f"Invalid pattern: {pattern_input}")
                        self.console.print("[yellow]Continuing without recurrence...[/yellow]")
                    else:
                        # Prompt for interval
                        interval_input = Prompt.ask("Enter interval (e.g., 1 for every, 2 for every other)", default="1")
                        try:
                            recurrence_interval = int(interval_input)
                            if recurrence_interval < 1:
                                raise ValueError("Interval must be >= 1")
                        except ValueError:
                            self.task_service.display_error_message("Invalid interval, using 1")
                            recurrence_interval = 1

                        # For weekly pattern, optionally specify weekdays
                        if recurrence_pattern == RecurrencePattern.WEEKLY:
                            has_weekdays = Confirm.ask("Specify specific weekdays (e.g., Mon/Wed/Fri)?", default=False)
                            if has_weekdays:
                                weekdays_input = Prompt.ask(
                                    "Enter weekdays (0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun), comma-separated"
                                ).strip()
                                try:
                                    recurrence_weekdays = [int(d.strip()) for d in weekdays_input.split(",")]
                                    # Validate weekdays
                                    if not all(0 <= d <= 6 for d in recurrence_weekdays):
                                        raise ValueError("Weekdays must be 0-6")
                                except ValueError as e:
                                    self.task_service.display_error_message(f"Invalid weekdays: {e}")
                                    recurrence_weekdays = None

                        # Optionally set end date
                        has_end_date = Confirm.ask("Set an end date for recurrence?", default=False)
                        if has_end_date:
                            end_date_input = Prompt.ask("Enter end date (YYYY-MM-DD)").strip()
                            try:
                                from ..services.validation_service import validate_date_input
                                recurrence_end_date = validate_date_input(end_date_input)
                            except ValueError as e:
                                self.task_service.display_error_message(f"Invalid end date: {e}")

                except Exception as e:
                    self.task_service.display_error_message(f"Error setting up recurrence: {e}")
                    recurrence_pattern = None

        # Optional: Configure reminders (T056 - User Story 3)
        reminder_settings = []
        if due_time:  # Reminders require due_time
            has_reminders = Confirm.ask("Set up email reminders?", default=False)
            if has_reminders:
                self.console.print("\n[yellow]Configure reminders (you can add multiple)[/yellow]")

                while True:
                    offset_input = Prompt.ask(
                        "Enter reminder time before due (e.g., '60' for 1 hour, '1440' for 1 day, or 'done' to finish)"
                    ).strip().lower()

                    if offset_input == 'done':
                        break

                    try:
                        offset_minutes = int(offset_input)
                        if offset_minutes <= 0:
                            self.task_service.display_error_message("Offset must be greater than 0")
                            continue

                        # Generate label
                        if offset_minutes < 60:
                            label = f"{offset_minutes} minutes before"
                        elif offset_minutes < 1440:
                            hours = offset_minutes // 60
                            label = f"{hours} hour{'s' if hours > 1 else ''} before"
                        else:
                            days = offset_minutes // 1440
                            label = f"{days} day{'s' if days > 1 else ''} before"

                        from ..models.reminder import ReminderSetting
                        reminder_settings.append(ReminderSetting(
                            offset_minutes=offset_minutes,
                            label=label
                        ))
                        self.console.print(f"[green]Added reminder: {label}[/green]")

                        if not Confirm.ask("Add another reminder?", default=False):
                            break

                    except ValueError:
                        self.task_service.display_error_message("Invalid offset. Please enter a number.")

        # Add the task with all required fields
        try:
            task = self.task_service.add_task(
                title.strip(),
                description,
                priority=priority,
                categories=categories,
                due_date=due_date,
                due_time=due_time
            )

            # Set recurrence fields if specified (T041 - User Story 2)
            if recurrence_pattern:
                task.recurrence_pattern = recurrence_pattern
                task.recurrence_interval = recurrence_interval
                task.recurrence_weekdays = recurrence_weekdays
                task.recurrence_end_date = recurrence_end_date

                # Create recurring series
                series = self.task_service.recurring_service.create_recurring_task(task)
                self.console.print(f"[green]Created recurring task series: {series.series_id}[/green]")

            # Set reminder settings if specified (T056 - User Story 3)
            if reminder_settings:
                task.reminder_settings = reminder_settings
                self.console.print(f"[green]Configured {len(reminder_settings)} reminder(s)[/green]")

            self.task_service.save_to_file()
            self.task_service.display_success_message(f"Task added successfully with ID: {task.id}")
        except ValueError as e:
            self.task_service.display_error_message(f"Failed to add task: {str(e)}")

    def _handle_view(self):
        """Handle the view command to display all tasks."""
        self.task_service.display_all_tasks_enhanced()

    def _handle_update(self):
        """Handle the update command with full re-entry of all fields (Phase 11 - Enhanced Features)."""
        self.task_service.rich_ui.display_info_message("Updating a task:")

        try:
            task_id_str = Prompt.ask("Enter task ID to update")
            task_id = int(task_id_str)
        except ValueError:
            self.task_service.display_error_message("Invalid task ID. Please enter a number.")
            return

        # Check if task exists
        task = self.task_service.get_by_id(task_id)
        if not task:
            self.task_service.display_error_message(f"Task with ID {task_id} not found.")
            return

        # Check if this is a recurring task (T085 - User Story 5)
        update_all_future = False
        if task.series_id:
            self.console.print("\n[yellow]⚠ This is a recurring task.[/yellow]")
            update_choice = Prompt.ask(
                "Update scope",
                choices=["this", "future"],
                default="this"
            )
            update_all_future = (update_choice == "future")

            if update_all_future:
                self.console.print("[cyan]Will update all future instances in the series.[/cyan]")
            else:
                self.console.print("[cyan]Will update only this instance.[/cyan]")

        # Display current values (Phase 11 - Enhanced Features)
        self.console.print("\n[bold cyan]Current Task Details:[/bold cyan]")
        self.console.print(f"  Title: {task.title}")
        self.console.print(f"  Description: {task.description}")
        self.console.print(f"  Priority: {task.priority.value}")
        self.console.print(f"  Categories: {', '.join(task.categories)}")
        self.console.print(f"  Due Date: {task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'}")
        self.console.print(f"  Due Time: {task.due_time.strftime('%H:%M') if task.due_time else 'None'}")
        self.console.print(f"  Completed: {task.completed}\n")

        self.console.print("[yellow]Please re-enter ALL fields (full re-entry required):[/yellow]\n")

        # Full re-entry: Title
        new_title = Prompt.ask("Enter task title", default=task.title)

        if not new_title or len(new_title.strip()) < 1 or len(new_title.strip()) > 200:
            self.task_service.display_error_message("Title must be between 1 and 200 characters.")
            return

        # Full re-entry: Description
        new_description = Prompt.ask("Enter task description", default=task.description)

        if len(new_description) > 1000:
            self.task_service.display_error_message("Description cannot exceed 1000 characters.")
            return

        # Full re-entry: Priority
        new_priority = None
        while new_priority is None:
            priority_input = Prompt.ask(
                "Enter task priority (high/medium/low)",
                default=task.priority.value
            ).strip().lower()

            try:
                from ..services.validation_service import validate_priority
                new_priority = validate_priority(priority_input)
            except ValueError as e:
                self.task_service.display_error_message(str(e))
                retry = Confirm.ask("Try again?", default=True)
                if not retry:
                    self.task_service.display_error_message("Task update cancelled.")
                    return

        # Full re-entry: Categories
        new_categories = None
        while new_categories is None or len(new_categories) == 0:
            categories_input = Prompt.ask(
                "Enter task categories (comma-separated)",
                default=", ".join(task.categories)
            ).strip()

            if not categories_input:
                self.task_service.display_error_message("At least one category is required.")
                retry = Confirm.ask("Try again?", default=True)
                if not retry:
                    self.task_service.display_error_message("Task update cancelled.")
                    return
                continue

            new_categories = [cat.strip() for cat in categories_input.split(",") if cat.strip()]

            if len(new_categories) == 0:
                self.task_service.display_error_message("At least one category is required.")
                retry = Confirm.ask("Try again?", default=True)
                if not retry:
                    self.task_service.display_error_message("Task update cancelled.")
                    return
                new_categories = None

        # Full re-entry: Due date
        new_due_date = None
        new_due_time = None
        current_due_date_str = task.due_date.strftime('%Y-%m-%d') if task.due_date else ""
        current_due_time_str = task.due_time.strftime('%H:%M') if task.due_time else ""

        has_due_date = Confirm.ask("Add/update due date?", default=bool(task.due_date))
        if has_due_date:
            due_date_input = Prompt.ask(
                "Enter due date (MM/DD/YYYY, YYYY-MM-DD, or 'tomorrow', 'next week', etc.)",
                default=current_due_date_str
            ).strip()

            if due_date_input:
                try:
                    from ..services.validation_service import validate_date_input
                    new_due_date = validate_date_input(due_date_input)

                    # If due date is set, optionally prompt for time (T024 - User Story 1)
                    has_due_time = Confirm.ask("Add/update specific time?", default=bool(task.due_time))
                    if has_due_time:
                        due_time_input = Prompt.ask(
                            "Enter time (HH:MM, HH:MM AM/PM, or '2pm', '9am', etc.)",
                            default=current_due_time_str
                        ).strip()

                        if due_time_input:
                            try:
                                from ..utils.date_parser import parse_time
                                new_due_time = parse_time(due_time_input)
                            except ValueError as e:
                                self.task_service.display_error_message(f"Invalid time: {str(e)}")
                                self.console.print("[yellow]Continuing without time...[/yellow]")

                except ValueError as e:
                    self.task_service.display_error_message(f"Invalid date: {str(e)}")
                    self.console.print("[yellow]Continuing without due date...[/yellow]")

        # Update the task with all new values
        try:
            updated_task = self.task_service.update_task(
                task_id=task_id,
                title=new_title.strip(),
                description=new_description,
                priority=new_priority,
                categories=new_categories,
                due_date=new_due_date,
                due_time=new_due_time
            )

            if updated_task:
                # If updating all future instances of recurring task (T085 - User Story 5)
                if task.series_id and update_all_future:
                    try:
                        updated_count = self.task_service.recurring_service.update_series(
                            series_id=task.series_id,
                            update_future=True,
                            title=new_title.strip(),
                            description=new_description,
                            priority=new_priority,
                            categories=new_categories,
                            due_time=new_due_time
                        )
                        self.console.print(f"[green]Updated {updated_count} future instance(s) in the series.[/green]")
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Could not update future instances: {e}[/yellow]")

                self.task_service.save_to_file()
                self.task_service.display_success_message(f"Task {task_id} updated successfully!")
            else:
                self.task_service.display_error_message(f"Failed to update task {task_id}.")
        except ValueError as e:
            self.task_service.display_error_message(f"Failed to update task: {str(e)}")

    def _handle_delete(self):
        """Handle the delete command to remove a task."""
        self.task_service.rich_ui.display_info_message("Deleting a task:")

        try:
            task_id_str = Prompt.ask("Enter task ID to delete")
            task_id = int(task_id_str)
        except ValueError:
            self.task_service.display_error_message("Invalid task ID. Please enter a number.")
            return

        # Check if task exists
        task = self.task_service.get_by_id(task_id)
        if not task:
            self.task_service.display_error_message(f"Task with ID {task_id} not found.")
            return

        # Check if this is a recurring task (T086 - User Story 5)
        stop_all_future = False
        if task.series_id:
            self.console.print("\n[yellow]⚠ This is a recurring task.[/yellow]")
            delete_choice = Prompt.ask(
                "Delete scope",
                choices=["this", "future"],
                default="this"
            )
            stop_all_future = (delete_choice == "future")

            if stop_all_future:
                self.console.print("[cyan]Will stop the series and delete all future instances.[/cyan]")
            else:
                self.console.print("[cyan]Will delete only this instance.[/cyan]")

        self.task_service.rich_ui.display_info_message(f"Task to delete: {task.title}")

        confirm = Confirm.ask("Are you sure you want to delete this task?")

        if confirm:
            success = self.task_service.delete_task(task_id)

            if success:
                # If stopping all future instances of recurring task (T086 - User Story 5)
                if task.series_id and stop_all_future:
                    try:
                        deleted_count = self.task_service.recurring_service.stop_recurrence(
                            series_id=task.series_id,
                            delete_future=True
                        )
                        self.console.print(f"[green]Stopped series and deleted {deleted_count} future instance(s).[/green]")
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Could not stop series: {e}[/yellow]")

                self.task_service.display_success_message(f"Task {task_id} deleted successfully!")
            else:
                self.task_service.display_error_message(f"Failed to delete task {task_id}.")
        else:
            self.task_service.rich_ui.display_warning_message("Task deletion cancelled.")

    def _handle_complete(self):
        """Handle the complete command to toggle task completion status."""
        self.task_service.rich_ui.display_info_message("Toggle task completion:")

        try:
            task_id_str = Prompt.ask("Enter task ID to toggle completion status")
            task_id = int(task_id_str)
        except ValueError:
            self.task_service.display_error_message("Invalid task ID. Please enter a number.")
            return

        # Check if task exists
        task = self.task_service.get_by_id(task_id)
        if not task:
            self.task_service.display_error_message(f"Task with ID {task_id} not found.")
            return

        # Toggle completion status
        success = self.task_service.toggle_complete(task_id)

        if success:
            # Get updated task to show current status
            updated_task = self.task_service.get_by_id(task_id)
            new_status = updated_task.status.value
            self.task_service.display_success_message(f"Task {task_id} marked as {new_status}!")
        else:
            self.task_service.display_error_message(f"Failed to toggle completion status for task {task_id}.")

    def _handle_quit(self):
        """Handle the quit command to gracefully shut down the app."""
        self.task_service.rich_ui.display_info_message("Saving tasks and exiting...")
        self.task_service.save_to_file()

        # Stop reminder service if running (T073 - User Story 4)
        if self.reminder_service:
            self.console.print("[yellow]Stopping reminder service...[/yellow]")
            self.reminder_service.stop()

        self.task_service.display_success_message("Tasks saved successfully. Goodbye!")

    def _handle_stats(self):
        """Handle the stats command to display progress statistics."""
        self.task_service.display_progress_stats_enhanced()

    def _handle_reminders(self):
        """Handle the reminders command to display reminder service status (T074 - User Story 4)."""
        if not self.reminder_service:
            self.console.print("[yellow]Email reminder service is not available.[/yellow]")
            self.console.print("[dim]To enable reminders, add credentials.json to the project directory.[/dim]")
            return

        # Get status
        status = self.reminder_service.get_status()

        # Create status panel
        from rich.panel import Panel
        from rich.table import Table

        table = Table(show_header=False, box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Service Status", "🟢 Running" if status['running'] else "🔴 Stopped")
        table.add_row("Pending Reminders", str(status['pending_count']))
        table.add_row("Failed Reminders", str(status['failed_count']))
        table.add_row("Total Reminders", str(status['total_count']))

        panel = Panel(
            table,
            title="[bold cyan]Email Reminder Service Status[/bold cyan]",
            border_style="cyan"
        )

        self.console.print("\n", panel, "\n")

        # Show pending reminders if any
        if status['pending_count'] > 0:
            pending = self.reminder_service.get_pending_reminders()
            self.console.print(f"[cyan]Next {min(3, len(pending))} pending reminders:[/cyan]")
            for reminder in pending[:3]:
                task = self.task_service.get_by_id(reminder.task_id)
                if task:
                    scheduled_local = self.reminder_service.time_zone_service.to_local(
                        reminder.scheduled_time,
                        self.reminder_service.time_zone_service.get_user_timezone()
                    )
                    self.console.print(
                        f"  • Task #{task.id}: {task.title} - "
                        f"Reminder at {scheduled_local.strftime('%b %d, %Y %I:%M %p')}"
                    )

        # Show failed reminders if any
        if status['failed_count'] > 0:
            self.console.print(f"\n[yellow]⚠ {status['failed_count']} reminder(s) failed to send[/yellow]")
            self.console.print("[dim]A daily digest will be sent at 8:00 AM with failed reminders.[/dim]")

    def _handle_recurring_series(self):
        """Handle the recurring command to list and manage recurring series (T083 - User Story 5)."""
        from rich.panel import Panel
        from rich.table import Table

        # Get all recurring series from the recurring service
        series_list = list(self.task_service.recurring_service.series_registry.values())

        if not series_list:
            self.console.print("[yellow]No recurring task series found.[/yellow]")
            return

        # Create table
        table = Table(title="Recurring Task Series", show_header=True, header_style="bold cyan")
        table.add_column("Series ID", style="cyan", no_wrap=True)
        table.add_column("Pattern", style="green")
        table.add_column("Interval", style="yellow")
        table.add_column("Active", style="magenta")
        table.add_column("Completed", style="blue")
        table.add_column("Status", style="white")

        for series in series_list:
            status = "🟢 Active" if series.is_active else "🔴 Stopped"
            table.add_row(
                series.series_id[:8] + "...",
                series.recurrence_pattern,
                str(series.recurrence_interval),
                str(len(series.active_instance_ids)),
                str(len(series.completed_instance_ids)),
                status
            )

        self.console.print("\n", table, "\n")

        # Ask if user wants to stop a series (T084)
        if Confirm.ask("Do you want to stop a recurring series?", default=False):
            series_id_input = Prompt.ask("Enter series ID (first 8 characters are enough)")

            # Find matching series
            matching_series = None
            for series in series_list:
                if series.series_id.startswith(series_id_input):
                    matching_series = series
                    break

            if not matching_series:
                self.console.print("[red]Series not found.[/red]")
                return

            # Ask if user wants to delete future instances
            delete_future = Confirm.ask(
                "Delete all future instances? (No = just stop generating new ones)",
                default=False
            )

            try:
                deleted_count = self.task_service.recurring_service.stop_recurrence(
                    series_id=matching_series.series_id,
                    delete_future=delete_future
                )

                if delete_future:
                    self.console.print(f"[green]✓ Series stopped and {deleted_count} future instance(s) deleted.[/green]")
                else:
                    self.console.print("[green]✓ Series stopped. Existing instances preserved.[/green]")

            except Exception as e:
                self.console.print(f"[red]Error stopping series: {e}[/red]")

    def _handle_timezone(self):
        """Handle timezone configuration command (T102 - Phase 10)."""
        try:
            from ..utils.config_manager import ConfigManager
            import pytz

            config = ConfigManager()
            current_tz = config.get_time_zone()

            self.console.print(f"\n[bold cyan]Time Zone Configuration[/bold cyan]")
            self.console.print(f"Current time zone: [green]{current_tz}[/green]\n")

            change = Confirm.ask("Do you want to change the time zone?", default=False)

            if change:
                self.console.print("\n[yellow]Enter a valid time zone (e.g., America/New_York, Europe/London, Asia/Tokyo)[/yellow]")
                self.console.print("[dim]Common time zones:[/dim]")
                self.console.print("  - America/New_York (EST/EDT)")
                self.console.print("  - America/Los_Angeles (PST/PDT)")
                self.console.print("  - America/Chicago (CST/CDT)")
                self.console.print("  - Europe/London (GMT/BST)")
                self.console.print("  - Europe/Paris (CET/CEST)")
                self.console.print("  - Asia/Tokyo (JST)")
                self.console.print("  - Asia/Shanghai (CST)")
                self.console.print("  - Australia/Sydney (AEST/AEDT)\n")

                new_tz = Prompt.ask("Enter time zone", default=current_tz)

                if new_tz.strip():
                    try:
                        # Validate timezone
                        if new_tz not in pytz.all_timezones:
                            self.console.print(f"[red]✗ Invalid time zone: {new_tz}[/red]")
                            self.console.print("[yellow]Use a valid IANA time zone name (e.g., America/New_York)[/yellow]")
                            return

                        # Update config
                        config.set_time_zone(new_tz)
                        self.console.print(f"[green]✓ Time zone updated to: {new_tz}[/green]")
                        self.console.print("[yellow]Note: Restart the application for changes to take full effect.[/yellow]")

                    except ValueError as e:
                        self.console.print(f"[red]✗ Error: {e}[/red]")
                else:
                    self.console.print("[yellow]Time zone not changed.[/yellow]")

        except Exception as e:
            self.console.print(f"[red]Error managing time zone: {e}[/red]")

    def _handle_search(self):
        """Handle the search command to find tasks by keyword with scope selection (Phase 11 - Enhanced Features)."""
        self.task_service.rich_ui.display_info_message("Search tasks:")

        keyword = Prompt.ask("Enter search keyword")

        if not keyword or not keyword.strip():
            self.task_service.display_error_message("Search keyword cannot be empty.")
            return

        # Prompt for search scope (Phase 11 - Enhanced Features)
        self.console.print("\n[yellow]Search scope options:[/yellow]")
        self.console.print("  1. Title only")
        self.console.print("  2. Description only")
        self.console.print("  3. Both title and description (default)\n")

        scope_choice = Prompt.ask(
            "Select search scope",
            choices=["1", "2", "3"],
            default="3"
        )

        # Map choice to scope
        scope_map = {
            "1": "title",
            "2": "description",
            "3": "both"
        }
        scope = scope_map[scope_choice]

        # Get all tasks
        all_tasks = self.task_service.list_tasks()

        # Search tasks with scope
        try:
            results = self.search_service.search_tasks_with_scope(all_tasks, keyword.strip(), scope)

            if results:
                scope_text = {
                    "title": "in titles",
                    "description": "in descriptions",
                    "both": "in titles and descriptions"
                }
                self.task_service.rich_ui.display_success_message(
                    f"Found {len(results)} task(s) matching '{keyword}' {scope_text[scope]}:"
                )
                self.task_service.rich_ui.display_tasks(results)
            else:
                self.task_service.rich_ui.display_warning_message(
                    f"No tasks found matching '{keyword}' in selected scope."
                )
                self.console.print("\n[dim]Try different keywords, scope, or check your spelling.[/dim]\n")
        except ValueError as e:
            self.task_service.display_error_message(f"Search error: {str(e)}")

    def _handle_filter(self):
        """Handle the filter command to filter tasks by criteria."""
        self.task_service.rich_ui.display_info_message("Filter tasks:")

        # Get all tasks
        all_tasks = self.task_service.list_tasks()

        if not all_tasks:
            self.task_service.rich_ui.display_warning_message("No tasks to filter.")
            return

        # Ask for filter criteria
        self.console.print("\n[bold]Filter Options:[/bold]")
        self.console.print("1. Status (complete/incomplete)")
        self.console.print("2. Priority (high/medium/low)")
        self.console.print("3. Categories")
        self.console.print("4. All criteria")
        self.console.print("5. Cancel\n")

        choice = Prompt.ask("Select filter option", choices=["1", "2", "3", "4", "5"], default="5")

        if choice == "5":
            self.task_service.rich_ui.display_info_message("Filter cancelled.")
            return

        results = all_tasks

        # Filter by status
        if choice in ["1", "4"]:
            status_choice = Prompt.ask(
                "Filter by status",
                choices=["complete", "incomplete", "all"],
                default="all"
            )
            if status_choice != "all":
                results = self.filter_service.filter_tasks(results, status=status_choice)

        # Filter by priority
        if choice in ["2", "4"]:
            priority_choice = Prompt.ask(
                "Filter by priority",
                choices=["high", "medium", "low", "all"],
                default="all"
            )
            if priority_choice != "all":
                priority_map = {
                    "high": Priority.HIGH,
                    "medium": Priority.MEDIUM,
                    "low": Priority.LOW
                }
                results = self.filter_service.filter_tasks(
                    results,
                    priority=priority_map[priority_choice]
                )

        # Filter by categories
        if choice in ["3", "4"]:
            categories_input = Prompt.ask(
                "Enter categories (comma-separated, or press Enter to skip)",
                default=""
            )
            if categories_input.strip():
                categories = [cat.strip() for cat in categories_input.split(",") if cat.strip()]
                if categories:
                    match_logic = Prompt.ask(
                        "Match logic",
                        choices=["any", "all"],
                        default="any"
                    )
                    results = self.filter_service.filter_tasks(
                        results,
                        categories=categories,
                        category_match=match_logic
                    )

        # Display results
        if results:
            self.task_service.rich_ui.display_success_message(
                f"Found {len(results)} task(s) matching your criteria:"
            )
            self.task_service.rich_ui.display_tasks(results)
        else:
            self.task_service.rich_ui.display_warning_message(
                "No tasks found matching your criteria."
            )
            self.console.print("\n[dim]Try adjusting your filter criteria.[/dim]\n")

    def _handle_sort(self):
        """Handle the sort command to sort tasks by criteria."""
        self.task_service.rich_ui.display_info_message("Sort tasks:")

        # Get all tasks
        all_tasks = self.task_service.list_tasks()

        if not all_tasks:
            self.task_service.rich_ui.display_warning_message("No tasks to sort.")
            return

        # Ask for sort criteria
        self.console.print("\n[bold]Sort Options:[/bold]")
        self.console.print("1. Due Date (earliest first)")
        self.console.print("2. Priority (high to low)")
        self.console.print("3. Title (alphabetically)")
        self.console.print("4. Cancel\n")

        choice = Prompt.ask("Select sort option", choices=["1", "2", "3", "4"], default="4")

        if choice == "4":
            self.task_service.rich_ui.display_info_message("Sort cancelled.")
            return

        # Map choice to sort criteria
        sort_map = {
            "1": "due_date",
            "2": "priority",
            "3": "title"
        }

        sort_by = sort_map[choice]

        # Ask for secondary sort
        secondary = None
        if choice in ["1", "2"]:
            use_secondary = Confirm.ask("Apply secondary sort?", default=False)
            if use_secondary:
                if choice == "1":  # Due date primary
                    secondary_choice = Prompt.ask(
                        "Secondary sort",
                        choices=["priority", "title", "none"],
                        default="priority"
                    )
                else:  # Priority primary
                    secondary_choice = Prompt.ask(
                        "Secondary sort",
                        choices=["due_date", "title", "none"],
                        default="due_date"
                    )
                if secondary_choice != "none":
                    secondary = secondary_choice

        # Sort tasks
        try:
            sorted_tasks = self.sort_service.sort_tasks(all_tasks, sort_by, secondary)

            self.task_service.rich_ui.display_success_message(
                f"Tasks sorted by {sort_by.replace('_', ' ')}" +
                (f" (then by {secondary})" if secondary else "") + ":"
            )
            self.task_service.rich_ui.display_tasks(sorted_tasks)
        except ValueError as e:
            self.task_service.display_error_message(f"Sort failed: {str(e)}")

    def _handle_clear(self):
        """Handle the clear command to properly clear the terminal buffer (Phase 11 - Enhanced Features)."""
        try:
            from ..utils.terminal_utils import TerminalUtils

            terminal_utils = TerminalUtils()
            terminal_utils.clear_terminal()

            self.task_service.rich_ui.display_success_message("Terminal cleared successfully!")
        except RuntimeError as e:
            # Fallback to Rich console clear if platform-specific clearing fails
            self.console.clear()
            self.task_service.rich_ui.display_warning_message(
                f"Platform-specific clear failed ({str(e)}). Used fallback method."
            )

    def _handle_delete_all(self):
        """Handle the delete all command to remove all tasks with confirmation (Phase 9 - User Story 5)."""
        # Check if any tasks exist
        if not self.task_service.tasks:
            self.task_service.rich_ui.display_info_message("No tasks to delete.")
            return

        # Display warning and confirmation prompt
        self.console.print("\n[bold red]⚠️  WARNING: Delete All Tasks[/bold red]")
        self.console.print("This will permanently delete ALL tasks and reset the ID counter to 1.")
        self.console.print("This action cannot be undone.\n")

        # Prompt for confirmation
        confirmed = Confirm.ask("Are you sure you want to continue?", default=False)

        if not confirmed:
            self.task_service.rich_ui.display_info_message("Delete all cancelled. No changes made.")
            return

        # Delete all tasks
        result = self.task_service.delete_all()

        if result:
            # Reset ID counter
            self.task_service.id_manager.reset_counter()

            # Save to storage
            self.task_service.save_to_file()

            # Display success message
            self.task_service.rich_ui.display_success_message("✓ All tasks deleted successfully")
            self.console.print("[yellow]ID counter reset to 1[/yellow]\n")
        else:
            self.task_service.display_error_message("Failed to delete tasks.")

    def _handle_help(self):
        """Display help information with all available commands."""
        # Use the enhanced menu function to display help
        options = [
            "Add a new task",
            "View all tasks",
            "Update a task",
            "Delete a task",
            "Toggle task completion status",
            "Search tasks by keyword",
            "Filter tasks by criteria",
            "Sort tasks by criteria",
            "Clear the console",
            "View task statistics",
            "Show this help message",
            "Exit the application"
        ]

        menu = create_styled_menu([
            "add or a - Add a new task",
            "view or v - View all tasks",
            "update or u - Update a task",
            "delete or d - Delete a task",
            "delete all or dela - Delete all tasks with confirmation",
            "complete or c - Toggle task completion status",
            "search or find or f - Search tasks by keyword",
            "filter or fl - Filter tasks by criteria",
            "sort or sr - Sort tasks by criteria",
            "clear or clr - Clear the console",
            "stats or s - View task statistics",
            "reminders or rem - View email reminder service status",
            "recurring or rec - List and manage recurring task series",
            "timezone or tz - Configure time zone settings",
            "help or h - Show this help message",
            "quit or q - Exit the application"
        ], "Available Commands")

        self.console.print("\n", menu, "\n")


def main():
    """Main entry point for the application."""
    cli = TickListoCLI()
    try:
        cli.run()
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()