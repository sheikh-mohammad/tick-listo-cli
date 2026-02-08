---
id: 0004
title: Advanced Ticklisto implementation plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: 003-advance-ticklisto-enhancements
branch: 003-advance-ticklisto-enhancements
user: user
command: /sp.plan
labels: ["plan", "architecture", "design", "recurring-tasks", "reminders", "gmail"]
links:
  spec: specs/003-advance-ticklisto-enhancements/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-advance-ticklisto-enhancements/plan.md
  - specs/003-advance-ticklisto-enhancements/research.md
  - specs/003-advance-ticklisto-enhancements/data-model.md
  - specs/003-advance-ticklisto-enhancements/quickstart.md
  - specs/003-advance-ticklisto-enhancements/contracts/gmail-service.md
  - specs/003-advance-ticklisto-enhancements/contracts/reminder-service.md
  - specs/003-advance-ticklisto-enhancements/contracts/recurring-task-service.md
tests:
  - none (planning phase)
---

## Prompt

```
/sp.plan @specs/003-advance-ticklisto-enhancements\
```

User requested implementation planning for Advanced Ticklisto Enhancements feature after completing two clarification sessions with 9 total clarifications.

## Response snapshot

**Phase 0: Research & Technology Decisions**
- Documented technology choices for Gmail API integration, time zone handling, time parsing, background service, exponential backoff, recurring task scheduling, and configuration management
- Selected: google-api-python-client for Gmail, pytz for time zones, python-dateutil for parsing, threading.Thread for background service
- Defined implementation patterns and best practices for each technology
- Documented performance considerations, security requirements, and testing strategies

**Phase 1: Design & Contracts**
- Created comprehensive data model with 7 entities: Task (enhanced), RecurrencePattern, ReminderSetting, EmailReminder, ReminderStatus, RecurringSeries, DailyDigest
- Defined storage schema for ticklisto_data.json (confirmed actual storage file name from codebase analysis)
- Created three service contracts:
  - GmailService: OAuth authentication, send reminder emails, send daily digest, token refresh, rate limiting
  - ReminderService: Background thread (1-minute intervals), schedule/cancel reminders, exponential backoff retry, daily digest at 8 AM
  - RecurringTaskService: Create series, calculate next occurrence, generate instances, update/stop series
- Documented all method signatures, parameters, return types, error handling, and business rules

**Project Structure Analysis**
- Analyzed existing codebase structure (src/ticklisto/ with models/, services/, utils/, cli/, ui/)
- Confirmed storage file: ticklisto_data.json (not tasks.json)
- Verified credentials location: credentials/token.json and credentials/credentials.json
- Identified files to modify: task.py, storage_service.py, task_service.py, date_parser.py, ticklisto_cli.py, rich_ui.py
- Identified files to create: 9 new files (reminder.py, recurring_series.py, gmail_service.py, reminder_service.py, recurring_task_service.py, time_zone_service.py, time_utils.py, config_manager.py, plus test files)

**Constitution Check**
- All 8 constitution principles satisfied without violations
- Spec-Driven Development: Complete spec with 9 clarifications
- Test-First: TDD will be enforced
- Clean Architecture: Clear separation of concerns with modular services
- No complexity tracking violations

**Quickstart Guide**
- Created 6-phase implementation order: Foundation → Recurring Tasks → Gmail Integration → Reminder Service → CLI/UI → Documentation
- Provided storage schemas, service initialization patterns, common usage examples
- Documented deployment checklist and troubleshooting guide

## Outcome

- ✅ Impact: Complete implementation plan created with research, data model, service contracts, and quickstart guide. All technology decisions documented with rationale. Project structure analyzed and confirmed actual storage file (ticklisto_data.json). Ready for task generation with /sp.tasks.
- 🧪 Tests: No tests run (planning phase). Testing strategy documented in each contract and quickstart guide.
- 📁 Files: Created 7 planning documents (plan.md, research.md, data-model.md, quickstart.md, 3 service contracts)
- 🔁 Next prompts: /sp.tasks to generate detailed task breakdown from this plan
- 🧠 Reflection: User correctly identified need to analyze actual codebase structure. Confirmed storage file is ticklisto_data.json (not tasks.json). All planning documents reference correct file paths and existing code structure. Plan accounts for backward compatibility with existing Task model and storage format. Constitution check passed without violations - all new features integrate cleanly into existing Phase I console application architecture.

## Evaluation notes (flywheel)

- Failure modes observed: Initial planning documents may have assumed generic file names; user intervention ensured actual codebase analysis (storage_service.py confirmed ticklisto_data.json)
- Graders run and results (PASS/FAIL): N/A (planning phase)
- Prompt variant (if applicable): Standard /sp.plan workflow with codebase analysis
- Next experiment (smallest change to try): Consider adding explicit codebase analysis step at start of /sp.plan to verify actual file names, storage patterns, and existing structure before creating planning documents
