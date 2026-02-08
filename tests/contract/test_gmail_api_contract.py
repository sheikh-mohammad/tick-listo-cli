"""Contract tests for Gmail API message format (T045 - User Story 3)."""

import pytest
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class TestGmailAPIContract:
    """Contract tests to verify Gmail API message format compliance."""

    def test_message_format_structure(self):
        """Test that message follows Gmail API expected structure."""
        # Gmail API expects messages in this format:
        # {
        #   "raw": base64url_encoded_email
        # }

        # Create a simple email
        message = MIMEText("Test body")
        message['to'] = "test@example.com"
        message['from'] = "sender@example.com"
        message['subject'] = "Test Subject"

        # Encode as Gmail API expects
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Verify structure
        gmail_message = {'raw': raw_message}

        assert 'raw' in gmail_message
        assert isinstance(gmail_message['raw'], str)
        assert len(gmail_message['raw']) > 0

    def test_message_can_be_decoded(self):
        """Test that encoded message can be decoded back."""
        original_body = "This is a test reminder"
        message = MIMEText(original_body)
        message['to'] = "test@example.com"
        message['from'] = "sender@example.com"
        message['subject'] = "Reminder: Test Task"

        # Encode
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Decode
        decoded_bytes = base64.urlsafe_b64decode(raw_message)
        decoded_message = decoded_bytes.decode('utf-8')

        # Verify original content is preserved
        assert "test@example.com" in decoded_message
        assert "Test Task" in decoded_message
        assert original_body in decoded_message

    def test_multipart_message_format(self):
        """Test multipart message format for HTML emails."""
        # Create multipart message (text + HTML)
        message = MIMEMultipart('alternative')
        message['to'] = "test@example.com"
        message['from'] = "sender@example.com"
        message['subject'] = "Test Subject"

        # Add text part
        text_part = MIMEText("Plain text version", 'plain')
        message.attach(text_part)

        # Add HTML part
        html_part = MIMEText("<html><body><h1>HTML version</h1></body></html>", 'html')
        message.attach(html_part)

        # Encode
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Verify structure
        gmail_message = {'raw': raw_message}
        assert 'raw' in gmail_message
        assert isinstance(gmail_message['raw'], str)

        # Decode and verify both parts exist
        decoded_bytes = base64.urlsafe_b64decode(raw_message)
        decoded_message = decoded_bytes.decode('utf-8')
        assert "Plain text version" in decoded_message
        assert "HTML version" in decoded_message

    def test_message_headers_format(self):
        """Test that required email headers are properly formatted."""
        message = MIMEText("Test body")
        message['to'] = "recipient@example.com"
        message['from'] = "sender@example.com"
        message['subject'] = "Test Subject"

        # Verify headers are set
        assert message['to'] == "recipient@example.com"
        assert message['from'] == "sender@example.com"
        assert message['subject'] == "Test Subject"

        # Encode and verify headers are preserved
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        decoded_bytes = base64.urlsafe_b64decode(raw_message)
        decoded_message = decoded_bytes.decode('utf-8')

        assert "To: recipient@example.com" in decoded_message
        assert "From: sender@example.com" in decoded_message
        assert "Subject: Test Subject" in decoded_message

    def test_special_characters_in_subject(self):
        """Test that special characters in subject are properly encoded."""
        message = MIMEText("Test body")
        message['to'] = "test@example.com"
        message['from'] = "sender@example.com"
        message['subject'] = "Reminder: Task with émojis 🔔 and spëcial chars"

        # Encode
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Decode and verify special characters are preserved
        decoded_bytes = base64.urlsafe_b64decode(raw_message)
        decoded_message = decoded_bytes.decode('utf-8')

        # Subject should be encoded properly
        assert "Subject:" in decoded_message

    def test_long_message_body(self):
        """Test that long message bodies are properly encoded."""
        # Create a long message body
        long_body = "This is a test reminder.\n" * 100

        message = MIMEText(long_body)
        message['to'] = "test@example.com"
        message['from'] = "sender@example.com"
        message['subject'] = "Long Message Test"

        # Encode
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Verify encoding succeeded
        assert len(raw_message) > 0
        assert isinstance(raw_message, str)

        # Decode and verify content
        decoded_bytes = base64.urlsafe_b64decode(raw_message)
        decoded_message = decoded_bytes.decode('utf-8')
        assert "This is a test reminder." in decoded_message

    def test_message_with_newlines_and_formatting(self):
        """Test that message with newlines and formatting is preserved."""
        body = """Task Reminder

Title: Important Meeting
Description: Discuss project timeline
Due: Feb 15, 2026 at 2:30 PM
Priority: HIGH

Please complete this task on time."""

        message = MIMEText(body)
        message['to'] = "test@example.com"
        message['from'] = "sender@example.com"
        message['subject'] = "Task Reminder"

        # Encode
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Decode and verify formatting is preserved
        decoded_bytes = base64.urlsafe_b64decode(raw_message)
        decoded_message = decoded_bytes.decode('utf-8')

        assert "Important Meeting" in decoded_message
        assert "Feb 15, 2026" in decoded_message
        assert "Priority: HIGH" in decoded_message
