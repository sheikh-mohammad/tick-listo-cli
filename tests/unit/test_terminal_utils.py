"""Unit tests for TerminalUtils - Platform-specific terminal clearing."""

import sys
from unittest.mock import patch, MagicMock
import pytest

from tick_listo_cli.utils.terminal_utils import TerminalUtils, get_platform


class TestPlatformDetection:
    """Test platform detection."""

    def test_get_platform_windows(self):
        """Test platform detection for Windows."""
        with patch('sys.platform', 'win32'):
            platform = get_platform()
            assert platform == "windows"

    def test_get_platform_linux(self):
        """Test platform detection for Linux."""
        with patch('sys.platform', 'linux'):
            platform = get_platform()
            assert platform == "linux"

    def test_get_platform_macos(self):
        """Test platform detection for macOS."""
        with patch('sys.platform', 'darwin'):
            platform = get_platform()
            assert platform == "macos"

    def test_get_platform_unknown(self):
        """Test platform detection for unknown platform."""
        with patch('sys.platform', 'unknown_os'):
            platform = get_platform()
            assert platform == "unknown"


class TestTerminalClearing:
    """Test platform-specific terminal clearing (Phase 11 - Enhanced Features)."""

    @patch('subprocess.run')
    @patch('sys.platform', 'win32')
    def test_clear_terminal_windows(self, mock_run):
        """Test terminal clearing on Windows."""
        utils = TerminalUtils()

        utils.clear_terminal()

        # Verify cls command was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert 'cls' in str(call_args)

    @patch('subprocess.run')
    @patch('sys.stdout')
    @patch('sys.platform', 'linux')
    def test_clear_terminal_linux(self, mock_stdout, mock_run):
        """Test terminal clearing on Linux."""
        utils = TerminalUtils()

        utils.clear_terminal()

        # Verify ANSI codes were printed and clear command was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert 'clear' in str(call_args)

    @patch('subprocess.run')
    @patch('sys.stdout')
    @patch('sys.platform', 'darwin')
    def test_clear_terminal_macos(self, mock_stdout, mock_run):
        """Test terminal clearing on macOS."""
        utils = TerminalUtils()

        utils.clear_terminal()

        # Verify ANSI codes were printed and clear command was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert 'clear' in str(call_args)

    @patch('subprocess.run')
    @patch('sys.platform', 'win32')
    def test_clear_terminal_subprocess_failure(self, mock_run):
        """Test error handling when subprocess fails."""
        mock_run.side_effect = Exception("Command failed")

        utils = TerminalUtils()

        with pytest.raises(RuntimeError, match="Failed to clear terminal"):
            utils.clear_terminal()

    @patch('sys.platform', 'unknown_os')
    def test_clear_terminal_unknown_platform(self):
        """Test error handling for unknown platform."""
        utils = TerminalUtils()

        with pytest.raises(RuntimeError, match="Unsupported platform"):
            utils.clear_terminal()


class TestTerminalUtilsIntegration:
    """Integration tests for terminal utils."""

    def test_terminal_utils_initialization(self):
        """Test that TerminalUtils can be initialized."""
        utils = TerminalUtils()
        assert utils is not None

    def test_get_platform_returns_valid_value(self):
        """Test that get_platform returns a valid platform string."""
        platform = get_platform()
        assert platform in ["windows", "linux", "macos", "unknown"]
