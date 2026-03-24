import json
import os
from typing import Any, Dict, Optional


class FileHandler:
    """
    Utility class for handling file operations for data persistence.
    Provides methods for saving and loading data in JSON format.
    """

    def __init__(self):
        """Initialize the FileHandler."""
        pass

    def save_data(self, file_path: str, data: Dict[str, Any]):
        """
        Save data to a JSON file.

        Args:
            file_path: Path to the file to save data to
            data: Dictionary containing data to save
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving data to {file_path}: {str(e)}")

    def load_data(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load data from a JSON file.

        Args:
            file_path: Path to the file to load data from

        Returns:
            Dictionary containing loaded data, or None if file doesn't exist or error occurs
        """
        try:
            if not os.path.exists(file_path):
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {str(e)}")
            return None
        except IOError as e:
            print(f"Error loading data from {file_path}: {str(e)}")
            return None