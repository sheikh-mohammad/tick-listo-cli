"""Integration tests for task persistence across application restarts."""

import json
import os
import tempfile
from datetime import datetime

import pytest

from tick_listo_cli.models.task import Priority, Task
from tick_listo_cli.services.id_manager import IDManager
from tick_listo_cli.services.storage_service import StorageService
from tick_listo_cli.services.task_service import TaskService


class TestTaskPersistenceAcrossRestarts:
    """Test that tasks persist across application restarts."""

    def test_tasks_persist_after_save_and_reload(self):
        """Test that tasks are saved and can be loaded after restart."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create and save tasks
            task_manager = TaskService(data_file=file_path)

            # Create tasks using add_task method
            task1 = task_manager.add_task(
                title="Task 1",
                description="Description 1",
                priority=Priority.HIGH,
                categories=["work"],
            )

            task2 = task_manager.add_task(
                title="Task 2",
                description="Description 2",
                priority=Priority.MEDIUM,
                categories=["home", "personal"],
            )

            # Save to storage
            task_manager.save_to_file()

            # Session 2: Load tasks (simulating app restart)
            task_manager2 = TaskService(data_file=file_path)

            # Verify tasks were loaded
            loaded_tasks = task_manager2.get_all()
            assert len(loaded_tasks) == 2

            # Verify task 1
            loaded_task1 = next(t for t in loaded_tasks if t.id == task1.id)
            assert loaded_task1.title == "Task 1"
            assert loaded_task1.description == "Description 1"
            assert loaded_task1.priority == Priority.HIGH
            assert loaded_task1.categories == ["work"]

            # Verify task 2
            loaded_task2 = next(t for t in loaded_tasks if t.id == task2.id)
            assert loaded_task2.title == "Task 2"
            assert loaded_task2.description == "Description 2"
            assert loaded_task2.priority == Priority.MEDIUM
            assert set(loaded_task2.categories) == {"home", "personal"}

    def test_task_modifications_persist(self):
        """Test that task modifications are persisted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create task
            task_manager = TaskService(data_file=file_path)

            task = task_manager.add_task(
                title="Original Title",
                description="Original Description",
                priority=Priority.LOW,
                categories=["work"],
            )
            task_id = task.id

            task_manager.save_to_file()

            # Session 2: Modify task
            task_manager2 = TaskService(data_file=file_path)

            # Modify the task
            task_manager2.update_task(
                task_id,
                title="Updated Title",
                description="Updated Description",
                priority=Priority.HIGH,
                categories=["home", "urgent"],
            )

            task_manager2.save_to_file()

            # Session 3: Verify modifications persisted
            task_manager3 = TaskService(data_file=file_path)

            loaded_task = task_manager3.get_by_id(task_id)
            assert loaded_task.title == "Updated Title"
            assert loaded_task.description == "Updated Description"
            assert loaded_task.priority == Priority.HIGH
            assert set(loaded_task.categories) == {"home", "urgent"}

    def test_task_deletion_persists(self):
        """Test that task deletions are persisted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create tasks
            task_manager = TaskService(data_file=file_path)

            task1 = task_manager.add_task(title="Task 1", priority=Priority.HIGH, categories=["work"])
            task2 = task_manager.add_task(title="Task 2", priority=Priority.MEDIUM, categories=["home"])
            task3 = task_manager.add_task(title="Task 3", priority=Priority.LOW, categories=["personal"])

            task_manager.save_to_file()

            # Session 2: Delete task 2
            task_manager2 = TaskService(data_file=file_path)

            task_manager2.delete_task(task2.id)
            task_manager2.save_to_file()

            # Session 3: Verify deletion persisted
            task_manager3 = TaskService(data_file=file_path)

            loaded_tasks = task_manager3.get_all()
            assert len(loaded_tasks) == 2

            task_ids = [t.id for t in loaded_tasks]
            assert task1.id in task_ids
            assert task2.id not in task_ids
            assert task3.id in task_ids

    def test_empty_task_list_persists(self):
        """Test that empty task list is persisted correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Save empty task list
            task_manager = TaskService(data_file=file_path)

            task_manager.save_to_file()

            # Session 2: Load and verify
            task_manager2 = TaskService(data_file=file_path)

            loaded_tasks = task_manager2.get_all()
            assert len(loaded_tasks) == 0

    def test_large_number_of_tasks_persist(self):
        """Test that large number of tasks (1000) persist correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create 1000 tasks
            task_manager = TaskService(data_file=file_path)

            for i in range(1, 1001):
                task_manager.add_task(
                    title=f"Task {i}",
                    description=f"Description {i}",
                    priority=[Priority.HIGH, Priority.MEDIUM, Priority.LOW][i % 3],
                    categories=[["work"], ["home"], ["personal"]][i % 3],
                )

            task_manager.save_to_file()

            # Session 2: Load and verify
            task_manager2 = TaskService(data_file=file_path)

            loaded_tasks = task_manager2.get_all()
            assert len(loaded_tasks) == 1000

            # Verify some random tasks
            all_tasks_by_title = {t.title: t for t in loaded_tasks}
            assert "Task 100" in all_tasks_by_title
            assert "Task 500" in all_tasks_by_title
            assert "Task 1000" in all_tasks_by_title


class TestIDUniqueness:
    """Test that IDs remain unique across application restarts."""

    def test_id_counter_persists_across_restarts(self):
        """Test that ID counter persists and continues from correct value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create tasks with IDs 1, 2, 3
            task_manager = TaskService(data_file=file_path)

            for i in range(3):
                task_manager.add_task(
                    title=f"Task {i+1}",
                    priority=Priority.MEDIUM,
                    categories=["work"],
                )

            task_manager.save_to_file()

            # Session 2: Load and create new task (should get ID 4)
            task_manager2 = TaskService(data_file=file_path)

            # Create new task
            new_task = task_manager2.add_task(
                title="New Task",
                priority=Priority.HIGH,
                categories=["home"],
            )

            # Verify new task has ID 4
            assert new_task.id == 4

            # Verify all task IDs are unique
            all_tasks = task_manager2.get_all()
            task_ids = [t.id for t in all_tasks]
            assert len(task_ids) == len(set(task_ids))  # All unique
            assert task_ids == [1, 2, 3, 4]

    def test_ids_never_reused_after_deletion(self):
        """Test that deleted task IDs are never reused."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create tasks 1, 2, 3
            task_manager = TaskService(data_file=file_path)

            task1 = task_manager.add_task(title="Task 1", priority=Priority.HIGH, categories=["work"])
            task2 = task_manager.add_task(title="Task 2", priority=Priority.MEDIUM, categories=["home"])
            task3 = task_manager.add_task(title="Task 3", priority=Priority.LOW, categories=["personal"])

            # Delete task 2
            task_manager.delete_task(task2.id)

            task_manager.save_to_file()

            # Session 2: Load and create new task
            task_manager2 = TaskService(data_file=file_path)

            # Create new task (should get ID 4, NOT 2)
            new_task = task_manager2.add_task(
                title="New Task",
                priority=Priority.HIGH,
                categories=["work"],
            )
            assert new_task.id == 4  # Not 2!

            # Verify task IDs
            all_tasks = task_manager2.get_all()
            task_ids = [t.id for t in all_tasks]
            assert set(task_ids) == {1, 3, 4}  # 2 is not reused

    def test_id_counter_resets_after_delete_all(self):
        """Test that ID counter resets to 1 after delete all."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create tasks
            task_manager = TaskService(data_file=file_path)

            for i in range(5):
                task_manager.add_task(
                    title=f"Task {i+1}",
                    priority=Priority.MEDIUM,
                    categories=["work"],
                )

            # Delete all tasks
            task_manager.delete_all()
            task_manager.id_manager.reset_counter()

            task_manager.save_to_file()

            # Session 2: Load and create new task (should get ID 1)
            task_manager2 = TaskService(data_file=file_path)

            # Create new task
            new_task = task_manager2.add_task(
                title="New Task",
                priority=Priority.HIGH,
                categories=["work"],
            )
            assert new_task.id == 1  # Fresh start!

            # Verify only one task with ID 1
            all_tasks = task_manager2.get_all()
            assert len(all_tasks) == 1
            assert all_tasks[0].id == 1

    def test_concurrent_sessions_maintain_id_uniqueness(self):
        """Test that ID uniqueness is maintained even with multiple sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create initial tasks
            task_manager1 = TaskService(data_file=file_path)

            for i in range(3):
                task_manager1.add_task(
                    title=f"Task {i+1}",
                    priority=Priority.MEDIUM,
                    categories=["work"]
                )

            task_manager1.save_to_file()

            # Session 2: Load and add more tasks
            task_manager2 = TaskService(data_file=file_path)

            for i in range(2):
                task_manager2.add_task(
                    title=f"Task {i+4}",
                    priority=Priority.HIGH,
                    categories=["home"]
                )

            task_manager2.save_to_file()

            # Session 3: Load and verify all IDs are unique
            task_manager3 = TaskService(data_file=file_path)

            all_tasks = task_manager3.get_all()
            task_ids = [t.id for t in all_tasks]

            # Verify all IDs are unique
            assert len(task_ids) == len(set(task_ids))
            assert task_ids == [1, 2, 3, 4, 5]
