# Feature Specification: Intermediate Ticklisto Enhancements

**Feature Branch**: `002-intermediate-tick-listo-cli-enhancements`
**Created**: 2026-01-31
**Updated**: 2026-02-03
**Status**: Completed
**Input**: Enhanced intermediate ticklisto features including:
- Required priority level (high/medium/low) and categories during task creation
- Delete all tasks command with "dela" alias and confirmation prompt
- Improved clear command that properly clears terminal buffer (not just scrolls)
- Search & filter by keyword, status, priority, and date
- Sort tasks by due date, priority, or alphabetically

## **Intermediate Level (Organization & Usability)**

Add these to make the app feel polished and practical:

1. **Required Priority & Categories** – Task creation MUST require priority level (high/medium/low) and at least one category tag. Users can assign multiple categories (work/home/personal or custom).
2. **Search & Filter** – Search by keyword; filter by status, priority, and date with flexible date parsing
3. **Sort Tasks** – Reorder by due date (primary), priority (secondary), or alphabetically
4. **Clear Command** – Properly clear terminal screen and buffer (not just scroll) using "clear" or "clr" alias
5. **Delete All Command** – Delete all tasks using "delete all" or "dela" alias with confirmation prompt

Also update README.md with these new features

this is feature 002

## **Requirements**

* All existing Basic Level features (Add, Delete, Update, View, Mark Complete) are implemented do not change them, add new code
* Enhance the CLI interface with Rich library for comprehensive beautification
* Maintain backward compatibility with existing functionality
* Follow clean code principles and proper Python project structure

## **Technology Stack**

- UV for package management
- UV for dependency management
- Python 3.13+ for console application development
- Rich for beautiful CLI interfaces and terminal formatting
- GitHub for deployment
- Git for Version Control System
- JSON file storage (ticklisto_data.json) for task persistence

### Infrastructure & Deployment
- Console-based user interface for Phase I with enhanced Rich formatting
- Local development environment

## **Deliverables**

* /src folder with Python source code incorporating Rich enhancements
* README.md with setup instructions
* Working console application demonstrating:
* Adding tasks with title and description
* Listing all tasks with status indicators using styled tables
* Updating task details
* Deleting tasks by ID
* Marking tasks as complete/incomplete
* Enhanced visual interface with all Rich features implemented
* **Required Priority & Categories**: Task creation MUST prompt for and require priority level (high/medium/low) and at least one category tag (predefined: work/home/personal, or custom). Multiple categories can be assigned.
* **Search & Filter**: Search by keyword; filter by status, priority, and date with flexible date parsing and natural language support
* **Sort Tasks**: Reorder by due date (primary), priority (secondary), or alphabetically
* **Clear Command**: Properly clear terminal screen and buffer using "clear" or "clr" alias, preventing scroll-back to previous commands
* **Delete All Command**: Delete all tasks using "delete all" or "dela" alias with confirmation prompt to prevent accidental data loss

## Clarifications

### Session 2026-01-31

- Q: What specific date range filter options should be available for the task filtering functionality? → A: Date filters should include: before specific date, after specific date, between two dates, and relative dates (today, this week, this month)
- Q: When sorting tasks by priority, what should be the order of priority levels? → A: When sorting by priority, tasks should be ordered as: High priority first, then Medium, then Low
- Q: Should the "clear" command affect the stored tasks or only the visual interface? → A: The "clear" command should only clear the console interface/terminal display, leaving all tasks intact in memory
- Q: How should the application prioritize sorting when a task has multiple conflicting attributes (e.g., a past-due date but low priority)? → A: Prioritize by due date first, then by priority.

### Session 2026-02-01

- Q: How should tasks without due dates be handled when sorting by due date? → A: Tasks without due dates are grouped separately in a "No Due Date" section
- Q: Can a task be assigned multiple category tags simultaneously (e.g., both "work" AND "home"), or is it limited to a single category per task? → A: Multiple categories per task (a task can have work AND home tags simultaneously)
- Q: What date format should users use when inputting dates for task due dates and date filters? → A: Flexible parsing supporting multiple formats (MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD) with natural language support for relative dates (today, tomorrow, next week, next Monday, in 3 days)
- Q: Should the search functionality be case-sensitive or case-insensitive when matching keywords in task titles and descriptions? → A: Case-insensitive (searching "work" matches "Work", "WORK", "work")
- Q: When a user applies multiple category filters simultaneously (e.g., selects both "work" AND "home" as filter criteria), which tasks should be displayed? → A: Provide a toggle allowing user to switch between OR and AND logic
- Q: Should the system validate priority and category values when users input them, or accept any string value? → A: Strict validation for priority (only accept high/medium/low), flexible validation for categories (accept any string but suggest predefined values work/home/personal as defaults/autocomplete)

### Session 2026-02-03

- Q: How should tasks be uniquely identified in the system? → A: Auto-incrementing integer IDs (1, 2, 3, ...)
- Q: How should task data be persisted? → A: JSON file persistence (ticklisto_data.json) - data survives application restarts
- Q: After deleting a task, should its ID be reused for new tasks? → A: Never reuse IDs during normal operation (counter always increments, deleted IDs stay retired). However, reset ID counter to 1 after "delete all" command for fresh start.
- Q: When updating a task, can users modify individual fields or must they re-enter all fields? → A: Full re-entry - user must provide all fields again when updating
- Q: When searching by keyword, should tasks match if the keyword appears in title OR description, or must it appear in BOTH? → A: Separate search fields - user specifies whether to search title, description, or both

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Task Priorities & Categories (Priority: P1)

As a user, I want to assign priority levels (high/medium/low) and one or more category tags (work/home/personal) to my tasks so that I can better organize and prioritize my work.

**Why this priority**: Essential for organizing tasks by importance and context, which is fundamental to productivity management.

**Independent Test**: User can create a task with priority level and category tag, then view it in the task list with visual indicators for priority and category.

**Acceptance Scenarios**:

1. **Given** I am on the task creation screen, **When** I add a task with high priority and "work" category, **Then** the task is saved with these attributes and displays appropriately in the list.
2. **Given** I have existing tasks without priorities/categories, **When** I update a task to add priority and category, **Then** the task is updated with the new attributes and displays correctly in the list.
3. **Given** I am creating or editing a task, **When** I assign multiple category tags (e.g., both "work" and "home"), **Then** the task is saved with all assigned categories and displays all tags in the list.
4. **Given** I am creating or editing a task, **When** I enter an invalid priority value (not high/medium/low), **Then** the system displays an error message and does not save the task until a valid priority is provided.
5. **Given** I am creating or editing a task, **When** I enter a custom category tag (not in the predefined list), **Then** the system accepts the custom category and saves it with the task, while still suggesting predefined categories via autocomplete.

---

### User Story 2 - Search & Filter Tasks (Priority: P1)

As a user, I want to search my tasks by keyword with the ability to specify search scope (title, description, or both) and filter them by status, priority, and date so that I can quickly find specific tasks among many.

**Why this priority**: Critical for usability when managing a large number of tasks, allowing users to efficiently locate what they need.

**Independent Test**: User can enter search terms, specify search scope, and apply filters to narrow down the task list to relevant items only.

**Acceptance Scenarios**:

1. **Given** I have multiple tasks with various titles and descriptions, **When** I enter a keyword and specify to search in title only, **Then** only tasks containing that keyword in the title are displayed (case-insensitive matching).
2. **Given** I have multiple tasks with various titles and descriptions, **When** I enter a keyword and specify to search in description only, **Then** only tasks containing that keyword in the description are displayed (case-insensitive matching).
3. **Given** I have multiple tasks with various titles and descriptions, **When** I enter a keyword and specify to search in both fields, **Then** only tasks containing that keyword in either title or description are displayed (case-insensitive matching).
4. **Given** I have tasks with different statuses, priorities, and due dates, **When** I apply filters for specific criteria, **Then** only tasks matching those criteria are displayed.
5. **Given** I want to filter tasks by date, **When** I enter a date in any supported format (MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD) or use natural language (today, tomorrow, next week, next Monday, in 3 days), **Then** the system correctly parses the date and filters tasks accordingly.
6. **Given** I select multiple category filters, **When** I toggle between OR and AND logic, **Then** the displayed tasks update to show either tasks matching ANY selected category (OR) or tasks matching ALL selected categories (AND).

---

### User Story 3 - Sort Tasks (Priority: P2)

As a user, I want to sort my tasks primarily by due date (earliest first) and secondarily by priority (highest first) so that I can efficiently manage my workflow.

**Why this priority**: Improves usability by allowing users to view tasks in their preferred organization method, enhancing productivity.

**Independent Test**: User can select sorting options and the task list reorders accordingly based on the selected criteria.

**Acceptance Scenarios**:

1. **Given** I have tasks with different due dates, **When** I select "Sort by Due Date", **Then** tasks are arranged chronologically from nearest to furthest due date, with tasks without due dates grouped separately in a "No Due Date" section.
2. **Given** I have tasks with different priority levels, **When** I select "Sort by Priority", **Then** tasks are arranged from high to low priority.
3. **Given** I have tasks with the same due date, **When** I select "Sort by Priority", **Then** tasks are arranged from high to low priority within that due date group.

---

### User Story 4 - Clear Interactive Session (Priority: P2)

As a user, I want to properly clear the terminal screen and command history so that I can start with a completely clean interface without being able to scroll back to previous commands.

**Why this priority**: Enhances user experience by providing a truly clean slate when the interface becomes cluttered, improving focus and reducing visual clutter.

**Independent Test**: User can execute a clear command that completely clears the terminal buffer, preventing scroll-back to previous commands.

**Acceptance Scenarios**:

1. **Given** I have executed several commands in the interactive session, **When** I run the "clear" command (with alias "clr"), **Then** the terminal screen is completely cleared and I cannot scroll up to see previous commands.
2. **Given** I have a cluttered terminal with many previous commands, **When** I execute the clear command, **Then** the terminal buffer is reset and the cursor is positioned at the top of a clean screen.

---

### User Story 5 - Delete All Tasks (Priority: P2)

As a user, I want to delete all tasks at once so that I can quickly start fresh without manually deleting tasks one by one.

**Why this priority**: Provides efficiency when users need to clear their entire task list, such as starting a new project phase or cleaning up test data.

**Independent Test**: User can execute a delete all command that removes all tasks from storage.

**Acceptance Scenarios**:

1. **Given** I have multiple tasks in my task list, **When** I run the "delete all" command (with alias "dela"), **Then** all tasks are permanently removed from storage and the task list is empty.
2. **Given** I have no tasks in my task list, **When** I run the "delete all" command, **Then** the system displays a message indicating there are no tasks to delete.
3. **Given** I am about to delete all tasks, **When** I execute the delete all command, **Then** the system prompts me for confirmation before proceeding with the deletion to prevent accidental data loss.

---

### User Story 6 - Required Priority and Categories During Task Creation (Priority: P1)

As a user, I want to be prompted for priority level and categories when creating a task so that all my tasks are properly organized from the start.

**Why this priority**: Ensures consistent task organization by making priority and categorization mandatory, preventing tasks from being created without proper classification.

**Independent Test**: User cannot create a task without specifying priority and at least one category.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I enter the task title and description, **Then** the system prompts me to select a priority level (high/medium/low) before proceeding.
2. **Given** I am creating a new task and have selected a priority, **When** the system prompts for categories, **Then** I can select one or multiple categories from predefined options or enter custom categories.
3. **Given** I am creating a new task, **When** I attempt to skip the priority or category selection, **Then** the system displays an error message and requires me to provide these values before the task can be saved.
4. **Given** I am creating a new task, **When** I am prompted for categories, **Then** I can select multiple categories (e.g., both "work" and "home") and all selected categories are saved with the task.

---

### Edge Cases

- What happens when a task has both a past due date and high priority? (Clarified: Past due date takes precedence, then sorted by priority).
- Tasks without due dates when sorting by due date (Clarified: Grouped separately in a "No Due Date" section).
- How does filtering by category work when a task has multiple categories? (Clarified: User can toggle between OR logic - task matches ANY selected category, or AND logic - task matches ALL selected categories).
- What happens when a user enters an invalid or ambiguous date format? (Clarified: System should provide helpful error message suggesting valid formats and examples).
- What happens when a user enters an invalid priority value? (Clarified: System strictly validates and rejects invalid priority values with error message).
- How does the system handle custom category tags not in the predefined list? (Clarified: System accepts any string value for categories while suggesting predefined values via autocomplete).
- How does the system handle searching for special characters or symbols in task titles/descriptions? (Search is case-insensitive and matches literal characters).
- What occurs when no tasks match the applied search/filter criteria? (System should display a clear "No tasks found" message with suggestions to adjust filters).
- What happens when a user executes "delete all" command accidentally? (System must prompt for confirmation before deleting all tasks to prevent accidental data loss).
- What happens when "delete all" is executed on an empty task list? (System displays a message indicating there are no tasks to delete).
- How does the clear command ensure previous commands cannot be scrolled back to? (System must clear the terminal buffer completely, not just scroll down, using platform-specific terminal clearing mechanisms).
- What happens when a user tries to create a task without providing priority or categories? (System must block task creation and display an error message requiring these mandatory fields).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST require users to specify a priority level (high/medium/low) when creating a new task. Task creation MUST NOT proceed without a valid priority selection. System MUST strictly validate priority input and only accept the predefined values (high, medium, low), displaying an error message for invalid input.
- **FR-002**: System MUST require users to specify at least one category tag when creating a new task. Task creation MUST NOT proceed without at least one category. System MUST use flexible validation: accept any string value for categories while suggesting predefined values (work/home/personal) as defaults with autocomplete functionality. Users MUST be able to select multiple categories during task creation.
- **FR-003**: System MUST allow users to update priority levels and category tags for existing tasks during editing operations. When updating a task, users MUST re-enter all task fields (title, description, priority, categories, due date).
- **FR-004**: System MUST display priority and category information visually in the task list using Rich formatting
- **FR-005**: System MUST provide a search functionality that filters tasks by keyword. Users MUST be able to specify the search scope: title only, description only, or both fields. Search MUST be case-insensitive.
- **FR-006**: System MUST provide filter options for task status (completed/incomplete), priority, and date range. Date inputs MUST support flexible parsing of multiple formats (MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD) and natural language expressions (today, tomorrow, next week, next Monday, in 3 days). When filtering by multiple categories, system MUST provide a toggle to switch between OR logic (match ANY selected category) and AND logic (match ALL selected categories).
- **FR-007**: System MUST provide sorting functionality. The default and primary sort order MUST be by due date (earliest first), with secondary sorting by priority (high first) for tasks with the same due date. Tasks without due dates MUST be grouped separately in a "No Due Date" section. Alphabetical sorting MUST also be available as an option.
- **FR-008**: System MUST provide a "clear" command with alias "clr" that completely clears the terminal screen and buffer, preventing users from scrolling back to view previous commands. The clear operation MUST use platform-specific terminal clearing mechanisms to ensure proper buffer reset.
- **FR-009**: System MUST provide a "delete all" command with alias "dela" that removes all tasks from storage. The command MUST prompt for user confirmation before executing the deletion to prevent accidental data loss. If no tasks exist, the system MUST display an appropriate message. After successful deletion of all tasks, the ID counter MUST reset to 1 for fresh numbering.
- **FR-010**: System MUST maintain backward compatibility with existing basic task operations (add, delete, update, view, mark complete)
- **FR-011**: System MUST persist priority and category information in the in-memory storage
- **FR-012**: System MUST update the README.md documentation to include instructions for the new features

### Key Entities

- **Task**: Represents a user task with:
  - **ID**: Auto-incrementing integer (1, 2, 3, ...) for unique identification
  - **Title**: Task name/summary
  - **Description**: Detailed task information
  - **Status**: completed/incomplete
  - **Priority**: Strictly validated (high/medium/low only)
  - **Categories**: List of one or more strings (predefined suggestions: work/home/personal, but accepts any custom string)
  - **Due Date**: Optional date field
- **Filter**: Represents criteria to narrow down task lists based on status, priority, date, or keyword search
- **SortCriteria**: Represents parameters for ordering tasks (due date, priority, alphabetical)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users must specify priority and at least one category when creating tasks with 100% enforcement rate
- **SC-002**: Priority and category assignment completes with visual feedback in under 2 seconds
- **SC-003**: Search functionality returns relevant results within 500ms for up to 1000 tasks
- **SC-004**: Filtering operations complete and update the display within 300ms for up to 1000 tasks
- **SC-005**: Sorting operations complete and update the display within 500ms for up to 1000 tasks
- **SC-006**: Clear command completely clears terminal buffer 100% of the time, preventing scroll-back to previous commands
- **SC-007**: Delete all command removes all tasks with confirmation prompt, achieving 100% success rate with zero accidental deletions without confirmation
- **SC-008**: All existing basic task operations continue to function without regression (100% backward compatibility)
- **SC-009**: Updated README.md documentation covers all new features with examples and usage instructions