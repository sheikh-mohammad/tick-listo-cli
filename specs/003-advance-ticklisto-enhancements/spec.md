# Feature Specification: Advanced Ticklisto Enhancements

**Feature Branch**: `003-advance-ticklisto-enhancements`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Advanced Level (Intelligent Features) - Add recurring tasks with auto-rescheduling, due dates with time reminders, and Gmail notifications. Task creation must support optional recurring task configuration. Users can assign due date and time. All reminders sent via Gmail API to haji08307@gmail.com using google-api-python-client, google-auth, and google-auth-oauthlib libraries. Credentials (token.json and credentials.json) are already added. Update README.md with new features. This is feature 003 on branch 003-advance-ticklisto-enhancements."

## Clarifications

### Session 2026-02-08

- Q: How should the system handle Gmail API rate limiting when multiple reminders are due simultaneously? → A: Queue with exponential backoff + daily digest (queue failed reminders, retry with exponential backoff max 3 attempts, send daily digest email if individual reminders fail)
- Q: When a recurring task is marked complete BEFORE its due date, how should the next instance be scheduled? → A: From original due date (next instance uses original due date + interval to maintain consistent schedule)
- Q: How should the system handle time zones for due dates and reminders? → A: User-configurable time zone (allow user to set preferred time zone separate from system)
- Q: What implementation approach should the background reminder service use? → A: Startup-based reminder checking (application checks for pending reminders on startup and sends them; designed for deployment on Hugging Face Spaces with continuous running)
- Q: The spec mentions 'custom' recurrence patterns. What level of customization should be supported? → A: Interval + specific weekdays (support interval multiplier and specific days of week like Mon/Wed/Fri)
- Q: How frequently should the application check for pending reminders during continuous operation on Hugging Face Spaces? → A: Every 1 minute (most responsive for time-sensitive reminders, minimal performance impact)
- Q: When should the daily digest email be sent if individual reminders fail due to rate limiting? → A: 8:00 AM user's time zone (standard morning digest time when users check email)
- Q: Should users be able to set multiple reminder times for a single task (e.g., 1 day before AND 1 hour before)? → A: Yes, multiple reminders per task (maximum flexibility, aligns with User Story 6 P3 feature)
- Q: How should users configure their preferred time zone for the application? → A: Global setting in config file (simple one-time configuration stored in preferences)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Due Dates with Time Support (Priority: P1)

As a user, I want to set specific due dates and times for my tasks so that I can schedule work with precise deadlines and receive timely reminders.

**Why this priority**: Foundation for time-based features; enables precise scheduling which is essential for effective task management and reminder functionality.

**Independent Test**: User can create a task with a specific date and time (e.g., "2026-02-15 14:30"), view it in the task list with the time displayed, and the system stores both date and time components accurately.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I choose to add a due date and time, **Then** the system prompts me to enter both date and time, and stores them accurately.
2. **Given** I am creating a task, **When** I enter a due date with time (e.g., "tomorrow at 2pm", "2026-02-15 14:30"), **Then** the system parses and stores both components correctly.
3. **Given** I have tasks with due times, **When** I view the task list, **Then** tasks display both date and time in a clear format (e.g., "Feb 15, 2026 at 2:30 PM").
4. **Given** I am updating a task, **When** I modify the due date and time, **Then** the system updates both components and reflects the changes immediately.
5. **Given** I have tasks with different due times on the same date, **When** I sort by due date, **Then** tasks are ordered by date first, then by time within the same date.

---

### User Story 2 - Recurring Tasks with Auto-Rescheduling (Priority: P1)

As a user, I want to create recurring tasks that automatically reschedule themselves when completed so that I don't have to manually recreate repetitive tasks like weekly meetings or daily reviews.

**Why this priority**: Core feature that significantly reduces manual work for repetitive tasks; essential for productivity and the primary value proposition of this feature set.

**Independent Test**: User can create a task with recurrence pattern (daily, weekly, monthly), mark it complete, and the system automatically creates the next instance with the appropriate due date.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I choose to make it recurring, **Then** the system prompts me to select a recurrence pattern (daily, weekly, bi-weekly, monthly, yearly, custom).
2. **Given** I have a recurring task with "weekly" pattern, **When** I mark it as complete (even before the due date), **Then** the system automatically creates a new instance with the due date set to one week from the original due date (not from completion date).
3. **Given** I have a recurring task, **When** I view the task details, **Then** the system displays the recurrence pattern clearly (e.g., "Repeats: Every week on Monday").
4. **Given** I have a recurring task, **When** I update it, **Then** the system asks whether to update only this instance or all future instances.
5. **Given** I have a recurring task, **When** I delete it, **Then** the system asks whether to delete only this instance or stop all future recurrences.
6. **Given** I create a recurring task without a due date, **When** I mark it complete, **Then** the system creates the next instance with the due date calculated from the completion date.

---

### User Story 3 - Email Reminders via Gmail API (Priority: P1)

As a user, I want to receive email reminders for upcoming tasks so that I don't miss important deadlines even when I'm not actively using the application.

**Why this priority**: Critical for ensuring users stay on top of their tasks; provides value beyond the CLI interface by reaching users wherever they check email.

**Independent Test**: User creates a task with a due date and time, and the system sends an email reminder to haji08307@gmail.com at the appropriate time before the deadline.

**Acceptance Scenarios**:

1. **Given** I have a task with a due date and time, **When** the reminder time arrives (default: 1 hour before due time), **Then** the system sends an email reminder to haji08307@gmail.com with task details.
2. **Given** I am creating a task with a due date, **When** I configure reminder settings, **Then** I can choose when to receive reminders (e.g., 15 minutes, 1 hour, 1 day before).
3. **Given** I have multiple tasks due at different times, **When** reminder times arrive, **Then** the system sends separate email reminders for each task at the appropriate times.
4. **Given** I have a recurring task, **When** each instance's reminder time arrives, **Then** the system sends a reminder for that specific instance.
5. **Given** the Gmail API authentication fails, **When** the system attempts to send a reminder, **Then** the system logs the error and displays a warning message without crashing.
6. **Given** I mark a task as complete, **When** the task had pending reminders, **Then** the system cancels those reminders and does not send emails for completed tasks.

---

### User Story 4 - Startup Reminder Checking (Priority: P1)

As a user, I want the application to check for pending reminders on startup and send them immediately so that I receive notifications when the application is running on Hugging Face Spaces.

**Why this priority**: Essential for the deployment model on Hugging Face Spaces where the application runs continuously; ensures reminders are sent reliably without requiring a separate background service.

**Independent Test**: User starts the application, and the system immediately checks all tasks for pending reminders (reminders that should have been sent) and sends them via email.

**Acceptance Scenarios**:

1. **Given** the application starts up, **When** there are tasks with reminders due in the past or within the next check interval, **Then** the system immediately sends those reminder emails.
2. **Given** the application is running on Hugging Face Spaces, **When** tasks are added or updated with new reminder times, **Then** the system schedules those reminders for the next check cycle.
3. **Given** the application is running, **When** a reminder time arrives, **Then** the system sends the email reminder within 2 minutes of the scheduled time.
4. **Given** the application restarts, **When** there are overdue reminders (reminders that should have been sent while the app was not running), **Then** the system sends those reminders immediately on startup.
5. **Given** the application is running continuously, **When** I check the system status, **Then** I can see when the next reminder check will occur and how many reminders are pending.

---

### User Story 5 - Recurring Task Management (Priority: P2)

As a user, I want to view, edit, and manage my recurring tasks as a series so that I can make changes to future occurrences without affecting past instances.

**Why this priority**: Important for managing recurring tasks effectively, but basic recurrence functionality (P1) provides core value; this enhances the management experience.

**Independent Test**: User can view all instances of a recurring task series, edit future instances, and stop recurrence without deleting past instances.

**Acceptance Scenarios**:

1. **Given** I have a recurring task series, **When** I view the task list, **Then** I can see which tasks are part of a recurring series with a visual indicator.
2. **Given** I select a recurring task, **When** I choose to edit it, **Then** the system asks whether to update "This instance only" or "This and all future instances".
3. **Given** I edit a recurring task and choose "This and all future instances", **When** I save changes, **Then** all future instances are updated while past completed instances remain unchanged.
4. **Given** I have a recurring task series, **When** I choose to stop recurrence, **Then** the system stops creating new instances but preserves existing instances.
5. **Given** I have a recurring task, **When** I view its details, **Then** I can see the recurrence pattern, next scheduled date, and history of completed instances.

---

### User Story 6 - Flexible Reminder Configuration (Priority: P3)

As a user, I want to customize reminder timing and frequency for individual tasks so that I can receive notifications that match the importance and urgency of each task.

**Why this priority**: Nice-to-have customization that enhances user experience; default reminder settings (P1) provide sufficient functionality for most use cases.

**Independent Test**: User can set multiple reminders for a single task (e.g., 1 day before, 1 hour before) and customize reminder timing per task.

**Acceptance Scenarios**:

1. **Given** I am creating or editing a task, **When** I configure reminders, **Then** I can add multiple reminder times (e.g., 1 day before, 1 hour before, 15 minutes before) for the same task.
2. **Given** I have a task with multiple reminders, **When** each reminder time arrives, **Then** the system sends separate email notifications at each configured time.
3. **Given** I am configuring reminders, **When** I set custom reminder times, **Then** I can specify exact times (e.g., "remind me at 9:00 AM on the day before").
4. **Given** I have default reminder preferences, **When** I create a new task with a due date, **Then** the system automatically applies my default reminder settings unless I customize them.

---

### User Story 7 - Reminder Email Content (Priority: P3)

As a user, I want reminder emails to contain comprehensive task information so that I can understand what needs to be done without opening the CLI application.

**Why this priority**: Improves user experience but not essential for core functionality; basic reminder emails (P1) provide sufficient value.

**Independent Test**: User receives a reminder email that includes task title, description, due date/time, priority, categories, and a summary of what needs to be done.

**Acceptance Scenarios**:

1. **Given** I receive a reminder email, **When** I open it, **Then** I see the task title, description, due date/time, priority level, and categories clearly formatted.
2. **Given** I receive a reminder email for a recurring task, **When** I open it, **Then** the email indicates it's a recurring task and shows the recurrence pattern.
3. **Given** I receive a reminder email, **When** the task is high priority, **Then** the email subject line includes a priority indicator (e.g., "[HIGH PRIORITY]").
4. **Given** I receive a reminder email, **When** I read it, **Then** the email includes a clear subject line like "Reminder: [Task Title] due in 1 hour".

---

### Edge Cases

- What happens when a user creates a recurring task with an end date and that date is reached? (System stops creating new instances after the end date)
- How does the system handle recurring tasks when the calculated next due date falls on a date that doesn't exist (e.g., February 30)? (System adjusts to the last valid day of the month)
- What occurs when the Gmail API rate limit is exceeded? (System queues reminders and retries with exponential backoff max 3 attempts; if individual reminders continue to fail, system sends a daily digest email summarizing all pending reminders)
- How does the system handle time zones for due dates and reminders? (Users can configure their preferred time zone separate from system time zone; stores timestamps in UTC internally; displays times in user's configured time zone)
- What happens when a user marks a recurring task complete before its due date? (System creates next instance based on original due date + interval, not completion date, to maintain consistent schedule)
- How does the system handle reminder emails when the user is offline or the network is unavailable? (Queues reminders and sends when connection is restored; logs failures after 3 retry attempts)
- What occurs when token.json expires or becomes invalid? (System displays clear error message with instructions to re-authenticate; reminders are queued until authentication is restored)
- How does the system handle very frequent recurring tasks (e.g., every hour)? (Supports minimum recurrence interval of 1 hour; warns user about potential email volume)
- What happens when a user deletes a recurring task that has pending reminders? (System cancels all pending reminders for that task series)
- How does the system handle tasks with due times but no due date? (Requires due date when time is specified; prompts user to provide date)
- What occurs when multiple tasks have reminders scheduled for the exact same time? (System sends individual emails for each task sequentially; with 1-minute check intervals, all reminders within the same minute are processed and sent)
- How does the system handle daylight saving time transitions for recurring tasks? (Maintains the same local time across DST transitions; adjusts UTC timestamp accordingly)
- What happens when a task has multiple reminders configured (e.g., 1 day before, 1 hour before)? (System sends separate emails at each configured reminder time; each reminder is tracked independently with its own retry logic)
- How does the system handle the daily digest if no reminders failed? (No digest email is sent; digest only sent when reminders have failed after 3 retry attempts)
- What occurs if the user changes their time zone configuration? (All future reminders and displays use the new time zone; existing scheduled reminders are recalculated based on the new time zone; past timestamps remain unchanged)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support adding time component to task due dates in addition to the date. Time input MUST support multiple formats including 24-hour (14:30), 12-hour with AM/PM (2:30 PM), and natural language (2pm, 2:30pm).
- **FR-002**: System MUST display due dates with time in a consistent, readable format (e.g., "Feb 15, 2026 at 2:30 PM") throughout the interface.
- **FR-003**: System MUST support creating recurring tasks with the following patterns: daily, weekly, bi-weekly, monthly, yearly, and custom intervals. Custom patterns MUST support interval multipliers (e.g., every 3 days, every 2 weeks) and specific weekdays (e.g., Mon/Wed/Fri, weekdays only). Recurrence configuration MUST be optional during task creation.
- **FR-004**: System MUST automatically create the next instance of a recurring task when the current instance is marked as complete. The new instance MUST have the same title, description, priority, categories, and recurrence pattern. When a task is completed before its due date, the next due date MUST be calculated from the original due date + recurrence interval (not from completion date) to maintain consistent scheduling.
- **FR-005**: System MUST allow users to specify whether to update/delete only the current instance or all future instances of a recurring task series.
- **FR-006**: System MUST send email reminders to haji08307@gmail.com using the Gmail API (google-api-python-client, google-auth, google-auth-oauthlib) at configured times before task due dates.
- **FR-007**: System MUST support configurable reminder timing with default of 1 hour before due time. Users MUST be able to set multiple reminder times per task (e.g., 1 day before, 1 hour before, 15 minutes before) with each reminder sent as a separate email at the configured time.
- **FR-008**: System MUST authenticate with Gmail API using existing credentials (token.json and credentials.json) and handle authentication errors gracefully with clear error messages.
- **FR-009**: System MUST cancel pending reminders when a task is marked as complete or deleted.
- **FR-010**: System MUST include task details in reminder emails: title, description, due date/time, priority, categories, and time until due.
- **FR-011**: System MUST handle Gmail API failures gracefully by logging errors, queuing failed reminders, and retrying with exponential backoff (max 3 attempts). If individual reminders continue to fail due to rate limiting, system MUST send a daily digest email at 8:00 AM in the user's configured time zone summarizing all pending reminders.
- **FR-012**: System MUST store recurring task metadata including recurrence pattern (including custom interval multipliers and specific weekdays for custom patterns), series ID, and relationship to other instances in the series.
- **FR-013**: System MUST sort tasks with due times by date first, then by time within the same date.
- **FR-014**: System MUST persist all new task attributes (due time, recurrence pattern, reminder settings) to the JSON storage file.
- **FR-015**: System MUST maintain backward compatibility with existing tasks that don't have time, recurrence, or reminder data.
- **FR-016**: System MUST check for pending reminders on application startup and send any overdue reminders immediately. The application MUST run continuously on Hugging Face Spaces and perform periodic reminder checks every 1 minute to send reminders at their scheduled times.
- **FR-017**: System MUST provide status information showing when the next reminder check will occur and how many reminders are pending.
- **FR-018**: System MUST update the README.md documentation to include instructions for all new features (recurring tasks, due times, email reminders, startup-based reminder checking, time zone configuration, multiple reminders per task).
- **FR-019**: System MUST validate that due time is provided when configuring reminders (cannot set reminders without a specific due time).
- **FR-020**: System MUST allow users to configure their preferred time zone via a global setting in a configuration file. The system MUST store all timestamps in UTC internally and convert to/from the user's configured time zone for display and input. If no time zone is configured, the system MUST default to the system time zone.

### Key Entities

- **Task**: Enhanced with new attributes:
  - **ID**: Auto-incrementing integer (existing)
  - **Title**: Task name/summary (existing)
  - **Description**: Detailed task information (existing)
  - **Status**: completed/incomplete (existing)
  - **Priority**: high/medium/low (existing)
  - **Categories**: List of category tags (existing)
  - **Due Date**: Date component (existing)
  - **Due Time**: NEW - Time component (HH:MM format, optional)
  - **Recurrence Pattern**: NEW - Recurrence configuration (daily/weekly/monthly/yearly/custom, optional)
  - **Recurrence Interval**: NEW - Interval for custom recurrence (e.g., every 3 days)
  - **Recurrence Weekdays**: NEW - Specific weekdays for custom weekly patterns (e.g., [Mon, Wed, Fri])
  - **Recurrence End Date**: NEW - Optional end date for recurring series
  - **Series ID**: NEW - Identifier linking instances of the same recurring task
  - **Instance Number**: NEW - Position in the recurring series (1, 2, 3, ...)
  - **Reminder Settings**: NEW - List of reminder times relative to due date/time (supports multiple reminders per task)
  - **User Time Zone**: NEW - User's configured time zone for display and input (stored in global config file, defaults to system time zone if not configured)
  - **Created At**: Creation timestamp (existing)
  - **Updated At**: Last update timestamp (existing)

- **ReminderService**: NEW - Startup-based service that checks for pending reminders and sends email notifications:
  - **Last Check Time**: Timestamp of last reminder check
  - **Next Check Time**: Timestamp of next scheduled reminder check
  - **Check Interval**: 1 minute between reminder checks
  - **Pending Reminders**: Queue of reminders to be sent
  - **Failed Reminders**: Log of failed reminder attempts with retry count
  - **Daily Digest Queue**: List of reminders that failed individual delivery and will be included in daily digest sent at 8:00 AM user's time zone
  - **Daily Digest Time**: 8:00 AM in user's configured time zone

- **RecurringSeries**: NEW - Represents a series of recurring task instances:
  - **Series ID**: Unique identifier for the series
  - **Base Task**: Template task with recurrence pattern
  - **Active Instances**: List of current and future instances
  - **Completed Instances**: History of completed instances

- **EmailReminder**: NEW - Represents a scheduled email reminder:
  - **Task ID**: Associated task
  - **Scheduled Time**: When to send the reminder
  - **Reminder Type**: Time before due (e.g., 1 hour before)
  - **Status**: pending/sent/failed
  - **Retry Count**: Number of send attempts

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create tasks with specific due times (date + time) with 100% accuracy in parsing common time formats (24-hour, 12-hour AM/PM, natural language).
- **SC-002**: Users can create recurring tasks with standard patterns (daily, weekly, monthly) and the system automatically generates the next instance within 1 second of marking the current instance complete.
- **SC-003**: Email reminders are sent to haji08307@gmail.com at the configured time before due date with 95% reliability (allowing for network issues and API rate limits).
- **SC-004**: Reminder emails are delivered within 2 minutes of the scheduled reminder time under normal network conditions.
- **SC-005**: The application checks for pending reminders on startup and sends overdue reminders within 30 seconds. During continuous operation with 1-minute check intervals, reminders are sent within 1 minute of their scheduled time.
- **SC-006**: Users can configure multiple reminder times per task (e.g., 15 min, 1 hour, 1 day before) and the system schedules all reminders accurately with less than 1-minute deviation from scheduled times.
- **SC-007**: When a recurring task is marked complete (even before its due date), the next instance is created with the due date calculated from the original due date + recurrence interval (100% accuracy for standard patterns and custom patterns with interval multipliers and specific weekdays).
- **SC-008**: Users can update or delete recurring task instances with clear options for "this instance only" or "all future instances", with changes applied correctly 100% of the time.
- **SC-009**: The system handles Gmail API authentication errors gracefully, displaying clear error messages and allowing retry without data loss.
- **SC-010**: All new features maintain backward compatibility with existing tasks (tasks without time/recurrence/reminders continue to function normally).
- **SC-011**: Task operations (add, view, update, delete) with new fields complete in under 1 second for up to 10,000 tasks.
- **SC-012**: The system successfully queues and retries failed reminder emails up to 3 times with exponential backoff. If individual reminders continue to fail due to rate limiting, the system sends a daily digest email at 8:00 AM in the user's configured time zone summarizing all pending reminders, achieving eventual delivery for 98% of reminders.
- **SC-013**: Updated README.md documentation includes clear examples and usage instructions for all new features (recurring tasks with custom patterns including interval multipliers and specific weekdays, due times, multiple reminders per task, startup-based reminder checking with 1-minute intervals, time zone configuration via config file, daily digest at 8:00 AM).
- **SC-014**: Users can sort tasks by due date and time with correct ordering (earlier dates/times first) completing in under 500ms for up to 10,000 tasks.
- **SC-015**: The system stores and retrieves all new task attributes (due time, recurrence, reminders) from JSON storage with 100% data integrity across application restarts.

## Assumptions

- Gmail API credentials (token.json and credentials.json) are valid and properly configured before feature implementation
- The user's system has network connectivity for sending email reminders
- The email address haji08307@gmail.com is valid and accessible
- Users understand basic recurring task concepts (daily, weekly, monthly patterns)
- The system clock is reasonably accurate for scheduling reminders
- The application will be deployed on Hugging Face Spaces and run continuously, allowing for 1-minute periodic reminder checks
- Users can configure their preferred time zone via a configuration file, which may differ from the system time zone
- Users will configure their time zone once during initial setup and rarely change it
- JSON file storage is sufficient for the expected number of tasks and recurring instances (up to 10,000 tasks)
- Users prefer email reminders over other notification methods (push notifications, SMS, etc.)
- Custom recurrence patterns with interval multipliers (e.g., every 3 days) and specific weekdays (e.g., Mon/Wed/Fri) cover the majority of user needs
- Users may want multiple reminders for important tasks (e.g., 1 day before AND 1 hour before)
- A 1-minute check interval provides sufficient responsiveness for time-sensitive reminders without excessive resource usage
- Daily digest emails at 8:00 AM provide adequate fallback notification for rate-limited reminders

## Dependencies

- Gmail API Python libraries: google-api-python-client, google-auth, google-auth-oauthlib (specified in requirements)
- Existing Gmail API credentials: token.json and credentials.json (already added per user input)
- Python datetime and dateutil libraries for time parsing and manipulation
- Python pytz library for time zone handling and conversion
- Hugging Face Spaces deployment platform for continuous application running
- Existing Ticklisto codebase with JSON persistence and Rich UI components

## Out of Scope

- Web or mobile interface for task management (remains CLI-only)
- Push notifications or SMS reminders (email only via Gmail API)
- Shared tasks or multi-user collaboration
- Task dependencies or subtasks
- Calendar integration (Google Calendar, Outlook, etc.)
- Natural language processing for complex recurrence patterns beyond interval multipliers and specific weekdays (e.g., "every second Tuesday of the month", "last Friday of each quarter")
- Reminder snooze functionality
- Email reply-to-complete functionality (completing tasks via email response)
- Attachment support for tasks
- Task templates or quick-add shortcuts
- Analytics or productivity reports
- Integration with other task management systems
- Custom email templates or branding
- Multiple email recipient support (fixed to haji08307@gmail.com)
