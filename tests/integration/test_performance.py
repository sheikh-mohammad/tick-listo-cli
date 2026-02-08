"""Performance tests for TickListo (T110 - Phase 10).

Tests that operations with 1000+ tasks complete in under 1 second.
"""

import pytest
import time
import os
from datetime import datetime, timedelta, time as dt_time
from ticklisto.models.task import Task, Priority, TaskStatus
from ticklisto.services.task_service import TaskService
from ticklisto.services.sort_service import SortService


class TestPerformanceWith1000Tasks:
    """Test performance with 1000+ tasks."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test with clean data file."""
        self.test_file = "test_performance.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

        self.service = TaskService(data_file=self.test_file)

        yield

        # Cleanup
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_1000_tasks_performance(self):
        """Test adding 1000 tasks completes in reasonable time."""
        start_time = time.time()

        # Add 1000 tasks
        for i in range(1000):
            self.service.add_task(
                title=f"Task {i}",
                description=f"Description for task {i}",
                priority=Priority.MEDIUM,
                categories=["test", f"category{i % 10}"]
            )

        elapsed = time.time() - start_time

        # Should complete in under 5 seconds for 1000 tasks
        assert elapsed < 5.0, f"Adding 1000 tasks took {elapsed:.2f}s (expected < 5s)"

        # Verify all tasks were added
        all_tasks = self.service.get_all()
        assert len(all_tasks) == 1000

    def test_list_1000_tasks_performance(self):
        """Test listing 1000 tasks completes in under 1 second."""
        # Add 1000 tasks first
        for i in range(1000):
            self.service.add_task(
                title=f"Task {i}",
                description=f"Description {i}",
                priority=Priority.MEDIUM,
                categories=["test"]
            )

        # Measure list operation
        start_time = time.time()
        all_tasks = self.service.get_all()
        elapsed = time.time() - start_time

        assert elapsed < 1.0, f"Listing 1000 tasks took {elapsed:.2f}s (expected < 1s)"
        assert len(all_tasks) == 1000

    def test_search_1000_tasks_performance(self):
        """Test searching through 1000 tasks completes in under 1 second."""
        # Add 1000 tasks with varied titles
        for i in range(1000):
            self.service.add_task(
                title=f"Task {i} - {'important' if i % 100 == 0 else 'regular'}",
                description=f"Description {i}",
                priority=Priority.HIGH if i % 100 == 0 else Priority.MEDIUM,
                categories=["test"]
            )

        # Measure search operation
        start_time = time.time()
        all_tasks = self.service.get_all()
        results = [t for t in all_tasks if "important" in t.title.lower()]
        elapsed = time.time() - start_time

        assert elapsed < 1.0, f"Searching 1000 tasks took {elapsed:.2f}s (expected < 1s)"
        assert len(results) == 10  # Should find 10 "important" tasks

    def test_filter_by_category_1000_tasks_performance(self):
        """Test filtering 1000 tasks by category completes in under 1 second."""
        # Add 1000 tasks with different categories
        for i in range(1000):
            self.service.add_task(
                title=f"Task {i}",
                description=f"Description {i}",
                priority=Priority.MEDIUM,
                categories=[f"category{i % 10}"]
            )

        # Measure filter operation
        start_time = time.time()
        all_tasks = self.service.get_all()
        results = [t for t in all_tasks if "category5" in t.categories]
        elapsed = time.time() - start_time

        assert elapsed < 1.0, f"Filtering 1000 tasks took {elapsed:.2f}s (expected < 1s)"
        assert len(results) == 100  # Should find 100 tasks in category5

    def test_filter_by_priority_1000_tasks_performance(self):
        """Test filtering 1000 tasks by priority completes in under 1 second."""
        # Add 1000 tasks with different priorities
        for i in range(1000):
            priority = Priority.HIGH if i % 3 == 0 else Priority.MEDIUM
            self.service.add_task(
                title=f"Task {i}",
                description=f"Description {i}",
                priority=priority,
                categories=["test"]
            )

        # Measure filter operation
        start_time = time.time()
        all_tasks = self.service.get_all()
        results = [t for t in all_tasks if t.priority == Priority.HIGH]
        elapsed = time.time() - start_time

        assert elapsed < 1.0, f"Filtering by priority took {elapsed:.2f}s (expected < 1s)"
        assert len(results) == 334  # Should find ~334 high priority tasks

    def test_sort_1000_tasks_performance(self):
        """Test sorting 1000 tasks completes in under 1 second."""
        # Add 1000 tasks with varied due dates
        base_date = datetime(2026, 3, 1)
        for i in range(1000):
            self.service.add_task(
                title=f"Task {i}",
                description=f"Description {i}",
                priority=Priority.MEDIUM,
                categories=["test"],
                due_date=base_date + timedelta(days=i % 100)
            )

        all_tasks = self.service.get_all()
        sort_service = SortService()

        # Measure sort operation
        start_time = time.time()
        sorted_tasks = sort_service.sort_tasks(all_tasks, sort_by="due_date")
        elapsed = time.time() - start_time

        assert elapsed < 1.0, f"Sorting 1000 tasks took {elapsed:.2f}s (expected < 1s)"
        assert len(sorted_tasks) == 1000

    def test_update_task_in_1000_tasks_performance(self):
        """Test updating a task among 1000 tasks completes in under 1 second."""
        # Add 1000 tasks
        task_ids = []
        for i in range(1000):
            task = self.service.add_task(
                title=f"Task {i}",
                description=f"Description {i}",
                priority=Priority.MEDIUM,
                categories=["test"]
            )
            task_ids.append(task.id)

        # Measure update operation (update task in the middle)
        target_id = task_ids[500]
        start_time = time.time()
        self.service.update_task(
            target_id,
            title="Updated Task",
            description="Updated description",
            priority=Priority.HIGH,
            categories=["updated"]
        )
        elapsed = time.time() - start_time

        assert elapsed < 1.0, f"Updating task took {elapsed:.2f}s (expected < 1s)"

        # Verify update
        updated = self.service.get_by_id(target_id)
        assert updated.title == "Updated Task"

    def test_complete_task_in_1000_tasks_performance(self):
        """Test completing a task among 1000 tasks completes in under 1 second."""
        # Add 1000 tasks
        task_ids = []
        for i in range(1000):
            task = self.service.add_task(
                title=f"Task {i}",
                description=f"Description {i}",
                priority=Priority.MEDIUM,
                categories=["test"]
            )
            task_ids.append(task.id)

        # Measure complete operation
        target_id = task_ids[500]
        start_time = time.time()
        self.service.complete_task(target_id)
        elapsed = time.time() - start_time

        assert elapsed < 1.0, f"Completing task took {elapsed:.2f}s (expected < 1s)"

        # Verify completion
        completed = self.service.get_by_id(target_id)
        assert completed.completed is True

    def test_delete_task_in_1000_tasks_performance(self):
        """Test deleting a task among 1000 tasks completes in under 1 second."""
        # Add 1000 tasks
        task_ids = []
        for i in range(1000):
            task = self.service.add_task(
                title=f"Task {i}",
                description=f"Description {i}",
                priority=Priority.MEDIUM,
                categories=["test"]
            )
            task_ids.append(task.id)

        # Measure delete operation
        target_id = task_ids[500]
        start_time = time.time()
        self.service.delete_task(target_id)
        elapsed = time.time() - start_time

        assert elapsed < 1.0, f"Deleting task took {elapsed:.2f}s (expected < 1s)"

        # Verify deletion
        all_tasks = self.service.get_all()
        assert len(all_tasks) == 999
        assert target_id not in [t.id for t in all_tasks]

    def test_get_pending_tasks_1000_tasks_performance(self):
        """Test getting pending tasks from 1000 tasks completes in under 1 second."""
        # Add 1000 tasks, complete half of them
        for i in range(1000):
            task = self.service.add_task(
                title=f"Task {i}",
                description=f"Description {i}",
                priority=Priority.MEDIUM,
                categories=["test"]
            )
            if i % 2 == 0:
                self.service.complete_task(task.id)

        # Measure get pending operation
        start_time = time.time()
        all_tasks = self.service.get_all()
        pending = [t for t in all_tasks if not t.completed]
        elapsed = time.time() - start_time

        assert elapsed < 1.0, f"Getting pending tasks took {elapsed:.2f}s (expected < 1s)"
        assert len(pending) == 500

    def test_get_completed_tasks_1000_tasks_performance(self):
        """Test getting completed tasks from 1000 tasks completes in under 1 second."""
        # Add 1000 tasks, complete half of them
        for i in range(1000):
            task = self.service.add_task(
                title=f"Task {i}",
                description=f"Description {i}",
                priority=Priority.MEDIUM,
                categories=["test"]
            )
            if i % 2 == 0:
                self.service.complete_task(task.id)

        # Measure get completed operation
        start_time = time.time()
        all_tasks = self.service.get_all()
        completed = [t for t in all_tasks if t.completed]
        elapsed = time.time() - start_time

        assert elapsed < 1.0, f"Getting completed tasks took {elapsed:.2f}s (expected < 1s)"
        assert len(completed) == 500
