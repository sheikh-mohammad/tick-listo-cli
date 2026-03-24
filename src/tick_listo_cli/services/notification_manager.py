"""
Notification manager for handling styled messages per data-model.md.
"""

from datetime import datetime
from typing import List
from ..models.notification import Notification, NotificationType
from ..ui.components import display_notification


class NotificationManager:
    """
    Notification manager class for handling styled messages per data-model.md.
    """

    def __init__(self):
        """
        Initialize the notification manager.
        """
        self.notifications: List[Notification] = []
        self.next_id = 1

    def create_notification(self, notification_type: NotificationType, title: str, message: str, duration: int = 3000) -> Notification:
        """
        Create a new notification.

        Args:
            notification_type: Type of notification (info, success, warning, error)
            title: Notification title
            message: Notification message
            duration: Duration to display in milliseconds

        Returns:
            Created Notification object
        """
        notification = Notification(
            id=self.next_id,
            type=notification_type,
            title=title,
            message=message,
            duration=duration
        )

        self.notifications.append(notification)
        self.next_id += 1

        return notification

    def show_notification(self, notification: Notification):
        """
        Display a notification using Rich formatting per FR-015.

        Args:
            notification: Notification to display
        """
        display_notification(notification)

    def show_info(self, title: str, message: str):
        """
        Show an info notification per FR-015.

        Args:
            title: Notification title
            message: Notification message
        """
        notification = self.create_notification(NotificationType.INFO, title, message)
        self.show_notification(notification)

    def show_success(self, title: str, message: str):
        """
        Show a success notification per FR-015.

        Args:
            title: Notification title
            message: Notification message
        """
        notification = self.create_notification(NotificationType.SUCCESS, title, message)
        self.show_notification(notification)

    def show_warning(self, title: str, message: str):
        """
        Show a warning notification per FR-015.

        Args:
            title: Notification title
            message: Notification message
        """
        notification = self.create_notification(NotificationType.WARNING, title, message)
        self.show_notification(notification)

    def show_error(self, title: str, message: str):
        """
        Show an error notification per FR-015.

        Args:
            title: Notification title
            message: Notification message
        """
        notification = self.create_notification(NotificationType.ERROR, title, message)
        self.show_notification(notification)

    def get_recent_notifications(self, count: int = 5) -> List[Notification]:
        """
        Get the most recent notifications.

        Args:
            count: Number of recent notifications to return

        Returns:
            List of recent Notification objects
        """
        return self.notifications[-count:] if len(self.notifications) >= count else self.notifications[:]

    def clear_notifications(self):
        """
        Clear all notifications from the manager.
        """
        self.notifications.clear()

    def get_unread_notifications(self) -> List[Notification]:
        """
        Get all notifications (since we're not tracking read status).

        Returns:
            List of all Notification objects
        """
        return self.notifications.copy()

    def get_notification_by_id(self, notification_id: int) -> Notification:
        """
        Get a specific notification by ID.

        Args:
            notification_id: ID of the notification to retrieve

        Returns:
            Notification object if found, None otherwise
        """
        for notification in self.notifications:
            if notification.id == notification_id:
                return notification
        return None

    def remove_notification(self, notification_id: int) -> bool:
        """
        Remove a notification by ID.

        Args:
            notification_id: ID of the notification to remove

        Returns:
            True if notification was removed, False if not found
        """
        for i, notification in enumerate(self.notifications):
            if notification.id == notification_id:
                del self.notifications[i]
                return True
        return False