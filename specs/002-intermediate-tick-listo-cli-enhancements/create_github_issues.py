#!/usr/bin/env python3
"""
Script to create GitHub issues for all 80 tasks from tasks.md
Repository: sheikh-mohammad/hackathon-ii-evolution-of-todo
"""

import subprocess
import sys
import json
from typing import List, Dict

# Task definitions extracted from tasks.md
tasks = [
    # Phase 1: Setup (Shared Infrastructure)
    {"id": "T001", "phase": "phase-1", "description": "Add python-dateutil>=2.8.0 to project dependencies in pyproject.toml", "labels": ["phase-1", "implementation"], "parallel": False, "story": None},
    {"id": "T002", "phase": "phase-1", "description": "Verify Rich>=13.0.0 is in project dependencies in pyproject.toml", "labels": ["phase-1", "implementation"], "parallel": False, "story": None},
    {"id": "T003", "phase": "phase-1", "description": "Install dependencies using UV package manager", "labels": ["phase-1", "implementation"], "parallel": False, "story": None},
    {"id": "T004", "phase": "phase-1", "description": "Create src/ticklisto/utils/ directory for utility modules", "labels": ["phase-1", "implementation"], "parallel": False, "story": None},
    {"id": "T005", "phase": "phase-1", "description": "Create tests/unit/ directory structure for unit tests", "labels": ["phase-1", "implementation"], "parallel": False, "story": None},
    {"id": "T006", "phase": "phase-1", "description": "Create tests/integration/ directory structure for integration tests", "labels": ["phase-1", "implementation"], "parallel": False, "story": None},
    {"id": "T007", "phase": "phase-1", "description": "Create tests/contract/ directory structure for contract tests", "labels": ["phase-1", "implementation"], "parallel": False, "story": None},

    # Phase 2: Foundational (Blocking Prerequisites) - Tests
    {"id": "T008", "phase": "phase-2", "description": "Write unit tests for Priority enum validation in tests/unit/test_task_model.py", "labels": ["phase-2", "test", "tdd", "parallel"], "parallel": True, "story": None},
    {"id": "T009", "phase": "phase-2", "description": "Write unit tests for Task model field validation in tests/unit/test_task_model.py", "labels": ["phase-2", "test", "tdd", "parallel"], "parallel": True, "story": None},
    {"id": "T010", "phase": "phase-2", "description": "Write unit tests for Task model helper methods in tests/unit/test_task_model.py", "labels": ["phase-2", "test", "tdd", "parallel"], "parallel": True, "story": None},
    {"id": "T011", "phase": "phase-2", "description": "Write unit tests for validate_priority function in tests/unit/test_validation_service.py", "labels": ["phase-2", "test", "tdd", "parallel"], "parallel": True, "story": None},
    {"id": "T012", "phase": "phase-2", "description": "Write unit tests for validate_categories function in tests/unit/test_validation_service.py", "labels": ["phase-2", "test", "tdd", "parallel"], "parallel": True, "story": None},
    {"id": "T013", "phase": "phase-2", "description": "Write unit tests for validate_date_input function in tests/unit/test_validation_service.py", "labels": ["phase-2", "test", "tdd", "parallel"], "parallel": True, "story": None},
    {"id": "T014", "phase": "phase-2", "description": "Write unit tests for date parser utility in tests/unit/test_date_parser.py", "labels": ["phase-2", "test", "tdd", "parallel"], "parallel": True, "story": None},

    # Phase 2: Foundational - Implementation
    {"id": "T015", "phase": "phase-2", "description": "Create Priority enum in src/ticklisto/models/task.py", "labels": ["phase-2", "implementation"], "parallel": False, "story": None},
    {"id": "T016", "phase": "phase-2", "description": "Enhance Task dataclass with priority, categories, due_date fields in src/ticklisto/models/task.py", "labels": ["phase-2", "implementation"], "parallel": False, "story": None},
    {"id": "T017", "phase": "phase-2", "description": "Add __post_init__ validation to Task model in src/ticklisto/models/task.py", "labels": ["phase-2", "implementation"], "parallel": False, "story": None},
    {"id": "T018", "phase": "phase-2", "description": "Add helper methods to Task model (mark_complete, mark_incomplete, update_field, is_overdue, matches_keyword, has_category, has_any_category, has_all_categories) in src/ticklisto/models/task.py", "labels": ["phase-2", "implementation"], "parallel": False, "story": None},
    {"id": "T019", "phase": "phase-2", "description": "Create date parser utility with flexible format support in src/ticklisto/utils/date_parser.py", "labels": ["phase-2", "implementation"], "parallel": False, "story": None},
    {"id": "T020", "phase": "phase-2", "description": "Create ValidationService with validate_priority function in src/ticklisto/services/validation_service.py", "labels": ["phase-2", "implementation"], "parallel": False, "story": None},
    {"id": "T021", "phase": "phase-2", "description": "Add validate_categories function to ValidationService in src/ticklisto/services/validation_service.py", "labels": ["phase-2", "implementation"], "parallel": False, "story": None},
    {"id": "T022", "phase": "phase-2", "description": "Add validate_date_input function to ValidationService in src/ticklisto/services/validation_service.py", "labels": ["phase-2", "implementation"], "parallel": False, "story": None},
    {"id": "T023", "phase": "phase-2", "description": "Add get_category_suggestions function to ValidationService in src/ticklisto/services/validation_service.py", "labels": ["phase-2", "implementation"], "parallel": False, "story": None},

    # Phase 3: User Story 1 - Tests
    {"id": "T024", "phase": "phase-3", "description": "Write contract tests for backward compatibility with existing tasks in tests/contract/test_backward_compatibility.py", "labels": ["phase-3", "test", "tdd", "parallel", "US1"], "parallel": True, "story": "US1"},
    {"id": "T025", "phase": "phase-3", "description": "Write integration tests for task creation with priority and categories in tests/integration/test_task_operations.py", "labels": ["phase-3", "test", "tdd", "parallel", "US1"], "parallel": True, "story": "US1"},
    {"id": "T026", "phase": "phase-3", "description": "Write integration tests for task update with priority and categories in tests/integration/test_task_operations.py", "labels": ["phase-3", "test", "tdd", "parallel", "US1"], "parallel": True, "story": "US1"},
    {"id": "T027", "phase": "phase-3", "description": "Write integration tests for displaying tasks with Rich formatting in tests/integration/test_cli_commands.py", "labels": ["phase-3", "test", "tdd", "parallel", "US1"], "parallel": True, "story": "US1"},

    # Phase 3: User Story 1 - Implementation
    {"id": "T028", "phase": "phase-3", "description": "Update TaskManager to handle Task model with new fields in src/ticklisto/services/task_manager.py", "labels": ["phase-3", "implementation", "US1"], "parallel": False, "story": "US1"},
    {"id": "T029", "phase": "phase-3", "description": "Add migration logic for existing tasks to new model in src/ticklisto/services/task_manager.py", "labels": ["phase-3", "implementation", "US1"], "parallel": False, "story": "US1"},
    {"id": "T030", "phase": "phase-3", "description": "Create Rich display components for priority indicators in src/ticklisto/ui/components.py", "labels": ["phase-3", "implementation", "US1"], "parallel": False, "story": "US1"},
    {"id": "T031", "phase": "phase-3", "description": "Create Rich display components for category tags in src/ticklisto/ui/components.py", "labels": ["phase-3", "implementation", "US1"], "parallel": False, "story": "US1"},
    {"id": "T032", "phase": "phase-3", "description": "Update display_tasks function with enhanced table formatting in src/ticklisto/cli/display.py", "labels": ["phase-3", "implementation", "US1"], "parallel": False, "story": "US1"},
    {"id": "T033", "phase": "phase-3", "description": "Add prompt_for_priority function using Rich Prompt in src/ticklisto/cli/parsers.py", "labels": ["phase-3", "implementation", "US1"], "parallel": False, "story": "US1"},
    {"id": "T034", "phase": "phase-3", "description": "Add prompt_for_categories function with suggestions in src/ticklisto/cli/parsers.py", "labels": ["phase-3", "implementation", "US1"], "parallel": False, "story": "US1"},
    {"id": "T035", "phase": "phase-3", "description": "Add prompt_for_due_date function with flexible parsing in src/ticklisto/cli/parsers.py", "labels": ["phase-3", "implementation", "US1"], "parallel": False, "story": "US1"},
    {"id": "T036", "phase": "phase-3", "description": "Update add_task command to accept priority, categories, due_date in src/ticklisto/cli/commands.py", "labels": ["phase-3", "implementation", "US1"], "parallel": False, "story": "US1"},
    {"id": "T037", "phase": "phase-3", "description": "Update update_task command to modify priority, categories, due_date in src/ticklisto/cli/commands.py", "labels": ["phase-3", "implementation", "US1"], "parallel": False, "story": "US1"},
    {"id": "T038", "phase": "phase-3", "description": "Add error handling and validation feedback in CLI commands in src/ticklisto/cli/commands.py", "labels": ["phase-3", "implementation", "US1"], "parallel": False, "story": "US1"},

    # Phase 4: User Story 2 - Tests
    {"id": "T039", "phase": "phase-4", "description": "Write unit tests for search_tasks function in tests/unit/test_search_service.py", "labels": ["phase-4", "test", "tdd", "parallel", "US2"], "parallel": True, "story": "US2"},
    {"id": "T040", "phase": "phase-4", "description": "Write unit tests for filter_tasks function with all criteria in tests/unit/test_filter_service.py", "labels": ["phase-4", "test", "tdd", "parallel", "US2"], "parallel": True, "story": "US2"},
    {"id": "T041", "phase": "phase-4", "description": "Write unit tests for date filter logic in tests/unit/test_filter_service.py", "labels": ["phase-4", "test", "tdd", "parallel", "US2"], "parallel": True, "story": "US2"},
    {"id": "T042", "phase": "phase-4", "description": "Write unit tests for category filter OR/AND logic in tests/unit/test_filter_service.py", "labels": ["phase-4", "test", "tdd", "parallel", "US2"], "parallel": True, "story": "US2"},
    {"id": "T043", "phase": "phase-4", "description": "Write integration tests for combined search and filter operations in tests/integration/test_search_filter_integration.py", "labels": ["phase-4", "test", "tdd", "parallel", "US2"], "parallel": True, "story": "US2"},
    {"id": "T044", "phase": "phase-4", "description": "Write integration tests for CLI search command in tests/integration/test_cli_commands.py", "labels": ["phase-4", "test", "tdd", "parallel", "US2"], "parallel": True, "story": "US2"},
    {"id": "T045", "phase": "phase-4", "description": "Write integration tests for CLI filter command in tests/integration/test_cli_commands.py", "labels": ["phase-4", "test", "tdd", "parallel", "US2"], "parallel": True, "story": "US2"},

    # Phase 4: User Story 2 - Implementation
    {"id": "T046", "phase": "phase-4", "description": "Create SearchService with search_tasks function in src/ticklisto/services/search_service.py", "labels": ["phase-4", "implementation", "parallel", "US2"], "parallel": True, "story": "US2"},
    {"id": "T047", "phase": "phase-4", "description": "Create FilterService with filter_tasks function in src/ticklisto/services/filter_service.py", "labels": ["phase-4", "implementation", "parallel", "US2"], "parallel": True, "story": "US2"},
    {"id": "T048", "phase": "phase-4", "description": "Add apply_date_filter helper to FilterService in src/ticklisto/services/filter_service.py", "labels": ["phase-4", "implementation", "US2"], "parallel": False, "story": "US2"},
    {"id": "T049", "phase": "phase-4", "description": "Add search command to CLI in src/ticklisto/cli/commands.py", "labels": ["phase-4", "implementation", "US2"], "parallel": False, "story": "US2"},
    {"id": "T050", "phase": "phase-4", "description": "Add filter command with status option to CLI in src/ticklisto/cli/commands.py", "labels": ["phase-4", "implementation", "US2"], "parallel": False, "story": "US2"},
    {"id": "T051", "phase": "phase-4", "description": "Add filter command with priority option to CLI in src/ticklisto/cli/commands.py", "labels": ["phase-4", "implementation", "US2"], "parallel": False, "story": "US2"},
    {"id": "T052", "phase": "phase-4", "description": "Add filter command with date range options to CLI in src/ticklisto/cli/commands.py", "labels": ["phase-4", "implementation", "US2"], "parallel": False, "story": "US2"},
    {"id": "T053", "phase": "phase-4", "description": "Add filter command with category options (OR/AND toggle) to CLI in src/ticklisto/cli/commands.py", "labels": ["phase-4", "implementation", "US2"], "parallel": False, "story": "US2"},
    {"id": "T054", "phase": "phase-4", "description": "Add prompt for category filter logic toggle in src/ticklisto/cli/parsers.py", "labels": ["phase-4", "implementation", "US2"], "parallel": False, "story": "US2"},
    {"id": "T055", "phase": "phase-4", "description": "Display 'No tasks found' message with helpful suggestions in src/ticklisto/cli/display.py", "labels": ["phase-4", "implementation", "US2"], "parallel": False, "story": "US2"},

    # Phase 5: User Story 3 - Tests
    {"id": "T056", "phase": "phase-5", "description": "Write unit tests for sort by due date with secondary priority in tests/unit/test_sort_service.py", "labels": ["phase-5", "test", "tdd", "parallel", "US3"], "parallel": True, "story": "US3"},
    {"id": "T057", "phase": "phase-5", "description": "Write unit tests for sort by priority in tests/unit/test_sort_service.py", "labels": ["phase-5", "test", "tdd", "parallel", "US3"], "parallel": True, "story": "US3"},
    {"id": "T058", "phase": "phase-5", "description": "Write unit tests for sort alphabetically in tests/unit/test_sort_service.py", "labels": ["phase-5", "test", "tdd", "parallel", "US3"], "parallel": True, "story": "US3"},
    {"id": "T059", "phase": "phase-5", "description": "Write unit tests for handling tasks without due dates in tests/unit/test_sort_service.py", "labels": ["phase-5", "test", "tdd", "parallel", "US3"], "parallel": True, "story": "US3"},
    {"id": "T060", "phase": "phase-5", "description": "Write integration tests for CLI sort command in tests/integration/test_cli_commands.py", "labels": ["phase-5", "test", "tdd", "parallel", "US3"], "parallel": True, "story": "US3"},

    # Phase 5: User Story 3 - Implementation
    {"id": "T061", "phase": "phase-5", "description": "Create SortService with sort_tasks function in src/ticklisto/services/sort_service.py", "labels": ["phase-5", "implementation", "US3"], "parallel": False, "story": "US3"},
    {"id": "T062", "phase": "phase-5", "description": "Implement sort by due date with secondary priority sorting in src/ticklisto/services/sort_service.py", "labels": ["phase-5", "implementation", "US3"], "parallel": False, "story": "US3"},
    {"id": "T063", "phase": "phase-5", "description": "Implement sort by priority in src/ticklisto/services/sort_service.py", "labels": ["phase-5", "implementation", "US3"], "parallel": False, "story": "US3"},
    {"id": "T064", "phase": "phase-5", "description": "Implement sort alphabetically in src/ticklisto/services/sort_service.py", "labels": ["phase-5", "implementation", "US3"], "parallel": False, "story": "US3"},
    {"id": "T065", "phase": "phase-5", "description": "Add sort command to CLI with sort criteria options in src/ticklisto/cli/commands.py", "labels": ["phase-5", "implementation", "US3"], "parallel": False, "story": "US3"},
    {"id": "T066", "phase": "phase-5", "description": "Display 'No Due Date' section for tasks without due dates in src/ticklisto/cli/display.py", "labels": ["phase-5", "implementation", "US3"], "parallel": False, "story": "US3"},

    # Phase 6: User Story 4 - Tests
    {"id": "T067", "phase": "phase-6", "description": "Write integration tests for clear command in tests/integration/test_cli_commands.py", "labels": ["phase-6", "test", "tdd", "parallel", "US4"], "parallel": True, "story": "US4"},
    {"id": "T068", "phase": "phase-6", "description": "Write integration tests for clr alias in tests/integration/test_cli_commands.py", "labels": ["phase-6", "test", "tdd", "parallel", "US4"], "parallel": True, "story": "US4"},

    # Phase 6: User Story 4 - Implementation
    {"id": "T069", "phase": "phase-6", "description": "Implement clear_console function using Rich Console in src/ticklisto/cli/display.py", "labels": ["phase-6", "implementation", "US4"], "parallel": False, "story": "US4"},
    {"id": "T070", "phase": "phase-6", "description": "Add clear command to CLI in src/ticklisto/cli/commands.py", "labels": ["phase-6", "implementation", "US4"], "parallel": False, "story": "US4"},
    {"id": "T071", "phase": "phase-6", "description": "Add clr alias for clear command in src/ticklisto/cli/commands.py", "labels": ["phase-6", "implementation", "US4"], "parallel": False, "story": "US4"},

    # Phase 7: Polish & Cross-Cutting Concerns
    {"id": "T072", "phase": "phase-7", "description": "Update README.md with new features documentation", "labels": ["phase-7", "implementation", "parallel"], "parallel": True, "story": None},
    {"id": "T073", "phase": "phase-7", "description": "Add usage examples for priorities and categories to README.md", "labels": ["phase-7", "implementation", "parallel"], "parallel": True, "story": None},
    {"id": "T074", "phase": "phase-7", "description": "Add usage examples for search and filter to README.md", "labels": ["phase-7", "implementation", "parallel"], "parallel": True, "story": None},
    {"id": "T075", "phase": "phase-7", "description": "Add usage examples for sort to README.md", "labels": ["phase-7", "implementation", "parallel"], "parallel": True, "story": None},
    {"id": "T076", "phase": "phase-7", "description": "Add usage examples for clear command to README.md", "labels": ["phase-7", "implementation", "parallel"], "parallel": True, "story": None},
    {"id": "T077", "phase": "phase-7", "description": "Run performance validation for 10000 tasks (search <500ms, filter <300ms, sort <500ms)", "labels": ["phase-7", "test"], "parallel": False, "story": None},
    {"id": "T078", "phase": "phase-7", "description": "Run full test suite and verify 90%+ code coverage", "labels": ["phase-7", "test"], "parallel": False, "story": None},
    {"id": "T079", "phase": "phase-7", "description": "Verify backward compatibility with existing basic operations", "labels": ["phase-7", "test"], "parallel": False, "story": None},
    {"id": "T080", "phase": "phase-7", "description": "Code cleanup and refactoring (if needed)", "labels": ["phase-7", "implementation"], "parallel": False, "story": None},
]


def create_issue_body(task: Dict) -> str:
    """Generate the issue body with task details."""
    body_parts = [
        f"## Task Details",
        f"",
        f"**Task ID:** {task['id']}",
        f"**Phase:** {task['phase']}",
        f"**Description:** {task['description']}",
        f"",
    ]

    if task['story']:
        body_parts.append(f"**User Story:** {task['story']}")
        body_parts.append("")

    if task['parallel']:
        body_parts.append("**Parallel Execution:** This task can be executed in parallel with other [P] tasks")
        body_parts.append("")

    # Add phase-specific context
    phase_context = {
        "phase-1": "**Phase Context:** Setup - Project initialization and dependency management",
        "phase-2": "**Phase Context:** Foundational - Core infrastructure that MUST be complete before ANY user story can be implemented",
        "phase-3": "**Phase Context:** User Story 1 - Add Task Priorities & Categories (Priority: P1) 🎯 MVP",
        "phase-4": "**Phase Context:** User Story 2 - Search & Filter Tasks (Priority: P1)",
        "phase-5": "**Phase Context:** User Story 3 - Sort Tasks (Priority: P2)",
        "phase-6": "**Phase Context:** User Story 4 - Clear Interactive Session (Priority: P2)",
        "phase-7": "**Phase Context:** Polish & Cross-Cutting Concerns - Documentation, performance validation, and final integration",
    }

    if task['phase'] in phase_context:
        body_parts.append(phase_context[task['phase']])
        body_parts.append("")

    # Add TDD reminder for test tasks
    if 'test' in task['labels'] and 'tdd' in task['labels']:
        body_parts.append("## TDD Approach")
        body_parts.append("")
        body_parts.append("⚠️ **CRITICAL:** This is a TDD test task. The test MUST be written FIRST and MUST FAIL before implementation begins.")
        body_parts.append("")

    body_parts.append("## Acceptance Criteria")
    body_parts.append("")
    body_parts.append("- [ ] Task completed as described")

    if 'test' in task['labels']:
        body_parts.append("- [ ] Tests written and initially failing (Red phase)")
        body_parts.append("- [ ] Tests pass after implementation (Green phase)")
    else:
        body_parts.append("- [ ] Implementation complete")
        body_parts.append("- [ ] Related tests passing")

    body_parts.append("- [ ] Code reviewed")
    body_parts.append("- [ ] Changes committed with proper message")
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("*Generated from specs/002-intermediate-ticklisto-enhancements/tasks.md*")

    return "\n".join(body_parts)


def create_github_issue(task: Dict, dry_run: bool = False) -> bool:
    """Create a GitHub issue for the given task."""
    title = f"[{task['id']}] {task['description']}"
    body = create_issue_body(task)
    labels = ",".join(task['labels'])

    cmd = [
        "gh", "issue", "create",
        "--title", title,
        "--body", body,
        "--label", labels,
        "--repo", "sheikh-mohammad/hackathon-ii-evolution-of-todo"
    ]

    if dry_run:
        print(f"\n{'='*80}")
        print(f"Would create issue: {task['id']}")
        print(f"Title: {title}")
        print(f"Labels: {labels}")
        print(f"Body:\n{body}")
        return True

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issue_url = result.stdout.strip()
        print(f"[OK] Created {task['id']}: {issue_url}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Failed to create {task['id']}: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] Error creating {task['id']}: {str(e)}")
        return False


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Create GitHub issues for all tasks")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without actually creating issues")
    parser.add_argument("--start", type=int, default=1, help="Start from task number (default: 1)")
    parser.add_argument("--end", type=int, default=80, help="End at task number (default: 80)")

    args = parser.parse_args()

    print(f"{'='*80}")
    print(f"GitHub Issue Creation Script")
    print(f"Repository: sheikh-mohammad/hackathon-ii-evolution-of-todo")
    print(f"Total tasks: {len(tasks)}")
    print(f"Range: T{args.start:03d} to T{args.end:03d}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"{'='*80}\n")

    if not args.dry_run:
        # Verify gh CLI is available
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: GitHub CLI (gh) is not installed or not in PATH")
            print("Install from: https://cli.github.com/")
            sys.exit(1)

        # Verify authentication
        try:
            subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            print("ERROR: Not authenticated with GitHub CLI")
            print("Run: gh auth login")
            sys.exit(1)

    # Filter tasks based on range
    tasks_to_create = [t for t in tasks if args.start <= int(t['id'][1:]) <= args.end]

    success_count = 0
    failed_count = 0

    for task in tasks_to_create:
        if create_github_issue(task, dry_run=args.dry_run):
            success_count += 1
        else:
            failed_count += 1

    print(f"\n{'='*80}")
    print(f"Summary:")
    print(f"  Total: {len(tasks_to_create)}")
    print(f"  Success: {success_count}")
    print(f"  Failed: {failed_count}")
    print(f"{'='*80}")

    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
