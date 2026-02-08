"""Gmail service for sending email reminders (T048-T053 - User Story 3)."""

import os
import base64
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ticklisto.models.task import Task


class GmailService:
    """
    Service for sending email reminders via Gmail API.

    Handles OAuth authentication, token refresh, email sending with retry logic,
    and daily digest emails for failed reminders.
    """

    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY_BASE = 1  # seconds

    def __init__(self, token_path: str = "credentials/token.json", credentials_path: str = "credentials/credentials.json"):
        """
        Initialize Gmail service with OAuth credentials.

        Args:
            token_path: Path to token.json file (stores user's access/refresh tokens)
            credentials_path: Path to credentials.json file (OAuth client credentials)

        Raises:
            FileNotFoundError: If credentials.json doesn't exist
        """
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.service = None

        # Check if credentials file exists
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"credentials.json not found at {credentials_path}. "
                "Please download OAuth credentials from Google Cloud Console."
            )

        self._initialize_service()

    def _initialize_service(self):
        """Initialize Gmail API service with OAuth authentication."""
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                creds.refresh(Request())
            else:
                # Run OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        # Build Gmail API service
        self.service = build('gmail', 'v1', credentials=creds)

    def send_reminder_email(
        self,
        task: Task,
        recipient: str,
        offset_label: str
    ) -> bool:
        """
        Send a reminder email for a task.

        Args:
            task: Task to send reminder for
            recipient: Email address to send to
            offset_label: Human-readable label (e.g., "1 hour before")

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create email message
            message = self._create_reminder_message(task, recipient, offset_label)

            # Send with retry logic
            return self._send_with_retry(message)

        except Exception as e:
            print(f"Error sending reminder email: {e}")
            return False

    def _create_reminder_message(self, task: Task, recipient: str, offset_label: str) -> dict:
        """
        Create email message for task reminder.

        Args:
            task: Task to create reminder for
            recipient: Email recipient
            offset_label: Reminder timing label

        Returns:
            Gmail API message dict with 'raw' field
        """
        # Create multipart message (text + HTML)
        message = MIMEMultipart('alternative')
        message['to'] = recipient
        message['from'] = 'me'  # 'me' is special value for authenticated user

        # Add priority indicator to subject for HIGH priority tasks (T098 - User Story 7)
        subject = f"Reminder: {task.title}"
        if task.priority == Priority.HIGH:
            subject = f"[HIGH PRIORITY] {subject}"
        message['subject'] = subject

        # Create text version
        text_body = self._format_text_body(task, offset_label)
        text_part = MIMEText(text_body, 'plain')
        message.attach(text_part)

        # Create HTML version
        html_body = self._format_html_body(task, offset_label)
        html_part = MIMEText(html_body, 'html')
        message.attach(html_part)

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        return {'raw': raw_message}

    def _format_text_body(self, task: Task, offset_label: str) -> str:
        """Format plain text email body."""
        lines = [
            f"Task Reminder ({offset_label})",
            "",
            f"Title: {task.title}",
        ]

        if task.description:
            lines.append(f"Description: {task.description}")

        if task.due_date:
            if task.due_time:
                due_str = task.due_date.strftime("%b %d, %Y") + f" at {task.due_time.strftime('%I:%M %p')}"
            else:
                due_str = task.due_date.strftime("%b %d, %Y")
            lines.append(f"Due: {due_str}")

        if task.priority:
            lines.append(f"Priority: {task.priority.value.upper()}")

        if task.categories:
            lines.append(f"Categories: {', '.join(task.categories)}")

        if task.recurrence_pattern:
            lines.append(f"Recurrence: {task.recurrence_pattern.value}")

        lines.extend([
            "",
            "Please complete this task on time.",
            "",
            "---",
            "Sent by Ticklisto Task Manager"
        ])

        return "\n".join(lines)

    def _format_html_body(self, task: Task, offset_label: str) -> str:
        """Format HTML email body."""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c3e50;">Task Reminder ({offset_label})</h2>

            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #2c3e50;">{task.title}</h3>
        """

        if task.description:
            html += f"<p><strong>Description:</strong> {task.description}</p>"

        if task.due_date:
            if task.due_time:
                due_str = task.due_date.strftime("%b %d, %Y") + f" at {task.due_time.strftime('%I:%M %p')}"
            else:
                due_str = task.due_date.strftime("%b %d, %Y")
            html += f"<p><strong>Due:</strong> {due_str}</p>"

        if task.priority:
            priority_color = {
                'high': '#e74c3c',
                'medium': '#f39c12',
                'low': '#3498db'
            }.get(task.priority.value, '#95a5a6')
            html += f'<p><strong>Priority:</strong> <span style="color: {priority_color}; font-weight: bold;">{task.priority.value.upper()}</span></p>'

        if task.categories:
            html += f"<p><strong>Categories:</strong> {', '.join(task.categories)}</p>"

        if task.recurrence_pattern:
            html += f"<p><strong>Recurrence:</strong> 🔁 {task.recurrence_pattern.value}</p>"

        html += """
            </div>

            <p style="color: #7f8c8d;">Please complete this task on time.</p>

            <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
            <p style="font-size: 12px; color: #95a5a6;">Sent by Ticklisto Task Manager</p>
        </body>
        </html>
        """

        return html

    def _send_with_retry(self, message: dict) -> bool:
        """
        Send email with exponential backoff retry logic.

        Args:
            message: Gmail API message dict

        Returns:
            True if sent successfully, False otherwise
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                # Send message
                self.service.users().messages().send(
                    userId='me',
                    body=message
                ).execute()

                return True

            except HttpError as e:
                # Check if error is retryable
                if e.resp.status == 429:  # Rate limit
                    if attempt < self.MAX_RETRIES - 1:
                        # Exponential backoff: 1s, 2s, 4s
                        delay = self.RETRY_DELAY_BASE * (2 ** attempt)
                        time.sleep(delay)
                        continue
                    else:
                        print(f"Rate limit exceeded after {self.MAX_RETRIES} attempts")
                        return False

                elif e.resp.status in [500, 502, 503, 504]:  # Server errors
                    if attempt < self.MAX_RETRIES - 1:
                        delay = self.RETRY_DELAY_BASE * (2 ** attempt)
                        time.sleep(delay)
                        continue
                    else:
                        print(f"Server error after {self.MAX_RETRIES} attempts")
                        return False

                else:
                    # Non-retryable error (401, 403, 404, etc.)
                    print(f"Non-retryable error: {e.resp.status}")
                    return False

            except Exception as e:
                # Network errors, connection errors, etc.
                print(f"Error sending email: {e}")
                return False

        return False

    def send_daily_digest(self, tasks: List[Task], recipient: str) -> bool:
        """
        Send daily digest email with multiple tasks.

        Args:
            tasks: List of tasks to include in digest
            recipient: Email address to send to

        Returns:
            True if email sent successfully, False otherwise
        """
        if not tasks:
            # No tasks to send
            return True

        try:
            # Create digest message
            message = self._create_digest_message(tasks, recipient)

            # Send with retry logic
            return self._send_with_retry(message)

        except Exception as e:
            print(f"Error sending daily digest: {e}")
            return False

    def _create_digest_message(self, tasks: List[Task], recipient: str) -> dict:
        """
        Create email message for daily digest.

        Args:
            tasks: List of tasks for digest
            recipient: Email recipient

        Returns:
            Gmail API message dict with 'raw' field
        """
        # Create multipart message
        message = MIMEMultipart('alternative')
        message['to'] = recipient
        message['from'] = 'me'
        message['subject'] = f"Daily Task Digest - {len(tasks)} pending reminders"

        # Create text version
        text_body = self._format_digest_text(tasks)
        text_part = MIMEText(text_body, 'plain')
        message.attach(text_part)

        # Create HTML version
        html_body = self._format_digest_html(tasks)
        html_part = MIMEText(html_body, 'html')
        message.attach(html_part)

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        return {'raw': raw_message}

    def _format_digest_text(self, tasks: List[Task]) -> str:
        """Format plain text digest body."""
        lines = [
            "Daily Task Digest",
            "=" * 50,
            "",
            f"You have {len(tasks)} pending task(s) with reminders:",
            ""
        ]

        for i, task in enumerate(tasks, 1):
            lines.append(f"{i}. {task.title}")
            if task.due_date:
                if task.due_time:
                    due_str = task.due_date.strftime("%b %d, %Y") + f" at {task.due_time.strftime('%I:%M %p')}"
                else:
                    due_str = task.due_date.strftime("%b %d, %Y")
                lines.append(f"   Due: {due_str}")
            if task.priority:
                lines.append(f"   Priority: {task.priority.value.upper()}")
            lines.append("")

        lines.extend([
            "---",
            "Sent by Ticklisto Task Manager"
        ])

        return "\n".join(lines)

    def _format_digest_html(self, tasks: List[Task]) -> str:
        """Format HTML digest body."""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c3e50;">Daily Task Digest</h2>
            <p>You have <strong>{len(tasks)}</strong> pending task(s) with reminders:</p>

            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Task</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Due</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Priority</th>
                    </tr>
                </thead>
                <tbody>
        """

        for task in tasks:
            due_str = ""
            if task.due_date:
                if task.due_time:
                    due_str = task.due_date.strftime("%b %d, %Y") + f" at {task.due_time.strftime('%I:%M %p')}"
                else:
                    due_str = task.due_date.strftime("%b %d, %Y")

            priority_str = task.priority.value.upper() if task.priority else "N/A"
            priority_color = {
                'HIGH': '#e74c3c',
                'MEDIUM': '#f39c12',
                'LOW': '#3498db'
            }.get(priority_str, '#95a5a6')

            html += f"""
                    <tr style="border-bottom: 1px solid #dee2e6;">
                        <td style="padding: 10px;">{task.title}</td>
                        <td style="padding: 10px;">{due_str}</td>
                        <td style="padding: 10px; color: {priority_color}; font-weight: bold;">{priority_str}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>

            <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
            <p style="font-size: 12px; color: #95a5a6;">Sent by Ticklisto Task Manager</p>
        </body>
        </html>
        """

        return html
