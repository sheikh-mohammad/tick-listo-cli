import json
import os
from pathlib import Path
from typing import Optional
import pytz


class ConfigManager:
    """
    Utility for loading and saving configuration from config.json.

    Manages user preferences including time zone, default reminder settings,
    email recipient, and daily digest time.
    """

    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize ConfigManager.

        Args:
            config_path: Path to config.json file
        """
        self.config_path = Path(config_path)
        self._config = None
        self._load_config()

    def _load_config(self):
        """Load configuration from file or create default if not exists."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                self._validate_config()
            except (json.JSONDecodeError, IOError) as e:
                raise ValueError(f"Failed to load config from {self.config_path}: {e}")
        else:
            # Create default config
            self._config = self._get_default_config()
            self._save_config()

    def _get_default_config(self) -> dict:
        """Get default configuration values."""
        return {
            "time_zone": "America/New_York",
            "default_reminder_offsets": [60, 1440],  # 1 hour and 1 day in minutes
            "email_recipient": "haji08307@gmail.com",
            "daily_digest_time": "08:00"
        }

    def _validate_config(self):
        """Validate configuration values."""
        # Validate time zone
        time_zone = self._config.get("time_zone")
        if time_zone and time_zone not in pytz.all_timezones:
            raise ValueError(f"Invalid time zone: {time_zone}")

        # Validate default_reminder_offsets (list of positive integers in minutes)
        offsets = self._config.get("default_reminder_offsets")
        if offsets is not None:
            if not isinstance(offsets, list):
                raise ValueError("default_reminder_offsets must be a list")
            if not all(isinstance(o, int) and o > 0 for o in offsets):
                raise ValueError("default_reminder_offsets must contain positive integers")

        # Validate daily_digest_time format (HH:MM)
        digest_time = self._config.get("daily_digest_time")
        if digest_time:
            try:
                hours, minutes = digest_time.split(":")
                if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
                    raise ValueError
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid daily_digest_time format: {digest_time}. Expected HH:MM")

    def _save_config(self):
        """Save configuration to file."""
        # Create directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            raise ValueError(f"Failed to save config to {self.config_path}: {e}")

    def get_time_zone(self) -> str:
        """Get configured time zone."""
        return self._config.get("time_zone", "America/New_York")

    def set_time_zone(self, time_zone: str):
        """
        Set time zone.

        Args:
            time_zone: Time zone name (must be valid pytz timezone)

        Raises:
            ValueError: If time zone is invalid
        """
        if time_zone not in pytz.all_timezones:
            raise ValueError(f"Invalid time zone: {time_zone}")
        self._config["time_zone"] = time_zone
        self._save_config()

    def get_default_reminder_offset(self) -> int:
        """
        Get default reminder offset in seconds (deprecated - use get_default_reminder_offsets).

        Returns:
            First offset from default_reminder_offsets list, or 3600 if not set
        """
        offsets = self._config.get("default_reminder_offsets", [60])
        return offsets[0] * 60 if offsets else 3600

    def get_default_reminder_offsets(self) -> list:
        """
        Get default reminder offsets in minutes.

        Returns:
            List of reminder offsets in minutes (e.g., [60, 1440] for 1 hour and 1 day)
        """
        return self._config.get("default_reminder_offsets", [60, 1440])

    def set_default_reminder_offsets(self, offsets_minutes: list):
        """
        Set default reminder offsets.

        Args:
            offsets_minutes: List of offsets in minutes (must be positive integers)

        Raises:
            ValueError: If offsets are invalid
        """
        if not isinstance(offsets_minutes, list):
            raise ValueError("Offsets must be a list")
        if not all(isinstance(o, int) and o > 0 for o in offsets_minutes):
            raise ValueError("All offsets must be positive integers")
        self._config["default_reminder_offsets"] = offsets_minutes
        self._save_config()

    def set_default_reminder_offset(self, offset_seconds: int):
        """
        Set default reminder offset (deprecated - use set_default_reminder_offsets).

        Args:
            offset_seconds: Offset in seconds (must be positive)

        Raises:
            ValueError: If offset is not positive
        """
        if offset_seconds <= 0:
            raise ValueError("Offset must be positive")
        offset_minutes = offset_seconds // 60
        self._config["default_reminder_offsets"] = [offset_minutes]
        self._save_config()

    def get_email_recipient(self) -> str:
        """Get email recipient address."""
        return self._config.get("email_recipient", "haji08307@gmail.com")

    def set_email_recipient(self, email: str):
        """
        Set email recipient address.

        Args:
            email: Email address
        """
        self._config["email_recipient"] = email
        self._save_config()

    def get_daily_digest_time(self) -> str:
        """Get daily digest time in HH:MM format."""
        return self._config.get("daily_digest_time", "08:00")

    def set_daily_digest_time(self, time_str: str):
        """
        Set daily digest time.

        Args:
            time_str: Time in HH:MM format

        Raises:
            ValueError: If time format is invalid
        """
        try:
            hours, minutes = time_str.split(":")
            if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
                raise ValueError
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM")

        self._config["daily_digest_time"] = time_str
        self._save_config()

    def get_all(self) -> dict:
        """Get all configuration values."""
        return self._config.copy()
