"""Storage service for JSON file persistence with atomic write operations."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class StorageService:
    """
    Service for persisting tasks to JSON file with atomic write operations.

    Provides safe JSON file I/O with:
    - Atomic writes (temp file + rename)
    - Error handling for corrupted files
    - Data structure validation
    """

    def load_from_json(self, file_path: str = "ticklisto_data.json") -> dict:
        """
        Load tasks and metadata from JSON file.

        Args:
            file_path: Path to JSON file (default: ticklisto_data.json)

        Returns:
            Dictionary containing:
            - tasks: List of task dictionaries
            - next_id: Next available task ID (integer)

        Raises:
            ValueError: If JSON is corrupted or invalid format
        """
        # If file doesn't exist, return empty structure
        if not os.path.exists(file_path):
            return {"tasks": [], "next_id": 1}

        # If file is empty, return empty structure
        if os.path.getsize(file_path) == 0:
            return {"tasks": [], "next_id": 1}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate structure
            if not isinstance(data, dict):
                raise ValueError("JSON file must contain a dictionary")

            if "tasks" not in data:
                raise ValueError("JSON file must contain 'tasks' key")

            if "next_id" not in data:
                raise ValueError("JSON file must contain 'next_id' key")

            if not isinstance(data["tasks"], list):
                raise ValueError("'tasks' must be a list")

            if not isinstance(data["next_id"], int) or data["next_id"] < 1:
                raise ValueError("'next_id' must be a positive integer")

            # Return deep copy to prevent external modification
            return {
                "tasks": [task.copy() for task in data["tasks"]],
                "next_id": data["next_id"],
            }

        except json.JSONDecodeError as e:
            raise ValueError(f"JSON file is corrupted: {str(e)}")
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Error loading JSON file: {str(e)}")

    def save_to_json(self, data: dict, file_path: str = "ticklisto_data.json") -> None:
        """
        Save tasks and metadata to JSON file atomically.

        Uses atomic write operation (temp file + rename) to ensure data integrity.

        Args:
            data: Dictionary containing tasks and next_id
            file_path: Path to JSON file (default: ticklisto_data.json)

        Raises:
            ValueError: If data structure is invalid
            IOError: If write operation fails
        """
        # Validate data structure
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        if "tasks" not in data:
            raise ValueError("Data must contain 'tasks' key")

        if "next_id" not in data:
            raise ValueError("Data must contain 'next_id' key")

        if not isinstance(data["tasks"], list):
            raise ValueError("'tasks' must be a list")

        if not isinstance(data["next_id"], int) or data["next_id"] < 1:
            raise ValueError("'next_id' must be a positive integer")

        try:
            # Create parent directories if they don't exist
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            # Write to temporary file first (atomic write)
            temp_file_path = file_path + ".tmp"

            with open(temp_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())  # Ensure data is written to disk

            # Atomic rename (replaces original file)
            # On Windows, need to remove target file first if it exists
            if os.name == "nt" and os.path.exists(file_path):
                os.remove(file_path)

            os.rename(temp_file_path, file_path)

        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass

            raise IOError(f"Error saving to JSON file: {str(e)}")
