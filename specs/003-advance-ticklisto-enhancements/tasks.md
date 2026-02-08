# Tasks: Advanced Ticklisto Enhancements

**Input**: Design documents from `/specs/003-advance-ticklisto-enhancements/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: TDD is MANDATORY per project constitution. All test tasks must be completed and approved before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project type**: Single console application
- **Source**: `src/ticklisto/`
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/contract/`
- **Config**: `config/`
- **Storage**: `ticklisto_data.json` (root)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and create basic configuration structure

- [X] T001 Install Gmail API dependencies via `uv add google-api-python-client google-auth google-auth-oauthlib`
- [X] T002 Install time handling dependencies via `uv add python-dateutil pytz`
- [X] T003 [P] Create config directory structure at `config/`
- [X] T004 [P] Create config.json template with time_zone, default_reminder_offset, email_recipient, daily_digest_time fields

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create RecurrencePattern enum in `src/ticklisto/models/task.py`
- [X] T006 Create ReminderStatus enum in `src/ticklisto/models/reminder.py`
- [X] T007 [P] Create ReminderSetting value object in `src/ticklisto/models/task.py`
- [X] T008 [P] Create ConfigManager utility in `src/ticklisto/utils/config_manager.py` for loading/saving config.json
- [X] T009 [P] Create TimeZoneService in `src/ticklisto/services/time_zone_service.py` for UTC/user TZ conversions
- [X] T010 Update StorageService in `src/ticklisto/services/storage_service.py` to handle recurring_series section in ticklisto_data.json

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Due Dates with Time Support (Priority: P1) 🎯 MVP

**Goal**: Enable users to set specific due dates and times for tasks with proper parsing and display

**Independent Test**: User can create a task with date and time (e.g., "2026-02-15 14:30"), view it in the task list with time displayed, and system stores both components accurately

### Tests for User Story 1 (TDD - Write First) ⚠️

> **CRITICAL: Write these tests FIRST, get user approval, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Unit test for Task model with due_time field in `tests/unit/test_task_model.py`
- [X] T012 [P] [US1] Unit test for time parsing (24-hour, 12-hour AM/PM, natural language) in `tests/unit/test_date_parser.py`
- [X] T013 [P] [US1] Unit test for time zone conversion utilities in `tests/unit/test_time_zone_service.py`
- [X] T014 [P] [US1] Integration test for creating task with due time in `tests/integration/test_task_with_time.py`
- [X] T015 [P] [US1] Integration test for sorting tasks by date and time in `tests/integration/test_task_sorting.py`

### Implementation for User Story 1

- [X] T016 [US1] Add due_time field (time, optional) to Task model in `src/ticklisto/models/task.py`
- [X] T017 [US1] Update Task.to_dict() and Task.from_dict() to handle due_time serialization in `src/ticklisto/models/task.py`
- [X] T018 [US1] Extend date_parser in `src/ticklisto/utils/date_parser.py` to parse time formats (24-hour, 12-hour AM/PM, natural language like "2pm")
- [X] T019 [US1] Create time_utils module in `src/ticklisto/utils/time_utils.py` with functions for time formatting and validation
- [X] T020 [US1] Update TaskService.create_task() in `src/ticklisto/services/task_service.py` to accept and validate due_time parameter
- [X] T021 [US1] Update TaskService.update_task() in `src/ticklisto/services/task_service.py` to handle due_time updates
- [X] T022 [US1] Update SortService in `src/ticklisto/services/sort_service.py` to sort by date first, then time within same date
- [X] T023 [US1] Update Rich UI in `src/ticklisto/ui/rich_ui.py` to display due date with time (e.g., "Feb 15, 2026 at 2:30 PM")
- [X] T024 [US1] Update CLI in `src/ticklisto/cli/ticklisto_cli.py` to accept due time input when creating/updating tasks

**Checkpoint**: User Story 1 complete - users can set and view due times

---

## Phase 4: User Story 2 - Recurring Tasks with Auto-Rescheduling (Priority: P1)

**Goal**: Enable users to create recurring tasks that automatically generate next instance on completion

**Independent Test**: User can create a task with recurrence pattern (daily, weekly, monthly), mark it complete, and system automatically creates next instance with appropriate due date

### Tests for User Story 2 (TDD - Write First) ⚠️

- [X] T025 [P] [US2] Unit test for RecurringSeries entity in `tests/unit/test_recurring_series.py`
- [X] T026 [P] [US2] Unit test for calculate_next_due_date() with all patterns in `tests/unit/test_recurring_task_service.py`
- [X] T027 [P] [US2] Unit test for edge cases (month-end, leap year, DST) in `tests/unit/test_recurring_task_service.py`
- [X] T028 [P] [US2] Integration test for recurring task lifecycle in `tests/integration/test_recurring_tasks.py`
- [X] T029 [P] [US2] Integration test for early completion (before due date) in `tests/integration/test_recurring_tasks.py`

### Implementation for User Story 2

- [X] T030 [US2] Add recurrence fields to Task model: recurrence_pattern, recurrence_interval, recurrence_weekdays, recurrence_end_date, series_id, instance_number in `src/ticklisto/models/task.py`
- [X] T031 [US2] Update Task.to_dict() and Task.from_dict() for recurrence fields in `src/ticklisto/models/task.py`
- [X] T032 [US2] Create RecurringSeries entity in `src/ticklisto/models/recurring_series.py`
- [X] T033 [US2] Create RecurringTaskService in `src/ticklisto/services/recurring_task_service.py` with create_recurring_task() method
- [X] T034 [US2] Implement calculate_next_due_date() in RecurringTaskService for all patterns (daily, weekly, monthly, yearly, custom)
- [X] T035 [US2] Implement complete_instance_and_generate_next() in RecurringTaskService
- [X] T036 [US2] Handle weekday-specific recurrence (Mon/Wed/Fri) in calculate_next_due_date()
- [X] T037 [US2] Handle edge cases: month-end dates, leap years, DST transitions in calculate_next_due_date()
- [X] T038 [US2] Update TaskService.complete_task() in `src/ticklisto/services/task_service.py` to call RecurringTaskService for recurring tasks
- [X] T039 [US2] Update StorageService to persist recurring_series data in ticklisto_data.json
- [X] T040 [US2] Update Rich UI to display recurrence indicator (🔁) and pattern in `src/ticklisto/ui/rich_ui.py`
- [X] T041 [US2] Add CLI command for creating recurring tasks in `src/ticklisto/cli/ticklisto_cli.py`

**Checkpoint**: User Story 2 complete - recurring tasks auto-reschedule on completion

---

## Phase 5: User Story 3 - Email Reminders via Gmail API (Priority: P1)

**Goal**: Enable users to receive email reminders for tasks via Gmail API

**Independent Test**: User creates a task with due date and time, system sends email reminder to haji08307@gmail.com at appropriate time before deadline

### Tests for User Story 3 (TDD - Write First) ⚠️

- [X] T042 [P] [US3] Unit test for GmailService with mocked Gmail API in `tests/unit/test_gmail_service.py`
- [X] T043 [P] [US3] Unit test for EmailReminder entity in `tests/unit/test_reminder.py`
- [X] T044 [P] [US3] Unit test for exponential backoff retry logic in `tests/unit/test_gmail_service.py`
- [X] T045 [P] [US3] Contract test for Gmail API message format in `tests/contract/test_gmail_api_contract.py`
- [X] T046 [P] [US3] Integration test for sending reminder email (with test account) in `tests/integration/test_email_reminders.py`

### Implementation for User Story 3

- [X] T047 [US3] Create EmailReminder entity in `src/ticklisto/models/reminder.py` with id, task_id, scheduled_time, status, retry_count fields
- [X] T048 [US3] Create GmailService in `src/ticklisto/services/gmail_service.py` with OAuth initialization
- [X] T049 [US3] Implement send_reminder_email() in GmailService with task details formatting
- [X] T050 [US3] Implement token refresh logic in GmailService for expired tokens
- [X] T051 [US3] Implement exponential backoff retry logic in GmailService for rate limit errors
- [X] T052 [US3] Implement send_daily_digest() in GmailService for failed reminders
- [X] T053 [US3] Add error handling for AuthenticationError, RateLimitError, NetworkError in GmailService
- [X] T054 [US3] Add reminder_settings field (list of ReminderSetting) to Task model in `src/ticklisto/models/task.py`
- [X] T055 [US3] Update Task serialization for reminder_settings in `src/ticklisto/models/task.py`
- [X] T056 [US3] Add CLI command for configuring reminders when creating/updating tasks in `src/ticklisto/cli/ticklisto_cli.py`

**Checkpoint**: User Story 3 complete - email reminders can be sent via Gmail API

---

## Phase 6: User Story 4 - Startup Reminder Checking (Priority: P1)

**Goal**: Enable application to check for pending reminders on startup and send them immediately

**Independent Test**: User starts application, system immediately checks all tasks for pending reminders and sends them via email

### Tests for User Story 4 (TDD - Write First) ⚠️

- [X] T057 [P] [US4] Unit test for ReminderService.schedule_reminders() in `tests/unit/test_reminder_service.py`
- [X] T058 [P] [US4] Unit test for ReminderService.cancel_reminders() in `tests/unit/test_reminder_service.py`
- [X] T059 [P] [US4] Unit test for reminder queue management in `tests/unit/test_reminder_service.py`
- [X] T060 [P] [US4] Integration test for startup reminder check in `tests/integration/test_reminder_service.py`
- [X] T061 [P] [US4] Integration test for 1-minute check interval in `tests/integration/test_reminder_service.py`

### Implementation for User Story 4

- [X] T062 [US4] Create ReminderService in `src/ticklisto/services/reminder_service.py` with __init__(gmail_service, storage_service, time_zone_service)
- [X] T063 [US4] Implement schedule_reminders(task) in ReminderService to create EmailReminder objects
- [X] T064 [US4] Implement cancel_reminders(task_id) in ReminderService
- [X] T065 [US4] Implement _check_loop() background thread method with 1-minute interval
- [X] T066 [US4] Implement _send_reminder(reminder) with retry logic and exponential backoff
- [X] T067 [US4] Implement _send_daily_digest() for 8 AM user time zone
- [X] T068 [US4] Implement start() and stop() methods for thread lifecycle management
- [X] T069 [US4] Implement get_status() to show pending/failed reminder counts
- [X] T070 [US4] Create reminders.json storage for transient reminder state
- [X] T071 [US4] Update TaskService to call ReminderService.schedule_reminders() when task created/updated with reminder_settings
- [X] T072 [US4] Update TaskService to call ReminderService.cancel_reminders() when task completed/deleted
- [X] T073 [US4] Update `src/ticklisto/__main__.py` to start ReminderService on app launch
- [X] T074 [US4] Add CLI command to check reminder service status in `src/ticklisto/cli/ticklisto_cli.py`

**Checkpoint**: User Story 4 complete - reminders checked on startup and every 1 minute

---

## Phase 7: User Story 5 - Recurring Task Management (Priority: P2)

**Goal**: Enable users to view, edit, and manage recurring task series

**Independent Test**: User can view all instances of a recurring task series, edit future instances, and stop recurrence without deleting past instances

### Tests for User Story 5 (TDD - Write First) ⚠️

- [X] T075 [P] [US5] Unit test for update_series() in `tests/unit/test_recurring_task_service.py`
- [X] T076 [P] [US5] Unit test for stop_recurrence() in `tests/unit/test_recurring_task_service.py`
- [X] T077 [P] [US5] Integration test for updating all future instances in `tests/integration/test_recurring_tasks.py`
- [X] T078 [P] [US5] Integration test for stopping recurrence in `tests/integration/test_recurring_tasks.py`

### Implementation for User Story 5

- [X] T079 [US5] Implement update_series(series_id, update_future, **updates) in RecurringTaskService
- [X] T080 [US5] Implement stop_recurrence(series_id, delete_future) in RecurringTaskService
- [X] T081 [US5] Implement get_series(series_id) in RecurringTaskService
- [X] T082 [US5] Implement get_series_instances(series_id, include_completed) in RecurringTaskService
- [X] T083 [US5] Add CLI command for listing recurring series in `src/ticklisto/cli/ticklisto_cli.py`
- [X] T084 [US5] Add CLI command for stopping recurring series in `src/ticklisto/cli/ticklisto_cli.py`
- [X] T085 [US5] Update CLI update command to ask "This instance only" or "All future instances" for recurring tasks
- [X] T086 [US5] Update CLI delete command to ask "This instance only" or "Stop all future" for recurring tasks
- [X] T087 [US5] Update Rich UI to show series information (next occurrence, completed count) in `src/ticklisto/ui/rich_ui.py`

**Checkpoint**: User Story 5 complete - recurring task series can be managed

---

## Phase 8: User Story 6 - Flexible Reminder Configuration (Priority: P3)

**Goal**: Enable users to set multiple reminders per task with custom timing

**Independent Test**: User can set multiple reminders for a single task (e.g., 1 day before, 1 hour before) and customize reminder timing per task

### Tests for User Story 6 (TDD - Write First) ⚠️

- [X] T088 [P] [US6] Unit test for multiple reminders per task in `tests/unit/test_reminder_service.py`
- [X] T089 [P] [US6] Integration test for multiple reminder delivery in `tests/integration/test_email_reminders.py`

### Implementation for User Story 6

- [X] T090 [US6] Update ReminderService.schedule_reminders() to handle multiple ReminderSetting objects per task
- [X] T091 [US6] Update CLI to accept multiple reminder offsets when creating/updating tasks in `src/ticklisto/cli/ticklisto_cli.py`
- [X] T092 [US6] Add default reminder preferences to config.json schema
- [X] T093 [US6] Update TaskService to apply default reminder settings from config when task created with due_time
- [X] T094 [US6] Update Rich UI to display all configured reminders for a task in `src/ticklisto/ui/rich_ui.py`

**Checkpoint**: User Story 6 complete - multiple reminders per task supported

---

## Phase 9: User Story 7 - Reminder Email Content (Priority: P3)

**Goal**: Enhance reminder emails with comprehensive task information

**Independent Test**: User receives reminder email with task title, description, due date/time, priority, categories, and clear formatting

### Tests for User Story 7 (TDD - Write First) ⚠️

- [X] T095 [P] [US7] Unit test for email content formatting in `tests/unit/test_gmail_service.py`
- [X] T096 [P] [US7] Unit test for priority indicator in subject line in `tests/unit/test_gmail_service.py`

### Implementation for User Story 7

- [X] T097 [US7] Enhance send_reminder_email() in GmailService to include all task details (title, description, due date/time, priority, categories)
- [X] T098 [US7] Add priority indicator to email subject line (e.g., "[HIGH PRIORITY]") in GmailService
- [X] T099 [US7] Format email body as HTML with clear sections for task details in GmailService
- [X] T100 [US7] Add recurrence pattern indicator for recurring tasks in email body
- [X] T101 [US7] Enhance daily digest email format with HTML table in GmailService

**Checkpoint**: User Story 7 complete - reminder emails contain comprehensive information

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, documentation, and quality improvements

- [X] T102 [P] Add time zone configuration CLI command in `src/ticklisto/cli/ticklisto_cli.py`
- [X] T103 [P] Add validation for due_time requires due_date in TaskService
- [X] T104 [P] Add validation for reminder_settings requires due_time in TaskService
- [X] T105 [P] Update README.md with new features documentation (recurring tasks, due times, reminders, time zone config)
- [X] T106 [P] Add troubleshooting section to README.md (Gmail auth, reminder service, time zones)
- [X] T107 [P] Add logging for all reminder operations (schedule, send, fail, retry)
- [X] T108 [P] Add logging for recurring task operations (create series, generate instance)
- [X] T109 [P] Verify backward compatibility with existing tasks (no time/recurrence/reminders)
- [X] T110 [P] Performance test with 1000+ tasks to verify <1 second operations
- [X] T111 [P] Test reminder service stability over 24 hours continuous operation
- [X] T112 Create example config.json with all fields documented

**Checkpoint**: Feature complete and production-ready

---

## Dependencies & Execution Order

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundation) → Phase 3-10 (User Stories)

Phase 3 (US1) ─┐
               ├─→ Phase 4 (US2) ─┐
               │                   ├─→ Phase 5 (US3) ─→ Phase 6 (US4) ─→ Phase 7 (US5) ─→ Phase 8 (US6) ─→ Phase 9 (US7) ─→ Phase 10 (Polish)
               └─────────────────┘

US1 (Due Times) is prerequisite for US2 (Recurring) and US3 (Reminders)
US2 and US3 can be implemented in parallel after US1
US4 (Startup Checking) depends on US3 (Reminders)
US5-US7 are enhancements that depend on earlier stories
```

### Parallel Execution Opportunities

**Within Phase 2 (Foundation)**:
- T007, T008, T009 can run in parallel (different files)

**Within Phase 3 (US1)**:
- T011-T015 (all tests) can run in parallel
- T018, T019 can run in parallel (different files)

**Within Phase 4 (US2)**:
- T025-T029 (all tests) can run in parallel
- T032, T033 can run in parallel after T030-T031

**Within Phase 5 (US3)**:
- T042-T046 (all tests) can run in parallel
- T047, T048 can run in parallel (different files)

**Within Phase 6 (US4)**:
- T057-T061 (all tests) can run in parallel

**Within Phase 10 (Polish)**:
- T102-T112 can mostly run in parallel (different files/concerns)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Recommended MVP**: User Story 1 only (Due Dates with Time Support)
- Provides immediate value: precise task scheduling
- Foundation for all other features
- Independently testable and deliverable
- Low risk, high value

**Extended MVP**: User Stories 1-4 (All P1 stories)
- Complete core functionality: time support, recurring tasks, email reminders, startup checking
- Delivers full value proposition of the feature
- All P1 stories are independently testable

### Incremental Delivery

1. **Sprint 1**: Phase 1-3 (Setup + Foundation + US1) → Deliver time support
2. **Sprint 2**: Phase 4 (US2) → Deliver recurring tasks
3. **Sprint 3**: Phase 5-6 (US3-US4) → Deliver email reminders
4. **Sprint 4**: Phase 7-9 (US5-US7) → Deliver enhancements
5. **Sprint 5**: Phase 10 (Polish) → Production ready

### TDD Workflow (MANDATORY per Constitution)

For each user story:
1. **RED**: Write tests first (T0XX test tasks), get user approval, verify tests FAIL
2. **GREEN**: Implement features (T0XX implementation tasks), verify tests PASS
3. **REFACTOR**: Clean up code, maintain test coverage
4. **COMMIT**: Atomic commits with co-authoring: `Co-authored-by: Claude Code <claude-code@anthropic.com>`

---

## Task Summary

**Total Tasks**: 112
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundation): 6 tasks
- Phase 3 (US1 - P1): 14 tasks (5 tests + 9 implementation)
- Phase 4 (US2 - P1): 17 tasks (5 tests + 12 implementation)
- Phase 5 (US3 - P1): 15 tasks (5 tests + 10 implementation)
- Phase 6 (US4 - P1): 13 tasks (5 tests + 8 implementation)
- Phase 7 (US5 - P2): 13 tasks (4 tests + 9 implementation)
- Phase 8 (US6 - P3): 7 tasks (2 tests + 5 implementation)
- Phase 9 (US7 - P3): 7 tasks (2 tests + 5 implementation)
- Phase 10 (Polish): 11 tasks

**Parallel Opportunities**: 45+ tasks marked with [P] can run in parallel

**Independent Test Criteria**:
- US1: Create task with time, view in list, verify storage
- US2: Create recurring task, complete it, verify next instance generated
- US3: Create task with reminder, verify email sent
- US4: Start app, verify overdue reminders sent immediately
- US5: Edit recurring series, verify future instances updated
- US6: Set multiple reminders, verify all sent at correct times
- US7: Receive reminder email, verify comprehensive content

**Format Validation**: ✅ All tasks follow checklist format with ID, optional [P], Story label, and file paths
