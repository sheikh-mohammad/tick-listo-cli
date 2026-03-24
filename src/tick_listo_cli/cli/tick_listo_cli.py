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
        has_due_date = Confirm.ask("Add a due date?", default=False)
        if has_due_date:
            due_date_input = Prompt.ask(
                "Enter due date (MM/DD/YYYY, YYYY-MM-DD, or 'tomorrow', 'next week', etc.)"
            ).strip()

            if due_date_input:
                try:
                    from ..services.validation_service import validate_date_input
                    due_date = validate_date_input(due_date_input)
                except ValueError as e:
                    self.task_service.display_error_message(f"Invalid date: {str(e)}")
                    self.console.print("[yellow]Continuing without due date...[/yellow]")

        # Add the task with all required fields
        try:
            task = self.task_service.add_task(
                title.strip(),
                description,
                priority=priority,
                categories=categories,
                due_date=due_date
            )
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

        # Display current values (Phase 11 - Enhanced Features)
        self.console.print("\n[bold cyan]Current Task Details:[/bold cyan]")
        self.console.print(f"  Title: {task.title}")
        self.console.print(f"  Description: {task.description}")
        self.console.print(f"  Priority: {task.priority.value}")
        self.console.print(f"  Categories: {', '.join(task.categories)}")
        self.console.print(f"  Due Date: {task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'}")
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
        current_due_date_str = task.due_date.strftime('%Y-%m-%d') if task.due_date else ""

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
                due_date=new_due_date
            )

            if updated_task:
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

        self.task_service.rich_ui.display_info_message(f"Task to delete: {task.title}")

        confirm = Confirm.ask("Are you sure you want to delete this task?")

        if confirm:
            success = self.task_service.delete_task(task_id)

            if success:
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
        self.task_service.display_success_message("Tasks saved successfully. Goodbye!")

    def _handle_stats(self):
        """Handle the stats command to display progress statistics."""
        self.task_service.display_progress_stats_enhanced()

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