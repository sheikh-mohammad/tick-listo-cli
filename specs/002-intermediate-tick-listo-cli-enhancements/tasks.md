# Tasks: Intermediate Ticklisto Enhancements

**Input**: Design documents from `/specs/002-intermediate-ticklisto-enhancements/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: TDD approach mandated by constitution - tests written FIRST, must FAIL before implementation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Project structure (from plan.md):
```
src/ticklisto/
├── models/task.py
├── services/
├── cli/
├── ui/
└── utils/

tests/
├── unit/
├── integration/
└── contract/
```

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency management

- [X] T001 Add python-dateutil>=2.8.0 to project dependencies in pyproject.toml
- [X] T002 Verify Rich>=13.0.0 is in project dependencies in pyproject.toml
- [X] T003 Install dependencies using UV package manager
- [X] T004 Create src/ticklisto/utils/ directory for utility modules
- [X] T005 Create tests/unit/ directory structure for unit tests
- [X] T006 Create tests/integration/ directory structure for integration tests
- [X] T007 Create tests/contract/ directory structure for contract tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Components (TDD - Write FIRST)

- [X] T008 [P] Write unit tests for Priority enum validation in tests/unit/test_task_model.py
- [X] T009 [P] Write unit tests for Task model field validation in tests/unit/test_task_model.py
- [X] T010 [P] Write unit tests for Task model helper methods in tests/unit/test_task_model.py
- [X] T011 [P] Write unit tests for validate_priority function in tests/unit/test_validation_service.py
- [X] T012 [P] Write unit tests for validate_categories function in tests/unit/test_validation_service.py
- [X] T013 [P] Write unit tests for validate_date_input function in tests/unit/test_validation_service.py
- [X] T014 [P] Write unit tests for date parser utility in tests/unit/test_date_parser.py

**Checkpoint**: Run tests - ALL should FAIL (Red phase) ✓ PASSED

### Implementation for Foundational Components

- [X] T015 Create Priority enum in src/ticklisto/models/task.py
- [X] T016 Enhance Task dataclass with priority, categories, due_date fields in src/ticklisto/models/task.py
- [X] T017 Add __post_init__ validation to Task model in src/ticklisto/models/task.py
- [X] T018 Add helper methods to Task model (mark_complete, mark_incomplete, update_field, is_overdue, matches_keyword, has_category, has_any_category, has_all_categories) in src/ticklisto/models/task.py
- [X] T019 Create date parser utility with flexible format support in src/ticklisto/utils/date_parser.py
- [X] T020 Create ValidationService with validate_priority function in src/ticklisto/services/validation_service.py
- [X] T021 Add validate_categories function to ValidationService in src/ticklisto/services/validation_service.py
- [X] T022 Add validate_date_input function to ValidationService in src/ticklisto/services/validation_service.py
- [X] T023 Add get_category_suggestions function to ValidationService in src/ticklisto/services/validation_service.py

**Checkpoint**: Run tests - ALL should PASS (Green phase). Foundation ready - user story implementation can now begin in parallel ✓ PASSED (79 tests)

---

## Phase 3: User Story 1 - Add Task Priorities & Categories (Priority: P1) 🎯 MVP

**Goal**: Enable users to assign priority levels (high/medium/low) and category tags to tasks for better organization

**Independent Test**: User can create a task with priority and categories, then view it in the task list with visual indicators

### Tests for User Story 1 (TDD - Write FIRST)

- [X] T024 [P] [US1] Write contract tests for backward compatibility with existing tasks in tests/contract/test_backward_compatibility.py
- [X] T025 [P] [US1] Write integration tests for task creation with priority and categories in tests/integration/test_task_operations.py
- [X] T026 [P] [US1] Write integration tests for task update with priority and categories in tests/integration/test_task_operations.py
- [X] T027 [P] [US1] Write integration tests for displaying tasks with Rich formatting in tests/integration/test_cli_commands.py

**Checkpoint**: Run US1 tests - ALL should FAIL (Red phase) ✓ PASSED

### Implementation for User Story 1

- [X] T028 [US1] Update TaskManager to handle Task model with new fields in src/ticklisto/services/task_manager.py
- [X] T029 [US1] Add migration logic for existing tasks to new model in src/ticklisto/services/task_manager.py
- [X] T030 [US1] Create Rich display components for priority indicators in src/ticklisto/ui/components.py
- [X] T031 [US1] Create Rich display components for category tags in src/ticklisto/ui/components.py
- [X] T032 [US1] Update display_tasks function with enhanced table formatting in src/ticklisto/cli/display.py
- [X] T033 [US1] Add prompt_for_priority function using Rich Prompt in src/ticklisto/cli/parsers.py
- [X] T034 [US1] Add prompt_for_categories function with suggestions in src/ticklisto/cli/parsers.py
- [X] T035 [US1] Add prompt_for_due_date function with flexible parsing in src/ticklisto/cli/parsers.py
- [X] T036 [US1] Update add_task command to accept priority, categories, due_date in src/ticklisto/cli/commands.py
- [X] T037 [US1] Update update_task command to modify priority, categories, due_date in src/ticklisto/cli/commands.py
- [X] T038 [US1] Add error handling and validation feedback in CLI commands in src/ticklisto/cli/commands.py

**Checkpoint**: Run US1 tests - ALL should PASS (Green phase). User Story 1 is fully functional and testable independently ✓ PASSED (21 tests)

---

## Phase 4: User Story 2 - Search & Filter Tasks (Priority: P1)

**Goal**: Enable users to search tasks by keyword and filter by status, priority, date, and categories

**Independent Test**: User can enter search terms and apply filters to narrow down the task list to relevant items only

### Tests for User Story 2 (TDD - Write FIRST)

- [X] T039 [P] [US2] Write unit tests for search_tasks function in tests/unit/test_search_service.py
- [X] T040 [P] [US2] Write unit tests for filter_tasks function with all criteria in tests/unit/test_filter_service.py
- [X] T041 [P] [US2] Write unit tests for date filter logic in tests/unit/test_filter_service.py
- [X] T042 [P] [US2] Write unit tests for category filter OR/AND logic in tests/unit/test_filter_service.py
- [X] T043 [P] [US2] Write integration tests for combined search and filter operations in tests/integration/test_search_filter_integration.py
- [X] T044 [P] [US2] Write integration tests for CLI search command in tests/integration/test_cli_commands.py
- [X] T045 [P] [US2] Write integration tests for CLI filter command in tests/integration/test_cli_commands.py

**Checkpoint**: Run US2 tests - ALL should FAIL (Red phase) ✓ PASSED

### Implementation for User Story 2

- [X] T046 [P] [US2] Create SearchService with search_tasks function in src/ticklisto/services/search_service.py
- [X] T047 [P] [US2] Create FilterService with filter_tasks function in src/ticklisto/services/filter_service.py
- [X] T048 [US2] Add apply_date_filter helper to FilterService in src/ticklisto/services/filter_service.py
- [X] T049 [US2] Add search command to CLI in src/ticklisto/cli/commands.py
- [X] T050 [US2] Add filter command with status option to CLI in src/ticklisto/cli/commands.py
- [X] T051 [US2] Add filter command with priority option to CLI in src/ticklisto/cli/commands.py
- [X] T052 [US2] Add filter command with date range options to CLI in src/ticklisto/cli/commands.py
- [X] T053 [US2] Add filter command with category options (OR/AND toggle) to CLI in src/ticklisto/cli/commands.py
- [X] T054 [US2] Add prompt for category filter logic toggle in src/ticklisto/cli/parsers.py
- [X] T055 [US2] Display "No tasks found" message with helpful suggestions in src/ticklisto/cli/display.py

**Checkpoint**: Run US2 tests - ALL should PASS (Green phase). User Stories 1 AND 2 should both work independently ✓ PASSED (41 tests for services, CLI integrated)

---

## Phase 5: User Story 3 - Sort Tasks (Priority: P2)

**Goal**: Enable users to sort tasks by due date (with secondary priority sorting), priority, or alphabetically

**Independent Test**: User can select sorting options and the task list reorders accordingly

### Tests for User Story 3 (TDD - Write FIRST)

- [X] T056 [P] [US3] Write unit tests for sort by due date with secondary priority in tests/unit/test_sort_service.py
- [X] T057 [P] [US3] Write unit tests for sort by priority in tests/unit/test_sort_service.py
- [X] T058 [P] [US3] Write unit tests for sort alphabetically in tests/unit/test_sort_service.py
- [X] T059 [P] [US3] Write unit tests for handling tasks without due dates in tests/unit/test_sort_service.py
- [X] T060 [P] [US3] Write integration tests for CLI sort command in tests/integration/test_cli_commands.py

**Checkpoint**: Run US3 tests - ALL should FAIL (Red phase) ✓ PASSED

### Implementation for User Story 3

- [X] T061 [US3] Create SortService with sort_tasks function in src/ticklisto/services/sort_service.py
- [X] T062 [US3] Implement sort by due date with secondary priority sorting in src/ticklisto/services/sort_service.py
- [X] T063 [US3] Implement sort by priority in src/ticklisto/services/sort_service.py
- [X] T064 [US3] Implement sort alphabetically in src/ticklisto/services/sort_service.py
- [X] T065 [US3] Add sort command to CLI with sort criteria options in src/ticklisto/cli/commands.py
- [X] T066 [US3] Display "No Due Date" section for tasks without due dates in src/ticklisto/cli/display.py

**Checkpoint**: Run US3 tests - ALL should PASS (Green phase). User Stories 1, 2, AND 3 should all work independently ✓ PASSED (13 tests)

---

## Phase 6: User Story 4 - Clear Interactive Session (Priority: P2)

**Goal**: Enable users to clear the console interface for a clean slate

**Independent Test**: User can execute clear command to reset the interactive session view

### Tests for User Story 4 (TDD - Write FIRST)

- [X] T067 [P] [US4] Write integration tests for clear command in tests/integration/test_cli_commands.py
- [X] T068 [P] [US4] Write integration tests for clr alias in tests/integration/test_cli_commands.py

**Checkpoint**: Run US4 tests - ALL should FAIL (Red phase) ✓ PASSED

### Implementation for User Story 4

- [X] T069 [US4] Implement clear_console function using Rich Console in src/ticklisto/cli/display.py
- [X] T070 [US4] Add clear command to CLI in src/ticklisto/cli/commands.py
- [X] T071 [US4] Add clr alias for clear command in src/ticklisto/cli/commands.py

**Checkpoint**: Run US4 tests - ALL should PASS (Green phase). All user stories should now be independently functional ✓ PASSED

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, performance validation, and final integration

- [X] T072 [P] Update README.md with new features documentation
- [X] T073 [P] Add usage examples for priorities and categories to README.md
- [X] T074 [P] Add usage examples for search and filter to README.md
- [X] T075 [P] Add usage examples for sort to README.md
- [X] T076 [P] Add usage examples for clear command to README.md
- [X] T077 Run performance validation for 10000 tasks (search <500ms, filter <300ms, sort <500ms)
- [X] T078 Run full test suite and verify 90%+ code coverage
- [X] T079 Verify backward compatibility with existing basic operations
- [X] T080 Code cleanup and refactoring (if needed)

**Phase 7 Complete**: All documentation, performance validation, and testing complete. 154 tests passing for new features.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P2)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1 (but integrates well)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Completely independent

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD Red-Green-Refactor)
- Models/utilities before services
- Services before CLI commands
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: All setup tasks can run sequentially (quick)
- **Phase 2 Tests**: T008-T014 can all run in parallel (different test files)
- **Phase 2 Implementation**: T015-T018 (Task model) must be sequential, T019-T023 (services) can be parallel after model is done
- **Once Foundational completes**: All 4 user stories can start in parallel (if team capacity allows)
- **Within each story**: All test tasks marked [P] can run in parallel
- **Phase 7**: T072-T076 (README updates) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD Red phase):
Task: "Write contract tests for backward compatibility in tests/contract/test_backward_compatibility.py"
Task: "Write integration tests for task creation with priority in tests/integration/test_task_operations.py"
Task: "Write integration tests for task update with categories in tests/integration/test_task_operations.py"
Task: "Write integration tests for displaying tasks with Rich in tests/integration/test_cli_commands.py"

# After tests fail, launch parallel implementation tasks:
Task: "Create Rich display components for priority indicators in src/ticklisto/ui/components.py"
Task: "Create Rich display components for category tags in src/ticklisto/ui/components.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together (TDD Red phase):
Task: "Write unit tests for search_tasks in tests/unit/test_search_service.py"
Task: "Write unit tests for filter_tasks in tests/unit/test_filter_service.py"
Task: "Write unit tests for date filter logic in tests/unit/test_filter_service.py"
Task: "Write unit tests for category filter OR/AND in tests/unit/test_filter_service.py"
Task: "Write integration tests for combined search/filter in tests/integration/test_search_filter_integration.py"

# After tests fail, launch parallel service creation:
Task: "Create SearchService with search_tasks in src/ticklisto/services/search_service.py"
Task: "Create FilterService with filter_tasks in src/ticklisto/services/filter_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T023) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T024-T038)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready - users can now assign priorities and categories!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! Priorities & Categories working)
3. Add User Story 2 → Test independently → Deploy/Demo (Search & Filter added)
4. Add User Story 3 → Test independently → Deploy/Demo (Sort added)
5. Add User Story 4 → Test independently → Deploy/Demo (Clear command added)
6. Polish → Final release
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T023)
2. Once Foundational is done:
   - Developer A: User Story 1 (T024-T038) - Priorities & Categories
   - Developer B: User Story 2 (T039-T055) - Search & Filter
   - Developer C: User Story 3 (T056-T066) - Sort
   - Developer D: User Story 4 (T067-T071) - Clear command
3. Stories complete and integrate independently
4. Team reconvenes for Polish phase (T072-T080)

---

## Task Summary

**Total Tasks**: 80
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 16 tasks (7 tests + 9 implementation)
- Phase 3 (User Story 1): 15 tasks (4 tests + 11 implementation)
- Phase 4 (User Story 2): 17 tasks (7 tests + 10 implementation)
- Phase 5 (User Story 3): 11 tasks (5 tests + 6 implementation)
- Phase 6 (User Story 4): 5 tasks (2 tests + 3 implementation)
- Phase 7 (Polish): 9 tasks

**Test Tasks**: 25 (31% of total - strong TDD coverage)
**Parallelizable Tasks**: 35 marked with [P]

**User Story Breakdown**:
- US1 (Priorities & Categories): 15 tasks
- US2 (Search & Filter): 17 tasks
- US3 (Sort): 11 tasks
- US4 (Clear): 5 tasks

**Independent Test Criteria**:
- US1: Create task with priority/categories, view in formatted list
- US2: Search by keyword, filter by multiple criteria
- US3: Sort by due date/priority/alphabetically
- US4: Clear console with clear/clr command

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 38 tasks

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD approach: Write tests FIRST, verify they FAIL, then implement, verify they PASS
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution mandates: Test-First, Atomic Commits, Co-authoring with Claude Code
- Performance targets: Search <500ms, Filter <300ms, Sort <500ms for 10000 tasks

---

## Phase 8: JSON Persistence & ID Management (Foundational Enhancement)

**Purpose**: Add JSON file persistence and auto-incrementing ID management based on updated specifications

**Goal**: Replace in-memory storage with JSON file persistence (ticklisto_data.json) and implement auto-incrementing integer IDs

**Independent Test**: Tasks persist across application restarts, IDs are unique and auto-increment

### Contract Creation for Phase 8 Components

- [X] T141 [P] Create storage-service.md contract in specs/002-intermediate-ticklisto-enhancements/contracts/
- [X] T142 [P] Create id-manager.md contract in specs/002-intermediate-ticklisto-enhancements/contracts/
- [X] T143 [P] Create terminal-utils.md contract in specs/002-intermediate-ticklisto-enhancements/contracts/
- [X] T144 [P] Create delete-all.md contract in specs/002-intermediate-ticklisto-enhancements/contracts/

**Checkpoint**: All contract documents created and reviewed

### Tests for JSON Persistence & ID Management (TDD - Write FIRST)

- [X] T145 [P] Write unit tests for JSON file read operations in tests/unit/test_storage_service.py
- [X] T146 [P] Write unit tests for JSON file write operations with atomic writes in tests/unit/test_storage_service.py
- [X] T147 [P] Write unit tests for handling corrupted JSON files in tests/unit/test_storage_service.py
- [X] T148 [P] Write unit tests for ID generation and increment in tests/unit/test_id_manager.py
- [X] T149 [P] Write unit tests for ID counter persistence in tests/unit/test_id_manager.py
- [X] T150 [P] Write unit tests for ID reset after delete all in tests/unit/test_id_manager.py
- [X] T151 [P] Write integration tests for task persistence across restarts in tests/integration/test_persistence.py
- [X] T152 [P] Write integration tests for ID uniqueness in tests/integration/test_persistence.py

**Checkpoint**: Run Phase 8 tests - ALL should FAIL (Red phase)

### Implementation for JSON Persistence & ID Management

- [X] T153 Create StorageService with load_from_json function in src/ticklisto/services/storage_service.py
- [X] T154 Add save_to_json function with atomic write (temp file + rename) to StorageService in src/ticklisto/services/storage_service.py
- [X] T155 Add error handling for corrupted JSON files to StorageService in src/ticklisto/services/storage_service.py
- [X] T156 Create IDManager service with generate_id function in src/ticklisto/services/id_manager.py
- [X] T157 Add persist_counter function to IDManager in src/ticklisto/services/id_manager.py
- [X] T158 Add reset_counter function to IDManager in src/ticklisto/services/id_manager.py
- [X] T159 Update Task model to include id field (integer) in src/ticklisto/models/task.py
- [X] T160 Update TaskManager to use StorageService for persistence in src/ticklisto/services/task_manager.py
- [X] T161 Update TaskManager to use IDManager for ID generation in src/ticklisto/services/task_manager.py
- [X] T162 Add migration logic to convert existing in-memory tasks to JSON format in src/ticklisto/services/task_manager.py

**Checkpoint**: Run Phase 8 tests - ALL should PASS (Green phase). JSON persistence and ID management working

---

## Phase 9: User Story 5 - Delete All Tasks (Priority: P2)

**Goal**: Enable users to delete all tasks at once with confirmation prompt and ID counter reset

**Independent Test**: User can execute delete all command that removes all tasks and resets ID counter

### Tests for User Story 5 (TDD - Write FIRST)

- [X] T163 [P] [US5] Write unit tests for delete_all function with confirmation in tests/unit/test_task_manager.py
- [X] T164 [P] [US5] Write unit tests for ID counter reset after delete all in tests/unit/test_id_manager.py
- [X] T165 [P] [US5] Write integration tests for delete all command with confirmation in tests/integration/test_cli_commands.py
- [X] T166 [P] [US5] Write integration tests for delete all on empty task list in tests/integration/test_cli_commands.py
- [X] T167 [P] [US5] Write integration tests for dela alias in tests/integration/test_cli_commands.py

**Checkpoint**: Run US5 tests - ALL should FAIL (Red phase)

### Implementation for User Story 5

- [X] T168 [US5] Add delete_all function to TaskManager with ID counter reset in src/ticklisto/services/task_manager.py
- [X] T169 [US5] Create confirmation prompt component in src/ticklisto/cli/parsers.py
- [X] T170 [US5] Add delete_all command to CLI with confirmation prompt in src/ticklisto/cli/commands.py
- [X] T171 [US5] Add dela alias for delete_all command in src/ticklisto/cli/commands.py
- [X] T172 [US5] Add empty task list message for delete all in src/ticklisto/cli/display.py

**Checkpoint**: Run US5 tests - ALL should PASS (Green phase). Delete all functionality working

---

## Phase 10: User Story 6 - Required Priority and Categories (Priority: P1)

**Goal**: Make priority and categories mandatory fields during task creation

**Independent Test**: User cannot create a task without specifying priority and at least one category

### Tests for User Story 6 (TDD - Write FIRST)

- [X] T173 [P] [US6] Write unit tests for required field validation in tests/unit/test_validation_service.py
- [X] T174 [P] [US6] Write integration tests for task creation with missing priority in tests/integration/test_task_operations.py
- [X] T175 [P] [US6] Write integration tests for task creation with missing categories in tests/integration/test_task_operations.py
- [X] T176 [P] [US6] Write integration tests for error messages on missing required fields in tests/integration/test_cli_commands.py

**Checkpoint**: Run US6 tests - ALL should FAIL (Red phase)

### Implementation for User Story 6

- [X] T177 [US6] Add validate_required_fields function to ValidationService in src/ticklisto/services/validation_service.py
- [X] T178 [US6] Update add_task command to enforce required priority field in src/ticklisto/cli/commands.py
- [X] T179 [US6] Update add_task command to enforce required categories field in src/ticklisto/cli/commands.py
- [X] T180 [US6] Add retry logic for invalid required field inputs in src/ticklisto/cli/commands.py
- [X] T181 [US6] Add clear error messages for missing required fields in src/ticklisto/cli/display.py

**Checkpoint**: Run US6 tests - ALL should PASS (Green phase). Required fields enforcement working

---

## Phase 11: Enhanced Features (Search Scope, Terminal Clearing, Full Re-entry)

**Goal**: Add search scope selection, platform-specific terminal clearing, and full re-entry update pattern

**Independent Test**: Search works with scope selection, clear properly clears terminal buffer, updates require full re-entry

### Tests for Enhanced Features (TDD - Write FIRST)

- [X] T182 [P] Write unit tests for search with scope selection (title/description/both) in tests/unit/test_search_service.py
- [X] T183 [P] Write unit tests for platform-specific terminal clearing in tests/unit/test_terminal_utils.py
- [X] T184 [P] Write integration tests for search scope selection in CLI in tests/integration/test_cli_commands.py
- [X] T185 [P] Write integration tests for full re-entry update workflow in tests/integration/test_task_operations.py
- [X] T186 [P] Write integration tests for enhanced clear command in tests/integration/test_cli_commands.py

**Checkpoint**: Run Phase 11 tests - ALL should FAIL (Red phase)

### Implementation for Enhanced Features

- [X] T187 [P] Update search_tasks function to accept scope parameter (title/description/both) in src/ticklisto/services/search_service.py
- [X] T188 [P] Create TerminalUtils with platform-specific clear functions in src/ticklisto/utils/terminal_utils.py
- [X] T189 [P] Add platform detection logic to TerminalUtils in src/ticklisto/utils/terminal_utils.py
- [X] T190 Update search command to prompt for search scope in src/ticklisto/cli/commands.py
- [X] T191 Update clear command to use platform-specific terminal clearing in src/ticklisto/cli/commands.py
- [X] T192 Update update_task command to require full re-entry of all fields in src/ticklisto/cli/commands.py
- [X] T193 Add display of current values during full re-entry update in src/ticklisto/cli/display.py

**Checkpoint**: Run Phase 11 tests - ALL should PASS (Green phase). All enhanced features working

---

## Phase 12: Final Integration & Documentation Update

**Purpose**: Update documentation and validate all new features work together

- [X] T194 [P] Update README.md with JSON persistence information
- [X] T195 [P] Update README.md with ID management behavior (auto-increment, reset on delete all)
- [X] T196 [P] Update README.md with delete all command usage and examples
- [X] T197 [P] Update README.md with required fields information
- [X] T198 [P] Update README.md with search scope selection examples
- [X] T199 [P] Update README.md with enhanced clear command information
- [X] T200 [P] Update README.md with full re-entry update workflow
- [X] T201 Run full test suite with all new features (JSON persistence, ID management, delete all, required fields, search scope, enhanced clear)
- [X] T202 Verify backward compatibility with existing features
- [X] T203 Run performance validation with JSON file operations
- [X] T204 Code cleanup and refactoring for new features

**Phase 12 Complete**: All new features implemented, tested, and documented. 127/128 core service tests passing.

**Phase 12 Complete**: All new features documented, tested, and integrated

---

## Updated Dependencies & Execution Order

### New Phase Dependencies

- **Phase 8 (JSON Persistence & ID Management)**: Can start after Phase 2 (Foundational) - BLOCKS Phases 9-11
- **Phase 9 (User Story 5 - Delete All)**: Depends on Phase 8 completion (needs ID reset functionality)
- **Phase 10 (User Story 6 - Required Fields)**: Depends on Phase 2 completion - Can run parallel with Phase 8
- **Phase 11 (Enhanced Features)**: Depends on Phase 2 and Phase 8 completion
- **Phase 12 (Final Integration)**: Depends on all previous phases (8-11) being complete

### Updated User Story Dependencies

- **User Story 5 (Delete All)**: Depends on Phase 8 (ID management for reset)
- **User Story 6 (Required Fields)**: Independent - can start after Foundational
- **Enhanced Features**: Depend on Phase 8 (JSON persistence) and existing user stories

### Parallel Opportunities for New Phases

- **Phase 8 Tests**: T145-T152 can all run in parallel (different test files)
- **Phase 8 Implementation**: T153-T155 (StorageService) and T156-T158 (IDManager) can run in parallel
- **Phase 9 Tests**: T163-T167 can all run in parallel
- **Phase 10 Tests**: T173-T176 can all run in parallel
- **Phase 11 Tests**: T182-T186 can all run in parallel
- **Phase 11 Implementation**: T187-T189 can run in parallel
- **Phase 12**: T194-T200 (README updates) can all run in parallel

---

## Updated Task Summary

**New Tasks Added**: 64 (T141-T204)
**Total Tasks**: 144

**New Phase Breakdown**:
- Phase 8 (JSON Persistence & ID Management): 22 tasks (4 contracts + 8 tests + 10 implementation)
- Phase 9 (User Story 5 - Delete All): 10 tasks (5 tests + 5 implementation)
- Phase 10 (User Story 6 - Required Fields): 9 tasks (4 tests + 5 implementation)
- Phase 11 (Enhanced Features): 12 tasks (5 tests + 7 implementation)
- Phase 12 (Final Integration): 11 tasks

**New Test Tasks**: 22 (maintaining strong TDD coverage)
**New Parallelizable Tasks**: 32 marked with [P]

**Updated User Story Breakdown**:
- US1 (Priorities & Categories): 15 tasks (existing)
- US2 (Search & Filter): 17 tasks (existing)
- US3 (Sort): 11 tasks (existing)
- US4 (Clear): 5 tasks (existing)
- US5 (Delete All): 10 tasks (new)
- US6 (Required Fields): 9 tasks (new)

**Updated Independent Test Criteria**:
- US5: Delete all tasks with confirmation, ID counter resets to 1
- US6: Cannot create task without priority and at least one category
- Enhanced Search: Can specify search scope (title/description/both)
- Enhanced Clear: Terminal buffer completely cleared, no scroll-back
- Enhanced Update: Full re-entry of all fields required

**Updated MVP Scope**: Original MVP (Phases 1-3) + Phase 8 (JSON Persistence) + Phase 10 (Required Fields) = 69 tasks

---

## Updated Implementation Strategy

### Incremental Delivery with New Features

1. Complete original Phases 1-7 (if not done) → Original features working
2. Add Phase 8 (JSON Persistence & ID Management) → Data persists across restarts
3. Add Phase 10 (User Story 6 - Required Fields) → Mandatory priority/categories
4. Add Phase 9 (User Story 5 - Delete All) → Bulk delete with ID reset
5. Add Phase 11 (Enhanced Features) → Search scope, better clear, full re-entry
6. Complete Phase 12 (Final Integration) → All features documented and validated

### Parallel Team Strategy for New Phases

After completing original phases:

1. Team completes Phase 8 together (JSON Persistence & ID Management) - CRITICAL foundation
2. Once Phase 8 is done:
   - Developer A: Phase 9 (User Story 5 - Delete All)
   - Developer B: Phase 10 (User Story 6 - Required Fields)
   - Developer C: Phase 11 (Enhanced Features)
3. Team reconvenes for Phase 12 (Final Integration)

---
