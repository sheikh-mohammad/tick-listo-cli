<!-- Sync Impact Report:
Version change: 2.2.6 → 2.2.7 (Renamed the app to tick listo cli)
Added sections: none
Modified sections: whole constitution
Removed sections: none
Templates requiring updates: ⚠ pending manual review of .specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md
Follow-up TODOs: none
-->

# Tick Listo CLI Constitution

## Table of Contents
- [Core Principles](#core-principles)
  - [I. Spec-Driven Development (NON-NEGOTIABLE)](#i-spec-driven-development-non-negotiable)
  - [II. AI-Agent Driven Implementation](#ii-ai-agent-driven-implementation)
  - [III. Progressive Complexity Evolution](#iii-progressive-complexity-evolution)
  - [IV. Reusable Intelligence & Modularity](#iv-reusable-intelligence--modularity)
  - [V. Test-First (NON-NEGOTIABLE)](#v-test-first-non-negotiable)
  - [VI. Atomic Commits](#vi-atomic-commits)
  - [VII. Co-authoring with Claude Code](#vii-co-authoring-with-claude-code)
  - [VIII. Clean Architecture & Separation of Concerns](#viii-clean-architecture--separation-of-concerns)
- [Technology Stack Standards](#technology-stack-standards)
  - [Primary Technologies](#primary-technologies)
  - [Infrastructure & Deployment](#infrastructure--deployment)
- [Development Workflow](#development-workflow)
  - [Specification Process](#specification-process)
  - [Code Review & Quality Gates](#code-review--quality-gates)
- [Changelog](#changelog)
- [Governance](#governance)

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)
All development must follow the Spec-Driven Development methodology: Specification → Plan → Tasks → Implementation. No code may be written without a corresponding specification, plan, and task breakdown. This ensures alignment between requirements and implementation.

### II. AI-Agent Driven Implementation
All code must be generated using Claude Code or other approved AI agents following the Agentic Dev Stack workflow. Manual coding is prohibited. AI agents must follow the structured workflow defined in AGENTS.md and utilize Spec-Kit Plus for specification management.

### III. Progressive Complexity Evolution
Development follows a structured progression from simple to complex: starting with in-memory console applications in Phase I and evolving to full-stack web apps, AI chatbots, and cloud-native deployments in subsequent phases. Each phase builds upon the previous with increasing architectural sophistication. Currently focused on Phase I implementation.

### IV. Reusable Intelligence & Modularity
Components must be designed as reusable, modular units that can be leveraged across different phases and applications. Emphasis on creating reusable intelligence via Claude Code Subagents and Agent Skills to accelerate development.

### V. Test-First (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced. All features must have corresponding tests before implementation completion.

### VI. Atomic Commits
All changes must be committed individually as atomic units. Each commit should represent a single, cohesive change or improvement. Small tasks like adding a sentence, changing a file, or fixing a typo should be committed separately. This ensures clear history and easier debugging.

### VII. Co-authoring with Claude Code
All commits must include Claude Code as a co-author using the format: "Co-authored-by: Claude Code <claude-code@anthropic.com>". This acknowledges the AI collaboration and maintains proper attribution for all contributions made through AI assistance.

### VIII. Clean Architecture & Separation of Concerns
Maintain clear separation between different modules and functions within the console application. Each component should have well-defined interfaces and responsibilities to enable independent development and testing. In Phase I, focus on clean module organization and proper separation of concerns within the single console application.

## Technology Stack Standards

### Primary Technologies
- Python 3.13+ for console application development
- UV for package management
- UV for dependency management
- Pytest for testing
- Rich for beautiful CLI interfaces and terminal formatting
- GitHub for deployment
- Git for Version Control System
- Claude Code and Spec-Kit Plus for spec-driven development
- In-memory data storage for Phase I

### Infrastructure & Deployment
- Console-based user interface for Phase I
- Local development environment
- Spec-Driven Development workflow with Claude Code

## Development Workflow

### Specification Process
1. Write comprehensive specifications in the /specs directory following Spec-Kit Plus conventions for Phase I console application
2. Generate implementation plans that align with architectural constraints for in-memory Python console app
3. Break plans into atomic, testable tasks specific to Phase I requirements
4. Implement only what is specified in approved tasks for Phase I

> Note: All this will be done by you and user, wait for the prompt by the user. Means all these specification process are user-dependent.

### Code Review & Quality Gates
- All PRs must verify compliance with Phase I specification requirements
- Code must be generated via AI agents following AGENTS.md guidelines
- Specifications must be updated if requirements change during development
- Manual code changes require explicit exception approval
- Focus on implementing Basic Level features: Add Task, Delete Task, Update Task, View Task List, Mark as Complete

## Changelog

## Version 2.2.7 - 2026-03-09
- Updated the app name to tick listo cli

## Version 2.2.6 - 2026-01-29
- Updated the app name to tick listo

### Version 2.2.5 - 2026-01-28
- Updated technology stack to add Git for Version Control System in Phase I.

### Version 2.2.4 - 2026-01-26
- Added automatic Table of Contents section for easier navigation.

### Version 2.2.3 - 2026-01-26
- Updated technology stack to add Rich for beautiful CLI interfaces and terminal formatting in Phase I.

### Version 2.2.2 - 2026-01-25
- Updated technology stack to add pytest for testing.

### Version 2.2.1 - 2026-01-25
- Updated technology stack to add uv for dependency management and github for deployment.
- Updated development workflow by updating the specification process for human in the loop (user dependent).

### Version 2.1.0 - 2026-01-16
- Added Atomic Commits principle for small task management
- Added Co-authoring with Claude Code principle for proper attribution
- Renumbered principles to maintain sequence integrity

### Version 2.0.0 - 2026-01-16
- Updated technology stack to reflect Phase I requirements (Python console app, UV, in-memory storage)
- Modified Progressive Complexity Evolution to clarify current Phase I focus
- Updated Clean Architecture principle to reflect console application context
- Revised Development Workflow to emphasize Phase I specific requirements
- Added focus on Basic Level features: Add, Delete, Update, View, Mark Complete
- Added Changelog section to document version history

### Version 1.0.0 - 2026-01-16
- Initial constitution created for Todo App Hackathon II
- Established core principles: Spec-Driven Development, AI-Agent Implementation, Progressive Complexity
- Defined initial technology stack and development workflow

## Governance

This constitution supersedes all other development practices. Amendments require documentation of the change, approval from project maintainers, and a migration plan for existing code. All development activities must comply with these principles and can be audited for compliance.

**Version**: 2.2.7 | **Ratified**: 2026-01-16 | **Last Amended**: 2026-03-09