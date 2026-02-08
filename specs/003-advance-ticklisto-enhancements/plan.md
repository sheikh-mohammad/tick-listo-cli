# Implementation Plan: Advanced Ticklisto Enhancements

**Branch**: `003-advance-ticklisto-enhancements` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-advance-ticklisto-enhancements/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add intelligent task management features to Ticklisto including recurring tasks with auto-rescheduling, due dates with time support, and Gmail-based email reminders. Tasks can be configured with optional recurrence patterns (daily, weekly, monthly, yearly, custom with interval multipliers and specific weekdays). Users can set multiple reminder times per task (e.g., 1 day before, 1 hour before). The system sends email reminders via Gmail API to haji08307@gmail.com with rate limiting handling (exponential backoff + 8 AM daily digest fallback). Application runs continuously on Hugging Face Spaces with 1-minute reminder check intervals. Time zone support allows users to configure their preferred time zone via config file while storing all timestamps in UTC internally.

**Technical Approach**: Extend existing Task model with new optional fields for backward compatibility. Implement ReminderService as a background thread that checks for pending reminders every 1 minute. Use Gmail API with existing credentials (token.json, credentials.json). Store all data in existing JSON file format. Implement RecurringTaskService to handle series management and auto-rescheduling on task completion.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**:
- Rich (existing - CLI UI)
- google-api-python-client (NEW - Gmail API) - Add via: `uv add google-api-python-client`
- google-auth (NEW - Gmail authentication) - Add via: `uv add google-auth`
- google-auth-oauthlib (NEW - Gmail OAuth) - Add via: `uv add google-auth-oauthlib`
- python-dateutil (NEW - time parsing) - Add via: `uv add python-dateutil`
- pytz (NEW - time zone handling) - Add via: `uv add pytz`

**Package Management**: Use UV for all dependency management per project constitution

**Storage**: JSON file (existing - tasks.json), Config file (NEW - config.json for time zone)
**Testing**: pytest (existing)
**Target Platform**: Hugging Face Spaces (continuous running), Python CLI application
**Project Type**: Single console application
**Performance Goals**:
- Task operations <1 second for up to 10,000 tasks
- Reminder checks every 1 minute
- Reminder delivery within 1 minute of scheduled time
- Task sorting <500ms for 10,000 tasks

**Constraints**:
- Gmail API rate limits (250 quota units/user/second, 100 units per send)
- 95% reminder delivery reliability
- Backward compatibility with existing tasks (no time/recurrence/reminders)
- JSON storage only (no database)
- Single user (haji08307@gmail.com)

**Scale/Scope**:
- Up to 10,000 tasks
- Multiple reminders per task
- Recurring task series with unlimited instances
- 1-minute reminder check intervals

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development (NON-NEGOTIABLE)
- Specification complete with 9 clarifications across 2 sessions
- Plan being created following SDD methodology
- Tasks will be generated from this plan

### ✅ AI-Agent Driven Implementation
- All code will be generated using Claude Code
- Following Agentic Dev Stack workflow

### ✅ Progressive Complexity Evolution
- Building on Phase I console application
- Adding intelligent features while maintaining console interface
- No web/mobile components (Phase I focus)

### ✅ Reusable Intelligence & Modularity
- ReminderService designed as reusable module
- RecurringTaskService as independent component
- Gmail integration encapsulated in separate service
- Time zone handling in utility module

### ✅ Test-First (NON-NEGOTIABLE)
- TDD will be enforced: tests written → approved → fail → implement
- Red-Green-Refactor cycle for all new features

### ✅ Atomic Commits
- Each feature component will be committed separately
- Small, cohesive changes per commit

### ✅ Co-authoring with Claude Code
- All commits will include: Co-authored-by: Claude Code <claude-code@anthropic.com>

### ✅ Clean Architecture & Separation of Concerns
- Clear separation: models/ (Task, Reminder), services/ (ReminderService, RecurringTaskService, GmailService), utils/ (time zone, date parsing)
- Well-defined interfaces between components

**Gate Status**: ✅ PASSED - All constitution principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/003-advance-ticklisto-enhancements/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── gmail-api.md     # Gmail API integration contract
│   ├── reminder-service.md  # ReminderService interface
│   └── recurring-task-service.md  # RecurringTaskService interface
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/ticklisto/
├── models/
│   ├── __init__.py
│   ├── task.py                    # MODIFY: Add new fields (due_time, recurrence*, reminder_settings)
│   ├── reminder.py                # NEW: EmailReminder entity
│   └── recurring_series.py        # NEW: RecurringSeries entity
│
├── services/
│   ├── __init__.py
│   ├── task_service.py            # MODIFY: Add recurring task logic
│   ├── storage_service.py         # MODIFY: Handle new Task fields
│   ├── reminder_service.py        # NEW: Background reminder checking & sending
│   ├── recurring_task_service.py  # NEW: Recurring task series management
│   ├── gmail_service.py           # NEW: Gmail API integration
│   └── time_zone_service.py       # NEW: Time zone conversion utilities
│
├── utils/
│   ├── __init__.py
│   ├── date_parser.py             # MODIFY: Add time parsing support
│   ├── time_utils.py              # NEW: Time zone utilities
│   └── config_manager.py          # NEW: Config file management (time zone)
│
├── cli/
│   ├── __init__.py
│   └── ticklisto_cli.py           # MODIFY: Add new commands (recurring, reminders, time zone config)
│
└── ui/
    ├── __init__.py
    └── rich_ui.py                 # MODIFY: Display due times, recurrence patterns, reminder status

tests/
├── unit/
│   ├── test_task_model.py         # MODIFY: Test new Task fields
│   ├── test_reminder_service.py   # NEW: Test reminder logic
│   ├── test_recurring_task_service.py  # NEW: Test recurring task logic
│   ├── test_gmail_service.py      # NEW: Test Gmail integration (mocked)
│   └── test_time_zone_service.py  # NEW: Test time zone conversions
│
├── integration/
│   ├── test_task_with_reminders.py  # NEW: End-to-end reminder flow
│   └── test_recurring_tasks.py      # NEW: End-to-end recurring task flow
│
└── contract/
    └── test_gmail_api_contract.py   # NEW: Gmail API contract tests

config/
└── config.json                      # NEW: User configuration (time zone)

credentials/
├── token.json                       # EXISTING: Gmail OAuth token
└── credentials.json                 # EXISTING: Gmail OAuth credentials
```

**Structure Decision**: Single project structure maintained. All new features integrated into existing `src/ticklisto/` hierarchy following established patterns (models/, services/, utils/, cli/, ui/). New services added for reminder management, recurring tasks, and Gmail integration. Configuration file added for time zone settings. Tests organized by type (unit, integration, contract) following existing pytest structure.

## Complexity Tracking

> **No violations** - All constitution principles satisfied without exceptions.

