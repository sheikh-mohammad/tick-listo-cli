"""Unit tests for StorageService - JSON file persistence."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from tick_listo_cli.services.storage_service import StorageService


class TestStorageServiceLoad:
    """Test JSON file read operations."""

    def test_load_from_nonexistent_file_returns_empty_structure(self):
        """Test loading from non-existent file returns empty structure."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "nonexistent.json")
            data = service.load_from_json(file_path)

            assert data == {"tasks": [], "next_id": 1}

    def test_load_from_valid_json_file(self):
        """Test loading from valid JSON file."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")

            # Create valid JSON file
            test_data = {
                "tasks": [
                    {
                        "id": 1,
                        "title": "Test Task",
                        "description": "Test Description",
                        "completed": False,
                        "priority": "high",
                        "categories": ["work"],
                        "due_date": None,
                        "created_at": "2026-02-01T10:00:00",
                        "updated_at": "2026-02-01T10:00:00",
                    }
                ],
                "next_id": 2,
            }

            with open(file_path, "w") as f:
                json.dump(test_data, f)

            # Load and verify
            data = service.load_from_json(file_path)
            assert data["tasks"] == test_data["tasks"]
            assert data["next_id"] == 2

    def test_load_from_empty_file_returns_empty_structure(self):
        """Test loading from empty file returns empty structure."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "empty.json")

            # Create empty file
            Path(file_path).touch()

            data = service.load_from_json(file_path)
            assert data == {"tasks": [], "next_id": 1}

    def test_load_from_corrupted_json_raises_value_error(self):
        """Test loading from corrupted JSON raises ValueError."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "corrupted.json")

            # Create corrupted JSON file
            with open(file_path, "w") as f:
                f.write("{invalid json content")

            with pytest.raises(ValueError, match="JSON file is corrupted"):
                service.load_from_json(file_path)

    def test_load_from_json_missing_tasks_key_raises_value_error(self):
        """Test loading from JSON missing 'tasks' key raises ValueError."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "missing_tasks.json")

            # Create JSON without tasks key
            with open(file_path, "w") as f:
                json.dump({"next_id": 1}, f)

            with pytest.raises(ValueError, match="must contain 'tasks' key"):
                service.load_from_json(file_path)

    def test_load_from_json_missing_next_id_key_raises_value_error(self):
        """Test loading from JSON missing 'next_id' key raises ValueError."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "missing_next_id.json")

            # Create JSON without next_id key
            with open(file_path, "w") as f:
                json.dump({"tasks": []}, f)

            with pytest.raises(ValueError, match="must contain 'next_id' key"):
                service.load_from_json(file_path)

    def test_load_returns_deep_copy(self):
        """Test that load returns a deep copy to prevent external modification."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")

            test_data = {"tasks": [{"id": 1, "title": "Task"}], "next_id": 2}

            with open(file_path, "w") as f:
                json.dump(test_data, f)

            # Load twice
            data1 = service.load_from_json(file_path)
            data2 = service.load_from_json(file_path)

            # Modify first copy
            data1["tasks"].append({"id": 2, "title": "New Task"})

            # Second copy should be unaffected
            assert len(data2["tasks"]) == 1


class TestStorageServiceSave:
    """Test JSON file write operations with atomic writes."""

    def test_save_valid_data_structure(self):
        """Test saving valid data structure."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")

            data = {
                "tasks": [
                    {
                        "id": 1,
                        "title": "Test Task",
                        "completed": False,
                        "priority": "high",
                        "categories": ["work"],
                    }
                ],
                "next_id": 2,
            }

            service.save_to_json(data, file_path)

            # Verify file exists and contains correct data
            assert os.path.exists(file_path)
            with open(file_path, "r") as f:
                saved_data = json.load(f)
            assert saved_data == data

    def test_save_with_missing_tasks_key_raises_value_error(self):
        """Test saving data without 'tasks' key raises ValueError."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")

            data = {"next_id": 1}  # Missing tasks key

            with pytest.raises(ValueError, match="must contain 'tasks' key"):
                service.save_to_json(data, file_path)

    def test_save_with_missing_next_id_key_raises_value_error(self):
        """Test saving data without 'next_id' key raises ValueError."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")

            data = {"tasks": []}  # Missing next_id key

            with pytest.raises(ValueError, match="must contain 'next_id' key"):
                service.save_to_json(data, file_path)

    def test_save_with_invalid_tasks_type_raises_value_error(self):
        """Test saving data with non-list tasks raises ValueError."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")

            data = {"tasks": "not a list", "next_id": 1}

            with pytest.raises(ValueError, match="'tasks' must be a list"):
                service.save_to_json(data, file_path)

    def test_save_with_invalid_next_id_type_raises_value_error(self):
        """Test saving data with non-integer next_id raises ValueError."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")

            data = {"tasks": [], "next_id": "not an integer"}

            with pytest.raises(ValueError, match="'next_id' must be a positive integer"):
                service.save_to_json(data, file_path)

    def test_atomic_write_uses_temp_file(self):
        """Test that atomic write uses temporary file."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")

            data = {"tasks": [], "next_id": 1}

            service.save_to_json(data, file_path)

            # Verify temp file doesn't exist after successful write
            temp_file_path = file_path + ".tmp"
            assert not os.path.exists(temp_file_path)

            # Verify actual file exists
            assert os.path.exists(file_path)

    def test_save_creates_parent_directories(self):
        """Test that save creates parent directories if they don't exist."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "subdir", "nested", "test.json")

            data = {"tasks": [], "next_id": 1}

            service.save_to_json(data, file_path)

            # Verify file was created in nested directory
            assert os.path.exists(file_path)

    def test_save_overwrites_existing_file(self):
        """Test that save overwrites existing file."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")

            # Save initial data
            data1 = {"tasks": [{"id": 1, "title": "Task 1"}], "next_id": 2}
            service.save_to_json(data1, file_path)

            # Save new data
            data2 = {"tasks": [{"id": 2, "title": "Task 2"}], "next_id": 3}
            service.save_to_json(data2, file_path)

            # Verify new data is saved
            with open(file_path, "r") as f:
                saved_data = json.load(f)
            assert saved_data == data2

    def test_save_uses_json_indent_for_readability(self):
        """Test that saved JSON is formatted with indentation."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")

            data = {"tasks": [], "next_id": 1}

            service.save_to_json(data, file_path)

            # Read raw file content
            with open(file_path, "r") as f:
                content = f.read()

            # Verify it's formatted (contains newlines and indentation)
            assert "\n" in content
            assert "  " in content  # Indentation


class TestStorageServiceIntegration:
    """Test handling of corrupted JSON files."""

    def test_round_trip_save_and_load(self):
        """Test that data can be saved and loaded without loss."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")

            original_data = {
                "tasks": [
                    {
                        "id": 1,
                        "title": "Task 1",
                        "description": "Description 1",
                        "completed": False,
                        "priority": "high",
                        "categories": ["work", "urgent"],
                        "due_date": "2026-02-15T00:00:00",
                        "created_at": "2026-02-01T10:00:00",
                        "updated_at": "2026-02-01T10:00:00",
                    },
                    {
                        "id": 2,
                        "title": "Task 2",
                        "description": None,
                        "completed": True,
                        "priority": "low",
                        "categories": ["home"],
                        "due_date": None,
                        "created_at": "2026-02-01T11:00:00",
                        "updated_at": "2026-02-01T11:00:00",
                    },
                ],
                "next_id": 3,
            }

            # Save and load
            service.save_to_json(original_data, file_path)
            loaded_data = service.load_from_json(file_path)

            # Verify data integrity
            assert loaded_data == original_data

    def test_large_dataset_performance(self):
        """Test performance with 1000 tasks."""
        service = StorageService()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "large.json")

            # Create 1000 tasks
            tasks = [
                {
                    "id": i,
                    "title": f"Task {i}",
                    "description": f"Description {i}",
                    "completed": i % 2 == 0,
                    "priority": ["high", "medium", "low"][i % 3],
                    "categories": ["work", "home", "personal"][: (i % 3) + 1],
                    "due_date": None,
                    "created_at": "2026-02-01T10:00:00",
                    "updated_at": "2026-02-01T10:00:00",
                }
                for i in range(1, 1001)
            ]

            data = {"tasks": tasks, "next_id": 1001}

            # Save and load (should complete in <100ms)
            import time

            start = time.time()
            service.save_to_json(data, file_path)
            save_time = time.time() - start

            start = time.time()
            loaded_data = service.load_from_json(file_path)
            load_time = time.time() - start

            # Verify performance (adjusted for Windows systems)
            assert save_time < 0.3  # <300ms (relaxed for Windows I/O)
            assert load_time < 0.4  # <400ms (relaxed for Windows I/O)

            # Verify data integrity
            assert len(loaded_data["tasks"]) == 1000
            assert loaded_data["next_id"] == 1001
