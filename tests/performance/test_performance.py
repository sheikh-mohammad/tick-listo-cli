"""
Performance validation script for Tick Listo CLI.
Tests search, filter, and sort operations with 10,000 tasks.

Performance targets:
- Search: < 500ms
- Filter: < 300ms
- Sort: < 500ms
"""
import sys
import os
from pathlib import Path

# Add src directory to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

import time
from datetime import datetime, timedelta
import random
from tick_listo_cli.models.task import Task, Priority
from tick_listo_cli.services.search_service import SearchService
from tick_listo_cli.services.filter_service import FilterService
from tick_listo_cli.services.sort_service import SortService


def generate_test_tasks(count: int) -> list[Task]:
    """Generate test tasks with varied data."""
    tasks = []
    priorities = [Priority.HIGH, Priority.MEDIUM, Priority.LOW]
    categories_pool = ["work", "home", "personal", "urgent", "project", "meeting", "documentation"]

    today = datetime.now()

    for i in range(count):
        task = Task(
            id=i + 1,
            title=f"Task {i + 1}: {random.choice(['Complete', 'Review', 'Update', 'Fix', 'Implement'])} {random.choice(['project', 'documentation', 'feature', 'bug', 'report'])}",
            description=f"Description for task {i + 1} with some searchable content",
            priority=random.choice(priorities),
            categories=random.sample(categories_pool, k=random.randint(0, 3)),
            due_date=today + timedelta(days=random.randint(-10, 30)) if random.random() > 0.2 else None,
            completed=random.random() > 0.7
        )
        tasks.append(task)

    return tasks


def run_search_performance(tasks: list[Task], search_service: SearchService) -> dict:
    """Test search performance."""
    keywords = ["project", "documentation", "complete", "task", "feature"]
    results = {}

    for keyword in keywords:
        start = time.time()
        search_results = search_service.search_tasks(tasks, keyword)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        results[keyword] = {
            "elapsed_ms": elapsed,
            "results_count": len(search_results),
            "passed": elapsed < 500
        }

    return results


def run_filter_performance(tasks: list[Task], filter_service: FilterService) -> dict:
    """Test filter performance."""
    test_cases = [
        ("status_incomplete", {"status": "incomplete"}),
        ("priority_high", {"priority": Priority.HIGH}),
        ("categories_work", {"categories": ["work"], "category_match": "any"}),
        ("categories_multiple", {"categories": ["work", "urgent"], "category_match": "all"}),
        ("combined", {"status": "incomplete", "priority": Priority.HIGH, "categories": ["work"]})
    ]

    results = {}

    for name, criteria in test_cases:
        start = time.time()
        filter_results = filter_service.filter_tasks(tasks, **criteria)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        results[name] = {
            "elapsed_ms": elapsed,
            "results_count": len(filter_results),
            "passed": elapsed < 300
        }

    return results


def run_sort_performance(tasks: list[Task], sort_service: SortService) -> dict:
    """Test sort performance."""
    test_cases = [
        ("due_date", "due_date", None),
        ("due_date_priority", "due_date", "priority"),
        ("priority", "priority", None),
        ("priority_title", "priority", "title"),
        ("title", "title", None)
    ]

    results = {}

    for name, sort_by, secondary in test_cases:
        start = time.time()
        sorted_results = sort_service.sort_tasks(tasks, sort_by, secondary)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        results[name] = {
            "elapsed_ms": elapsed,
            "results_count": len(sorted_results),
            "passed": elapsed < 500
        }

    return results


def main():
    """Run performance validation."""
    print("=" * 70)
    print("TICK LISTO CLI PERFORMANCE VALIDATION")
    print("=" * 70)
    print()

    # Generate test data
    print("Generating 10,000 test tasks...")
    tasks = generate_test_tasks(10000)
    print(f"[OK] Generated {len(tasks)} tasks")
    print()

    # Initialize services
    search_service = SearchService()
    filter_service = FilterService()
    sort_service = SortService()

    # Test search performance
    print("-" * 70)
    print("SEARCH PERFORMANCE (Target: < 500ms)")
    print("-" * 70)
    search_results = run_search_performance(tasks, search_service)

    for keyword, result in search_results.items():
        status = "[PASS]" if result["passed"] else "[FAIL]"
        print(f"{status} | {keyword:20s} | {result['elapsed_ms']:6.2f}ms | {result['results_count']:5d} results")

    search_passed = all(r["passed"] for r in search_results.values())
    print()

    # Test filter performance
    print("-" * 70)
    print("FILTER PERFORMANCE (Target: < 300ms)")
    print("-" * 70)
    filter_results = run_filter_performance(tasks, filter_service)

    for name, result in filter_results.items():
        status = "[PASS]" if result["passed"] else "[FAIL]"
        print(f"{status} | {name:20s} | {result['elapsed_ms']:6.2f}ms | {result['results_count']:5d} results")

    filter_passed = all(r["passed"] for r in filter_results.values())
    print()

    # Test sort performance
    print("-" * 70)
    print("SORT PERFORMANCE (Target: < 500ms)")
    print("-" * 70)
    sort_results = run_sort_performance(tasks, sort_service)

    for name, result in sort_results.items():
        status = "[PASS]" if result["passed"] else "[FAIL]"
        print(f"{status} | {name:20s} | {result['elapsed_ms']:6.2f}ms | {result['results_count']:5d} results")

    sort_passed = all(r["passed"] for r in sort_results.values())
    print()

    # Overall summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Search: {'[PASS]' if search_passed else '[FAIL]'}")
    print(f"Filter: {'[PASS]' if filter_passed else '[FAIL]'}")
    print(f"Sort:   {'[PASS]' if sort_passed else '[FAIL]'}")
    print()

    if search_passed and filter_passed and sort_passed:
        print("[OK] ALL PERFORMANCE TARGETS MET")
        return 0
    else:
        print("[ERROR] SOME PERFORMANCE TARGETS NOT MET")
        return 1


if __name__ == "__main__":
    exit(main())
