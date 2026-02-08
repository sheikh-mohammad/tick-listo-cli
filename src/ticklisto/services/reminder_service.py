"""Reminder service for managing email reminders (T062-T074 - User Story 4)."""

import threading
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json
import os

from ticklisto.models.task import Task
from ticklisto.models.reminder import EmailReminder, ReminderStatus, ReminderSetting
from ticklisto.services.gmail_service import GmailService
from ticklisto.services.storage_service import StorageService
from ticklisto.services.time_zone_service import TimeZoneService

# Configure logging for reminder operations (T107 - Phase 10)
logger = logging.getLogger(__name__)


class ReminderService:
    """
    Service for managing email reminders with background checking.

    Responsibilities:
    - Schedule reminders for tasks with due times
    - Cancel reminders when tasks are completed/deleted
    - Run background thread to check for due reminders every minute
    - Send reminders via Gmail API with retry logic
    - Send daily digest at 8 AM for failed reminders
    - Persist reminder state to storage
    """

    # Check interval in seconds (60 seconds = 1 minute)
    CHECK_INTERVAL = 60

    # Daily digest time (8:00 AM)
    DIGEST_HOUR = 8
    DIGEST_MINUTE = 0

    def __init__(
        self,
        gmail_service: GmailService,
        storage_service: StorageService,
        time_zone_service: TimeZoneService,
        reminders_file: str = "reminders.json"
    ):
        """
        Initialize ReminderService.

        Args:
            gmail_service: Service for sending emails
            storage_service: Service for task storage
            time_zone_service: Service for timezone conversions
            reminders_file: Path to reminders storage file
        """
        self.gmail_service = gmail_service
        self.storage_service = storage_service
        self.time_zone_service = time_zone_service
        self.reminders_file = reminders_file

        # Reminder queue (in-memory)
        self._reminder_queue: List[EmailReminder] = []

        # Background thread
        self._check_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()

        # Last digest send time
        self._last_digest_time: Optional[datetime] = None

        # Load existing reminders from storage
        self._load_reminders()

    def schedule_reminders(self, task: Task) -> List[EmailReminder]:
        """
        Schedule reminders for a task.

        Args:
            task: Task to schedule reminders for

        Returns:
            List of created EmailReminder objects
        """
        # Reminders require due_time
        if not task.due_time or not task.reminder_settings:
            return []

        reminders = []

        # Combine due_date and due_time
        due_datetime = datetime.combine(task.due_date.date(), task.due_time)

        # Convert to UTC
        due_datetime_utc = self.time_zone_service.to_utc(due_datetime)

        for setting in task.reminder_settings:
            # Calculate scheduled time (due time - offset)
            scheduled_time = due_datetime_utc - timedelta(minutes=setting.offset_minutes)

            # Skip if scheduled time is in the past (use timezone-aware comparison)
            if scheduled_time < self.time_zone_service.now_utc():
                continue

            # Create reminder
            reminder = EmailReminder(
                id=str(uuid.uuid4()),
                task_id=task.id,
                scheduled_time=scheduled_time,
                offset_minutes=setting.offset_minutes,
                status=ReminderStatus.PENDING
            )

            reminders.append(reminder)

        # Add to queue
        with self._lock:
            self._reminder_queue.extend(reminders)
            self._save_reminders()

        # Log reminder scheduling (T107 - Phase 10)
        logger.info(f"Scheduled {len(reminders)} reminder(s) for task {task.id}: {task.title}")
        for reminder in reminders:
            logger.debug(f"  - Reminder {reminder.id}: {reminder.offset_minutes} min before, scheduled for {reminder.scheduled_time}")

        return reminders

    def cancel_reminders(self, task_id: int):
        """
        Cancel all reminders for a task.

        Args:
            task_id: ID of task to cancel reminders for
        """
        cancelled_count = 0
        with self._lock:
            for reminder in self._reminder_queue:
                if reminder.task_id == task_id and reminder.status == ReminderStatus.PENDING:
                    reminder.status = ReminderStatus.CANCELLED
                    cancelled_count += 1

            self._save_reminders()

        # Log reminder cancellation (T107 - Phase 10)
        if cancelled_count > 0:
            logger.info(f"Cancelled {cancelled_count} reminder(s) for task {task_id}")

    def get_pending_reminders(self) -> List[EmailReminder]:
        """Get all pending reminders."""
        with self._lock:
            return [r for r in self._reminder_queue if r.status == ReminderStatus.PENDING]

    def get_failed_reminders(self) -> List[EmailReminder]:
        """Get all failed reminders."""
        with self._lock:
            return [r for r in self._reminder_queue if r.status == ReminderStatus.FAILED]

    def get_status(self) -> Dict:
        """
        Get reminder service status.

        Returns:
            Dictionary with pending_count, failed_count, total_count
        """
        with self._lock:
            pending = sum(1 for r in self._reminder_queue if r.status == ReminderStatus.PENDING)
            failed = sum(1 for r in self._reminder_queue if r.status == ReminderStatus.FAILED)
            total = len(self._reminder_queue)

            return {
                'pending_count': pending,
                'failed_count': failed,
                'total_count': total,
                'running': self._running
            }

    def start(self):
        """Start the background reminder check thread."""
        if self._running:
            return

        self._running = True
        self._check_thread = threading.Thread(target=self._check_loop, daemon=True)
        self._check_thread.start()

    def stop(self):
        """Stop the background reminder check thread."""
        self._running = False
        if self._check_thread:
            self._check_thread.join(timeout=5)

    def _check_loop(self):
        """Background thread loop that checks for due reminders."""
        while self._running:
            try:
                # Check for due reminders
                self._check_pending_reminders()

                # Check if daily digest should be sent
                self._check_daily_digest()

            except Exception as e:
                print(f"Error in reminder check loop: {e}")

            # Sleep for check interval
            time.sleep(self.CHECK_INTERVAL)

    def _check_pending_reminders(self):
        """Check for pending reminders that are due and send them."""
        now = datetime.utcnow()

        with self._lock:
            due_reminders = [
                r for r in self._reminder_queue
                if r.status == ReminderStatus.PENDING and r.scheduled_time <= now
            ]

        # Send due reminders (outside lock to avoid blocking)
        for reminder in due_reminders:
            self._send_reminder(reminder)

    def _send_reminder(self, reminder: EmailReminder):
        """
        Send a reminder email with retry logic.

        Args:
            reminder: EmailReminder to send
        """
        # Get task from storage
        task = self.storage_service.get_task(reminder.task_id)
        if not task:
            # Task no longer exists, cancel reminder
            with self._lock:
                reminder.status = ReminderStatus.CANCELLED
                self._save_reminders()
            return

        # Get recipient from config
        from ticklisto.utils.config_manager import ConfigManager
        config = ConfigManager()
        recipient = config.get_email_recipient()

        # Generate offset label
        offset_minutes = reminder.offset_minutes
        if offset_minutes < 60:
            label = f"{offset_minutes} minutes before"
        elif offset_minutes < 1440:
            hours = offset_minutes // 60
            label = f"{hours} hour{'s' if hours > 1 else ''} before"
        else:
            days = offset_minutes // 1440
            label = f"{days} day{'s' if days > 1 else ''} before"

        # Update status to sending
        with self._lock:
            reminder.status = ReminderStatus.SENDING
            reminder.last_attempt_time = datetime.utcnow()

        # Log reminder send attempt (T107 - Phase 10)
        logger.info(f"Sending reminder {reminder.id} for task {task.id}: {task.title} ({label})")

        # Attempt to send with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                success = self.gmail_service.send_reminder_email(
                    task=task,
                    recipient=recipient,
                    offset_label=label
                )

                if success:
                    # Mark as sent
                    with self._lock:
                        reminder.status = ReminderStatus.SENT
                        reminder.sent_time = datetime.utcnow()
                        self._save_reminders()

                    # Log successful send (T107 - Phase 10)
                    logger.info(f"✓ Reminder {reminder.id} sent successfully for task {task.id}")
                    return

            except Exception as e:
                reminder.error_message = str(e)
                # Log retry attempt (T107 - Phase 10)
                logger.warning(f"Reminder {reminder.id} send attempt {attempt + 1} failed: {e}")

            # Increment retry count
            reminder.retry_count = attempt + 1

            # If not last attempt, wait with exponential backoff
            if attempt < max_retries - 1:
                delay = 2 ** attempt  # 1s, 2s, 4s
                time.sleep(delay)

        # All retries failed
        with self._lock:
            reminder.status = ReminderStatus.FAILED
            self._save_reminders()

        # Log failure after all retries (T107 - Phase 10)
        logger.error(f"✗ Reminder {reminder.id} failed after {max_retries} attempts for task {task.id}: {reminder.error_message}")

    def _check_daily_digest(self):
        """Check if daily digest should be sent (at 8 AM user time)."""
        # Get current time in user timezone
        user_tz = self.time_zone_service.get_user_timezone()
        now_local = self.time_zone_service.to_local(datetime.utcnow(), user_tz)

        # Check if it's digest time (8:00 AM)
        if now_local.hour != self.DIGEST_HOUR or now_local.minute != self.DIGEST_MINUTE:
            return

        # Check if we already sent digest today
        if self._last_digest_time:
            last_digest_local = self.time_zone_service.to_local(self._last_digest_time, user_tz)
            if last_digest_local.date() == now_local.date():
                return  # Already sent today

        # Get failed reminders
        failed_reminders = self.get_failed_reminders()
        if not failed_reminders:
            return

        # Get tasks for failed reminders
        tasks = []
        for reminder in failed_reminders:
            task = self.storage_service.get_task(reminder.task_id)
            if task:
                tasks.append(task)

        if not tasks:
            return

        # Send daily digest
        from ticklisto.utils.config_manager import ConfigManager
        config = ConfigManager()
        recipient = config.get_email_recipient()

        try:
            success = self.gmail_service.send_daily_digest(
                tasks=tasks,
                recipient=recipient
            )

            if success:
                self._last_digest_time = datetime.utcnow()

        except Exception as e:
            print(f"Error sending daily digest: {e}")

    def _save_reminders(self):
        """Save reminders to storage."""
        try:
            data = [r.to_dict() for r in self._reminder_queue]
            with open(self.reminders_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving reminders: {e}")

    def _load_reminders(self):
        """Load reminders from storage."""
        if not os.path.exists(self.reminders_file):
            return

        try:
            with open(self.reminders_file, 'r') as f:
                data = json.load(f)

            self._reminder_queue = [EmailReminder.from_dict(r) for r in data]

        except Exception as e:
            print(f"Error loading reminders: {e}")
